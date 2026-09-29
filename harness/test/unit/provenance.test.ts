/* Provenance (Workspace and data): a run's outputs are what its output locations gained or changed while it ran. */

import { describe, expect, test } from "bun:test";
import { diffOutputs, type OutputSnapshot } from "../../src/harness/index.ts";
import { signature } from "../../src/model/index.ts";

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
