import fs from "node:fs";
import type { ServerInfo } from "../../src/shared/types.ts";
import { serverJson } from "./paths.ts";
import { cli, isAlive, waitFor, type Finished } from "./process.ts";

export interface Daemon {
  info: ServerInfo;
  /** The server's origin, `http://127.0.0.1:<port>/`. */
  url: string;
  /** The WebUI's URL as `serve` printed it, with the token in the fragment. */
  uiUrl: string;
  /** The `serve --daemon` process, which has exited by the time startDaemon returns. */
  parent: Finished;
  stop(): Promise<void>;
}

const started = new Set<number>();

/** The WebUI URL in the output of `serve`. */
export const printedUrl = (stdout: string): string | undefined =>
  /http:\/\/127\.0\.0\.1:\d+\/#token=[0-9a-f]+/.exec(stdout)?.[0];

/** Starts `bun src/cli.ts serve --daemon <workspace>` and reads the server.json it waited for. */
export async function startDaemon(
  workspace: string,
  args: string[] = [],
  options: Parameters<typeof cli>[1] = {},
): Promise<Daemon> {
  const parent = await cli(["serve", "--daemon", workspace, ...args], options);
  if (parent.code !== 0)
    throw new Error(`serve --daemon exited with ${parent.code}: ${parent.stderr || parent.stdout}`);
  const info = JSON.parse(fs.readFileSync(serverJson(workspace), "utf8")) as ServerInfo;
  started.add(info.pid);
  const uiUrl = printedUrl(parent.stdout);
  if (!uiUrl) throw new Error(`serve --daemon printed no WebUI URL: ${parent.stdout}`);
  return {
    info,
    url: `http://127.0.0.1:${info.port}/`,
    uiUrl,
    parent,
    async stop() {
      if (isAlive(info.pid)) {
        const result = await cli(["stop", workspace]);
        if (result.code !== 0) throw new Error(`stop exited with ${result.code}: ${result.stderr}`);
        await waitFor(() => !isAlive(info.pid), 20_000, `daemon ${info.pid} to stop`);
      }
      started.delete(info.pid);
    },
  };
}

/** The daemon that server.json names, if any. */
export function readServerInfo(workspace: string): ServerInfo | null {
  try {
    return JSON.parse(fs.readFileSync(serverJson(workspace), "utf8")) as ServerInfo;
  } catch {
    return null;
  }
}

/** The daemons serving `workspace` (`… cli.ts serve <workspace>`), from ps. */
function serveProcesses(workspace: string): number[] {
  const ps = Bun.spawnSync(["ps", "-ax", "-o", "pid=,command="]);
  return ps.stdout
    .toString()
    .split("\n")
    .flatMap((line) => {
      const match = /^\s*(\d+)\s+(.*)$/.exec(line);
      return match?.[2]?.includes(` serve ${workspace}`) ? [Number(match[1])] : [];
    });
}

/**
 * Stops the daemon of a workspace however it was started; the MCP server starts one when it has
 * none to relay to. A daemon still starting is waited for, and whatever does not stop is killed,
 * so no daemon outlives the test.
 */
export async function stopWorkspaceDaemon(workspace: string): Promise<void> {
  if (!fs.existsSync(serverJson(workspace)) && serveProcesses(workspace).length > 0)
    await waitFor(
      () => fs.existsSync(serverJson(workspace)) || serveProcesses(workspace).length === 0,
      20_000,
      "a starting daemon to write server.json",
    ).catch(() => {});
  if (fs.existsSync(serverJson(workspace))) await cli(["stop", workspace]);
  for (const pid of serveProcesses(workspace)) {
    try {
      process.kill(pid, "SIGKILL");
    } catch {
      // Already gone.
    }
  }
}

/** Kills daemons a failed test left behind. */
export function killStrayDaemons(): void {
  for (const pid of started) {
    try {
      process.kill(pid, "SIGKILL");
    } catch {
      // Already gone.
    }
  }
  started.clear();
}
