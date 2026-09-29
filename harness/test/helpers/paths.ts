import path from "node:path";
import { fileURLToPath } from "node:url";

/** harness/ */
export const HARNESS_ROOT = fileURLToPath(new URL("../..", import.meta.url));
/** The repository root (the Plugin root). */
export const REPO_ROOT = path.resolve(HARNESS_ROOT, "..");
export const CLI = path.join(HARNESS_ROOT, "src", "cli.ts");
export const EXAMPLES = path.join(REPO_ROOT, "examples");

export const serverJson = (workspace: string): string =>
  path.join(workspace, ".alps-harness", "server.json");
