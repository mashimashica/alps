/*
 * Converting old records (Workspace and data): a state.json without schemaVersion is converted when
 * read. Work items become instances, their inputs come from the last run's inputs, the case is
 * dropped, and judgment strings are read as judgments without evidence.
 */

import { describe, expect, test } from "bun:test";
import fs from "node:fs";
import path from "node:path";
import { instanceIdOf, migrateStateV1 } from "../../src/harness/index.ts";
import { stateFileSchema, stateFileV1Schema } from "../../src/shared/schema.ts";
import type { StateFileV1 } from "../../src/shared/types.ts";
import { FIXTURES } from "../helpers/paths.ts";

const NOW = 1_800_000_000_000;

const fixture = (): StateFileV1 => {
  const parsed = stateFileV1Schema.safeParse(
    JSON.parse(fs.readFileSync(path.join(FIXTURES, "state-v1.json"), "utf8")),
  );
  if (!parsed.success) throw parsed.error;
  return parsed.data;
};

describe("version 1 records", () => {
  test("work items become instances whose inputs come from the last run's inputs, and the case is dropped", () => {
    const { state } = migrateStateV1(fixture(), NOW);
    expect(Object.keys(state.instances).sort()).toEqual(["i1", "i4", "i6"]);
    expect(state.instances.i4).toEqual({
      id: "i4",
      process: "解決案の設計",
      inputs: { 変更概要: ["docs/changes/CHG-001/change-summary.md"] },
      // A concrete target of the last run is the output location; a pattern leaves it to the agent.
      outputs: { 設計記述: "docs/changes/CHG-001/design/" },
      criteria: [],
      notes: "",
      runs: ["r5"],
      evaluation: {
        runId: "r5",
        judgments: [
          { outcome: 0, judgment: "achieved", evidence: "" },
          { outcome: 1, judgment: "achieved", evidence: "" },
        ],
        by: { kind: "user" },
        at: 1790615022852,
      },
    });
    expect(state.instances.i1?.outputs).toEqual({ 候補版: null });
    expect(state.instances.i6).toMatchObject({
      inputs: {},
      outputs: {},
      runs: [],
      evaluation: null,
    });
    expect(JSON.stringify(state)).not.toMatch(/"(case|plannedStart|plannedEnd|workItems?|review)"/);
  });

  test("judgment strings become judgments without evidence by a user; others are dropped", () => {
    const v1 = fixture();
    v1.workItems.w4!.review = {
      runId: "r5",
      judgments: ["achieved", "maybe", "not-achieved"],
      note: "Checked by hand.",
      at: 5,
    };
    const { state } = migrateStateV1(v1, NOW);
    expect(state.instances.i4?.evaluation).toEqual({
      runId: "r5",
      judgments: [
        { outcome: 0, judgment: "achieved", evidence: "" },
        { outcome: 2, judgment: "not-achieved", evidence: "" },
      ],
      note: "Checked by hand.",
      by: { kind: "user" },
      at: 5,
    });
  });

  test("runs keep their ids and move to their own records; a run left running is interrupted", () => {
    const v1 = fixture();
    v1.runs.r3!.status = "running";
    v1.runs.r3!.endedAt = null;
    const { state, runs } = migrateStateV1(v1, NOW);
    expect(runs.map((run) => run.id).sort()).toEqual(["r2", "r3", "r5"]);
    const r5 = runs.find((run) => run.id === "r5");
    expect(r5).toMatchObject({
      kind: "process",
      instance: "i4",
      report: v1.runs.r5?.summary,
      client: null,
    });
    // Version 1 kept no digests of the inputs.
    expect(r5?.inputs).toEqual([
      {
        type: "変更概要",
        role: "input",
        paths: ["docs/changes/CHG-001/change-summary.md"],
        missing: [],
        sha256: {},
      },
    ]);
    for (const key of ["case", "workItem", "summary"]) expect(r5).not.toHaveProperty(key);
    expect(runs.find((run) => run.id === "r3")).toMatchObject({
      status: "interrupted",
      endedAt: NOW,
    });
    expect(state.runs.r3).toEqual({
      id: "r3",
      kind: "process",
      instance: "i1",
      status: "interrupted",
      startedAt: v1.runs.r3!.startedAt,
      endedAt: NOW,
    });
  });

  test("the result is a version 2 state that keeps provenance and the sequence", () => {
    const v1 = fixture();
    const { state } = migrateStateV1(v1, NOW);
    expect(stateFileSchema.safeParse(state).success).toBe(true);
    expect(state).toMatchObject({
      schemaVersion: 2,
      provenance: v1.provenance,
      seq: 6,
      lastWakeAt: null,
    });
    // An id above the recorded sequence raises it, so new ids never collide.
    expect(migrateStateV1({ ...v1, seq: 2 }, NOW).state.seq).toBe(6);
  });

  test("work item w<n> becomes instance i<n>", () => {
    expect(instanceIdOf("w12")).toBe("i12");
    expect(instanceIdOf("custom")).toBe("custom");
  });
});
