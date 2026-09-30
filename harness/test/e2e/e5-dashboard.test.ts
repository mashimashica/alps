/*
 * E5 (dashboard): after evaluate, changing an input or the SKILL.md makes the instance's evidence
 * stale, and get_assessment and /api/stats count the same. "Changing" means that the content
 * differs (SHA-256) from what the judged run used. The command line's assess prints the same.
 */

import { afterAll, describe, expect, test } from "bun:test";
import fs from "node:fs";
import path from "node:path";
import type {
  Assessment,
  AssessmentMarkdownResponse,
  AssessmentResponse,
  InstanceResponse,
  InstancesResponse,
  InstanceView,
  RunDetailResponse,
  RunStartResponse,
  ServerInfo,
  StatsResponse,
} from "../../src/shared/types.ts";
import { apiClient } from "../helpers/api.ts";
import { copyOf } from "../helpers/copy.ts";
import { killStrayDaemons, stopWorkspaceDaemon } from "../helpers/daemon.ts";
import { callTool, mcpClient, type McpSession } from "../helpers/mcp.ts";
import { serverJson } from "../helpers/paths.ts";
import { cli } from "../helpers/process.ts";
import { tmpWorkspace, type TmpWorkspace } from "../helpers/workspace.ts";

let ws: TmpWorkspace | undefined;
let mcp: McpSession | undefined;
const workspaces: TmpWorkspace[] = [];
const sessions: McpSession[] = [];

afterAll(async () => {
  for (const session of [mcp, ...sessions]) await session?.close().catch(() => {});
  for (const workspace of [ws, ...workspaces])
    if (workspace) await stopWorkspaceDaemon(workspace.root).catch(() => {});
  killStrayDaemons();
  for (const workspace of [ws, ...workspaces]) workspace?.dispose();
});

/** Instantiates a Process, runs it with the demo, and judges each of its Outcomes with evidence. */
async function evaluated(
  session: McpSession,
  process: string,
  inputs: Record<string, string[]>,
  outputs: Record<string, string>,
): Promise<InstanceView> {
  const { instance } = await callTool<InstanceResponse>(session, "instantiate", {
    process,
    inputs,
    outputs,
  });
  const { run } = await callTool<RunStartResponse>(session, "run", {
    instance: instance.id,
    agent: "demo",
  });
  await callTool<RunDetailResponse>(session, "get_run", { run: run.id, wait: 30 });
  const judged = await callTool<InstanceResponse>(session, "evaluate", {
    instance: instance.id,
    judgments: [
      {
        outcome: 0,
        judgment: "achieved",
        evidence: "Read the output: it covers the first Outcome.",
      },
      {
        outcome: 1,
        judgment: "unverified",
        evidence: "The demo output does not show the second Outcome.",
        limits: "Demo only.",
      },
    ],
  });
  return judged.instance;
}

describe("E5 dashboard", () => {
  test(
    "E5 the evidence is stale once an input or the SKILL.md no longer holds what the judged run used, and touching them changes nothing",
    async () => {
      const work = tmpWorkspace();
      workspaces.push(work);
      const session = await mcpClient({ workspace: work.root });
      sessions.push(session);
      const brief = path.join(work.root, "docs/changes/CHG-001/change-brief.md");
      const skill = path.join(work.root, "skills/design-solution/SKILL.md");
      const design = await evaluated(
        session,
        "Solution Design",
        { "Change brief": ["docs/changes/CHG-001/change-brief.md"] },
        { "Design description": "docs/changes/CHG-001/design/" },
      );
      const facts = async (): Promise<InstanceView["facts"]> =>
        (await callTool<InstancesResponse>(session, "list_instances")).instances.find(
          (i) => i.id === design.id,
        )!.facts;
      expect((await facts()).stale).toBe(false);

      // Newer modification times with the same content: still current.
      const later = new Date(Date.now() + 60_000);
      fs.utimesSync(brief, later, later);
      fs.utimesSync(skill, later, later);
      expect(copyOf(await facts())).toMatchObject({ stale: false, staleness: [] });

      // Another content: stale, until the content is what the judged run used again.
      const original = fs.readFileSync(brief, "utf8");
      fs.appendFileSync(brief, "\n- Search results show the stock level.\n");
      expect(copyOf(await facts())).toMatchObject({
        stale: true,
        staleness: [
          { kind: "input", path: "docs/changes/CHG-001/change-brief.md", change: "modified" },
        ],
      });
      fs.writeFileSync(brief, original);
      expect((await facts()).stale).toBe(false);

      // The SKILL.md is compared the same way.
      fs.appendFileSync(skill, "\n");
      expect(copyOf(await facts())).toMatchObject({
        stale: true,
        staleness: [{ kind: "skill", path: "skills/design-solution/SKILL.md" }],
      });
    },
    { timeout: 90_000 },
  );

  test(
    "E5 after evaluate, changing an input or the SKILL.md makes the evidence stale, and get_assessment and /api/stats count the same",
    async () => {
      ws = tmpWorkspace({ server: { idleMinutes: 5 } });
      mcp = await mcpClient({ workspace: ws.root });
      const brief = "docs/changes/CHG-001/change-brief.md";
      const skill = "skills/release-to-production/SKILL.md";
      const design = await evaluated(
        mcp,
        "Solution Design",
        { "Change brief": [brief] },
        { "Design description": "docs/changes/CHG-001/design/" },
      );
      const release = await evaluated(
        mcp,
        "Production Release",
        { "Release candidate": ["releases/CHG-001/candidate.json"] },
        { "Deployed service revision": "releases/CHG-001/deployment.json" },
      );
      expect(copyOf(design.evaluation)).toMatchObject({
        by: { kind: "agent", id: "alps-harness-e2e" },
      });
      const stale = async (): Promise<Record<string, InstanceView["facts"]>> =>
        Object.fromEntries(
          (await callTool<InstancesResponse>(mcp!, "list_instances")).instances.map((i) => [
            i.id,
            i.facts,
          ]),
        );
      expect(Object.values(await stale()).map((facts) => facts.stale)).toEqual([false, false]);

      // After the judgments: the design's input and the release's SKILL.md change.
      await Bun.sleep(20);
      const afterJudgments = Date.now();
      fs.appendFileSync(path.join(ws.root, brief), "\n- Search results show the stock level.\n");
      fs.appendFileSync(path.join(ws.root, skill), "\n");
      const facts = await stale();
      expect(copyOf(facts[design.id])).toMatchObject({
        stale: true,
        staleness: [{ kind: "input", path: brief, change: "modified" }],
      });
      expect(copyOf(facts[release.id])).toMatchObject({
        stale: true,
        staleness: [{ kind: "skill", path: skill }],
      });

      // The assessment and the dashboard count the same stale evaluations.
      const { assessment } = await callTool<AssessmentResponse>(mcp, "get_assessment", {
        format: "json",
      });
      const info = JSON.parse(fs.readFileSync(serverJson(ws.root), "utf8")) as ServerInfo;
      const api = apiClient({ url: `http://127.0.0.1:${info.port}/`, info });
      const dashboard = await api.ok<StatsResponse>("GET", "/api/stats?period=all");
      expect(assessment.stats.metrics.staleEvaluations).toBe(2);
      expect(dashboard.stats.metrics.staleEvaluations).toBe(2);
      expect(
        assessment.instances
          .filter((i) => i.stale)
          .map((i) => i.instance)
          .sort(),
      ).toEqual([design.id, release.id].sort());
      // Two Outcomes judged per instance: two achieved, two unverified.
      expect(dashboard.stats.metrics.achievement).toMatchObject({ numerator: 2, denominator: 4 });
      expect(assessment.stats.metrics.achievement).toEqual(dashboard.stats.metrics.achievement);
      expect(assessment.stats.metrics.unverified).toEqual(dashboard.stats.metrics.unverified);
      expect(assessment.stats.metrics.runSuccess).toEqual(dashboard.stats.metrics.runSuccess);
      expect(dashboard.stats.metrics.runSuccess).toMatchObject({ numerator: 2, denominator: 2 });
      // What the numbers count: both instances are judged, and their evaluations are stale.
      expect(
        dashboard.members.instances
          .filter((i) => i.stale)
          .map((i) => i.id)
          .sort(),
      ).toEqual([design.id, release.id].sort());
      // The stale evaluations are the state now, whatever the window: an assessment since the
      // judgments, which counts none of them, and the dashboard's 7 days count the same two.
      const recent = await callTool<AssessmentResponse>(mcp, "get_assessment", {
        format: "json",
        since: afterJudgments,
      });
      const week = await api.ok<StatsResponse>("GET", "/api/stats?period=7d");
      expect(recent.assessment.stats.metrics.achievement.denominator).toBe(0);
      expect(recent.assessment.stats.metrics.staleEvaluations).toBe(2);
      expect(week.stats.metrics.staleEvaluations).toBe(2);
      expect(
        week.members.instances
          .filter((i) => i.stale)
          .map((i) => i.id)
          .sort(),
      ).toEqual([design.id, release.id].sort());
      // The findings say which SKILL.md changed after its Process last ran.
      expect(assessment.findings).toContainEqual(
        expect.objectContaining({
          kind: "unverified",
          key: "finding.skillChanged",
          subject: { process: "Production Release" },
        }),
      );

      // The Markdown form reports the same statistics.
      const { markdown } = await callTool<AssessmentMarkdownResponse>(mcp, "get_assessment", {
        format: "markdown",
      });
      expect(markdown).toContain("## Statistics");
      expect(markdown).toContain("| Stale evaluations | 2 |");
      expect(markdown).toContain("| Achievement | 50% (2 of 4 judged Outcomes) |");
      const since = await callTool<AssessmentMarkdownResponse>(mcp, "get_assessment", {
        format: "markdown",
        since: afterJudgments,
      });
      expect(since.markdown).toContain("Stale evaluations are counted as they are now.");
      expect(since.markdown).toContain("| Stale evaluations | 2 |");

      // alps-harness assess asks the daemon that runs and prints the same assessment.
      const printed = await cli(["assess", ws.root]);
      expect(printed.code, printed.stderr).toBe(0);
      expect(printed.stdout).toContain("## Statistics");
      expect(printed.stdout).toContain("| Stale evaluations | 2 |");
      expect(printed.stdout).toContain("| Achievement | 50% (2 of 4 judged Outcomes) |");
      const json = await cli(["assess", ws.root, "--format", "json"]);
      expect(json.code, json.stderr).toBe(0);
      const printedJson = JSON.parse(json.stdout) as Assessment;
      expect(printedJson.stats.metrics.staleEvaluations).toBe(2);
      expect(printedJson.stats.metrics.achievement).toMatchObject({ numerator: 2, denominator: 4 });
      expect(printedJson.findings).toEqual(assessment.findings);
      const wrong = await cli(["assess", ws.root, "--format", "html"]);
      expect(wrong.code).toBe(2);
      expect(wrong.stderr).toContain("--format must be markdown or json.");
    },
    { timeout: 90_000 },
  );
});
