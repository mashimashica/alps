/*
 * Reading an agent's output (Agents): a line of a shape the harness cannot read is kept as
 * output, and a line the harness fails on does not stop the reading, so the rest of the output
 * (the report and the usage come last) still reaches the run.
 */

import { describe, expect, test } from "bun:test";
import { parseOutputLine } from "../../src/agents/index.ts";
import { startAgent } from "../../src/server/agent-process.ts";

describe("agent output", () => {
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
