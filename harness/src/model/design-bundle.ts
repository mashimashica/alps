import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import type { DesignSkillFileDraft, ModelWriteRequest } from "../shared/types.ts";
import {
  CONFIG_FILES,
  HARNESS_DIR,
  MODEL_FILES,
  SKIP_DIRS,
  isRecord,
  toPosix,
  type ParseYaml,
} from "./files.ts";
import { prepareWorkspaceModelUpdate } from "./edit.ts";
import type { LoadedWorkspace } from "./load.ts";

const MAX_SNAPSHOT_FILES = 1_000;
const MAX_SNAPSHOT_BYTES = 16 * 1024 * 1024;
const MAX_BUNDLE_BYTES = 8 * 1024 * 1024;
const SKILL_NAME = /^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$/;
const SUPPORT_DIRS = new Set(["references", "scripts", "assets", "agents"]);

const sha256 = (data: string | Uint8Array): string =>
  crypto.createHash("sha256").update(data).digest("hex");

const isInside = (relative: string): boolean =>
  relative === "" ||
  (relative !== ".." && !relative.startsWith(`..${path.sep}`) && !path.isAbsolute(relative));

const isInsidePosix = (child: string, parent: string): boolean =>
  child === parent || child.startsWith(`${parent}/`);

const partsOf = (relative: string): string[] => relative.split("/").filter(Boolean);

function existingAncestor(abs: string): string {
  let current = abs;
  for (;;) {
    if (fs.lstatSync(current, { throwIfNoEntry: false })) return current;
    const parent = path.dirname(current);
    if (parent === current) return current;
    current = parent;
  }
}

function normalizeWorkspaceFile(root: string, given: string, subject: string): string {
  const trimmed = given.trim();
  if (!trimmed) throw new Error(`${subject}: path is empty.`);
  if (trimmed.includes("\0")) throw new Error(`${subject}: path contains a NUL byte.`);
  if (path.isAbsolute(trimmed)) throw new Error(`${subject}: use a workspace-relative path.`);
  if (trimmed.split(/[\\/]+/).some((part) => part === ".."))
    throw new Error(`${subject}: traversal with '..' is not allowed.`);

  const abs = path.resolve(root, trimmed);
  const relative = path.relative(root, abs);
  if (!isInside(relative)) throw new Error(`${subject}: ${given} is outside the workspace.`);
  const normalized = toPosix(relative);
  const parts = partsOf(normalized);
  const lowered = parts.map((part) => part.toLowerCase());
  if (lowered.some((part) => part === ".git" || part === HARNESS_DIR || part === "node_modules"))
    throw new Error(`${subject}: ${normalized} is in a reserved directory.`);
  const reservedFiles: readonly string[] = [...CONFIG_FILES, ...MODEL_FILES];
  if (reservedFiles.includes(normalized))
    throw new Error(`${subject}: ${normalized} is a reserved model or configuration file.`);

  const realRoot = fs.realpathSync(root);
  let component = root;
  for (const part of parts) {
    component = path.join(component, part);
    if (fs.lstatSync(component, { throwIfNoEntry: false })?.isSymbolicLink())
      throw new Error(`${subject}: ${normalized} contains a symlink and cannot be written safely.`);
  }
  const ancestor = existingAncestor(abs);
  const realAncestor = fs.realpathSync(ancestor);
  const realRelative = path.relative(realRoot, realAncestor);
  if (!isInside(realRelative))
    throw new Error(`${subject}: ${normalized} follows a symlink outside the workspace.`);
  const realParts = partsOf(toPosix(realRelative)).map((part) => part.toLowerCase());
  if (realParts.some((part) => part === ".git" || part === HARNESS_DIR))
    throw new Error(`${subject}: ${normalized} follows a symlink into a reserved directory.`);

  const current = fs.lstatSync(abs, { throwIfNoEntry: false });
  if (current?.isSymbolicLink())
    throw new Error(`${subject}: ${normalized} is a symlink and cannot be written safely.`);
  return normalized;
}

function normalizeSkillRoot(root: string, given: string): string | null {
  try {
    const relative = path.relative(root, path.resolve(root, given));
    if (!isInside(relative) || relative === "") return null;
    const normalized = toPosix(relative).replace(/\/+$/, "");
    const lowered = partsOf(normalized).map((part) => part.toLowerCase());
    if (lowered.some((part) => part === ".git" || part === HARNESS_DIR || part === "node_modules"))
      return null;
    return normalized;
  } catch {
    return null;
  }
}

function skillPackageDir(root: string, skillPath: string): string {
  const normalized = normalizeWorkspaceFile(root, skillPath, `skill ${skillPath}`).replace(
    /\/+$/,
    "",
  );
  return path.posix.basename(normalized) === "SKILL.md"
    ? path.posix.dirname(normalized)
    : normalized;
}

function declaredSkillDirs(
  root: string,
  request: ModelWriteRequest,
  skillRoots: readonly string[],
) {
  const roots = skillRoots.map((item) => normalizeSkillRoot(root, item)).filter((item) => item);
  const dirs = new Map<string, string>();
  for (const process of request.processes) {
    if (!process.skill) continue;
    const dir = skillPackageDir(root, process.skill);
    if (!roots.some((skillRoot) => isInsidePosix(dir, skillRoot!)))
      throw new Error(
        `${process.name}: Skill ${process.skill} must be inside a configured skill root.`,
      );
    dirs.set(dir, process.name);
  }
  return dirs;
}

function assertDraftInDeclaredSkill(relPath: string, skillDirs: ReadonlyMap<string, string>): void {
  const dir = [...skillDirs.keys()].find((candidate) => isInsidePosix(relPath, candidate));
  if (!dir) throw new Error(`${relPath}: file is not inside a declared Skill package.`);
  const rest = relPath.slice(dir.length).replace(/^\/+/, "");
  if (rest === "SKILL.md") return;
  const first = rest.split("/")[0] ?? "";
  if (!SUPPORT_DIRS.has(first))
    throw new Error(
      `${relPath}: supporting files must be under references/, scripts/, assets/, or agents/.`,
    );
}

function textAt(root: string, relPath: string, drafts: ReadonlyMap<string, string>): string | null {
  const draft = drafts.get(relPath);
  if (draft !== undefined) return draft;
  try {
    return fs.readFileSync(path.join(root, relPath), "utf8");
  } catch {
    return null;
  }
}

function existsAt(root: string, relPath: string, drafts: ReadonlyMap<string, string>): boolean {
  if (drafts.has(relPath)) return true;
  return fs.statSync(path.join(root, relPath), { throwIfNoEntry: false })?.isFile() ?? false;
}

function validateSkillMarkdown(
  root: string,
  skillDir: string,
  parseYaml: ParseYaml,
  drafts: ReadonlyMap<string, string>,
): void {
  const skillFile = `${skillDir}/SKILL.md`;
  const text = textAt(root, skillFile, drafts);
  if (text === null) throw new Error(`${skillFile}: declared Skill is missing.`);
  const match = /^﻿?---\r?\n([\s\S]*?)\r?\n---[ \t]*(?:\r?\n|$)/.exec(text);
  if (!match) throw new Error(`${skillFile}: SKILL.md needs YAML frontmatter.`);
  let data: unknown;
  try {
    data = parseYaml(match[1] ?? "");
  } catch (error) {
    throw new Error(`${skillFile}: frontmatter is not valid YAML: ${(error as Error).message}`);
  }
  if (!isRecord(data)) throw new Error(`${skillFile}: frontmatter must be a mapping.`);
  const name = typeof data.name === "string" ? data.name.trim() : "";
  const description = typeof data.description === "string" ? data.description.trim() : "";
  const expectedName = path.posix.basename(skillDir);
  if (!SKILL_NAME.test(name) || name.includes("--"))
    throw new Error(
      `${skillFile}: frontmatter name must be lowercase letters, numbers, and hyphens.`,
    );
  if (name !== expectedName)
    throw new Error(
      `${skillFile}: frontmatter name must match the Skill directory (${expectedName}).`,
    );
  if (!description || description.length > 1024)
    throw new Error(
      `${skillFile}: frontmatter description is required and must fit 1024 characters.`,
    );
  if (!text.slice(match[0].length).trim()) throw new Error(`${skillFile}: body is empty.`);

  const body = text.slice(match[0].length);
  const links = body.matchAll(/\[[^\]]*]\(([^)\s]+)(?:\s+["'][^)]*)?\)/g);
  for (const link of links) {
    const target = link[1]?.trim() ?? "";
    if (!target || target.startsWith("#") || /^[a-z][a-z0-9+.-]*:/i.test(target)) continue;
    const clean = target.split("#")[0]!.split("?")[0]!;
    if (!clean || clean.startsWith("#")) continue;
    if (path.isAbsolute(clean))
      throw new Error(`${skillFile}: link ${target} must be relative to the workspace.`);
    const linked = toPosix(path.posix.normalize(path.posix.join(skillDir, clean)));
    if (!isInside(path.relative(root, path.resolve(root, linked))))
      throw new Error(`${skillFile}: link ${target} leaves the workspace.`);
    const absolute = path.resolve(root, linked);
    if (
      !isInside(path.relative(fs.realpathSync(root), fs.realpathSync(existingAncestor(absolute))))
    )
      throw new Error(`${skillFile}: link ${target} follows a symlink outside the workspace.`);
    if (!existsAt(root, linked, drafts))
      throw new Error(`${skillFile}: linked file ${clean} is missing.`);
  }
}

function writeAtomic(file: string, content: string | Uint8Array): void {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const tmp = path.join(
    path.dirname(file),
    `.${path.basename(file)}.tmp-${process.pid}-${Date.now()}`,
  );
  try {
    fs.writeFileSync(tmp, content, { flag: "wx" });
    fs.renameSync(tmp, file);
  } finally {
    fs.rmSync(tmp, { force: true });
  }
}

function writeDraftFiles(
  root: string,
  drafts: ReadonlyMap<string, string>,
  baseline: Readonly<Record<string, string>>,
): { savedFiles: string[]; rollback: () => void } {
  const backups: { path: string; existed: boolean; content: Buffer | null }[] = [];
  // Check the entire bundle before the first write, then recheck each destination at commit.
  const states = new Map<string, string | null>();
  for (const [relPath, content] of drafts) {
    normalizeWorkspaceFile(root, relPath, "Skill file");
    const file = path.join(root, relPath);
    const stat = fs.lstatSync(file, { throwIfNoEntry: false });
    if (stat && !stat.isFile()) throw new Error(`${relPath}: destination is not a regular file.`);
    const currentHash = stat ? sha256(fs.readFileSync(file)) : null;
    const expected = baseline[relPath];
    if (expected !== undefined && currentHash !== expected)
      throw new Error(`${relPath}: file changed since the design session started.`);
    if (expected === undefined && currentHash !== null && currentHash !== sha256(content))
      throw new Error(`${relPath}: existing file was not captured in the design baseline.`);
    states.set(relPath, currentHash);
  }
  try {
    for (const [relPath, content] of drafts) {
      normalizeWorkspaceFile(root, relPath, "Skill file");
      const file = path.join(root, relPath);
      const existing = fs.statSync(file, { throwIfNoEntry: false });
      const current = existing?.isFile() ? fs.readFileSync(file) : null;
      const currentHash = current ? sha256(current) : null;
      const expected = baseline[relPath];
      const nextHash = sha256(content);
      if (currentHash !== states.get(relPath))
        throw new Error(`${relPath}: file changed before the bundle could be saved.`);
      if (currentHash !== null) {
        if (expected !== undefined && currentHash !== expected)
          throw new Error(`${relPath}: file changed since the design session started.`);
        if (expected === undefined && currentHash !== nextHash)
          throw new Error(`${relPath}: existing file was not captured in the design baseline.`);
      } else if (expected !== undefined) {
        throw new Error(`${relPath}: file was removed since the design session started.`);
      }
      if (currentHash === nextHash) continue;
      backups.push({ path: file, existed: current !== null, content: current });
      writeAtomic(file, content);
    }
  } catch (error) {
    rollbackBackups(backups);
    throw error;
  }
  return { savedFiles: [...drafts.keys()], rollback: () => rollbackBackups(backups) };
}

function rollbackBackups(
  backups: readonly { path: string; existed: boolean; content: Buffer | null }[],
): void {
  for (const backup of [...backups].reverse()) {
    try {
      if (backup.existed && backup.content) writeAtomic(backup.path, backup.content);
      else fs.rmSync(backup.path, { force: true });
    } catch {
      // The model write will report the original failure; rollback is best effort.
    }
  }
}

export function snapshotDesignSkills(
  root: string,
  loaded: LoadedWorkspace,
): Record<string, string> {
  const roots = new Set<string>();
  for (const skillRoot of loaded.skillRoots) {
    const normalized = normalizeSkillRoot(root, skillRoot);
    if (normalized) roots.add(normalized);
  }
  for (const process of loaded.model.processes) {
    if (!process.skill) continue;
    try {
      roots.add(skillPackageDir(root, process.skill));
    } catch {
      // Existing invalid Skill paths are reported elsewhere; they should not block prompt creation.
    }
  }
  const result: Record<string, string> = {};
  let count = 0;
  let bytes = 0;
  const walk = (dir: string): void => {
    if (count >= MAX_SNAPSHOT_FILES || bytes >= MAX_SNAPSHOT_BYTES) return;
    const absolute = path.join(root, dir);
    const entries = fs
      .readdirSync(absolute, { withFileTypes: true })
      .sort((a, b) => a.name.localeCompare(b.name));
    for (const entry of entries) {
      if (count >= MAX_SNAPSHOT_FILES || SKIP_DIRS.has(entry.name)) continue;
      const child = `${dir}/${entry.name}`;
      const abs = path.join(root, child);
      if (entry.isSymbolicLink()) continue;
      if (entry.isDirectory()) walk(child);
      else if (entry.isFile()) {
        const size = fs.statSync(abs).size;
        if (bytes + size > MAX_SNAPSHOT_BYTES) continue;
        result[toPosix(child)] = sha256(fs.readFileSync(abs));
        bytes += size;
        count += 1;
      }
    }
  };
  for (const dir of [...roots].sort()) {
    try {
      normalizeWorkspaceFile(root, `${dir}/SKILL.md`, "Skill baseline");
      if (fs.lstatSync(path.join(root, dir), { throwIfNoEntry: false })?.isDirectory()) walk(dir);
    } catch {
      // Unsafe or inaccessible packages are never authorized for replacement.
    }
  }
  return result;
}

export function saveDesignBundle(options: {
  root: string;
  loaded: LoadedWorkspace;
  request: ModelWriteRequest;
  skillFiles: readonly DesignSkillFileDraft[];
  skillBaseline?: Record<string, string>;
  parseYaml: ParseYaml;
}): { loaded: LoadedWorkspace; savedFiles: string[] } {
  assertBundleSize(options.skillFiles);
  const root = path.resolve(options.root);
  const skillDirs = declaredSkillDirs(root, options.request, options.loaded.skillRoots);
  const drafts = new Map<string, string>();
  for (const file of options.skillFiles) {
    const relPath = normalizeWorkspaceFile(root, file.path, `Skill file ${file.path}`);
    assertDraftInDeclaredSkill(relPath, skillDirs);
    const known = drafts.get(relPath);
    if (known !== undefined && known !== file.content)
      throw new Error(`${relPath}: multiple drafts disagree.`);
    drafts.set(relPath, file.content);
  }
  for (const skillDir of skillDirs.keys())
    validateSkillMarkdown(root, skillDir, options.parseYaml, drafts);

  const prepared = prepareWorkspaceModelUpdate({
    root,
    modelPath: options.loaded.modelPath,
    request: options.request,
    parseYaml: options.parseYaml,
  });
  let rollback: (() => void) | undefined;
  try {
    const written = writeDraftFiles(root, drafts, options.skillBaseline ?? {});
    rollback = written.rollback;
    const loaded = prepared.commit();
    return { loaded, savedFiles: written.savedFiles };
  } catch (error) {
    rollback?.();
    throw error;
  } finally {
    prepared.cleanup();
  }
}

function assertBundleSize(files: readonly DesignSkillFileDraft[]): void {
  if (
    files.length > 200 ||
    files.reduce((n, file) => n + Buffer.byteLength(file.content), 0) > MAX_BUNDLE_BYTES
  )
    throw new Error("The Skill bundle is too large; submit at most 200 files and 8 MiB.");
}

export function saveMissingDesignSkills(options: {
  root: string;
  loaded: LoadedWorkspace;
  request: ModelWriteRequest;
  skillFiles: readonly DesignSkillFileDraft[];
  parseYaml: ParseYaml;
}): { savedFiles: string[] } {
  assertBundleSize(options.skillFiles);
  // A historical proposal must not restore instructions for a meaning that has since changed.
  for (const proposed of options.request.processes) {
    if (!proposed.skill) continue;
    const current = options.loaded.model.processes.find((process) => process.id === proposed.id);
    if (!current)
      throw new Error(`${proposed.name}: process no longer exists; review the Skill first.`);
    for (const [key, value] of Object.entries(proposed)) {
      if (value === undefined) continue;
      const actual = (current as unknown as Record<string, unknown>)[key];
      if (JSON.stringify(actual ?? (Array.isArray(value) ? [] : "")) !== JSON.stringify(value))
        throw new Error(`${proposed.name}: ${key} changed; review the Skill before restoring it.`);
    }
  }
  const root = path.resolve(options.root);
  const skillDirs = declaredSkillDirs(root, options.request, options.loaded.skillRoots);
  const drafts = new Map<string, string>();
  for (const file of options.skillFiles) {
    const relPath = normalizeWorkspaceFile(root, file.path, `Skill file ${file.path}`);
    assertDraftInDeclaredSkill(relPath, skillDirs);
    const known = drafts.get(relPath);
    if (known !== undefined && known !== file.content)
      throw new Error(`${relPath}: multiple drafts disagree.`);
    drafts.set(relPath, file.content);
  }
  for (const skillDir of skillDirs.keys())
    validateSkillMarkdown(root, skillDir, options.parseYaml, drafts);

  return { savedFiles: writeDraftFiles(root, drafts, {}).savedFiles };
}
