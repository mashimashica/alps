import fs from "node:fs";
import path from "node:path";
import { formatIssues, processModelFileSchema } from "../shared/schema.ts";
import type { ProcessModelFile } from "../shared/schema.ts";
import type {
  ModelWriteActivity,
  ModelWriteArtifact,
  ModelWriteProcess,
  ModelWriteRequest,
} from "../shared/types.ts";
import { CONFIG_FILES, MODEL_FILES, ModelError, isRecord, rel, type ParseYaml } from "./files.ts";
import { loadWorkspace, validateWorkspaceModel, type LoadedWorkspace } from "./load.ts";
import { fileState, signature } from "./scan.ts";

export class ModelRevisionError extends Error {
  constructor() {
    super("The process model changed before the write could be completed.");
    this.name = "ModelRevisionError";
  }
}

export interface UpdateWorkspaceModelOptions {
  root: string;
  modelPath: string;
  request: ModelWriteRequest;
  parseYaml: ParseYaml;
}

export interface PreparedWorkspaceModelUpdate {
  commit(): LoadedWorkspace;
  cleanup(): void;
}

type MutableRecord = Record<string, unknown>;

const clean = (values: readonly string[] | undefined): string[] => [
  ...new Set((values ?? []).map((value) => value.trim()).filter(Boolean)),
];

const textOf = (value: unknown): string => (typeof value === "string" ? value.trim() : "");

const recordsOf = (value: unknown): MutableRecord[] =>
  Array.isArray(value) ? value.filter(isRecord).map((item) => ({ ...item })) : [];

const stringsOf = (value: unknown): string[] =>
  Array.isArray(value) ? value.filter((item): item is string => typeof item === "string") : [];

const keyOf = (value: { id?: unknown; name?: unknown }): string | null => {
  const id = typeof value.id === "string" ? value.id.trim() : "";
  const name = typeof value.name === "string" ? value.name.trim() : "";
  return id || name || null;
};

function revisionOf(root: string, modelPath: string): string {
  const files = [...CONFIG_FILES, ...MODEL_FILES].map((name) => path.join(root, name));
  files.push(modelPath);
  return files
    .map((file) => {
      try {
        const stat = fs.statSync(file);
        return `${file}:${stat.mtimeMs}:${stat.size}`;
      } catch {
        return `${file}:-`;
      }
    })
    .join("|");
}

function copyUnknown(
  target: MutableRecord,
  source: Record<string, unknown>,
  known: ReadonlySet<string>,
): void {
  for (const [key, value] of Object.entries(source)) {
    if (!known.has(key) && value !== undefined) target[key] = value;
  }
}

function setText(target: MutableRecord, key: string, value: string | undefined): void {
  if (value === undefined) return;
  const text = value.trim();
  if (text) target[key] = text;
  else delete target[key];
}

function setList(target: MutableRecord, key: string, value: readonly string[] | undefined): void {
  if (value === undefined) return;
  const list = clean(value);
  if (list.length > 0) target[key] = list;
  else delete target[key];
}

function setNullableText(
  target: MutableRecord,
  key: string,
  value: string | null | undefined,
): void {
  if (value === undefined) return;
  const text = value?.trim() ?? "";
  if (text) target[key] = text;
  else delete target[key];
}

const activityKnown = new Set(["name", "tasks", "supportsOutcomes"]);

function mergeActivities(
  existing: MutableRecord[],
  updates: ModelWriteActivity[],
  processName: string,
): MutableRecord[] {
  const byName = new Map<string, number>();
  existing.forEach((activity, index) => {
    const name = textOf(activity.name);
    if (name && !byName.has(name)) byName.set(name, index);
  });

  return updates.map((update, index) => {
    const name = update.name.trim();
    if (!name)
      throw new ModelError(
        "no-model",
        `process-model: processes.${processName}.activities.${index}: an activity needs a name.`,
      );
    const existingIndex = byName.get(name);
    const next: MutableRecord = existingIndex === undefined ? {} : { ...existing[existingIndex] };
    copyUnknown(next, update as unknown as MutableRecord, activityKnown);
    next.name = name;
    setList(next, "tasks", update.tasks);
    setList(next, "supportsOutcomes", update.supportsOutcomes);
    return next;
  });
}

const processKnown = new Set([
  "id",
  "name",
  "purpose",
  "outcomes",
  "scope",
  "activities",
  "tasks",
  "constraints",
  "enablers",
  "entryCriteria",
  "exitCriteria",
  "references",
  "inputs",
  "controls",
  "outputs",
  "skill",
]);

function processRecord(
  update: ModelWriteProcess,
  existing: MutableRecord | undefined,
): MutableRecord {
  const next: MutableRecord = existing ? { ...existing } : {};
  copyUnknown(next, update as unknown as MutableRecord, processKnown);

  setText(next, "id", update.id);
  setText(next, "name", update.name);
  setText(next, "purpose", update.purpose);
  setList(next, "outcomes", update.outcomes);
  setText(next, "scope", update.scope);
  if (update.activities !== undefined) {
    const activities = mergeActivities(recordsOf(next.activities), update.activities, update.name);
    if (activities.length > 0) next.activities = activities;
    else delete next.activities;
  }
  setList(next, "tasks", update.tasks);
  setList(next, "constraints", update.constraints);
  setList(next, "enablers", update.enablers);
  setList(next, "entryCriteria", update.entryCriteria);
  setList(next, "exitCriteria", update.exitCriteria);
  setList(next, "references", update.references);
  setList(next, "inputs", update.inputs);
  setList(next, "controls", update.controls);
  setList(next, "outputs", update.outputs);
  setNullableText(next, "skill", update.skill);

  if (!existing) {
    const name = textOf(next.name);
    const purpose = textOf(next.purpose);
    const outcomes = clean(stringsOf(next.outcomes));
    if (!name || !purpose || outcomes.length === 0)
      throw new ModelError(
        "no-model",
        `process-model: a new process needs a Name, a Purpose, and at least one Outcome.`,
      );
  }

  return next;
}

const artifactKnown = new Set(["id", "name", "description", "kind", "paths"]);

function artifactRecord(
  update: ModelWriteArtifact,
  existing: MutableRecord | undefined,
): MutableRecord {
  const next: MutableRecord = existing ? { ...existing } : {};
  copyUnknown(next, update as unknown as MutableRecord, artifactKnown);
  setText(next, "id", update.id);
  setText(next, "name", update.name);
  setText(next, "description", update.description);
  if (update.kind !== undefined) {
    if (update.kind) next.kind = update.kind;
    else delete next.kind;
  }
  setList(next, "paths", update.paths);
  return next;
}

function replaceByKey<T>(
  existing: MutableRecord[],
  updates: T[],
  makeRecord: (update: T, existing: MutableRecord | undefined) => MutableRecord,
): MutableRecord[] {
  const byKey = new Map<string, number>();
  existing.forEach((entry, index) => {
    const key = keyOf(entry);
    if (key && !byKey.has(key)) byKey.set(key, index);
  });
  const next = [...existing];
  for (const update of updates) {
    const key = keyOf(update as { id?: unknown; name?: unknown });
    if (key && byKey.has(key)) next[byKey.get(key)!] = makeRecord(update, next[byKey.get(key)!]);
    else next.push(makeRecord(update, undefined));
  }
  return next;
}

function parseModelFile(modelPath: string, parseYaml: ParseYaml): MutableRecord {
  let text: string;
  try {
    text = fs.readFileSync(modelPath, "utf8").replace(/^﻿/, "");
  } catch (error) {
    throw new ModelError("no-model", `Cannot read ${modelPath}: ${(error as Error).message}`, [
      modelPath,
    ]);
  }
  try {
    const value = /\.json$/i.test(modelPath) ? JSON.parse(text) : parseYaml(text);
    return isRecord(value) ? { ...value } : {};
  } catch (error) {
    throw new ModelError("no-model", `Cannot parse ${modelPath}: ${(error as Error).message}`, [
      modelPath,
    ]);
  }
}

function mergeModelFile(raw: MutableRecord, request: ModelWriteRequest): ProcessModelFile {
  const next: MutableRecord = { ...raw };
  copyUnknown(next, request as unknown as MutableRecord, new Set(["expectedRevision"]));
  next.name = request.name.trim();
  setText(next, "description", request.description);
  if (request.draft === true || request.processes.length === 0) next.draft = true;
  else delete next.draft;
  next.processes = replaceByKey(recordsOf(raw.processes), request.processes, processRecord);
  if (request.artifacts !== undefined)
    next.artifacts = replaceByKey(recordsOf(raw.artifacts), request.artifacts, artifactRecord);
  return next as ProcessModelFile;
}

const simpleKey = /^[A-Za-z_][A-Za-z0-9_-]*$/;

function yamlScalar(value: unknown): string {
  if (typeof value === "string") return JSON.stringify(value);
  if (typeof value === "number" || typeof value === "boolean") return String(value);
  if (value === null) return "null";
  return JSON.stringify(value);
}

function writeYamlValue(lines: string[], indent: number, value: unknown): void {
  const pad = " ".repeat(indent);
  if (Array.isArray(value)) {
    if (value.length === 0) {
      lines.push(`${pad}[]`);
      return;
    }
    for (const item of value) {
      if (isRecord(item) || Array.isArray(item)) {
        lines.push(`${pad}-`);
        writeYamlValue(lines, indent + 2, item);
      } else {
        lines.push(`${pad}- ${yamlScalar(item)}`);
      }
    }
    return;
  }
  if (isRecord(value)) {
    const entries = Object.entries(value).filter(([, item]) => item !== undefined);
    if (entries.length === 0) {
      lines.push(`${pad}{}`);
      return;
    }
    for (const [key, item] of entries) {
      const label = simpleKey.test(key) ? key : JSON.stringify(key);
      if (Array.isArray(item)) {
        if (item.length === 0) lines.push(`${pad}${label}: []`);
        else {
          lines.push(`${pad}${label}:`);
          writeYamlValue(lines, indent + 2, item);
        }
      } else if (isRecord(item)) {
        lines.push(`${pad}${label}:`);
        writeYamlValue(lines, indent + 2, item);
      } else {
        lines.push(`${pad}${label}: ${yamlScalar(item)}`);
      }
    }
    return;
  }
  lines.push(`${pad}${yamlScalar(value)}`);
}

function yamlOf(model: ProcessModelFile): string {
  const lines: string[] = [];
  writeYamlValue(lines, 0, model);
  return `${lines.join("\n")}\n`;
}

function contentOf(modelPath: string, model: ProcessModelFile): string {
  if (/\.json$/i.test(modelPath)) return `${JSON.stringify(model, null, 2)}\n`;
  return yamlOf(model);
}

function assertWritableModelPath(root: string, modelPath: string): void {
  const relativePath = path.relative(root, modelPath);
  if (
    relativePath === ".." ||
    relativePath.startsWith(`..${path.sep}`) ||
    path.isAbsolute(relativePath)
  )
    throw new ModelError("no-model", `The process model ${modelPath} is outside the workspace.`, [
      modelPath,
    ]);
  const stat = fs.lstatSync(modelPath);
  if (stat.isSymbolicLink())
    throw new ModelError(
      "no-model",
      `The process model ${modelPath} is a symlink and cannot be edited safely.`,
      [modelPath],
    );
  const rootReal = fs.realpathSync(root);
  const modelReal = fs.realpathSync(modelPath);
  const relativeReal = path.relative(rootReal, modelReal);
  if (
    relativeReal === ".." ||
    relativeReal.startsWith(`..${path.sep}`) ||
    path.isAbsolute(relativeReal)
  )
    throw new ModelError("no-model", `The process model ${modelPath} is outside the workspace.`, [
      modelPath,
    ]);
}

export function prepareWorkspaceModelUpdate(
  options: UpdateWorkspaceModelOptions,
): PreparedWorkspaceModelUpdate {
  const root = path.resolve(options.root);
  const modelPath = path.resolve(options.modelPath);
  assertWritableModelPath(root, modelPath);
  const relative = rel(root, modelPath);
  const currentState = fileState(root, relative);
  if (!currentState)
    throw new ModelError("no-model", `The process model ${relative} does not exist.`, [modelPath]);
  const expectedRevision = options.request.expectedRevision;
  if (expectedRevision !== revisionOf(root, modelPath)) throw new ModelRevisionError();

  const raw = parseModelFile(modelPath, options.parseYaml);
  const model = mergeModelFile(raw, options.request);
  const parsed = processModelFileSchema.safeParse(model);
  if (!parsed.success)
    throw new ModelError("no-model", formatIssues(path.basename(modelPath), parsed.error), [
      modelPath,
    ]);
  validateWorkspaceModel(root, { parseYaml: options.parseYaml }, modelPath, parsed.data);

  const tmp = path.join(
    path.dirname(modelPath),
    `.${path.basename(modelPath)}.tmp-${process.pid}-${Date.now()}`,
  );
  fs.writeFileSync(tmp, contentOf(modelPath, model), { flag: "wx" });
  let committed = false;
  return {
    commit() {
      try {
        assertWritableModelPath(root, modelPath);
        if (revisionOf(root, modelPath) !== expectedRevision) throw new ModelRevisionError();
        const afterWriteState = fileState(root, relative);
        if (!afterWriteState || signature(afterWriteState) !== signature(currentState))
          throw new ModelRevisionError();
        fs.renameSync(tmp, modelPath);
        committed = true;
        return loadWorkspace(root, { parseYaml: options.parseYaml });
      } finally {
        if (!committed) fs.rmSync(tmp, { force: true });
      }
    },
    cleanup() {
      if (!committed) fs.rmSync(tmp, { force: true });
    },
  };
}

export function updateWorkspaceModel(options: UpdateWorkspaceModelOptions): LoadedWorkspace {
  return prepareWorkspaceModelUpdate(options).commit();
}
