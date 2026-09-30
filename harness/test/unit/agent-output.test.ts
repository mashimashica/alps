/*
 * Reading an agent's output (Agents): a line of a shape the harness cannot read is kept as
 * output, and a line the harness fails on does not stop the reading, so the rest of the output
 * (the report and the usage come last) still reaches the run. A Codex failure, as recorded from
 * the real agent (test/fixtures/agents/codex-fail.jsonl), is read as what went wrong.
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
