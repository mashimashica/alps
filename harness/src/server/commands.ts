/*
 * The `serve`, `stop`, `wake`, and `assess` commands. `wake` and `assess` ask the workspace's
 * harness server as the MCP server does (DaemonLink), which starts one when none runs.
 */

import { Harness, StateError } from "../harness/index.ts";
import {
  DEFAULT_IDLE_MINUTES,
  DEFAULT_PORT,
  ModelError,
  findWorkspace,
  loadWorkspace,
} from "../model/index.ts";
import type {
  AssessmentMarkdownResponse,
  AssessmentResponse,
  Failure,
  ServerInfo,
  WakeResponse,
} from "../shared/types.ts";
import { startAgent } from "./agent-process.ts";
import { CLI_PATH, DaemonError, startDaemon, stopServer } from "./daemon.ts";
import { checkVersion, gitInfo } from "./host.ts";
import { startServer } from "./http.ts";
import { liveServer, serverUrl, uiUrl } from "./info.ts";
import { openUi } from "./open.ts";
import { DaemonLink, RelayError } from "./relay.ts";
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
function serverSettings(root: string): { port: number; idleMinutes: number } {
  try {
    return loadWorkspace(root, { parseYaml }).server;
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
      openHarness: () =>
        new Harness(root, {
          parseYaml,
          gitInfo,
          checkVersion,
          startAgent,
          mcpServer: { command: process.execPath, args: [CLI_PATH, "mcp"] },
          log,
        }),
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

/**
 * Sends one request to the workspace's harness server, starting it when none runs, as a person
 * (no MCP client is named). A failure is printed; the result is `null` then.
 */
async function ask<T extends { ok: true }>(
  root: string,
  method: "GET" | "POST",
  route: string,
  body?: unknown,
): Promise<T | null> {
  const link = new DaemonLink(root, parseYaml);
  try {
    const reply = await link.request(method, route, { body });
    const answer = reply.body as T | Failure | null;
    if (answer && typeof answer === "object" && "ok" in answer) {
      if (answer.ok) return answer;
      err(answer.error.message);
      if (answer.error.files?.length) err(`See ${answer.error.files.join(" and ")}.`);
      return null;
    }
    err(`The harness server answered ${reply.status} without a result.`);
    return null;
  } catch (error) {
    if (!(error instanceof RelayError)) throw error;
    err(`${error.message}\nSee ${error.files.join(" and ")}.`);
    return null;
  } finally {
    await link.close();
  }
}

/** What `wake` asks: the agent, and a request with its attachments, Processes, and whether to run. */
export interface WakeArgs {
  agent?: string | undefined;
  request?: string | undefined;
  /** Absolute paths, or relative to the workspace. */
  attachments: string[];
  processes: string[];
  /** Only instantiate what is planned (`runs: plan`). */
  plan: boolean;
}

/**
 * Starts a wake run, as the MCP tool wake does: for an external scheduler (launchd, cron, CI), or
 * with a request. It returns once the agent has started, or once the wake was skipped because
 * another runs; what the agent planned and why comes later, in the wake run's report.
 */
export async function wake(start: string, args: WakeArgs): Promise<number> {
  const root = workspaceOrReport(start);
  if (!root) return 1;
  const requested =
    args.request !== undefined ||
    args.attachments.length > 0 ||
    args.processes.length > 0 ||
    args.plan;
  const result = await ask<WakeResponse>(root, "POST", "/api/wake", {
    ...(args.agent ? { agent: args.agent } : {}),
    ...(args.request !== undefined ? { request: args.request } : {}),
    ...(args.attachments.length > 0 ? { attachments: args.attachments } : {}),
    ...(args.processes.length > 0 ? { processes: args.processes } : {}),
    ...(args.plan ? { runs: "plan" } : {}),
  });
  if (!result) return 1;
  out(
    result.run
      ? `Woke ${result.run.agent}  wake run ${result.run.id}`
      : `Skipped  wake run ${result.running ?? ""} still runs${requested ? "; the request was not taken" : ""}`,
  );
  if (result.run && requested)
    out(
      result.run.runs === "plan"
        ? "It plans only: it instantiates what it plans and starts no run. Its report says what it planned and why."
        : "It plans and runs what the request calls for. Its report says what it planned and why.",
    );
  return 0;
}

/** Prints the assessment (the statistics, the findings, the facts of the instances), as get_assessment returns it. */
export async function assess(start: string, format: "markdown" | "json"): Promise<number> {
  const root = workspaceOrReport(start);
  if (!root) return 1;
  const result = await ask<AssessmentMarkdownResponse | AssessmentResponse>(
    root,
    "GET",
    `/api/assessment?format=${format}`,
  );
  if (!result) return 1;
  const text = "markdown" in result ? result.markdown : JSON.stringify(result.assessment, null, 2);
  // Written whole before the process exits, however long it is.
  await Bun.write(Bun.stdout, text.endsWith("\n") ? text : `${text}\n`);
  return 0;
}
