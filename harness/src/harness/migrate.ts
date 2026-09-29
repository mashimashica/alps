/*
 * Converting a state.json without schemaVersion (harness 0.8 and earlier) to version 2.
 *
 * A work item becomes an instance: its inputs are the inputs of its last run, its outputs the
 * concrete targets of that run, and its review an evaluation by a user whose judgments carry no
 * evidence (version 1 recorded none). What version 2 does not have is dropped: the case, the
 * planned dates, the agent and creation time of work items. Runs keep their ids and move to
 * runs/<id>.json; `workItem` becomes `instance` and `summary` becomes `report`.
 */

import type {
  Evaluation,
  Instance,
  Judgment,
  OutcomeJudgment,
  Run,
  RunV1,
  StateFile,
  StateFileV1,
  WorkItemV1,
} from "../shared/types.ts";

const JUDGMENTS: readonly string[] = [
  "achieved",
  "not-achieved",
  "unverified",
] satisfies Judgment[];

export const INTERRUPTED_ERROR = "The harness server stopped while the run was running.";

/** Instance ids use the prefix `i`: work item `w4` becomes instance `i4`. */
export const instanceIdOf = (workItemId: string): string =>
  /^w\d+$/.test(workItemId) ? `i${workItemId.slice(1)}` : workItemId;

const seqOf = (id: string): number => Number(/(\d+)$/.exec(id)?.[1] ?? 0);

function lastRun(item: WorkItemV1, runs: Record<string, RunV1>): RunV1 | null {
  for (let i = item.runs.length - 1; i >= 0; i--) {
    const run = runs[item.runs[i] ?? ""];
    if (run) return run;
  }
  return null;
}

function instanceOf(item: WorkItemV1, runs: Record<string, RunV1>): Instance {
  const last = lastRun(item, runs);
  const inputs: Record<string, string[]> = {};
  for (const input of last?.inputs ?? [])
    inputs[input.type] = [...new Set([...(inputs[input.type] ?? []), ...input.paths])];
  const outputs: Record<string, string | null> = {};
  for (const target of last?.targets ?? [])
    outputs[target.type] = target.concrete && target.path ? target.path : null;

  let evaluation: Evaluation | null = null;
  if (item.review) {
    const judgments: OutcomeJudgment[] = item.review.judgments.flatMap((judgment, outcome) =>
      JUDGMENTS.includes(judgment)
        ? [{ outcome, judgment: judgment as Judgment, evidence: "" }]
        : [],
    );
    if (judgments.length > 0)
      evaluation = {
        runId: item.review.runId,
        judgments,
        ...(item.review.note.trim() ? { note: item.review.note } : {}),
        by: { kind: "user" },
        at: item.review.at,
      };
  }
  return {
    id: instanceIdOf(item.id),
    process: item.process,
    inputs,
    outputs,
    criteria: [],
    notes: "",
    runs: item.runs.filter((id) => runs[id]),
    evaluation,
  };
}

function runOf(run: RunV1, now: number): Run {
  const interrupted = run.status === "running";
  return {
    id: run.id,
    kind: "process",
    instance: run.workItem ? instanceIdOf(run.workItem) : null,
    process: run.process,
    agent: run.agent,
    status: interrupted ? "interrupted" : run.status,
    createdAt: run.createdAt,
    startedAt: run.startedAt,
    endedAt: run.endedAt ?? (interrupted ? now : null),
    exitCode: run.exitCode,
    error: interrupted ? (run.error ?? INTERRUPTED_ERROR) : run.error,
    agentError: run.agentError,
    // Version 1 listed only inputs that it had found, so none was missing.
    inputs: run.inputs.map((input) => ({ ...input, missing: [] })),
    targets: run.targets,
    outputs: run.outputs,
    usage: run.usage,
    report: run.summary,
    events: run.events,
    command: run.command,
    client: null,
    prompt: run.prompt,
    git: run.git,
    skill: run.skill,
  };
}

/** The version 2 state and run records of a version 1 state. */
export function migrateStateV1(v1: StateFileV1, now: number): { state: StateFile; runs: Run[] } {
  const runs = Object.values(v1.runs).map((run) => runOf(run, now));
  const instances = Object.values(v1.workItems).map((item) => instanceOf(item, v1.runs));
  const seq = Math.max(
    v1.seq,
    ...runs.map((run) => seqOf(run.id)),
    ...instances.map((i) => seqOf(i.id)),
  );
  return {
    state: {
      schemaVersion: 2,
      instances: Object.fromEntries(instances.map((instance) => [instance.id, instance])),
      provenance: { ...v1.provenance },
      seq,
      lastWakeAt: null,
      runs: Object.fromEntries(
        runs.map((run) => [
          run.id,
          {
            id: run.id,
            kind: run.kind,
            instance: run.instance,
            status: run.status,
            startedAt: run.startedAt,
            endedAt: run.endedAt,
          },
        ]),
      ),
    },
    runs,
  };
}
