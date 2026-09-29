/* Paths that instances name: they must stay inside the workspace. */

import fs from "node:fs";
import path from "node:path";
import { toPosix } from "../model/index.ts";

const isInside = (relative: string): boolean =>
  relative === "" || (!relative.startsWith("..") && !path.isAbsolute(relative));

/** The deepest of `abs` and its ancestors that exists (a dangling symlink counts: it exists as a link). */
function existingAncestor(abs: string): string {
  let current = abs;
  for (;;) {
    try {
      fs.lstatSync(current);
      return current;
    } catch {
      const parent = path.dirname(current);
      if (parent === current) return current;
      current = parent;
    }
  }
}

export type WorkspacePath = { ok: true; path: string } | { ok: false; reason: "outside" | "empty" };

/**
 * A path given for an instance input or output, made relative to the workspace with forward
 * slashes (a trailing slash, which marks a directory, is kept). It is refused when it leaves the
 * workspace: through `..`, as an absolute path elsewhere, or through a symlink that points out of
 * it (also one whose target does not exist yet).
 */
export function workspacePath(root: string, given: string): WorkspacePath {
  const trimmed = given.trim();
  const directory = /[\\/]$/.test(trimmed);
  const abs = path.resolve(root, trimmed);
  const relative = path.relative(root, abs);
  if (!isInside(relative)) return { ok: false, reason: "outside" };
  if (relative === "") return { ok: false, reason: "empty" };
  let realRoot: string;
  try {
    realRoot = fs.realpathSync(root);
  } catch {
    realRoot = root;
  }
  try {
    const real = fs.realpathSync(existingAncestor(abs));
    if (!isInside(path.relative(realRoot, real))) return { ok: false, reason: "outside" };
  } catch {
    // A symlink whose target does not exist: where it leads cannot be checked.
    return { ok: false, reason: "outside" };
  }
  return { ok: true, path: `${toPosix(relative)}${directory ? "/" : ""}` };
}

/** A location without the trailing slash that marks a directory, as provenance and scans name it. */
export const artifactPath = (location: string): string => location.replace(/\/+$/, "");
