/*
 * E5 (dashboard): after evaluate, changing an input or the SKILL.md makes the instance's evidence
 * stale, and get_assessment and /api/stats count the same (stage 4).
 */

import { afterAll, describe, expect, test } from "bun:test";
import fs from "node:fs";
import path from "node:path";
import type {
  AssessmentResponse,
  InstanceResponse,
  InstancesResponse,
  InstanceView,
  RunDetailResponse,
  RunStartResponse,
  ServerInfo,
  Stats,
} from "../../src/shared/types.ts";
import { apiClient } from "../helpers/api.ts";
import { copyOf } from "../helpers/copy.ts";
import { killStrayDaemons, stopWorkspaceDaemon } from "../helpers/daemon.ts";
import { callTool, mcpClient, type McpSession } from "../helpers/mcp.ts";
import { serverJson } from "../helpers/paths.ts";
import { tmpWorkspace, type TmpWorkspace } from "../helpers/workspace.ts";

let ws: TmpWorkspace | undefined;
let mcp: McpSession | undefined;

afterAll(async () => {
  await mcp?.close().catch(() => {});
  if (ws) await stopWorkspaceDaemon(ws.root).catch(() => {});
  killStrayDaemons();
  ws?.dispose();
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
  test.todo(
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
      const dashboard = await apiClient({ url: `http://127.0.0.1:${info.port}/`, info }).ok<{
        ok: true;
        stats: Stats;
      }>("GET", "/api/stats?period=all");
      expect(assessment.stats?.metrics.staleEvaluations).toBe(2);
      expect(dashboard.stats.metrics.staleEvaluations).toBe(2);
      expect(
        assessment.instances
          .filter((i) => i.stale)
          .map((i) => i.instance)
          .sort(),
      ).toEqual([design.id, release.id].sort());
      // Two Outcomes judged per instance: two achieved, two unverified.
      expect(dashboard.stats.metrics.achievement).toMatchObject({ numerator: 2, denominator: 4 });
      expect(assessment.stats?.metrics.achievement).toEqual(dashboard.stats.metrics.achievement);
    },
    { timeout: 90_000 },
  );
});
