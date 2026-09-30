#!/usr/bin/env bun
/* alps-harness: the harness's command line. */

import pkg from "../package.json" with { type: "json" };

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
  wake [workspace] [--agent <agent>]
        Wake an agent, as the schedules in alps-harness.yaml and the MCP tool wake do: it is
        started with the harness's MCP server and decides which Processes to run. For an
        external scheduler (launchd, cron, CI). It returns once the agent has started; while
        another wake runs, none is started (skipped).
        --agent  claude-code (the default) or codex
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

const defaultStart = (): string => process.env.ALPS_WORKSPACE || process.cwd();

/** Parses `[workspace]` and the given flags. Flags with a value take it as the next argument or after `=`. */
function parse(args: string[], flags: { boolean: string[]; value: string[] }) {
  const positional: string[] = [];
  const options: Record<string, string | true> = {};
  for (let i = 0; i < args.length; i++) {
    const arg = args[i] ?? "";
    if (!arg.startsWith("--")) {
      positional.push(arg);
      continue;
    }
    const [name = "", inline] = arg.slice(2).split(/=(.*)/s, 2);
    if (flags.boolean.includes(name) && inline === undefined) options[name] = true;
    else if (flags.value.includes(name)) {
      const value = inline ?? args[++i];
      if (value === undefined) throw new UsageError(`--${name} needs a value.`);
      options[name] = value;
    } else throw new UsageError(`Unknown option: ${arg}`);
  }
  if (positional.length > 1) throw new UsageError(`Unexpected argument: ${positional[1]}`);
  return { workspace: positional[0], options };
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
      const { workspace, options } = parse(rest, { boolean: [], value: ["agent"] });
      const { wake } = await import("./server/commands.ts");
      return wake(
        workspace ?? defaultStart(),
        typeof options.agent === "string" ? options.agent : undefined,
      );
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
