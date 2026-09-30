/*
 * E3 (current state, MCP): running a fake claude-code reads its stream-json as the harness's
 * events and records the usage and the report; cancel_run stops its whole process group. The fake
 * codex is read the same way from its JSON Lines. A Claude Code agent is started without the
 * variables that mark a Claude Code session.
 *
 * What the fake agents do (test/fakes/agent.ts): they answer --version, print the lines of
 * test/fixtures/agents/ for ALPS_FAKE_SCENARIO (ok, fail, slow, hang), and write the output paths
 * that the prompt names. With `hang` the agent starts a child process, writes its own pid and the
 * child's to the file ALPS_FAKE_PIDS names (one per line), ignores SIGTERM, and waits to be killed.
 * With ALPS_FAKE_ENV_DUMP each start, --version included, adds the names of its environment's
 * variables to that file.
 */

import { afterAll, describe, expect, test } from "bun:test";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import type {
  ArtifactsResponse,
  AssessmentResponse,
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

/** A line that a fake agent adds to the file ALPS_FAKE_ENV_DUMP names, each time it starts. */
interface EnvDump {
  start: "version" | "run";
  names: string[];
  values: Record<string, string>;
}

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
      // The usage and the report come from the result line of the recorded run (Claude Code
      // 2.1.96, stage 7b). The input tokens are all of them (8 uncached, 20190 written to the
      // prompt cache, 91966 read from it), as Codex counts; the turns are Claude Code's (its 6
      // tool round trips + 1).
      expect(detail.run.usage).toEqual({
        costUsd: 0.2300105,
        turns: 7,
        inputTokens: 112164,
        cachedInputTokens: 91966,
        outputTokens: 2312,
      });
      expect(detail.run.report).toStartWith("Outcome 0:");
      // The stream is read as the common events; the raw output is kept as it came.
      const kinds = new Set(detail.events.map((event) => event.kind));
      for (const kind of ["system", "message", "thinking", "tool", "result", "end"] as const)
        expect(kinds.has(kind), kind).toBe(true);
      const texts = detail.events.map((event) => event.text);
      // Claude Code gives its tools absolute paths.
      expect(
        texts.some(
          (text) => text.startsWith("Read /") && text.endsWith("/skills/design-solution/SKILL.md"),
        ),
      ).toBe(true);
      expect(texts.some((text) => text.startsWith("Glob **/*.md in /"))).toBe(true);
      expect(texts).toContain("Session started (claude-opus-4-6[1m])");
      expect(texts).toContain("Rate limit (five_hour): allowed, resets at 2026-09-30T12:00:00Z");
      expect(texts).toContain(
        "The agent ended (completed) after 53 s and 7 turns (tool round trips + 1)",
      );
      const raw = fs.readFileSync(records(ws.root, "runs", `${run.id}.raw.log`), "utf8");
      expect(raw).toContain('"type":"result"');
      expect(raw.trim().split("\n")).toHaveLength(22);
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
    "E3 two runs at the same time in the same locations: what one of them writes is not the other's output",
    async () => {
      // 22 lines 800 ms apart: each run writes (before its line 19) 3 s before it ends, so the
      // second, started right after the first and lagging up to a second behind it, writes while
      // the first still runs.
      const { ws, mcp } = await withFake("claude-code", {
        env: { ALPS_FAKE_SCENARIO: "slow", ALPS_FAKE_DELAY_MS: "800" },
      });
      // Stage 7b: a run of Feasibility Assessment took as its output the change brief that a run
      // of Requirements Clarification at the same time had created. Here one run has a concrete
      // location, and the other leaves its location to the agent (the fake fills the pattern's
      // wildcard: docs/changes/fake/change-brief.md).
      const own = "docs/changes/CHG-002/change-brief.md";
      const decided = "docs/changes/fake/change-brief.md";
      const { instance: clarify } = await callTool<InstanceResponse>(mcp, "instantiate", {
        process: "Requirements Clarification",
        inputs: { "Stakeholder information": ["docs/changes/CHG-002/stakeholders.md"] },
        outputs: { "Change brief": own },
      });
      const { instance: assess } = await callTool<InstanceResponse>(mcp, "instantiate", {
        process: "Feasibility Assessment",
        inputs: {
          "Change brief": ["docs/changes/CHG-001/change-brief.md"],
          "Production observations": ["observations/2026-09-27.md"],
        },
      });
      expect(assess.outputs).toEqual({ "Change brief": null });
      const first = await callTool<RunStartResponse>(mcp, "run", {
        instance: clarify.id,
        agent: "claude-code",
      });
      const second = await callTool<RunStartResponse>(mcp, "run", {
        instance: assess.id,
        agent: "claude-code",
      });
      const a = await callTool<RunDetailResponse>(mcp, "get_run", { run: first.run.id, wait: 60 });
      const b = await callTool<RunDetailResponse>(mcp, "get_run", { run: second.run.id, wait: 60 });
      expect([a.run.status, b.run.status]).toEqual(["succeeded", "succeeded"]);
      // Each wrote while the other ran, in the locations that the other looks at.
      const written = (file: string): number => fs.statSync(path.join(ws.root, file)).mtimeMs;
      const during = (at: number, run: RunDetailResponse["run"]) =>
        run.startedAt < at && at < (run.endedAt ?? 0);
      expect(during(written(own), b.run)).toBe(true);
      expect(during(written(decided), a.run)).toBe(true);

      // A concrete location's output is that path alone; within the pattern, the other run's
      // concrete location is not an output.
      expect(a.run.outputs).toEqual([{ type: "Change brief", path: own, change: "created" }]);
      expect(b.run.outputs).toEqual([{ type: "Change brief", path: decided, change: "created" }]);
      const { artifacts } = await callTool<ArtifactsResponse>(mcp, "list_artifacts", {
        type: "Change brief",
      });
      const producer = (file: string) => artifacts.find((artifact) => artifact.path === file);
      expect(producer(own)?.producedBy).toBe(a.run.id);
      expect(producer(decided)?.producedBy).toBe(b.run.id);
      // Nothing is held by both, so the origin of nothing is in doubt.
      const { assessment } = await callTool<AssessmentResponse>(mcp, "get_assessment", {});
      expect(assessment.findings.filter((f) => f.key === "finding.sharedOrigin")).toEqual([]);
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
      // Codex reports tokens but no cost; its input tokens include the cached ones.
      expect(detail.run.usage).toEqual({
        costUsd: null,
        turns: null,
        inputTokens: 96428,
        cachedInputTokens: 81152,
        outputTokens: 1729,
      });
      expect(detail.run.report).toStartWith("Outcome 0:");
      const texts = detail.events.map((event) => event.text);
      expect(texts).toContain("Thread started");
      // A command that failed says so (rg exits with 1 when it matches nothing).
      expect(texts).toContain(
        `$ /bin/zsh -lc "cat skills/design-solution/SKILL.md; cat docs/changes/CHG-001/change-brief.md; rg --files -g 'AGENTS.md' -g '*template*' -g '*requirements*'" (exit code 1)`,
      );
      // Codex names the files it changed by their absolute paths.
      expect(
        texts.some(
          (text) =>
            text.startsWith("Changed /") &&
            text.endsWith("/docs/changes/CHG-001/design/fake-agent.md"),
        ),
      ).toBe(true);
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
      // Claude Code not logged in: its result says "success" and is_error, and its result text
      // tells the failure.
      expect(copyOf(detail.run)).toMatchObject({
        status: "failed",
        exitCode: 1,
        agentError: "Not logged in · Please run /login",
        usage: { costUsd: 0, turns: 1, inputTokens: 0, cachedInputTokens: 0, outputTokens: 0 },
      });
      expect(detail.events).toContainEqual(
        expect.objectContaining({ kind: "error", text: "Not logged in · Please run /login" }),
      );
      expect(detail.events.map((event) => event.text)).toContain(
        "The agent reported a failure (Not logged in · Please run /login)",
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
    "E3 a Claude Code agent and its version check do not inherit the variables that mark a Claude Code session, and keep the rest; a Codex agent inherits them",
    async () => {
      const dir = tmpDir();
      const dump = (agent: "claude-code" | "codex"): string => path.join(dir, `${agent}.env`);
      const ws = tmpWorkspace({
        agents: {
          "claude-code": {
            command: path.join(FAKES, "claude.ts"),
            env: { ALPS_FAKE_ENV_DUMP: dump("claude-code") },
          },
          codex: {
            command: path.join(FAKES, "codex.ts"),
            env: { ALPS_FAKE_ENV_DUMP: dump("codex") },
          },
        },
      });
      workspaces.push(ws);
      // The harness server as a Claude Code session starts it: the Plugin's MCP server starts the
      // daemon, which inherits the session's marks, a setting of the user's, and the rest.
      const marks = [
        "CLAUDECODE",
        "CLAUDE_CODE_ENTRYPOINT",
        "CLAUDE_CODE_SSE_PORT",
        "CLAUDE_CODE_SESSION_ID",
        "CLAUDE_EFFORT",
      ];
      const mcp = await mcpClient({
        workspace: ws.root,
        env: {
          ...Object.fromEntries(marks.map((name) => [name, "1"])),
          DISABLE_AUTOUPDATER: "1",
          ALPS_E3_KEPT: "kept",
        },
      });
      sessions.push(mcp);
      for (const agent of ["claude-code", "codex"] as const) {
        const { run } = await startDesign(mcp, agent);
        const detail = await callTool<RunDetailResponse>(mcp, "get_run", {
          run: run.id,
          wait: 60,
        });
        expect(detail.run.status).toBe("succeeded");
      }
      const starts = (agent: "claude-code" | "codex"): EnvDump[] =>
        fs
          .readFileSync(dump(agent), "utf8")
          .trim()
          .split("\n")
          .map((line) => JSON.parse(line) as EnvDump);

      const claude = starts("claude-code");
      expect(new Set(claude.map((start) => start.start))).toEqual(new Set(["version", "run"]));
      for (const start of claude) {
        for (const mark of marks) expect(start.names, `${start.start} ${mark}`).not.toContain(mark);
        for (const kept of ["PATH", "DISABLE_AUTOUPDATER"])
          expect(start.names, `${start.start} ${kept}`).toContain(kept);
        expect(start.values.ALPS_E3_KEPT).toBe("kept");
      }
      // Codex is started with the whole environment of the server.
      const codex = starts("codex");
      expect(new Set(codex.map((start) => start.start))).toEqual(new Set(["version", "run"]));
      for (const start of codex)
        for (const mark of marks) expect(start.names, `${start.start} ${mark}`).toContain(mark);
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
