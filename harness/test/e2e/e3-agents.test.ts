/*
 * E3 (current state, MCP): running a fake claude-code reads its stream-json as the harness's
 * events and records the usage and the report; cancel_run stops its whole process group (stage 3).
 *
 * What the fake agent does (test/fakes/claude.ts, written in stage 3): it answers --version,
 * prints the stream-json lines of test/fixtures/agents/ for ALPS_FAKE_SCENARIO (ok, fail, slow,
 * hang), and writes the output paths that the prompt names. With `hang` it starts a child
 * process, writes its own pid and the child's to the file ALPS_FAKE_PIDS names (one per line),
 * and waits to be killed.
 */

import { afterAll, describe, expect, test } from "bun:test";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import type {
  CancelResponse,
  InstanceResponse,
  ModelResponse,
  RunDetailResponse,
  RunStartResponse,
} from "../../src/shared/types.ts";
import { copyOf } from "../helpers/copy.ts";
import { killStrayDaemons, stopWorkspaceDaemon } from "../helpers/daemon.ts";
import { callTool, mcpClient, type McpSession } from "../helpers/mcp.ts";
import { FAKES, records } from "../helpers/paths.ts";
import { isAlive, waitFor } from "../helpers/process.ts";
import { tmpWorkspace, type TmpWorkspace } from "../helpers/workspace.ts";

const workspaces: TmpWorkspace[] = [];
const sessions: McpSession[] = [];
const dirs: string[] = [];

afterAll(async () => {
  for (const session of sessions) await session.close().catch(() => {});
  for (const ws of workspaces) await stopWorkspaceDaemon(ws.root).catch(() => {});
  killStrayDaemons();
  for (const ws of workspaces) ws.dispose();
  for (const dir of dirs) fs.rmSync(dir, { recursive: true, force: true });
});

/** A workspace whose claude-code is the fake, with the given scenario settings. */
async function withFakeClaude(
  env: Record<string, string>,
): Promise<{ ws: TmpWorkspace; mcp: McpSession }> {
  const ws = tmpWorkspace({
    agents: { "claude-code": { command: path.join(FAKES, "claude.ts"), env } },
  });
  workspaces.push(ws);
  const mcp = await mcpClient({ workspace: ws.root });
  sessions.push(mcp);
  return { ws, mcp };
}

async function startDesign(mcp: McpSession): Promise<RunStartResponse> {
  const { instance } = await callTool<InstanceResponse>(mcp, "instantiate", {
    process: "Solution Design",
    inputs: { "Change brief": ["docs/changes/CHG-001/change-brief.md"] },
    outputs: { "Design description": "docs/changes/CHG-001/design/" },
  });
  return callTool<RunStartResponse>(mcp, "run", { instance: instance.id, agent: "claude-code" });
}

describe("E3 agents", () => {
  test.todo(
    "E3 a fake claude-code's stream-json is read as events, and its usage and report are recorded",
    async () => {
      const { ws, mcp } = await withFakeClaude({ ALPS_FAKE_SCENARIO: "ok" });
      const { model } = await callTool<ModelResponse>(mcp, "get_model");
      expect(copyOf(model.agents.find((agent) => agent.id === "claude-code"))).toMatchObject({
        available: true,
        version: expect.any(String),
      });

      const { run } = await startDesign(mcp);
      const detail = await callTool<RunDetailResponse>(mcp, "get_run", {
        run: run.id,
        wait: 60,
        tail: 500,
      });
      expect(copyOf(detail.run)).toMatchObject({
        status: "succeeded",
        exitCode: 0,
        agentError: null,
        // The command line is recorded without the prompt.
        command: expect.stringContaining("<prompt>"),
      });
      expect(detail.run.command).toContain("--output-format stream-json");
      // The usage and the report come from the result line.
      expect(detail.run.usage).toEqual({
        costUsd: expect.any(Number),
        turns: expect.any(Number),
        inputTokens: expect.any(Number),
        outputTokens: expect.any(Number),
      });
      expect(detail.run.report.trim()).not.toBe("");
      // The stream is read as the common events; the raw output is kept as it came.
      const kinds = new Set(detail.events.map((event) => event.kind));
      for (const kind of ["system", "message", "tool", "result", "end"] as const)
        expect(kinds.has(kind), kind).toBe(true);
      expect(fs.readFileSync(records(ws.root, "runs", `${run.id}.raw.log`), "utf8")).toContain(
        '"type":"result"',
      );
      // What the fake wrote at the output location is the run's output.
      expect(detail.run.outputs.map((output) => output.type)).toContain("Design description");
    },
    { timeout: 90_000 },
  );

  test.todo(
    "E3 cancel_run stops the agent's whole process group",
    async () => {
      const dir = fs.mkdtempSync(path.join(os.tmpdir(), "alps-harness-e3-"));
      dirs.push(dir);
      const pidFile = path.join(dir, "pids");
      const { mcp } = await withFakeClaude({ ALPS_FAKE_SCENARIO: "hang", ALPS_FAKE_PIDS: pidFile });
      const { run } = await startDesign(mcp);
      const pids = (): number[] =>
        fs.existsSync(pidFile)
          ? fs.readFileSync(pidFile, "utf8").trim().split("\n").map(Number)
          : [];
      await waitFor(() => pids().length === 2, 20_000, "the fake agent to start its child");
      const [agent = 0, child = 0] = pids();
      expect(isAlive(agent) && isAlive(child)).toBe(true);

      const canceled = await callTool<CancelResponse>(mcp, "cancel_run", { run: run.id });
      expect(canceled.canceled).toBe(true);
      const detail = await callTool<RunDetailResponse>(mcp, "get_run", { run: run.id, wait: 30 });
      expect(detail.run.status).toBe("canceled");
      // The child of the agent stops with it: the harness signals the process group.
      await waitFor(
        () => !isAlive(agent) && !isAlive(child),
        10_000,
        "the agent's process group to stop",
      );
    },
    { timeout: 90_000 },
  );
});
