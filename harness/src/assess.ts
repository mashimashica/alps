/*
 * The dashboard's statistics and the assessment's findings. Both are pure functions of the
 * records (instances and runs), the model, and what the workspace holds now, which the harness
 * gives as facts and digests. The dashboard only draws what they return, and nothing here judges
 * an Outcome: only the three-valued judgments that people and agents recorded are counted.
 *
 * What counts (the statistics' window, `Stats.window`):
 * - process runs that started in the window; wake runs are not process runs and never count;
 * - the judgments of the evaluations made in the window (an instance keeps its latest evaluation);
 * - with a Process, the runs and judgments of its instances; with an agent, its runs and the
 *   judgments about the runs it performed.
 * The stale evaluations are the state now, whatever the window, as the WebUI's count at the top
 * right: a Process filter keeps its instances, and an agent filter does not apply, since whether
 * the evidence is stale depends on what the workspace holds, not on who ran.
 */

import { say, type MessageArgs, type MessageKey } from "./shared/strings.ts";
import type {
  AgentBreakdown,
  AgentId,
  AgentInfo,
  ArtifactType,
  DurationStats,
  Finding,
  Granularity,
  Instance,
  InstanceFacts,
  Judgment,
  JudgeBreakdown,
  OutcomeBreakdown,
  Period,
  ProcessBreakdown,
  ProcessView,
  Ratio,
  Run,
  RunStatus,
  Stats,
  StatsFilter,
  StatsInstance,
  StatsMembers,
  StatsRun,
  TrendBucket,
} from "./shared/types.ts";

const MINUTE_MS = 60_000;
const DAY_MS = 86_400_000;
const PERIOD_DAYS: Record<Exclude<Period, "all">, number> = { "7d": 7, "30d": 30, "90d": 90 };

/** The fields of a run record that the statistics read. */
export type StatsRunRecord = Pick<
  Run,
  "id" | "kind" | "instance" | "process" | "agent" | "status" | "startedAt" | "endedAt" | "usage"
>;

/** What the statistics are computed from. */
export interface StatsInput {
  /** The model's Processes, in the model's order, with their Outcomes. */
  processes: readonly { id: string; outcomes: readonly string[] }[];
  instances: readonly Instance[];
  runs: readonly StatsRunRecord[];
  /** The instances whose evaluation no longer rests on what the workspace holds (facts.stale). */
  stale: ReadonlySet<string>;
}

export interface StatsClock {
  now: number;
  /** Minutes east of UTC: where days and weeks (from Monday) start. */
  utcOffsetMinutes: number;
}

/* ---------- time ---------- */

/** The start of the day that holds `t`, at `offset` minutes east of UTC. */
export function dayStart(t: number, offset: number): number {
  const shift = offset * MINUTE_MS;
  return Math.floor((t + shift) / DAY_MS) * DAY_MS - shift;
}

/** The start of the week (from Monday) that holds `t`, at `offset` minutes east of UTC. */
export function weekStart(t: number, offset: number): number {
  const day = dayStart(t, offset);
  // Day 0 of the epoch (1970-01-01) was a Thursday: 3 days after a Monday.
  const days = Math.round((day + offset * MINUTE_MS) / DAY_MS);
  const sinceMonday = (((days + 3) % 7) + 7) % 7;
  return day - sinceMonday * DAY_MS;
}

/**
 * The window of the statistics: from `since`, from midnight of the period's first day (the period
 * ends today, today included), or from the beginning (`start: null`), until now.
 */
export function statsWindow(
  filter: Pick<StatsFilter, "period" | "since">,
  clock: StatsClock,
): { start: number | null; end: number } {
  if (filter.since !== undefined) return { start: filter.since, end: clock.now };
  if (filter.period === "all") return { start: null, end: clock.now };
  const days = PERIOD_DAYS[filter.period];
  return {
    start: dayStart(clock.now, clock.utcOffsetMinutes) - (days - 1) * DAY_MS,
    end: clock.now,
  };
}

/* ---------- numbers ---------- */

/** A share; `value` is `null` when there is nothing to divide by. */
export const ratio = (numerator: number, denominator: number): Ratio => ({
  numerator,
  denominator,
  value: denominator === 0 ? null : numerator / denominator,
});

/** The `q` quantile of sorted numbers, between the two nearest ranks; `null` for none. */
export function quantile(sorted: readonly number[], q: number): number | null {
  if (sorted.length === 0) return null;
  const at = (sorted.length - 1) * q;
  const low = sorted[Math.floor(at)] ?? 0;
  const high = sorted[Math.ceil(at)] ?? low;
  return low + (high - low) * (at - Math.floor(at));
}

/**
 * The median and p90 of how long runs took, from start to end. Only runs that ended by
 * themselves (succeeded or failed) count: a canceled or interrupted run says how long someone
 * waited, not how long the work took.
 */
export function durationOf(runs: readonly StatsRunRecord[]): DurationStats {
  const taken = runs
    .filter((r) => (r.status === "succeeded" || r.status === "failed") && r.endedAt !== null)
    .map((r) => Math.max(0, (r.endedAt ?? r.startedAt) - r.startedAt))
    .sort((a, b) => a - b);
  return { medianMs: quantile(taken, 0.5), p90Ms: quantile(taken, 0.9) };
}

/** The sum of the values that are known; `null` when none is. */
function sumKnown(values: Iterable<number | null | undefined>): number | null {
  let total = 0;
  let known = false;
  for (const value of values) {
    if (value === null || value === undefined) continue;
    total += value;
    known = true;
  }
  return known ? total : null;
}

const perAchieved = (cost: number | null, achieved: number): number | null =>
  cost === null || achieved === 0 ? null : cost / achieved;

const runSuccess = (runs: readonly StatsRunRecord[]): Ratio => {
  const ended = runs.filter((r) => r.status !== "running");
  return ratio(ended.filter((r) => r.status === "succeeded").length, ended.length);
};

/* ---------- statistics ---------- */

type JudgeKind = JudgeBreakdown["judge"];

/** One judged Outcome that counts. */
interface Counted {
  instance: string;
  process: string;
  outcome: number;
  judgment: Judgment;
  judge: JudgeKind;
  at: number;
  /** The agent that performed the judged run, if its record is there. */
  agent: AgentId | null;
}

const achievementOf = (judgments: readonly Counted[]): Ratio =>
  ratio(judgments.filter((j) => j.judgment === "achieved").length, judgments.length);

const unverifiedOf = (judgments: readonly Counted[]): Ratio =>
  ratio(judgments.filter((j) => j.judgment === "unverified").length, judgments.length);

const emptyRuns = (): Record<Exclude<RunStatus, "running">, number> => ({
  succeeded: 0,
  failed: 0,
  canceled: 0,
  interrupted: 0,
});

const emptyJudgments = (): Record<Judgment, number> => ({
  achieved: 0,
  "not-achieved": 0,
  unverified: 0,
});

/** Outcomes that were judged but never achieved come first, then those mostly unverified, then those never judged. */
function outcomeRank({ counts }: OutcomeBreakdown): number {
  const total = counts.achieved + counts["not-achieved"] + counts.unverified;
  if (total > 0 && counts.achieved === 0) return 0;
  if (total > 0 && counts.unverified * 2 > total) return 1;
  if (total === 0) return 2;
  return 3;
}

/**
 * The statistics of the dashboard and the assessment for a filter, with what each number counts
 * (`members`, which the WebUI lists when a number is clicked).
 */
export function computeStats(
  input: StatsInput,
  filter: StatsFilter,
  clock: StatsClock,
): { stats: Stats; members: StatsMembers } {
  const window = statsWindow(filter, clock);
  const inWindow = (t: number): boolean => window.start === null || t >= window.start;
  const byId = new Map(input.runs.map((run) => [run.id, run]));
  const ofProcess = (process: string | null): boolean =>
    filter.process === undefined || process === filter.process;
  const ofAgent = (agent: AgentId | null | undefined): boolean =>
    filter.agent === undefined || agent === filter.agent;

  // The process runs that started in the window.
  const runs = input.runs.filter(
    (r) =>
      r.kind === "process" && ofProcess(r.process) && ofAgent(r.agent) && inWindow(r.startedAt),
  );

  // The judgments of the evaluations made in the window.
  const judgedInstances = input.instances.filter(
    (i) =>
      i.evaluation !== null &&
      ofProcess(i.process) &&
      ofAgent(byId.get(i.evaluation.runId)?.agent) &&
      inWindow(i.evaluation.at),
  );
  const judgments: Counted[] = judgedInstances.flatMap((instance) => {
    const evaluation = instance.evaluation;
    if (!evaluation) return [];
    const judge: JudgeKind =
      evaluation.by.kind === "user" ? "user" : evaluation.by.self ? "self" : "agent";
    const agent = byId.get(evaluation.runId)?.agent ?? null;
    return evaluation.judgments.map((j) => ({
      instance: instance.id,
      process: instance.process,
      outcome: j.outcome,
      judgment: j.judgment,
      judge,
      at: evaluation.at,
      agent,
    }));
  });

  // Instances whose latest run ended in the window and has no judgment yet.
  const awaiting = new Set<string>();
  for (const instance of input.instances) {
    const latest = byId.get(instance.runs.at(-1) ?? "");
    if (
      latest &&
      latest.kind === "process" &&
      (latest.status === "succeeded" || latest.status === "failed") &&
      latest.endedAt !== null &&
      inWindow(latest.endedAt) &&
      ofProcess(instance.process) &&
      ofAgent(latest.agent) &&
      instance.evaluation?.runId !== latest.id
    )
      awaiting.add(instance.id);
  }
  const judged = new Set(judgedInstances.map((i) => i.id));
  // The evaluations whose evidence is stale now, whatever the window and the agent.
  const stale = new Set(
    input.instances
      .filter((i) => i.evaluation !== null && ofProcess(i.process) && input.stale.has(i.id))
      .map((i) => i.id),
  );

  // The instances in scope: those that the numbers count, and every instance for all time.
  const inScope = new Set<string>([...judged, ...awaiting, ...stale]);
  for (const run of runs) if (run.instance) inScope.add(run.instance);
  if (window.start === null && filter.agent === undefined)
    for (const instance of input.instances)
      if (ofProcess(instance.process)) inScope.add(instance.id);
  const instances = input.instances.filter((i) => inScope.has(i.id));

  const achieved = judgments.filter((j) => j.judgment === "achieved").length;
  const cost = sumKnown(runs.map((r) => r.usage?.costUsd));
  const metrics: Stats["metrics"] = {
    achievement: achievementOf(judgments),
    unverified: { ...unverifiedOf(judgments), awaitingJudgment: awaiting.size },
    staleEvaluations: stale.size,
    runSuccess: runSuccess(runs),
    duration: durationOf(runs),
    usage: {
      costUsd: cost,
      inputTokens: sumKnown(runs.map((r) => r.usage?.inputTokens)),
      outputTokens: sumKnown(runs.map((r) => r.usage?.outputTokens)),
      costPerAchievedOutcome: perAchieved(cost, achieved),
    },
  };

  return {
    stats: {
      filter: { ...filter },
      window,
      metrics,
      trends: trendsOf(runs, judgments, filter.granularity, window.start, clock),
      breakdowns: {
        process: processBreakdown(input, instances, runs, judgments, filter),
        agent: agentBreakdown(runs, judgments),
        outcome: outcomeBreakdown(input, judgments, filter),
        judge: (["user", "agent", "self"] as const).map((judge) => {
          const own = judgments.filter((j) => j.judge === judge);
          return { judge, judgments: own.length, achievement: achievementOf(own) };
        }),
      },
    },
    members: {
      instances: instances.map((i): StatsInstance => ({
        id: i.id,
        process: i.process,
        judged: judged.has(i.id),
        awaiting: awaiting.has(i.id),
        stale: stale.has(i.id),
      })),
      runs: [...runs]
        .sort((a, b) => b.startedAt - a.startedAt)
        .map((r): StatsRun => ({
          id: r.id,
          instance: r.instance,
          process: r.process,
          agent: r.agent,
          status: r.status,
          startedAt: r.startedAt,
          endedAt: r.endedAt,
          costUsd: r.usage?.costUsd ?? null,
        })),
    },
  };
}

/** The buckets of the trends: every day or week from the window's start (or the first record) to now. */
function trendsOf(
  runs: readonly StatsRunRecord[],
  judgments: readonly Counted[],
  granularity: Granularity,
  start: number | null,
  clock: StatsClock,
): TrendBucket[] {
  const offset = clock.utcOffsetMinutes;
  const bucketOf = (t: number): number =>
    granularity === "day" ? dayStart(t, offset) : weekStart(t, offset);
  const step = granularity === "day" ? DAY_MS : 7 * DAY_MS;
  let earliest = clock.now;
  let latest = clock.now;
  for (const t of [...runs.map((r) => r.startedAt), ...judgments.map((j) => j.at)]) {
    earliest = Math.min(earliest, t);
    latest = Math.max(latest, t);
  }
  const first = bucketOf(start ?? earliest);
  const last = bucketOf(latest);

  interface Acc {
    runs: StatsRunRecord[];
    judgments: Counted[];
  }
  const buckets = new Map<number, Acc>();
  for (let t = first; t <= last; t += step) buckets.set(t, { runs: [], judgments: [] });
  for (const run of runs) buckets.get(bucketOf(run.startedAt))?.runs.push(run);
  for (const judgment of judgments) buckets.get(bucketOf(judgment.at))?.judgments.push(judgment);

  return [...buckets].map(([bucketStart, acc]) => {
    const byStatus = emptyRuns();
    for (const run of acc.runs) if (run.status !== "running") byStatus[run.status] += 1;
    const byJudgment = emptyJudgments();
    for (const judgment of acc.judgments) byJudgment[judgment.judgment] += 1;
    const costByAgent: Record<string, number> = {};
    for (const run of acc.runs) {
      const cost = run.usage?.costUsd;
      if (cost !== null && cost !== undefined)
        costByAgent[run.agent] = (costByAgent[run.agent] ?? 0) + cost;
    }
    return {
      start: bucketStart,
      runs: byStatus,
      judgments: byJudgment,
      achievementRate: achievementOf(acc.judgments).value,
      costByAgent,
      duration: durationOf(acc.runs),
    };
  });
}

function processBreakdown(
  input: StatsInput,
  instances: readonly Instance[],
  runs: readonly StatsRunRecord[],
  judgments: readonly Counted[],
  filter: StatsFilter,
): ProcessBreakdown[] {
  const ids = input.processes.map((p) => p.id);
  // Records of Processes that the model no longer has come after the model's.
  const extra = [
    ...instances.map((i) => i.process),
    ...runs.flatMap((r) => (r.process ? [r.process] : [])),
  ];
  for (const id of extra) if (!ids.includes(id)) ids.push(id);
  return ids
    .filter((id) => filter.process === undefined || id === filter.process)
    .map((process) => {
      const own = runs.filter((r) => r.process === process);
      const judged = judgments.filter((j) => j.process === process);
      return {
        process,
        instances: instances.filter((i) => i.process === process).length,
        runs: own.length,
        runSuccess: runSuccess(own),
        duration: durationOf(own),
        achievement: achievementOf(judged),
        unverified: unverifiedOf(judged),
        costUsd: sumKnown(own.map((r) => r.usage?.costUsd)),
      };
    });
}

function agentBreakdown(
  runs: readonly StatsRunRecord[],
  judgments: readonly Counted[],
): AgentBreakdown[] {
  const agents = new Set<AgentId>(runs.map((r) => r.agent));
  for (const judgment of judgments) if (judgment.agent !== null) agents.add(judgment.agent);
  return [...agents]
    .map((agent) => {
      const own = runs.filter((r) => r.agent === agent);
      const judged = judgments.filter((j) => j.agent === agent);
      const achieved = judged.filter((j) => j.judgment === "achieved").length;
      const instances = new Set(own.flatMap((r) => (r.instance ? [r.instance] : []))).size;
      return {
        agent,
        runs: own.length,
        runSuccess: runSuccess(own),
        achievement: achievementOf(judged),
        costPerAchievedOutcome: perAchieved(sumKnown(own.map((r) => r.usage?.costUsd)), achieved),
        runsPerInstance: instances === 0 ? null : own.length / instances,
      };
    })
    .sort((a, b) => b.runs - a.runs || a.agent.localeCompare(b.agent));
}

function outcomeBreakdown(
  input: StatsInput,
  judgments: readonly Counted[],
  filter: StatsFilter,
): OutcomeBreakdown[] {
  const rows = new Map<string, OutcomeBreakdown>();
  const row = (process: string, outcome: number): OutcomeBreakdown => {
    const key = `${process}\u0000${outcome}`;
    let found = rows.get(key);
    if (!found) {
      found = { process, outcome, counts: emptyJudgments() };
      rows.set(key, found);
    }
    return found;
  };
  for (const process of input.processes)
    if (filter.process === undefined || process.id === filter.process)
      process.outcomes.forEach((_, outcome) => row(process.id, outcome));
  for (const judgment of judgments)
    row(judgment.process, judgment.outcome).counts[judgment.judgment] += 1;
  // A stable sort keeps the model's order within each rank.
  return [...rows.values()].sort((a, b) => outcomeRank(a) - outcomeRank(b));
}

/* ---------- findings ---------- */

/** What the findings are drawn from. */
export interface FindingsInput {
  processes: readonly ProcessView[];
  artifacts: readonly ArtifactType[];
  agents: readonly AgentInfo[];
  facts: readonly InstanceFacts[];
  /** The SKILL.md that the latest process run of each Process used, by Process id. */
  lastSkillUse: ReadonlyMap<string, { run: string; path: string; sha256: string | null }>;
  /** The digest of each Process's SKILL.md now, by Process id (`null`: it cannot be read). */
  skillNow: ReadonlyMap<string, string | null>;
}

/** A message in English with its key and arguments. */
const said = <K extends MessageKey>(key: K, args: MessageArgs<K>) => ({
  message: say("en", key, args),
  key,
  args: args as Record<string, string | number | boolean>,
});

/**
 * The findings: problems of the configuration (a Skill that is not found, a type without a
 * location, an agent that cannot be started), of the description (a type that no Process produces
 * or reads), and what is unverified (a SKILL.md that changed after the last run, results that
 * await a judgment, judgments whose evidence is stale).
 */
export function findingsOf(input: FindingsInput): Finding[] {
  const configuration: Finding[] = [];
  const description: Finding[] = [];
  const unverified: Finding[] = [];
  const names = (list: readonly ProcessView[]): string => list.map((p) => p.name).join(", ");

  for (const process of input.processes) {
    const skill = process.skill;
    if (skill && "missing" in skill)
      configuration.push({
        kind: "configuration",
        subject: { process: process.id },
        ...said("finding.skillMissing", { process: process.name, location: skill.missing }),
        evidence: [skill.missing],
      });
    else if (!skill)
      configuration.push({
        kind: "configuration",
        subject: { process: process.id },
        ...said("finding.noSkill", { process: process.name }),
        evidence: [],
      });
    else {
      const used = input.lastSkillUse.get(process.id);
      const now = input.skillNow.get(process.id) ?? null;
      if (used && used.sha256 !== null && (used.path !== skill.path || used.sha256 !== now))
        unverified.push({
          kind: "unverified",
          subject: { process: process.id },
          ...said("finding.skillChanged", {
            process: process.name,
            run: used.run,
            path: skill.path,
          }),
          evidence: [skill.path, used.run],
        });
    }
  }

  for (const type of input.artifacts) {
    if (type.paths.length === 0)
      configuration.push({
        kind: "configuration",
        subject: { artifact: type.id },
        ...said("finding.noLocation", { type: type.name }),
        evidence: [],
      });
    const producers = input.processes.filter((p) => p.outputs.includes(type.id));
    const consumers = input.processes.filter(
      (p) => p.inputs.includes(type.id) || p.controls.includes(type.id),
    );
    const subject = { artifact: type.id };
    if (producers.length === 0 && consumers.length === 0)
      description.push({
        kind: "description",
        subject,
        ...said("finding.unused", { type: type.name }),
        evidence: [],
      });
    else if (producers.length === 0)
      description.push({
        kind: "description",
        subject,
        ...said("finding.notProduced", { type: type.name, consumers: names(consumers) }),
        evidence: consumers.map((p) => p.id),
      });
    else if (consumers.length === 0)
      description.push({
        kind: "description",
        subject,
        ...said("finding.notRead", { type: type.name, producers: names(producers) }),
        evidence: producers.map((p) => p.id),
      });
  }

  for (const agent of input.agents)
    if (!agent.available)
      configuration.push({
        kind: "configuration",
        subject: { agent: agent.id },
        ...said("finding.agentUnavailable", {
          agent: agent.label,
          reason: agent.reason ?? "it is not available",
        }),
        evidence: [agent.id],
      });

  for (const fact of input.facts) {
    const latest = fact.latestRun;
    const subject = { instance: fact.instance, process: fact.process };
    if (
      latest &&
      (latest.status === "succeeded" || latest.status === "failed") &&
      fact.evaluatedRun !== latest.id
    )
      unverified.push({
        kind: "unverified",
        subject,
        ...said("finding.awaiting", { run: latest.id, status: latest.status }),
        evidence: [latest.id],
      });
    if (fact.stale) {
      const paths = fact.staleness.map((reason) => reason.path ?? "SKILL.md");
      unverified.push({
        kind: "unverified",
        subject,
        ...said("finding.stale", { run: fact.evaluatedRun ?? "", paths: paths.join(", ") }),
        evidence: paths,
      });
    }
  }
  return [...configuration, ...description, ...unverified];
}
