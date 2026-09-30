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
  envLeftOut,
  mcpArgs,
  mcpConfigFile,
  parseOutputLine,
  resolveAgents,
  startsProcess,
  takesMcpServer,
  type AgentHandle,
  type AgentLaunch,
  type AgentOutput,
  type AgentSpec,
  type EventDraft,
  type McpServerLaunch,
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
import { attachmentPath, dayOf, MAX_NAME_CANDIDATES, safeFileName } from "../shared/requests.ts";
import type {
  EvaluateRequest,
  FinishRequest,
  InstantiateRequest,
  RunRequest,
  WakeRequest,
} from "../shared/schema.ts";
import { spoken, type MessageArgs, type Spoken } from "../shared/strings.ts";
import { computeStats, findingsOf, type FindingsInput, type StatsInput } from "../assess.ts";
import type {
  AgentInfo,
  Artifact,
  ArtifactType,
  Assessment,
  ClientInfo,
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
  SkillLocation,
  StateFile,
  Stats,
  StatsFilter,
  StatsMembers,
  WakeRuns,
} from "../shared/types.ts";
import { demoFile, demoReport, demoSteps } from "./demo.ts";
import { DigestCache } from "./digest.ts";
import { HarnessError, refuse } from "./errors.ts";
import { INTERRUPTED_ERROR, runError } from "./migrate.ts";
import { artifactPath, workspacePath } from "./paths.ts";
import { buildPrompt } from "./prompt.ts";
import {
  attributeOutputs,
  diffOutputs,
  shareOutputs,
  type OutputLocation,
  type OutputSnapshot,
} from "./provenance.ts";
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
import { buildWakePrompt, WAKE_LISTED } from "./wake-prompt.ts";

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
/** The WebUI is given at most this much of a SKILL.md. */
const MAX_SKILL_BYTES = 1024 * 1024;
/** The agent that a wake starts when none is named. */
const WAKE_AGENT = "claude-code";
/** The name of the harness's MCP server in the configuration of the agent that a wake starts. */
const WAKE_MCP_SERVER = "alps_harness";

/** Why a self run is interrupted when the MCP session that performs it closes before finish_run. */
export const SESSION_CLOSED_ERROR = spoken("runError.sessionClosed", {});

export interface HarnessDeps {
  parseYaml: ParseYaml;
  /** `git rev-parse HEAD` and whether the working tree is dirty; `null` outside a repository. */
  gitInfo(root: string): { head: string; dirty: boolean } | null;
  /** Runs `<command> --version` for an agent that starts a process. Never rejects. */
  checkVersion(spec: AgentSpec): Promise<VersionCheck>;
  /** Starts an agent's process in a process group of its own; throws when it cannot be started. */
  startAgent(launch: AgentLaunch, output: AgentOutput): AgentHandle;
  /**
   * How an agent starts this harness's MCP server (`bun <harness>/src/cli.ts mcp`), which a wake
   * gives the agent it starts.
   */
  mcpServer: { command: string; args: string[] };
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
 * agent through the MCP server, which names its client and the session it holds with the server,
 * and, for the agent that a wake started, that wake run.
 */
export type Caller =
  | { kind: "user" }
  | { kind: "agent"; client: ClientInfo; session: string | null; wake: string | null };

/** What woke an agent: a schedule of alps-harness.yaml, or a request (the MCP tool, the CLI, the API). */
export type WakeTrigger = { kind: "schedule"; cron: string } | { kind: "request"; caller: Caller };

/**
 * What a wake is asked, as its record keeps it: the request's text (`null` without one), the
 * attached workspace paths, the ids of the Processes that the plan must include, and whether the
 * agent starts the runs it plans.
 */
interface WakeAsked {
  request: string | null;
  attachments: string[];
  processes: string[];
  runs: WakeRuns;
}

/** A file that a person attaches to a request, as the WebUI sent it. */
export interface AttachedFile {
  name: string;
  data: Uint8Array;
}

/** What woke an agent, as the wake events say it (shared/strings.ts). */
const wokenBy = (trigger: WakeTrigger): MessageArgs<"event.woken"> =>
  trigger.kind === "schedule"
    ? { by: "schedule", cron: trigger.cron, client: "" }
    : trigger.caller.kind === "agent"
      ? { by: "client", cron: "", client: trigger.caller.client.name }
      : { by: "request", cron: "", client: "" };

/** How a run ends. */
interface RunEnd {
  status: Exclude<RunStatus, "running">;
  exitCode?: number | null;
  /** Why the harness considers the run failed or stopped (the run's error). */
  error?: Spoken | null;
}

/** A run that has not ended. */
interface ActiveRun {
  /** The output locations: each output type's concrete location, or the patterns to decide within. */
  locations: OutputLocation[];
  before: OutputSnapshot;
  /**
   * The process runs that ran at some time while this one did (each started while the other was
   * running): what they changed in the same locations is told apart from this run's outputs.
   */
  overlapping: Set<string>;
  release: () => void;
  timer: ReturnType<typeof setTimeout> | null;
  /** The agent's process, for an agent that starts one. */
  agent: AgentHandle | null;
  /** How the run ends once its agent's process has: set when it is canceled or the server stops. */
  stopping: "canceled" | "interrupted" | null;
  /**
   * A wake run: the status that its agent gave with finish_run. The run ends when the agent's
   * process does, so the usage it reports last is kept.
   */
  reported: FinishRequest["status"] | null;
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
  /** The model's signature when poll() last looked; `null` before it first did. */
  #polledModel: string | null = null;
  /** Whether each instance's evidence was stale when the WebUI last heard of it. */
  readonly #staleSent = new Map<string, boolean>();

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

  /** Sends an instance to the WebUI, noting whether its evidence was stale then (for poll()). */
  #sendInstance(view: InstanceView): void {
    this.#staleSent.set(view.id, view.facts.stale);
    this.#hooks.broadcast({ type: "instance", instance: view });
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
   * and outputs are fixed when the instance is made, because its evaluation rests on them. A new
   * instance that the agent of a running wake makes (through the MCP server the wake gave it)
   * records that wake in createdBy, and the wake's events say so.
   */
  instantiate(
    request: InstantiateRequest,
    caller: Caller = { kind: "user" },
  ): { instance: InstanceView; created: boolean } {
    const { loaded, description } = this.#describe();
    const { model } = loaded;
    let instance: Instance;
    let created: boolean;
    let wake: Run | undefined;
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
      wake = caller.kind === "agent" && caller.wake ? this.#runningWakeRun(caller.wake) : undefined;
      instance = {
        id: this.#nextId("i"),
        process: process.id,
        inputs,
        outputs,
        criteria,
        notes: request.notes,
        runs: [],
        evaluation: null,
        createdBy: wake ? { run: wake.id } : null,
      };
      this.#state.instances[instance.id] = instance;
      created = true;
    }
    this.#saveState();
    if (wake) {
      this.#emit(wake, {
        kind: "system",
        ...spoken("event.instantiated", {
          instance: instance.id,
          process: this.#process(model, instance.process).name,
        }),
      });
      this.#writeRun(wake);
    }
    const view = this.#view(instance, description);
    this.#sendInstance(view);
    return { instance: view, created };
  }

  /**
   * `POST /api/attachments`: saves the files that a person attaches to a request in the
   * attachments directory (alps-harness.yaml), in a directory for the day, each under its name
   * made harmless and free there (shared/requests.ts). Returns their paths relative to the
   * workspace, in the order given. The directory must stay inside the workspace and outside
   * .alps-harness/, also where symlinks lead; no file is written otherwise. The API checks the
   * number and sizes of the files first; here every name is found before any file is written, and
   * the files of one upload are saved all or none.
   */
  attach(files: readonly AttachedFile[]): string[] {
    if (this.#closing) throw refuse("server-unreachable", "error.stopping", {});
    const { attachments } = this.#loaded();
    const day = dayOf(Date.now());
    const folder = this.#pathIn(`${attachments}${day}/`, "attachments");
    const absolute = (relative: string): string => path.resolve(this.root, relative);
    try {
      fs.mkdirSync(absolute(folder), { recursive: true });
    } catch (error) {
      // Something other than a directory is on the way: a file, or a symlink that leads nowhere.
      const { code, message } = error as NodeJS.ErrnoException;
      if (code !== "ENOTDIR" && code !== "EEXIST" && code !== "ENOENT") throw error;
      throw refuse("no-model", "error.attachmentsDir", { folder, detail: message }, [
        absolute(folder),
      ]);
    }
    // Once the directories exist, where they lead is checked again: through a symlink made meanwhile too.
    this.#pathIn(folder, "attachments");
    // A name is taken by whatever is there, a symlink that leads nowhere too, and by the names
    // chosen for the upload's other files.
    const chosen = new Set<string>();
    const taken = (relative: string): boolean =>
      chosen.has(relative) ||
      fs.lstatSync(absolute(relative), { throwIfNoEntry: false }) !== undefined;
    const place = (file: AttachedFile): string => {
      const relative = attachmentPath(attachments, day, file.name, taken);
      if (relative === null)
        throw refuse("invalid-request", "error.attachmentNames", {
          name: safeFileName(file.name),
          folder,
          limit: MAX_NAME_CANDIDATES,
        });
      chosen.add(relative);
      return relative;
    };
    const planned = files.map(place);
    const saved: string[] = [];
    try {
      files.forEach((file, i) => {
        let relative = planned[i] ?? place(file);
        for (;;) {
          try {
            // Never over another file: one that appears between the look and the write is left
            // alone, and the next free name is taken.
            fs.writeFileSync(absolute(relative), file.data, { flag: "wx" });
            saved.push(relative);
            return;
          } catch (error) {
            if ((error as NodeJS.ErrnoException).code !== "EEXIST") throw error;
            relative = place(file);
          }
        }
      });
    } catch (error) {
      for (const relative of saved)
        try {
          fs.unlinkSync(absolute(relative));
        } catch {
          // Already gone.
        }
      throw error;
    }
    this.#deps.log(`saved ${saved.length} attachment(s) in ${folder}`);
    this.#hooks.broadcast({ type: "artifacts" });
    return saved;
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
      ...(draft.key ? { key: draft.key, args: draft.args ?? {} } : {}),
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
      this.#sendInstance(this.#view(instance, this.#describe().description));
    } catch {
      // The model cannot be read now; clients read the instance again when they need it.
    }
  }

  /**
   * `POST /api/instances/:id/run`: records a run and starts its agent. Starting is all that
   * success means. An agent that starts a process is checked first (`<command> --version`); the
   * demo starts none, and a self run is performed by the calling session, which the result's prompt
   * instructs and which ends it with finish_run. The agent of a wake that plans only starts none.
   */
  async startRun(
    instanceId: string,
    request: RunRequest,
    caller: Caller,
  ): Promise<{ run: RunView; prompt?: string }> {
    if (this.#closing) throw refuse("server-unreachable", "error.stopping", {});
    this.#refusePlanOnly(caller);
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
    // A concrete location is the only place of the run's outputs of its type; without one, the run
    // decides within the instance's pattern, or else within the type's location patterns.
    const locations: OutputLocation[] = process.outputs.map((type) => {
      const location = instance.outputs[type] ?? null;
      if (location !== null && isConcrete(location))
        return { type, patterns: [], paths: [artifactPath(location)] };
      return {
        type,
        patterns: location !== null ? [location] : [...(typeOf(type)?.paths ?? [])],
        paths: [],
      };
    });
    const active: ActiveRun = {
      locations,
      before: this.#snapshot(locations),
      overlapping: new Set(),
      release: this.#hooks.hold(),
      timer: null,
      agent: null,
      stopping: null,
      reported: null,
    };
    for (const [other, running] of this.#active) {
      if (this.#records.runs.get(other)?.kind !== "process") continue;
      running.overlapping.add(id);
      active.overlapping.add(other);
    }
    this.#active.set(id, active);
    this.#records.runs.set(id, run);
    this.#state.runs[id] = summaryOf(run);
    instance.runs.push(id);
    writeRun(this.root, run);
    this.#saveState();
    if (caller.kind === "agent" && caller.wake) this.#attach(caller.wake, run);

    if (self) this.#emit(run, { kind: "system", ...spoken("event.self", {}) });
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
      ...spoken("event.started", { agent: spec.label, version: info?.version ?? "" }),
    });
    let handle: AgentHandle;
    try {
      handle = this.#deps.startAgent(
        {
          command: spec.command ?? "",
          args,
          cwd: this.root,
          unset: envLeftOut(spec),
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
            // A wake's agent that reported with finish_run keeps that report.
            if (parsed.report !== undefined && active.reported === null) run.report = parsed.report;
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
      const failure = spoken("event.notStarted", {
        agent: spec.label,
        detail: (error as Error).message,
      });
      this.#emit(run, { kind: "error", ...failure });
      this.#end(run, { status: "failed", error: failure });
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
        // A wake's agent may have said with finish_run that it could not do what it decided.
        const reportedFailure = active.reported === "failed";
        const succeeded = exitCode === 0 && !run.agentError && !reportedFailure;
        this.#end(run, {
          status: succeeded ? "succeeded" : "failed",
          exitCode,
          error:
            succeeded || run.agentError || reportedFailure
              ? null
              : exitCode !== null
                ? spoken("runError.exited", { agent: spec.label, code: exitCode })
                : spoken("runError.signal", { agent: spec.label, signal: signal ?? "" }),
        });
      },
      (error: unknown) => {
        raw.close();
        this.#deps.log(`run ${run.id}: ${(error as Error).stack ?? String(error)}`);
        this.#end(run, {
          status: "failed",
          error: spoken("runError.lost", { agent: spec.label, detail: (error as Error).message }),
        });
      },
    );
  }

  #runDemo(run: Run, active: ActiveRun, loaded: LoadedWorkspace, process: Process): void {
    const typeName = (type: string): string =>
      loaded.model.artifacts.find((a) => a.id === type)?.name ?? type;
    const steps = demoSteps({
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
          this.#emit(run, { kind: "error", ...failure });
          this.#finish(run, { status: "failed", exitCode: 1, error: failure });
          return;
        }
        this.#emit(run, step);
        active.timer = setTimeout(tick, DEMO_STEP_MS);
      } catch (error) {
        const message = (error as Error).message;
        this.#deps.log(`demo run ${run.id}: ${(error as Error).stack ?? message}`);
        this.#end(run, {
          status: "failed",
          error: spoken("runError.demoStopped", { detail: message }),
        });
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
  ): Spoken | null {
    const target = workspacePath(this.root, location);
    if (!target.ok) return spoken("runError.demoOutside", { path: location });
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
      return spoken("runError.demoWrite", { path: file, detail: (error as Error).message });
    }
  }

  /**
   * Ends a run: its outputs are what changed in the output locations since it started. When runs
   * ran at the same time, what they can be told to have changed is left out (attributeOutputs),
   * and a change that the run holds with one of them that has ended is marked in both records. An
   * input that the run itself created or modified is kept with the digest it left, so the
   * evaluation of the run rests on what the run made of it.
   */
  #finish(run: Run, end: RunEnd): void {
    if (run.status !== "running") return;
    const active = this.#active.get(run.id);
    this.#active.delete(run.id);
    if (active?.timer) clearTimeout(active.timer);
    run.status = end.status;
    run.endedAt = Date.now();
    run.exitCode = end.exitCode ?? null;
    if (end.error) Object.assign(run, runError(end.error));
    if (active) {
      const others = [...active.overlapping].flatMap((id) => {
        const other = this.#records.runs.get(id);
        return other ? [other] : [];
      });
      const found = attributeOutputs({
        locations: active.locations,
        changes: diffOutputs(active.before, this.#snapshot(active.locations)),
        inputs: run.inputs.flatMap((input) => input.paths.map(artifactPath)),
        claimed: others.flatMap((other) =>
          other.targets.flatMap((target) =>
            target.concrete && target.path !== null ? [artifactPath(target.path)] : [],
          ),
        ),
        alone: others.length === 0,
      });
      // A run that is still running compares its outputs with this one's when it ends.
      const shared = shareOutputs(
        { id: run.id, outputs: found },
        others.filter((other) => other.status !== "running"),
      );
      run.outputs = shared.outputs;
      for (const [id, outputs] of shared.others) {
        const other = this.#records.runs.get(id);
        if (!other) continue;
        other.outputs = outputs;
        try {
          writeRun(this.root, other);
        } catch (error) {
          this.#deps.log(`cannot write run ${id}: ${(error as Error).message}`);
        }
      }
      for (const output of run.outputs) this.#state.provenance[output.path] = run.id;
      const produced = new Set(run.outputs.map((output) => output.path));
      for (const input of run.inputs)
        for (const p of input.paths) {
          if (!produced.has(artifactPath(p))) continue;
          const digest = this.#digests.of(artifactPath(p));
          if (digest) input.sha256[p] = digest;
        }
    }
    if (run.kind === "wake")
      try {
        fs.rmSync(recordPaths(this.root).mcpConfig(run.id), { force: true });
      } catch (error) {
        this.#deps.log(
          `cannot remove the MCP configuration of run ${run.id}: ${(error as Error).message}`,
        );
      }
    const seconds = Math.round((run.endedAt - run.startedAt) / 1000);
    this.#emit(run, { kind: "end", ...spoken("event.end", { status: end.status, seconds }) });
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

  /**
   * `POST /api/runs/:id/finish`: ends a self run with the session's report. A wake run's agent
   * reports the same way, and its run ends when the agent's process does, right after.
   */
  finishRun(id: string, request: FinishRequest): { run: RunView; outputs: RunOutput[] } {
    const run = this.#run(id);
    if (run.agent !== "self" && run.kind !== "wake")
      throw refuse("invalid-request", "error.notSelf", { run: id, agent: run.agent });
    if (run.status !== "running")
      throw refuse("invalid-request", "error.ended", { run: id, status: run.status });
    run.report = request.report;
    const active = this.#active.get(id);
    if (run.kind === "wake" && active?.agent) {
      active.reported = request.status;
      this.#emit(run, {
        kind: "system",
        ...spoken("event.wakeReported", { status: request.status }),
      });
      writeRun(this.root, run);
      return { run: viewOf(run), outputs: [] };
    }
    this.#finish(run, { status: request.status });
    return { run: viewOf(run), outputs: run.outputs };
  }

  /* ---------- wakes ---------- */

  /** The schedules of alps-harness.yaml; `null` while the model or the configuration cannot be read. */
  schedules(): { cron: string; agent: string }[] | null {
    try {
      return (this.#loaded().config.schedules ?? []).map(({ cron, agent }) => ({ cron, agent }));
    } catch (error) {
      if (error instanceof HarnessError) return null;
      throw error;
    }
  }

  /** The wake run that has not ended; there is at most one. */
  #runningWake(): Run | undefined {
    for (const id of this.#active.keys()) {
      const run = this.#records.runs.get(id);
      if (run?.kind === "wake") return run;
    }
    return undefined;
  }

  /** A wake while another runs is skipped; the events of the one that runs record it. */
  #skip(running: Run, trigger: WakeTrigger): { skipped: true; running: string } {
    const skipped = spoken("event.wakeSkipped", wokenBy(trigger));
    this.#emit(running, { kind: "system", ...skipped });
    try {
      writeRun(this.root, running);
    } catch (error) {
      this.#deps.log(`cannot write run ${running.id}: ${(error as Error).message}`);
    }
    this.#deps.log(`${skipped.text} (wake run ${running.id})`);
    return { skipped: true, running: running.id };
  }

  /** Writes a run's record; a failure is logged, and the record in memory stays as it is. */
  #writeRun(run: Run): void {
    try {
      writeRun(this.root, run);
    } catch (error) {
      this.#deps.log(`cannot write run ${run.id}: ${(error as Error).message}`);
    }
  }

  /**
   * The wake run `id` while it runs: what its agent does through the MCP server that the wake gave
   * it (X-Harness-Wake) is recorded in it. An ended or unknown wake gets nothing.
   */
  #runningWakeRun(id: string): Run | undefined {
    const wake = this.#records.runs.get(id);
    return wake?.kind === "wake" && wake.status === "running" ? wake : undefined;
  }

  /**
   * Refuses a run or a wake that the agent of a wake asked for a plan only (runs: plan) starts,
   * through the MCP server the wake gave it (X-Harness-Wake): the harness keeps that agent to
   * instantiating, whatever its prompt made of it. Instantiating, evaluating, and reporting stay open.
   */
  #refusePlanOnly(caller: Caller | null): void {
    if (caller?.kind !== "agent" || !caller.wake) return;
    const wake = this.#records.runs.get(caller.wake);
    if (wake?.kind === "wake" && wake.runs === "plan")
      throw refuse("invalid-request", "error.planOnly", { run: wake.id });
  }

  /** Lists a run in the wake run whose agent started it, through the MCP server the wake gave it. */
  #attach(wakeId: string, run: Run): void {
    const wake = this.#runningWakeRun(wakeId);
    if (!wake) return;
    wake.started = [...(wake.started ?? []), run.id];
    this.#emit(wake, {
      kind: "system",
      ...spoken("event.attached", { run: run.id, agent: run.agent, instance: run.instance ?? "" }),
    });
    this.#writeRun(wake);
  }

  /**
   * What a wake is asked, checked against the workspace: the Processes it names, by id (a name
   * the model does not have is not-found), and its attachments, relative to the workspace, which
   * must exist inside it and outside .alps-harness/.
   */
  #asked(request: WakeRequest): WakeAsked {
    const { model } = this.#loaded();
    const processes = [...new Set(request.processes.map((key) => this.#process(model, key).id))];
    const attachments = [
      ...new Set(
        request.attachments.map((given, i) => {
          const where = `attachments.${i}`;
          const inside = artifactPath(this.#pathIn(given, where));
          if (!fileState(this.root, inside))
            throw refuse("invalid-request", "error.noAttachment", { where, path: given });
          return inside;
        }),
      ),
    ];
    return { request: request.request || null, attachments, processes, runs: request.runs };
  }

  /**
   * What a wake's agent is told: what it is asked, if anything, where the model and the guidance
   * are, and the state now.
   */
  #wakePrompt(
    run: string,
    since: number | null,
    loaded: LoadedWorkspace,
    description: ModelDescription,
    agents: AgentInfo[],
    asked: WakeAsked,
  ): string {
    const changed = this.artifacts(since === null ? {} : { changedSince: since });
    const instances = Object.values(this.#state.instances).sort(
      (a, b) => seqOf(b.id) - seqOf(a.id),
    );
    const facts = instances.map((instance) => this.#facts(instance, description));
    const findings = findingsOf({
      processes: description.processes,
      artifacts: description.artifacts,
      agents,
      facts: [...facts].reverse(),
      ...this.#skillUse(description.processes),
      sharedOrigins: this.#sharedOrigins(),
    });
    const { model } = loaded;
    const requested =
      asked.request !== null ||
      asked.attachments.length > 0 ||
      asked.processes.length > 0 ||
      asked.runs === "plan";
    return buildWakePrompt({
      language: loaded.language,
      root: this.root,
      run,
      server: WAKE_MCP_SERVER,
      request: requested
        ? {
            text: asked.request,
            attachments: asked.attachments,
            processes: asked.processes.map((id) => ({
              id,
              name: model.processes.find((p) => p.id === id)?.name ?? id,
            })),
            runs: asked.runs,
          }
        : null,
      modelPath: description.modelPath,
      guidance: (loaded.config.guidance ?? []).map((file) => ({
        path: file,
        found: fs.existsSync(path.resolve(this.root, file)),
      })),
      since,
      changed: {
        listed: changed.artifacts.slice(0, WAKE_LISTED),
        total: changed.artifacts.length,
        truncated: changed.truncated,
      },
      instances: {
        listed: instances
          .slice(0, WAKE_LISTED)
          .map((instance, i) => ({ ...instance, facts: facts[i] as InstanceFacts })),
        total: instances.length,
      },
      findings: { listed: findings.slice(0, WAKE_LISTED), total: findings.length },
      agents: agents.filter((agent) => agent.available).map((agent) => agent.id),
      typeName: (type) => model.artifacts.find((a) => a.id === type)?.name ?? type,
      processName: (id) => model.processes.find((p) => p.id === id)?.name ?? id,
    });
  }

  /**
   * `POST /api/wake` and the schedules: records a wake run (no instance) and starts its agent with
   * this harness's MCP server, through which it instantiates, runs, waits, evaluates, and reports.
   * A wake may be given a request: its text, attachments, and the Processes that the plan must
   * include go into the prompt and the record, and with `runs: plan` the agent only instantiates:
   * the harness refuses the runs and wakes it would start. The harness decides nothing about what
   * runs and interprets neither the request nor the guidance. Only one wake runs at a time: while
   * one runs, another is skipped, and the events of the one that runs record the skip. A request
   * that names what the workspace does not have is refused first, before it could be skipped.
   */
  async wake(
    request: WakeRequest,
    trigger: WakeTrigger,
  ): Promise<{ run: RunView; skipped: false } | { skipped: true; running: string }> {
    if (this.#closing) throw refuse("server-unreachable", "error.stopping", {});
    this.#refusePlanOnly(trigger.kind === "request" ? trigger.caller : null);
    const asked = this.#asked(request);
    const earlier = this.#runningWake();
    if (earlier) return this.#skip(earlier, trigger);
    const name = request.agent ?? WAKE_AGENT;
    const agentSpec = (loaded: LoadedWorkspace): { spec: AgentSpec; specs: AgentSpec[] } => {
      const specs = resolveAgents(loaded.config.agents);
      const spec = specs.find((s) => s.id === name);
      if (!spec)
        throw refuse("agent-unavailable", "error.noAgent", {
          agent: name,
          agents: specs.map((s) => s.id).join(", "),
        });
      if (!takesMcpServer(spec))
        throw refuse("agent-unavailable", "error.wakeAgent", {
          agent: spec.label,
          agents: specs
            .filter(takesMcpServer)
            .map((s) => s.id)
            .join(", "),
        });
      return { spec, specs };
    };
    const checked = agentSpec(this.#loaded());
    const info = await this.#availability(checked.spec, checked.specs);
    if (!info.available)
      throw refuse("agent-unavailable", "error.agentUnavailable", {
        agent: checked.spec.label,
        reason: info.reason ?? "it is not available",
      });
    const agents = await this.#checkAgents(checked.specs);
    // From here on nothing waits, so no other wake comes between the checks and the record.
    if (this.#closing) throw refuse("server-unreachable", "error.stopping", {});
    const other = this.#runningWake();
    if (other) return this.#skip(other, trigger);
    const { loaded, description } = this.#describe();
    const { spec } = agentSpec(loaded);
    const now = Date.now();
    const id = this.#nextId("r");
    const since = this.#state.lastWakeAt;
    const prompt = this.#wakePrompt(id, since, loaded, description, agents, asked);
    // The agent's MCP server names this wake, so the runs it starts are listed in started.
    const server: McpServerLaunch = {
      name: WAKE_MCP_SERVER,
      command: this.#deps.mcpServer.command,
      args: [...this.#deps.mcpServer.args, "--wake", id],
      env: { ALPS_WORKSPACE: this.root },
    };
    const configFile = recordPaths(this.root).mcpConfig(id);
    const args = argsFor(
      { ...spec, args: [...spec.args, ...mcpArgs(spec, server, configFile)] },
      prompt,
    );
    const run: Run = {
      id,
      kind: "wake",
      instance: null,
      process: null,
      agent: spec.id,
      status: "running",
      createdAt: now,
      startedAt: now,
      endedAt: null,
      exitCode: null,
      error: null,
      agentError: null,
      inputs: [],
      targets: [],
      outputs: [],
      usage: null,
      report: "",
      events: 0,
      command: commandLine(spec, args, prompt),
      client: null,
      prompt,
      git: this.#deps.gitInfo(this.root),
      skill: null,
      started: [],
      ...asked,
    };
    const active: ActiveRun = {
      locations: [],
      before: new Map(),
      overlapping: new Set(),
      release: this.#hooks.hold(),
      timer: null,
      agent: null,
      stopping: null,
      reported: null,
    };
    this.#active.set(id, active);
    this.#records.runs.set(id, run);
    this.#state.runs[id] = summaryOf(run);
    this.#state.lastWakeAt = now;
    writeRun(this.root, run);
    this.#saveState();
    this.#emit(run, { kind: "system", ...spoken("event.woken", wokenBy(trigger)) });
    if (spec.format === "claude")
      try {
        fs.writeFileSync(configFile, mcpConfigFile(server));
      } catch (error) {
        const failure = spoken("event.mcpConfig", {
          agent: spec.label,
          detail: (error as Error).message,
        });
        this.#emit(run, { kind: "error", ...failure });
        this.#end(run, { status: "failed", error: failure });
        return { run: viewOf(run), skipped: false };
      }
    this.#runAgent(run, active, spec, info, args);
    this.#announce(run);
    return { run: viewOf(run), skipped: false };
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
    this.#sendInstance(view);
    return { instance: view };
  }

  /* ---------- statistics and assessment ---------- */

  /** What the statistics are computed from: the records, and which evaluations are stale now. */
  #statsInput(description: ModelDescription, facts?: readonly InstanceFacts[]): StatsInput {
    const instances = Object.values(this.#state.instances);
    const stale = new Set<string>();
    if (facts) {
      for (const fact of facts) if (fact.stale) stale.add(fact.instance);
    } else {
      for (const instance of instances)
        if (instance.evaluation && this.#facts(instance, description).stale) stale.add(instance.id);
    }
    return {
      processes: description.processes.map((p) => ({ id: p.id, outcomes: p.outcomes })),
      instances,
      runs: [...this.#records.runs.values()],
      stale,
    };
  }

  /**
   * `GET /api/stats`: the dashboard's statistics for a filter, with what each number counts.
   * Days and weeks start at `utcOffsetMinutes` east of UTC (the server's own zone by default).
   */
  stats(
    filter: StatsFilter,
    utcOffsetMinutes = localUtcOffset(),
  ): { stats: Stats; members: StatsMembers } {
    const { loaded, description } = this.#describe();
    const resolved: StatsFilter = { ...filter };
    if (filter.process !== undefined)
      resolved.process = this.#process(loaded.model, filter.process).id;
    return computeStats(this.#statsInput(description), resolved, {
      now: Date.now(),
      utcOffsetMinutes,
    });
  }

  /**
   * The Artifacts whose latest change, as provenance names it, the run holds together with runs
   * that ran at the same time (RunOutput.sharedWith).
   */
  #sharedOrigins(): FindingsInput["sharedOrigins"] {
    const shared: { path: string; type: string; runs: string[] }[] = [];
    for (const [artifact, id] of Object.entries(this.#state.provenance)) {
      const output = this.#records.runs.get(id)?.outputs.find((o) => o.path === artifact);
      if (output?.sharedWith?.length)
        shared.push({ path: artifact, type: output.type, runs: [id, ...output.sharedWith] });
    }
    return shared;
  }

  /** The SKILL.md that the latest process run of each Process used, and each SKILL.md's digest now. */
  #skillUse(processes: readonly ProcessView[]): Pick<FindingsInput, "lastSkillUse" | "skillNow"> {
    const lastSkillUse = new Map<string, { run: string; path: string; sha256: string | null }>();
    const startedAt = new Map<string, number>();
    for (const run of this.#records.runs.values()) {
      if (run.kind !== "process" || !run.process || !run.skill) continue;
      if ((startedAt.get(run.process) ?? Number.NEGATIVE_INFINITY) > run.startedAt) continue;
      startedAt.set(run.process, run.startedAt);
      lastSkillUse.set(run.process, { run: run.id, ...run.skill });
    }
    const skillNow = new Map<string, string | null>();
    for (const process of processes)
      if (process.skill && "path" in process.skill)
        skillNow.set(process.id, this.#digests.of(process.skill.path));
    return { lastSkillUse, skillNow };
  }

  /**
   * `GET /api/assessment`: the statistics (all time by week, or since `since`), the findings that
   * follow from the records, the model, and the configuration, and the facts of each instance.
   */
  async assessment(since?: number): Promise<Assessment> {
    const agents = await this.model().then((model) => model.agents);
    const { description } = this.#describe();
    const facts = Object.values(this.#state.instances)
      .sort((a, b) => seqOf(a.id) - seqOf(b.id))
      .map((instance) => this.#facts(instance, description));
    const findings = findingsOf({
      processes: description.processes,
      artifacts: description.artifacts,
      agents,
      facts,
      ...this.#skillUse(description.processes),
      sharedOrigins: this.#sharedOrigins(),
    });
    const { stats } = computeStats(
      this.#statsInput(description, facts),
      { period: "all", granularity: "week", ...(since === undefined ? {} : { since }) },
      { now: Date.now(), utcOffsetMinutes: localUtcOffset() },
    );
    return { stats, findings, instances: facts };
  }

  /** `GET /api/assessment?format=markdown`: the assessment as Markdown, in the workspace's language. */
  async assessmentMarkdown(since?: number): Promise<string> {
    const assessment = await this.assessment(since);
    const { loaded, description } = this.#describe();
    const processOf = (id: string) => description.processes.find((p) => p.id === id);
    return assessmentMarkdown(assessment, {
      language: loaded.language,
      model: description.name,
      processName: (id) => processOf(id)?.name ?? id,
      outcomeText: (id, outcome) => processOf(id)?.outcomes[outcome] ?? "",
    });
  }

  /** `GET /api/skill`: the text of a Process's SKILL.md, for the WebUI to show. */
  skill(key: string): { skill: SkillLocation; text: string; truncated: boolean } {
    const { loaded, description } = this.#describe();
    const process = this.#process(loaded.model, key);
    const skill = description.processes.find((p) => p.id === process.id)?.skill;
    if (!skill || "missing" in skill)
      throw refuse("not-found", "error.noSkill", { process: process.name });
    let bytes: Buffer;
    try {
      bytes = fs.readFileSync(path.resolve(this.root, skill.path));
    } catch {
      throw refuse("not-found", "error.noSkill", { process: process.name });
    }
    return {
      skill,
      text: bytes.subarray(0, MAX_SKILL_BYTES).toString("utf8"),
      truncated: bytes.length > MAX_SKILL_BYTES,
    };
  }

  /* ---------- changes on disk ---------- */

  /**
   * What changed on disk since the last call, as events for the WebUI: the model, the
   * configuration, or a SKILL.md (`model`), and evaluations whose evidence became stale or current
   * again (`instance`). The first call only takes note. The server calls it every few seconds while
   * a WebUI is connected; nothing else notices an edit made outside the harness.
   */
  poll(): ServerEvent[] {
    let model: string;
    let description: ModelDescription | null = null;
    try {
      const described = this.#describe();
      description = described.description;
      model = [
        this.#modelSignature(described.loaded.modelPath),
        ...description.processes.map((p) =>
          p.skill && "path" in p.skill ? `${p.skill.path}:${this.#digests.of(p.skill.path)}` : "-",
        ),
      ].join("|");
    } catch (error) {
      model = `unreadable: ${(error as Error).message}`;
    }
    const events: ServerEvent[] = [];
    if (this.#polledModel !== null && this.#polledModel !== model) events.push({ type: "model" });
    this.#polledModel = model;
    if (description)
      for (const instance of Object.values(this.#state.instances)) {
        if (!instance.evaluation) continue;
        const view = this.#view(instance, description);
        const before = this.#staleSent.get(instance.id);
        if (before === undefined) this.#staleSent.set(instance.id, view.facts.stale);
        else if (before !== view.facts.stale) {
          this.#staleSent.set(instance.id, view.facts.stale);
          events.push({ type: "instance", instance: view });
        }
      }
    return events;
  }
}

/** Minutes east of UTC on this machine now. */
const localUtcOffset = (): number => -new Date().getTimezoneOffset();
