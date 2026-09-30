/*
 * The dashboard's statistics and the assessment's findings (Dashboard): metrics, trends, and
 * breakdowns counted from the records of test/fixtures/stats/records.json, checked against numbers
 * worked out by hand. Wake runs are not counted; only recorded three-valued judgments are.
 */

import { describe, expect, test } from "bun:test";
import fs from "node:fs";
import {
  computeStats,
  dayStart,
  findingsOf,
  quantile,
  statsWindow,
  weekStart,
  type FindingsInput,
  type StatsInput,
  type StatsRunRecord,
} from "../../src/assess.ts";
import type {
  AgentInfo,
  ArtifactType,
  Instance,
  InstanceFacts,
  ProcessView,
  StatsFilter,
} from "../../src/shared/types.ts";

interface FixtureEvaluation extends Omit<NonNullable<Instance["evaluation"]>, "at"> {
  at: string;
}
interface Fixture {
  now: string;
  utcOffsetMinutes: number;
  processes: StatsInput["processes"];
  stale: string[];
  instances: (Pick<Instance, "id" | "process" | "runs"> & {
    evaluation: FixtureEvaluation | null;
  })[];
  runs: (Omit<StatsRunRecord, "startedAt" | "endedAt"> & {
    startedAt: string;
    endedAt: string | null;
  })[];
}

const fixture = JSON.parse(
  fs.readFileSync(new URL("../fixtures/stats/records.json", import.meta.url), "utf8"),
) as Fixture;
const ms = Date.parse;
const clock = { now: ms(fixture.now), utcOffsetMinutes: fixture.utcOffsetMinutes };
const input: StatsInput = {
  processes: fixture.processes,
  stale: new Set(fixture.stale),
  instances: fixture.instances.map((i) => ({
    ...i,
    inputs: {},
    outputs: {},
    criteria: [],
    notes: "",
    evaluation: i.evaluation ? { ...i.evaluation, at: ms(i.evaluation.at) } : null,
  })),
  runs: fixture.runs.map((r) => ({
    ...r,
    startedAt: ms(r.startedAt),
    endedAt: r.endedAt === null ? null : ms(r.endedAt),
  })),
};
const stats = (filter: Partial<StatsFilter> = {}) =>
  computeStats(input, { period: "7d", granularity: "day", ...filter }, clock);
const SECOND = 1000;

describe("dashboard statistics", () => {
  test("days start at midnight and weeks on Monday, in the given zone", () => {
    // Wednesday 2026-09-30 21:00 at UTC+9.
    expect(new Date(dayStart(clock.now, 540)).toISOString()).toBe("2026-09-29T15:00:00.000Z");
    expect(new Date(weekStart(clock.now, 540)).toISOString()).toBe("2026-09-27T15:00:00.000Z");
    expect(new Date(dayStart(clock.now, 0)).toISOString()).toBe("2026-09-30T00:00:00.000Z");
    expect(new Date(weekStart(clock.now, 0)).toISOString()).toBe("2026-09-28T00:00:00.000Z");
    expect(new Date(weekStart(ms("2026-09-28T00:00:00Z"), 0)).toISOString()).toBe(
      "2026-09-28T00:00:00.000Z",
    );
  });

  test("a period of days ends today and starts at midnight of its first day; all time has no start", () => {
    expect(new Date(statsWindow({ period: "7d" }, clock).start ?? 0).toISOString()).toBe(
      "2026-09-23T15:00:00.000Z",
    );
    expect(new Date(statsWindow({ period: "30d" }, clock).start ?? 0).toISOString()).toBe(
      "2026-08-31T15:00:00.000Z",
    );
    expect(statsWindow({ period: "all" }, clock)).toEqual({ start: null, end: clock.now });
    expect(statsWindow({ period: "all", since: 5 }, clock)).toEqual({ start: 5, end: clock.now });
  });

  test("the median and p90 lie between the nearest ranks", () => {
    expect(quantile([], 0.5)).toBeNull();
    expect(quantile([30, 60, 90, 120], 0.5)).toBe(75);
    expect(quantile([30, 60, 90, 120], 0.9)).toBeCloseTo(111);
    expect(quantile([7], 0.9)).toBe(7);
  });

  test("the metric tiles count the judged Outcomes, the process runs, and their usage in the period; wake runs never count", () => {
    const { stats: s } = stats();
    expect(s.window.start).toBe(ms("2026-09-23T15:00:00Z"));
    expect(s.metrics).toEqual({
      // i1: achieved, not achieved; i2: achieved, unverified. i6 was judged before the period.
      achievement: { numerator: 2, denominator: 4, value: 0.5 },
      // i4's run ended and awaits a judgment; i3's run was canceled, which awaits none.
      unverified: { numerator: 1, denominator: 4, value: 0.25, awaitingJudgment: 1 },
      // i1's evaluation is stale now.
      staleEvaluations: 1,
      // r1, r3, r7 succeeded and r2 failed; r6 is running, r4 is before the period, r5 wakes.
      runSuccess: { numerator: 3, denominator: 4, value: 0.75 },
      // r2 30 s, r1 60 s, r7 90 s, r3 120 s.
      duration: { medianMs: 75 * SECOND, p90Ms: 111 * SECOND },
      // r7 was recorded before the cached tokens were read, so only r1's count.
      usage: {
        costUsd: expect.closeTo(0.6, 10),
        inputTokens: 1500,
        cachedInputTokens: 600,
        outputTokens: 300,
        costPerAchievedOutcome: expect.closeTo(0.3, 10),
      },
    });
  });

  test("the trends have one bucket per day of the period, with run results, judgments, cost by agent, and durations", () => {
    const { stats: s } = stats();
    expect(s.trends.map((b) => new Date(b.start).toISOString())).toEqual([
      "2026-09-23T15:00:00.000Z",
      "2026-09-24T15:00:00.000Z",
      "2026-09-25T15:00:00.000Z",
      "2026-09-26T15:00:00.000Z",
      "2026-09-27T15:00:00.000Z",
      "2026-09-28T15:00:00.000Z",
      "2026-09-29T15:00:00.000Z",
    ]);
    const [empty, , , , , sep29, sep30] = s.trends;
    expect(empty).toEqual({
      start: ms("2026-09-23T15:00:00Z"),
      runs: { succeeded: 0, failed: 0, canceled: 0, interrupted: 0 },
      judgments: { achieved: 0, "not-achieved": 0, unverified: 0 },
      achievementRate: null,
      costByAgent: {},
      duration: { medianMs: null, p90Ms: null },
    });
    expect(sep29).toMatchObject({
      runs: { succeeded: 1, failed: 1, canceled: 0, interrupted: 0 },
      judgments: { achieved: 1, "not-achieved": 1, unverified: 0 },
      achievementRate: 0.5,
      costByAgent: { "claude-code": expect.closeTo(0.4, 10) },
      duration: { medianMs: 45 * SECOND, p90Ms: 57 * SECOND },
    });
    // r6 is running: it is in no run result yet.
    expect(sep30).toMatchObject({
      runs: { succeeded: 2, failed: 0, canceled: 0, interrupted: 0 },
      judgments: { achieved: 1, "not-achieved": 0, unverified: 1 },
      achievementRate: 0.5,
      costByAgent: { "claude-code": expect.closeTo(0.2, 10) },
      duration: { medianMs: 105 * SECOND, p90Ms: 117 * SECOND },
    });
  });

  test("weekly trends of all time start with the week of the first record", () => {
    const { stats: s } = stats({ period: "all", granularity: "week" });
    expect(s.trends).toHaveLength(10);
    expect(new Date(s.trends[0]!.start).toISOString()).toBe("2026-07-26T15:00:00.000Z");
    expect(new Date(s.trends.at(-1)!.start).toISOString()).toBe("2026-09-27T15:00:00.000Z");
    expect(s.trends[0]!.runs.succeeded).toBe(1);
    expect(s.trends[0]!.judgments.unverified).toBe(2);
    expect(s.metrics.achievement).toEqual({ numerator: 2, denominator: 6, value: 2 / 6 });
    expect(s.metrics.unverified).toMatchObject({ numerator: 3, denominator: 6 });
    expect(s.metrics.runSuccess).toEqual({ numerator: 4, denominator: 6, value: 4 / 6 });
  });

  test("the breakdown by Process follows the model, with the instances, runs, and judgments of each", () => {
    const { stats: s } = stats();
    expect(s.breakdowns.process).toEqual([
      {
        process: "Solution Design",
        instances: 2,
        runs: 3,
        runSuccess: { numerator: 2, denominator: 3, value: 2 / 3 },
        duration: { medianMs: 60 * SECOND, p90Ms: 84 * SECOND },
        achievement: { numerator: 1, denominator: 2, value: 0.5 },
        unverified: { numerator: 0, denominator: 2, value: 0 },
        costUsd: expect.closeTo(0.6, 10),
      },
      {
        process: "Change Implementation",
        instances: 0,
        runs: 0,
        runSuccess: { numerator: 0, denominator: 0, value: null },
        duration: { medianMs: null, p90Ms: null },
        achievement: { numerator: 0, denominator: 0, value: null },
        unverified: { numerator: 0, denominator: 0, value: null },
        costUsd: null,
      },
      {
        process: "Production Release",
        instances: 1,
        runs: 2,
        runSuccess: { numerator: 1, denominator: 1, value: 1 },
        duration: { medianMs: 120 * SECOND, p90Ms: 120 * SECOND },
        achievement: { numerator: 1, denominator: 2, value: 0.5 },
        unverified: { numerator: 1, denominator: 2, value: 0.5 },
        costUsd: null,
      },
    ]);
    // For all time, every instance counts, also one that never ran.
    const all = stats({ period: "all" }).stats.breakdowns.process;
    expect(all.map((p) => p.instances)).toEqual([2, 2, 2]);
  });

  test("the breakdown by agent counts its runs and the judgments of the runs it performed", () => {
    expect(stats().stats.breakdowns.agent).toEqual([
      {
        agent: "claude-code",
        runs: 3,
        runSuccess: { numerator: 2, denominator: 3, value: 2 / 3 },
        achievement: { numerator: 1, denominator: 2, value: 0.5 },
        costPerAchievedOutcome: expect.closeTo(0.6, 10),
        runsPerInstance: 1.5,
      },
      {
        agent: "codex",
        runs: 2,
        runSuccess: { numerator: 1, denominator: 1, value: 1 },
        achievement: { numerator: 1, denominator: 2, value: 0.5 },
        costPerAchievedOutcome: null,
        runsPerInstance: 2,
      },
    ]);
  });

  test("the breakdown by Outcome puts those judged but never achieved first, then those mostly unverified, then those never judged", () => {
    const rows = (filter: Partial<StatsFilter>) =>
      stats(filter).stats.breakdowns.outcome.map(
        (o) =>
          `${o.process} ${o.outcome}: ${o.counts.achieved}/${o.counts["not-achieved"]}/${o.counts.unverified}`,
      );
    expect(rows({})).toEqual([
      "Solution Design 1: 0/1/0",
      "Production Release 1: 0/0/1",
      "Change Implementation 0: 0/0/0",
      "Change Implementation 1: 0/0/0",
      "Solution Design 0: 1/0/0",
      "Production Release 0: 1/0/0",
    ]);
    // Over all time, Production Release's first Outcome is achieved once and unverified once: not a majority.
    expect(rows({ period: "all", process: "Production Release" })).toEqual([
      "Production Release 1: 0/0/2",
      "Production Release 0: 1/0/1",
    ]);
  });

  test("the breakdown by judge separates people, agents, and the performer's own judgments", () => {
    expect(stats().stats.breakdowns.judge).toEqual([
      { judge: "user", judgments: 2, achievement: { numerator: 1, denominator: 2, value: 0.5 } },
      { judge: "agent", judgments: 0, achievement: { numerator: 0, denominator: 0, value: null } },
      { judge: "self", judgments: 2, achievement: { numerator: 1, denominator: 2, value: 0.5 } },
    ]);
    expect(stats({ period: "all" }).stats.breakdowns.judge[1]).toMatchObject({
      judge: "agent",
      judgments: 2,
    });
  });

  test("an agent filter keeps its runs and the judgments of its runs; a Process filter keeps that Process", () => {
    const codex = stats({ period: "all", agent: "codex" });
    expect(codex.stats.metrics.achievement).toEqual({ numerator: 1, denominator: 4, value: 0.25 });
    expect(codex.stats.metrics.runSuccess).toEqual({ numerator: 2, denominator: 2, value: 1 });
    // i1 ran with claude-code; it is listed for its stale evaluation, which no agent filter narrows.
    expect(codex.members.instances.map((i) => i.id)).toEqual(["i1", "i2", "i6"]);
    expect(codex.stats.metrics.staleEvaluations).toBe(1);
    expect(codex.members.runs.map((r) => r.id)).toEqual(["r6", "r3", "r8"]);

    const design = stats({ period: "30d", process: "Solution Design" });
    expect(design.stats.metrics.runSuccess).toEqual({ numerator: 2, denominator: 3, value: 2 / 3 });
    expect(design.stats.metrics.unverified.awaitingJudgment).toBe(1);
    expect(design.stats.breakdowns.process.map((p) => p.process)).toEqual(["Solution Design"]);
  });

  test("since starts the window instead of the period", () => {
    const { stats: s } = stats({ period: "all", since: ms("2026-09-30T00:00:00Z") });
    expect(s.window.start).toBe(ms("2026-09-30T00:00:00Z"));
    expect(s.metrics.achievement).toEqual({ numerator: 1, denominator: 2, value: 0.5 });
    expect(s.metrics.runSuccess).toEqual({ numerator: 2, denominator: 2, value: 1 });
  });

  test("the stale evaluations are the state now, whatever the period; a Process filter applies, an agent filter does not", () => {
    // i6 was judged before the period, about a run of codex; its evidence is stale now, as i1's is.
    const now = (filter: Partial<StatsFilter>) =>
      computeStats(
        { ...input, stale: new Set(["i1", "i6"]) },
        { period: "7d", granularity: "day", ...filter },
        clock,
      );
    const week = now({});
    expect(week.stats.metrics.staleEvaluations).toBe(2);
    // The judgments that count are still those made in the period.
    expect(week.stats.metrics.achievement).toEqual({ numerator: 2, denominator: 4, value: 0.5 });
    // The instances that the number counts are listed, and i6 is in scope for its Process.
    expect(week.members.instances.filter((i) => i.stale)).toEqual([
      { id: "i1", process: "Solution Design", judged: true, awaiting: false, stale: true },
      { id: "i6", process: "Production Release", judged: false, awaiting: false, stale: true },
    ]);
    expect(week.stats.breakdowns.process.map((p) => p.instances)).toEqual([2, 0, 2]);

    expect(now({ period: "all" }).stats.metrics.staleEvaluations).toBe(2);
    // No judgment is made since now, and both evaluations are still stale.
    expect(now({ since: clock.now }).stats.metrics.staleEvaluations).toBe(2);
    expect(now({ process: "Production Release" }).stats.metrics.staleEvaluations).toBe(1);
    expect(now({ agent: "claude-code" }).stats.metrics.staleEvaluations).toBe(2);
  });

  test("the members are what the numbers count: instances with the numbers they are in, and runs newest first", () => {
    const { members } = stats();
    expect(members.instances).toEqual([
      { id: "i1", process: "Solution Design", judged: true, awaiting: false, stale: true },
      { id: "i2", process: "Production Release", judged: true, awaiting: false, stale: false },
      { id: "i4", process: "Solution Design", judged: false, awaiting: true, stale: false },
    ]);
    expect(members.runs.map((r) => r.id)).toEqual(["r6", "r7", "r3", "r2", "r1"]);
    expect(members.runs[1]).toEqual({
      id: "r7",
      instance: "i4",
      process: "Solution Design",
      agent: "claude-code",
      status: "succeeded",
      startedAt: ms("2026-09-30T06:00:00Z"),
      endedAt: ms("2026-09-30T06:01:30Z"),
      costUsd: 0.2,
    });
  });
});

describe("assessment findings", () => {
  const process = (overrides: Partial<ProcessView>): ProcessView => ({
    id: "P",
    name: "P",
    purpose: "",
    outcomes: ["O"],
    constraints: [],
    enablers: [],
    inputs: [],
    controls: [],
    outputs: [],
    skill: null,
    ...overrides,
  });
  const skill = (path: string) => ({
    path,
    dir: path.replace(/\/SKILL\.md$/, ""),
    name: "s",
    description: "",
    titles: [],
    translations: [],
  });
  const type = (id: string, paths = [`docs/${id}.md`]): ArtifactType => ({
    id,
    name: id,
    description: "",
    kind: "information",
    paths,
  });
  const agent = (id: string, available: boolean): AgentInfo => ({
    id,
    label: id,
    available,
    version: null,
    reason: available ? null : "the command was not found",
  });
  const fact = (overrides: Partial<InstanceFacts>): InstanceFacts => ({
    instance: "i1",
    process: "Design",
    latestRun: null,
    judgments: null,
    evaluatedRun: null,
    stale: false,
    staleness: [],
    ...overrides,
  });

  const input: FindingsInput = {
    processes: [
      process({
        id: "Design",
        name: "Design",
        inputs: ["Brief"],
        outputs: ["Design doc"],
        skill: skill("skills/design/SKILL.md"),
      }),
      process({ id: "Build", name: "Build", inputs: ["Design doc"], outputs: ["Build log"] }),
      process({
        id: "Check",
        name: "Check",
        controls: ["Criteria"],
        skill: { missing: "skills/check" },
      }),
    ],
    artifacts: [
      type("Brief"),
      type("Design doc"),
      type("Build log", []),
      type("Criteria"),
      type("Loose"),
    ],
    agents: [agent("claude-code", false), agent("demo", true)],
    facts: [
      fact({
        instance: "i1",
        latestRun: {
          id: "r2",
          kind: "process",
          instance: "i1",
          status: "succeeded",
          startedAt: 1,
          endedAt: 2,
        },
        judgments: [{ outcome: 0, judgment: "achieved", evidence: "Read it." }],
        evaluatedRun: "r1",
        stale: true,
        staleness: [{ kind: "input", type: "Brief", path: "docs/Brief.md", change: "modified" }],
      }),
    ],
    lastSkillUse: new Map([["Design", { run: "r2", path: "skills/design/SKILL.md", sha256: "a" }]]),
    skillNow: new Map([["Design", "b"]]),
  };

  test("the findings name configuration problems, then description problems, then what is unverified", () => {
    const findings = findingsOf(input);
    expect(findings.map((f) => `${f.kind} ${f.key}`)).toEqual([
      "configuration finding.noSkill",
      "configuration finding.skillMissing",
      "configuration finding.noLocation",
      "configuration finding.agentUnavailable",
      "description finding.notProduced",
      "description finding.notRead",
      "description finding.notProduced",
      "description finding.unused",
      "unverified finding.skillChanged",
      "unverified finding.awaiting",
      "unverified finding.stale",
    ]);
    expect(findings.find((f) => f.key === "finding.notRead")).toMatchObject({
      subject: { artifact: "Build log" },
      message: "No Process reads Build log (produced by Build).",
      evidence: ["Build"],
    });
    expect(findings.find((f) => f.key === "finding.skillChanged")).toMatchObject({
      subject: { process: "Design" },
      args: { process: "Design", run: "r2", path: "skills/design/SKILL.md" },
      evidence: ["skills/design/SKILL.md", "r2"],
    });
    expect(findings.find((f) => f.key === "finding.agentUnavailable")).toMatchObject({
      subject: { agent: "claude-code" },
      message: "claude-code cannot be started: the command was not found.",
      evidence: ["claude-code"],
    });
  });

  test("a SKILL.md that the last run used as it is now is no finding", () => {
    const same = findingsOf({ ...input, skillNow: new Map([["Design", "a"]]) });
    expect(same.some((f) => f.key === "finding.skillChanged")).toBe(false);
  });
});
