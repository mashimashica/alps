/*
 * What the harness checks in an assessment before it records it: every item rests on evidence,
 * unless it is unverified, and the evidence names records that exist: a run (and, for an event of
 * its log, that event), an instance (and, for its evaluation, one), or a path in the workspace,
 * which is kept relative to it. A cut of the statistics is kept as given. Nothing here reads the
 * records itself: the harness answers what the check asks (EvidenceRecords).
 */

import type { AssessmentItem, Evidence } from "../shared/types.ts";
import { refuse } from "./errors.ts";

/** What checking the evidence needs to know of the records. */
export interface EvidenceRecords {
  /** A run, or `null` when there is none; `events` is `null` when its record cannot be read. */
  run(id: string): { events: number | null } | null;
  /** A bounded run observation, or `null` when no run records it. */
  observation(id: string): { run: string } | null;
  /** An instance, or `null` when there is none; `evaluated` once it has had an evaluation. */
  instance(id: string): { evaluated: boolean } | null;
  /**
   * The path relative to the workspace, or `null` when nothing is there. A path outside the
   * workspace or in its records is refused (thrown) as an instance's would be.
   */
  path(given: string, where: string): string | null;
}

/** An item as the agent gave it, its subject already put in the model's ids. */
export type ItemDraft = Omit<AssessmentItem, "n">;

/**
 * The items numbered from 1, with their evidence checked and its paths made relative to the
 * workspace. Throws the refusal of the first problem (invalid-request, or outside-workspace for a
 * path there).
 */
export function checkedItems(
  items: readonly ItemDraft[],
  records: EvidenceRecords,
): AssessmentItem[] {
  return items.map((item, i) => {
    const n = i + 1;
    if (item.evidence.length === 0 && item.kind !== "unverified")
      throw refuse("invalid-request", "error.noEvidence", { n });
    const evidence = item.evidence.map((cited, k): Evidence => {
      if ("run" in cited) {
        if (!records.run(cited.run))
          throw refuse("invalid-request", "error.evidenceRun", { n, run: cited.run });
        return cited;
      }
      if ("instance" in cited) {
        if (!records.instance(cited.instance))
          throw refuse("invalid-request", "error.evidenceInstance", {
            n,
            instance: cited.instance,
          });
        return cited;
      }
      if ("evaluation" in cited) {
        const instance = records.instance(cited.evaluation);
        if (!instance)
          throw refuse("invalid-request", "error.evidenceInstance", {
            n,
            instance: cited.evaluation,
          });
        if (!instance.evaluated)
          throw refuse("invalid-request", "error.evidenceEvaluation", {
            n,
            instance: cited.evaluation,
          });
        return cited;
      }
      if ("observation" in cited) {
        if (!records.observation(cited.observation))
          throw refuse("invalid-request", "error.evidenceObservation", {
            n,
            observation: cited.observation,
          });
        return cited;
      }
      if ("log" in cited) {
        const run = records.run(cited.log.run);
        if (!run) throw refuse("invalid-request", "error.evidenceRun", { n, run: cited.log.run });
        if (run.events !== null && cited.log.n > run.events)
          throw refuse("invalid-request", "error.evidenceLog", {
            n,
            run: cited.log.run,
            event: cited.log.n,
            events: run.events,
          });
        return cited;
      }
      if ("path" in cited) {
        const found = records.path(cited.path, `items.${i}.evidence.${k}.path`);
        if (found === null)
          throw refuse("invalid-request", "error.evidencePath", { n, path: cited.path });
        return { path: found };
      }
      return cited;
    });
    return {
      n,
      kind: item.kind,
      subject: item.subject,
      statement: item.statement,
      evidence,
      ...(item.limits ? { limits: item.limits } : {}),
    };
  });
}
