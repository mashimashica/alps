/*
 * Loading a workspace: alps-harness.yaml (the realization) and process-model.yaml (the meaning).
 * The configuration only adds how the workspace realizes the model (locations, kinds, Skills);
 * it never changes the model's meaning.
 */

import path from "node:path";
import {
  formatIssues,
  harnessConfigSchema,
  processModelFileSchema,
  type HarnessConfig,
  type ProcessModelFile,
} from "../shared/schema.ts";
import type { ArtifactType, Language, Process, ProcessModel } from "../shared/types.ts";
import {
  CONFIG_FILES,
  MODEL_FILES,
  ModelError,
  isFile,
  readStructured,
  type ParseYaml,
} from "./files.ts";

export const DEFAULT_SKILL_ROOTS = ["skills", ".claude/skills", ".agents/skills", ".codex/skills"];
export const DEFAULT_PORT = 4830;
export const DEFAULT_IDLE_MINUTES = 30;

export interface LoadedWorkspace {
  root: string;
  configPath: string | null;
  modelPath: string;
  config: HarnessConfig;
  model: ProcessModel;
  skillRoots: string[];
  language: Language;
  server: { port: number; idleMinutes: number };
}

export interface LoadOptions {
  parseYaml: ParseYaml;
  /** A configuration file other than the workspace's alps-harness.yaml, relative to the workspace. */
  config?: string;
}

/** `<case>` (and `{case}` from the block form) is read as `*`; locations use only `*` and `**`. */
const normalizePaths = (paths: string[]): string[] =>
  paths.map((p) => p.replace(/<case>|\{case\}/g, "*"));

export function loadWorkspace(root: string, options: LoadOptions): LoadedWorkspace {
  const { parseYaml } = options;
  let configPath: string | null;
  if (options.config) {
    configPath = path.resolve(root, options.config);
    if (!isFile(configPath)) {
      throw new ModelError(
        "no-model",
        `The configuration file ${options.config} does not exist in ${root}.`,
      );
    }
  } else {
    configPath = CONFIG_FILES.map((name) => path.join(root, name)).find(isFile) ?? null;
  }

  let config: HarnessConfig = {};
  if (configPath) {
    const raw = readStructured(configPath, parseYaml) ?? {};
    const parsed = harnessConfigSchema.safeParse(raw);
    if (!parsed.success)
      throw new ModelError("no-model", formatIssues(path.basename(configPath), parsed.error));
    config = parsed.data;
  }

  const modelPath = config.model
    ? path.resolve(root, config.model)
    : MODEL_FILES.map((name) => path.join(root, name)).find(isFile);
  if (!modelPath || !isFile(modelPath)) {
    throw config.model
      ? new ModelError(
          "no-model",
          `The process model ${config.model} named by model in ${configPath} does not exist.`,
          [path.resolve(root, config.model)],
        )
      : new ModelError("no-model", `No process model: place process-model.yaml in ${root}.`, [
          path.join(root, "process-model.yaml"),
        ]);
  }
  const rawModel = readStructured(modelPath, parseYaml);
  const parsedModel = processModelFileSchema.safeParse(rawModel);
  if (!parsedModel.success) {
    throw new ModelError("no-model", formatIssues(path.basename(modelPath), parsedModel.error));
  }

  const model = normalizeModel(parsedModel.data, path.basename(modelPath));
  applyConfig(model, config, configPath ? path.basename(configPath) : "configuration");

  return {
    root,
    configPath,
    modelPath,
    config,
    model,
    skillRoots: config.skillRoots ?? DEFAULT_SKILL_ROOTS,
    language: config.language ?? "en",
    server: {
      port: config.server?.port ?? DEFAULT_PORT,
      idleMinutes: config.server?.idleMinutes ?? DEFAULT_IDLE_MINUTES,
    },
  };
}

function normalizeModel(raw: ProcessModelFile, file: string): ProcessModel {
  const artifacts: ArtifactType[] = [];
  const byId = new Map<string, ArtifactType>();
  const byName = new Map<string, ArtifactType>();
  const add = (id: string, name: string, extra: Partial<ArtifactType> = {}): ArtifactType => {
    const artifact: ArtifactType = { id, name, description: "", kind: null, paths: [], ...extra };
    artifacts.push(artifact);
    byId.set(id, artifact);
    if (!byName.has(name)) byName.set(name, artifact);
    return artifact;
  };

  for (const entry of raw.artifacts) {
    const name = entry.name || entry.id || "";
    const id = entry.id || name;
    if (byId.has(id))
      throw new ModelError("no-model", `${file}: the artifact type "${id}" is defined twice.`);
    add(id, name, {
      description: entry.description ?? "",
      kind: entry.kind ?? null,
      paths: normalizePaths(entry.paths),
    });
  }
  // A process may refer to a type that artifacts does not list; it is still a type of the model.
  const resolve = (ref: string): string => (byId.get(ref) ?? byName.get(ref) ?? add(ref, ref)).id;

  const processes: Process[] = [];
  const ids = new Set<string>();
  for (const entry of raw.processes) {
    const name = entry.name || entry.id || "";
    const id = entry.id || name;
    if (ids.has(id))
      throw new ModelError("no-model", `${file}: the process "${id}" is defined twice.`);
    ids.add(id);
    const refs = (list: string[]): string[] => [...new Set(list.map(resolve))];
    processes.push({
      id,
      name,
      purpose: entry.purpose ?? "",
      outcomes: entry.outcomes,
      constraints: entry.constraints,
      enablers: entry.enablers,
      inputs: refs(entry.inputs),
      controls: refs(entry.controls),
      outputs: refs(entry.outputs),
      skill: entry.skill || null,
    });
  }
  return {
    name: raw.name || "Process model",
    description: raw.description ?? "",
    processes,
    artifacts,
  };
}

function applyConfig(model: ProcessModel, config: HarnessConfig, file: string): void {
  const find = <T extends { id: string; name: string }>(list: T[], key: string): T | undefined =>
    list.find((x) => x.id === key) ?? list.find((x) => x.name === key);

  for (const [key, spec] of Object.entries(config.artifacts ?? {})) {
    const artifact = find(model.artifacts, key);
    if (!artifact)
      throw new ModelError(
        "no-model",
        `${file}: artifacts.${key} is not an artifact type of the process model.`,
      );
    if (spec.kind !== undefined) artifact.kind = spec.kind;
    if (spec.paths !== undefined) artifact.paths = normalizePaths(spec.paths);
  }
  for (const [key, location] of Object.entries(config.skills ?? {})) {
    const process = find(model.processes, key);
    if (!process)
      throw new ModelError(
        "no-model",
        `${file}: skills.${key} is not a process of the process model.`,
      );
    process.skill = location || null;
  }
}
