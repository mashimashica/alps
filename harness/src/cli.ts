#!/usr/bin/env bun
/* alps-harness: the harness's command line. */

import fs from "node:fs";
import path from "node:path";
import pkg from "../package.json" with { type: "json" };
import { startDirectory } from "./model/files.ts";

const USAGE = `Usage: alps-harness <command> [options]

Commands:
  serve [workspace] [--daemon] [--port <port>] [--dev] [--open]
        Start the harness server (WebUI and HTTP API) for the workspace and print the
        WebUI's URL. The URL carries the per-start token after #; keep it to yourself.
        --daemon  start it detached and return once .alps-harness/server.json is written
        --port    the port to try first (default: server.port in alps-harness.yaml, or 4830)
        --dev     Bun's development mode (the UI is bundled on each request, with HMR); its
                  page and assets bypass the server's Host check and security headers
        --open    open the WebUI in a browser (BROWSER=<command> picks it, BROWSER=none opens
                  none) through .alps-harness/open.html, which only you can read, so the token
                  never appears on a command line
  stop [workspace]
        Stop the harness server of the workspace, and the agents it is running.
  mcp [--wake <run>]
        Serve MCP on stdio for the workspace in ALPS_WORKSPACE or the current directory. It
        relays to the workspace's harness server and starts one (detached) when none runs.
        --wake  the wake run whose agent this server serves; the harness passes it to the
                agents it wakes, so the runs they start are listed in that wake run
  wake [workspace] [--agent <agent>] [--request <text>] [--attach <path>]... [--process <process>]... [--plan]
        Wake an agent, as the schedules in alps-harness.yaml and the MCP tool wake do: it is
        started with the harness's MCP server and decides which Processes to run. For an
        external scheduler (launchd, cron, CI), or to hand the agent a request. It returns once
        the agent has started; while another wake runs, none is started (skipped). What the
        agent planned and why comes later, in the wake run's report.
        --agent    claude-code (the default) or codex
        --request  what is asked, in free text: the agent plans the Processes that serve it,
                   instantiates them with criteria it derives from the request, and runs them
        --attach   a file or directory in the workspace that the request refers to, relative to
                   the current directory (repeatable, at most 10)
        --process  a Process (id or name) that the plan must include (repeatable)
        --plan     only instantiate what is planned; start no run
  assess [workspace] [--format markdown|json]
        Print the assessment: the statistics, the findings, and the facts of every instance,
        as the MCP tool get_assessment returns it (Markdown by default, in the workspace's
        language).

The workspace is the first of the given directory, ALPS_WORKSPACE, and the current directory,
or the nearest parent of it that has alps-harness.yaml or process-model.yaml.

Options:
  -h, --help     Show this help.
  -v, --version  Show the version.
`;

class UsageError extends Error {}

/**
 * ALPS_WORKSPACE, or the current directory. The plugin's .mcp.json sets ALPS_WORKSPACE to
 * ${CLAUDE_PROJECT_DIR}; a value left unexpanded names no directory, and the current directory,
 * where Claude Code starts the server (the project directory), is used (startDirectory).
 */
const defaultStart = (): string =>
  startDirectory(process.env.ALPS_WORKSPACE, process.cwd(), fs.existsSync);

/**
 * Parses `[workspace]` and the given flags. Flags with a value take it as the next argument or
 * after `=`; those in `many` may be repeated, and their values are collected in `lists`.
 */
function parse(args: string[], flags: { boolean: string[]; value: string[]; many?: string[] }) {
  const positional: string[] = [];
  const options: Record<string, string | true> = {};
  const lists: Record<string, string[]> = {};
  for (let i = 0; i < args.length; i++) {
    const arg = args[i] ?? "";
    if (!arg.startsWith("--")) {
      positional.push(arg);
      continue;
    }
    const [name = "", inline] = arg.slice(2).split(/=(.*)/s, 2);
    const many = flags.many?.includes(name) ?? false;
    if (flags.boolean.includes(name) && inline === undefined) options[name] = true;
    else if (flags.value.includes(name) || many) {
      const value = inline ?? args[++i];
      if (value === undefined) throw new UsageError(`--${name} needs a value.`);
      if (many) (lists[name] ??= []).push(value);
      else options[name] = value;
    } else throw new UsageError(`Unknown option: ${arg}`);
  }
  if (positional.length > 1) throw new UsageError(`Unexpected argument: ${positional[1]}`);
  return { workspace: positional[0], options, lists };
}

async function main(argv: string[]): Promise<number> {
  const [command, ...rest] = argv;
  switch (command) {
    case "serve": {
      const { workspace, options } = parse(rest, {
        boolean: ["daemon", "dev", "open"],
        value: ["port"],
      });
      const port = options.port === undefined ? null : Number(options.port);
      if (port !== null && !(Number.isInteger(port) && port >= 0 && port <= 65_535)) {
        throw new UsageError("--port must be an integer from 0 to 65535.");
      }
      const { serve } = await import("./server/commands.ts");
      return serve(
        {
          start: workspace ?? defaultStart(),
          daemon: options.daemon === true,
          port,
          dev: options.dev === true,
          open: options.open === true,
        },
        pkg.version,
      );
    }
    case "stop": {
      const { workspace } = parse(rest, { boolean: [], value: [] });
      const { stop } = await import("./server/commands.ts");
      return stop(workspace ?? defaultStart());
    }
    case "mcp": {
      const { workspace, options } = parse(rest, { boolean: [], value: ["wake"] });
      if (workspace !== undefined) throw new UsageError(`Unexpected argument: ${workspace}`);
      const [{ runMcp }, { parseYaml }] = await Promise.all([
        import("./mcp.ts"),
        import("./server/yaml.ts"),
      ]);
      await runMcp({
        start: defaultStart(),
        parseYaml,
        version: pkg.version,
        wake: typeof options.wake === "string" ? options.wake : null,
      });
      return 0;
    }
    case "wake": {
      const { workspace, options, lists } = parse(rest, {
        boolean: ["plan"],
        value: ["agent", "request"],
        many: ["attach", "process"],
      });
      const { wake } = await import("./server/commands.ts");
      return wake(workspace ?? defaultStart(), {
        agent: typeof options.agent === "string" ? options.agent : undefined,
        request: typeof options.request === "string" ? options.request : undefined,
        // A path is read from the current directory, as the shell gives it; the server keeps it
        // relative to the workspace and refuses one outside it.
        attachments: (lists.attach ?? []).map((given) => path.resolve(given)),
        processes: lists.process ?? [],
        plan: options.plan === true,
      });
    }
    case "assess": {
      const { workspace, options } = parse(rest, { boolean: [], value: ["format"] });
      const format = options.format ?? "markdown";
      if (format !== "markdown" && format !== "json")
        throw new UsageError("--format must be markdown or json.");
      const { assess } = await import("./server/commands.ts");
      return assess(workspace ?? defaultStart(), format);
    }
    case "-h":
    case "--help":
      console.log(USAGE);
      return 0;
    case "-v":
    case "--version":
      console.log(pkg.version);
      return 0;
    case undefined:
      console.error(USAGE);
      return 2;
    default:
      throw new UsageError(`Unknown command: ${command}`);
  }
}

try {
  process.exit(await main(process.argv.slice(2)));
} catch (error) {
  if (!(error instanceof UsageError)) throw error;
  console.error(`${error.message}\n\n${USAGE}`);
  process.exit(2);
}
