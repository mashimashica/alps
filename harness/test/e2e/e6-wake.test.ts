/*
 * E6 (scheduled runs): wake starts a fake agent with this workspace's harness MCP server; when the
 * agent calls instantiate and run, the runs are listed in the wake record's started[]. A second
 * wake while the first still runs is skipped, and the skip is recorded. alps-harness wake starts
 * the same wake for an external scheduler, and configured schedules keep the daemon from stopping
 * when idle. The cron expressions themselves are read by test/unit/cron.test.ts.
 *
 * What the fake wake agent does (test/fakes/wake-agent.ts): it is started as claude-code or codex
 * is, with the MCP configuration the harness gives it (--mcp-config, or -c mcp_servers.…); it
 * connects with @modelcontextprotocol/client, calls instantiate and run(demo), waits with get_run,
 * and ends with finish_run. With ALPS_FAKE_SCENARIO=slow it waits 30 s before it starts.
 */

import { afterAll, describe, expect, test } from "bun:test";
import fs from "node:fs";
import path from "node:path";
import type {
  AssessmentResponse,
  InstancesResponse,
  RunDetailResponse,
  StateFile,
  WakeResponse,
} from "../../src/shared/types.ts";
import { copyOf } from "../helpers/copy.ts";
import { killStrayDaemons, startDaemon, stopWorkspaceDaemon } from "../helpers/daemon.ts";
import { callTool, mcpClient, type McpSession } from "../helpers/mcp.ts";
import { FAKES, records } from "../helpers/paths.ts";
import { cli, isAlive } from "../helpers/process.ts";
import { tmpWorkspace, type TmpWorkspace, type WorkspaceOverrides } from "../helpers/workspace.ts";

const workspaces: TmpWorkspace[] = [];
const sessions: McpSession[] = [];

afterAll(async () => {
  for (const session of sessions) await session.close().catch(() => {});
  for (const ws of workspaces) await stopWorkspaceDaemon(ws.root).catch(() => {});
  killStrayDaemons();
  for (const ws of workspaces) ws.dispose();
});

const WAKE_AGENT = path.join(FAKES, "wake-agent.ts");

function wakeWorkspace(
  agent: "claude-code" | "codex",
  scenario: string,
  overrides: WorkspaceOverrides = {},
): TmpWorkspace {
  const ws = tmpWorkspace({
    ...overrides,
    agents: { [agent]: { command: WAKE_AGENT, env: { ALPS_FAKE_SCENARIO: scenario } } },
  });
  workspaces.push(ws);
  return ws;
}

async function withWakeAgent(scenario: string): Promise<{ ws: TmpWorkspace; mcp: McpSession }> {
  const ws = wakeWorkspace("claude-code", scenario);
  const mcp = await mcpClient({ workspace: ws.root });
  sessions.push(mcp);
  return { ws, mcp };
}

const readState = (ws: TmpWorkspace): StateFile =>
  JSON.parse(fs.readFileSync(records(ws.root, "state.json"), "utf8")) as StateFile;

describe("E6 wake", () => {
  test(
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
      // Claude Code is given the harness's MCP server in a file and allowed its tools only.
      const id = woke.run?.id ?? "";
      expect(woke.run?.command).toContain(
        `--mcp-config ${records(ws.root, "runs", `${id}.mcp.json`)}`,
      );
      expect(woke.run?.command).toContain("--allowedTools mcp__alps_harness");
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
      const state = readState(ws);
      expect(state.lastWakeAt).toBeGreaterThanOrEqual(wake.run.startedAt);

      // The prompt points to the model and the guidance instead of copying them, gives the
      // state, and names the run to report with finish_run.
      expect(wake.run.prompt).toContain("The process model is process-model.yaml.");
      expect(wake.run.prompt).toContain("- docs/operations.md\n");
      expect(wake.run.prompt).not.toContain("# Operations");
      expect(wake.run.prompt).toContain("This is the first wake.");
      expect(wake.run.prompt).toContain(`call finish_run for run ${id}`);
      // The report is the one given with finish_run; the usage comes from the agent's last line,
      // after it, since the run ends when the agent's process does. The temporary file is gone.
      expect(wake.run.report).toBe(
        "Read the model and the guidance; started one run with the demo agent.",
      );
      expect(wake.run.usage?.costUsd).toBe(0.0123);
      expect(fs.existsSync(records(ws.root, "runs", `${id}.mcp.json`))).toBe(false);
      // A wake run is no instance and no process run: the instances and the statistics leave it out.
      const listed = await callTool<InstancesResponse>(mcp, "list_instances", {});
      expect(listed.instances.map((instance) => instance.runs)).toEqual([[startedId ?? ""]]);
      const { assessment } = await callTool<AssessmentResponse>(mcp, "get_assessment", {});
      expect(assessment.stats.metrics.runSuccess).toMatchObject({ numerator: 1, denominator: 1 });
    },
    { timeout: 120_000 },
  );

  test(
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
      const state = readState(ws);
      expect(Object.values(state.runs).filter((run) => run.kind === "wake")).toHaveLength(1);
      await callTool(mcp, "cancel_run", { run: first.run?.id });
    },
    { timeout: 120_000 },
  );

  test(
    "E6 alps-harness wake starts the same wake for an external scheduler (launchd, cron, CI)",
    async () => {
      // Codex is woken here: it takes the harness's MCP server as -c overrides.
      const ws = wakeWorkspace("codex", "ok");
      const woke = await cli(["wake", ws.root, "--agent", "codex"]);
      expect(woke.code, woke.stderr).toBe(0);
      const id = /^Woke codex\s+wake run (r\d+)$/m.exec(woke.stdout)?.[1];
      expect(id, woke.stdout).toBeDefined();
      // The command line started the daemon, as the MCP server does; an MCP client follows the run.
      const mcp = await mcpClient({ workspace: ws.root });
      sessions.push(mcp);
      const wake = await callTool<RunDetailResponse>(mcp, "get_run", { run: id, wait: 60 });
      expect(copyOf(wake.run)).toMatchObject({ kind: "wake", agent: "codex", status: "succeeded" });
      expect(wake.run.started).toHaveLength(1);
      // The command line is recorded with each -c value quoted as JSON.
      expect(wake.run.command).toContain("mcp_servers.alps_harness.args=");
      expect(wake.run.command).toContain(
        String.raw`mcp_servers.alps_harness.default_tools_approval_mode=\"approve\"`,
      );
      expect(wake.run.usage?.inputTokens).toBe(1200);
      expect(wake.events.some((event) => event.text === "Woken on request.")).toBe(true);
      // An agent that the harness cannot give its MCP server is refused, and nothing is recorded.
      const demo = await cli(["wake", ws.root, "--agent", "demo"]);
      expect(demo.code).toBe(1);
      expect(demo.stderr).toContain("Demo cannot be woken");
      expect(Object.values(readState(ws).runs).filter((run) => run.kind === "wake")).toHaveLength(
        1,
      );
    },
    { timeout: 120_000 },
  );

  test(
    "E6 while schedules are configured, the daemon does not exit when idle",
    async () => {
      // Once a year, so that no wake starts during the test; without it the daemon stops after 3 s.
      const ws = wakeWorkspace("claude-code", "ok", {
        server: { idleMinutes: 0.05 },
        config: { schedules: [{ cron: "0 0 1 1 *", agent: "claude-code" }] },
      });
      const daemon = await startDaemon(ws.root);
      await Bun.sleep(6000);
      expect(isAlive(daemon.info.pid)).toBe(true);
      const state = fs.existsSync(records(ws.root, "state.json")) ? readState(ws) : null;
      expect(Object.keys(state?.runs ?? {})).toEqual([]);
      await daemon.stop();
    },
    { timeout: 60_000 },
  );
});
