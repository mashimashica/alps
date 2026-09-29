/*
 * The harness of one workspace: instances, runs, provenance, and evaluations. While its server
 * runs it is the only writer of .alps-harness/. It reads the model and the configuration again
 * whenever their files change, and it never writes them. Runtime-agnostic: reading YAML,
 * `git`, and agent version checks are passed in by src/server/.
 */

import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import {
  agentInfo,
  resolveAgents,
  startsProcess,
  type AgentSpec,
  type EventDraft,
  type VersionCheck,
} from "../agents/index.ts";
import {
  CONFIG_FILES,
  MODEL_FILES,
  ModelError,
  describeModel,
  fileState,
  isConcrete,
  loadWorkspace,
  scanLocations,
  signature,
  type LoadedWorkspace,
  type ParseYaml,
} from "../model/index.ts";
import type {
  EvaluateRequest,
  FinishRequest,
  InstantiateRequest,
  RunRequest,
} from "../shared/schema.ts";
import type {
  AgentInfo,
  Artifact,
  ArtifactType,
  Assessment,
  Finding,
  Instance,
  InstanceFacts,
  InstanceView,
  ModelDescription,
  ModelView,
  OutcomeCriterion,
  Process,
  ProcessModel,
  ProcessView,
  Run,
  RunEvent,
  RunInput,
  RunOutput,
  RunStatus,
  RunTarget,
  RunView,
  ServerEvent,
  StaleReason,
  StateFile,
} from "../shared/types.ts";
import { demoFile, demoReport, demoSteps } from "./demo.ts";
import { HarnessError } from "./errors.ts";
import { INTERRUPTED_ERROR } from "./migrate.ts";
import { artifactPath, workspacePath } from "./paths.ts";
import { buildPrompt } from "./prompt.ts";
import { diffOutputs, type OutputSnapshot } from "./provenance.ts";
import { staleness, type CurrentState } from "./stale.ts";
import {
  appendEvent,
  loadRecords,
  persist,
  readEvents,
  stateSignature,
  summaryOf,
  writeRun,
  writeState,
  type LoadedRecords,
} from "./store.ts";

/** The pause between the steps of a demo run. */
const DEMO_STEP_MS = 250;
/** Events are cut to this length. */
const MAX_EVENT_TEXT = 8000;
/** How long agent version checks are reused. */
const AGENT_CHECK_TTL_MS = 5 * 60_000;

const END_LABEL: Record<Exclude<RunStatus, "running">, string> = {
  succeeded: "Succeeded",
  failed: "Failed",
  canceled: "Canceled",
  interrupted: "Interrupted",
};

export interface HarnessDeps {
  parseYaml: ParseYaml;
  /** `git rev-parse HEAD` and whether the working tree is dirty; `null` outside a repository. */
  gitInfo(root: string): { head: string; dirty: boolean } | null;
  /** Runs `<command> --version` for an agent that starts a process. Never rejects. */
  checkVersion(spec: AgentSpec): Promise<VersionCheck>;
  log(line: string): void;
}

export interface HarnessHooks {
  /** Sends an event to the clients of `GET /api/events`. */
  broadcast(event: ServerEvent): void;
  /** Keeps the server from stopping while a run is running; the returned function lets it go. */
  hold(): () => void;
}

/** A run that has not ended. */
interface ActiveRun {
  /** The output locations: each output type's patterns and the instance's concrete location. */
  locations: { type: string; patterns: string[]; paths: string[] }[];
  before: OutputSnapshot;
  release: () => void;
  timer: ReturnType<typeof setTimeout> | null;
}

/** The number in an id (`i12` → 12), which orders instances and runs by creation. */
export const seqOf = (id: string): number => Number(/(\d+)$/.exec(id)?.[1] ?? 0);

const viewOf = (run: Run): RunView => {
  const { prompt: _prompt, ...view } = run;
  return view;
};

const byKey = <T extends { id: string; name: string }>(list: T[], key: string): T | undefined =>
  list.find((item) => item.id === key) ?? list.find((item) => item.name === key);

function sha256(file: string): string | null {
  try {
    return crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
  } catch {
    return null;
  }
}

const describeReason = (reason: StaleReason): string =>
  reason.kind === "input"
    ? `${reason.path} was ${reason.change}`
    : reason.path
      ? `${reason.path} changed`
      : "the Skill is no longer found";

export class Harness {
  readonly root: string;
  readonly #deps: HarnessDeps;
  #hooks: HarnessHooks = { broadcast: () => {}, hold: () => () => {} };
  #records: LoadedRecords;
  /** state.json as it was read, to tell whether it changed before the server owned the workspace. */
  #readSignature: string;
  readonly #active = new Map<string, ActiveRun>();
  readonly #waiters = new Map<string, Set<() => void>>();
  #workspace: { loaded: LoadedWorkspace; signature: string } | null = null;
  #agentChecks: { key: string; at: number; info: Promise<AgentInfo[]> } | null = null;
  readonly #skillHashes = new Map<string, { signature: string; sha256: string | null }>();
  #closed = false;

  /** Reads the records; throws a StateError when state.json cannot be used. Nothing is written yet. */
  constructor(root: string, deps: HarnessDeps) {
    this.root = root;
    this.#deps = deps;
    this.#readSignature = stateSignature(root);
    this.#records = loadRecords(root);
    for (const { id, reason } of this.#records.unreadable)
      deps.log(`the record of run ${id} cannot be read: ${reason}`);
  }

  /**
   * Called once the server owns the workspace: writes what loading changed and starts reporting.
   * Records that a stopping server wrote after they were read are read again.
   */
  start(hooks: HarnessHooks): void {
    this.#hooks = hooks;
    if (stateSignature(this.root) !== this.#readSignature) this.#records = loadRecords(this.root);
    if (this.#records.changes.convertedV1 !== null)
      this.#deps.log("converted state.json from version 1; the original is kept as state.v1.json");
    persist(this.root, this.#records);
  }

  /** Interrupts the runs that have not ended and writes the records. */
  close(): void {
    if (this.#closed) return;
    this.#closed = true;
    // #finish deletes the entry being visited, which Map iteration allows.
    for (const id of this.#active.keys()) {
      const run = this.#records.runs.get(id);
      if (run) this.#finish(run, { status: "interrupted", error: INTERRUPTED_ERROR });
    }
  }

  get #state(): StateFile {
    return this.#records.state;
  }

  /* ---------- model and agents ---------- */

  #modelSignature(extra: string | null): string {
    const files = [...CONFIG_FILES, ...MODEL_FILES].map((name) => path.join(this.root, name));
    if (extra) files.push(extra);
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

  /** The workspace's model and configuration, read again when their files changed. */
  #loaded(): LoadedWorkspace {
    const known = this.#workspace;
    if (known && known.signature === this.#modelSignature(known.loaded.modelPath))
      return known.loaded;
    try {
      const loaded = loadWorkspace(this.root, { parseYaml: this.#deps.parseYaml });
      this.#workspace = { loaded, signature: this.#modelSignature(loaded.modelPath) };
      return loaded;
    } catch (error) {
      if (error instanceof ModelError)
        throw new HarnessError("no-model", error.message, error.files);
      throw error;
    }
  }

  #describe(): { loaded: LoadedWorkspace; description: ModelDescription } {
    const loaded = this.#loaded();
    return { loaded, description: describeModel(loaded, this.#deps.parseYaml) };
  }

  #checkAgents(specs: AgentSpec[]): Promise<AgentInfo[]> {
    const key = JSON.stringify(specs);
    const known = this.#agentChecks;
    if (known && known.key === key && Date.now() - known.at < AGENT_CHECK_TTL_MS) return known.info;
    const info = Promise.all(
      specs.map(async (spec) =>
        agentInfo(
          spec,
          startsProcess(spec) && spec.command
            ? await this.#deps.checkVersion(spec).catch(() => null)
            : null,
        ),
      ),
    );
    this.#agentChecks = { key, at: Date.now(), info };
    return info;
  }

  /** `GET /api/model`: the model as the workspace realizes it, with the agents and their availability. */
  async model(): Promise<ModelView> {
    const { loaded, description } = this.#describe();
    return { ...description, agents: await this.#checkAgents(resolveAgents(loaded.config.agents)) };
  }

  #process(model: ProcessModel, key: string): Process {
    const process = byKey(model.processes, key);
    if (!process)
      throw new HarnessError(
        "not-found",
        `No Process "${key}" in the model. Its Processes are: ${model.processes.map((p) => p.name).join(", ")}.`,
      );
    return process;
  }

  #type(model: ProcessModel, key: string): ArtifactType | undefined {
    return byKey(model.artifacts, key);
  }

  /* ---------- artifacts ---------- */

  /** `GET /api/artifacts`: the Artifacts in the locations of each type, newest first. */
  artifacts(query: { type?: string; changedSince?: number }): {
    artifacts: Artifact[];
    truncated: boolean;
  } {
    const { model } = this.#loaded();
    let types = model.artifacts;
    if (query.type) {
      const type = this.#type(model, query.type);
      if (!type)
        throw new HarnessError(
          "not-found",
          `No Artifact type "${query.type}" in the model. Its types are: ${model.artifacts.map((a) => a.name).join(", ")}.`,
        );
      types = [type];
    }
    const artifacts: Artifact[] = [];
    let truncated = false;
    for (const type of types) {
      const scan = scanLocations(this.root, type.paths);
      truncated ||= scan.truncated;
      for (const found of scan.found) {
        if (query.changedSince !== undefined && !(found.mtime > query.changedSince)) continue;
        artifacts.push({
          type: type.id,
          path: found.path,
          dir: found.dir,
          size: found.size,
          items: found.items,
          mtime: found.mtime,
          producedBy: this.#state.provenance[found.path] ?? null,
        });
      }
    }
    artifacts.sort((a, b) => b.mtime - a.mtime || a.path.localeCompare(b.path));
    return { artifacts, truncated };
  }

  /* ---------- instances ---------- */

  #instance(id: string): Instance {
    const instance = this.#state.instances[id];
    if (!instance) throw new HarnessError("not-found", `No instance ${id}.`);
    return instance;
  }

  #nextId(prefix: "i" | "r"): string {
    let id: string;
    do {
      this.#state.seq += 1;
      id = `${prefix}${this.#state.seq}`;
    } while (this.#state.instances[id] || this.#state.runs[id]);
    return id;
  }

  #saveState(): void {
    writeState(this.root, this.#state);
  }

  /** The SKILL.md at a workspace-relative path now, with its SHA-256 (cached while the file is unchanged). */
  #skillNow(relPath: string): { path: string; sha256: string | null; mtime: number } | null {
    const file = path.resolve(this.root, relPath);
    let stat: fs.Stats;
    try {
      stat = fs.statSync(file);
    } catch {
      return null;
    }
    const sig = `${stat.mtimeMs}:${stat.size}`;
    let known = this.#skillHashes.get(file);
    if (known?.signature !== sig) {
      known = { signature: sig, sha256: sha256(file) };
      this.#skillHashes.set(file, known);
    }
    return { path: relPath, sha256: known.sha256, mtime: stat.mtimeMs };
  }

  #current(instance: Instance, processes: ProcessView[]): CurrentState {
    const inputs = Object.entries(instance.inputs).flatMap(([type, paths]) =>
      paths.map((p) => ({ type, path: p, state: fileState(this.root, artifactPath(p)) })),
    );
    const skill = processes.find((p) => p.id === instance.process)?.skill;
    return { inputs, skill: skill && "path" in skill ? this.#skillNow(skill.path) : null };
  }

  #facts(instance: Instance, description: ModelDescription): InstanceFacts {
    const latestId = instance.runs.at(-1);
    const evaluation = instance.evaluation;
    const reasons = evaluation
      ? staleness(
          evaluation,
          this.#records.runs.get(evaluation.runId) ?? null,
          this.#current(instance, description.processes),
        )
      : [];
    return {
      instance: instance.id,
      process: instance.process,
      latestRun: latestId ? (this.#state.runs[latestId] ?? null) : null,
      judgments: evaluation?.judgments ?? null,
      evaluatedRun: evaluation?.runId ?? null,
      stale: reasons.length > 0,
      staleness: reasons,
    };
  }

  #view(instance: Instance, description: ModelDescription): InstanceView {
    return { ...instance, facts: this.#facts(instance, description) };
  }

  /** `GET /api/instances`: newest first, a page at a time. */
  instances(query: { process?: string; path?: string; limit: number; cursor?: string }): {
    instances: InstanceView[];
    next: string | null;
  } {
    const { loaded, description } = this.#describe();
    const process = query.process ? this.#process(loaded.model, query.process).id : undefined;
    const before = query.cursor === undefined ? Number.POSITIVE_INFINITY : Number(query.cursor);
    const part = query.path;
    const mentions = (instance: Instance): boolean =>
      part === undefined ||
      Object.values(instance.inputs).some((paths) => paths.some((p) => p.includes(part))) ||
      Object.values(instance.outputs).some((p) => p !== null && p.includes(part));
    const matching = Object.values(this.#state.instances)
      .filter(
        (i) =>
          (process === undefined || i.process === process) && mentions(i) && seqOf(i.id) < before,
      )
      .sort((a, b) => seqOf(b.id) - seqOf(a.id));
    const page = matching.slice(0, query.limit);
    const last = page.at(-1);
    return {
      instances: page.map((instance) => this.#view(instance, description)),
      next: matching.length > page.length && last ? String(seqOf(last.id)) : null,
    };
  }

  /** An instance path: inside the workspace, relative to it. */
  #pathIn(given: string, where: string): string {
    const result = workspacePath(this.root, given);
    if (result.ok) return result.path;
    if (result.reason === "empty")
      throw new HarnessError(
        "invalid-request",
        `${where}: "${given}" names no file or directory in the workspace.`,
      );
    throw new HarnessError(
      "outside-workspace",
      `${where}: ${given} is outside the workspace (${this.root}). Instances name only paths inside it.`,
    );
  }

  #inputs(
    model: ProcessModel,
    process: Process,
    given: Record<string, string[]>,
  ): Record<string, string[]> {
    const allowed = [...new Set([...process.inputs, ...process.controls])];
    const inputs: Record<string, string[]> = {};
    for (const [key, paths] of Object.entries(given)) {
      const type = this.#type(model, key);
      if (!type || !allowed.includes(type.id))
        throw new HarnessError(
          "invalid-request",
          `inputs: ${key} is not an input or control of ${process.name}. They are: ${allowed.join(", ") || "none"}.`,
        );
      const list = [
        ...(inputs[type.id] ?? []),
        ...paths.map((p) => this.#pathIn(p, `inputs.${key}`)),
      ];
      inputs[type.id] = [...new Set(list)];
    }
    return inputs;
  }

  #outputs(
    model: ProcessModel,
    process: Process,
    given: Record<string, string | null>,
  ): Record<string, string | null> {
    const outputs: Record<string, string | null> = Object.fromEntries(
      process.outputs.map((type) => [type, null]),
    );
    for (const [key, location] of Object.entries(given)) {
      const type = this.#type(model, key);
      if (!type || !process.outputs.includes(type.id))
        throw new HarnessError(
          "invalid-request",
          `outputs: ${key} is not an output of ${process.name}. Its outputs are: ${process.outputs.join(", ") || "none"}.`,
        );
      outputs[type.id] = location === null ? null : this.#pathIn(location, `outputs.${key}`);
    }
    return outputs;
  }

  #criteria(process: Process, criteria: OutcomeCriterion[]): OutcomeCriterion[] {
    const count = process.outcomes.length;
    for (const criterion of criteria)
      if (criterion.outcome >= count)
        throw new HarnessError(
          "invalid-request",
          `criteria: ${process.name} has ${count} Outcome${count === 1 ? "" : "s"} (numbered from 0); there is no Outcome ${criterion.outcome}.`,
        );
    return criteria.map((c) => ({
      outcome: c.outcome,
      statement: c.statement,
      ...(c.checks ? { checks: c.checks } : {}),
    }));
  }

  /**
   * `POST /api/instances`: a new instance, or new criteria and notes for an existing one. Inputs
   * and outputs are fixed when the instance is made, because its evaluation rests on them.
   */
  instantiate(request: InstantiateRequest): { instance: InstanceView; created: boolean } {
    const { loaded, description } = this.#describe();
    const { model } = loaded;
    let instance: Instance;
    let created: boolean;
    if ("instance" in request) {
      instance = this.#instance(request.instance);
      if (request.criteria !== undefined)
        instance.criteria = this.#criteria(
          this.#process(model, instance.process),
          request.criteria,
        );
      if (request.notes !== undefined) instance.notes = request.notes;
      created = false;
    } else {
      const process = this.#process(model, request.process);
      const inputs = this.#inputs(model, process, request.inputs);
      const outputs = this.#outputs(model, process, request.outputs);
      const criteria = this.#criteria(process, request.criteria);
      instance = {
        id: this.#nextId("i"),
        process: process.id,
        inputs,
        outputs,
        criteria,
        notes: request.notes,
        runs: [],
        evaluation: null,
      };
      this.#state.instances[instance.id] = instance;
      created = true;
    }
    this.#saveState();
    const view = this.#view(instance, description);
    this.#hooks.broadcast({ type: "instance", instance: view });
    return { instance: view, created };
  }

  /* ---------- runs ---------- */

  #run(id: string): Run {
    const run = this.#records.runs.get(id);
    if (run) return run;
    throw new HarnessError(
      "not-found",
      this.#state.runs[id]
        ? `The record of run ${id} (runs/${id}.json) is missing or unreadable.`
        : `No run ${id}.`,
    );
  }

  #emit(run: Run, draft: EventDraft): void {
    run.events += 1;
    const event: RunEvent = {
      n: run.events,
      t: Date.now(),
      kind: draft.kind,
      text: draft.text.slice(0, MAX_EVENT_TEXT),
    };
    try {
      appendEvent(this.root, run.id, event);
    } catch (error) {
      this.#deps.log(`cannot write an event of run ${run.id}: ${(error as Error).message}`);
    }
  }

  /** Each path in the output locations now. */
  #snapshot(locations: ActiveRun["locations"]): OutputSnapshot {
    const snapshot: OutputSnapshot = new Map();
    for (const { type, patterns, paths } of locations) {
      for (const found of scanLocations(this.root, patterns).found)
        if (!snapshot.has(found.path))
          snapshot.set(found.path, { type, signature: signature(found) });
      for (const p of paths) {
        const state = snapshot.has(p) ? null : fileState(this.root, p);
        if (state) snapshot.set(p, { type, signature: signature(state) });
      }
    }
    return snapshot;
  }

  #announce(run: Run): void {
    this.#hooks.broadcast({ type: "run", run: summaryOf(run) });
    const instance = run.instance ? this.#state.instances[run.instance] : undefined;
    if (!instance) return;
    try {
      this.#hooks.broadcast({
        type: "instance",
        instance: this.#view(instance, this.#describe().description),
      });
    } catch {
      // The model cannot be read now; clients read the instance again when they need it.
    }
  }

  /**
   * `POST /api/instances/:id/run`: records a run and starts its agent. Starting is all that
   * success means. This version starts the demo and the calling session (self); starting Claude
   * Code, Codex, and other commands comes with the agent runner.
   */
  startRun(instanceId: string, request: RunRequest): { run: RunView; prompt?: string } {
    const instance = this.#instance(instanceId);
    const { loaded, description } = this.#describe();
    const { model } = loaded;
    const process = this.#process(model, instance.process);
    const skill = description.processes.find((p) => p.id === process.id)?.skill ?? null;

    const specs = resolveAgents(loaded.config.agents);
    const spec = specs.find((s) => s.id === request.agent);
    if (!spec)
      throw new HarnessError(
        "agent-unavailable",
        `No agent "${request.agent}" in this workspace${request.agent === "self" ? " (agents.self is false in alps-harness.yaml)" : ""}. Its agents are: ${specs.map((s) => s.id).join(", ")}.`,
      );
    if (startsProcess(spec))
      throw new HarnessError(
        "agent-unavailable",
        `This harness does not start ${spec.label} yet; it runs the demo and self agents.`,
      );
    const running = instance.runs
      .map((id) => this.#state.runs[id])
      .find((r) => r?.status === "running");
    if (running)
      throw new HarnessError(
        "already-running",
        `Run ${running.id} of instance ${instance.id} has not ended. Wait for it (get_run with wait) or cancel it (cancel_run).`,
      );

    const typeOf = (id: string): ArtifactType | undefined =>
      model.artifacts.find((a) => a.id === id);
    const runInput = (type: string, role: RunInput["role"]): RunInput => {
      const paths = instance.inputs[type] ?? [];
      return {
        type,
        role,
        paths,
        missing: paths.filter((p) => !fileState(this.root, artifactPath(p))),
      };
    };
    const inputs = [
      ...process.inputs.map((type) => runInput(type, "input")),
      ...process.controls.map((type) => runInput(type, "control")),
    ];
    const targets: RunTarget[] = process.outputs.map((type) => {
      const location = instance.outputs[type] ?? typeOf(type)?.paths[0] ?? null;
      return { type, path: location, concrete: location !== null && isConcrete(location) };
    });
    const now = Date.now();
    const id = this.#nextId("r");
    const self = spec.format === "self";
    const prompt = buildPrompt({
      language: loaded.language,
      template: loaded.config.prompt,
      process,
      skill,
      typeName: (type) => typeOf(type)?.name ?? type,
      inputs,
      targets,
      criteria: instance.criteria,
      notes: instance.notes,
      ...(self ? { finishRun: id } : {}),
    });
    const run: Run = {
      id,
      kind: "process",
      instance: instance.id,
      process: process.id,
      agent: spec.id,
      status: "running",
      createdAt: now,
      startedAt: now,
      endedAt: null,
      exitCode: null,
      error: null,
      agentError: null,
      inputs,
      targets,
      outputs: [],
      usage: null,
      report: "",
      events: 0,
      command: null,
      client: self ? (request.client ?? null) : null,
      prompt,
      git: this.#deps.gitInfo(this.root),
      skill:
        skill && "path" in skill
          ? { path: skill.path, sha256: this.#skillNow(skill.path)?.sha256 ?? null }
          : null,
    };
    const locations = process.outputs.map((type) => {
      const location = instance.outputs[type];
      return {
        type,
        patterns: typeOf(type)?.paths ?? [],
        paths: location && isConcrete(location) ? [artifactPath(location)] : [],
      };
    });
    const active: ActiveRun = {
      locations,
      before: this.#snapshot(locations),
      release: this.#hooks.hold(),
      timer: null,
    };
    this.#active.set(id, active);
    this.#records.runs.set(id, run);
    this.#state.runs[id] = summaryOf(run);
    instance.runs.push(id);
    writeRun(this.root, run);
    this.#saveState();

    if (self)
      this.#emit(run, {
        kind: "system",
        text: "The calling session performs the run (self). It ends with finish_run.",
      });
    else this.#runDemo(run, active, loaded, process);
    this.#announce(run);
    return { run: viewOf(run), ...(self ? { prompt } : {}) };
  }

  #runDemo(run: Run, active: ActiveRun, loaded: LoadedWorkspace, process: Process): void {
    const typeName = (type: string): string =>
      loaded.model.artifacts.find((a) => a.id === type)?.name ?? type;
    const steps = demoSteps({
      language: loaded.language,
      processName: process.name,
      skillPath: run.skill?.path ?? null,
      inputs: run.inputs,
      targets: run.targets,
      runId: run.id,
    });
    let next = 0;
    const tick = (): void => {
      active.timer = null;
      if (run.status !== "running") return;
      try {
        const step = steps[next++];
        if (!step) {
          run.report = demoReport(loaded.language);
          this.#finish(run, { status: "succeeded", exitCode: 0 });
          return;
        }
        const failure = step.write
          ? this.#writeDemo(step.write.path, typeName(step.write.type), run, process, loaded)
          : null;
        if (failure) {
          this.#emit(run, { kind: "error", text: failure });
          this.#finish(run, { status: "failed", exitCode: 1, error: failure });
          return;
        }
        this.#emit(run, step);
        active.timer = setTimeout(tick, DEMO_STEP_MS);
      } catch (error) {
        const message = (error as Error).message;
        this.#deps.log(`demo run ${run.id}: ${(error as Error).stack ?? message}`);
        try {
          this.#finish(run, { status: "failed", error: `The demo stopped: ${message}` });
        } catch {
          // The records cannot be written; the log has the reason.
        }
      }
    };
    active.timer = setTimeout(tick, DEMO_STEP_MS);
  }

  /**
   * Writes the demo's placeholder at an output location. An existing file keeps its content and
   * only has its modification time updated, so the demo never overwrites work.
   */
  #writeDemo(
    location: string,
    typeName: string,
    run: Run,
    process: Process,
    loaded: LoadedWorkspace,
  ): string | null {
    const target = workspacePath(this.root, location);
    if (!target.ok) return `The demo does not write ${location}: it is outside the workspace.`;
    const { file, text } = demoFile({
      language: loaded.language,
      path: target.path,
      typeName,
      processName: process.name,
      runId: run.id,
    });
    const abs = path.join(this.root, file);
    try {
      if (fs.existsSync(abs)) {
        const now = new Date();
        fs.utimesSync(abs, now, now);
      } else {
        fs.mkdirSync(path.dirname(abs), { recursive: true });
        fs.writeFileSync(abs, text, { flag: "wx" });
      }
      return null;
    } catch (error) {
      return `The demo could not write ${file}: ${(error as Error).message}`;
    }
  }

  /** Ends a run: its outputs are what changed in the output locations since it started. */
  #finish(
    run: Run,
    end: { status: Exclude<RunStatus, "running">; exitCode?: number | null; error?: string | null },
  ): void {
    if (run.status !== "running") return;
    const active = this.#active.get(run.id);
    this.#active.delete(run.id);
    if (active?.timer) clearTimeout(active.timer);
    run.status = end.status;
    run.endedAt = Date.now();
    run.exitCode = end.exitCode ?? null;
    if (end.error) run.error = end.error;
    if (active) {
      run.outputs = diffOutputs(active.before, this.#snapshot(active.locations));
      for (const output of run.outputs) this.#state.provenance[output.path] = run.id;
    }
    const seconds = Math.round((run.endedAt - run.startedAt) / 1000);
    this.#emit(run, { kind: "end", text: `${END_LABEL[end.status]} (${seconds} s)` });
    this.#state.runs[run.id] = summaryOf(run);
    try {
      writeRun(this.root, run);
      this.#saveState();
    } finally {
      active?.release();
      for (const wake of this.#waiters.get(run.id) ?? []) wake();
      this.#waiters.delete(run.id);
    }
    this.#announce(run);
    this.#hooks.broadcast({ type: "artifacts" });
  }

  #waitForEnd(id: string, ms: number, signal?: AbortSignal): Promise<void> {
    return new Promise((resolve) => {
      const waiters = this.#waiters.get(id) ?? new Set<() => void>();
      this.#waiters.set(id, waiters);
      const done = (): void => {
        clearTimeout(timer);
        waiters.delete(done);
        signal?.removeEventListener("abort", done);
        resolve();
      };
      const timer = setTimeout(done, ms);
      waiters.add(done);
      signal?.addEventListener("abort", done, { once: true });
    });
  }

  /** `GET /api/runs/:id`: the record and its last events, after waiting up to `wait` seconds for it to end. */
  async getRun(
    id: string,
    options: { tail: number; wait: number },
    signal?: AbortSignal,
  ): Promise<{ run: Run; events: RunEvent[]; truncated: boolean }> {
    const run = this.#run(id);
    if (options.wait > 0 && run.status === "running")
      await this.#waitForEnd(id, options.wait * 1000, signal);
    const { events, total } = readEvents(this.root, id, options.tail);
    return { run, events, truncated: total > events.length };
  }

  /** `POST /api/runs/:id/cancel`. A run that has already ended is left as it is. */
  cancelRun(id: string): { run: RunView; canceled: boolean } {
    const run = this.#run(id);
    if (run.status !== "running") return { run: viewOf(run), canceled: false };
    this.#finish(run, { status: "canceled" });
    return { run: viewOf(run), canceled: true };
  }

  /** `POST /api/runs/:id/finish`: ends a self (or wake) run with the session's report. */
  finishRun(id: string, request: FinishRequest): { run: RunView; outputs: RunOutput[] } {
    const run = this.#run(id);
    if (run.agent !== "self" && run.kind !== "wake")
      throw new HarnessError(
        "invalid-request",
        `Run ${id} is a ${run.agent} run. finish_run ends only the self and wake runs that the calling session performs.`,
      );
    if (run.status !== "running")
      throw new HarnessError(
        "invalid-request",
        `Run ${id} has already ended (${run.status}). See it with get_run.`,
      );
    run.report = request.report;
    this.#finish(run, { status: request.status });
    return { run: viewOf(run), outputs: run.outputs };
  }

  /* ---------- evaluations ---------- */

  /**
   * `POST /api/instances/:id/evaluate`: judgments of the latest run's results, per Outcome, with
   * evidence. It replaces the instance's evaluation.
   */
  evaluate(instanceId: string, request: EvaluateRequest): { instance: InstanceView } {
    const instance = this.#instance(instanceId);
    const { loaded, description } = this.#describe();
    const process = this.#process(loaded.model, instance.process);
    const latestId = instance.runs.at(-1);
    const latest = latestId ? this.#state.runs[latestId] : undefined;
    if (!latest)
      throw new HarnessError(
        "not-found",
        `Instance ${instance.id} has no run to evaluate. Run it first.`,
      );
    if (latest.status === "running")
      throw new HarnessError(
        "already-running",
        `Run ${latest.id} of instance ${instance.id} has not ended. Evaluate its results once it has (get_run with wait).`,
      );
    const count = process.outcomes.length;
    const judged = new Set<number>();
    for (const { outcome } of request.judgments) {
      if (outcome >= count)
        throw new HarnessError(
          "invalid-judgment",
          `${process.name} has ${count} Outcome${count === 1 ? "" : "s"} (numbered from 0); there is no Outcome ${outcome}.`,
        );
      if (judged.has(outcome))
        throw new HarnessError("invalid-judgment", `Outcome ${outcome} is judged twice.`);
      judged.add(outcome);
    }
    instance.evaluation = {
      runId: latest.id,
      judgments: [...request.judgments]
        .sort((a, b) => a.outcome - b.outcome)
        .map((j) => ({
          outcome: j.outcome,
          judgment: j.judgment,
          evidence: j.evidence,
          ...(j.limits ? { limits: j.limits } : {}),
        })),
      ...(request.note?.trim() ? { note: request.note } : {}),
      by: request.by,
      at: Date.now(),
    };
    this.#saveState();
    const view = this.#view(instance, description);
    this.#hooks.broadcast({ type: "instance", instance: view });
    return { instance: view };
  }

  /* ---------- assessment ---------- */

  /**
   * `GET /api/assessment`: the facts of each instance and the findings that follow from them and
   * from the model. The statistics come with the dashboard.
   */
  assessment(): Assessment {
    const { description } = this.#describe();
    const facts = Object.values(this.#state.instances)
      .sort((a, b) => seqOf(a.id) - seqOf(b.id))
      .map((instance) => this.#facts(instance, description));
    const findings: Finding[] = [];
    for (const process of description.processes)
      if (process.skill && "missing" in process.skill)
        findings.push({
          kind: "configuration",
          subject: { process: process.id },
          message: `The Skill declared for ${process.name} (${process.skill.missing}) is not a readable SKILL.md.`,
          evidence: [process.skill.missing],
        });
    for (const fact of facts) {
      const latest = fact.latestRun;
      const subject = { instance: fact.instance, process: fact.process };
      if (
        latest &&
        (latest.status === "succeeded" || latest.status === "failed") &&
        fact.evaluatedRun !== latest.id
      )
        findings.push({
          kind: "unverified",
          subject,
          message: `Run ${latest.id} ended (${latest.status}) and its results have no judgment yet.`,
          evidence: [latest.id],
        });
      if (fact.stale)
        findings.push({
          kind: "unverified",
          subject,
          message: `The judgment of run ${fact.evaluatedRun} no longer rests on the workspace: ${fact.staleness.map(describeReason).join("; ")}.`,
          evidence: fact.staleness.map((reason) => reason.path ?? "SKILL.md"),
        });
    }
    return { stats: null, findings, instances: facts };
  }
}
