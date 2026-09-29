/* Location patterns (Workspace and data): only `*` and `**` are wildcards; `<case>` is read as `*`. */

import { describe, expect, test } from "bun:test";
import {
  compilePattern,
  isConcrete,
  matchesPattern,
  normalizeLocations,
} from "../../src/model/index.ts";

const matches = (pattern: string, relPath: string, dir = false): boolean =>
  matchesPattern(compilePattern(pattern), relPath, dir);

describe("location patterns", () => {
  test("* matches within one directory level", () => {
    const pattern = "docs/changes/*/stakeholders.md";
    expect(matches(pattern, "docs/changes/CHG-001/stakeholders.md")).toBe(true);
    expect(matches(pattern, "docs/changes/stakeholders.md")).toBe(false);
    expect(matches(pattern, "docs/changes/a/b/stakeholders.md")).toBe(false);
    expect(matches("observations/*.md", "observations/2026-09-27.md")).toBe(true);
    expect(matches("observations/*.md", "observations/2026/09-27.md")).toBe(false);
  });

  test("** matches any number of directory levels, none included", () => {
    for (const relPath of ["docs/x.md", "docs/a/x.md", "docs/a/b/c/x.md"])
      expect(matches("docs/**/x.md", relPath), relPath).toBe(true);
    expect(matches("docs/**/x.md", "other/x.md")).toBe(false);
    expect(matches("docs/**", "docs/a/b.md")).toBe(true);
  });

  test("a trailing / makes each matching directory one Artifact", () => {
    expect(matches("measurements/*/", "measurements/CHG-001", true)).toBe(true);
    expect(matches("measurements/*/", "measurements/CHG-001", false)).toBe(false);
    expect(matches("measurements/*/", "measurements/CHG-001/baseline.json", false)).toBe(false);
    expect(compilePattern("docs/changes/*/design/")).toMatchObject({
      dirOnly: true,
      prefix: "docs/changes",
      depth: 2,
    });
  });

  test("every other character stands for itself, ? included", () => {
    expect(matches("docs/what?.md", "docs/what?.md")).toBe(true);
    expect(matches("docs/what?.md", "docs/whatx.md")).toBe(false);
    expect(matches("releases/*/candidate.json", "releases/r1/candidateXjson")).toBe(false);
    expect(matches("notes/(draft)+[1].md", "notes/(draft)+[1].md")).toBe(true);
  });

  test("scanning starts below the segments that have no wildcard", () => {
    expect(compilePattern("./docs/pilot-context.md")).toMatchObject({
      pattern: "docs/pilot-context.md",
      prefix: "docs",
      depth: 1,
      deep: false,
    });
    expect(compilePattern("*.md")).toMatchObject({ prefix: "", depth: 1 });
    expect(compilePattern("releases/*/candidate.json")).toMatchObject({
      prefix: "releases",
      depth: 2,
    });
    expect(compilePattern("docs/**/x.md")).toMatchObject({ prefix: "docs", deep: true });
  });

  test("<case> of harness 0.8 is read as *", () => {
    expect(
      normalizeLocations(["docs/changes/<case>/change-brief.md", "measurements/{case}/"]),
    ).toEqual(["docs/changes/*/change-brief.md", "measurements/*/"]);
  });

  test("a location without wildcards names one file or directory", () => {
    expect(isConcrete("docs/changes/CHG-002/change-brief.md")).toBe(true);
    expect(isConcrete("docs/changes/CHG-002/design/")).toBe(true);
    expect(isConcrete("docs/changes/*/change-brief.md")).toBe(false);
  });
});
