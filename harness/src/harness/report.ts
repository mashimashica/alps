/*
 * The assessment as Markdown, in the workspace's language (get_assessment with format markdown
 * and the alps://assessment resource): the findings, then the facts of each instance. The
 * statistics come with the dashboard.
 */

import { sayReceived } from "../shared/strings.ts";
import type { Assessment, FindingKind, Judgment, Language } from "../shared/types.ts";

const WORDS = {
  en: {
    title: (model: string) => `# Assessment of ${model}`,
    stats: "The statistics are not computed yet: they come with the dashboard.",
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
    stale: (paths: string) => `stale: ${paths} changed`,
    current: "current",
    none: "—",
  },
  ja: {
    title: (model: string) => `# ${model} の所見`,
    stats: "統計はまだ計算していない（ダッシュボードとともに加わる）。",
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
    stale: (paths: string) => `古い: ${paths} が変わった`,
    current: "最新",
    none: "—",
  },
} as const;

/** A table cell: one line, with the pipe escaped. */
const cell = (text: string): string => text.replace(/\r?\n/g, " ").replace(/\|/g, "\\|");

export function assessmentMarkdown(
  assessment: Assessment,
  options: { language: Language; model: string; processName: (id: string) => string },
): string {
  const words = WORDS[options.language];
  const lines = [words.title(options.model), "", words.stats, "", `## ${words.findings}`, ""];
  if (assessment.findings.length === 0) lines.push(words.noFindings);
  for (const finding of assessment.findings) {
    const subject = [
      finding.subject.instance,
      finding.subject.process && options.processName(finding.subject.process),
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
      ? `${[...counts].map(([judgment, count]) => `${words.judgment[judgment]} ${count}`).join(", ")} ${words.of(fact.evaluatedRun ?? "")}`
      : words.none;
    const evidence = !fact.judgments
      ? words.none
      : fact.stale
        ? words.stale(fact.staleness.map((reason) => reason.path ?? "SKILL.md").join(", "))
        : words.current;
    lines.push(
      `| ${[fact.instance, options.processName(fact.process), latest, judgments, evidence].map(cell).join(" | ")} |`,
    );
  }
  return `${lines.join("\n")}\n`;
}
