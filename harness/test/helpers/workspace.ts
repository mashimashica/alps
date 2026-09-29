import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { EXAMPLES, HARNESS_ROOT } from "./paths.ts";

export interface TmpWorkspace {
  /** The copied workspace (…/examples/service-change, or …/examples/locales/ja/service-change). */
  root: string;
  /** The temporary directory that holds the copy of examples/. */
  base: string;
  dispose(): void;
}

export interface WorkspaceOverrides {
  /** `ja` copies the Japanese counterpart, examples/locales/ja/service-change (`language: ja`). */
  locale?: "ja";
  server?: { port?: number; idleMinutes?: number };
}

/** Records of earlier runs and Python caches are not part of the example. */
const NOT_COPIED = new Set([".alps-harness", "__pycache__"]);

/**
 * Copies examples/ into a temporary directory and rewrites the example workspace's
 * alps-harness.yaml for tests: `server.port: 0` and a small `server.idleMinutes`.
 * The whole directory is copied because the workspaces refer to their Skills by relative paths:
 * the English workspace declares `../assess-service-change`, and the Japanese counterpart uses
 * the English workspace's Skills through `skillRoots` and the translated headings.
 */
export function tmpWorkspace(overrides: WorkspaceOverrides = {}): TmpWorkspace {
  const base = fs.mkdtempSync(path.join(os.tmpdir(), "alps-harness-e2e-"));
  const examples = path.join(base, "examples");
  fs.cpSync(EXAMPLES, examples, {
    recursive: true,
    filter: (source) => !NOT_COPIED.has(path.basename(source)),
  });
  const root = overrides.locale
    ? path.join(examples, "locales", overrides.locale, "service-change")
    : path.join(examples, "service-change");

  const file = path.join(root, "alps-harness.yaml");
  const config = Bun.YAML.parse(fs.readFileSync(file, "utf8")) as Record<string, unknown>;
  config.server = { port: 0, idleMinutes: 0.5, ...overrides.server };
  // JSON is YAML, so the rewritten file is still a valid alps-harness.yaml.
  fs.writeFileSync(file, `${JSON.stringify(config, null, 2)}\n`);

  return { root, base, dispose: () => fs.rmSync(base, { recursive: true, force: true }) };
}

/**
 * Copies the harness package (its sources and manifests) into `dir` for a test that changes the
 * sources, and links the copy's node_modules to the real one. Returns the copy's cli.ts.
 */
export function copyHarness(dir: string): string {
  const copy = path.join(dir, "harness");
  fs.cpSync(path.join(HARNESS_ROOT, "src"), path.join(copy, "src"), { recursive: true });
  for (const file of ["package.json", "tsconfig.json"])
    fs.copyFileSync(path.join(HARNESS_ROOT, file), path.join(copy, file));
  fs.symlinkSync(
    path.join(HARNESS_ROOT, "node_modules"),
    path.join(copy, "node_modules"),
    "junction",
  );
  return path.join(copy, "src", "cli.ts");
}
