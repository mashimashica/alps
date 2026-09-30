/*
 * The demo agent: it starts no process. It shows the reads an agent would make, puts a placeholder
 * at each output location that has none (an existing file is only touched, never overwritten),
 * and reports that no Outcome was checked, so the flow of a run can be seen without an agent.
 * What it says in the events is the harness's own: English, with its key and arguments in
 * shared/strings.ts. Its report and placeholders follow the workspace's language.
 */

import type { EventDraft } from "../agents/index.ts";
import { say, spoken } from "../shared/strings.ts";
import type { Language, RunInput, RunTarget } from "../shared/types.ts";

export interface DemoStep extends EventDraft {
  /** Where to write a placeholder (a trailing slash writes README.md in that directory), and for which type. */
  write?: { path: string; type: string };
}

export const demoReport = (language: Language): string => say(language, "demo.report", {});

/** A concrete path for a location: each wildcard becomes the run id (`**` spans no directory). */
export const demoPath = (location: string, runId: string): string =>
  location.replace(/\*\*\//g, "").replace(/\*+/g, runId);

export function demoSteps(options: {
  processName: string;
  skillPath: string | null;
  inputs: RunInput[];
  targets: RunTarget[];
  runId: string;
}): DemoStep[] {
  const steps: DemoStep[] = [{ kind: "system", ...spoken("demo.start", {}) }];
  if (options.skillPath) steps.push({ kind: "tool", text: `Read ${options.skillPath}` });
  for (const input of options.inputs)
    for (const file of input.paths.filter((p) => !input.missing.includes(p)).slice(0, 2))
      steps.push({ kind: "tool", text: `Read ${file}` });
  steps.push({ kind: "message", ...spoken("demo.aim", { process: options.processName }) });
  for (const target of options.targets) {
    if (!target.path) continue;
    const file = demoPath(target.path, options.runId);
    steps.push({ kind: "tool", text: `Write ${file}`, write: { path: file, type: target.type } });
  }
  steps.push({ kind: "message", ...spoken("demo.report", {}) });
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
  const note = say(options.language, "demo.note", {
    run: options.runId,
    process: options.processName,
  });
  if (options.path.endsWith("/"))
    return { file: `${options.path}README.md`, text: `# ${options.typeName}\n\n${note}\n` };
  if (/\.json$/i.test(options.path))
    return {
      file: options.path,
      text: `${JSON.stringify({ artifact: options.typeName, run: options.runId, note }, null, 2)}\n`,
    };
  return { file: options.path, text: `# ${options.typeName}\n\n${note}\n` };
}
