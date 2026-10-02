/*
 * The records of an assessment, worked out by hand: an evaluation that replaces another keeps it
 * at the front of the instance's evaluations (supersede); what the records gained after an
 * assessment's run started counts the process runs and the Outcome judgments since then, those
 * of replaced evaluations included and wake and assessment runs left out, within a Process and an
 * agent (countSince); and the items of an assessment rest on evidence that the records have,
 * except an unverified one (checkedItems).
 */

import { describe, expect, test } from "bun:test";
import { countSince, type StatsRunRecord } from "../../src/assess.ts";
import {
  checkedItems,
  type EvidenceRecords,
  type ItemDraft,
} from "../../src/harness/assessment.ts";
import { HarnessError } from "../../src/harness/errors.ts";
import { supersede } from "../../src/harness/harness.ts";
import type { Evaluation, Instance } from "../../src/shared/types.ts";

const evaluation = (runId: string, at: number, outcomes = 1): Evaluation => ({
  runId,
  judgments: Array.from({ length: outcomes }, (_, outcome) => ({
    outcome,
    judgment: "achieved" as const,
    evidence: `Read the output of ${runId}.`,
  })),
  by: { kind: "user" },
  at,
});

const instance = (id: string, process: string): Instance => ({
  id,
  process,
  inputs: {},
  outputs: {},
  criteria: [],
  notes: "",
  runs: [],
  evaluation: null,
});

const run = (
  id: string,
  kind: StatsRunRecord["kind"],
  startedAt: number,
  options: { process?: string; agent?: string } = {},
): StatsRunRecord => ({
  id,
  kind,
  instance: kind === "process" ? "i1" : null,
  process: kind === "process" ? (options.process ?? "design") : null,
  agent: options.agent ?? "demo",
  status: "succeeded",
  startedAt,
  endedAt: startedAt + 10,
  usage: null,
});

describe("supersede", () => {
  test("an evaluation that replaces another keeps it at the front of evaluations, newest first", () => {
    const target = instance("i1", "design");
    supersede(target, evaluation("r1", 100));
    expect(target.evaluation?.runId).toBe("r1");
    expect(target.evaluations).toBeUndefined();
    supersede(target, evaluation("r2", 200));
    expect(target.evaluation?.runId).toBe("r2");
    expect(target.evaluations?.map((e) => e.runId)).toEqual(["r1"]);
    supersede(target, evaluation("r3", 300));
    expect(target.evaluation?.runId).toBe("r3");
    expect(target.evaluations?.map((e) => e.runId)).toEqual(["r2", "r1"]);
  });
});

describe("countSince", () => {
  const runs = [
    run("r1", "process", 100),
    run("r2", "process", 500, { agent: "codex" }),
    run("r3", "wake", 600),
    run("r4", "assess", 700),
    run("r5", "process", 800, { process: "release" }),
  ];
  const design = instance("i1", "design");
  const release = instance("i2", "release");
  // i1: judged twice, once before and once after 400; the second replaced the first.
  supersede(design, evaluation("r1", 300, 2));
  supersede(design, evaluation("r2", 550, 2));
  // i2: judged once after 400.
  supersede(release, evaluation("r5", 900, 3));

  test("the process runs that started, and the judgments made, from the start on", () => {
    // r2 and r5 are process runs from 400 on; the wake and the assessment do not count. Two
    // judgments of i1 (the evaluation now) and three of i2; the replaced one was made before 400.
    expect(countSince({ instances: [design, release], runs }, 400)).toEqual({
      runs: 2,
      judgments: 5,
    });
  });

  test("the judgments of the evaluations that later ones replaced count too", () => {
    expect(countSince({ instances: [design, release], runs }, 200)).toEqual({
      runs: 2,
      judgments: 7,
    });
  });

  test("nothing counts before a run or a judgment comes", () => {
    expect(countSince({ instances: [design, release], runs }, 1000)).toEqual({
      runs: 0,
      judgments: 0,
    });
  });

  test("within the scope's Process and agent, as the statistics count them", () => {
    expect(countSince({ instances: [design, release], runs }, 400, { process: "design" })).toEqual({
      runs: 1,
      judgments: 2,
    });
    // The agent's runs, and the judgments about the runs it performed (r2's).
    expect(countSince({ instances: [design, release], runs }, 0, { agent: "codex" })).toEqual({
      runs: 1,
      judgments: 2,
    });
  });
});

describe("checkedItems", () => {
  /** A run r1 with 5 events, a run r2 whose record cannot be read, i1 evaluated, i2 not. */
  const records: EvidenceRecords = {
    run: (id) => (id === "r1" ? { events: 5 } : id === "r2" ? { events: null } : null),
    observation: (id) => (id === "r1:o1" ? { run: "r1" } : null),
    instance: (id) =>
      id === "i1" ? { evaluated: true } : id === "i2" ? { evaluated: false } : null,
    path: (given, where) => {
      if (given.startsWith(".."))
        throw new HarnessError("outside-workspace", {
          key: "error.outside",
          args: { where, path: given, root: "/w" },
        });
      return given === "docs/a.md" || given === "/w/docs/a.md" ? "docs/a.md" : null;
    },
  };
  const item = (overrides: Partial<ItemDraft>): ItemDraft => ({
    kind: "configuration",
    subject: {},
    statement: "A statement.",
    evidence: [{ run: "r1" }],
    ...overrides,
  });
  const refusal = (items: ItemDraft[]): { code: string; key: string } => {
    try {
      checkedItems(items, records);
    } catch (error) {
      if (error instanceof HarnessError) return { code: error.code, key: error.key };
      throw error;
    }
    throw new Error("the items were not refused");
  };

  test("the items are numbered from 1, and their paths made relative to the workspace", () => {
    const items = checkedItems(
      [
        item({ evidence: [{ run: "r1" }, { log: { run: "r1", n: 5 } }, { path: "/w/docs/a.md" }] }),
        item({ kind: "description", evidence: [{ evaluation: "i1" }, { instance: "i2" }] }),
        item({
          kind: "operation",
          evidence: [{ stat: { filter: { period: "30d" }, metric: "runSuccess" } }],
          limits: "Only 30 days.",
        }),
        item({ kind: "unverified", evidence: [] }),
      ],
      records,
    );
    expect(items.map((i) => i.n)).toEqual([1, 2, 3, 4]);
    expect(items[0]?.evidence).toEqual([
      { run: "r1" },
      { log: { run: "r1", n: 5 } },
      { path: "docs/a.md" },
    ]);
    expect(items[2]?.limits).toBe("Only 30 days.");
    expect(items[3]?.evidence).toEqual([]);
  });

  test("an item without evidence is refused unless it is unverified", () => {
    expect(refusal([item({ evidence: [] })])).toEqual({
      code: "invalid-request",
      key: "error.noEvidence",
    });
    expect(() => checkedItems([item({ kind: "unverified", evidence: [] })], records)).not.toThrow();
  });

  test("evidence that names what the records do not have is refused", () => {
    expect(refusal([item({ evidence: [{ run: "r9" }] })]).key).toBe("error.evidenceRun");
    expect(refusal([item({ evidence: [{ instance: "i9" }] })]).key).toBe("error.evidenceInstance");
    expect(refusal([item({ evidence: [{ evaluation: "i2" }] })]).key).toBe(
      "error.evidenceEvaluation",
    );
    expect(refusal([item({ evidence: [{ log: { run: "r1", n: 6 } }] })]).key).toBe(
      "error.evidenceLog",
    );
    expect(refusal([item({ evidence: [{ log: { run: "r9", n: 1 } }] })]).key).toBe(
      "error.evidenceRun",
    );
    expect(refusal([item({ evidence: [{ path: "docs/none.md" }] })]).key).toBe(
      "error.evidencePath",
    );
    expect(refusal([item({ evidence: [{ path: "../outside.md" }] })]).code).toBe(
      "outside-workspace",
    );
  });

  test("an event of a run whose record cannot be read is not checked against its log", () => {
    expect(() =>
      checkedItems([item({ evidence: [{ log: { run: "r2", n: 99 } }] })], records),
    ).not.toThrow();
  });

  test("the first problem is refused, by the item's number", () => {
    try {
      checkedItems([item({}), item({ evidence: [] })], records);
      throw new Error("not refused");
    } catch (error) {
      expect((error as HarnessError).args).toEqual({ n: 2 });
    }
  });
});
