/*
 * The agents that can run a Process: how each is started, how its availability is read from
 * `<command> --version`, and how the command line is recorded. Pure functions only; src/server/
 * starts the processes.
 */

import { MAX_WAIT_SECONDS, type HarnessConfig } from "../shared/schema.ts";
import type { AgentInfo } from "../shared/types.ts";

export { parseOutputLine, type EventDraft, type ParsedLine } from "./parse.ts";

/** How an agent is run and how its standard output is read. */
export type AgentFormat = "claude" | "codex" | "text" | "demo" | "self";

export interface AgentSpec {
  id: string;
  label: string;
  format: AgentFormat;
  /** The executable; `null` for demo and self, which start no process. */
  command: string | null;
  /** `{prompt}` stands for the prompt. */
  args: string[];
  /** Pass the prompt on standard input instead of as an argument (the default on Windows, whose arguments cannot hold newlines). */
  stdin: boolean;
  env: Record<string, string>;
}

type Defaults = Omit<AgentSpec, "id" | "stdin" | "env"> & { stdin?: boolean };

const DEFAULTS: Record<string, Defaults> = {
  "claude-code": {
    label: "Claude Code",
    format: "claude",
    command: "claude",
    args: [
      "-p",
      "{prompt}",
      "--output-format",
      "stream-json",
      "--verbose",
      "--permission-mode",
      "acceptEdits",
    ],
  },
  codex: {
    label: "Codex",
    format: "codex",
    command: "codex",
    args: ["exec", "--json", "--sandbox", "workspace-write", "--skip-git-repo-check", "{prompt}"],
  },
  demo: { label: "Demo", format: "demo", command: null, args: [], stdin: false },
  self: { label: "The calling session", format: "self", command: null, args: [], stdin: false },
};

/**
 * The variables by which a Claude Code session marks the processes it starts, or ties them to
 * itself. A harness server started from inside a session (by the Plugin's MCP server, or from a
 * shell of the session) inherits them, and a `claude` started with them takes itself for a part
 * of that session: it refuses to start as a nested session (CLAUDECODE), reports the session's
 * entry point, joins the session's IDE (CLAUDE_CODE_SSE_PORT) and its desktop app's channel and
 * host, and takes over its effort. A Claude Code agent does not inherit them: of the variables
 * that the user's settings and the running session put in the server's environment, only these
 * marks are left out. Any variable not listed here is passed on: the user's credentials
 * (ANTHROPIC_API_KEY and the like) and PATH, and also the other variables that a session sets
 * (other CLAUDE_CODE_* variables and ANTHROPIC_BASE_URL among them). How a `claude` started with
 * those behaves is not verified: the real runs were made from a server started without the
 * desktop session's variables. The agent's `env` in alps-harness.yaml is added after, and can
 * still set any variable.
 */
export const CLAUDE_SESSION_VARIABLES: readonly string[] = [
  "CLAUDECODE",
  "CLAUDE_CODE_ENTRYPOINT",
  "CLAUDE_CODE_SSE_PORT",
  "CLAUDE_EFFORT",
  "CLAUDE_CODE_SESSION_ID",
  "CLAUDE_CODE_HOST_SESSION_ID",
  "CLAUDE_CODE_CHILD_SESSION",
  "CLAUDE_CODE_SESSION_ATTENDED",
  "CLAUDE_CODE_MESSAGING_SOCKET",
  "CLAUDE_CODE_MESSAGING_TOKEN",
  "CLAUDE_CODE_TERMINAL_MCP_TOOLS",
  "CLAUDE_CODE_SDK_HAS_HOST_AUTH_REFRESH",
  "CLAUDE_CODE_DESKTOP_APP_VERSION",
  "CLAUDE_AGENT_SDK_VERSION",
  "CLAUDE_CODE_EXECPATH",
  "CLAUDE_PID",
];

/** The variables of the harness server's environment that an agent's process does not inherit. */
export const envLeftOut = (spec: AgentSpec): readonly string[] =>
  spec.format === "claude" ? CLAUDE_SESSION_VARIABLES : [];

/** The agents of a workspace: the defaults, changed or removed by `agents` in alps-harness.yaml. */
export function resolveAgents(
  overrides: HarnessConfig["agents"],
  platform: string = process.platform,
): AgentSpec[] {
  const specs = new Map<string, AgentSpec>();
  const complete = (id: string, spec: Defaults): AgentSpec => ({
    id,
    ...spec,
    stdin: spec.stdin ?? platform === "win32",
    env: {},
  });
  for (const [id, spec] of Object.entries(DEFAULTS)) specs.set(id, complete(id, spec));
  for (const [id, override] of Object.entries(overrides ?? {})) {
    if (override === false || override === null) {
      specs.delete(id);
      continue;
    }
    const base =
      specs.get(id) ??
      complete(id, { label: id, format: "text", command: null, args: [], stdin: false });
    specs.set(id, {
      ...base,
      label: override.label ?? base.label,
      // demo and self start no process; their format is theirs.
      format:
        base.format === "demo" || base.format === "self"
          ? base.format
          : (override.format ?? base.format),
      command: override.command ?? base.command,
      args: override.args ?? base.args,
      stdin: override.stdin ?? base.stdin,
      env: { ...base.env, ...override.env },
    });
  }
  return [...specs.values()];
}

/** Whether the agent starts a process (and so needs a command and a version check). */
export const startsProcess = (spec: AgentSpec): boolean =>
  spec.format !== "demo" && spec.format !== "self";

/** What starting an agent's process takes. src/server/ starts it (Bun.spawn). */
export interface AgentLaunch {
  command: string;
  args: string[];
  cwd: string;
  /** Left out of the environment of the harness server (envLeftOut), before `env` is added. */
  unset: readonly string[];
  /** Added to the environment of the harness server. */
  env: Record<string, string>;
  /** Written to standard input, which is then closed; `null` gives the agent an empty standard input. */
  stdin: string | null;
}

/** Receives an agent's output one line at a time, without the line end. */
export interface AgentOutput {
  stdout(line: string): void;
  stderr(line: string): void;
}

/** A started agent process, in a process group of its own (on Windows, a process tree). */
export interface AgentHandle {
  pid: number;
  /**
   * Stops the agent and every process it started: SIGTERM to its process group, then SIGKILL to
   * what is left after 5 seconds (on Windows, taskkill of its process tree). Calling it again
   * changes nothing.
   */
  stop(): void;
  /**
   * Resolves once the agent has exited and its output has been read. Output that processes it
   * left behind keep open ends the wait after a short grace period, and those processes are stopped.
   */
  done: Promise<{ exitCode: number | null; signal: string | null }>;
}

/** The arguments for a prompt. With `stdin`, the prompt is left out (codex reads it from `-`). */
export function argsFor(spec: AgentSpec, prompt: string): string[] {
  if (!spec.stdin) return spec.args.map((arg) => arg.split("{prompt}").join(prompt));
  const args = spec.args.filter((arg) => arg !== "{prompt}");
  if (spec.format === "codex" && !args.includes("-")) args.push("-");
  return args;
}

/** An MCP server that an agent starts on stdio: here, the harness's own for the agent a wake starts. */
export interface McpServerLaunch {
  /** The server's name, which prefixes its tools for the agent (Claude Code: `mcp__<name>__<tool>`). */
  name: string;
  command: string;
  args: string[];
  env: Record<string, string>;
}

/** Whether the harness can give the agent an MCP server: Claude Code and Codex, by their formats. */
export const takesMcpServer = (spec: AgentSpec): boolean =>
  spec.format === "claude" || spec.format === "codex";

/** The file for Claude Code's `--mcp-config`: the server as `.mcp.json` names one. */
export const mcpConfigFile = (server: McpServerLaunch): string =>
  `${JSON.stringify(
    {
      mcpServers: {
        [server.name]: {
          type: "stdio",
          command: server.command,
          args: server.args,
          env: server.env,
        },
      },
    },
    null,
    2,
  )}\n`;

/**
 * The arguments that give an agent an MCP server and let it call that server's tools without
 * asking; everything else follows the agent's own defaults. Claude Code reads the server from
 * `configFile` (--mcp-config, written with mcpConfigFile) and from nowhere else (--strict-mcp-config:
 * the user's other MCP servers, such as the claude.ai connectors, are not loaded), and is allowed
 * its tools (--allowedTools mcp__<name>). Codex takes it as configuration overrides (-c, dotted
 * keys with TOML values, which JSON strings and arrays of strings are), with its tools approved,
 * since `codex exec` cannot ask, and with a tool timeout longer than get_run's longest wait
 * (Codex's own is 60 s).
 */
export function mcpArgs(spec: AgentSpec, server: McpServerLaunch, configFile: string): string[] {
  if (spec.format === "claude")
    return [
      "--mcp-config",
      configFile,
      "--strict-mcp-config",
      "--allowedTools",
      `mcp__${server.name}`,
    ];
  if (spec.format !== "codex") return [];
  const key = `mcp_servers.${server.name}`;
  return [
    ["command", JSON.stringify(server.command)],
    ["args", JSON.stringify(server.args)],
    ...Object.entries(server.env).map(([name, value]) => [`env.${name}`, JSON.stringify(value)]),
    ["default_tools_approval_mode", JSON.stringify("approve")],
    ["tool_timeout_sec", String(MAX_WAIT_SECONDS + 30)],
  ].flatMap(([name, value]) => ["-c", `${key}.${name}=${value}`]);
}

/** The command line as recorded in the run, with the prompt left out. */
export function commandLine(spec: AgentSpec, args: string[], prompt: string): string | null {
  if (!spec.command) return null;
  const shown = args.map((arg) =>
    arg === prompt ? "<prompt>" : /[\s"'\\]/.test(arg) ? JSON.stringify(arg) : arg,
  );
  return [spec.command, ...shown].join(" ");
}

/** The outcome of running `<command> --version`. */
export interface VersionCheck {
  exitCode: number | null;
  stdout: string;
  /** The command does not exist. */
  notFound: boolean;
  timedOut: boolean;
}

const MAX_VERSION_LENGTH = 80;

/** An agent's availability. Demo and self are always available; the others when `--version` succeeds. */
export function agentInfo(spec: AgentSpec, check: VersionCheck | null): AgentInfo {
  const info = { id: spec.id, label: spec.label };
  if (!startsProcess(spec)) return { ...info, available: true, version: null, reason: null };
  if (!spec.command)
    return { ...info, available: false, version: null, reason: "no command is configured" };
  if (!check || check.notFound)
    return { ...info, available: false, version: null, reason: `${spec.command} was not found` };
  if (check.timedOut)
    return {
      ...info,
      available: false,
      version: null,
      reason: `${spec.command} --version did not answer`,
    };
  if (check.exitCode !== 0)
    return {
      ...info,
      available: false,
      version: null,
      reason: `${spec.command} --version failed (exit code ${check.exitCode})`,
    };
  const version = check.stdout.trim().split("\n")[0]?.trim().slice(0, MAX_VERSION_LENGTH) ?? "";
  return { ...info, available: true, version: version || null, reason: null };
}
