/* The `serve` and `stop` commands. */

import { Harness, StateError } from "../harness/index.ts";
import {
  DEFAULT_IDLE_MINUTES,
  DEFAULT_PORT,
  ModelError,
  findWorkspace,
  loadWorkspace,
} from "../model/index.ts";
import type { ServerInfo } from "../shared/types.ts";
import { startAgent } from "./agent-process.ts";
import { DaemonError, startDaemon, stopServer } from "./daemon.ts";
import { checkVersion, gitInfo } from "./host.ts";
import { startServer } from "./http.ts";
import { liveServer, serverUrl, uiUrl } from "./info.ts";
import { openUi } from "./open.ts";
import { UiBuildError } from "./ui.ts";
import { parseYaml } from "./yaml.ts";

export interface ServeArgs {
  /** Where to start looking for the workspace. */
  start: string;
  daemon: boolean;
  port: number | null;
  dev: boolean;
  /** Open the WebUI in a browser once the server answers. */
  open: boolean;
}

const out = (line: string): void => console.log(line);
const err = (line: string): void => console.error(line);

function workspaceOrReport(start: string): string | null {
  const root = findWorkspace(start);
  if (!root)
    err(`No alps-harness.yaml or process-model.yaml in ${start} or its parent directories.`);
  return root;
}

/**
 * The server settings of the workspace. When the model or the configuration cannot be read, the
 * server still starts, with the default settings: it answers no-model with the reason until the
 * files are fixed, and it reads them again on every request.
 */
function serverSettings(root: string): { port: number; idleMinutes: number | null } {
  try {
    const workspace = loadWorkspace(root, { parseYaml });
    // The daemon never stops by itself while schedules are configured.
    const idleMinutes = workspace.config.schedules?.length ? null : workspace.server.idleMinutes;
    return { port: workspace.server.port, idleMinutes };
  } catch (error) {
    if (!(error instanceof ModelError)) throw error;
    err(`${error.message}\nThe harness answers no-model until this is fixed.`);
    return { port: DEFAULT_PORT, idleMinutes: DEFAULT_IDLE_MINUTES };
  }
}

/**
 * Opens the WebUI in a browser through .alps-harness/open.html (mode 0600), so the token never
 * appears on the browser's command line.
 */
async function openOrReport(root: string, info: ServerInfo): Promise<void> {
  const { opened } = await openUi(root, info, { open: true });
  if (!opened) err("Could not open a browser. Open the URL above.");
}

/** Prints the WebUI's URL, which carries the token in its fragment, and opens it when asked. */
async function announce(
  root: string,
  label: string,
  info: ServerInfo,
  open: boolean,
): Promise<void> {
  out(`${label}  ${uiUrl(info)}  (pid ${info.pid})`);
  if (open) await openOrReport(root, info);
}

export async function serve(args: ServeArgs, version: string): Promise<number> {
  const root = workspaceOrReport(args.start);
  if (!root) return 1;

  if (args.daemon) {
    // The daemon has no terminal, so this process opens the browser once the daemon answers.
    const forwarded = [
      ...(args.port === null ? [] : ["--port", String(args.port)]),
      ...(args.dev ? ["--dev"] : []),
    ];
    try {
      const { info, reused } = await startDaemon(root, forwarded);
      await announce(root, reused ? "Already running" : "Started", info, args.open);
      return 0;
    } catch (error) {
      if (error instanceof DaemonError) {
        err(error.message);
        return 1;
      }
      throw error;
    }
  }

  const running = await liveServer(root);
  if (running) {
    await announce(root, "Already running", running.info, args.open);
    return 0;
  }
  const settings = serverSettings(root);
  const log = (line: string): void => err(`[${new Date().toISOString()}] ${line}`);
  let result: Awaited<ReturnType<typeof startServer>>;
  try {
    result = await startServer({
      root,
      port: args.port ?? settings.port,
      idleMinutes: settings.idleMinutes,
      development: args.dev,
      version,
      log,
      openHarness: () => new Harness(root, { parseYaml, gitInfo, checkVersion, startAgent, log }),
    });
  } catch (error) {
    if (error instanceof UiBuildError || error instanceof StateError) {
      log(error.message);
      return 1;
    }
    throw error;
  }
  if (result.kind === "running") {
    await announce(root, "Already running", result.info, args.open);
    return 0;
  }
  const { server } = result;
  out(`ALPS harness  ${uiUrl(server.info)}`);
  out(`Workspace     ${root}`);
  if (args.open) await openOrReport(root, server.info);
  const onSignal = (signal: NodeJS.Signals): void => void server.stop(signal);
  process.once("SIGINT", onSignal);
  process.once("SIGTERM", onSignal);
  await server.closed;
  return 0;
}

export async function stop(start: string): Promise<number> {
  const root = workspaceOrReport(start);
  if (!root) return 1;
  try {
    const stopped = await stopServer(root);
    out(
      stopped
        ? `Stopped  ${serverUrl(stopped)}  (pid ${stopped.pid})`
        : `No harness server is running for ${root}.`,
    );
    return 0;
  } catch (error) {
    if (error instanceof DaemonError) {
      err(error.message);
      return 1;
    }
    throw error;
  }
}
