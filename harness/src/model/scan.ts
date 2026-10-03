/*
 * Scanning the workspace for the Artifacts that match location patterns, and the state of one
 * path, which the harness compares before and after a run and against a judgment.
 */

import fs from "node:fs";
import path from "node:path";
import { SKIP_DIRS } from "./files.ts";
import { compilePattern, matchesPattern, type LocationPattern } from "./patterns.ts";

/** Directory levels read below a pattern's prefix when the pattern has `**`. */
const MAX_DEEP_LEVELS = 12;
/** Directory levels read inside a directory Artifact. */
export const MAX_DIR_LEVELS = 4;
/** Files counted inside a directory Artifact. */
export const MAX_DIR_FILES = 500;
/** Matches read per pattern. */
export const SCAN_LIMIT = 2000;

/**
 * The state of a file or directory Artifact. A directory is one unit: its newest file and its file
 * count. The modification time and the size can be kept by a write (`cp -p`, `touch -r`); the
 * status-change time cannot, and a file put in the place of another has another inode.
 */
export interface FileState {
  dir: boolean;
  size: number | null;
  items: number | null;
  mtime: number;
  /** The latest status change (ctimeMs): of the file, or of the directory and the files in it. */
  ctime: number;
  /** The inode of the file or directory. */
  ino: number;
}

export interface ScannedArtifact extends FileState {
  path: string;
}

/** Two states are the same when their signatures are. */
export const signature = (state: FileState): string =>
  `${state.dir ? "d" : "f"}:${state.mtime}:${state.dir ? state.items : state.size}:${state.ctime}:${state.ino}`;

export function dirStat(abs: string): { latest: number; changed: number; count: number } {
  let latest = 0;
  let changed = 0;
  let count = 0;
  const walk = (dir: string, depth: number): void => {
    let entries: fs.Dirent[];
    try {
      entries = fs.readdirSync(dir, { withFileTypes: true });
    } catch {
      return;
    }
    for (const entry of entries) {
      if (SKIP_DIRS.has(entry.name) || count >= MAX_DIR_FILES) continue;
      const p = path.join(dir, entry.name);
      if (entry.isFile()) {
        count += 1;
        try {
          const stat = fs.statSync(p);
          latest = Math.max(latest, stat.mtimeMs);
          changed = Math.max(changed, stat.ctimeMs);
        } catch {
          // A file removed while reading is not counted.
        }
      } else if (entry.isDirectory() && depth < MAX_DIR_LEVELS) walk(p, depth + 1);
    }
  };
  walk(abs, 0);
  return { latest, changed, count };
}

function stateOf(abs: string, stat: fs.Stats): FileState {
  if (!stat.isDirectory())
    return {
      dir: false,
      size: stat.size,
      items: null,
      mtime: stat.mtimeMs,
      ctime: stat.ctimeMs,
      ino: stat.ino,
    };
  const inside = dirStat(abs);
  return {
    dir: true,
    size: null,
    items: inside.count,
    mtime: Math.max(stat.mtimeMs, inside.latest),
    ctime: Math.max(stat.ctimeMs, inside.changed),
    ino: stat.ino,
  };
}

/** The state of a workspace-relative path, or `null` when nothing is there. */
export function fileState(root: string, relPath: string): FileState | null {
  const abs = path.join(root, relPath);
  try {
    return stateOf(abs, fs.statSync(abs));
  } catch {
    return null;
  }
}

/** The Artifacts that match one pattern, and whether the scan stopped at the limit. */
export function scanPattern(
  root: string,
  compiled: LocationPattern,
  limit = SCAN_LIMIT,
): { found: ScannedArtifact[]; truncated: boolean } {
  const found: ScannedArtifact[] = [];
  let truncated = false;
  const maxDepth = compiled.deep ? MAX_DEEP_LEVELS : compiled.depth;
  const visit = (abs: string, relPath: string, depth: number): void => {
    if (truncated) return;
    let stat: fs.Stats;
    try {
      stat = fs.statSync(abs);
    } catch {
      return;
    }
    if (relPath && matchesPattern(compiled, relPath, stat.isDirectory())) {
      if (found.length >= limit) {
        truncated = true;
        return;
      }
      found.push({ path: relPath, ...stateOf(abs, stat) });
      if (!compiled.deep) return;
    }
    if (!stat.isDirectory() || depth >= maxDepth) return;
    let entries: fs.Dirent[];
    try {
      entries = fs.readdirSync(abs, { withFileTypes: true });
    } catch {
      return;
    }
    for (const entry of entries.sort((a, b) => a.name.localeCompare(b.name))) {
      if (SKIP_DIRS.has(entry.name)) continue;
      visit(
        path.join(abs, entry.name),
        relPath ? `${relPath}/${entry.name}` : entry.name,
        depth + 1,
      );
    }
  };
  visit(path.join(root, compiled.prefix), compiled.prefix, 0);
  return { found, truncated };
}

/** The Artifacts of one type: the matches of all its patterns, each path once. */
export function scanLocations(
  root: string,
  patterns: string[],
): { found: ScannedArtifact[]; truncated: boolean } {
  const seen = new Map<string, ScannedArtifact>();
  let truncated = false;
  for (const pattern of patterns) {
    const result = scanPattern(root, compilePattern(pattern));
    truncated ||= result.truncated;
    for (const artifact of result.found)
      if (!seen.has(artifact.path)) seen.set(artifact.path, artifact);
  }
  return { found: [...seen.values()], truncated };
}
