/*
 * The schedules of alps-harness.yaml (Scheduled runs): a schedule names an agent that can be woken,
 * one of the claude or codex format. One that names another is an error of the configuration, as an
 * unreadable cron expression is: the harness answers no-model with what is wrong and the file,
 * instead of failing to wake the agent at the scheduled time. The cron expressions themselves are
 * read by cron.test.ts.
 */

import { afterAll, describe, expect, test } from "bun:test";
import path from "node:path";
import { loadWorkspace, ModelError } from "../../src/model/index.ts";
import { tmpWorkspace, type TmpWorkspace } from "../helpers/workspace.ts";

const workspaces: TmpWorkspace[] = [];

afterAll(() => {
  for (const ws of workspaces) ws.dispose();
});

/** Loads the example workspace with these schedules and agents: the ModelError it throws, or `null`. */
function load(
  schedules: { cron: string; agent: string }[],
  agents: Record<string, unknown> = {},
): { error: ModelError | null; config: string } {
  const ws = tmpWorkspace({ agents, config: { schedules } });
  workspaces.push(ws);
  const config = path.join(ws.root, "alps-harness.yaml");
  try {
    loadWorkspace(ws.root, { parseYaml: Bun.YAML.parse });
    return { error: null, config };
  } catch (error) {
    if (error instanceof ModelError) return { error, config };
    throw error;
  }
}

describe("schedules", () => {
  test("a schedule whose agent cannot be woken makes the configuration no-model, as an unreadable cron expression does", () => {
    const daily = "0 9 * * 1-5";
    const woken = load(
      [
        { cron: daily, agent: "claude-code" },
        { cron: daily, agent: "codex" },
        { cron: daily, agent: "reviewer" },
      ],
      { reviewer: { command: "reviewer", format: "claude" } },
    );
    expect(woken.error).toBeNull();

    const wrong = load([
      { cron: daily, agent: "claud-code" },
      { cron: daily, agent: "demo" },
    ]);
    expect(wrong.error?.code).toBe("no-model");
    expect(wrong.error?.files).toEqual([wrong.config]);
    expect(wrong.error?.message.split("\n")).toEqual([
      'alps-harness.yaml: schedules.0.agent: "claud-code" is not an agent of this workspace; the agents that can be woken: claude-code, codex',
      `alps-harness.yaml: schedules.1.agent: "demo" cannot be woken: a wake gives its agent the harness's MCP server, which only agents of the claude and codex formats take; the agents that can be woken: claude-code, codex`,
    ]);

    // An unreadable cron expression is refused the same way.
    const cron = load([{ cron: "0 9 * *", agent: "claude-code" }]);
    expect(cron.error?.code).toBe("no-model");
    expect(cron.error?.files).toEqual([cron.config]);
    expect(cron.error?.message).toMatch(/^alps-harness\.yaml: schedules\.0\.cron: /);
  });
});
