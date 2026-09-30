/*
 * Loading a workspace: alps-harness.yaml (the realization) and process-model.yaml (the meaning).
 * The configuration only adds how the workspace realizes the model (locations, kinds, Skills);
 * it never changes the model's meaning.
 */

import fs from "node:fs";
import path from "node:path";
import { resolveAgents, takesMcpServer } from "../agents/index.ts";
import { DEFAULT_ATTACHMENTS } from "../shared/requests.ts";
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
  HARNESS_DIR,
  MODEL_FILES,
  ModelError,
  isDir,
  isFile,
  readStructured,
  toPosix,
  type ParseYaml,
} from "./files.ts";
import { normalizeLocations } from "./patterns.ts";

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
  /**
   * Where the WebUI saves the files attached to a request (`attachments`, inbox/ by default):
   * relative to the workspace, with forward slashes and a trailing slash.
   */
  attachments: string;
}

/**
 * The attachments directory that alps-harness.yaml names (inbox/ when it names none), relative to
 * the workspace with forward slashes and a trailing slash (empty for the workspace itself), or
 * why it cannot be used: it leaves the workspace, or it lies in .alps-harness/ (compared without
 * case, as macOS and Windows compare names). Only the names are compared; the server looks where
 * symlinks lead when it saves a file.
 */
export function attachmentsLocation(
  root: string,
  configured: string | undefined,
): { ok: true; dir: string } | { ok: false; reason: "outside" | "records" } {
  const relative = path.relative(root, path.resolve(root, configured || DEFAULT_ATTACHMENTS));
  if (relative === ".." || relative.startsWith(`..${path.sep}`) || path.isAbsolute(relative))
    return { ok: false, reason: "outside" };
  if (relative.split(path.sep)[0]?.toLowerCase() === HARNESS_DIR)
    return { ok: false, reason: "records" };
  return { ok: true, dir: relative === "" ? "" : `${toPosix(relative)}/` };
}

/**
 * The first part of an attachments directory (relative to the workspace, with a trailing slash)
 * that is there as something other than a directory: a file, or a symlink that leads nowhere;
 * `null` when each part is a directory or is not there yet (it is made when a file is saved).
 */
function notDirectory(root: string, dir: string): string | null {
  let relative = "";
  for (const part of dir.split("/").filter(Boolean)) {
    relative = relative ? `${relative}/${part}` : part;
    const absolute = path.join(root, relative);
    if (fs.lstatSync(absolute, { throwIfNoEntry: false }) === undefined) return null;
    if (!isDir(absolute)) return relative;
  }
  return null;
}

export interface LoadOptions {
  parseYaml: ParseYaml;
  /** A configuration file other than the workspace's alps-harness.yaml, relative to the workspace. */
  config?: string;
}

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
      throw new ModelError("no-model", formatIssues(path.basename(configPath), parsed.error), [
        configPath,
      ]);
    config = parsed.data;
    // Like an unreadable cron expression, a schedule that cannot wake its agent is an error of the file.
    const problems = scheduleProblems(config, path.basename(configPath));
    if (problems) throw new ModelError("no-model", problems, [configPath]);
  }
  // Without a configuration the default, inbox/, is always inside the workspace.
  const attachments = attachmentsLocation(root, config.attachments);
  if (!attachments.ok)
    throw new ModelError(
      "no-model",
      `${path.basename(configPath ?? CONFIG_FILES[0])}: attachments: ${config.attachments} ${
        attachments.reason === "outside"
          ? `is outside the workspace (${root})`
          : "is in .alps-harness/, the harness's own records"
      }; the files attached to requests are saved inside the workspace and outside .alps-harness/.`,
      configPath ? [configPath] : [],
    );
  // The directory that alps-harness.yaml names holds a directory for each day: it cannot be a file.
  const blocked = config.attachments ? notDirectory(root, attachments.dir) : null;
  if (blocked !== null)
    throw new ModelError(
      "no-model",
      `${path.basename(configPath ?? CONFIG_FILES[0])}: attachments: ${config.attachments} cannot hold the files attached to requests: ${blocked} is not a directory (a file, or a symlink that leads nowhere). Name a directory, or one that does not exist yet.`,
      configPath ? [configPath] : [],
    );

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
    throw new ModelError("no-model", formatIssues(path.basename(modelPath), parsedModel.error), [
      modelPath,
    ]);
  }

  const files = [modelPath, ...(configPath ? [configPath] : [])];
  const model = withFiles(files, () => normalizeModel(parsedModel.data, path.basename(modelPath)));
  withFiles(files, () =>
    applyConfig(model, config, configPath ? path.basename(configPath) : "configuration"),
  );

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
    attachments: attachments.dir,
  };
}

/**
 * What is wrong with the agents that `schedules` wake, one line for each wrong schedule in the
 * words of formatIssues, or `null`. A schedule names an agent of the workspace (the defaults as
 * `agents` changes them) that the harness can give its MCP server: of the claude or codex format.
 */
function scheduleProblems(config: HarnessConfig, file: string): string | null {
  const schedules = config.schedules ?? [];
  if (schedules.length === 0) return null;
  const agents = resolveAgents(config.agents);
  const wakeable = agents.filter(takesMcpServer).map((agent) => agent.id);
  const problems = schedules.flatMap(({ agent: id }, i) => {
    const agent = agents.find((spec) => spec.id === id);
    if (agent && takesMcpServer(agent)) return [];
    const problem = agent
      ? `"${id}" cannot be woken: a wake gives its agent the harness's MCP server, which only agents of the claude and codex formats take`
      : `"${id}" is not an agent of this workspace`;
    return [
      `${file}: schedules.${i}.agent: ${problem}; the agents that can be woken: ${wakeable.join(", ") || "none"}`,
    ];
  });
  return problems.length > 0 ? problems.join("\n") : null;
}

/** Adds the files looked at to a ModelError that names none. */
function withFiles<T>(files: string[], read: () => T): T {
  try {
    return read();
  } catch (error) {
    if (error instanceof ModelError && error.files.length === 0)
      throw new ModelError(error.code, error.message, files);
    throw error;
  }
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
      paths: normalizeLocations(entry.paths),
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
    if (spec.paths !== undefined) artifact.paths = normalizeLocations(spec.paths);
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
