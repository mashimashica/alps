/*
 * E11 (technology choices): in a fresh clone, `bun install --frozen-lockfile --ignore-scripts`
 * finishes within 60 seconds and `bun harness/src/cli.ts mcp` answers initialize. This is what
 * Claude Code runs when it fetches the Plugin from a marketplace. The install reads the root
 * package.json, which has only the runtime dependencies: the development tools of
 * harness/package.json stay out of the Plugin's copy.
 *
 * The clone gets the working tree's uncommitted changes (modified and untracked, not ignored),
 * so the test also holds before they are committed. By default Bun's global cache is used;
 * ALPS_E2E_COLD_CACHE=1 installs through an empty cache, as a first fetch on a new machine would.
 */

import { SUPPORTED_PROTOCOL_VERSIONS } from "@modelcontextprotocol/client";
import { afterAll, describe, expect, test } from "bun:test";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import type { ModelResponse } from "../../src/shared/types.ts";
import { stopWorkspaceDaemon } from "../helpers/daemon.ts";
import { callTool, mcpClient } from "../helpers/mcp.ts";
import { REPO_ROOT } from "../helpers/paths.ts";
import { exec, HOOK_TIMEOUT_MS } from "../helpers/process.ts";

const INSTALL_LIMIT_S = 60;
const base = fs.mkdtempSync(path.join(os.tmpdir(), "alps-harness-e11-"));

afterAll(() => fs.rmSync(base, { recursive: true, force: true }), HOOK_TIMEOUT_MS);

/** The packages installed under `root`/node_modules, including those only in Bun's isolated store (.bun). */
function installedPackages(root: string): Set<string> {
  const modules = path.join(root, "node_modules");
  const names = new Set<string>();
  const entries = (dir: string): string[] => (fs.existsSync(dir) ? fs.readdirSync(dir) : []);
  for (const entry of entries(modules)) {
    if (entry === ".bin") continue;
    if (entry === ".bun") {
      // <name>@<version>, with the scope's slash written as +.
      for (const stored of entries(path.join(modules, ".bun"))) {
        const match = /^(@[^+]+\+)?([^@]+)@/.exec(stored);
        if (match) names.add(`${match[1]?.replace("+", "/") ?? ""}${match[2]}`);
      }
    } else if (entry.startsWith("@"))
      for (const scoped of entries(path.join(modules, entry))) names.add(`${entry}/${scoped}`);
    else names.add(entry);
  }
  return names;
}

async function git(args: string[], cwd: string): Promise<string> {
  const result = await exec(["git", ...args], { cwd });
  if (result.code !== 0) throw new Error(`git ${args.join(" ")} failed: ${result.stderr}`);
  return result.stdout;
}

/** Copies what `git add -A` would commit on top of the clone; a symlink stays a symlink, as git keeps it. */
async function overlayWorkingTree(clone: string): Promise<void> {
  const changed = (
    await git(["ls-files", "-z", "--modified", "--others", "--exclude-standard"], REPO_ROOT)
  )
    .split("\0")
    .filter(Boolean);
  for (const file of changed) {
    const source = path.join(REPO_ROOT, file);
    const target = path.join(clone, file);
    let link = false;
    try {
      link = fs.lstatSync(source).isSymbolicLink();
    } catch {
      fs.rmSync(target, { force: true });
      continue;
    }
    fs.mkdirSync(path.dirname(target), { recursive: true });
    fs.rmSync(target, { force: true });
    if (link) fs.symlinkSync(fs.readlinkSync(source), target);
    else fs.copyFileSync(source, target);
  }
}

describe("E11 fresh clone", () => {
  test(
    "E11 a fresh clone installs only the runtime dependencies with --frozen-lockfile --ignore-scripts within 60 s and mcp answers initialize",
    async () => {
      const clone = path.join(base, "alps");
      await git(["clone", "--quiet", "--local", REPO_ROOT, clone], base);
      await overlayWorkingTree(clone);
      expect(fs.existsSync(path.join(clone, "node_modules"))).toBe(false);

      const cold = process.env.ALPS_E2E_COLD_CACHE === "1";
      const started = performance.now();
      const install = await exec(
        [process.execPath, "install", "--frozen-lockfile", "--ignore-scripts"],
        {
          cwd: clone,
          env: cold ? { BUN_INSTALL_CACHE_DIR: path.join(base, "bun-cache") } : {},
          timeoutMs: 120_000,
        },
      );
      const seconds = (performance.now() - started) / 1000;
      console.info(`E11 bun install (${cold ? "cold" : "warm"} cache): ${seconds.toFixed(1)} s`);
      expect(install.code, install.stderr).toBe(0);
      expect(seconds).toBeLessThan(INSTALL_LIMIT_S);
      // The runtime dependencies are installed at the root, where the harness's imports find them,
      // and none of the development tools is, anywhere in the clone.
      const installed = installedPackages(clone);
      const manifest = (file: string): Record<string, Record<string, string> | undefined> =>
        JSON.parse(fs.readFileSync(path.join(clone, file), "utf8"));
      const runtime = Object.keys(manifest("package.json").dependencies ?? {});
      const development = Object.keys(manifest("harness/package.json").devDependencies ?? {});
      expect(runtime).toContain("@modelcontextprotocol/server");
      expect(runtime.filter((name) => !installed.has(name))).toEqual([]);
      expect(development.length).toBeGreaterThan(0);
      expect(development.filter((name) => installed.has(name))).toEqual([]);
      expect(fs.existsSync(path.join(clone, "harness", "node_modules"))).toBe(false);

      // The 2025 initialize handshake, at the newest 2025-era version the client offers
      // (E2 covers the newest revision through server/discover).
      const workspace = path.join(clone, "examples", "service-change");
      const session = await mcpClient({
        cli: path.join(clone, "harness", "src", "cli.ts"),
        cwd: clone,
        workspace,
        negotiation: "legacy",
      });
      try {
        expect(session.client.getServerVersion()?.name).toBe("alps-harness");
        expect(session.client.getProtocolEra()).toBe("legacy");
        expect(SUPPORTED_PROTOCOL_VERSIONS).toContain(
          String(session.client.getNegotiatedProtocolVersion()),
        );
        // The clone's MCP server relays to a daemon of its own, which it started.
        const { model } = await callTool<ModelResponse>(session, "get_model");
        expect(model.workspace).toBe(workspace);
      } finally {
        await session.close();
        await stopWorkspaceDaemon(workspace);
      }
    },
    { timeout: 180_000 },
  );
});
