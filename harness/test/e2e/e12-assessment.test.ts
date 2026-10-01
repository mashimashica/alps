/*
 * E12 (assessment): an assessment's agent reads the records through the harness's MCP server and
 * records what it finds; the analysis then shows the latest assessment, an interpretation kept
 * apart from the observation below it, and an evidence chip opens the run it cites. Before any
 * assessment the analysis shows only the empty state. A person's review of an item is recorded,
 * and a run added after the assessment counts in its since. The agent of an assessment is refused
 * run, instantiate, wake, evaluate, and cancel_run; list_runs filters the runs; evaluate keeps the
 * evaluations that it replaces. With the agent self the calling session performs the assessment
 * (a request from no MCP client is refused), and the harness refuses an item without evidence and
 * evidence that names what the records do not have.
 * alps-harness assess --with starts one, and alps-harness assess prints the latest with the
 * observation.
 *
 * What the fake assessment agent does (test/fakes/assess-agent.ts): it is started as claude-code
 * is, with the MCP configuration the harness gives it (--mcp-config), connects with
 * @modelcontextprotocol/client, reads get_assessment, list_runs (kind process), list_instances,
 * and get_run (the newest process run), records three items with record_assessment (a
 * configuration item citing that run, the first event of its log, its first output, and its
 * Process's run success; a description item citing the newest judged instance's evaluation; an
 * unverified item without evidence), and ends with finish_run. With ALPS_FAKE_TRY_RUN it also
 * calls instantiate, run, and wake, and its report says how each was answered.
 */

import { afterAll, describe, expect, test } from "bun:test";
import path from "node:path";
import type { Browser, Page } from "playwright";
import type {
  AssessResponse,
  AssessmentMarkdownResponse,
  AssessmentRecordResponse,
  AssessmentResponse,
  Failure,
  InstanceResponse,
  InstancesResponse,
  RunDetailResponse,
  RunStartResponse,
  RunsResponse,
} from "../../src/shared/types.ts";
import { apiClient, type Api } from "../helpers/api.ts";
import { closeBrowser, killStrayBrowsers, launchBrowser } from "../helpers/browser.ts";
import {
  killStrayDaemons,
  readServerInfo,
  startDaemon,
  stopWorkspaceDaemon,
  type Daemon,
} from "../helpers/daemon.ts";
import { callTool, mcpClient, toolFailure, type McpSession } from "../helpers/mcp.ts";
import { FAKES } from "../helpers/paths.ts";
import { cli, HOOK_TIMEOUT_MS } from "../helpers/process.ts";
import { tmpWorkspace, type TmpWorkspace } from "../helpers/workspace.ts";

const workspaces: TmpWorkspace[] = [];
const sessions: McpSession[] = [];

afterAll(async () => {
  for (const session of sessions) await session.close().catch(() => {});
  killStrayBrowsers();
  for (const ws of workspaces) await stopWorkspaceDaemon(ws.root).catch(() => {});
  killStrayDaemons();
  for (const ws of workspaces) ws.dispose();
}, HOOK_TIMEOUT_MS);

const ASSESS_AGENT = path.join(FAKES, "assess-agent.ts");
const BRIEF = "docs/changes/CHG-001/change-brief.md";

/** A workspace whose claude-code is the fake assessment agent. */
function assessWorkspace(env: Record<string, string> = {}): TmpWorkspace {
  const ws = tmpWorkspace({
    agents: {
      "claude-code": { command: ASSESS_AGENT, env: { ALPS_FAKE_SCENARIO: "ok", ...env } },
    },
  });
  workspaces.push(ws);
  return ws;
}

/** A Solution Design instance with a demo run that ended, judged twice (the second replaces the first). */
async function seed(api: Api): Promise<{ instance: string; run: string }> {
  const { instance } = await api.ok<InstanceResponse>("POST", "/api/instances", {
    process: "Solution Design",
    inputs: { "Change brief": [BRIEF] },
    outputs: { "Design description": "docs/changes/CHG-001/design/" },
  });
  const { run } = await api.ok<RunStartResponse>("POST", `/api/instances/${instance.id}/run`, {
    agent: "demo",
  });
  await api.ok<RunDetailResponse>("GET", `/api/runs/${run.id}?wait=30`);
  for (const judgment of ["unverified", "achieved"])
    await api.ok<InstanceResponse>("POST", `/api/instances/${instance.id}/evaluate`, {
      judgments: [{ outcome: 0, judgment, evidence: `Read the design that ${run.id} wrote.` }],
    });
  return { instance: instance.id, run: run.id };
}

/** The analysis in a browser, in English, with what goes wrong on the page collected. */
async function openAnalysis(
  browser: Browser,
  daemon: Daemon,
): Promise<{ page: Page; problems: string[] }> {
  const page = await browser.newPage({ viewport: { width: 1280, height: 800 }, locale: "en-US" });
  const problems: string[] = [];
  page.on("console", (message) => {
    if (message.type() === "error") problems.push(`console: ${message.text()}`);
  });
  page.on("pageerror", (error) => problems.push(`page: ${error.message}`));
  await page.goto(`${daemon.uiUrl}&view=dashboard`);
  await page.locator('[data-testid="health"][data-status="ok"]').waitFor({ timeout: 15_000 });
  return { page, problems };
}

describe("E12 assessment", () => {
  test(
    "E12 before any assessment, latest is null and the analysis shows only the empty state",
    async () => {
      const ws = assessWorkspace();
      const daemon = await startDaemon(ws.root, [], { cwd: "/" });
      const api = apiClient(daemon);
      const browser = await launchBrowser();
      try {
        const { assessment } = await api.ok<AssessmentResponse>("GET", "/api/assessment");
        expect(assessment.latest).toBeNull();
        expect(assessment.since).toBeNull();
        const { page, problems } = await openAnalysis(browser, daemon);
        const card = page.getByTestId("assessment");
        await page
          .locator('[data-testid="assessment"][data-state="empty"]')
          .waitFor({ timeout: 10_000 });
        expect(await card.getByTestId("assessment-latest").count()).toBe(0);
        expect(await card.getByTestId("opportunities").count()).toBe(0);
        expect(await card.getByTestId("assess-open").count()).toBe(1);
        // The observation is below it, as before.
        await page.getByTestId("observation").getByTestId("findings").waitFor({ timeout: 10_000 });
        expect(problems).toEqual([]);
      } finally {
        await closeBrowser(browser);
        await daemon.stop();
      }
    },
    { timeout: 60_000 },
  );

  test(
    "E12 an assessment's agent records what it finds: the analysis shows it as the latest, its run chip opens the run, a person's review is recorded, and a run added afterwards counts in since",
    async () => {
      const ws = assessWorkspace({ ALPS_FAKE_TRY_RUN: "1" });
      const daemon = await startDaemon(ws.root, [], { cwd: "/" });
      const api = apiClient(daemon);
      const seeded = await seed(api);
      const mcp = await mcpClient({ workspace: ws.root });
      sessions.push(mcp);
      const started = await callTool<AssessResponse>(mcp, "assess", {
        scope: { period: "all" },
        request: "Why do the runs not do the work?",
      });
      expect(started.run).toMatchObject({
        kind: "assess",
        instance: null,
        process: null,
        status: "running",
        scope: { period: "all", request: "Why do the runs not do the work?" },
      });
      expect(started.prompt).toBeUndefined();
      expect(started.run.command).toContain("--allowedTools mcp__alps_harness");
      // One assessment runs at a time.
      const second = await toolFailure(mcp, "assess", {});
      expect(second.error.code).toBe("already-running");
      const ended = await callTool<RunDetailResponse>(mcp, "get_run", {
        run: started.run.id,
        wait: 60,
      });
      expect(ended.run.status).toBe("succeeded");
      // The agent of an assessment is refused what would change the records.
      expect(ended.run.report).toContain(
        "Tried anyway: instantiate refused (invalid-request); run refused (invalid-request); wake refused (invalid-request).",
      );
      // The prompt names the scope and the point of view, and what not to do.
      expect(ended.run.prompt).toContain("- Period: all time");
      expect(ended.run.prompt).toContain("> Why do the runs not do the work?");
      expect(ended.run.prompt).toContain("record_assessment");
      expect(ended.run.prompt).toContain(`call finish_run for run ${started.run.id}`);

      const { assessment } = await callTool<AssessmentResponse>(mcp, "get_assessment", {});
      const latest = assessment.latest;
      expect(latest).toMatchObject({
        id: started.run.id,
        runId: started.run.id,
        agent: "claude-code",
        scope: { period: "all" },
        reviews: [],
      });
      expect(latest?.items.map((item) => [item.n, item.kind])).toEqual([
        [1, "configuration"],
        [2, "description"],
        [3, "unverified"],
      ]);
      expect(latest?.items[0]?.evidence).toEqual([
        { run: seeded.run },
        { log: { run: seeded.run, n: 1 } },
        { path: "docs/changes/CHG-001/design" },
        { stat: { filter: { period: "all", process: "Solution Design" }, metric: "runSuccess" } },
      ]);
      expect(assessment.since).toEqual({ runs: 0, judgments: 0 });
      // An assessment run counts in no statistic: the demo run is the only run.
      expect(assessment.stats.metrics.runSuccess).toMatchObject({ numerator: 1, denominator: 1 });

      const browser = await launchBrowser();
      try {
        const { page, problems } = await openAnalysis(browser, daemon);
        const card = page.getByTestId("assessment");
        const shown = card.getByTestId("assessment-latest");
        await shown.waitFor({ timeout: 10_000 });
        expect(await shown.getAttribute("data-assessment")).toBe(started.run.id);
        expect(await card.getByTestId("assessment-summary").textContent()).toContain(
          "Did not read the content of the Artifacts.",
        );
        expect(await card.getByTestId("opportunities").locator("[data-item]").count()).toBe(3);
        expect(await card.getByTestId("assessment-since").getAttribute("data-runs")).toBe("0");

        // The run chip of the first item opens that run in the panel.
        await card.locator('[data-item="1"] [data-evidence="run"]').click();
        await page
          .locator(`[data-testid="panel-run"][data-run="${seeded.run}"]`)
          .waitFor({ timeout: 5000 });

        // A person reviews the first item: adopted, with a note.
        await card.locator('[data-item="1"]').getByTestId("review-open").click();
        const dialog = page.getByTestId("review");
        await dialog.waitFor({ timeout: 5000 });
        await dialog.locator('input[value="adopted"]').check();
        await dialog.getByTestId("review-note").fill("Run it with a real agent.");
        await dialog.getByRole("button", { name: "Record the review" }).click();
        await card.locator('[data-item="1"] [data-review="adopted"]').waitFor({ timeout: 10_000 });
        const reviewed = await api.ok<AssessmentRecordResponse>(
          "GET",
          `/api/assessments/${started.run.id}`,
        );
        expect(reviewed.assessment.reviews).toEqual([
          {
            n: 1,
            judgment: "adopted",
            note: "Run it with a real agent.",
            by: { kind: "user" },
            at: expect.any(Number),
          },
        ]);

        // A run after the assessment counts in its since.
        const { run } = await api.ok<RunStartResponse>(
          "POST",
          `/api/instances/${seeded.instance}/run`,
          { agent: "demo" },
        );
        await api.ok<RunDetailResponse>("GET", `/api/runs/${run.id}?wait=30`);
        await card
          .locator('[data-testid="assessment-since"][data-runs="1"]')
          .waitFor({ timeout: 10_000 });
        const after = await api.ok<AssessmentResponse>("GET", "/api/assessment");
        expect(after.assessment.since).toEqual({ runs: 1, judgments: 0 });
        expect(problems).toEqual([]);
      } finally {
        await closeBrowser(browser);
        await daemon.stop();
      }
    },
    { timeout: 150_000 },
  );

  test(
    "E12 the agent of an assessment is refused run, instantiate, wake, evaluate, and cancel_run, through its MCP server or with its header",
    async () => {
      const ws = assessWorkspace();
      const daemon = await startDaemon(ws.root, [], { cwd: "/" });
      const api = apiClient(daemon);
      try {
        const seeded = await seed(api);
        const { run } = await api.ok<AssessResponse>("POST", "/api/assess", {});
        await api.ok<RunDetailResponse>("GET", `/api/runs/${run.id}?wait=60`);
        // What its MCP server sends: the client, and the assessment run it serves.
        const headers = {
          "X-Harness-Token": daemon.info.token,
          "Content-Type": "application/json",
          "X-Harness-Client": encodeURIComponent(JSON.stringify({ name: "agent", version: "1" })),
          "X-Harness-Assess": run.id,
        };
        for (const [route, body] of [
          [`/api/instances/${seeded.instance}/run`, { agent: "demo" }],
          ["/api/instances", { process: "Solution Design" }],
          ["/api/wake", { request: "Run it." }],
          [
            `/api/instances/${seeded.instance}/evaluate`,
            { judgments: [{ outcome: 0, judgment: "achieved", evidence: "Read it." }] },
          ],
          [`/api/runs/${seeded.run}/cancel`, {}],
        ] as const) {
          const response = await fetch(new URL(route, daemon.url), {
            method: "POST",
            headers,
            body: JSON.stringify(body),
          });
          const failure = (await response.json()) as Failure;
          expect([response.status, failure.error.code, failure.error.key], route).toEqual([
            400,
            "invalid-request",
            "error.assessOnly",
          ]);
        }
      } finally {
        await daemon.stop();
      }
    },
    { timeout: 120_000 },
  );

  test(
    "E12 list_runs lists the runs newest first, by Process, agent, status, kind, and since",
    async () => {
      const ws = assessWorkspace();
      const mcp = await mcpClient({ workspace: ws.root });
      sessions.push(mcp);
      const { instance } = await callTool<InstanceResponse>(mcp, "instantiate", {
        process: "Solution Design",
        inputs: { "Change brief": [BRIEF] },
      });
      const first = await callTool<RunStartResponse>(mcp, "run", {
        instance: instance.id,
        agent: "demo",
      });
      await callTool<RunDetailResponse>(mcp, "get_run", { run: first.run.id, wait: 30 });
      const assessed = await callTool<AssessResponse>(mcp, "assess", {});
      await callTool<RunDetailResponse>(mcp, "get_run", { run: assessed.run.id, wait: 60 });
      const second = await callTool<RunStartResponse>(mcp, "run", {
        instance: instance.id,
        agent: "demo",
      });
      await callTool<RunDetailResponse>(mcp, "get_run", { run: second.run.id, wait: 30 });

      const ids = (result: RunsResponse): string[] => result.runs.map((run) => run.id);
      const all = await callTool<RunsResponse>(mcp, "list_runs", {});
      expect(ids(all)).toEqual([second.run.id, assessed.run.id, first.run.id]);
      expect(all.runs[0]).toMatchObject({
        kind: "process",
        process: "Solution Design",
        agent: "demo",
        status: "succeeded",
        costUsd: null,
      });
      expect(ids(await callTool<RunsResponse>(mcp, "list_runs", { kind: "assess" }))).toEqual([
        assessed.run.id,
      ]);
      expect(
        ids(await callTool<RunsResponse>(mcp, "list_runs", { process: "Solution Design" })),
      ).toEqual([second.run.id, first.run.id]);
      expect(ids(await callTool<RunsResponse>(mcp, "list_runs", { agent: "claude-code" }))).toEqual(
        [assessed.run.id],
      );
      expect(ids(await callTool<RunsResponse>(mcp, "list_runs", { status: "running" }))).toEqual(
        [],
      );
      expect(
        ids(await callTool<RunsResponse>(mcp, "list_runs", { since: second.run.startedAt })),
      ).toEqual([second.run.id]);
      const page = await callTool<RunsResponse>(mcp, "list_runs", { limit: 2 });
      expect(ids(page)).toEqual([second.run.id, assessed.run.id]);
      expect(
        ids(await callTool<RunsResponse>(mcp, "list_runs", { limit: 2, cursor: page.next })),
      ).toEqual([first.run.id]);
      const unknown = await toolFailure(mcp, "list_runs", { process: "No Such Process" });
      expect(unknown.error.code).toBe("not-found");
    },
    { timeout: 150_000 },
  );

  test(
    "E12 evaluate keeps the evaluations that it replaces, newest first",
    async () => {
      const ws = assessWorkspace();
      const mcp = await mcpClient({ workspace: ws.root });
      sessions.push(mcp);
      const { instance } = await callTool<InstanceResponse>(mcp, "instantiate", {
        process: "Solution Design",
        inputs: { "Change brief": [BRIEF] },
      });
      const { run } = await callTool<RunStartResponse>(mcp, "run", {
        instance: instance.id,
        agent: "demo",
      });
      await callTool<RunDetailResponse>(mcp, "get_run", { run: run.id, wait: 30 });
      for (const judgment of ["not-achieved", "unverified", "achieved"])
        await callTool<InstanceResponse>(mcp, "evaluate", {
          instance: instance.id,
          judgments: [{ outcome: 0, judgment, evidence: `Read it (${judgment}).` }],
        });
      const { instances } = await callTool<InstancesResponse>(mcp, "list_instances", {});
      const [listed] = instances;
      expect(listed?.evaluation?.judgments[0]?.judgment).toBe("achieved");
      expect(listed?.evaluations?.map((e) => e.judgments[0]?.judgment)).toEqual([
        "unverified",
        "not-achieved",
      ]);
      // The statistics count the evaluation now only.
      const { assessment } = await callTool<AssessmentResponse>(mcp, "get_assessment", {});
      expect(assessment.stats.metrics.achievement).toMatchObject({ numerator: 1, denominator: 1 });
    },
    { timeout: 90_000 },
  );

  test(
    "E12 with the agent self the calling session performs the assessment, and the harness refuses an item without evidence and evidence that names what the records do not have",
    async () => {
      const ws = assessWorkspace();
      const mcp = await mcpClient({ workspace: ws.root });
      sessions.push(mcp);
      const { instance } = await callTool<InstanceResponse>(mcp, "instantiate", {
        process: "Solution Design",
        inputs: { "Change brief": [BRIEF] },
      });
      const { run: done } = await callTool<RunStartResponse>(mcp, "run", {
        instance: instance.id,
        agent: "demo",
      });
      const detail = await callTool<RunDetailResponse>(mcp, "get_run", { run: done.id, wait: 30 });

      const started = await callTool<AssessResponse>(mcp, "assess", {
        agent: "self",
        scope: { process: "Solution Design", period: "30d" },
      });
      expect(started.run).toMatchObject({
        kind: "assess",
        agent: "self",
        command: null,
        scope: { process: "Solution Design", period: "30d" },
      });
      expect(started.prompt).toContain("assess-harness-records");
      expect(started.prompt).toContain("- Process: Solution Design");
      const id = started.run.id;

      // While it runs, this session makes no instance, evaluates nothing, and cancels no run.
      for (const [tool, args] of [
        ["instantiate", { process: "Solution Design" }],
        [
          "evaluate",
          {
            instance: instance.id,
            judgments: [{ outcome: 0, judgment: "achieved", evidence: "Read it." }],
          },
        ],
        ["cancel_run", { run: id }],
      ] as const) {
        const refused = await toolFailure(mcp, tool, args);
        expect([refused.error.code, refused.error.key], tool).toEqual([
          "invalid-request",
          "error.assessOnly",
        ]);
      }
      // Another session performs no assessment, so it records none.
      const other = await mcpClient({ workspace: ws.root, name: "another-client" });
      sessions.push(other);
      const stranger = await toolFailure(other, "record_assessment", {
        summary: "Read nothing.",
        items: [],
      });
      expect(stranger.error.key).toBe("error.noAssessRun");

      const record = (items: unknown[]) =>
        toolFailure(mcp, "record_assessment", { summary: "Read the runs.", items });
      const statement = "The demo writes placeholders.";
      const refusals = [
        [[{ kind: "configuration", statement }], "invalid-request", "error.noEvidence"],
        [
          [{ kind: "configuration", statement, evidence: [{ run: "r999" }] }],
          "invalid-request",
          "error.evidenceRun",
        ],
        [
          [
            {
              kind: "configuration",
              statement,
              evidence: [{ log: { run: done.id, n: detail.run.events + 1 } }],
            },
          ],
          "invalid-request",
          "error.evidenceLog",
        ],
        [
          [{ kind: "description", statement, evidence: [{ evaluation: instance.id }] }],
          "invalid-request",
          "error.evidenceEvaluation",
        ],
        [
          [{ kind: "operation", statement, evidence: [{ path: "docs/none.md" }] }],
          "invalid-request",
          "error.evidencePath",
        ],
        [
          [{ kind: "operation", statement, evidence: [{ path: "../outside.md" }] }],
          "outside-workspace",
          "error.outside",
        ],
        [
          [{ kind: "operation", statement, evidence: [{ path: ".alps-harness/state.json" }] }],
          "outside-workspace",
          "error.records",
        ],
        [
          [
            {
              kind: "description",
              subject: { process: "No Such Process" },
              statement,
              evidence: [{ run: done.id }],
            },
          ],
          "invalid-request",
          "error.itemSubject",
        ],
        [
          [
            {
              kind: "operation",
              statement,
              evidence: [
                { stat: { filter: { process: "No Such Process" }, metric: "runSuccess" } },
              ],
            },
          ],
          "invalid-request",
          "error.evidenceProcess",
        ],
      ] as const;
      for (const [items, code, key] of refusals) {
        const refused = await record([...items]);
        expect([refused.error.code, refused.error.key], key).toEqual([code, key]);
      }

      const recorded = await callTool<AssessmentRecordResponse>(mcp, "record_assessment", {
        summary: "Read the runs of Solution Design.",
        items: [
          {
            kind: "configuration",
            subject: { process: "Solution Design" },
            statement,
            evidence: [
              { run: done.id },
              { path: BRIEF },
              { stat: { filter: { process: "Solution Design" }, metric: "runSuccess" } },
            ],
          },
          { kind: "unverified", statement: "Whether a real agent would do better is not known." },
        ],
      });
      expect(recorded.assessment.items.map((item) => item.n)).toEqual([1, 2]);
      // Until its run ends, it is not the latest, and nobody reviews it.
      const { assessment: before } = await callTool<AssessmentResponse>(mcp, "get_assessment", {});
      expect(before.latest).toBeNull();
      // The daemon that the MCP server started, as the WebUI reaches it.
      const info = readServerInfo(ws.root);
      if (!info) throw new Error("no daemon serves the workspace");
      const api = apiClient({ url: `http://127.0.0.1:${info.port}/`, info });
      const early = await api.post<AssessmentRecordResponse>(
        `/api/assessments/${id}/items/1/review`,
        { judgment: "held" },
      );
      expect([early.status, (early.body as Failure).error.key]).toEqual([
        400,
        "error.assessmentOpen",
      ]);

      const finished = await callTool<{ run: { status: string } }>(mcp, "finish_run", {
        run: id,
        report: "Read the runs of Solution Design.",
        status: "succeeded",
      });
      expect(finished.run.status).toBe("succeeded");
      const { assessment } = await callTool<AssessmentResponse>(mcp, "get_assessment", {});
      expect(assessment.latest?.id).toBe(id);
      expect(assessment.latest?.scope).toEqual({ process: "Solution Design", period: "30d" });
      expect(assessment.since).toEqual({ runs: 0, judgments: 0 });
      // The Markdown puts the interpretation first, apart from the observation.
      const { markdown } = await callTool<AssessmentMarkdownResponse>(mcp, "get_assessment", {
        format: "markdown",
      });
      expect(markdown.indexOf("## Latest assessment (interpretation)")).toBeLessThan(
        markdown.indexOf("## Statistics"),
      );
      expect(markdown).toContain("> Read the runs of Solution Design.");
      expect(markdown).toContain("## Checks");
      // An item that the assessment does not have, and a review that names an MCP client, are refused.
      const missing = await api.post<AssessmentRecordResponse>(
        `/api/assessments/${id}/items/9/review`,
        { judgment: "held" },
      );
      expect((missing.body as Failure).error.code).toBe("not-found");
      const held = await api.ok<AssessmentRecordResponse>(
        "POST",
        `/api/assessments/${id}/items/2/review`,
        { judgment: "held", note: "Ask for a run with Claude Code." },
      );
      expect(held.assessment.reviews.map((r) => [r.n, r.judgment])).toEqual([[2, "held"]]);
    },
    { timeout: 120_000 },
  );

  test(
    "E12 with the agent self only an MCP session assesses: a request from no MCP client is refused and leaves no assessment running",
    async () => {
      const ws = assessWorkspace();
      const daemon = await startDaemon(ws.root, [], { cwd: "/" });
      const api = apiClient(daemon);
      try {
        const refused = await api.post<AssessResponse>("/api/assess", { agent: "self" });
        const { error } = refused.body as Failure;
        expect([refused.status, error.code, error.key]).toEqual([
          400,
          "invalid-request",
          "error.selfAssess",
        ]);
        // No assessment was recorded, so the next one starts.
        const { run } = await api.ok<AssessResponse>("POST", "/api/assess", {});
        expect(run.status).toBe("running");
        await api.ok<RunDetailResponse>("GET", `/api/runs/${run.id}?wait=60`);
      } finally {
        await daemon.stop();
      }
    },
    { timeout: 120_000 },
  );

  test(
    "E12 alps-harness assess --with starts an assessment, and alps-harness assess prints the latest with the observation",
    async () => {
      const ws = assessWorkspace();
      const daemon = await startDaemon(ws.root, [], { cwd: "/" });
      const api = apiClient(daemon);
      try {
        const wrong = await cli(["assess", ws.root, "--request", "Look."]);
        expect(wrong.code).toBe(2);
        expect(wrong.stderr).toContain("--request needs --with");
        const started = await cli([
          "assess",
          ws.root,
          "--with",
          "claude-code",
          "--request",
          "Look at the failures.",
        ]);
        expect(started.code, started.stderr).toBe(0);
        const id = /assessment run (r\d+)/.exec(started.stdout)?.[1] ?? "";
        expect(id).toMatch(/^r\d+$/);
        const ended = await api.ok<RunDetailResponse>("GET", `/api/runs/${id}?wait=60`);
        expect(ended.run.scope).toEqual({ request: "Look at the failures." });
        const printed = await cli(["assess", ws.root]);
        expect(printed.code, printed.stderr).toBe(0);
        expect(printed.stdout).toContain("## Latest assessment (interpretation)");
        expect(printed.stdout).toContain(`An agent's interpretation: claude-code`);
        expect(printed.stdout).toContain("## Statistics");
        expect(printed.stdout).toContain("## Checks");
      } finally {
        await daemon.stop();
      }
    },
    { timeout: 120_000 },
  );
});
