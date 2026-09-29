/*
 * Reading an agent's standard output as the harness's common events (system, message, thinking,
 * tool, output, stderr, error, result, end), with the usage and the final report it carries.
 * One line at a time; a line that is not JSON is output.
 */

import type { RunEvent, Usage } from "../shared/types.ts";
import type { AgentFormat } from "./index.ts";

export interface EventDraft {
  kind: RunEvent["kind"];
  text: string;
}

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

const isJson = (value: unknown): value is Json =>
  value !== null && typeof value === "object" && !Array.isArray(value);
const text = (value: unknown): string =>
  typeof value === "string" ? value.trim() : typeof value === "number" ? String(value) : "";
const num = (value: unknown): number | null => (typeof value === "number" ? value : null);
const firstLine = (value: unknown, length = 200): string =>
  (String(value ?? "").split("\n")[0] ?? "").slice(0, length);
const list = (value: unknown): unknown[] => (Array.isArray(value) ? value : []);

function toolText(name: unknown, input: unknown): string {
  const i = isJson(input) ? input : {};
  const arg =
    i.file_path ?? i.path ?? i.command ?? i.pattern ?? i.url ?? i.query ?? i.description ?? "";
  return `${text(name)}${arg ? ` ${firstLine(arg)}` : ""}`;
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
    case "system":
      return {
        events:
          line.subtype === "init"
            ? [
                {
                  kind: "system",
                  text: `Session started${line.model ? ` (${text(line.model)})` : ""}`,
                },
              ]
            : [],
      };
    case "assistant": {
      const events: EventDraft[] = [];
      for (const part of list(message.content)) {
        if (!isJson(part)) continue;
        if (part.type === "text" && text(part.text))
          events.push({ kind: "message", text: text(part.text) });
        else if (part.type === "tool_use")
          events.push({ kind: "tool", text: toolText(part.name, part.input) });
        else if (part.type === "thinking" && text(part.thinking))
          events.push({ kind: "thinking", text: text(part.thinking) });
      }
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
      const failed =
        line.is_error === true || (line.subtype !== undefined && line.subtype !== "success");
      const subtype = text(line.subtype) || "error";
      return {
        events: [
          {
            kind: "result",
            text: failed
              ? `The agent reported a failure (${subtype})`
              : "The agent reported the end of its work",
          },
        ],
        usage: {
          costUsd: num(line.total_cost_usd),
          turns: num(line.num_turns),
          inputTokens: num(tokens.input_tokens),
          outputTokens: num(tokens.output_tokens),
        },
        ...(line.result === undefined || line.result === null
          ? {}
          : { report: String(line.result).slice(0, MAX_REPORT_LENGTH) }),
        ...(failed ? { agentError: subtype } : {}),
      };
    }
    default:
      return { events: [] };
  }
}

/** Codex: `codex exec --json` (thread.*, turn.*, item.*). */
function parseCodex(line: Json): ParsedLine {
  switch (line.type) {
    case "thread.started":
      return { events: [{ kind: "system", text: "Thread started" }] };
    case "turn.completed": {
      if (!isJson(line.usage)) return { events: [] };
      return {
        events: [],
        usage: {
          costUsd: null,
          turns: null,
          inputTokens: num(line.usage.input_tokens),
          outputTokens: num(line.usage.output_tokens),
        },
      };
    }
    case "turn.failed": {
      const error = (isJson(line.error) && text(line.error.message)) || "turn.failed";
      return { events: [{ kind: "error", text: error }], agentError: error };
    }
    case "error":
      return { events: [{ kind: "error", text: text(line.message) || "error" }] };
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
              text: `MCP ${[text(item.server), text(item.tool)].filter(Boolean).join(" ")}`,
            },
          ],
        };
      if (type === "web_search")
        return { events: [{ kind: "tool", text: `Web search ${text(item.query)}`.trim() }] };
      if (type === "error")
        return { events: [{ kind: "error", text: text(item.message) || "error" }] };
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
