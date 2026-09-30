/*
 * Reading an agent's standard output as the harness's common events (system, message, thinking,
 * tool, output, stderr, error, result, end), with the usage and the final report it carries.
 * One line at a time; a line that is not JSON is output.
 */

import type { RunEvent, Usage } from "../shared/types.ts";
import type { AgentFormat } from "./index.ts";

export type EventDraft = Pick<RunEvent, "kind" | "text" | "key" | "args">;

/** What one line of output means for the run. */
export interface ParsedLine {
  events: EventDraft[];
  usage?: Usage;
  report?: string;
  agentError?: string;
}

type Json = Record<string, unknown>;

const MAX_REPORT_LENGTH = 6000;
const MAX_TOOL_ERROR_LENGTH = 600;
/** The longest line of a tool call, and of one argument value of an MCP tool call. */
const MAX_TOOL_LENGTH = 200;
const MAX_VALUE_LENGTH = 40;

const isJson = (value: unknown): value is Json =>
  value !== null && typeof value === "object" && !Array.isArray(value);
const text = (value: unknown): string =>
  typeof value === "string" ? value.trim() : typeof value === "number" ? String(value) : "";
const num = (value: unknown): number | null => (typeof value === "number" ? value : null);
const firstLine = (value: unknown, length = MAX_TOOL_LENGTH): string =>
  (String(value ?? "").split("\n")[0] ?? "").slice(0, length);
/** The first line, cut at its end when it is longer. */
const head = (value: unknown, length: number): string => {
  const line = firstLine(value, Number.POSITIVE_INFINITY);
  return line.length > length ? `${line.slice(0, length - 1)}…` : line;
};
/** The first line, cut at its start when it is longer: the end of a path is its file's name. */
const tail = (value: unknown, length = MAX_TOOL_LENGTH): string => {
  const line = firstLine(value, Number.POSITIVE_INFINITY);
  return line.length > length ? `…${line.slice(line.length - length + 1)}` : line;
};
const list = (value: unknown): unknown[] => (Array.isArray(value) ? value : []);
const plural = (count: number, one: string): string => `${count} ${one}${count === 1 ? "" : "s"}`;
/** The sum of the numbers among the values; `null` when there is none. */
const total = (...values: unknown[]): number | null => {
  const known = values.filter((value): value is number => typeof value === "number");
  return known.length ? known.reduce((sum, value) => sum + value, 0) : null;
};

/** An argument of an MCP tool call, shortly: a string's first line, a list's length, `{…}` for an object. */
function gist(value: unknown): string {
  if (typeof value === "string") return JSON.stringify(head(value, MAX_VALUE_LENGTH));
  if (typeof value === "number" || typeof value === "boolean" || value === null)
    return String(value);
  if (Array.isArray(value)) return value.length ? `[${plural(value.length, "item")}]` : "[]";
  return isJson(value) && Object.keys(value).length === 0 ? "{}" : "{…}";
}

/**
 * A tool call in one line: the tool and what it works on. A path (Claude Code gives absolute ones)
 * keeps its end; Glob and Grep show their pattern and where they look; an MCP tool
 * (`mcp__<server>__<tool>`) shows each argument's name and a short value.
 */
function toolText(name: unknown, input: unknown): string {
  const tool = text(name);
  const i = isJson(input) ? input : {};
  if (tool.startsWith("mcp__")) {
    const [, server = "", ...rest] = tool.split("__");
    const args = Object.entries(i).map(([key, value]) => `${key}=${gist(value)}`);
    return head(
      `MCP ${server} ${rest.join("__")}${args.length ? ` ${args.join(", ")}` : ""}`,
      MAX_TOOL_LENGTH,
    );
  }
  const where = i.file_path ?? i.notebook_path ?? i.path;
  const place = where === undefined || where === null || where === "" ? "" : tail(where);
  if (tool === "Glob" || tool === "Grep") {
    const pattern = i.pattern === undefined || i.pattern === null ? "" : firstLine(i.pattern);
    return [tool, pattern, place && `in ${place}`].filter(Boolean).join(" ");
  }
  if (place) return `${tool} ${place}`;
  const arg = i.command ?? i.pattern ?? i.url ?? i.query ?? i.description ?? "";
  return `${tool}${arg ? ` ${firstLine(arg)}` : ""}`;
}

const contentText = (content: unknown): string =>
  typeof content === "string"
    ? content
    : list(content)
        .map((part) => (isJson(part) ? text(part.text) : ""))
        .join("");

/** Claude Code: `claude -p --output-format stream-json --verbose`. */
function parseClaude(line: Json): ParsedLine {
  const message = isJson(line.message) ? line.message : {};
  switch (line.type) {
    case "system": {
      if (line.subtype !== "init") return { events: [] };
      const events: EventDraft[] = [
        { kind: "system", text: `Session started${line.model ? ` (${text(line.model)})` : ""}` },
      ];
      // Whether each MCP server could be reached (connected, failed, needs-auth, …).
      const servers = list(line.mcp_servers).flatMap((server) =>
        isJson(server) && text(server.name)
          ? [`${text(server.name)} (${text(server.status) || "status unknown"})`]
          : [],
      );
      if (servers.length)
        events.push({ kind: "system", text: `MCP servers: ${servers.join(", ")}` });
      return { events };
    }
    case "rate_limit_event": {
      const info = isJson(line.rate_limit_info) ? line.rate_limit_info : {};
      const status = text(info.status);
      if (!status) return { events: [] };
      const window = text(info.rateLimitType);
      // resetsAt is in seconds since the epoch.
      const resets = new Date((num(info.resetsAt) ?? Number.NaN) * 1000);
      const at = Number.isNaN(resets.getTime())
        ? ""
        : `, resets at ${resets.toISOString().replace(/\.\d{3}Z$/, "Z")}`;
      return {
        events: [
          { kind: "system", text: `Rate limit${window ? ` (${window})` : ""}: ${status}${at}` },
        ],
      };
    }
    case "assistant": {
      // A message that Claude Code writes itself when it cannot use the model (model
      // "<synthetic>", with `error` such as "authentication_failed") tells why: it is an error.
      const failure = text(line.error);
      const events: EventDraft[] = [];
      for (const part of list(message.content)) {
        if (!isJson(part)) continue;
        if (part.type === "text" && text(part.text))
          events.push({ kind: failure ? "error" : "message", text: text(part.text) });
        else if (part.type === "tool_use")
          events.push({ kind: "tool", text: toolText(part.name, part.input) });
        else if (part.type === "thinking" && text(part.thinking))
          events.push({ kind: "thinking", text: text(part.thinking) });
      }
      if (failure && !events.some((event) => event.kind === "error"))
        events.push({ kind: "error", text: failure });
      return { events };
    }
    case "user": {
      // Tool results are long; only failures are kept.
      const events: EventDraft[] = [];
      for (const part of list(message.content)) {
        if (isJson(part) && part.type === "tool_result" && part.is_error === true)
          events.push({
            kind: "error",
            text: contentText(part.content).slice(0, MAX_TOOL_ERROR_LENGTH) || "A tool failed",
          });
      }
      return { events };
    }
    case "result": {
      const tokens = isJson(line.usage) ? line.usage : {};
      const subtype = text(line.subtype);
      const failed = line.is_error === true || (subtype !== "" && subtype !== "success");
      // The subtype names the failure (error_max_turns, error_during_execution); a failure whose
      // subtype is still "success", as when Claude Code is not logged in, is told by its result.
      const reason = !failed
        ? ""
        : (subtype !== "success" && subtype) || firstLine(text(line.result)) || "error";
      // How the agent's session ended by its own account: why it stopped (terminal_reason), how
      // long it took, how many turns (Claude Code's num_turns is its tool round trips plus one, a
      // different unit from --max-turns), and the tool uses that its permissions denied.
      const ending = text(line.terminal_reason);
      const ms = num(line.duration_ms);
      const turns = num(line.num_turns);
      const denials = list(line.permission_denials);
      const firstDenied = denials.map((d) => (isJson(d) ? text(d.tool_name) : "")).find(Boolean);
      const denied = denials.length
        ? `${plural(denials.length, "tool use")} denied${firstDenied ? `, the first ${firstDenied}` : ""}`
        : "";
      const spent = [
        ms === null ? "" : ms < 1000 ? `${ms} ms` : `${Math.round(ms / 1000)} s`,
        turns === null ? "" : `${plural(turns, "turn")} (tool round trips + 1)`,
      ].filter(Boolean);
      const events: EventDraft[] = [
        {
          kind: "result",
          text: failed
            ? `The agent reported a failure (${reason})`
            : "The agent reported the end of its work",
        },
      ];
      if (ending || spent.length || denied)
        events.push({
          kind: "system",
          text: `The agent ended${ending ? ` (${ending})` : ""}${
            spent.length ? ` after ${spent.join(" and ")}` : ""
          }${denied ? `; ${denied}` : ""}`,
        });
      const agentError = !failed
        ? undefined
        : `${reason}${ending && ending !== "completed" && !reason.includes(ending) ? ` (${ending})` : ""}${
            denied ? `; ${denied}` : ""
          }`;
      return {
        events,
        // Input tokens are counted as Codex counts them: those written to and read from the
        // prompt cache included.
        usage: {
          costUsd: num(line.total_cost_usd),
          turns,
          inputTokens: total(
            tokens.input_tokens,
            tokens.cache_creation_input_tokens,
            tokens.cache_read_input_tokens,
          ),
          cachedInputTokens: num(tokens.cache_read_input_tokens),
          outputTokens: num(tokens.output_tokens),
        },
        ...(line.result === undefined || line.result === null
          ? {}
          : { report: String(line.result).slice(0, MAX_REPORT_LENGTH) }),
        ...(agentError === undefined ? {} : { agentError }),
      };
    }
    default:
      return { events: [] };
  }
}

/**
 * A Codex error message. When the model's API refused the request, Codex puts the API's error,
 * as JSON, in the message (`{"type":"error","status":400,"error":{"message":…}}`); its message
 * says what went wrong.
 */
function codexMessage(value: unknown): string {
  const said = text(value);
  if (!said.startsWith("{")) return said;
  try {
    const parsed: unknown = JSON.parse(said);
    const inner = isJson(parsed)
      ? isJson(parsed.error)
        ? parsed.error.message
        : parsed.message
      : undefined;
    return text(inner) || said;
  } catch {
    return said;
  }
}

/** Codex: `codex exec --json` (thread.*, turn.*, item.*). */
function parseCodex(line: Json): ParsedLine {
  switch (line.type) {
    case "thread.started":
      return { events: [{ kind: "system", text: "Thread started" }] };
    case "turn.completed": {
      if (!isJson(line.usage)) return { events: [] };
      // Codex's input tokens include those read from the prompt cache.
      return {
        events: [],
        usage: {
          costUsd: null,
          turns: null,
          inputTokens: num(line.usage.input_tokens),
          cachedInputTokens: num(line.usage.cached_input_tokens),
          outputTokens: num(line.usage.output_tokens),
        },
      };
    }
    case "turn.failed": {
      const error = (isJson(line.error) && codexMessage(line.error.message)) || "turn.failed";
      return { events: [{ kind: "error", text: error }], agentError: error };
    }
    case "error":
      return { events: [{ kind: "error", text: codexMessage(line.message) || "error" }] };
    case "item.completed": {
      const item = isJson(line.item) ? line.item : {};
      const type = item.type ?? item.item_type;
      if (type === "agent_message" || type === "assistant_message") {
        const said = text(item.text);
        return {
          events: said ? [{ kind: "message", text: said }] : [],
          report: String(item.text ?? "").slice(0, MAX_REPORT_LENGTH),
        };
      }
      if (type === "reasoning")
        return { events: text(item.text) ? [{ kind: "thinking", text: text(item.text) }] : [] };
      if (type === "command_execution") {
        const code = item.exit_code;
        const failed = typeof code === "number" && code !== 0 ? ` (exit code ${code})` : "";
        return { events: [{ kind: "tool", text: `$ ${firstLine(item.command)}${failed}` }] };
      }
      if (type === "file_change") {
        const paths = list(item.changes).map((change) => (isJson(change) ? text(change.path) : ""));
        return { events: [{ kind: "tool", text: `Changed ${paths.filter(Boolean).join(", ")}` }] };
      }
      if (type === "mcp_tool_call")
        return {
          events: [
            {
              kind: "tool",
              text: `MCP ${[text(item.server), text(item.tool)].filter(Boolean).join(" ")}${
                item.status === "failed" ? " (failed)" : ""
              }`,
            },
          ],
        };
      if (type === "web_search")
        return { events: [{ kind: "tool", text: `Web search ${text(item.query)}`.trim() }] };
      if (type === "error")
        return { events: [{ kind: "error", text: codexMessage(item.message) || "error" }] };
      return { events: [] };
    }
    default:
      return { events: [] };
  }
}

/**
 * Reads one line of an agent's standard output. It does not throw: a line that cannot be read
 * as the format says (not JSON, or JSON of a shape that cannot be read, such as an object where
 * text belongs) is output.
 */
export function parseOutputLine(format: AgentFormat, line: string): ParsedLine {
  if ((format === "claude" || format === "codex") && line.startsWith("{")) {
    let parsed: unknown;
    try {
      parsed = JSON.parse(line);
    } catch {
      parsed = undefined;
    }
    if (isJson(parsed))
      try {
        return format === "claude" ? parseClaude(parsed) : parseCodex(parsed);
      } catch {
        // String() of an object whose toString is not a function throws; the line is output.
      }
  }
  return { events: [{ kind: "output", text: line }] };
}
