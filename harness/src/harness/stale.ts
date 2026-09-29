/*
 * "The evidence is stale" (Process Framework §8): one of the instance's inputs or the Process's
 * SKILL.md no longer holds what the judged run used, so the judgment has to be reconsidered. The
 * comparison is by content (SHA-256), not by modification time: touching a file changes nothing,
 * and an edit counts even when it keeps the time.
 */

import type { Evaluation, Run, StaleReason } from "../shared/types.ts";

/** What the workspace holds now for an instance. */
export interface CurrentState {
  /** Every input path of the instance with the SHA-256 of its content now; `null` when nothing is there. */
  inputs: { type: string; path: string; sha256: string | null }[];
  /** The SKILL.md that describes the Process now, with the SHA-256 of its content, or `null` when none is found. */
  skill: { path: string; sha256: string | null } | null;
}

/**
 * Why an evaluation is stale; empty when it is not, when there is no evaluation, and when the
 * judged run's record cannot be read (there is nothing to compare with).
 *
 * An input is compared with its content as the judged run used it (RunInput.sha256): the content
 * when the run started, or when it ended for a path the run itself created or modified. It is
 * modified when the digest differs, removed when it is gone although it was there, and created
 * when it is there although it was missing and the run did not create it. A record from before the
 * harness kept digests tells only that a path was there, so only its removal counts. The SKILL.md
 * changed when its digest differs from the one the judged run used, or when another SKILL.md (or
 * none) describes the Process now.
 */
export function staleness(
  evaluation: Evaluation | null,
  judgedRun: Pick<Run, "inputs" | "skill" | "outputs"> | null,
  current: CurrentState,
): StaleReason[] {
  if (!evaluation || !judgedRun) return [];
  const reasons: StaleReason[] = [];
  const given = new Set<string>();
  const used = new Map<string, string>();
  const missing = new Set<string>();
  for (const input of judgedRun.inputs) {
    for (const path of input.paths) given.add(path);
    for (const [path, sha256] of Object.entries(input.sha256)) used.set(path, sha256);
    for (const path of input.missing) missing.add(path);
  }
  const produced = new Set(judgedRun.outputs.map((output) => output.path));

  const seen = new Set<string>();
  for (const { type, path, sha256 } of current.inputs) {
    // A path that the judged run did not have (an instance converted from version 1 takes its
    // inputs from its last run) says nothing about that run.
    if (seen.has(path) || !given.has(path)) continue;
    seen.add(path);
    const before = used.get(path);
    let change: "modified" | "created" | "removed" | null = null;
    if (before !== undefined) {
      if (sha256 === null) change = "removed";
      else if (sha256 !== before) change = "modified";
    } else if (missing.has(path)) {
      if (sha256 !== null && !produced.has(path)) change = "created";
    } else if (sha256 === null) {
      change = "removed";
    }
    if (change) reasons.push({ kind: "input", type, path, change });
  }

  const skillUsed = judgedRun.skill;
  const skillNow = current.skill;
  if (skillUsed && skillNow && skillUsed.path === skillNow.path) {
    if (skillUsed.sha256 !== skillNow.sha256) reasons.push({ kind: "skill", path: skillNow.path });
  } else if (skillUsed || skillNow) {
    reasons.push({ kind: "skill", path: skillNow?.path ?? null });
  }
  return reasons;
}
