/*
 * The analysis. On top, the latest assessment: an agent's interpretation of the records
 * (views/assessment.tsx). Below it, what the harness observes: what the statistics of GET
 * /api/stats say for a period, a granularity, a Process, and an agent. The metric tiles (each with
 * the trend of its buckets), then the runs and their results beside the period's judgments (a
 * donut of achieved, not achieved, and unverified, counted in its legend; its centre is empty,
 * since the total is the tile's), the other trends, a breakdown table whose cut can be switched,
 * and the checks (the findings of GET /api/assessment), those of the filter's Process, of the
 * instances that its numbers count, and of its agent, with their evidence as links. Each number is
 * shown once; a tile's line under the value is its count, and what a number means is in its
 * title. A click on a number lists, in the panel, the instances or the runs it counts. The filter
 * is kept in the URL's fragment, so that a reload and a cut that an assessment cites show the same
 * numbers. The page draws the numbers; it judges nothing.
 */

import type { ComponentChildren } from "preact";
import { useEffect, useState } from "preact/hooks";
import { sayReceived } from "../../shared/strings.ts";
import type {
  Artifact,
  ArtifactsResponse,
  AssessmentResponse,
  AssessmentsResponse,
  Finding,
  FindingKind,
  Granularity,
  Period,
  Ratio,
  StatCut,
  Stats,
  StatsResponse,
  StatsRun,
  TrendBucket,
} from "../../shared/types.ts";
import { describeError, query } from "../api.ts";
import { Badge, type Tone } from "../components/badge.tsx";
import { Button } from "../components/button.tsx";
import { Card, CardHeader } from "../components/card.tsx";
import { Alert, Empty, Skeleton } from "../components/feedback.tsx";
import { Icon, type IconName } from "../components/icons.tsx";
import { Field } from "../components/input.tsx";
import { Select } from "../components/select.tsx";
import { rowActions, Table } from "../components/table.tsx";
import { tabPanel, Tabs } from "../components/tabs.tsx";
import { cx } from "../components/util.ts";
import { useUi, type Ui } from "../context.ts";
import { count, dateTime, duration, money, percent, shortDate } from "../format.ts";
import {
  AssessmentSection,
  EvidenceChip,
  type AssessmentData,
  type Loaded,
} from "./assessment.tsx";
import { Legend, Lines, Sparkline, StackedBars, Whiskers, type SeriesStyle } from "./charts.tsx";
import {
  InstanceLink,
  ModelProblem,
  processName,
  ProcessLink,
  scrollUnderHeader,
  TypeLink,
} from "./common.tsx";

interface Filter {
  period: Period;
  granularity: Granularity;
  process: string;
  agent: string;
}

type Cut = "process" | "agent" | "outcome" | "judge";

/** The filter and the cut stay as they were while the page is open (and in the URL's fragment). */
let kept: { filter: Filter; cut: Cut } = {
  filter: { period: "30d", granularity: "day", process: "", agent: "" },
  cut: "process",
};

const PERIODS: Period[] = ["7d", "30d", "90d", "all"];
const GRANULARITIES: Granularity[] = ["day", "week"];
const CUTS: Cut[] = ["process", "agent", "outcome", "judge"];
/** The keys of the analysis's state in the URL's fragment. */
const HASH_KEYS = ["period", "granularity", "process", "agent", "cut"] as const;

/** The filter and the cut that the URL's fragment holds, over what the page kept. */
function fromHash(): { filter: Filter; cut: Cut } {
  const params = new URLSearchParams(location.hash.slice(1));
  const one = <T extends string>(key: string, allowed: readonly T[], fallback: T): T => {
    const value = params.get(key);
    return value !== null && (allowed as readonly string[]).includes(value)
      ? (value as T)
      : fallback;
  };
  return {
    filter: {
      period: one("period", PERIODS, kept.filter.period),
      granularity: one("granularity", GRANULARITIES, kept.filter.granularity),
      process: params.get("process") ?? kept.filter.process,
      agent: params.get("agent") ?? kept.filter.agent,
    },
    cut: one("cut", CUTS, kept.cut),
  };
}

/** Puts the filter and the cut in the URL's fragment, or, with `null`, takes them out. */
function writeHash(state: { filter: Filter; cut: Cut } | null): void {
  const params = new URLSearchParams(location.hash.slice(1));
  for (const key of HASH_KEYS) params.delete(key);
  if (state) {
    const { filter, cut } = state;
    params.set("period", filter.period);
    params.set("granularity", filter.granularity);
    if (filter.process) params.set("process", filter.process);
    if (filter.agent) params.set("agent", filter.agent);
    params.set("cut", cut);
  }
  const text = params.toString();
  history.replaceState(
    history.state,
    "",
    `${location.pathname}${location.search}${text ? `#${text}` : ""}`,
  );
}
const AGENT_CLASSES = ["a0", "a1", "a2", "a3", "a4"];
/** How many findings show before "Show all". */
const FINDINGS_SHOWN = 6;

function Meter({ share }: { share: number | null }) {
  return (
    <span class="meter" aria-hidden="true">
      <span class="meter-fill" style={{ width: `${Math.round((share ?? 0) * 100)}%` }} />
    </span>
  );
}

function RatioCell({ share }: { share: Ratio }) {
  return (
    <td class="num">
      <span class="ratio">
        <span>{share.value === null ? "—" : `${percent(share.value)}%`}</span>
        <Meter share={share.value} />
      </span>
    </td>
  );
}

function Tile({
  label,
  value,
  unit,
  sub,
  hint,
  icon,
  tone,
  spark,
  onPick,
  testid,
}: {
  label: string;
  value: string;
  unit?: string;
  /** The count under the value; empty when the value says it all. */
  sub: string;
  /** What the number means, in the title. */
  hint?: string;
  icon: IconName;
  tone?: "primary" | "stale";
  spark: ComponentChildren;
  onPick: () => void;
  testid: string;
}) {
  return (
    <button
      type="button"
      class={cx("tile", tone && `tile-${tone}`)}
      data-testid={testid}
      title={hint}
      onClick={onPick}
    >
      <span class="tile-top">
        <span class="tile-label">{label}</span>
        <span class="tile-icon" aria-hidden="true">
          <Icon name={icon} size={15} />
        </span>
      </span>
      <span class="tile-middle">
        <span class="tile-value">
          {value}
          {unit && value !== "—" && <span class="tile-unit">{unit}</span>}
        </span>
        {spark}
      </span>
      <span class="tile-bottom">
        <span class="tile-sub">{sub}</span>
        <Icon name="arrowUpRight" class="tile-arrow" size={14} />
      </span>
    </button>
  );
}

/** Lists what a number counts in the panel. */
function members(
  ui: Ui,
  title: string,
  subtitle: string,
  instances: string[],
  runs: StatsRun[],
): void {
  ui.select({ kind: "members", title, subtitle, instances, runs });
}

function windowText(ui: Ui, stats: Stats): string {
  return stats.window.start === null
    ? ui.t("members.allTime")
    : ui.t("members.since", { from: dateTime(stats.window.start, ui.language) });
}

const judgedTotal = (b: TrendBucket): number =>
  b.judgments.achieved + b.judgments["not-achieved"] + b.judgments.unverified;
const endedTotal = (b: TrendBucket): number =>
  b.runs.succeeded + b.runs.failed + b.runs.canceled + b.runs.interrupted;

function Tiles({ answer, secondary = false }: { answer: StatsResponse; secondary?: boolean }) {
  const ui = useUi();
  const { t, language } = ui;
  const { metrics, trends } = answer.stats;
  const within = windowText(ui, answer.stats);
  const judged = answer.members.instances.filter((i) => i.judged).map((i) => i.id);
  const ended = answer.members.runs.filter(
    (r) => r.status === "succeeded" || r.status === "failed",
  );
  const usage = metrics.usage;
  return (
    <div class={secondary ? "tiles tiles-secondary" : "tiles"}>
      {[
        <Tile
          key="metric-achievement"
          testid="metric-achievement"
          tone="primary"
          icon="target"
          label={t("metric.achievement")}
          value={percent(metrics.achievement.value)}
          unit="%"
          sub={t("metric.judged", {
            n: metrics.achievement.numerator,
            d: metrics.achievement.denominator,
          })}
          spark={<Sparkline values={trends.map((b) => b.achievementRate)} tone="spark-achieved" />}
          onPick={() => members(ui, t("metric.achievement"), within, judged, [])}
        />,
        <Tile
          key="metric-run-success"
          testid="metric-run-success"
          icon="activity"
          label={t("metric.runSuccess")}
          value={percent(metrics.runSuccess.value)}
          unit="%"
          sub={t("metric.ended", {
            n: metrics.runSuccess.numerator,
            d: metrics.runSuccess.denominator,
          })}
          spark={
            <Sparkline
              values={trends.map((b) => (endedTotal(b) ? b.runs.succeeded / endedTotal(b) : null))}
              tone="spark-succeeded"
            />
          }
          onPick={() => members(ui, t("metric.runSuccess"), within, [], answer.members.runs)}
        />,
        <Tile
          key="metric-unverified"
          testid="metric-unverified"
          icon="help"
          label={t("metric.unverified")}
          value={percent(metrics.unverified.value)}
          unit="%"
          sub={t("metric.awaiting", { n: metrics.unverified.awaitingJudgment })}
          spark={
            <Sparkline
              values={trends.map((b) =>
                judgedTotal(b) ? b.judgments.unverified / judgedTotal(b) : null,
              )}
              tone="spark-unverified"
            />
          }
          onPick={() =>
            members(
              ui,
              t("metric.unverified"),
              within,
              answer.members.instances
                .filter(
                  (i) =>
                    i.awaiting ||
                    (i.judged &&
                      ui.instances
                        .get(i.id)
                        ?.evaluation?.judgments.some((j) => j.judgment === "unverified")),
                )
                .map((i) => i.id),
              [],
            )
          }
        />,
        <Tile
          key="metric-stale"
          testid="metric-stale"
          tone={metrics.staleEvaluations > 0 ? "stale" : undefined}
          icon="history"
          label={t("metric.stale")}
          value={String(metrics.staleEvaluations)}
          unit={t("unit.items")}
          sub=""
          hint={t("metric.staleHint")}
          spark={
            <Badge tone="warning" class="tile-now">
              {t("metric.now")}
            </Badge>
          }
          onPick={() =>
            members(
              ui,
              t("metric.stale"),
              t("members.now"),
              answer.members.instances.filter((i) => i.stale).map((i) => i.id),
              [],
            )
          }
        />,
        <Tile
          key="metric-duration"
          testid="metric-duration"
          icon="clock"
          label={t("metric.duration")}
          value={duration(metrics.duration.medianMs, language)}
          sub={t("metric.p90", { p90: duration(metrics.duration.p90Ms, language) })}
          spark={<Sparkline values={trends.map((b) => b.duration.medianMs)} />}
          onPick={() => members(ui, t("metric.duration"), within, [], ended)}
        />,
        <Tile
          key="metric-cost"
          testid="metric-cost"
          icon="coins"
          label={t("metric.cost")}
          value={money(usage.costUsd)}
          sub={
            usage.costUsd === null && usage.inputTokens === null
              ? t("metric.noUsage")
              : `${t("metric.perAchieved", { cost: money(usage.costPerAchievedOutcome) })} · ${t("metric.tokens", { input: count(usage.inputTokens, language), cached: usage.cachedInputTokens === null ? null : count(usage.cachedInputTokens, language), output: count(usage.outputTokens, language) })}`
          }
          spark={
            <Sparkline
              values={trends.map((b) => {
                const costs = Object.values(b.costByAgent);
                return costs.length ? costs.reduce((a, c) => a + c, 0) : null;
              })}
            />
          }
          onPick={() =>
            members(
              ui,
              t("metric.cost"),
              within,
              [],
              answer.members.runs.filter((r) => r.costUsd !== null),
            )
          }
        />,
      ].slice(secondary ? 4 : 0, secondary ? 6 : 4)}
    </div>
  );
}

/** Lists, in the panel, what a bucket of the trends counts: its judged instances and its runs. */
function bucketPicker(ui: Ui, answer: StatsResponse): (i: number) => void {
  const { t, language } = ui;
  const { trends } = answer.stats;
  const next = (i: number): number => trends[i + 1]?.start ?? Number.POSITIVE_INFINITY;
  return (i) => {
    const bucket = trends[i];
    if (!bucket) return;
    const inBucket = (at: number | undefined): boolean =>
      at !== undefined && at >= bucket.start && at < next(i);
    members(
      ui,
      shortDate(bucket.start, language),
      t("members.bucket", { from: dateTime(bucket.start, language) }),
      answer.members.instances
        .filter((m) => m.judged && inBucket(ui.instances.get(m.id)?.evaluation?.at))
        .map((m) => m.id),
      answer.members.runs.filter((r) => inBucket(r.startedAt)),
    );
  };
}

/** The chart's name for assistive technology, with how to use it from the keyboard. */
const chartName = (t: Ui["t"], title: string): string => `${title}. ${t("chart.keys")}`;

/** The runs of each bucket by result, stacked: succeeded, failed, canceled, interrupted. */
function RunsChart({ answer }: { answer: StatsResponse }) {
  const ui = useUi();
  const { t, language } = ui;
  const { trends } = answer.stats;
  const labels = trends.map((b) => shortDate(b.start, language));
  const runSeries: SeriesStyle[] = [
    { label: t("status.succeeded"), className: "c-succeeded" },
    { label: t("status.failed"), className: "c-failed" },
    { label: t("status.canceled"), className: "c-canceled" },
    { label: t("status.interrupted"), className: "c-interrupted" },
  ];
  const none = trends.every((b) => endedTotal(b) === 0);
  return (
    <ChartCard title={t("trend.runs")} legend={<Legend series={runSeries} />} class="summary-trend">
      {none && <p class="chart-empty-note">{t("trend.noData")}</p>}
      <StackedBars
        label={chartName(t, t("trend.runs"))}
        labels={labels}
        titles={trends.map(
          (b, i) =>
            `${labels[i]}: ${runSeries.map((s, k) => `${s.label} ${Object.values(b.runs)[k] ?? 0}`).join(", ")}`,
        )}
        onPick={bucketPicker(ui, answer)}
        series={runSeries}
        stacks={trends.map((b) => [
          b.runs.succeeded,
          b.runs.failed,
          b.runs.canceled,
          b.runs.interrupted,
        ])}
      />
    </ChartCard>
  );
}

/**
 * The first row under the tiles: the runs and their results, and the period's judgments as a
 * donut. Both use the server's buckets, as the trends below do. The donut's counts are in its
 * legend, and its centre is empty: how many were judged, and the rate, are the tile's.
 */
function SummaryCharts({ answer }: { answer: StatsResponse }) {
  const { t } = useUi();
  const { trends } = answer.stats;
  const totals = trends.reduce(
    (n, b) => [
      n[0]! + b.judgments.achieved,
      n[1]! + b.judgments["not-achieved"],
      n[2]! + b.judgments.unverified,
    ],
    [0, 0, 0],
  );
  const total = totals.reduce((a, b) => a + b, 0);
  const colors = ["var(--chart-achieved)", "var(--chart-not-achieved)", "var(--chart-unverified)"];
  const names = [t("judgment.achieved"), t("judgment.not-achieved"), t("judgment.unverified")];
  const circumference = 2 * Math.PI * 66;
  let offset = 0;
  return (
    <div class="summary-charts">
      <RunsChart answer={answer} />
      <Card class="summary-donut">
        <CardHeader title={t("summary.judgments")} />
        <div class="card-body">
          <div class="donut-wrap">
            <svg viewBox="0 0 160 160" aria-hidden="true">
              <circle class="donut-track" cx="80" cy="80" r="66" />
              {totals.map((n, i) => {
                const length = total ? (n / total) * circumference : 0;
                const start = offset;
                offset += length;
                return (
                  <circle
                    key={i}
                    class="donut-segment"
                    cx="80"
                    cy="80"
                    r="66"
                    stroke={colors[i]}
                    stroke-dasharray={`${length} ${circumference}`}
                    stroke-dashoffset={-start}
                  />
                );
              })}
            </svg>
          </div>
          <dl class="donut-legend">
            {totals.map((n, i) => (
              <div key={i}>
                <dt>
                  <span class="swatch" style={{ background: colors[i] }} />
                  {names[i]}
                </dt>
                <dd>{n}</dd>
              </div>
            ))}
          </dl>
        </div>
      </Card>
    </div>
  );
}

function ChartCard({
  title,
  legend,
  class: extra,
  children,
}: {
  title: string;
  legend?: ComponentChildren;
  class?: string;
  children: ComponentChildren;
}) {
  return (
    <Card class={cx("chart-card", extra)}>
      <CardHeader title={title} actions={legend} />
      <div class="card-body">{children}</div>
    </Card>
  );
}

/** The trends below the first row: the judgments with the achievement rate, cost, and duration. */
function Trends({ answer }: { answer: StatsResponse }) {
  const ui = useUi();
  const { t, language } = ui;
  const { trends } = answer.stats;
  const labels = trends.map((b) => shortDate(b.start, language));
  const pick = bucketPicker(ui, answer);
  const named = (title: string): string => chartName(t, title);
  const judgmentSeries: SeriesStyle[] = [
    { label: t("judgment.achieved"), className: "c-achieved" },
    { label: t("judgment.not-achieved"), className: "c-not-achieved" },
    { label: t("judgment.unverified"), className: "c-unverified" },
  ];
  const agents = [...new Set(trends.flatMap((b) => Object.keys(b.costByAgent)))].sort();
  const agentSeries = agents.map((agent, k) => ({
    label: agent,
    className: AGENT_CLASSES[k % AGENT_CLASSES.length] ?? "a0",
  }));
  const empty = trends.every(
    (b) =>
      Object.values(b.runs).every((n) => n === 0) &&
      Object.values(b.judgments).every((n) => n === 0),
  );
  if (empty) return null;
  return (
    <div class="trends">
      <ChartCard
        title={t("trend.judgments")}
        legend={
          <Legend series={[...judgmentSeries, { label: t("trend.rate"), className: "c-rate" }]} />
        }
      >
        <StackedBars
          label={named(t("trend.judgments"))}
          labels={labels}
          titles={trends.map(
            (b, i) =>
              `${labels[i]}: ${judgmentSeries.map((s, k) => `${s.label} ${Object.values(b.judgments)[k] ?? 0}`).join(", ")}; ${t("trend.rate")} ${b.achievementRate === null ? "—" : `${percent(b.achievementRate)}%`}`,
          )}
          onPick={pick}
          series={judgmentSeries}
          stacks={trends.map((b) => [
            b.judgments.achieved,
            b.judgments["not-achieved"],
            b.judgments.unverified,
          ])}
          rate={trends.map((b) => b.achievementRate)}
        />
      </ChartCard>
      <ChartCard
        title={t("trend.cost")}
        legend={agents.length > 0 ? <Legend series={agentSeries} /> : undefined}
      >
        {agents.length === 0 ? (
          <Empty icon="coins" title={t("metric.noUsage")} class="chart-empty" />
        ) : (
          <Lines
            label={named(t("trend.cost"))}
            labels={labels}
            titles={trends.map(
              (b, i) =>
                `${labels[i]}: ${agents.map((a) => `${a} ${money(b.costByAgent[a] ?? null)}`).join(", ")}`,
            )}
            onPick={pick}
            series={agentSeries}
            values={agents.map((a) => trends.map((b) => b.costByAgent[a] ?? null))}
            format={(v) => money(v)}
          />
        )}
      </ChartCard>
      <ChartCard title={t("trend.duration")}>
        <Whiskers
          label={named(t("trend.duration"))}
          labels={labels}
          titles={trends.map(
            (b, i) =>
              `${labels[i]}: ${duration(b.duration.medianMs, language)} (p90 ${duration(b.duration.p90Ms, language)})`,
          )}
          onPick={pick}
          medians={trends.map((b) => b.duration.medianMs)}
          p90s={trends.map((b) => b.duration.p90Ms)}
          format={(v) => duration(v, language)}
        />
      </ChartCard>
    </div>
  );
}

function Breakdown({
  answer,
  cut,
  setCut,
}: {
  answer: StatsResponse;
  cut: Cut;
  setCut: (cut: Cut) => void;
}) {
  const ui = useUi();
  const { t, language, model } = ui;
  const { breakdowns } = answer.stats;
  const within = windowText(ui, answer.stats);
  const instancesOf = (process: string): string[] =>
    answer.members.instances.filter((i) => i.process === process).map((i) => i.id);
  const rows = breakdowns[cut].length;
  return (
    <Card class="breakdown">
      <CardHeader
        title={t("breakdown.title")}
        actions={
          <Tabs
            value={cut}
            onChange={setCut}
            items={CUTS.map((name) => ({ value: name, label: t(`breakdown.${name}`) }))}
            label={t("breakdown.title")}
            base="breakdown"
            variant="pill"
          />
        }
      />
      <div class="card-table" {...tabPanel("breakdown", cut)}>
        {rows === 0 ? (
          <Empty icon="list" title={t("trend.noData")} />
        ) : (
          <Table label={t(`breakdown.${cut}`)}>
            {cut === "process" && (
              <>
                <thead>
                  <tr>
                    <th>{t("col.process")}</th>
                    <th class="num">{t("col.instances")}</th>
                    <th class="num">{t("col.runs")}</th>
                    <th class="num">{t("col.runSuccess")}</th>
                    <th class="num">{t("col.median")}</th>
                    <th class="num">{t("col.achievement")}</th>
                    <th class="num">{t("col.unverified")}</th>
                    <th class="num">{t("col.cost")}</th>
                  </tr>
                </thead>
                <tbody>
                  {breakdowns.process.map((row) => (
                    <tr
                      key={row.process}
                      {...rowActions(() =>
                        members(
                          ui,
                          processName(model, row.process),
                          within,
                          instancesOf(row.process),
                          answer.members.runs.filter((r) => r.process === row.process),
                        ),
                      )}
                    >
                      <td class="cell-name">{processName(model, row.process)}</td>
                      <td class="num">{row.instances}</td>
                      <td class="num">{row.runs}</td>
                      <RatioCell share={row.runSuccess} />
                      <td class="num">{duration(row.duration.medianMs, language)}</td>
                      <RatioCell share={row.achievement} />
                      <td class="num">
                        {row.unverified.value === null ? "—" : `${percent(row.unverified.value)}%`}
                      </td>
                      <td class="num">{money(row.costUsd)}</td>
                    </tr>
                  ))}
                </tbody>
              </>
            )}
            {cut === "agent" && (
              <>
                <thead>
                  <tr>
                    <th>{t("col.agent")}</th>
                    <th class="num">{t("col.runs")}</th>
                    <th class="num">{t("col.runSuccess")}</th>
                    <th class="num">{t("col.achievement")}</th>
                    <th class="num">{t("col.perAchieved")}</th>
                    <th class="num">{t("col.runsPerInstance")}</th>
                  </tr>
                </thead>
                <tbody>
                  {breakdowns.agent.map((row) => (
                    <tr
                      key={row.agent}
                      {...rowActions(() =>
                        members(
                          ui,
                          row.agent,
                          within,
                          [],
                          answer.members.runs.filter((r) => r.agent === row.agent),
                        ),
                      )}
                    >
                      <td class="cell-name">
                        {model?.agents.find((a) => a.id === row.agent)?.label ?? row.agent}
                      </td>
                      <td class="num">{row.runs}</td>
                      <RatioCell share={row.runSuccess} />
                      <RatioCell share={row.achievement} />
                      <td class="num">{money(row.costPerAchievedOutcome)}</td>
                      <td class="num">
                        {row.runsPerInstance === null ? "—" : row.runsPerInstance.toFixed(1)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </>
            )}
            {cut === "outcome" && (
              <>
                <thead>
                  <tr>
                    <th>{t("col.process")}</th>
                    <th>{t("col.outcome")}</th>
                    <th>{t("col.counts")}</th>
                  </tr>
                </thead>
                <tbody>
                  {breakdowns.outcome.map((row) => {
                    const { achieved, unverified } = row.counts;
                    const total = achieved + row.counts["not-achieved"] + unverified;
                    const flag =
                      total > 0 && achieved === 0
                        ? t("outcome.never")
                        : total > 0 && unverified * 2 > total
                          ? t("outcome.mostlyUnverified")
                          : "";
                    const text =
                      model?.processes.find((p) => p.id === row.process)?.outcomes[row.outcome] ??
                      "";
                    return (
                      <tr
                        key={`${row.process}:${row.outcome}`}
                        {...rowActions(() =>
                          members(
                            ui,
                            `${processName(model, row.process)} · ${row.outcome + 1}`,
                            text,
                            answer.members.instances
                              .filter((i) => i.judged && i.process === row.process)
                              .map((i) => i.id),
                            [],
                          ),
                        )}
                      >
                        <td class="cell-name">{processName(model, row.process)}</td>
                        <td class="cell-outcome">
                          <span class="outcome-text" title={text}>
                            {row.outcome + 1}. {text}
                          </span>
                          {flag && (
                            <Badge tone="warning" class="flag">
                              {flag}
                            </Badge>
                          )}
                          {total === 0 && (
                            <Badge tone="outline" class="flag">
                              {t("outcome.unjudged")}
                            </Badge>
                          )}
                        </td>
                        <td class="counts-cell">
                          <span class="stack" aria-hidden="true">
                            {(["achieved", "not-achieved", "unverified"] as const).map((key) => (
                              <span
                                key={key}
                                class={`c-${key}`}
                                style={{
                                  width: `${total ? (row.counts[key] / total) * 100 : 0}%`,
                                }}
                              />
                            ))}
                          </span>
                          <span class="mono">
                            {achieved} · {row.counts["not-achieved"]} · {unverified}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </>
            )}
            {cut === "judge" && (
              <>
                <thead>
                  <tr>
                    <th>{t("col.judge")}</th>
                    <th class="num">{t("col.judgments")}</th>
                    <th class="num">{t("col.achievement")}</th>
                  </tr>
                </thead>
                <tbody>
                  {breakdowns.judge.map((row) => (
                    <tr
                      key={row.judge}
                      {...rowActions(() =>
                        members(
                          ui,
                          t(`judgeKind.${row.judge}`),
                          within,
                          answer.members.instances
                            .filter((i) => {
                              const by = ui.instances.get(i.id)?.evaluation?.by;
                              const kind = !by
                                ? null
                                : by.kind === "user"
                                  ? "user"
                                  : by.self
                                    ? "self"
                                    : "agent";
                              return i.judged && kind === row.judge;
                            })
                            .map((i) => i.id),
                          [],
                        ),
                      )}
                    >
                      <td class="cell-name">{t(`judgeKind.${row.judge}`)}</td>
                      <td class="num">{row.judgments}</td>
                      <RatioCell share={row.achievement} />
                    </tr>
                  ))}
                </tbody>
              </>
            )}
          </Table>
        )}
      </div>
    </Card>
  );
}

/** Not amber: amber says that evidence is stale. */
const KIND_TONE: Record<FindingKind, Tone> = {
  description: "info",
  configuration: "neutral",
  unverified: "outline",
};

/**
 * A check's evidence as what it names: a run or an instance (which open), a Process (its panel),
 * an agent, or a path (an Artifact or a SKILL.md opens; another path shows as it is).
 */
function CheckEvidence({ line, artifacts }: { line: string; artifacts: readonly Artifact[] }) {
  const { runs, instances, model } = useUi();
  if (/^r\d+$/.test(line) && runs.has(line))
    return <EvidenceChip evidence={{ run: line }} artifacts={artifacts} />;
  if (/^i\d+$/.test(line) && instances.has(line))
    return <EvidenceChip evidence={{ instance: line }} artifacts={artifacts} />;
  if (model?.processes.some((p) => p.id === line)) return <ProcessLink id={line} />;
  const agent = model?.agents.find((a) => a.id === line);
  if (agent) return <span class="chip chip-agent">{agent.label}</span>;
  return <EvidenceChip evidence={{ path: line }} artifacts={artifacts} />;
}

/**
 * The checks that the filter shows: one about an instance, when the filter's numbers count that
 * instance (its runs, judgments, or stale evidence); one about an agent, when no other agent is
 * chosen; and the others, when no other Process is chosen.
 */
function checksIn(findings: readonly Finding[], filter: Filter, answer: StatsResponse): Finding[] {
  const counted = new Set(answer.members.instances.map((i) => i.id));
  return findings.filter((finding) => {
    const { subject } = finding;
    if (subject.instance) return counted.has(subject.instance);
    if (subject.agent && filter.agent) return subject.agent === filter.agent;
    return !filter.process || subject.process === filter.process;
  });
}

/**
 * The checks: what fixed tests of the records, the model, and the configuration find (what is
 * wrong in the description or the configuration, and what is unverified), as observations.
 */
function Checks({
  data,
  retry,
  filter,
  answer,
}: {
  data: Loaded<AssessmentData>;
  retry: () => void;
  filter: Filter;
  answer: StatsResponse;
}) {
  const { t, language, instances } = useUi();
  const [all, setAll] = useState(false);
  const found = data.status === "ok" ? checksIn(data.value.overview.findings, filter, answer) : [];
  const artifacts = data.status === "ok" ? data.value.artifacts : [];
  const shown = all ? found : found.slice(0, FINDINGS_SHOWN);
  return (
    <Card class="findings-card" data-testid="findings">
      <CardHeader
        title={t("findings.title")}
        icon={<Icon name="list" />}
        actions={
          data.status === "ok" && found.length > 0 ? (
            <Badge tone="outline">{found.length}</Badge>
          ) : undefined
        }
      />
      <div class="card-body">
        {data.status === "loading" && (
          <div class="loading" role="status">
            <span class="sr-only">{t("loading")}</span>
            <Skeleton width="80%" />
            <Skeleton width="64%" />
            <Skeleton width="72%" />
          </div>
        )}
        {data.status === "error" && (
          <Alert
            tone="danger"
            title={t("findings.error")}
            action={
              <Button variant="outline" size="sm" onClick={retry}>
                {t("retry")}
              </Button>
            }
          >
            {describeError(data.error, language)}
          </Alert>
        )}
        {data.status === "ok" && found.length === 0 && (
          <Empty icon="check" title={t("findings.none")} class="findings-empty" />
        )}
        {shown.length > 0 && (
          <ul class="findings">
            {shown.map((finding, i) => {
              const instance = finding.subject.instance
                ? instances.get(finding.subject.instance)
                : undefined;
              return (
                <li key={`${finding.kind}:${finding.key ?? ""}:${i}`} class="finding">
                  <Badge tone={KIND_TONE[finding.kind]} class="finding-kind">
                    {t(`findingKind.${finding.kind}`)}
                  </Badge>
                  <div class="finding-body">
                    <p>{sayReceived(language, finding.key, finding.args, finding.message)}</p>
                    {(finding.subject.process || finding.subject.artifact || instance) && (
                      <div class="chips">
                        {finding.subject.process && <ProcessLink id={finding.subject.process} />}
                        {finding.subject.artifact && <TypeLink id={finding.subject.artifact} />}
                        {instance && <InstanceLink instance={instance} />}
                      </div>
                    )}
                    {finding.evidence.length > 0 && (
                      <div class="chips evidence-chips">
                        {finding.evidence.slice(0, 3).map((line) => (
                          <CheckEvidence key={line} line={line} artifacts={artifacts} />
                        ))}
                      </div>
                    )}
                  </div>
                </li>
              );
            })}
          </ul>
        )}
        {found.length > FINDINGS_SHOWN && (
          <Button variant="link" class="findings-more" onClick={() => setAll((was) => !was)}>
            {all ? t("findings.less") : t("findings.more", { n: found.length })}
          </Button>
        )}
      </div>
    </Card>
  );
}

/**
 * What the analysis reads besides the statistics: the assessment (the latest, its since, and the
 * checks), the assessments recorded (the history), and the Artifacts (where a cited path opens),
 * again once the records settle after a change.
 */
function useAssessmentData(): { data: Loaded<AssessmentData>; retry: () => void } {
  const { client, version } = useUi();
  const [data, setData] = useState<Loaded<AssessmentData>>({ status: "loading" });
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    let live = true;
    const timer = setTimeout(
      () => {
        Promise.all([
          client.get<AssessmentResponse>("/api/assessment"),
          client.get<AssessmentsResponse>("/api/assessments"),
          client.get<ArtifactsResponse>("/api/artifacts"),
        ]).then(
          ([overview, history, artifacts]) => {
            if (live)
              setData({
                status: "ok",
                value: {
                  overview: overview.assessment,
                  history: history.assessments,
                  artifacts: artifacts.artifacts,
                },
              });
          },
          (error: unknown) => {
            if (live) setData({ status: "error", error });
          },
        );
      },
      data.status === "ok" ? 400 : 0,
    );
    return () => {
      live = false;
      clearTimeout(timer);
    };
  }, [client, version, attempt]);
  return { data, retry: () => setAttempt((n) => n + 1) };
}

function DashboardSkeleton({ label }: { label: string }) {
  return (
    <div class="dashboard-body" role="status" aria-busy="true">
      <span class="sr-only">{label}</span>
      <div class="tiles">
        {Array.from({ length: 6 }, (_, i) => (
          <div key={i} class="tile tile-skeleton" aria-hidden="true">
            <Skeleton width="55%" />
            <Skeleton width="38%" height="30px" />
            <Skeleton width="70%" />
          </div>
        ))}
      </div>
      <div class="trends">
        {Array.from({ length: 2 }, (_, i) => (
          <Card key={i} class="chart-card">
            <div class="card-body">
              <Skeleton width="40%" />
              <Skeleton height="150px" class="chart-skeleton" />
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}

const sameFilter = (stats: Stats, filter: Filter): boolean =>
  stats.filter.period === filter.period &&
  stats.filter.granularity === filter.granularity &&
  (stats.filter.process ?? "") === filter.process &&
  (stats.filter.agent ?? "") === filter.agent;

export function DashboardView({ modelError }: { modelError: unknown }) {
  const { client, model, t, version, language } = useUi();
  const [initial] = useState(fromHash);
  const [filter, setFilterState] = useState<Filter>(initial.filter);
  const [cut, setCutState] = useState<Cut>(initial.cut);
  const [answer, setAnswer] = useState<StatsResponse | null>(null);
  const [error, setError] = useState<unknown>(null);
  const [attempt, setAttempt] = useState(0);
  const assessment = useAssessmentData();
  const setFilter = (next: Partial<Filter>): void => {
    const merged = { ...filter, ...next };
    kept = { ...kept, filter: merged };
    setFilterState(merged);
  };
  const setCut = (next: Cut): void => {
    kept = { ...kept, cut: next };
    setCutState(next);
  };
  // The fragment follows the filter while the analysis is shown, and is left clean after it.
  useEffect(() => {
    kept = { filter, cut };
    writeHash(kept);
  }, [filter, cut]);
  useEffect(() => () => writeHash(null), []);
  /** A cut of the statistics that an assessment cites: the observation shows it. */
  const showCut = (cited: StatCut): void => {
    setFilter({
      period: cited.period ?? "all",
      granularity: cited.granularity ?? "week",
      process: cited.process ?? "",
      agent: cited.agent ?? "",
    });
    const observation = document.querySelector('[data-testid="observation"]');
    if (observation) scrollUnderHeader(observation);
  };

  useEffect(() => {
    if (!model) return;
    let live = true;
    // Records change in bursts (a run ends, its instance changes): read once they settle.
    const timer = setTimeout(
      () => {
        client
          .get<StatsResponse>(
            `/api/stats${query({ ...filter, tz: -new Date().getTimezoneOffset() })}`,
          )
          .then(
            (next) => {
              if (!live) return;
              setAnswer(next);
              setError(null);
            },
            (failure: unknown) => {
              if (live) setError(failure);
            },
          );
      },
      answer ? 300 : 0,
    );
    return () => {
      live = false;
      clearTimeout(timer);
    };
  }, [client, model, filter, version, attempt]);

  if (!model)
    return modelError ? (
      <ModelProblem error={modelError} />
    ) : (
      <DashboardSkeleton label={t("loading")} />
    );
  const updating = answer !== null && !sameFilter(answer.stats, filter);
  const retry = (
    <Button variant="outline" size="sm" onClick={() => setAttempt((n) => n + 1)}>
      <Icon name="refresh" />
      {t("retry")}
    </Button>
  );
  return (
    <div class="dashboard" data-testid="dashboard">
      <AssessmentSection
        data={assessment.data}
        retry={assessment.retry}
        scope={{
          period: filter.period,
          ...(filter.process ? { process: filter.process } : {}),
          ...(filter.agent ? { agent: filter.agent } : {}),
        }}
        onCut={showCut}
      />
      <div class="observation" data-testid="observation">
        <div class="toolbar filters dashboard-filters">
          <Field label={t("filter.process")}>
            {(control) => (
              <Select
                id={control.id}
                labelledBy={control.labelId}
                value={filter.process}
                icon={<Icon name="network" />}
                options={[
                  { value: "", label: t("filter.allProcesses") },
                  ...model.processes.map((p) => ({ value: p.id, label: p.name })),
                ]}
                onChange={(process) => setFilter({ process })}
              />
            )}
          </Field>
          <Field label={t("filter.agent")}>
            {(control) => (
              <Select
                id={control.id}
                labelledBy={control.labelId}
                value={filter.agent}
                icon={<Icon name="terminal" />}
                options={[
                  { value: "", label: t("filter.allAgents") },
                  ...model.agents.map((a) => ({ value: a.id, label: a.label })),
                ]}
                onChange={(agent) => setFilter({ agent })}
              />
            )}
          </Field>
          <Field class="filter-period" label={t("filter.period")}>
            {(control) => (
              <Select
                id={control.id}
                labelledBy={control.labelId}
                value={filter.period}
                icon={<Icon name="clock" />}
                options={PERIODS.map((p) => ({ value: p, label: t(`period.${p}`) }))}
                onChange={(period) => setFilter({ period })}
              />
            )}
          </Field>
          <Field class="filter-granularity" label={t("filter.granularity")}>
            {(control) => (
              <Select
                id={control.id}
                labelledBy={control.labelId}
                value={filter.granularity}
                options={GRANULARITIES.map((g) => ({ value: g, label: t(`granularity.${g}`) }))}
                onChange={(granularity) => setFilter({ granularity })}
              />
            )}
          </Field>
        </div>
        {error !== null && answer !== null && (
          <Alert tone="danger" title={t("dashboard.error")} action={retry}>
            {describeError(error, language)}
          </Alert>
        )}
        {answer ? (
          <div class={cx("dashboard-body", updating && "is-updating")} aria-busy={updating}>
            <Tiles answer={answer} />
            <SummaryCharts answer={answer} />
            <Tiles answer={answer} secondary />
            <Trends answer={answer} />
            <div class="dashboard-lower">
              <Breakdown answer={answer} cut={cut} setCut={setCut} />
              <Checks
                data={assessment.data}
                retry={assessment.retry}
                filter={filter}
                answer={answer}
              />
            </div>
          </div>
        ) : error !== null ? (
          <Alert tone="danger" title={t("dashboard.error")} action={retry}>
            {describeError(error, language)}
          </Alert>
        ) : (
          <DashboardSkeleton label={t("loading")} />
        )}
      </div>
    </div>
  );
}
