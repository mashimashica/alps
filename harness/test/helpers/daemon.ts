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
        await waitFor(() => !isAlive(info.pid), 10_000, `daemon ${info.pid} to stop`);
      }
      started.delete(info.pid);
    },
  };
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
