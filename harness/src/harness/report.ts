/*
 * The assessment as Markdown, in the workspace's language (get_assessment with format markdown
 * and the alps://assessment resource): first the latest assessment, an agent's interpretation,
 * with what the records gained since it; then what the harness observes: the statistics, the
 * checks (the JSON's findings), and the facts of each instance.
 */

import { sayReceived } from "../shared/strings.ts";
import type {
  Assessment,
  AssessmentItemKind,
  AssessmentOverview,
  Evidence,
  FindingKind,
  Judgment,
  Language,
  OutcomeBreakdown,
  Ratio,
  ReviewJudgment,
  Stats,
} from "../shared/types.ts";

const percent = (share: Ratio): string =>
  share.value === null ? "—" : `${Math.round(share.value * 100)}%`;

/** A duration in the largest units that keep it readable. */
export function formatDuration(ms: number | null): string {
  if (ms === null) return "—";
  if (ms < 10_000) return `${(ms / 1000).toFixed(1)} s`;
  const seconds = Math.round(ms / 1000);
  if (seconds < 60) return `${seconds} s`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)} min ${seconds % 60} s`;
  return `${Math.floor(seconds / 3600)} h ${Math.floor((seconds % 3600) / 60)} min`;
}

const money = (usd: number | null): string => (usd === null ? "—" : `$${usd.toFixed(2)}`);
const count = (n: number | null): string => (n === null ? "—" : n.toLocaleString("en-US"));

const WORDS = {
  en: {
    title: (model: string) => `# Assessment of ${model}`,
    latest: "Latest assessment (interpretation)",
    noAssessment: "No assessment has been made.",
    by: (a: { agent: string; at: string; run: string }) =>
      `An agent's interpretation: ${a.agent}, ${a.at}, run ${a.run}.`,
    scope: (parts: string) => `Scope: ${parts}.`,
    allTime: "all time",
    days: (n: string) => `the last ${n} days`,
    process: (name: string) => `Process ${name}`,
    agent: (agent: string) => `agent ${agent}`,
    pointOfView: (text: string) => `point of view “${text}”`,
    since: (runs: number, judgments: number) =>
      `Since its run started: ${runs} process run(s) started and ${judgments} Outcome judgment(s) made.`,
    noItems: "No items.",
    itemKind: {
      description: "Description",
      configuration: "Configuration",
      operation: "Operation",
      unverified: "Unverified",
    } satisfies Record<AssessmentItemKind, string>,
    limits: "Limits",
    review: "Review",
    reviewed: {
      adopted: "adopted",
      held: "held",
      rejected: "rejected",
    } satisfies Record<ReviewJudgment, string>,
    evidenceOf: {
      run: (id: string) => `run ${id}`,
      instance: (id: string) => `instance ${id}`,
      evaluation: (id: string) => `the evaluation of ${id}`,
      stat: (metric: string, cut: string) => `statistics ${metric}${cut ? ` (${cut})` : ""}`,
      log: (run: string, n: number) => `event ${n} of run ${run}`,
      path: (p: string) => p,
    },
    statistics: "Statistics",
    window: (since: string | null) =>
      since
        ? `The process runs that started, and the judgments made, since ${since}. Stale evaluations are counted as they are now. Wake and assessment runs are not counted.`
        : "All process runs and judgments. Stale evaluations are counted as they are now. Wake and assessment runs are not counted.",
    metrics: "| Metric | Value |",
    achievement: "Achievement",
    unverified: "Unverified",
    stale: "Stale evaluations",
    runSuccess: "Run success",
    duration: "Duration",
    usage: "Usage",
    judged: (share: Ratio) =>
      `${percent(share)} (${share.numerator} of ${share.denominator} judged Outcomes)`,
    awaiting: (n: number) => (n > 0 ? `; ${n} instance(s) await a judgment` : ""),
    ended: (share: Ratio) =>
      `${percent(share)} (${share.numerator} of ${share.denominator} ended runs)`,
    durationValue: (median: string, p90: string) => `median ${median}, p90 ${p90}`,
    usageValue: (cost: string, input: string, cached: string | null, output: string, per: string) =>
      `${cost}; ${input} input${cached === null ? "" : ` (${cached} cached)`} and ${output} output tokens; ${per} per achieved Outcome`,
    byProcess: "By Process",
    processHeader:
      "| Process | Instances | Runs | Run success | Median duration | Achievement | Unverified | Cost |",
    attention: "Outcomes judged but never achieved, or mostly unverified",
    outcome: (process: string, n: number, text: string, row: OutcomeBreakdown) =>
      `- ${process}, Outcome ${n}${text ? ` (${text})` : ""}: achieved ${row.counts.achieved}, not achieved ${row.counts["not-achieved"]}, unverified ${row.counts.unverified}`,
    findings: "Checks",
    noFindings: "The checks found nothing.",
    kind: {
      description: "Description",
      configuration: "Configuration",
      unverified: "Unverified",
    } satisfies Record<FindingKind, string>,
    evidence: "Evidence",
    instances: "Instances",
    noInstances: "No instances.",
    header: "| Instance | Process | Latest run | Judgments | Evidence |",
    judgment: {
      achieved: "achieved",
      "not-achieved": "not achieved",
      unverified: "unverified",
    } satisfies Record<Judgment, string>,
    of: (run: string) => `of ${run}`,
    staleEvidence: (paths: string) => `stale: ${paths} changed`,
    current: "current",
    none: "—",
  },
  ja: {
    title: (model: string) => `# ${model} のアセスメント`,
    latest: "最新のアセスメント（解釈）",
    noAssessment: "アセスメントはまだ行われていない。",
    by: (a: { agent: string; at: string; run: string }) =>
      `エージェントの解釈：${a.agent}、${a.at}、実行 ${a.run}。`,
    scope: (parts: string) => `範囲：${parts}。`,
    allTime: "全期間",
    days: (n: string) => `直近 ${n} 日`,
    process: (name: string) => `プロセス ${name}`,
    agent: (agent: string) => `エージェント ${agent}`,
    pointOfView: (text: string) => `観点「${text}」`,
    since: (runs: number, judgments: number) =>
      `その実行の開始後に、プロセスの実行 ${runs} 件が始まり、成果の判断 ${judgments} 件が記録された。`,
    noItems: "項目はない。",
    itemKind: {
      description: "記述",
      configuration: "構成",
      operation: "運用",
      unverified: "未確認",
    } satisfies Record<AssessmentItemKind, string>,
    limits: "限界",
    review: "確認",
    reviewed: {
      adopted: "採用",
      held: "保留",
      rejected: "却下",
    } satisfies Record<ReviewJudgment, string>,
    evidenceOf: {
      run: (id: string) => `実行 ${id}`,
      instance: (id: string) => `インスタンス ${id}`,
      evaluation: (id: string) => `${id} の評価`,
      stat: (metric: string, cut: string) => `統計 ${metric}${cut ? `（${cut}）` : ""}`,
      log: (run: string, n: number) => `実行 ${run} のイベント ${n}`,
      path: (p: string) => p,
    },
    statistics: "統計",
    window: (since: string | null) =>
      since
        ? `${since} 以降に始まったプロセスの実行と、その間の判断。根拠が古い評価は今の状態を数える。目覚めとアセスメントの実行は数えない。`
        : "すべてのプロセスの実行と判断。根拠が古い評価は今の状態を数える。目覚めとアセスメントの実行は数えない。",
    metrics: "| 指標 | 値 |",
    achievement: "成果の達成率",
    unverified: "未確認率",
    stale: "根拠が古い評価",
    runSuccess: "実行の正常終了率",
    duration: "所要時間",
    usage: "使用量と費用",
    judged: (share: Ratio) =>
      `${percent(share)}（判断された成果 ${share.denominator} 件のうち ${share.numerator} 件）`,
    awaiting: (n: number) => (n > 0 ? `。判断を待つインスタンスが ${n} 件` : ""),
    ended: (share: Ratio) =>
      `${percent(share)}（終わった実行 ${share.denominator} 件のうち ${share.numerator} 件）`,
    durationValue: (median: string, p90: string) => `中央値 ${median}、p90 ${p90}`,
    usageValue: (cost: string, input: string, cached: string | null, output: string, per: string) =>
      `${cost}。入力 ${input}${cached === null ? "" : `（キャッシュ ${cached}）`}・出力 ${output} トークン。達成 1 件あたり ${per}`,
    byProcess: "プロセス別",
    processHeader:
      "| プロセス | インスタンス | 実行 | 正常終了率 | 所要時間の中央値 | 達成率 | 未確認率 | 費用 |",
    attention: "判断されたが一度も達成されていない成果と、未確認が過半の成果",
    outcome: (process: string, n: number, text: string, row: OutcomeBreakdown) =>
      `- ${process} の成果 ${n}${text ? `（${text}）` : ""}: 達成 ${row.counts.achieved}、未達成 ${row.counts["not-achieved"]}、未確認 ${row.counts.unverified}`,
    findings: "検査",
    noFindings: "検査で見つかったことはない。",
    kind: {
      description: "記述の問題",
      configuration: "構成の問題",
      unverified: "未確認",
    } satisfies Record<FindingKind, string>,
    evidence: "根拠",
    instances: "インスタンス",
    noInstances: "インスタンスはない。",
    header: "| インスタンス | プロセス | 最新の実行 | 判断 | 根拠 |",
    judgment: {
      achieved: "達成",
      "not-achieved": "未達成",
      unverified: "未確認",
    } satisfies Record<Judgment, string>,
    of: (run: string) => `（${run} について）`,
    staleEvidence: (paths: string) => `古い: ${paths} が変わった`,
    current: "最新",
    none: "—",
  },
} as const;

type Words = (typeof WORDS)[Language];

/** A table cell: one line, with the pipe escaped. */
const cell = (text: string): string => text.replace(/\r?\n/g, " ").replace(/\|/g, "\\|");
const row = (cells: string[]): string => `| ${cells.map(cell).join(" | ")} |`;

interface ReportOptions {
  language: Language;
  model: string;
  processName: (id: string) => string;
  /** The text of a Process's Outcome, or "" when the model has no such Outcome. */
  outcomeText: (process: string, outcome: number) => string;
}

function statisticsLines(stats: Stats, words: Words, options: ReportOptions): string[] {
  const { metrics } = stats;
  const since =
    stats.filter.since === undefined ? null : new Date(stats.filter.since).toISOString();
  const lines = [
    `## ${words.statistics}`,
    "",
    words.window(since),
    "",
    words.metrics,
    "| --- | --- |",
  ];
  lines.push(
    row([words.achievement, words.judged(metrics.achievement)]),
    row([
      words.unverified,
      `${words.judged(metrics.unverified)}${words.awaiting(metrics.unverified.awaitingJudgment)}`,
    ]),
    row([words.stale, String(metrics.staleEvaluations)]),
    row([words.runSuccess, words.ended(metrics.runSuccess)]),
    row([
      words.duration,
      words.durationValue(
        formatDuration(metrics.duration.medianMs),
        formatDuration(metrics.duration.p90Ms),
      ),
    ]),
    row([
      words.usage,
      words.usageValue(
        money(metrics.usage.costUsd),
        count(metrics.usage.inputTokens),
        metrics.usage.cachedInputTokens === null ? null : count(metrics.usage.cachedInputTokens),
        count(metrics.usage.outputTokens),
        money(metrics.usage.costPerAchievedOutcome),
      ),
    ]),
  );

  const processes = stats.breakdowns.process.filter((p) => p.instances > 0 || p.runs > 0);
  if (processes.length > 0) {
    lines.push("", `### ${words.byProcess}`, "", words.processHeader, `|${" --- |".repeat(8)}`);
    for (const p of processes)
      lines.push(
        row([
          options.processName(p.process),
          String(p.instances),
          String(p.runs),
          percent(p.runSuccess),
          formatDuration(p.duration.medianMs),
          percent(p.achievement),
          percent(p.unverified),
          money(p.costUsd),
        ]),
      );
  }

  const attention = stats.breakdowns.outcome.filter((o) => {
    const total = o.counts.achieved + o.counts["not-achieved"] + o.counts.unverified;
    return total > 0 && (o.counts.achieved === 0 || o.counts.unverified * 2 > total);
  });
  if (attention.length > 0) {
    lines.push("", `### ${words.attention}`, "");
    for (const o of attention)
      lines.push(
        words.outcome(
          options.processName(o.process),
          o.outcome,
          options.outcomeText(o.process, o.outcome).replace(/\r?\n/g, " "),
          o,
        ),
      );
  }
  return lines;
}

/** A text on one line, as a list item holds it. */
const oneLine = (text: string): string => text.replace(/\r?\n/g, " ");

function evidenceText(evidence: Evidence, words: Words): string {
  const of = words.evidenceOf;
  if ("run" in evidence) return of.run(evidence.run);
  if ("instance" in evidence) return of.instance(evidence.instance);
  if ("evaluation" in evidence) return of.evaluation(evidence.evaluation);
  if ("log" in evidence) return of.log(evidence.log.run, evidence.log.n);
  if ("path" in evidence) return of.path(evidence.path);
  const cut = Object.values(evidence.stat.filter).filter(Boolean).join(", ");
  return of.stat(evidence.stat.metric, cut);
}

/** The latest assessment: who read what and when, its summary quoted, and its items with their reviews. */
function latestLines(
  latest: Assessment | null,
  since: AssessmentOverview["since"],
  words: Words,
  options: ReportOptions,
): string[] {
  const lines = [`## ${words.latest}`, ""];
  if (!latest) return [...lines, words.noAssessment];
  const { scope } = latest;
  const parts = [
    !scope.period || scope.period === "all" ? words.allTime : words.days(scope.period.slice(0, -1)),
    ...(scope.process ? [words.process(options.processName(scope.process))] : []),
    ...(scope.agent ? [words.agent(scope.agent)] : []),
    ...(scope.request ? [words.pointOfView(oneLine(scope.request))] : []),
  ];
  lines.push(
    words.by({ agent: latest.agent, at: new Date(latest.at).toISOString(), run: latest.runId }),
    words.scope(parts.join(options.language === "ja" ? "、" : ", ")),
  );
  if (since) lines.push(words.since(since.runs, since.judgments));
  lines.push("", ...latest.summary.split(/\r?\n/).map((line) => (line ? `> ${line}` : ">")), "");
  if (latest.items.length === 0) lines.push(words.noItems);
  for (const item of latest.items) {
    const subject = [
      item.subject.instance,
      item.subject.process && options.processName(item.subject.process),
      item.subject.artifact,
      item.subject.agent,
      item.subject.guidance,
    ]
      .filter(Boolean)
      .join(" · ");
    const evidence = item.evidence.map((e) => evidenceText(e, words)).join(", ");
    // The latest review of the item says where it stands; the earlier ones stay in the record.
    const review = latest.reviews.filter((r) => r.n === item.n).at(-1);
    const parts = [
      `${item.n}. **${words.itemKind[item.kind]}**${subject ? ` (${subject})` : ""}: ${oneLine(item.statement)}`,
      ...(evidence ? [`${words.evidence}: ${evidence}.`] : []),
      ...(item.limits ? [`${words.limits}: ${oneLine(item.limits)}`] : []),
      ...(review
        ? [
            `${words.review}: ${words.reviewed[review.judgment]}${review.note ? ` (${oneLine(review.note)})` : ""}, ${new Date(review.at).toISOString()}.`,
          ]
        : []),
    ];
    lines.push(parts.join(" "));
  }
  return lines;
}

export function assessmentMarkdown(overview: AssessmentOverview, options: ReportOptions): string {
  const words = WORDS[options.language];
  const lines = [words.title(options.model), ""];
  lines.push(...latestLines(overview.latest, overview.since, words, options), "");
  lines.push(...statisticsLines(overview.stats, words, options));
  lines.push("", `## ${words.findings}`, "");
  if (overview.findings.length === 0) lines.push(words.noFindings);
  for (const finding of overview.findings) {
    const subject = [
      finding.subject.instance,
      finding.subject.process && options.processName(finding.subject.process),
      finding.subject.artifact,
      finding.subject.agent,
    ]
      .filter(Boolean)
      .join(" · ");
    const message = sayReceived(options.language, finding.key, finding.args, finding.message);
    const evidence =
      finding.evidence.length > 0 ? ` ${words.evidence}: ${finding.evidence.join(", ")}` : "";
    lines.push(
      `- **${words.kind[finding.kind]}**${subject ? ` (${subject})` : ""}: ${message}${evidence}`,
    );
  }

  lines.push("", `## ${words.instances}`, "");
  if (overview.instances.length === 0) lines.push(words.noInstances);
  else lines.push(words.header, "| --- | --- | --- | --- | --- |");
  for (const fact of overview.instances) {
    const latest = fact.latestRun ? `${fact.latestRun.id} (${fact.latestRun.status})` : words.none;
    const counts = new Map<Judgment, number>();
    for (const judgment of fact.judgments ?? [])
      counts.set(judgment.judgment, (counts.get(judgment.judgment) ?? 0) + 1);
    const judgments = fact.judgments
      ? `${[...counts].map(([judgment, n]) => `${words.judgment[judgment]} ${n}`).join(", ")} ${words.of(fact.evaluatedRun ?? "")}`
      : words.none;
    const evidence = !fact.judgments
      ? words.none
      : fact.stale
        ? words.staleEvidence(fact.staleness.map((reason) => reason.path ?? "SKILL.md").join(", "))
        : words.current;
    lines.push(
      row([fact.instance, options.processName(fact.process), latest, judgments, evidence]),
    );
  }
  return `${lines.join("\n")}\n`;
}
