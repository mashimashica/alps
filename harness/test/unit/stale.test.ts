/*
 * "The evidence is stale" (Dashboard, instantiation and evaluation records): when one of the
 * instance's inputs or the SKILL.md changes after the judgment, the evaluation is shown as stale.
 */

import { describe, expect, test } from "bun:test";
import { staleness, type CurrentState } from "../../src/harness/index.ts";
import type { FileState } from "../../src/model/index.ts";
import type { Evaluation, Run } from "../../src/shared/types.ts";

const JUDGED_AT = 1_000;
const SKILL = "skills/design-solution/SKILL.md";

const evaluation: Evaluation = {
  runId: "r5",
  judgments: [{ outcome: 0, judgment: "achieved", evidence: "Each component traces to a need." }],
  by: { kind: "user" },
  at: JUDGED_AT,
};

const judgedRun = (
  inputs: Run["inputs"] = [
    {
      type: "Change brief",
      role: "input",
      paths: ["docs/changes/CHG-001/change-brief.md"],
      missing: [],
    },
  ],
  skill: Run["skill"] = { path: SKILL, sha256: "a".repeat(64) },
): Pick<Run, "inputs" | "skill"> => ({ inputs, skill });

const at = (mtime: number): FileState => ({ dir: false, size: 10, items: null, mtime });

const current = (
  state: FileState | null,
  skill: CurrentState["skill"] = { path: SKILL, sha256: "a".repeat(64), mtime: 500 },
  path = "docs/changes/CHG-001/change-brief.md",
): CurrentState => ({ inputs: [{ type: "Change brief", path, state }], skill });

describe("stale evaluations", () => {
  test("an instance without an evaluation is never stale", () => {
    expect(staleness(null, judgedRun(), current(at(5_000)))).toEqual([]);
  });

  test("nothing that changed before the judgment makes it stale", () => {
    expect(staleness(evaluation, judgedRun(), current(at(JUDGED_AT - 1)))).toEqual([]);
  });

  test("an input modified after the judgment makes it stale", () => {
    expect(staleness(evaluation, judgedRun(), current(at(JUDGED_AT + 1)))).toEqual([
      {
        kind: "input",
        type: "Change brief",
        path: "docs/changes/CHG-001/change-brief.md",
        change: "modified",
      },
    ]);
  });

  test("an input that the judged run had and that is gone now makes it stale", () => {
    expect(staleness(evaluation, judgedRun(), current(null))).toEqual([
      {
        kind: "input",
        type: "Change brief",
        path: "docs/changes/CHG-001/change-brief.md",
        change: "removed",
      },
    ]);
  });

  test("an input missing at the judged run is a change once it is created after the judgment, and none while it is still missing", () => {
    const missing = judgedRun([
      {
        type: "Change brief",
        role: "input",
        paths: ["docs/changes/CHG-001/change-brief.md"],
        missing: ["docs/changes/CHG-001/change-brief.md"],
      },
    ]);
    expect(staleness(evaluation, missing, current(null))).toEqual([]);
    expect(staleness(evaluation, missing, current(at(JUDGED_AT + 1)))).toEqual([
      {
        kind: "input",
        type: "Change brief",
        path: "docs/changes/CHG-001/change-brief.md",
        change: "created",
      },
    ]);
  });

  test("a SKILL.md whose content differs from the judged run's and that was modified after the judgment makes it stale", () => {
    const edited = { path: SKILL, sha256: "b".repeat(64), mtime: JUDGED_AT + 1 };
    expect(staleness(evaluation, judgedRun(), current(at(0), edited))).toEqual([
      { kind: "skill", path: SKILL },
    ]);
    // Touched after the judgment with the same content, or changed before it: not stale.
    expect(
      staleness(evaluation, judgedRun(), current(at(0), { ...edited, sha256: "a".repeat(64) })),
    ).toEqual([]);
    expect(
      staleness(evaluation, judgedRun(), current(at(0), { ...edited, mtime: JUDGED_AT - 1 })),
    ).toEqual([]);
  });

  test("another SKILL.md, or none, describing the Process now makes it stale", () => {
    const other = { path: "skills/other/SKILL.md", sha256: "c".repeat(64), mtime: 0 };
    expect(staleness(evaluation, judgedRun(), current(at(0), other))).toEqual([
      { kind: "skill", path: "skills/other/SKILL.md" },
    ]);
    expect(staleness(evaluation, judgedRun(), current(at(0), null))).toEqual([
      { kind: "skill", path: null },
    ]);
    expect(staleness(evaluation, judgedRun(undefined, null), current(at(0), other))).toEqual([
      { kind: "skill", path: "skills/other/SKILL.md" },
    ]);
    expect(staleness(evaluation, judgedRun(undefined, null), current(at(0), null))).toEqual([]);
  });

  test("without the judged run's record, only inputs modified after the judgment count", () => {
    expect(staleness(evaluation, null, current(null, null))).toEqual([]);
    expect(staleness(evaluation, null, current(at(JUDGED_AT + 1), null))).toEqual([
      {
        kind: "input",
        type: "Change brief",
        path: "docs/changes/CHG-001/change-brief.md",
        change: "modified",
      },
    ]);
  });
});
