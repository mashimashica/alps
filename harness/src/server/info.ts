/*
 * .alps-harness/server.json: which daemon serves the workspace. It holds the per-start
 * token, so only people who can read the workspace can use the API.
 */

import fs from "node:fs";
import path from "node:path";
import { HARNESS_DIR } from "../model/index.ts";
import type { HealthInfo, ServerInfo } from "../shared/types.ts";

export const harnessDir = (root: string): string => path.join(root, HARNESS_DIR);
export const serverJsonPath = (root: string): string => path.join(root, HARNESS_DIR, "server.json");
export const serverLogPath = (root: string): string => path.join(root, HARNESS_DIR, "server.log");
/** The page that hands the WebUI's URL, token and all, to a browser (see open.ts). */
export const openPagePath = (root: string): string => path.join(root, HARNESS_DIR, "open.html");
export const serverUrl = (info: Pick<ServerInfo, "port">): string =>
  `http://127.0.0.1:${info.port}/`;
/**
 * The WebUI's address with the token in the fragment, which browsers never send to servers.
 * The page reads it once and removes it from the address bar. `view` names the screen to show.
 */
export const uiUrl = (info: Pick<ServerInfo, "port" | "token">, view?: string): string =>
  `${serverUrl(info)}#token=${info.token}${view ? `&view=${encodeURIComponent(view)}` : ""}`;

function isServerInfo(value: unknown): value is ServerInfo {
  const v = value as Partial<ServerInfo> | null;
  return (
    typeof v === "object" &&
    v !== null &&
    Number.isInteger(v.pid) &&
    Number.isInteger(v.port) &&
    typeof v.token === "string" &&
    typeof v.startedAt === "number"
  );
}

/** The recorded daemon, or null when there is none or the file is unreadable (for example, half written). */
export function readServerInfo(root: string): ServerInfo | null {
  try {
    const value: unknown = JSON.parse(fs.readFileSync(serverJsonPath(root), "utf8"));
    return isServerInfo(value) ? value : null;
  } catch {
    return null;
  }
}

/**
 * Records this daemon. With `exclusive`, an existing file is left alone and `false` is returned,
 * so two daemons starting at once cannot both claim the workspace.
 */
export function writeServerInfo(root: string, info: ServerInfo, exclusive: boolean): boolean {
  fs.mkdirSync(harnessDir(root), { recursive: true });
  try {
    fs.writeFileSync(serverJsonPath(root), `${JSON.stringify(info, null, 2)}\n`, {
      flag: exclusive ? "wx" : "w",
      mode: 0o600,
    });
    return true;
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === "EEXIST") return false;
    throw error;
  }
}

/** Removes server.json only while it still names the given daemon. */
export function removeServerInfo(root: string, owner: Pick<ServerInfo, "pid" | "token">): boolean {
  const current = readServerInfo(root);
  if (!current || current.pid !== owner.pid || current.token !== owner.token) return false;
  try {
    fs.unlinkSync(serverJsonPath(root));
    return true;
  } catch {
    return false;
  }
}

export function isAlive(pid: number): boolean {
  try {
    process.kill(pid, 0);
    return true;
  } catch (error) {
    return (error as NodeJS.ErrnoException).code === "EPERM";
  }
}

/** Asks the recorded daemon for its health. Only the daemon that holds the token answers with its own pid. */
export async function probe(info: ServerInfo, timeoutMs = 2000): Promise<HealthInfo | null> {
  const controller = new AbortController();
  let timer: ReturnType<typeof setTimeout> | null = null;
  try {
    const timeout = new Promise<null>((resolve) => {
      timer = setTimeout(() => {
        controller.abort();
        resolve(null);
      }, timeoutMs);
    });
    const response = await Promise.race([
      fetch(`http://127.0.0.1:${info.port}/api/health`, {
        headers: { "X-Harness-Token": info.token },
        signal: controller.signal,
      }),
      timeout,
    ]);
    if (response === null) return null;
    if (!response.ok) return null;
    const health = (await Promise.race([response.json(), timeout])) as HealthInfo | null;
    if (!health) return null;
    return health.ok && health.pid === info.pid ? health : null;
  } catch {
    return null;
  } finally {
    if (timer) clearTimeout(timer);
  }
}

/** The daemon that serves the workspace now, if any. A stale server.json is removed. */
export async function liveServer(
  root: string,
): Promise<{ info: ServerInfo; health: HealthInfo } | null> {
  const info = readServerInfo(root);
  if (!info) return null;
  const health = await probe(info);
  if (health) return { info, health };
  if (!isAlive(info.pid)) removeServerInfo(root, info);
  return null;
}
