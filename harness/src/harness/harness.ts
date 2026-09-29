/*
 * The harness of one workspace: instances, runs, provenance, and evaluations. While its server
 * runs it is the only writer of .alps-harness/. It reads the model and the configuration again
 * whenever their files change, and it never writes them. Runtime-agnostic: reading YAML, `git`,
 * agent version checks, and starting agent processes are passed in by src/server/.
 */

import fs from "node:fs";
import path from "node:path";
import {
  agentInfo,
  argsFor,
  commandLine,
  parseOutputLine,
  resolveAgents,
  startsProcess,
  type AgentHandle,
  type AgentLaunch,
  type AgentOutput,
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
import { say, type MessageArgs, type MessageKey } from "../shared/strings.ts";
import type {
  AgentInfo,
  Artifact,
  ArtifactType,
  Assessment,
  ClientInfo,
  Finding,
  Instance,
  InstanceFacts,
  InstanceView,
  Judge,
  ModelDescription,
  ModelView,
  OutcomeCriterion,
  Process,
  ProcessModel,
  ProcessView,
  Run,
  RunClient,
  RunEvent,
  RunInput,
  RunOutput,
  RunStatus,
  RunSummary,
  RunTarget,
  RunView,
  ServerEvent,
  StateFile,
} from "../shared/types.ts";
import { demoFile, demoReport, demoSteps } from "./demo.ts";
import { DigestCache } from "./digest.ts";
import { refuse } from "./errors.ts";
import { INTERRUPTED_ERROR } from "./migrate.ts";
import { artifactPath, workspacePath } from "./paths.ts";
import { buildPrompt } from "./prompt.ts";
import { diffOutputs, type OutputSnapshot } from "./provenance.ts";
import { assessmentMarkdown } from "./report.ts";
import { staleness, type CurrentState } from "./stale.ts";
import {
  appendEvent,
  loadRecords,
  persist,
  readEvents,
  recordPaths,
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
/** The report of an agent that prints plain text is the end of its output, up to this length. */
const MAX_TEXT_REPORT = 6000;
/** How long agent version checks are reused. */
const AGENT_CHECK_TTL_MS = 5 * 60_000;
/** How long cancel_run and a stopping server wait for an agent's process group to end (it gets SIGKILL after 5 s). */
const STOP_WAIT_MS = 8000;

export const SESSION_CLOSED_ERROR =
  "The MCP connection of the session that performs the run closed before finish_run.";

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
  /** Starts an agent's process in a process group of its own; throws when it cannot be started. */
  startAgent(launch: AgentLaunch, output: AgentOutput): AgentHandle;
  log(line: string): void;
}

export interface HarnessHooks {
  /** Sends an event to the clients of `GET /api/events`. */
  broadcast(event: ServerEvent): void;
  /** Keeps the server from stopping while a run is running; the returned function lets it go. */
  hold(): () => void;
}

/**
 * Who makes a request: a person (the WebUI, or an HTTP client that names no MCP client), or an
 * agent through the MCP server, which names its client and the session it holds with the server.
 */
export type Caller =
  | { kind: "user" }
  | { kind: "agent"; client: ClientInfo; session: string | null };

/** How a run ends. */
interface RunEnd {
  status: Exclude<RunStatus, "running">;
  exitCode?: number | null;
  error?: string | null;
}

/** A run that has not ended. */
interface ActiveRun {
  /** The output locations: each output type's patterns and the instance's concrete location. */
  locations: { type: string; patterns: string[]; paths: string[] }[];
  before: OutputSnapshot;
  release: () => void;
  timer: ReturnType<typeof setTimeout> | null;
  /** The agent's process, for an agent that starts one. */
  agent: AgentHandle | null;
  /** How the run ends once its agent's process has: set when it is canceled or the server stops. */
  stopping: "canceled" | "interrupted" | null;
}

/** The number in an id (`i12` → 12), which orders instances and runs by creation. */
export const seqOf = (id: string): number => Number(/(\d+)$/.exec(id)?.[1] ?? 0);

const viewOf = (run: Run): RunView => {
  const { prompt: _prompt, ...view } = run;
  return view;
};

const byKey = <T extends { id: string; name: string }>(list: T[], key: string): T | undefined =>
  list.find((item) => item.id === key) ?? list.find((item) => item.name === key);

/**
 * Whether the agent that calls performed a self run: through the same MCP session. A record
 * without a session (none could be opened, or it predates sessions) is matched by the client's
 * name and version instead.
 */
const performedBy = (
  performer: RunClient | null,
  caller: Extract<Caller, { kind: "agent" }>,
): boolean => {
  if (performer === null) return false;
  if (performer.session !== null) return performer.session === caller.session;
  return performer.name === caller.client.name && performer.version === caller.client.version;
};

/** A message in English with its key and arguments, for a finding. */
const said = <K extends MessageKey>(key: K, args: MessageArgs<K>) => ({
  message: say("en", key, args),
  key,
  args: args as Record<string, string | number | boolean>,
});

/** The end of a text, kept to a length. */
class Tail {
  #text = "";
  push(line: string): void {
    this.#text = `${this.#text}${line}\n`.slice(-MAX_TEXT_REPORT);
  }
  get value(): string {
    return this.#text.trim();
  }
}

/** runs/<id>.raw.log: the agent's own output, stdout lines as they came and stderr lines marked. */
class RawLog {
  #fd: number | null;
  readonly #log: (line: string) => void;
  constructor(file: string, log: (line: string) => void) {
    this.#log = log;
    try {
      fs.mkdirSync(path.dirname(file), { recursive: true });
      this.#fd = fs.openSync(file, "a");
    } catch (error) {
      this.#fd = null;
      log(`cannot open ${file}: ${(error as Error).message}`);
    }
  }
  write(line: string): void {
    if (this.#fd === null) return;
    try {
      fs.writeSync(this.#fd, `${line}\n`);
    } catch (error) {
      this.#log(`cannot write the raw log: ${(error as Error).message}`);
      this.close();
    }
  }
  close(): void {
    if (this.#fd === null) return;
    try {
      fs.closeSync(this.#fd);
    } catch {
      // Already closed.
    }
    this.#fd = null;
  }
}

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
  readonly #digests: DigestCache;
  #closing: Promise<void> | null = null;

  /** Reads the records; throws a StateError when state.json cannot be used. Nothing is written yet. */
  constructor(root: string, deps: HarnessDeps) {
    this.root = root;
    this.#deps = deps;
    this.#digests = new DigestCache(root);
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

  /**
   * Stops the agents of the runs that have not ended, records those runs as interrupted, and
   * writes the records. Resolves once every agent's process group has ended (they get SIGKILL
   * after 5 seconds), or after a few seconds more.
   */
  close(): Promise<void> {
    this.#closing ??= (async () => {
      const waits: Promise<void>[] = [];
      // Ending a run deletes its entry, which iterating the map allows.
      for (const id of this.#active.keys()) {
        const active = this.#active.get(id);
        const run = this.#records.runs.get(id);
        if (!active || !run) continue;
        if (active.agent) {
          active.stopping = "interrupted";
          active.agent.stop();
          waits.push(this.#waitForEnd(id, STOP_WAIT_MS));
        } else this.#end(run, { status: "interrupted", error: INTERRUPTED_ERROR });
      }
      await Promise.all(waits);
      // What did not end in time is recorded as interrupted all the same.
      for (const id of this.#active.keys()) {
        const run = this.#records.runs.get(id);
        if (run) this.#end(run, { status: "interrupted", error: INTERRUPTED_ERROR });
      }
    })();
    return this.#closing;
  }

  /** Ends a run as #finish does, logging what cannot be written instead of throwing. */
  #end(run: Run, end: RunEnd): void {
    try {
      this.#finish(run, end);
    } catch (error) {
      this.#deps.log(`cannot record the end of run ${run.id}: ${(error as Error).message}`);
    }
  }

  /** The MCP session `session` closed: the self runs it performs are interrupted. */
  sessionClosed(session: string): void {
    for (const id of this.#active.keys()) {
      const run = this.#records.runs.get(id);
      if (run?.client?.session === session)
        this.#end(run, { status: "interrupted", error: SESSION_CLOSED_ERROR });
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
        throw refuse("no-model", "error.model", { detail: error.message }, error.files);
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

  /**
   * Whether an agent can be started now. An agent that the last check found unavailable is checked
   * again, since its command may have been installed since.
   */
  async #availability(spec: AgentSpec, specs: AgentSpec[]): Promise<AgentInfo> {
    const known = (await this.#checkAgents(specs)).find((info) => info.id === spec.id);
    if (known?.available) return known;
    const fresh = agentInfo(spec, await this.#deps.checkVersion(spec).catch(() => null));
    if (fresh.available) this.#agentChecks = null;
    return fresh;
  }

  /** `GET /api/model`: the model as the workspace realizes it, with the agents and their availability. */
  async model(): Promise<ModelView> {
    const { loaded, description } = this.#describe();
    return { ...description, agents: await this.#checkAgents(resolveAgents(loaded.config.agents)) };
  }

  #process(model: ProcessModel, key: string): Process {
    const process = byKey(model.processes, key);
    if (!process)
      throw refuse("not-found", "error.noProcess", {
        name: key,
        processes: model.processes.map((p) => p.name).join(", "),
      });
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
        throw refuse("not-found", "error.noType", {
          name: query.type,
          types: model.artifacts.map((a) => a.name).join(", "),
        });
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
    if (!instance) throw refuse("not-found", "error.noInstance", { id });
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

  /** The digests of an instance's inputs and of the Process's SKILL.md now. */
  #current(instance: Instance, processes: ProcessView[]): CurrentState {
    const inputs = Object.entries(instance.inputs).flatMap(([type, paths]) =>
      paths.map((p) => ({ type, path: p, sha256: this.#digests.of(artifactPath(p)) })),
    );
    const skill = processes.find((p) => p.id === instance.process)?.skill;
    return {
      inputs,
      skill:
        skill && "path" in skill
          ? { path: skill.path, sha256: this.#digests.of(skill.path) }
          : null,
    };
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

  /** `GET /api/instances/:id`: one instance with its facts. */
  instance(id: string): InstanceView {
    const instance = this.#instance(id);
    return this.#view(instance, this.#describe().description);
  }

  /** An instance path: inside the workspace and outside its records, relative to the workspace. */
  #pathIn(given: string, where: string): string {
    const result = workspacePath(this.root, given);
    if (result.ok) return result.path;
    if (result.reason === "empty")
      throw refuse("invalid-request", "error.emptyPath", { where, path: given });
    if (result.reason === "records")
      throw refuse("outside-workspace", "error.records", { where, path: given });
    throw refuse("outside-workspace", "error.outside", { where, path: given, root: this.root });
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
        throw refuse("invalid-request", "error.notInput", {
          type: key,
          process: process.name,
          allowed: allowed.join(", "),
        });
      const list = [...(inputs[type.id] ?? [])];
      for (const given of paths) {
        const where = `inputs.${key}`;
        const inside = this.#pathIn(given, where);
        // An input is what the evaluation rests on, so it names one file or directory.
        if (!isConcrete(inside))
          throw refuse("invalid-request", "error.pattern", { where, path: given });
        list.push(inside);
      }
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
        throw refuse("invalid-request", "error.notOutput", {
          type: key,
          process: process.name,
          outputs: process.outputs.join(", "),
        });
      outputs[type.id] = location === null ? null : this.#pathIn(location, `outputs.${key}`);
    }
    return outputs;
  }

  #criteria(process: Process, criteria: OutcomeCriterion[]): OutcomeCriterion[] {
    const count = process.outcomes.length;
    for (const criterion of criteria)
      if (criterion.outcome >= count)
        throw refuse("invalid-request", "error.noOutcome", {
          where: "criteria: ",
          process: process.name,
          count,
          outcome: criterion.outcome,
        });
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
    throw this.#state.runs[id]
      ? refuse("not-found", "error.runRecord", { id })
      : refuse("not-found", "error.noRun", { id });
  }

  /** `GET /api/runs`: run summaries, newest first, a page at a time. */
  runs(query: { limit: number; cursor?: string }): { runs: RunSummary[]; next: string | null } {
    const before = query.cursor === undefined ? Number.POSITIVE_INFINITY : Number(query.cursor);
    const matching = Object.values(this.#state.runs)
      .filter((run) => seqOf(run.id) < before)
      .sort((a, b) => seqOf(b.id) - seqOf(a.id));
    const page = matching.slice(0, query.limit);
    const last = page.at(-1);
    return {
      runs: page,
      next: matching.length > page.length && last ? String(seqOf(last.id)) : null,
    };
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
   * success means. An agent that starts a process is checked first (`<command> --version`); the
   * demo starts none, and a self run is performed by the calling session, which the result's prompt
   * instructs and which ends it with finish_run.
   */
  async startRun(
    instanceId: string,
    request: RunRequest,
    caller: Caller,
  ): Promise<{ run: RunView; prompt?: string }> {
    if (this.#closing) throw refuse("server-unreachable", "error.stopping", {});
    this.#instance(instanceId);
    const agentSpec = (loaded: LoadedWorkspace): { spec: AgentSpec; specs: AgentSpec[] } => {
      const specs = resolveAgents(loaded.config.agents);
      const spec = specs.find((s) => s.id === request.agent);
      if (spec) return { spec, specs };
      const agents = specs.map((s) => s.id).join(", ");
      throw request.agent === "self"
        ? refuse("agent-unavailable", "error.selfDisabled", { agents })
        : refuse("agent-unavailable", "error.noAgent", { agent: request.agent, agents });
    };
    let info: AgentInfo | null = null;
    {
      const { spec, specs } = agentSpec(this.#loaded());
      if (startsProcess(spec)) {
        info = await this.#availability(spec, specs);
        if (!info.available)
          throw refuse("agent-unavailable", "error.agentUnavailable", {
            agent: spec.label,
            reason: info.reason ?? "it is not available",
          });
      }
    }
    // From here on nothing waits, so no other request comes between the checks and the record.
    if (this.#closing) throw refuse("server-unreachable", "error.stopping", {});
    const instance = this.#instance(instanceId);
    const { loaded, description } = this.#describe();
    const { model } = loaded;
    const { spec } = agentSpec(loaded);
    const process = this.#process(model, instance.process);
    const skill = description.processes.find((p) => p.id === process.id)?.skill ?? null;
    const running = instance.runs
      .map((id) => this.#state.runs[id])
      .find((r) => r?.status === "running");
    if (running)
      throw refuse("already-running", "error.running", { run: running.id, instance: instance.id });

    const typeOf = (id: string): ArtifactType | undefined =>
      model.artifacts.find((a) => a.id === id);
    const runInput = (type: string, role: RunInput["role"]): RunInput => {
      const paths = instance.inputs[type] ?? [];
      const sha256: Record<string, string> = {};
      const missing: string[] = [];
      for (const p of paths) {
        if (!fileState(this.root, artifactPath(p))) {
          missing.push(p);
          continue;
        }
        const digest = this.#digests.of(artifactPath(p));
        if (digest) sha256[p] = digest;
      }
      return { type, role, paths, missing, sha256 };
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
    const args = startsProcess(spec) ? argsFor(spec, prompt) : [];
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
      command: startsProcess(spec) ? commandLine(spec, args, prompt) : null,
      // The session tells who performs the run: it is interrupted when the session closes, and an
      // evaluation through the same session is marked self.
      client:
        self && caller.kind === "agent" ? { ...caller.client, session: caller.session } : null,
      prompt,
      git: this.#deps.gitInfo(this.root),
      skill:
        skill && "path" in skill
          ? { path: skill.path, sha256: this.#digests.of(skill.path) }
          : null,
    };
    const locations = process.outputs.map((type) => {
      const location = instance.outputs[type];
      const concrete = location !== null && location !== undefined && isConcrete(location);
      return {
        type,
        patterns: [...(typeOf(type)?.paths ?? []), ...(location && !concrete ? [location] : [])],
        paths: location && concrete ? [artifactPath(location)] : [],
      };
    });
    const active: ActiveRun = {
      locations,
      before: this.#snapshot(locations),
      release: this.#hooks.hold(),
      timer: null,
      agent: null,
      stopping: null,
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
    else if (spec.format === "demo") this.#runDemo(run, active, loaded, process);
    else this.#runAgent(run, active, spec, info, args);
    this.#announce(run);
    return { run: viewOf(run), ...(self ? { prompt } : {}) };
  }

  /** Starts an agent's process and reads its output as the run's events, usage, and report. */
  #runAgent(
    run: Run,
    active: ActiveRun,
    spec: AgentSpec,
    info: AgentInfo | null,
    args: string[],
  ): void {
    const raw = new RawLog(recordPaths(this.root).raw(run.id), this.#deps.log);
    const text = spec.format === "text" ? new Tail() : null;
    this.#emit(run, {
      kind: "system",
      text: `Started ${spec.label}${info?.version ? ` (${info.version})` : ""}`,
    });
    let handle: AgentHandle;
    try {
      handle = this.#deps.startAgent(
        {
          command: spec.command ?? "",
          args,
          cwd: this.root,
          env: {
            ...spec.env,
            ALPS_RUN_ID: run.id,
            ALPS_INSTANCE: run.instance ?? "",
            ALPS_PROCESS: run.process ?? "",
          },
          stdin: spec.stdin ? run.prompt : null,
        },
        {
          stdout: (line) => {
            raw.write(line);
            if (run.status !== "running") return;
            const parsed = parseOutputLine(spec.format, line);
            for (const event of parsed.events) this.#emit(run, event);
            if (parsed.usage) run.usage = parsed.usage;
            if (parsed.report !== undefined) run.report = parsed.report;
            if (parsed.agentError !== undefined) run.agentError = parsed.agentError;
            text?.push(line);
          },
          stderr: (line) => {
            raw.write(`[stderr] ${line}`);
            if (run.status === "running") this.#emit(run, { kind: "stderr", text: line });
          },
        },
      );
    } catch (error) {
      raw.close();
      const message = `${spec.label} could not be started: ${(error as Error).message}`;
      this.#emit(run, { kind: "error", text: message });
      this.#end(run, { status: "failed", error: message });
      return;
    }
    active.agent = handle;
    handle.done.then(
      ({ exitCode, signal }) => {
        raw.close();
        if (text && !run.report) run.report = text.value;
        if (active.stopping) {
          this.#end(run, {
            status: active.stopping,
            exitCode,
            error: active.stopping === "interrupted" ? INTERRUPTED_ERROR : null,
          });
          return;
        }
        const succeeded = exitCode === 0 && !run.agentError;
        this.#end(run, {
          status: succeeded ? "succeeded" : "failed",
          exitCode,
          error:
            succeeded || run.agentError
              ? null
              : exitCode !== null
                ? `${spec.label} exited with code ${exitCode}.`
                : `${spec.label} was stopped by ${signal ?? "a signal"}.`,
        });
      },
      (error: unknown) => {
        raw.close();
        this.#deps.log(`run ${run.id}: ${(error as Error).stack ?? String(error)}`);
        this.#end(run, {
          status: "failed",
          error: `The harness lost ${spec.label}: ${(error as Error).message}`,
        });
      },
    );
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
        this.#end(run, { status: "failed", error: `The demo stopped: ${message}` });
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

  /**
   * Ends a run: its outputs are what changed in the output locations since it started. An input
   * that the run itself created or modified is kept with the digest it left, so the evaluation of
   * the run rests on what the run made of it.
   */
  #finish(run: Run, end: RunEnd): void {
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
      const produced = new Set(run.outputs.map((output) => output.path));
      for (const input of run.inputs)
        for (const p of input.paths) {
          if (!produced.has(artifactPath(p))) continue;
          const digest = this.#digests.of(artifactPath(p));
          if (digest) input.sha256[p] = digest;
        }
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
      if (this.#records.runs.get(id)?.status !== "running") {
        resolve();
        return;
      }
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

  /**
   * `POST /api/runs/:id/cancel`. An agent's process group is stopped (SIGTERM, then SIGKILL after
   * 5 s) and the answer comes once it has ended; a run that has already ended is left as it is.
   */
  async cancelRun(id: string): Promise<{ run: RunView; canceled: boolean }> {
    const run = this.#run(id);
    if (run.status !== "running") return { run: viewOf(run), canceled: false };
    const active = this.#active.get(id);
    if (active?.agent) {
      active.stopping ??= "canceled";
      active.agent.stop();
      await this.#waitForEnd(id, STOP_WAIT_MS);
    } else this.#finish(run, { status: "canceled" });
    return { run: viewOf(run), canceled: true };
  }

  /** `POST /api/runs/:id/finish`: ends a self (or wake) run with the session's report. */
  finishRun(id: string, request: FinishRequest): { run: RunView; outputs: RunOutput[] } {
    const run = this.#run(id);
    if (run.agent !== "self" && run.kind !== "wake")
      throw refuse("invalid-request", "error.notSelf", { run: id, agent: run.agent });
    if (run.status !== "running")
      throw refuse("invalid-request", "error.ended", { run: id, status: run.status });
    run.report = request.report;
    this.#finish(run, { status: request.status });
    return { run: viewOf(run), outputs: run.outputs };
  }

  /* ---------- evaluations ---------- */

  /**
   * `POST /api/instances/:id/evaluate`: judgments of the latest run's results, per Outcome, with
   * evidence. It replaces the instance's evaluation. Who judged comes from the caller, not the
   * request: a user, or an agent by its MCP client's name, marked self when the judged run is a
   * self run that the same MCP session performed (performedBy).
   */
  evaluate(
    instanceId: string,
    request: EvaluateRequest,
    caller: Caller,
  ): { instance: InstanceView } {
    const instance = this.#instance(instanceId);
    const { loaded, description } = this.#describe();
    const process = this.#process(loaded.model, instance.process);
    const latestId = instance.runs.at(-1);
    const latest = latestId ? this.#state.runs[latestId] : undefined;
    if (!latest) throw refuse("not-found", "error.nothingToJudge", { instance: instance.id });
    if (latest.status === "running")
      throw refuse("already-running", "error.judgeRunning", {
        run: latest.id,
        instance: instance.id,
      });
    const count = process.outcomes.length;
    const judged = new Set<number>();
    for (const { outcome } of request.judgments) {
      if (outcome >= count)
        throw refuse("invalid-judgment", "error.noOutcome", {
          where: "",
          process: process.name,
          count,
          outcome,
        });
      if (judged.has(outcome)) throw refuse("invalid-judgment", "error.judgedTwice", { outcome });
      judged.add(outcome);
    }
    let by: Judge = { kind: "user" };
    if (caller.kind === "agent") {
      const performer = this.#records.runs.get(latest.id)?.client ?? null;
      by = {
        kind: "agent",
        id: caller.client.name,
        ...(performedBy(performer, caller) ? { self: true } : {}),
      };
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
      by,
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
          ...said("finding.skillMissing", {
            process: process.name,
            location: process.skill.missing,
          }),
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
          ...said("finding.awaiting", { run: latest.id, status: latest.status }),
          evidence: [latest.id],
        });
      if (fact.stale) {
        const paths = fact.staleness.map((reason) => reason.path ?? "SKILL.md");
        findings.push({
          kind: "unverified",
          subject,
          ...said("finding.stale", { run: fact.evaluatedRun ?? "", paths: paths.join(", ") }),
          evidence: paths,
        });
      }
    }
    return { stats: null, findings, instances: facts };
  }

  /** `GET /api/assessment?format=markdown`: the assessment as Markdown, in the workspace's language. */
  assessmentMarkdown(): string {
    const assessment = this.assessment();
    const { loaded, description } = this.#describe();
    return assessmentMarkdown(assessment, {
      language: loaded.language,
      model: description.name,
      processName: (id) => description.processes.find((p) => p.id === id)?.name ?? id,
    });
  }
}
