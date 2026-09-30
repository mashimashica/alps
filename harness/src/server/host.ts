/* What the harness core needs from the machine: agent version checks and the git state, through Bun. */

import { envLeftOut, type AgentSpec, type VersionCheck } from "../agents/index.ts";
import { agentEnv } from "./agent-process.ts";

const VERSION_TIMEOUT_MS = 8000;
const GIT_TIMEOUT_MS = 5000;

/**
 * Runs `<command> --version` with a time limit, in the environment that the agent is started in
 * (agentEnv). Never rejects.
 */
export async function checkVersion(spec: AgentSpec): Promise<VersionCheck> {
  if (!spec.command) return { exitCode: null, stdout: "", notFound: true, timedOut: false };
  let child: Bun.Subprocess<"ignore", "pipe", "ignore">;
  try {
    child = Bun.spawn([spec.command, "--version"], {
      env: agentEnv(process.env, { unset: envLeftOut(spec), env: spec.env }),
      stdin: "ignore",
      stdout: "pipe",
      stderr: "ignore",
      windowsHide: true,
    });
  } catch {
    return { exitCode: null, stdout: "", notFound: true, timedOut: false };
  }
  let timedOut = false;
  const timer = setTimeout(() => {
    timedOut = true;
    child.kill("SIGKILL");
  }, VERSION_TIMEOUT_MS);
  try {
    const [stdout, exitCode] = await Promise.all([new Response(child.stdout).text(), child.exited]);
    return { exitCode, stdout, notFound: false, timedOut };
  } catch {
    return { exitCode: null, stdout: "", notFound: false, timedOut };
  } finally {
    clearTimeout(timer);
  }
}

/** `git rev-parse HEAD` and whether `git status --porcelain` lists anything; `null` outside a repository. */
export function gitInfo(root: string): { head: string; dirty: boolean } | null {
  try {
    const head = Bun.spawnSync(["git", "rev-parse", "HEAD"], {
      cwd: root,
      timeout: GIT_TIMEOUT_MS,
      stderr: "ignore",
    });
    if (!head.success) return null;
    const status = Bun.spawnSync(["git", "status", "--porcelain"], {
      cwd: root,
      timeout: GIT_TIMEOUT_MS,
      stderr: "ignore",
    });
    return { head: head.stdout.toString().trim(), dirty: status.stdout.toString().trim() !== "" };
  } catch {
    return null;
  }
}
