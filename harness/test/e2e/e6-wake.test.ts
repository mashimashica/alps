/*
 * E6 (scheduled runs): wake starts a fake agent with this workspace's harness MCP server; when the
 * agent calls instantiate and run, the runs are listed in the wake record's started[]. A second
 * wake while the first still runs is skipped, and the skip is recorded (stage 5).
 *
 * What the fake wake agent does (test/fakes/wake-agent.ts, written in stage 5): it is started as
 * claude-code is, with the MCP configuration the harness gives it; it connects with
 * @modelcontextprotocol/client, calls instantiate and run(demo), waits with get_run, and ends
 * with finish_run. With ALPS_FAKE_SCENARIO=slow it waits 30 s before finishing.
 */

import { afterAll, describe, expect, test } from "bun:test";
import fs from "node:fs";
import path from "node:path";
import type { RunDetailResponse, RunView, StateFile } from "../../src/shared/types.ts";
import { copyOf } from "../helpers/copy.ts";
import { killStrayDaemons, stopWorkspaceDaemon } from "../helpers/daemon.ts";
import { callTool, mcpClient, type McpSession } from "../helpers/mcp.ts";
import { FAKES, records } from "../helpers/paths.ts";
import { tmpWorkspace, type TmpWorkspace } from "../helpers/workspace.ts";

const workspaces: TmpWorkspace[] = [];
const sessions: McpSession[] = [];

afterAll(async () => {
  for (const session of sessions) await session.close().catch(() => {});
  for (const ws of workspaces) await stopWorkspaceDaemon(ws.root).catch(() => {});
  killStrayDaemons();
  for (const ws of workspaces) ws.dispose();
});

interface WakeResponse {
  ok: true;
  run?: RunView;
  /** The wake was not started because an earlier one still runs. */
  skipped?: boolean;
  running?: string;
}

async function withWakeAgent(scenario: string): Promise<{ ws: TmpWorkspace; mcp: McpSession }> {
  const ws = tmpWorkspace({
    agents: {
      "claude-code": {
        command: path.join(FAKES, "wake-agent.ts"),
        env: { ALPS_FAKE_SCENARIO: scenario },
      },
    },
  });
  workspaces.push(ws);
  const mcp = await mcpClient({ workspace: ws.root });
  sessions.push(mcp);
  return { ws, mcp };
}

describe("E6 wake", () => {
  test.todo(
    "E6 wake starts the agent with MCP, and the runs it starts are listed in started[]",
    async () => {
      const { ws, mcp } = await withWakeAgent("ok");
      const woke = await callTool<WakeResponse>(mcp, "wake", { agent: "claude-code" });
      expect(copyOf(woke.run)).toMatchObject({
        kind: "wake",
        instance: null,
        process: null,
        status: "running",
      });
      const wake = await callTool<RunDetailResponse>(mcp, "get_run", {
        run: woke.run?.id,
        wait: 60,
      });
      expect(wake.run.status).toBe("succeeded");
      expect(wake.run.started).toHaveLength(1);

      const [startedId] = wake.run.started ?? [];
      const started = await callTool<RunDetailResponse>(mcp, "get_run", {
        run: startedId,
        wait: 30,
      });
      expect(copyOf(started.run)).toMatchObject({
        kind: "process",
        agent: "demo",
        status: "succeeded",
      });
      const state = JSON.parse(
        fs.readFileSync(records(ws.root, "state.json"), "utf8"),
      ) as StateFile;
      expect(state.lastWakeAt).toBeGreaterThanOrEqual(wake.run.startedAt);
    },
    { timeout: 120_000 },
  );

  test.todo(
    "E6 a wake while the previous wake still runs is skipped, and the skip is recorded",
    async () => {
      const { ws, mcp } = await withWakeAgent("slow");
      const first = await callTool<WakeResponse>(mcp, "wake", { agent: "claude-code" });
      expect(first.run?.status).toBe("running");
      const second = await callTool<WakeResponse>(mcp, "wake", { agent: "claude-code" });
      expect(copyOf(second)).toMatchObject({ skipped: true, running: first.run?.id });
      expect(second.run).toBeUndefined();
      // The skip is recorded without a run of its own: the running wake's events say that a
      // wake was skipped, and the records hold one wake run only.
      const wake = await callTool<RunDetailResponse>(mcp, "get_run", {
        run: first.run?.id,
        tail: 1000,
      });
      expect(
        wake.events.some((event) => event.kind === "system" && /skipped/i.test(event.text)),
      ).toBe(true);
      const state = JSON.parse(
        fs.readFileSync(records(ws.root, "state.json"), "utf8"),
      ) as StateFile;
      expect(Object.values(state.runs).filter((run) => run.kind === "wake")).toHaveLength(1);
      await callTool(mcp, "cancel_run", { run: first.run?.id });
    },
    { timeout: 120_000 },
  );
});
