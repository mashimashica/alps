/*
 * E3 (current state, MCP): running a fake claude-code reads its stream-json as the harness's
 * events and records the usage and the report; cancel_run stops its whole process group. The fake
 * codex is read the same way from its JSON Lines.
 *
 * What the fake agents do (test/fakes/agent.ts): they answer --version, print the lines of
 * test/fixtures/agents/ for ALPS_FAKE_SCENARIO (ok, fail, slow, hang), and write the output paths
 * that the prompt names. With `hang` the agent starts a child process, writes its own pid and the
 * child's to the file ALPS_FAKE_PIDS names (one per line), ignores SIGTERM, and waits to be killed.
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
import { HOOK_TIMEOUT_MS, isAlive, waitFor } from "../helpers/process.ts";
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
}, HOOK_TIMEOUT_MS);

const tmpDir = (): string => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "alps-harness-e3-"));
  dirs.push(dir);
  return dir;
};

/** A workspace whose agent (claude-code or codex) is the fake, with the given settings. */
async function withFake(
  agent: "claude-code" | "codex",
  config: { env?: Record<string, string>; stdin?: boolean },
): Promise<{ ws: TmpWorkspace; mcp: McpSession }> {
  const ws = tmpWorkspace({
    agents: {
      [agent]: {
        command: path.join(FAKES, agent === "codex" ? "codex.ts" : "claude.ts"),
        ...config,
      },
    },
  });
  workspaces.push(ws);
  const mcp = await mcpClient({ workspace: ws.root });
  sessions.push(mcp);
  return { ws, mcp };
}

async function startDesign(
  mcp: McpSession,
  agent: "claude-code" | "codex" = "claude-code",
): Promise<RunStartResponse> {
  const { instance } = await callTool<InstanceResponse>(mcp, "instantiate", {
    process: "Solution Design",
    inputs: { "Change brief": ["docs/changes/CHG-001/change-brief.md"] },
    outputs: { "Design description": "docs/changes/CHG-001/design/" },
  });
  return callTool<RunStartResponse>(mcp, "run", { instance: instance.id, agent });
}

describe("E3 agents", () => {
  test(
    "E3 a fake claude-code's stream-json is read as events, and its usage and report are recorded",
    async () => {
      const { ws, mcp } = await withFake("claude-code", { env: { ALPS_FAKE_SCENARIO: "ok" } });
      const { model } = await callTool<ModelResponse>(mcp, "get_model");
      expect(copyOf(model.agents.find((agent) => agent.id === "claude-code"))).toMatchObject({
        available: true,
        version: "2.1.999 (Claude Code)",
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
        error: null,
        agentError: null,
        // The command line is recorded without the prompt.
        command: expect.stringContaining("<prompt>"),
      });
      expect(detail.run.command).toContain("--output-format stream-json");
      expect(detail.run.command).not.toContain("Solution Design");
      // The usage and the report come from the result line.
      expect(detail.run.usage).toEqual({
        costUsd: 0.0421,
        turns: 4,
        inputTokens: 6120,
        outputTokens: 418,
      });
      expect(detail.run.report).toStartWith("Outcome 0:");
      // The stream is read as the common events; the raw output is kept as it came.
      const kinds = new Set(detail.events.map((event) => event.kind));
      for (const kind of ["system", "message", "thinking", "tool", "result", "end"] as const)
        expect(kinds.has(kind), kind).toBe(true);
      expect(detail.events.map((event) => event.text)).toContain(
        "Read skills/design-solution/SKILL.md",
      );
      const raw = fs.readFileSync(records(ws.root, "runs", `${run.id}.raw.log`), "utf8");
      expect(raw).toContain('"type":"result"');
      expect(raw.trim().split("\n")).toHaveLength(9);
      const events = fs
        .readFileSync(records(ws.root, "runs", `${run.id}.jsonl`), "utf8")
        .trim()
        .split("\n");
      expect(events).toHaveLength(detail.run.events);
      // What the fake wrote at the output location is the run's output, and provenance names it.
      expect(detail.run.outputs).toEqual([
        { type: "Design description", path: "docs/changes/CHG-001/design", change: "modified" },
      ]);
      expect(
        fs.readFileSync(path.join(ws.root, "docs/changes/CHG-001/design/fake-agent.md"), "utf8"),
      ).toContain(`run ${run.id}`);
    },
    { timeout: 90_000 },
  );

  test(
    "E3 a fake codex's JSON Lines are read as events, with the usage it reports and its last message as the report",
    async () => {
      const { mcp } = await withFake("codex", {});
      const { run } = await startDesign(mcp, "codex");
      const detail = await callTool<RunDetailResponse>(mcp, "get_run", {
        run: run.id,
        wait: 60,
        tail: 500,
      });
      expect(copyOf(detail.run)).toMatchObject({ status: "succeeded", exitCode: 0 });
      expect(detail.run.command).toMatch(/codex\.ts exec --json .*<prompt>$/);
      // Codex reports tokens but no cost.
      expect(detail.run.usage).toEqual({
        costUsd: null,
        turns: null,
        inputTokens: 24763,
        outputTokens: 122,
      });
      expect(detail.run.report).toStartWith("Outcome 0:");
      const texts = detail.events.map((event) => event.text);
      expect(texts).toContain("Thread started");
      expect(texts).toContain("$ bash -lc 'cat skills/design-solution/SKILL.md'");
      expect(texts).toContain("Changed docs/changes/CHG-001/design/fake-agent.md");
      expect(detail.run.outputs.map((output) => output.type)).toEqual(["Design description"]);
    },
    { timeout: 90_000 },
  );

  test(
    "E3 an agent that reports a failure fails the run, and the failure it reported is kept",
    async () => {
      const { mcp } = await withFake("claude-code", { env: { ALPS_FAKE_SCENARIO: "fail" } });
      const { run } = await startDesign(mcp);
      const detail = await callTool<RunDetailResponse>(mcp, "get_run", { run: run.id, wait: 60 });
      expect(copyOf(detail.run)).toMatchObject({
        status: "failed",
        exitCode: 1,
        agentError: "error_during_execution",
        usage: { costUsd: 0.0102, turns: 2 },
      });
      const kinds = detail.events.map((event) => event.kind);
      expect(kinds).toContain("error");
      expect(detail.events.map((event) => event.text)).toContain(
        "The agent reported a failure (error_during_execution)",
      );
    },
    { timeout: 90_000 },
  );

  test(
    "E3 with stdin the prompt reaches the agent on its standard input, as on Windows, and stays off the command line",
    async () => {
      const promptFile = path.join(tmpDir(), "prompt.txt");
      const { mcp } = await withFake("claude-code", {
        stdin: true,
        env: { ALPS_FAKE_PROMPT: promptFile },
      });
      const { run } = await startDesign(mcp);
      const detail = await callTool<RunDetailResponse>(mcp, "get_run", { run: run.id, wait: 60 });
      expect(detail.run.status).toBe("succeeded");
      expect(detail.run.command).not.toContain("<prompt>");
      expect(detail.run.command).toMatch(/claude\.ts -p --output-format/);
      expect(fs.readFileSync(promptFile, "utf8")).toContain('Process "Solution Design"');
    },
    { timeout: 90_000 },
  );

  test(
    "E3 cancel_run stops the agent's whole process group",
    async () => {
      const pidFile = path.join(tmpDir(), "pids");
      const { mcp } = await withFake("claude-code", {
        env: { ALPS_FAKE_SCENARIO: "hang", ALPS_FAKE_PIDS: pidFile },
      });
      const { run } = await startDesign(mcp);
      const pids = (): number[] =>
        fs.existsSync(pidFile)
          ? fs.readFileSync(pidFile, "utf8").trim().split("\n").map(Number)
          : [];
      await waitFor(() => pids().length === 2, 20_000, "the fake agent to start its child");
      const [agent = 0, child = 0] = pids();
      expect(isAlive(agent) && isAlive(child)).toBe(true);
      // The agent leads a process group of its own, and its child is in it.
      const group = (pid: number): number =>
        Number(
          Bun.spawnSync(["ps", "-o", "pgid=", "-p", String(pid)])
            .stdout.toString()
            .trim(),
        );
      expect(group(agent)).toBe(agent);
      expect(group(child)).toBe(agent);

      // The agent ignores SIGTERM: the child ends with the group's SIGTERM, the agent with the
      // SIGKILL that follows 5 s later, and cancel_run answers once the run has ended.
      const started = Date.now();
      const canceled = await callTool<CancelResponse>(mcp, "cancel_run", { run: run.id });
      expect(canceled.canceled).toBe(true);
      expect(canceled.run.status).toBe("canceled");
      expect(Date.now() - started).toBeGreaterThanOrEqual(4_500);
      expect(isAlive(agent)).toBe(false);
      await waitFor(() => !isAlive(child), 5_000, "the agent's child to stop");
      const detail = await callTool<RunDetailResponse>(mcp, "get_run", { run: run.id });
      expect(copyOf(detail.run)).toMatchObject({ status: "canceled", error: null });
      expect(detail.events.at(-1)).toMatchObject({ kind: "end" });
      // Canceling again changes nothing.
      const again = await callTool<CancelResponse>(mcp, "cancel_run", { run: run.id });
      expect(again.canceled).toBe(false);
    },
    { timeout: 90_000 },
  );

  test(
    "E3 a run still running when the harness server stops is interrupted, and its agent's process group is stopped",
    async () => {
      const pidFile = path.join(tmpDir(), "pids");
      const { ws, mcp } = await withFake("claude-code", {
        env: { ALPS_FAKE_SCENARIO: "hang", ALPS_FAKE_PIDS: pidFile },
      });
      const { run } = await startDesign(mcp);
      await waitFor(() => fs.existsSync(pidFile), 20_000, "the fake agent to start its child");
      const [agent = 0, child = 0] = fs
        .readFileSync(pidFile, "utf8")
        .trim()
        .split("\n")
        .map(Number);

      // `alps-harness stop` returns once the daemon has ended, its agents first.
      await stopWorkspaceDaemon(ws.root);
      expect(isAlive(agent)).toBe(false);
      await waitFor(() => !isAlive(child), 5_000, "the agent's child to stop");
      const record = JSON.parse(
        fs.readFileSync(records(ws.root, "runs", `${run.id}.json`), "utf8"),
      ) as { status: string; error: string | null };
      expect(record).toMatchObject({
        status: "interrupted",
        error: "The harness server stopped while the run was running.",
      });
    },
    { timeout: 90_000 },
  );
});
