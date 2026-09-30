/*
 * The assessment as Markdown, in the workspace's language (get_assessment with format markdown
 * and the alps://assessment resource): the statistics, the findings, then the facts of each
 * instance.
 */

import { sayReceived } from "../shared/strings.ts";
import type {
  Assessment,
  FindingKind,
  Judgment,
  Language,
  OutcomeBreakdown,
  Ratio,
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
    statistics: "Statistics",
    window: (since: string | null) =>
      since
        ? `The process runs that started, and the judgments made, since ${since}. Stale evaluations are counted as they are now. Wake runs are not counted.`
        : "All process runs and judgments. Stale evaluations are counted as they are now. Wake runs are not counted.",
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
    usageValue: (cost: string, input: string, output: string, per: string) =>
      `${cost}; ${input} input and ${output} output tokens; ${per} per achieved Outcome`,
    byProcess: "By Process",
    processHeader:
      "| Process | Instances | Runs | Run success | Median duration | Achievement | Unverified | Cost |",
    attention: "Outcomes judged but never achieved, or mostly unverified",
    outcome: (process: string, n: number, text: string, row: OutcomeBreakdown) =>
      `- ${process}, Outcome ${n}${text ? ` (${text})` : ""}: achieved ${row.counts.achieved}, not achieved ${row.counts["not-achieved"]}, unverified ${row.counts.unverified}`,
    findings: "Findings",
    noFindings: "No findings.",
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
    title: (model: string) => `# ${model} の所見`,
    statistics: "統計",
    window: (since: string | null) =>
      since
        ? `${since} 以降に始まったプロセスの実行と、その間の判断。根拠が古い評価は今の状態を数える。目覚めの実行は数えない。`
        : "すべてのプロセスの実行と判断。根拠が古い評価は今の状態を数える。目覚めの実行は数えない。",
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
    usageValue: (cost: string, input: string, output: string, per: string) =>
      `${cost}。入力 ${input}・出力 ${output} トークン。達成 1 件あたり ${per}`,
    byProcess: "プロセス別",
    processHeader:
      "| プロセス | インスタンス | 実行 | 正常終了率 | 所要時間の中央値 | 達成率 | 未確認率 | 費用 |",
    attention: "判断されたが一度も達成されていない成果と、未確認が過半の成果",
    outcome: (process: string, n: number, text: string, row: OutcomeBreakdown) =>
      `- ${process} の成果 ${n}${text ? `（${text}）` : ""}: 達成 ${row.counts.achieved}、未達成 ${row.counts["not-achieved"]}、未確認 ${row.counts.unverified}`,
    findings: "所見",
    noFindings: "所見はない。",
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

export function assessmentMarkdown(assessment: Assessment, options: ReportOptions): string {
  const words = WORDS[options.language];
  const lines = [words.title(options.model), ""];
  lines.push(...statisticsLines(assessment.stats, words, options));
  lines.push("", `## ${words.findings}`, "");
  if (assessment.findings.length === 0) lines.push(words.noFindings);
  for (const finding of assessment.findings) {
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
  if (assessment.instances.length === 0) lines.push(words.noInstances);
  else lines.push(words.header, "| --- | --- | --- | --- | --- |");
  for (const fact of assessment.instances) {
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
