/*
 * Provenance (Workspace and data): a run's outputs are what its output locations gained or changed
 * while it ran, apart from what runs that ran at the same time can be told to have changed; what
 * runs at the same time both hold is marked shared.
 */

import { describe, expect, test } from "bun:test";
import {
  attributeOutputs,
  diffOutputs,
  shareOutputs,
  wildcardValues,
  type Attribution,
  type OutputSnapshot,
} from "../../src/harness/index.ts";
import { signature } from "../../src/model/index.ts";
import type { RunOutput } from "../../src/shared/types.ts";

// A write changes the status-change time with the modification time; the inode stays.
const file = (mtime: number, size: number) =>
  signature({ dir: false, size, items: null, mtime, ctime: mtime, ino: 1 });
const dir = (mtime: number, items: number) =>
  signature({ dir: true, size: null, items, mtime, ctime: mtime, ino: 2 });

const snapshot = (entries: [string, string, string][]): OutputSnapshot =>
  new Map(entries.map(([path, type, sig]) => [path, { type, signature: sig }]));

describe("provenance", () => {
  test("the outputs of a run are the paths that are new or changed between the snapshots before and after it", () => {
    const before = snapshot([
      ["docs/changes/CHG-001/change-brief.md", "Change brief", file(100, 393)],
      ["docs/changes/CHG-002/change-brief.md", "Change brief", file(100, 50)],
      ["docs/changes/CHG-001/design", "Design description", dir(100, 2)],
    ]);
    const after = snapshot([
      ["docs/changes/CHG-001/change-brief.md", "Change brief", file(100, 393)],
      ["docs/changes/CHG-002/change-brief.md", "Change brief", file(200, 50)],
      ["docs/changes/CHG-003/change-brief.md", "Change brief", file(200, 80)],
      ["docs/changes/CHG-001/design", "Design description", dir(200, 3)],
    ]);
    expect(diffOutputs(before, after)).toEqual([
      { type: "Change brief", path: "docs/changes/CHG-002/change-brief.md", change: "modified" },
      { type: "Change brief", path: "docs/changes/CHG-003/change-brief.md", change: "created" },
      { type: "Design description", path: "docs/changes/CHG-001/design", change: "modified" },
    ]);
  });

  test("an unchanged location has no outputs, and a removed path is not an output", () => {
    const before = snapshot([
      ["releases/CHG-001/candidate.json", "Release candidate", file(100, 258)],
      ["releases/CHG-002/candidate.json", "Release candidate", file(100, 258)],
    ]);
    const after = snapshot([
      ["releases/CHG-001/candidate.json", "Release candidate", file(100, 258)],
    ]);
    expect(diffOutputs(before, after)).toEqual([]);
  });

  test("a file and a directory at the same path with the same time and count differ", () => {
    expect(file(100, 2)).not.toBe(dir(100, 2));
  });
});

const BRIEF = "docs/changes/*/change-brief.md";
const brief = (id: string, change: RunOutput["change"] = "created"): RunOutput => ({
  type: "Change brief",
  path: `docs/changes/${id}/change-brief.md`,
  change,
});
const within = (patterns: string[]): Attribution["locations"] => [
  { type: "Change brief", patterns, paths: [] },
];

describe("provenance of a run alone", () => {
  test("a run alone has every change within its pattern, whatever its inputs, and at a concrete location that path alone", () => {
    // A run of Requirements Clarification from the CHG-003 stakeholders, with no run at the same
    // time, wrote the CHG-003 and the CHG-004 briefs.
    const attribution: Attribution = {
      locations: within([BRIEF]),
      changes: [brief("CHG-003"), brief("CHG-004")],
      inputs: ["docs/changes/CHG-003/stakeholders.md"],
      claimed: [],
      alone: true,
    };
    expect(attributeOutputs(attribution)).toEqual([brief("CHG-003"), brief("CHG-004")]);
    // Only with a run at the same time does the input prefer the CHG-003 brief.
    expect(attributeOutputs({ ...attribution, alone: false })).toEqual([brief("CHG-003")]);
    // A concrete location holds only its own change, alone too.
    expect(
      attributeOutputs({
        ...attribution,
        locations: [
          { type: "Change brief", patterns: [], paths: ["docs/changes/CHG-004/change-brief.md"] },
        ],
      }),
    ).toEqual([brief("CHG-004")]);
  });
});

describe("provenance of runs at the same time", () => {
  test("an input gives the wildcard directories of an output pattern their values, read from the start", () => {
    const values = (pattern: string, path: string) =>
      Object.fromEntries(wildcardValues(pattern, path));
    expect(values(BRIEF, "docs/changes/CHG-003/stakeholders.md")).toEqual({ 2: "CHG-003" });
    // A deeper input and a directory Artifact agree as far as they go.
    expect(values(BRIEF, "docs/changes/CHG-003/interviews/alice.md")).toEqual({ 2: "CHG-003" });
    expect(values("docs/changes/*/design/", "docs/changes/CHG-001/change-brief.md")).toEqual({
      2: "CHG-001",
    });
    expect(values("releases/v-*/candidate.json", "releases/v-2/candidate.json")).toEqual({
      1: "v-2",
    });
    // An input elsewhere gives nothing, and the Artifact's own name is never read.
    expect(values(BRIEF, "observations/2026-09-27.md")).toEqual({});
    expect(values("observations/*.md", "observations/2026-09-27.md")).toEqual({});
    expect(values("releases/v-*/candidate.json", "releases/2/candidate.json")).toEqual({});
    // `**` takes the rest as the last directory, and ends the reading elsewhere.
    expect(values("docs/**/change-brief.md", "docs/changes/CHG-003/stakeholders.md")).toEqual({
      1: "changes/CHG-003",
    });
    expect(values("docs/*/**/design/x.md", "docs/changes/CHG-003/design/y.md")).toEqual({
      1: "changes",
    });
  });

  test("at a concrete location a run's output is that path alone (stage 7b: r20 took the brief that r19 created)", () => {
    // r20 (Feasibility Assessment of CHG-002) and r19 (Requirements Clarification of CHG-003)
    // ran at the same time; r19 created the CHG-003 brief.
    const outputs = attributeOutputs({
      locations: [
        { type: "Change brief", patterns: [], paths: ["docs/changes/CHG-002/change-brief.md"] },
      ],
      changes: [brief("CHG-002", "modified"), brief("CHG-003")],
      inputs: ["docs/changes/CHG-002/change-brief.md", "observations/2026-09-27.md"],
      claimed: ["docs/changes/CHG-003/change-brief.md"],
    });
    expect(outputs).toEqual([brief("CHG-002", "modified")]);
  });

  test("within a pattern the changes that agree with the inputs are preferred to those that disagree", () => {
    const attribution: Attribution = {
      locations: within([BRIEF]),
      changes: [brief("CHG-002", "modified"), brief("CHG-003")],
      inputs: ["docs/changes/CHG-003/stakeholders.md"],
      claimed: [],
    };
    expect(attributeOutputs(attribution)).toEqual([brief("CHG-003")]);
    // Inputs of two changes keep both.
    expect(
      attributeOutputs({
        ...attribution,
        inputs: ["docs/changes/CHG-003/stakeholders.md", "docs/changes/CHG-002/change-brief.md"],
      }),
    ).toEqual([brief("CHG-002", "modified"), brief("CHG-003")]);
    // When no change agrees, or no input gives the wildcard a value, all are kept.
    expect(
      attributeOutputs({ ...attribution, inputs: ["docs/changes/CHG-009/stakeholders.md"] }),
    ).toEqual([...attribution.changes]);
    expect(attributeOutputs({ ...attribution, inputs: ["observations/2026-09-27.md"] })).toEqual([
      ...attribution.changes,
    ]);
    // A change that the instance's own pattern holds without a wildcard directory is kept.
    const own: RunOutput = {
      type: "Change brief",
      path: "docs/changes/CHG-003/notes.md",
      change: "created",
    };
    expect(
      attributeOutputs({
        ...attribution,
        locations: within(["docs/changes/CHG-003/*.md", BRIEF]),
        changes: [brief("CHG-002", "modified"), brief("CHG-003"), own],
      }),
    ).toEqual([brief("CHG-003"), own]);
  });

  test("within a pattern, what a run at the same time names as its concrete location is not an output", () => {
    const outputs = attributeOutputs({
      locations: [
        { type: "Change brief", patterns: [BRIEF], paths: [] },
        { type: "Design description", patterns: ["docs/changes/**/*.md"], paths: [] },
      ],
      changes: [
        brief("CHG-002", "modified"),
        brief("r9"),
        {
          type: "Design description",
          path: "docs/changes/CHG-001/design/components.md",
          change: "modified",
        },
      ],
      inputs: ["observations/2026-09-27.md"],
      claimed: ["docs/changes/CHG-002/change-brief.md", "docs/changes/CHG-001/design"],
    });
    expect(outputs).toEqual([brief("r9")]);
    // The same concrete location of two runs is each one's output: the harness marks it shared.
    expect(
      attributeOutputs({
        locations: [
          { type: "Change brief", patterns: [], paths: ["docs/changes/CHG-002/change-brief.md"] },
        ],
        changes: [brief("CHG-002", "modified")],
        inputs: [],
        claimed: ["docs/changes/CHG-002/change-brief.md"],
      }),
    ).toEqual([brief("CHG-002", "modified")]);
  });

  test("a change that runs at the same time both hold is marked in each, once", () => {
    const shared = shareOutputs({ id: "r20", outputs: [brief("CHG-003")] }, [
      { id: "r19", outputs: [brief("CHG-003"), brief("CHG-009")] },
      { id: "r18", outputs: [brief("CHG-001")] },
    ]);
    expect(shared.outputs).toEqual([{ ...brief("CHG-003"), sharedWith: ["r19"] }]);
    expect([...shared.others]).toEqual([
      ["r19", [{ ...brief("CHG-003"), sharedWith: ["r20"] }, brief("CHG-009")]],
    ]);
    const again = shareOutputs({ id: "r21", outputs: shared.outputs }, [
      { id: "r19", outputs: shared.others.get("r19") ?? [] },
    ]);
    expect(again.outputs).toEqual([{ ...brief("CHG-003"), sharedWith: ["r19"] }]);
    expect(again.others.get("r19")?.[0]).toEqual({
      ...brief("CHG-003"),
      sharedWith: ["r20", "r21"],
    });
    expect(shareOutputs({ id: "r20", outputs: [brief("CHG-002")] }, [])).toEqual({
      outputs: [brief("CHG-002")],
      others: new Map(),
    });
  });
});
