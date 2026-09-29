/*
 * Starting the server detached from the calling process (a Claude Code session, a terminal),
 * so that closing the caller stops neither the WebUI nor running agents, and stopping it.
 */

import { spawn } from "node:child_process";
import fs from "node:fs";
import { fileURLToPath } from "node:url";
import type { ServerInfo } from "../shared/types.ts";
import {
  harnessDir,
  isAlive,
  liveServer,
  probe,
  readServerInfo,
  removeServerInfo,
  serverJsonPath,
  serverLogPath,
} from "./info.ts";

const CLI_PATH = fileURLToPath(new URL("../cli.ts", import.meta.url));
/** How many of the lines a failed start wrote to server.log are quoted in the error. */
const LOG_LINES_QUOTED = 20;

export class DaemonError extends Error {
  readonly code = "server-unreachable";
  constructor(message: string) {
    super(message);
    this.name = "DaemonError";
  }
}

const sleep = (ms: number): Promise<void> => new Promise((resolve) => setTimeout(resolve, ms));

function fileSize(file: string): number {
  try {
    return fs.statSync(file).size;
  } catch {
    return 0;
  }
}

/** The last lines written to the log since `offset`, indented for an error message. */
function logSince(file: string, offset: number): string {
  try {
    const lines = fs.readFileSync(file).subarray(offset).toString("utf8").trimEnd().split("\n");
    const quoted = lines.slice(-LOG_LINES_QUOTED).filter(Boolean);
    return quoted.length > 0 ? `\n  ${quoted.join("\n  ")}\n` : " ";
  } catch {
    return " ";
  }
}

/**
 * Starts `serve` for the workspace as a detached process and waits until it has written
 * server.json and answers /api/health. A server that already runs is reused. The daemon runs in
 * the workspace root; its stderr goes to .alps-harness/server.log. Its stdout, which is for a
 * person at a terminal and carries the token, is discarded.
 */
export async function startDaemon(
  root: string,
  serveArgs: string[],
  timeoutMs = 20_000,
): Promise<{ info: ServerInfo; reused: boolean }> {
  const running = await liveServer(root);
  if (running) return { info: running.info, reused: true };

  fs.mkdirSync(harnessDir(root), { recursive: true });
  const logFile = serverLogPath(root);
  const logStart = fileSize(logFile);
  const log = fs.openSync(logFile, "a");
  let exit: string | null = null;
  let pid: number | undefined;
  try {
    const child = spawn(process.execPath, [CLI_PATH, "serve", root, ...serveArgs], {
      cwd: root,
      detached: true,
      stdio: ["ignore", "ignore", log],
      env: process.env,
      windowsHide: true,
    });
    pid = child.pid;
    child.once("error", (error) => (exit = error.message));
    child.once(
      "exit",
      (code, signal) => (exit = signal ? `signal ${signal}` : `exit code ${code}`),
    );
    child.unref();
  } finally {
    fs.closeSync(log);
  }

  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    const info = readServerInfo(root);
    if (info && (await probe(info))) return { info, reused: info.pid !== pid };
    if (exit)
      throw new DaemonError(
        `The harness server ended before it was ready (${exit}).${logSince(logFile, logStart)}See ${logFile}.`,
      );
    await sleep(50);
  }
  throw new DaemonError(
    `The harness server did not become ready within ${Math.round(timeoutMs / 1000)} s. See ${logFile} and ${serverJsonPath(root)}.`,
  );
}

/**
 * Asks the workspace's server to stop and waits for its process to end. A server with running
 * agents stops their process groups first, which takes up to about 8 seconds.
 */
export async function stopServer(root: string, timeoutMs = 20_000): Promise<ServerInfo | null> {
  const running = await liveServer(root);
  if (!running) return null;
  const { info } = running;
  const response = await fetch(`http://127.0.0.1:${info.port}/api/shutdown`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Harness-Token": info.token },
    body: "{}",
    signal: AbortSignal.timeout(5000),
  });
  if (!response.ok)
    throw new DaemonError(
      `The harness server on port ${info.port} refused to stop (${response.status}).`,
    );
  const deadline = Date.now() + timeoutMs;
  while (isAlive(info.pid)) {
    if (Date.now() > deadline)
      throw new DaemonError(
        `The harness server (pid ${info.pid}) did not stop within ${timeoutMs / 1000} s.`,
      );
    await sleep(50);
  }
  removeServerInfo(root, info);
  return info;
}
