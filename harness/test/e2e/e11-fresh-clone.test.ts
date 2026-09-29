/*
 * E11 (technology choices): in a fresh clone, `bun install --frozen-lockfile --ignore-scripts`
 * finishes within 60 seconds and `bun harness/src/cli.ts mcp` answers initialize. This is what
 * Claude Code runs when it fetches the Plugin from a marketplace.
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
import { exec } from "../helpers/process.ts";

const INSTALL_LIMIT_S = 60;
const base = fs.mkdtempSync(path.join(os.tmpdir(), "alps-harness-e11-"));

afterAll(() => fs.rmSync(base, { recursive: true, force: true }));

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
    "E11 a fresh clone installs with --frozen-lockfile --ignore-scripts within 60 s and mcp answers initialize",
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
      // The workspace package gets its dependencies.
      expect(
        fs.existsSync(
          path.join(clone, "harness", "node_modules", "@modelcontextprotocol", "server"),
        ),
      ).toBe(true);

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
