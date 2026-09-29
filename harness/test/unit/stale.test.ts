/*
 * "The evidence is stale" (Dashboard, instantiation and evaluation records): when one of the
 * instance's inputs or the SKILL.md no longer holds what the judged run used, the evaluation is
 * shown as stale. The comparison is by content (SHA-256), not by modification time.
 */

import { describe, expect, test } from "bun:test";
import { staleness, type CurrentState } from "../../src/harness/index.ts";
import type { Evaluation, Run } from "../../src/shared/types.ts";

const SKILL = "skills/design-solution/SKILL.md";
const BRIEF = "docs/changes/CHG-001/change-brief.md";
const digest = (c: string): string => c.repeat(64);

const evaluation: Evaluation = {
  runId: "r5",
  judgments: [{ outcome: 0, judgment: "achieved", evidence: "Each component traces to a need." }],
  by: { kind: "user" },
  at: 1_000,
};

type JudgedRun = Pick<Run, "inputs" | "skill" | "outputs">;

const judgedRun = (overrides: Partial<JudgedRun> = {}): JudgedRun => ({
  inputs: [
    {
      type: "Change brief",
      role: "input",
      paths: [BRIEF],
      missing: [],
      sha256: { [BRIEF]: digest("a") },
    },
  ],
  skill: { path: SKILL, sha256: digest("s") },
  outputs: [],
  ...overrides,
});

const current = (
  sha256: string | null,
  skill: CurrentState["skill"] = { path: SKILL, sha256: digest("s") },
): CurrentState => ({ inputs: [{ type: "Change brief", path: BRIEF, sha256 }], skill });

describe("stale evaluations", () => {
  test("an instance without an evaluation is never stale", () => {
    expect(staleness(null, judgedRun(), current(digest("b")))).toEqual([]);
  });

  test("inputs and a SKILL.md with the content the judged run used keep the evaluation current, whatever their times", () => {
    expect(staleness(evaluation, judgedRun(), current(digest("a")))).toEqual([]);
  });

  test("an input whose content differs from what the judged run used makes it stale", () => {
    expect(staleness(evaluation, judgedRun(), current(digest("b")))).toEqual([
      { kind: "input", type: "Change brief", path: BRIEF, change: "modified" },
    ]);
  });

  test("an input that the judged run had and that is gone now makes it stale", () => {
    expect(staleness(evaluation, judgedRun(), current(null))).toEqual([
      { kind: "input", type: "Change brief", path: BRIEF, change: "removed" },
    ]);
  });

  test("an input missing at the judged run is a change once it exists, and none while it is still missing", () => {
    const missing = judgedRun({
      inputs: [
        { type: "Change brief", role: "input", paths: [BRIEF], missing: [BRIEF], sha256: {} },
      ],
    });
    expect(staleness(evaluation, missing, current(null))).toEqual([]);
    expect(staleness(evaluation, missing, current(digest("b")))).toEqual([
      { kind: "input", type: "Change brief", path: BRIEF, change: "created" },
    ]);
  });

  test("an input that the judged run itself created or modified is compared with what the run left", () => {
    // The run was missing the brief and wrote it (it is an input and an output of the Process);
    // the digest it left is the one kept.
    const wrote = judgedRun({
      inputs: [
        {
          type: "Change brief",
          role: "input",
          paths: [BRIEF],
          missing: [BRIEF],
          sha256: { [BRIEF]: digest("c") },
        },
      ],
      outputs: [{ type: "Change brief", path: BRIEF, change: "created" }],
    });
    expect(staleness(evaluation, wrote, current(digest("c")))).toEqual([]);
    expect(staleness(evaluation, wrote, current(digest("d")))).toEqual([
      { kind: "input", type: "Change brief", path: BRIEF, change: "modified" },
    ]);
  });

  test("a run recorded before the harness kept digests counts only an input that is gone", () => {
    const old = judgedRun({
      inputs: [{ type: "Change brief", role: "input", paths: [BRIEF], missing: [], sha256: {} }],
    });
    expect(staleness(evaluation, old, current(digest("b")))).toEqual([]);
    expect(staleness(evaluation, old, current(null))).toEqual([
      { kind: "input", type: "Change brief", path: BRIEF, change: "removed" },
    ]);
  });

  test("a path that the judged run did not have says nothing about it", () => {
    const other = judgedRun({
      inputs: [{ type: "Change brief", role: "input", paths: [], missing: [], sha256: {} }],
    });
    expect(staleness(evaluation, other, current(null))).toEqual([]);
  });

  test("a SKILL.md whose content differs from the judged run's makes it stale", () => {
    expect(
      staleness(
        evaluation,
        judgedRun(),
        current(digest("a"), { path: SKILL, sha256: digest("t") }),
      ),
    ).toEqual([{ kind: "skill", path: SKILL }]);
  });

  test("another SKILL.md, or none, describing the Process now makes it stale", () => {
    const other = { path: "skills/other/SKILL.md", sha256: digest("s") };
    expect(staleness(evaluation, judgedRun(), current(digest("a"), other))).toEqual([
      { kind: "skill", path: "skills/other/SKILL.md" },
    ]);
    expect(staleness(evaluation, judgedRun(), current(digest("a"), null))).toEqual([
      { kind: "skill", path: null },
    ]);
    expect(staleness(evaluation, judgedRun({ skill: null }), current(digest("a"), other))).toEqual([
      { kind: "skill", path: "skills/other/SKILL.md" },
    ]);
    expect(staleness(evaluation, judgedRun({ skill: null }), current(digest("a"), null))).toEqual(
      [],
    );
  });

  test("without the judged run's record there is nothing to compare with", () => {
    expect(staleness(evaluation, null, current(null, null))).toEqual([]);
    expect(staleness(evaluation, null, current(digest("b")))).toEqual([]);
  });
});
