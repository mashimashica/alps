/*
 * Starting an agent's process through Bun. On macOS and Linux the agent starts a session and
 * process group of its own (setsid), so stopping it reaches every process it started: SIGTERM to
 * the group, then SIGKILL to whatever is left after 5 seconds. On Windows, taskkill ends its
 * process tree.
 */

import type { AgentHandle, AgentLaunch, AgentOutput } from "../agents/index.ts";

/** How long the process group has between SIGTERM and SIGKILL. */
export const STOP_GRACE_MS = 5000;
/** How long output may stay open after the agent exits (a process it left behind holds it). */
const OUTPUT_GRACE_MS = 2000;

const WINDOWS = process.platform === "win32";

const sleep = (ms: number): Promise<void> => new Promise((resolve) => setTimeout(resolve, ms));

/**
 * Reads a stream as lines (without their ends) until it closes. A line that `emit` fails on is
 * dropped and the reading goes on to the end: a reader that stopped would lose the rest of the
 * output (the report and the usage come last) and leave the agent writing into a pipe that is
 * closed, or full.
 */
async function readLines(
  stream: ReadableStream<Uint8Array>,
  emit: (line: string) => void,
): Promise<void> {
  const decoder = new TextDecoder();
  let buffer = "";
  const deliver = (line: string): void => {
    try {
      emit(line);
    } catch {
      // The harness records what it can of a line itself (parseOutputLine does not throw).
    }
  };
  const flush = (final: boolean): void => {
    let end = buffer.indexOf("\n");
    while (end >= 0) {
      deliver(buffer.slice(0, end).replace(/\r$/, ""));
      buffer = buffer.slice(end + 1);
      end = buffer.indexOf("\n");
    }
    if (final && buffer) {
      deliver(buffer.replace(/\r$/, ""));
      buffer = "";
    }
  };
  try {
    for await (const chunk of stream) {
      buffer += decoder.decode(chunk, { stream: true });
      flush(false);
    }
  } catch {
    // The stream itself broke off (the process was killed); what arrived is kept.
  }
  buffer += decoder.decode();
  flush(true);
}

/** Starts an agent. Throws when the process cannot be started (for example, the command does not exist). */
export function startAgent(launch: AgentLaunch, output: AgentOutput): AgentHandle {
  const child = Bun.spawn([launch.command, ...launch.args], {
    cwd: launch.cwd,
    env: { ...process.env, ...launch.env },
    detached: !WINDOWS,
    stdin: launch.stdin === null ? "ignore" : "pipe",
    stdout: "pipe",
    stderr: "pipe",
    windowsHide: true,
  });
  if (launch.stdin !== null && child.stdin) {
    try {
      void child.stdin.write(launch.stdin);
      void child.stdin.end();
    } catch {
      // An agent that exits before reading its input fails on its own.
    }
  }
  const stdout = readLines(child.stdout, output.stdout);
  const stderr = readLines(child.stderr, output.stderr);

  const group = -child.pid;
  const groupAlive = (): boolean => {
    try {
      process.kill(group, 0);
      return true;
    } catch (error) {
      return (error as NodeJS.ErrnoException).code === "EPERM";
    }
  };
  const signalGroup = (signal: NodeJS.Signals): void => {
    try {
      process.kill(group, signal);
    } catch {
      // The group has ended.
    }
  };

  let stopping = false;
  const stop = (): void => {
    if (stopping) return;
    stopping = true;
    if (WINDOWS) {
      try {
        Bun.spawn(["taskkill", "/pid", String(child.pid), "/T", "/F"], {
          stdin: "ignore",
          stdout: "ignore",
          stderr: "ignore",
          windowsHide: true,
        });
      } catch {
        child.kill();
      }
      return;
    }
    signalGroup("SIGTERM");
    setTimeout(() => {
      if (groupAlive()) signalGroup("SIGKILL");
    }, STOP_GRACE_MS);
  };

  const done = (async () => {
    await child.exited;
    const read = Promise.all([stdout, stderr]);
    const closed = await Promise.race([
      read.then(() => true),
      sleep(OUTPUT_GRACE_MS).then(() => false),
    ]);
    if (!closed) {
      // Processes the agent left behind hold its output: they end with it.
      stop();
      await Promise.race([read, sleep(STOP_GRACE_MS + 1000)]);
    } else if (!WINDOWS && groupAlive()) {
      // Processes the agent left behind without its output: they end with it too.
      stop();
    }
    return { exitCode: child.exitCode, signal: child.signalCode ?? null };
  })();

  return { pid: child.pid, stop, done };
}
