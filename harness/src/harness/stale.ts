/*
 * "The evidence is stale" (Process Framework §8): after the judgment, one of the instance's inputs
 * or the Process's SKILL.md changed, so the judgment has to be reconsidered.
 */

import type { FileState } from "../model/index.ts";
import type { Evaluation, Run, StaleReason } from "../shared/types.ts";

/** What the workspace holds now for an instance. */
export interface CurrentState {
  /** Every input path of the instance with its state now; `null` when nothing is there. */
  inputs: { type: string; path: string; state: FileState | null }[];
  /** The SKILL.md that describes the Process now, or `null` when none is found. */
  skill: { path: string; sha256: string | null; mtime: number } | null;
}

/**
 * Why an evaluation is stale; empty when it is not (or when there is no evaluation).
 *
 * An input changed when it was modified after the judgment (by its modification time; a
 * directory by its newest file), or when it is gone although it existed at the start of the
 * judged run. The SKILL.md changed when its content differs from the one the judged run used and
 * it was modified after the judgment, or when another SKILL.md (or none) describes the Process now.
 */
export function staleness(
  evaluation: Evaluation | null,
  judgedRun: Pick<Run, "inputs" | "skill"> | null,
  current: CurrentState,
): StaleReason[] {
  if (!evaluation) return [];
  const reasons: StaleReason[] = [];
  const given = new Set(judgedRun?.inputs.flatMap((input) => input.paths) ?? []);
  const missing = new Set(judgedRun?.inputs.flatMap((input) => input.missing) ?? []);
  const seen = new Set<string>();
  for (const { type, path, state } of current.inputs) {
    if (seen.has(path)) continue;
    seen.add(path);
    if (state) {
      if (state.mtime > evaluation.at)
        reasons.push({
          kind: "input",
          type,
          path,
          change: missing.has(path) ? "created" : "modified",
        });
    } else if (given.has(path) && !missing.has(path)) {
      reasons.push({ kind: "input", type, path, change: "removed" });
    }
  }

  if (judgedRun) {
    const used = judgedRun.skill;
    const now = current.skill;
    if (used && now && used.path === now.path) {
      if (used.sha256 !== now.sha256 && now.mtime > evaluation.at)
        reasons.push({ kind: "skill", path: now.path });
    } else if (used || now) {
      reasons.push({ kind: "skill", path: now?.path ?? null });
    }
  }
  return reasons;
}
