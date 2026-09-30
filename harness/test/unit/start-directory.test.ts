/*
 * Where the workspace is looked for (Workspace and data): ALPS_WORKSPACE, or the current directory
 * when it is not set, or when it still holds a variable that the client did not expand and names
 * no existing path.
 */

import { describe, expect, test } from "bun:test";
import path from "node:path";
import { startDirectory } from "../../src/model/index.ts";

describe("the start directory", () => {
  test("ALPS_WORKSPACE is used unless it is unset, or holds ${ and names no existing path", () => {
    const cwd = path.resolve("/cwd");
    const named = path.resolve("/work/a${x}b");
    const exists = (p: string): boolean => p === named;
    expect(startDirectory("/work/project", cwd, exists)).toBe("/work/project");
    expect(startDirectory(undefined, cwd, exists)).toBe(cwd);
    expect(startDirectory("", cwd, exists)).toBe(cwd);
    // Claude Code 2.1.96 passed the Plugin's ALPS_WORKSPACE unexpanded.
    expect(startDirectory("${CLAUDE_PROJECT_DIR}", cwd, exists)).toBe(cwd);
    // A directory whose name holds ${…} is used when it exists.
    expect(startDirectory(named, cwd, exists)).toBe(named);
  });
});
