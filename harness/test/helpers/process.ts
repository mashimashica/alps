import fs from "node:fs";
import { CLI, HARNESS_ROOT } from "./paths.ts";

export interface Finished {
  pid: number;
  code: number;
  stdout: string;
  stderr: string;
}

/** Environment variables as strings only, without ALPS_WORKSPACE unless a test sets it. */
export function cleanEnv(extra: Record<string, string | undefined> = {}): Record<string, string> {
  const merged: Record<string, string | undefined> = {
    ...process.env,
    ALPS_WORKSPACE: undefined,
    ...extra,
  };
  return Object.fromEntries(
    Object.entries(merged).filter(
      (entry): entry is [string, string] => typeof entry[1] === "string",
    ),
  );
}

/** Runs a command to completion, killing it after `timeoutMs`. */
export async function exec(
  cmd: string[],
  options: { cwd?: string; env?: Record<string, string | undefined>; timeoutMs?: number } = {},
): Promise<Finished> {
  const child = Bun.spawn(cmd, {
    cwd: options.cwd ?? HARNESS_ROOT,
    env: cleanEnv(options.env),
    stdin: "ignore",
    stdout: "pipe",
    stderr: "pipe",
  });
  const timer = setTimeout(() => child.kill("SIGKILL"), options.timeoutMs ?? 30_000);
  try {
    const [stdout, stderr, code] = await Promise.all([
      new Response(child.stdout).text(),
      new Response(child.stderr).text(),
      child.exited,
    ]);
    return { pid: child.pid, code, stdout, stderr };
  } finally {
    clearTimeout(timer);
  }
}

/** Runs `bun src/cli.ts <args>`. */
export const cli = (args: string[], options: Parameters<typeof exec>[1] = {}): Promise<Finished> =>
  exec([process.execPath, CLI, ...args], options);

export function isAlive(pid: number): boolean {
  try {
    process.kill(pid, 0);
    return true;
  } catch (error) {
    return (error as NodeJS.ErrnoException).code === "EPERM";
  }
}

/** The current directory of a running process (Linux: /proc; macOS: lsof), or null elsewhere. */
export function processCwd(pid: number): string | null {
  if (process.platform === "linux") return fs.readlinkSync(`/proc/${pid}/cwd`);
  if (process.platform !== "darwin") return null;
  const lsof = Bun.spawnSync(["lsof", "-a", "-p", String(pid), "-d", "cwd", "-Fn"]);
  const line = lsof.stdout
    .toString()
    .split("\n")
    .find((entry) => entry.startsWith("n"));
  return line ? line.slice(1) : null;
}

export async function waitFor(
  condition: () => boolean,
  timeoutMs: number,
  what: string,
): Promise<number> {
  const started = Date.now();
  while (!condition()) {
    if (Date.now() - started > timeoutMs)
      throw new Error(`Timed out after ${timeoutMs} ms waiting for ${what}`);
    await Bun.sleep(50);
  }
  return Date.now() - started;
}
