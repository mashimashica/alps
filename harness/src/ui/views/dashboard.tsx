/*
 * The dashboard: what the statistics of GET /api/stats say for a period, a granularity, a Process,
 * and an agent. The metric tiles on top (each with the trend of its buckets), the four trends in
 * the middle, a breakdown table below whose cut can be switched, and the findings of the
 * assessment (GET /api/assessment). A click on a number lists, in the panel, the instances or the
 * runs it counts. The page draws the numbers; it judges nothing.
 */

import type { ComponentChildren } from "preact";
import { useEffect, useState } from "preact/hooks";
import { sayReceived } from "../../shared/strings.ts";
import type {
  AssessmentResponse,
  Finding,
  FindingKind,
  Granularity,
  Period,
  Ratio,
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
import { Legend, Lines, Sparkline, StackedBars, Whiskers, type SeriesStyle } from "./charts.tsx";
import { InstanceLink, ModelProblem, processName, ProcessLink, TypeLink } from "./common.tsx";

interface Filter {
  period: Period;
  granularity: Granularity;
  process: string;
  agent: string;
}

type Cut = "process" | "agent" | "outcome" | "judge";

/** The filter and the cut stay as they were while the page is open. */
let kept: { filter: Filter; cut: Cut } = {
  filter: { period: "30d", granularity: "week", process: "", agent: "" },
  cut: "process",
};

const PERIODS: Period[] = ["7d", "30d", "90d", "all"];
const GRANULARITIES: Granularity[] = ["day", "week"];
const CUTS: Cut[] = ["process", "agent", "outcome", "judge"];
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
  icon,
  tone,
  spark,
  onPick,
  testid,
}: {
  label: string;
  value: string;
  unit?: string;
  sub: string;
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

function Tiles({ answer }: { answer: StatsResponse }) {
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
    <div class="tiles">
      <Tile
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
      />
      <Tile
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
      />
      <Tile
        testid="metric-stale"
        tone={metrics.staleEvaluations > 0 ? "stale" : undefined}
        icon="history"
        label={t("metric.stale")}
        value={String(metrics.staleEvaluations)}
        unit={t("unit.items")}
        sub={t("metric.staleSub")}
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
      />
      <Tile
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
      />
      <Tile
        testid="metric-duration"
        icon="clock"
        label={t("metric.duration")}
        value={duration(metrics.duration.medianMs, language)}
        sub={t("metric.p90", { p90: duration(metrics.duration.p90Ms, language) })}
        spark={<Sparkline values={trends.map((b) => b.duration.medianMs)} />}
        onPick={() => members(ui, t("metric.duration"), within, [], ended)}
      />
      <Tile
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
      />
    </div>
  );
}

function ChartCard({
  title,
  legend,
  children,
}: {
  title: string;
  legend?: ComponentChildren;
  children: ComponentChildren;
}) {
  return (
    <Card class="chart-card">
      <CardHeader title={title} actions={legend} />
      <div class="card-body">{children}</div>
    </Card>
  );
}

function Trends({ answer }: { answer: StatsResponse }) {
  const ui = useUi();
  const { t, language } = ui;
  const { trends } = answer.stats;
  const labels = trends.map((b) => shortDate(b.start, language));
  const next = (i: number): number => trends[i + 1]?.start ?? Number.POSITIVE_INFINITY;
  const pick = (i: number): void => {
    const bucket = trends[i];
    if (!bucket) return;
    const inBucket = (at: number | undefined): boolean =>
      at !== undefined && at >= bucket.start && at < next(i);
    members(
      ui,
      labels[i] ?? "",
      t("members.bucket", { from: dateTime(bucket.start, language) }),
      answer.members.instances
        .filter((m) => m.judged && inBucket(ui.instances.get(m.id)?.evaluation?.at))
        .map((m) => m.id),
      answer.members.runs.filter((r) => inBucket(r.startedAt)),
    );
  };
  const named = (title: string): string => `${title}. ${t("chart.keys")}`;
  const runSeries: SeriesStyle[] = [
    { label: t("status.succeeded"), className: "c-succeeded" },
    { label: t("status.failed"), className: "c-failed" },
    { label: t("status.canceled"), className: "c-canceled" },
    { label: t("status.interrupted"), className: "c-interrupted" },
  ];
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
  if (empty)
    return (
      <Card class="trends-empty">
        <Empty icon="dashboard" title={t("trend.noData")} />
      </Card>
    );
  return (
    <div class="trends">
      <ChartCard title={t("trend.runs")} legend={<Legend series={runSeries} />}>
        <StackedBars
          label={named(t("trend.runs"))}
          labels={labels}
          titles={trends.map(
            (b, i) =>
              `${labels[i]}: ${runSeries.map((s, k) => `${s.label} ${Object.values(b.runs)[k] ?? 0}`).join(", ")}`,
          )}
          onPick={pick}
          series={runSeries}
          stacks={trends.map((b) => [
            b.runs.succeeded,
            b.runs.failed,
            b.runs.canceled,
            b.runs.interrupted,
          ])}
        />
      </ChartCard>
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
        description={t("breakdown.hint")}
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

type Loaded<T> =
  | { status: "loading" }
  | { status: "ok"; value: T }
  | { status: "error"; error: unknown };

/** The findings of the assessment: what is wrong in the description or the configuration, and what is unverified. */
function Findings({ process }: { process: string }) {
  const { client, t, language, version, instances } = useUi();
  const [state, setState] = useState<Loaded<Finding[]>>({ status: "loading" });
  const [all, setAll] = useState(false);
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    let live = true;
    const timer = setTimeout(
      () => {
        client.get<AssessmentResponse>("/api/assessment").then(
          (answer) => {
            if (live) setState({ status: "ok", value: answer.assessment.findings });
          },
          (error: unknown) => {
            if (live) setState({ status: "error", error });
          },
        );
      },
      state.status === "ok" ? 400 : 0,
    );
    return () => {
      live = false;
      clearTimeout(timer);
    };
  }, [client, version, attempt]);

  const found =
    state.status === "ok"
      ? state.value.filter((f) => !process || f.subject.process === process)
      : [];
  const shown = all ? found : found.slice(0, FINDINGS_SHOWN);
  return (
    <Card class="findings-card" data-testid="findings">
      <CardHeader
        title={t("findings.title")}
        description={t("findings.sub")}
        icon={<Icon name="list" />}
        actions={
          state.status === "ok" && found.length > 0 ? (
            <Badge tone="outline">{found.length}</Badge>
          ) : undefined
        }
      />
      <div class="card-body">
        {state.status === "loading" && (
          <div class="loading" role="status">
            <span class="sr-only">{t("loading")}</span>
            <Skeleton width="80%" />
            <Skeleton width="64%" />
            <Skeleton width="72%" />
          </div>
        )}
        {state.status === "error" && (
          <Alert
            tone="danger"
            title={t("findings.error")}
            action={
              <Button variant="outline" size="sm" onClick={() => setAttempt((n) => n + 1)}>
                {t("retry")}
              </Button>
            }
          >
            {describeError(state.error, language)}
          </Alert>
        )}
        {state.status === "ok" && found.length === 0 && (
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
                      <ul class="finding-evidence mono">
                        {finding.evidence.slice(0, 3).map((line) => (
                          <li key={line} title={line}>
                            {line}
                          </li>
                        ))}
                      </ul>
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
  const [filter, setFilterState] = useState<Filter>(kept.filter);
  const [cut, setCutState] = useState<Cut>(kept.cut);
  const [answer, setAnswer] = useState<StatsResponse | null>(null);
  const [error, setError] = useState<unknown>(null);
  const [attempt, setAttempt] = useState(0);
  const setFilter = (next: Partial<Filter>): void => {
    const merged = { ...filter, ...next };
    kept = { ...kept, filter: merged };
    setFilterState(merged);
  };
  const setCut = (next: Cut): void => {
    kept = { ...kept, cut: next };
    setCutState(next);
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
  const all = { value: "", label: t("filter.all") };
  const updating = answer !== null && !sameFilter(answer.stats, filter);
  const retry = (
    <Button variant="outline" size="sm" onClick={() => setAttempt((n) => n + 1)}>
      <Icon name="refresh" />
      {t("retry")}
    </Button>
  );
  return (
    <div class="dashboard" data-testid="dashboard">
      <div class="toolbar filters">
        <Field label={t("filter.period")}>
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
        <Field label={t("filter.granularity")}>
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
        <Field label={t("filter.process")}>
          {(control) => (
            <Select
              id={control.id}
              labelledBy={control.labelId}
              value={filter.process}
              icon={<Icon name="network" />}
              options={[all, ...model.processes.map((p) => ({ value: p.id, label: p.name }))]}
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
              options={[all, ...model.agents.map((a) => ({ value: a.id, label: a.label }))]}
              onChange={(agent) => setFilter({ agent })}
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
          <Trends answer={answer} />
          <div class="dashboard-lower">
            <Breakdown answer={answer} cut={cut} setCut={setCut} />
            <Findings process={filter.process} />
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
  );
}
