import path from "node:path";
import { fileURLToPath } from "node:url";

/** harness/ */
export const HARNESS_ROOT = fileURLToPath(new URL("../..", import.meta.url));
/** The repository root (the Plugin root). */
export const REPO_ROOT = path.resolve(HARNESS_ROOT, "..");
export const CLI = path.join(HARNESS_ROOT, "src", "cli.ts");
export const EXAMPLES = path.join(REPO_ROOT, "examples");
export const FIXTURES = path.join(HARNESS_ROOT, "test", "fixtures");
/** The fake agents (stage 3): `claude.ts`, `codex.ts`, and the wake agent. */
export const FAKES = path.join(HARNESS_ROOT, "test", "fakes");

export const serverJson = (workspace: string): string =>
  path.join(workspace, ".alps-harness", "server.json");
/** The workspace's records directory, .alps-harness/. */
export const records = (workspace: string, ...parts: string[]): string =>
  path.join(workspace, ".alps-harness", ...parts);
