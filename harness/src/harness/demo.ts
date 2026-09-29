/*
 * The demo agent: it starts no process. It shows the reads an agent would make, puts a placeholder
 * at each output location that has none (an existing file is only touched, never overwritten),
 * and reports that no Outcome was checked, so the flow of a run can be seen without an agent.
 * Its texts follow the workspace's language.
 */

import type { EventDraft } from "../agents/index.ts";
import type { Language, RunInput, RunTarget } from "../shared/types.ts";

export interface DemoStep extends EventDraft {
  /** Where to write a placeholder (a trailing slash writes README.md in that directory), and for which type. */
  write?: { path: string; type: string };
}

const WORDS = {
  en: {
    start: "Running as a demo (no agent is started)",
    aim: (process: string) => `Preparing the outputs toward the Outcomes of "${process}".`,
    report:
      "This was a demo: no agent ran, and whether each Outcome is achieved was not checked. Judge from the content of the outputs.",
    note: (run: string, process: string) =>
      `Written by demo run ${run} (${process}). An agent's run writes the actual content.`,
  },
  ja: {
    start: "デモとして実行（エージェントは起動しない）",
    aim: (process: string) => `「${process}」の成果に向けて、出力を用意する。`,
    report:
      "デモのため、エージェントは起動しておらず、各成果の達成は確かめていない。出力の中身を見て判断すること。",
    note: (run: string, process: string) =>
      `デモ実行 ${run}（${process}）が作成した記録。実際の内容はエージェントの実行で作られる。`,
  },
} as const;

export const demoReport = (language: Language): string => WORDS[language].report;

/** A concrete path for a location: each wildcard becomes the run id (`**` spans no directory). */
export const demoPath = (location: string, runId: string): string =>
  location.replace(/\*\*\//g, "").replace(/\*+/g, runId);

export function demoSteps(options: {
  language: Language;
  processName: string;
  skillPath: string | null;
  inputs: RunInput[];
  targets: RunTarget[];
  runId: string;
}): DemoStep[] {
  const words = WORDS[options.language];
  const steps: DemoStep[] = [{ kind: "system", text: words.start }];
  if (options.skillPath) steps.push({ kind: "tool", text: `Read ${options.skillPath}` });
  for (const input of options.inputs)
    for (const file of input.paths.filter((p) => !input.missing.includes(p)).slice(0, 2))
      steps.push({ kind: "tool", text: `Read ${file}` });
  steps.push({ kind: "message", text: words.aim(options.processName) });
  for (const target of options.targets) {
    if (!target.path) continue;
    const file = demoPath(target.path, options.runId);
    steps.push({ kind: "tool", text: `Write ${file}`, write: { path: file, type: target.type } });
  }
  steps.push({ kind: "message", text: words.report });
  return steps;
}

/** The placeholder that a demo step writes: the file and its text. */
export function demoFile(options: {
  language: Language;
  path: string;
  typeName: string;
  processName: string;
  runId: string;
}): { file: string; text: string } {
  const note = WORDS[options.language].note(options.runId, options.processName);
  if (options.path.endsWith("/"))
    return { file: `${options.path}README.md`, text: `# ${options.typeName}\n\n${note}\n` };
  if (/\.json$/i.test(options.path))
    return {
      file: options.path,
      text: `${JSON.stringify({ artifact: options.typeName, run: options.runId, note }, null, 2)}\n`,
    };
  return { file: options.path, text: `# ${options.typeName}\n\n${note}\n` };
}
