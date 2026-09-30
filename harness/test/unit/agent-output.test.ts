/*
 * Reading an agent's output (Agents): a line of a shape the harness cannot read is kept as
 * output, and a line the harness fails on does not stop the reading, so the rest of the output
 * (the report and the usage come last) still reaches the run. A Codex failure, as recorded from
 * the real agent (test/fixtures/agents/codex-fail.jsonl), is read as what went wrong. Claude
 * Code's lines are those of the real Claude Code 2.1.96 (stage 7b, 2026-09-30), with the
 * machine's paths and the ids made neutral: the tool calls show what they work on, and the
 * session's MCP servers, the rate limit, and how the session ended by its own account are events.
 */

import { describe, expect, test } from "bun:test";
import fs from "node:fs";
import { parseOutputLine } from "../../src/agents/index.ts";
import { startAgent } from "../../src/server/agent-process.ts";

describe("agent output", () => {
  test("a Codex failure is read as the message of the API error it carries, and a failed MCP call is marked", () => {
    const recorded = fs
      .readFileSync(new URL("../fixtures/agents/codex-fail.jsonl", import.meta.url), "utf8")
      .trim()
      .split("\n")
      .map((line) => parseOutputLine("codex", line.replace("{{SESSION}}", "s")));
    const refused =
      "The 'no-such-model' model is not supported when using Codex with a ChatGPT account.";
    expect(recorded.at(-2)).toEqual({ events: [{ kind: "error", text: refused }] });
    expect(recorded.at(-1)).toEqual({
      events: [{ kind: "error", text: refused }],
      agentError: refused,
    });
    // A failed MCP call as the real Codex recorded it, when the harness had found no workspace
    // where Codex started it (the Plugin root): the status says failed, and error is null.
    const failedCall = String.raw`{"type":"item.completed","item":{"id":"item_3","type":"mcp_tool_call","server":"alps_harness","tool":"get_model","arguments":{},"result":{"content":[{"type":"text","text":"{\n  \"ok\": false,\n  \"error\": {\n    \"code\": \"no-model\",\n    \"message\": \"No alps-harness.yaml or process-model.yaml in /plugins/alps or its parent directories. Place one of them (error.files) to make it a workspace.\",\n    \"key\": \"error.noWorkspace\",\n    \"args\": {\n      \"start\": \"/plugins/alps\"\n    },\n    \"files\": [\n      \"/plugins/alps/alps-harness.yaml\",\n      \"/plugins/alps/process-model.yaml\"\n    ]\n  }\n}"},{"type":"text","text":"No alps-harness.yaml or process-model.yaml in /plugins/alps or its parent directories. Place one of them (error.files) to make it a workspace."}],"structured_content":{"ok":false,"error":{"code":"no-model","message":"No alps-harness.yaml or process-model.yaml in /plugins/alps or its parent directories. Place one of them (error.files) to make it a workspace.","key":"error.noWorkspace","args":{"start":"/plugins/alps"},"files":["/plugins/alps/alps-harness.yaml","/plugins/alps/process-model.yaml"]}}},"error":null,"status":"failed"}}`;
    expect(parseOutputLine("codex", failedCall)).toEqual({
      events: [{ kind: "tool", text: "MCP alps_harness get_model (failed)" }],
    });
    expect(
      parseOutputLine("codex", failedCall.replace('"status":"failed"', '"status":"completed"')),
    ).toEqual({ events: [{ kind: "tool", text: "MCP alps_harness get_model" }] });
  });

  test("a line of an unexpected shape is output, not an exception", () => {
    // Objects where text belongs, whose toString is not a function.
    const lines = [
      ["claude", '{"type":"result","result":{"toString":0}}'],
      [
        "claude",
        '{"type":"assistant","message":{"content":[{"type":"tool_use","name":"Read","input":{"file_path":{"toString":1}}}]}}',
      ],
      [
        "codex",
        '{"type":"item.completed","item":{"type":"command_execution","command":{"toString":"x"}}}',
      ],
    ] as const;
    for (const [format, line] of lines)
      expect(parseOutputLine(format, line)).toEqual({ events: [{ kind: "output", text: line }] });
  });

  test("the output is read to its end when the harness fails on a line of it", async () => {
    // Far more than a pipe holds (64 KiB), so the agent's writing depends on the reading.
    const count = 20_000;
    const seen: string[] = [];
    const handle = startAgent(
      {
        command: process.execPath,
        args: [
          "-e",
          `for (let i = 0; i < ${count}; i++) console.log(\`line \${i} \${"-".repeat(20)}\`);`,
        ],
        cwd: import.meta.dir,
        unset: [],
        env: {},
        stdin: null,
      },
      {
        stdout: (line) => {
          seen.push(line);
          if (seen.length === 1) throw new Error("the harness failed on a line");
        },
        stderr: () => {},
      },
    );
    const end = await Promise.race([handle.done, Bun.sleep(20_000).then(() => null)]);
    if (end === null) handle.stop();
    expect(end).toEqual({ exitCode: 0, signal: null });
    expect(seen.length).toBe(count);
    expect(seen.at(-1)).toBe(`line ${count - 1} ${"-".repeat(20)}`);
  }, 30_000);
});

/** The workspace of stage 7b, with this machine's user, session, and ids made neutral (same length). */
const WS =
  "/private/tmp/claude-0000000000/-Users-a-user-name-Project-alps-harness/00000000-0000-4000-8000-000000000000/scratchpad/stage7/ws-claude/examples/service-change";

/** A tool call as Claude Code 2.1.96 writes it: one tool_use in an assistant message. */
const call = (name: string, input: Record<string, unknown>): string =>
  JSON.stringify({
    type: "assistant",
    message: {
      model: "claude-opus-4-6",
      id: "msg_fake_01",
      type: "message",
      role: "assistant",
      content: [{ type: "tool_use", id: "toolu_fake_01", name, input, caller: { type: "direct" } }],
      container: null,
      stop_reason: null,
      stop_sequence: null,
      stop_details: null,
      usage: { input_tokens: 1, cache_creation_input_tokens: 1129, cache_read_input_tokens: 32476 },
      diagnostics: null,
      context_management: null,
    },
    parent_tool_use_id: null,
    session_id: "fake-session",
    uuid: "00000000-0000-4000-8000-000000000001",
  });
const toolText = (name: string, input: Record<string, unknown>): string | undefined =>
  parseOutputLine("claude", call(name, input)).events[0]?.text;

/** The result line of the wake r16 (Claude Code 2.1.96), without its usage details. */
const RESULT = {
  type: "result",
  subtype: "success",
  is_error: false,
  duration_ms: 320968,
  duration_api_ms: 195173,
  num_turns: 23,
  result: "## What I did",
  stop_reason: "end_turn",
  session_id: "fake-session",
  total_cost_usd: 0.7426932500000001,
  usage: {
    input_tokens: 16,
    cache_creation_input_tokens: 44063,
    cache_read_input_tokens: 420239,
    output_tokens: 10284,
  },
  permission_denials: [],
  terminal_reason: "completed",
  fast_mode_state: "off",
  uuid: "00000000-0000-4000-8000-000000000066",
};

describe("Claude Code's output (stage 7b)", () => {
  test("Glob and Grep show their pattern and where they look, and a long path keeps its end", () => {
    expect(toolText("Glob", { pattern: "docs/changes/**/change-brief.md", path: WS })).toBe(
      `Glob docs/changes/**/change-brief.md in ${WS}`,
    );
    // Grep takes the same pattern and path (no Grep was in the recorded runs).
    expect(
      toolText("Grep", {
        pattern: "acceptance condition",
        path: "docs/changes",
        glob: "*.md",
        output_mode: "files_with_matches",
      }),
    ).toBe("Grep acceptance condition in docs/changes");
    expect(toolText("Glob", { pattern: "**/*.md" })).toBe("Glob **/*.md");
    // 202 characters: the start gives way, so that the file's name stays.
    const file = `${WS}/measurements/CHG-001/measurement-status.md`;
    expect(file).toHaveLength(202);
    const read = toolText("Read", { file_path: file }) ?? "";
    expect(read).toBe(`Read …${file.slice(-199)}`);
    expect(read).toEndWith("/measurements/CHG-001/measurement-status.md");
    expect(toolText("Bash", { command: "ls docs\npwd", description: "List" })).toBe("Bash ls docs");
  });

  test("an MCP tool call shows its server, its tool, and each argument's name with a short value", () => {
    expect(toolText("mcp__alps_harness__get_model", {})).toBe("MCP alps_harness get_model");
    expect(toolText("mcp__alps_harness__get_run", { run: "r19", wait: 50, tail: 20 })).toBe(
      'MCP alps_harness get_run run="r19", wait=50, tail=20',
    );
    expect(toolText("mcp__alps_harness__list_artifacts", { type: "Change brief" })).toBe(
      'MCP alps_harness list_artifacts type="Change brief"',
    );
    expect(
      toolText("mcp__alps_harness__instantiate", {
        process: "Requirements Clarification",
        inputs: {
          "Stakeholder information": "docs/changes/CHG-003/stakeholders.md",
          "Change brief": [],
          "Improvement proposal": [],
        },
        outputs: { "Change brief": "docs/changes/CHG-003/change-brief.md" },
        criteria: [
          { outcome: 0, statement: "The needs for CHG-003 have observable acceptance conditions." },
          { outcome: 1, statement: "Material ambiguities in CHG-003 are identified." },
        ],
      }),
    ).toBe(
      'MCP alps_harness instantiate process="Requirements Clarification", inputs={…}, outputs={…}, criteria=[2 items]',
    );
    expect(
      toolText("mcp__alps_harness__finish_run", {
        run: "r15",
        report: "## What I read\n- Process model (get_model) and operations guidance",
        status: "succeeded",
      }),
    ).toBe('MCP alps_harness finish_run run="r15", report="## What I read", status="succeeded"');
    // A long value is cut short, and so is the whole line.
    expect(
      toolText("mcp__alps_harness__evaluate", {
        instance: "i10",
        judgments: [{ outcome: 0 }, { outcome: 1 }],
        note: "Run r12 was performed by a fake agent (codex-fake), so its design is a placeholder.",
      }),
    ).toBe(
      'MCP alps_harness evaluate instance="i10", judgments=[2 items], note="Run r12 was performed by a fake agent (…"',
    );
    expect(toolText("mcp__plugin_alps_harness__run", { instance: "i1", agent: "demo" })).toBe(
      'MCP plugin_alps_harness run instance="i1", agent="demo"',
    );
  });

  test("the session's MCP servers and the rate limit are system events", () => {
    const init = parseOutputLine(
      "claude",
      JSON.stringify({
        type: "system",
        subtype: "init",
        cwd: WS,
        session_id: "fake-session",
        tools: ["Bash", "Read", "mcp__alps_harness__get_model"],
        mcp_servers: [
          { name: "alps_harness", status: "connected" },
          { name: "claude.ai Example", status: "needs-auth" },
        ],
        model: "claude-opus-4-6[1m]",
        permissionMode: "acceptEdits",
        apiKeySource: "none",
        claude_code_version: "2.1.96",
      }),
    );
    expect(init.events).toEqual([
      { kind: "system", text: "Session started (claude-opus-4-6[1m])" },
      {
        kind: "system",
        text: "MCP servers: alps_harness (connected), claude.ai Example (needs-auth)",
      },
    ]);
    // Without MCP servers, as in a run of a Process, only the start.
    expect(
      parseOutputLine(
        "claude",
        '{"type":"system","subtype":"init","mcp_servers":[],"model":"claude-opus-4-6[1m]"}',
      ).events,
    ).toEqual([{ kind: "system", text: "Session started (claude-opus-4-6[1m])" }]);
    expect(
      parseOutputLine(
        "claude",
        '{"type":"rate_limit_event","rate_limit_info":{"status":"allowed","resetsAt":1790769600,"rateLimitType":"five_hour","isUsingOverage":false},"uuid":"00000000-0000-4000-8000-000000000006","session_id":"fake-session"}',
      ),
    ).toEqual({
      events: [
        { kind: "system", text: "Rate limit (five_hour): allowed, resets at 2026-09-30T12:00:00Z" },
      ],
    });
  });

  test("the result tells how the session ended by its own account, and turns are recorded as the agent counts them", () => {
    expect(parseOutputLine("claude", JSON.stringify(RESULT))).toEqual({
      events: [
        { kind: "result", text: "The agent reported the end of its work" },
        {
          kind: "system",
          text: "The agent ended (completed) after 321 s and 23 turns (tool round trips + 1)",
        },
      ],
      // 23 turns: the wake r16 called its tools 22 times, in 12 requests to the model (--max-turns 12).
      usage: {
        costUsd: 0.7426932500000001,
        turns: 23,
        inputTokens: 464318,
        cachedInputTokens: 420239,
        outputTokens: 10284,
      },
      report: "## What I did",
    });
    // Not logged in (the recorded failure): the session ended as completed, and the failure is
    // told by the result's text.
    const failed = fs
      .readFileSync(new URL("../fixtures/agents/claude-fail.jsonl", import.meta.url), "utf8")
      .trim()
      .split("\n")
      .at(-1);
    expect(parseOutputLine("claude", failed ?? "")).toMatchObject({
      events: [
        {
          kind: "result",
          text: "The agent reported a failure (Not logged in · Please run /login)",
        },
        {
          kind: "system",
          text: "The agent ended (completed) after 46 ms and 1 turn (tool round trips + 1)",
        },
      ],
      agentError: "Not logged in · Please run /login",
    });
    // Denied tool uses, in the shape of Claude Code's permission_denials (none were recorded):
    // their number and the first tool are in the event and in the failure.
    const denied = parseOutputLine(
      "claude",
      JSON.stringify({
        ...RESULT,
        subtype: "error_max_turns",
        is_error: true,
        num_turns: 13,
        terminal_reason: "max_turns",
        permission_denials: [
          { tool_name: "Bash", tool_use_id: "toolu_fake_02", tool_input: { command: "make" } },
          { tool_name: "Write", tool_use_id: "toolu_fake_03", tool_input: { file_path: "x.md" } },
        ],
      }),
    );
    expect(denied.events).toEqual([
      { kind: "result", text: "The agent reported a failure (error_max_turns)" },
      {
        kind: "system",
        text: "The agent ended (max_turns) after 321 s and 13 turns (tool round trips + 1); 2 tool uses denied, the first Bash",
      },
    ]);
    expect(denied.agentError).toBe("error_max_turns; 2 tool uses denied, the first Bash");
    expect(
      parseOutputLine(
        "claude",
        JSON.stringify({
          ...RESULT,
          is_error: true,
          terminal_reason: "aborted",
          result: "Stopped",
        }),
      ).agentError,
    ).toBe("Stopped (aborted)");
  });
});
