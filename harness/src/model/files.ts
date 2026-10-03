/* File helpers shared by the model loader. Runtime-agnostic: YAML parsing is passed in. */

import fs from "node:fs";
import path from "node:path";

/** Parses YAML text. The runtime provides it (Bun.YAML in src/server/yaml.ts). */
export type ParseYaml = (text: string) => unknown;

/** The per-workspace directory of the harness's own records. */
export const HARNESS_DIR = ".alps-harness";

/** Directories that never contain Artifacts or Skills. */
export const SKIP_DIRS: ReadonlySet<string> = new Set([".git", "node_modules", HARNESS_DIR]);

export const CONFIG_FILES = ["alps-harness.yaml", "alps-harness.yml", "alps-harness.json"] as const;
export const MODEL_FILES = [
  "process-model.yaml",
  "process-model.yml",
  "process-model.json",
] as const;

export type ModelErrorCode = "no-model";

/** The workspace has no usable process model: it is missing, unreadable, or invalid. */
export class ModelError extends Error {
  constructor(
    readonly code: ModelErrorCode,
    message: string,
    /** The files looked at, or where the files that would make a workspace can be placed. */
    readonly files: string[] = [],
  ) {
    super(message);
    this.name = "ModelError";
  }
}

export const toPosix = (p: string): string => p.split(path.sep).join("/");

/** A path relative to the workspace, with forward slashes. */
export const rel = (root: string, p: string): string => toPosix(path.relative(root, p));

export function isFile(p: string): boolean {
  try {
    return fs.statSync(p).isFile();
  } catch {
    return false;
  }
}

export function isDir(p: string): boolean {
  try {
    return fs.statSync(p).isDirectory();
  } catch {
    return false;
  }
}

export const isRecord = (value: unknown): value is Record<string, unknown> =>
  value !== null && typeof value === "object" && !Array.isArray(value);

/** Reads a YAML or JSON file. Throws a ModelError that names the file when it cannot be parsed. */
export function readStructured(file: string, parseYaml: ParseYaml): unknown {
  let text: string;
  try {
    text = fs.readFileSync(file, "utf8").replace(/^﻿/, "");
  } catch (error) {
    throw new ModelError("no-model", `Cannot read ${file}: ${(error as Error).message}`, [file]);
  }
  try {
    return /\.json$/i.test(file) ? JSON.parse(text) : parseYaml(text);
  } catch (error) {
    throw new ModelError("no-model", `Cannot parse ${file}: ${(error as Error).message}`, [file]);
  }
}

/**
 * Where to look for the workspace when no directory is given: `given` (ALPS_WORKSPACE), or `cwd`.
 * A client can pass a variable unexpanded (Claude Code 2.1.96 passed the Plugin's ALPS_WORKSPACE as
 * `${CLAUDE_PROJECT_DIR}`), so a value that holds `${` and names no existing path is none; an
 * existing path is used whatever its name.
 */
export function startDirectory(
  given: string | undefined,
  cwd: string,
  exists: (p: string) => boolean,
): string {
  if (!given || (given.includes("${") && !exists(path.resolve(cwd, given)))) return cwd;
  return given;
}

/**
 * The workspace for a start directory: the start directory or the nearest parent
 * that has alps-harness.yaml or process-model.yaml.
 */
export function findWorkspace(start: string): string | null {
  let dir = path.resolve(start);
  for (;;) {
    if ([...CONFIG_FILES, ...MODEL_FILES].some((name) => isFile(path.join(dir, name)))) return dir;
    const parent = path.dirname(dir);
    if (parent === dir) return null;
    dir = parent;
  }
}
