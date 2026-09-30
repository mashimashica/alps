/*
 * The dashboard: what the statistics of GET /api/stats say for a period, a granularity, a Process,
 * and an agent. The metric tiles on top, the four trends in the middle, and a breakdown table
 * below whose cut can be switched. A click on a number lists, in the panel, the instances or the
 * runs it counts. The page draws the numbers; it judges nothing.
 */

import { useEffect, useState } from "preact/hooks";
import type {
  Granularity,
  Period,
  Ratio,
  Stats,
  StatsResponse,
  StatsRun,
} from "../../shared/types.ts";
import { query } from "../api.ts";
import { useUi, type Ui } from "../context.ts";
import { count, dateTime, duration, money, percent, shortDate } from "../format.ts";
import { Legend, Lines, StackedBars, Whiskers, type SeriesStyle } from "./charts.tsx";
import { ModelProblem, processName } from "./common.tsx";

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

function Bar({ share }: { share: number | null }) {
  return (
    <span class="bar" aria-hidden="true">
      <span style={{ width: `${Math.round((share ?? 0) * 100)}%` }} />
    </span>
  );
}

function RatioCell({ share }: { share: Ratio }) {
  return (
    <td class="num">
      <span class="ratio">
        {share.value === null ? "—" : `${percent(share.value)}%`}
        <Bar share={share.value} />
      </span>
    </td>
  );
}

function Tile({
  label,
  value,
  unit,
  sub,
  primary,
  tone,
  onPick,
  testid,
}: {
  label: string;
  value: string;
  unit?: string;
  sub: string;
  primary?: boolean;
  tone?: "stale";
  onPick: () => void;
  testid: string;
}) {
  return (
    <button
      type="button"
      class={`tile${primary ? " highlight" : ""}${tone ? ` ${tone}` : ""}`}
      data-testid={testid}
      onClick={onPick}
    >
      <span class="label">{label}</span>
      <span class="value">
        {value}
        {unit && value !== "—" && <span class="unit">{unit}</span>}
      </span>
      <span class="sub">{sub}</span>
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

function Tiles({ answer }: { answer: StatsResponse }) {
  const ui = useUi();
  const { t, language } = ui;
  const { metrics } = answer.stats;
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
        primary
        label={t("metric.achievement")}
        value={percent(metrics.achievement.value)}
        unit="%"
        sub={t("metric.judged", {
          n: metrics.achievement.numerator,
          d: metrics.achievement.denominator,
        })}
        onPick={() => members(ui, t("metric.achievement"), within, judged, [])}
      />
      <Tile
        testid="metric-unverified"
        label={t("metric.unverified")}
        value={percent(metrics.unverified.value)}
        unit="%"
        sub={t("metric.awaiting", { n: metrics.unverified.awaitingJudgment })}
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
        tone="stale"
        label={t("metric.stale")}
        value={String(metrics.staleEvaluations)}
        unit={t("unit.items")}
        sub={t("metric.staleSub")}
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
        label={t("metric.runSuccess")}
        value={percent(metrics.runSuccess.value)}
        unit="%"
        sub={t("metric.ended", {
          n: metrics.runSuccess.numerator,
          d: metrics.runSuccess.denominator,
        })}
        onPick={() => members(ui, t("metric.runSuccess"), within, [], answer.members.runs)}
      />
      <Tile
        testid="metric-duration"
        label={t("metric.duration")}
        value={duration(metrics.duration.medianMs, language)}
        sub={t("metric.p90", { p90: duration(metrics.duration.p90Ms, language) })}
        onPick={() => members(ui, t("metric.duration"), within, [], ended)}
      />
      <Tile
        testid="metric-cost"
        label={t("metric.cost")}
        value={money(usage.costUsd)}
        sub={
          usage.costUsd === null && usage.inputTokens === null
            ? t("metric.noUsage")
            : `${t("metric.perAchieved", { cost: money(usage.costPerAchievedOutcome) })} · ${t("metric.tokens", { input: count(usage.inputTokens, language), output: count(usage.outputTokens, language) })}`
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
  const titles = trends.map(
    (b, i) =>
      `${labels[i]}: ${runSeries.map((s, k) => `${s.label} ${Object.values(b.runs)[k] ?? 0}`).join(", ")}`,
  );
  const empty = trends.every(
    (b) =>
      Object.values(b.runs).every((n) => n === 0) &&
      Object.values(b.judgments).every((n) => n === 0),
  );
  if (empty) return <p class="muted card">{t("trend.noData")}</p>;
  return (
    <div class="trends">
      <div class="card">
        <h3>{t("trend.runs")}</h3>
        <StackedBars
          labels={labels}
          titles={titles}
          onPick={pick}
          series={runSeries}
          stacks={trends.map((b) => [
            b.runs.succeeded,
            b.runs.failed,
            b.runs.canceled,
            b.runs.interrupted,
          ])}
        />
        <Legend series={runSeries} />
      </div>
      <div class="card">
        <h3>{t("trend.judgments")}</h3>
        <StackedBars
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
        <Legend series={[...judgmentSeries, { label: t("trend.rate"), className: "c-rate" }]} />
      </div>
      <div class="card">
        <h3>{t("trend.cost")}</h3>
        {agents.length === 0 ? (
          <p class="muted">{t("metric.noUsage")}</p>
        ) : (
          <>
            <Lines
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
            <Legend series={agentSeries} />
          </>
        )}
      </div>
      <div class="card">
        <h3>{t("trend.duration")}</h3>
        <Whiskers
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
      </div>
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
  return (
    <div class="card breakdown">
      <div class="card-head">
        <h3>{t("breakdown.title")}</h3>
        <div class="segmented" role="tablist">
          {CUTS.map((name) => (
            <button
              type="button"
              role="tab"
              key={name}
              aria-selected={cut === name}
              onClick={() => setCut(name)}
            >
              {t(`breakdown.${name}`)}
            </button>
          ))}
        </div>
      </div>
      <table>
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
                  class="clickable"
                  onClick={() =>
                    members(
                      ui,
                      processName(model, row.process),
                      within,
                      instancesOf(row.process),
                      answer.members.runs.filter((r) => r.process === row.process),
                    )
                  }
                >
                  <td>{processName(model, row.process)}</td>
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
                  class="clickable"
                  onClick={() =>
                    members(
                      ui,
                      row.agent,
                      within,
                      [],
                      answer.members.runs.filter((r) => r.agent === row.agent),
                    )
                  }
                >
                  <td>{model?.agents.find((a) => a.id === row.agent)?.label ?? row.agent}</td>
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
                  model?.processes.find((p) => p.id === row.process)?.outcomes[row.outcome] ?? "";
                return (
                  <tr
                    key={`${row.process}:${row.outcome}`}
                    class="clickable"
                    onClick={() =>
                      members(
                        ui,
                        `${processName(model, row.process)} · ${row.outcome + 1}`,
                        text,
                        answer.members.instances
                          .filter((i) => i.judged && i.process === row.process)
                          .map((i) => i.id),
                        [],
                      )
                    }
                  >
                    <td>{processName(model, row.process)}</td>
                    <td>
                      <span class="outcome-text">
                        {row.outcome + 1}. {text}
                      </span>
                      {flag && <span class="flag">{flag}</span>}
                      {total === 0 && <span class="flag quiet">{t("outcome.unjudged")}</span>}
                    </td>
                    <td class="counts-cell">
                      <span class="stack" aria-hidden="true">
                        {(["achieved", "not-achieved", "unverified"] as const).map((key) => (
                          <span
                            key={key}
                            class={`c-${key}`}
                            style={{ width: `${total ? (row.counts[key] / total) * 100 : 0}%` }}
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
                  class="clickable"
                  onClick={() =>
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
                    )
                  }
                >
                  <td>{t(`judgeKind.${row.judge}`)}</td>
                  <td class="num">{row.judgments}</td>
                  <RatioCell share={row.achievement} />
                </tr>
              ))}
            </tbody>
          </>
        )}
      </table>
    </div>
  );
}

export function DashboardView({ modelError }: { modelError: unknown }) {
  const { client, model, t, version, fail } = useUi();
  const [filter, setFilterState] = useState<Filter>(kept.filter);
  const [cut, setCutState] = useState<Cut>(kept.cut);
  const [answer, setAnswer] = useState<StatsResponse | null>(null);
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
              if (live) setAnswer(next);
            },
            (error: unknown) => {
              if (live) fail(error);
            },
          );
      },
      answer ? 300 : 0,
    );
    return () => {
      live = false;
      clearTimeout(timer);
    };
  }, [client, model, filter, version]);

  if (!model)
    return modelError ? (
      <ModelProblem error={modelError} />
    ) : (
      <p class="muted pad">{t("loading")}</p>
    );
  return (
    <div class="dashboard" data-testid="dashboard">
      <div class="filters">
        <label>
          {t("filter.period")}
          <select
            value={filter.period}
            onChange={(e) =>
              setFilter({ period: (e.currentTarget as HTMLSelectElement).value as Period })
            }
          >
            {PERIODS.map((p) => (
              <option key={p} value={p}>
                {t(`period.${p}`)}
              </option>
            ))}
          </select>
        </label>
        <label>
          {t("filter.granularity")}
          <select
            value={filter.granularity}
            onChange={(e) =>
              setFilter({
                granularity: (e.currentTarget as HTMLSelectElement).value as Granularity,
              })
            }
          >
            {GRANULARITIES.map((g) => (
              <option key={g} value={g}>
                {t(`granularity.${g}`)}
              </option>
            ))}
          </select>
        </label>
        <label>
          {t("filter.process")}
          <select
            value={filter.process}
            onChange={(e) => setFilter({ process: (e.currentTarget as HTMLSelectElement).value })}
          >
            <option value="">{t("filter.all")}</option>
            {model.processes.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          {t("filter.agent")}
          <select
            value={filter.agent}
            onChange={(e) => setFilter({ agent: (e.currentTarget as HTMLSelectElement).value })}
          >
            <option value="">{t("filter.all")}</option>
            {model.agents.map((a) => (
              <option key={a.id} value={a.id}>
                {a.label}
              </option>
            ))}
          </select>
        </label>
      </div>
      {answer ? (
        <div class="dashboard-body">
          <Tiles answer={answer} />
          <Trends answer={answer} />
          <Breakdown answer={answer} cut={cut} setCut={setCut} />
        </div>
      ) : (
        <p class="muted pad">{t("loading")}</p>
      )}
    </div>
  );
}
