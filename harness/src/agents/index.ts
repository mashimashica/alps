/*
 * The agents that can run a Process: how each is started, how its availability is read from
 * `<command> --version`, and how the command line is recorded. Pure functions only; src/server/
 * starts the processes.
 */

import type { HarnessConfig } from "../shared/schema.ts";
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
