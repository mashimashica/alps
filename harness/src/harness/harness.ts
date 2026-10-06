/*
 * The harness of one workspace: instances, runs, provenance, evaluations, and assessments. While
 * its server runs it is the only writer of .alps-harness/. It reads the model and the
 * configuration again whenever their files change; the local authoring API may write the model
 * file explicitly. Runtime-agnostic:
 * reading YAML, `git`, agent version checks, and starting agent processes are passed in by
 * src/server/.
 */

import { externalTracking } from "../shared/schema.ts";
import { definitionChanged, evaluationBasis, evaluationContext } from "./evaluation-basis.ts";
import { buildWorkObjects } from "./work-objects.ts";
import { withAgentSelection } from "../agents/models.ts";
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
  buildDesignPrompt,
  designCapabilities as designAgentCapabilities,
  designCommand,
  designSources,
  desktopProviderInstalled,
  desktopProviderOpenArgs,
  isolatedCwd,
  modelWriteFromWorkspace,
  newDesignId,
  parseDesignOutput,
  proposalWithRevision,
  readDesign,
  readDesignReferences,
  safeDesignSpec,
  validateDesignInputs,
  writeDesign,
} from "./designs.ts";
import {
  claudeProjectConfig,
  codexProjectConfig,
  mcpServerForWorkspace,
  probeMcpServer,
} from "../server/preflight.ts";
import {
  CONFIG_FILES,
  MODEL_FILES,
  ModelError,
  ModelRevisionError,
  describeModel,
  updateWorkspaceModel,
  fileState,
  isConcrete,
  loadWorkspace,
  scanLocations,
  signature,
  type LoadedWorkspace,
  type ParseYaml,
} from "../model/index.ts";
import {
  saveDesignBundle,
  saveMissingDesignSkills,
  snapshotDesignSkills,
} from "../model/design-bundle.ts";
import { attachmentPath, dayOf, MAX_NAME_CANDIDATES, safeFileName } from "../shared/requests.ts";
import { updateModelRequest } from "../shared/schema.ts";
import type {
  AssessRequest,
  EvaluateRequest,
  FinishRequest,
  InstantiateRequest,
  RecordAssessmentRequest,
  RecordObservationRequest,
  ReviewRequest,
  RunRequest,
  WakeRequest,
  UpdateModelRequest,
  CreateDesignRequest,
  DesignApplyRequest,
  DesignMessageRequest,
  DesignClaimRequest,
  DesignOpenRequest,
  DesignSubmitProposalRequest,
  DesignSubmitQuestionsRequest,
} from "../shared/schema.ts";
import { spoken, type MessageArgs, type Spoken } from "../shared/strings.ts";
import {
  computeStats,
  countSince,
  findingsOf,
  type FindingsInput,
  type StatsInput,
} from "../assess.ts";
import type {
  AgentInfo,
  AgentModel,
  AgentModelsResponse,
  AgentSelection,
  DesignCapabilitiesResponse,
  DesignProposal,
  DesignResponse,
  DesignSession,
  RunExecution,
  Artifact,
  ArtifactType,
  AssessScope,
  Assessment,
  AssessmentItem,
  AssessmentOverview,
  ClientInfo,
  Evaluation,
  Instance,
  InstanceFacts,
  InstanceView,
  Judge,
  ListedRun,
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
  RunObservation,
  RunOutput,
  RunKind,
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
import { buildAssessPrompt } from "./assess-prompt.ts";
import { checkedItems, type ItemDraft } from "./assessment.ts";
import { demoFile, demoReport, demoSteps } from "./demo.ts";
import { DigestCache } from "./digest.ts";
import { HarnessError, refuse } from "./errors.ts";
import { INTERRUPTED_ERROR, runError } from "./migrate.ts";
import { artifactPath, workspacePath } from "./paths.ts";
import { buildPrompt, workContextPrompt } from "./prompt.ts";
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
  writeAssessment,
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
/** The design agent is stopped if it cannot return a bounded proposal in time. */
const DESIGN_AGENT_TIMEOUT_MS = 10 * 60_000;
/** The design agent's stdout and stderr are kept in memory only up to this many bytes. */
const MAX_DESIGN_OUTPUT_BYTES = 2 * 1024 * 1024;
/** The agent that a wake starts when none is named. */
const WAKE_AGENT = "claude-code";
/** The agent that an assessment starts when none is named. */
const ASSESS_AGENT = "claude-code";
/**
 * The name of the harness's MCP server in the configuration of the agent that a wake or an
 * assessment starts.
 */
const WAKE_MCP_SERVER = "alps_harness";

/** Why a self run is interrupted when the MCP session that performs it closes before finish_run. */
export const SESSION_CLOSED_ERROR = spoken("runError.sessionClosed", {});

export interface HarnessDeps {
  parseYaml: ParseYaml;
  /** `git rev-parse HEAD` and whether the working tree is dirty; `null` outside a repository. */
  gitInfo(root: string): { head: string; dirty: boolean } | null;
  /** Runs `<command> --version` for an agent that starts a process. Never rejects. */
  checkVersion(spec: AgentSpec): Promise<VersionCheck>;
  readAgentModels(spec: AgentSpec, root: string): Promise<AgentModel[]>;
  /** Starts an agent's process in a process group of its own; throws when it cannot be started. */
  startAgent(launch: AgentLaunch, output: AgentOutput): AgentHandle;
  /**
   * How an agent starts this harness's MCP server (`bun <harness>/src/cli.ts mcp`), which a wake
   * gives the agent it starts.
   */
  mcpServer: { command: string; args: string[] };
  /** Optional telemetry sink. It must never throw or block a run from continuing. */
  observe?: (
    name: string,
    attributes: Record<string, string | number | boolean>,
  ) => { traceId: string; spanId: string } | null;
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
 * and, for the agent that a wake or an assessment started, that run.
 */
export type Caller =
  | { kind: "user" }
  | {
      kind: "agent";
      client: ClientInfo;
      session: string | null;
      wake: string | null;
      assess: string | null;
    };

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
   * A wake or assessment run: the status that its agent gave with finish_run. The run ends when
   * the agent's process does, so the usage it reports last is kept.
   */
  reported: FinishRequest["status"] | null;
}

interface ActiveDesign {
  release: () => void;
  agent: AgentHandle;
  cwd: string;
  timer: ReturnType<typeof setTimeout> | null;
}

interface PendingDesign {
  key: string;
  promise: Promise<DesignResponse>;
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
 * Records a new evaluation of an instance: the one it replaces goes to the front of the
 * instance's evaluations, which keep the replaced evaluations newest first.
 */
export function supersede(instance: Instance, evaluation: Evaluation): void {
  if (instance.evaluation)
    instance.evaluations = [instance.evaluation, ...(instance.evaluations ?? [])];
  instance.evaluation = evaluation;
}

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
  readonly #activeDesigns = new Map<string, ActiveDesign>();
  readonly #pendingDesigns = new Map<string, PendingDesign>();
  readonly #waiters = new Map<string, Set<() => void>>();
  #workspace: { loaded: LoadedWorkspace; signature: string } | null = null;
  #agentChecks: { key: string; at: number; info: Promise<AgentInfo[]> } | null = null;
  readonly #agentCatalogs = new Map<
    string,
    { at: number; pending: boolean; result: Promise<AgentModelsResponse> }
  >();
  readonly #digests: DigestCache;
  #closing: Promise<void> | null = null;
  /** The model's signature when poll() last looked; `null` before it first did. */
  #polledModel: string | null = null;
  /** Whether each instance's evidence was stale when the WebUI last heard of it. */
  readonly #staleSent = new Map<string, boolean>();

  #observe(
    run: Run,
    kind: RunObservation["kind"],
    message: string,
    options: {
      source?: RunObservation["source"];
      coverage?: RunObservation["coverage"];
      trace?: RunObservation["trace"];
      attributes?: Record<string, string | number | boolean>;
    } = {},
  ): RunObservation {
    const observations = run.observations ?? [];
    const id = `${run.id}:o${observations.length + 1}`;
    const attributes = {
      "alps.run": run.id,
      "alps.run.kind": run.kind,
      "alps.run.agent": run.agent,
      "alps.observation": id,
      ...(run.process ? { "alps.process": run.process } : {}),
      ...(run.instance ? { "alps.instance": run.instance } : {}),
      ...(run.execution?.launchId ? { "alps.launch": run.execution.launchId } : {}),
      ...options.attributes,
    };
    let trace: RunObservation["trace"] | undefined = options.trace;
    try {
      trace ??= this.#deps.observe?.(`alps.${kind}`, attributes) ?? undefined;
    } catch (error) {
      this.#deps.log(`cannot record telemetry for ${run.id}: ${(error as Error).message}`);
    }
    const observation: RunObservation = {
      id,
      at: Date.now(),
      source: options.source ?? "alps",
      kind,
      coverage: options.coverage ?? "observed",
      message: message.slice(0, 1000),
      ...(trace ? { trace } : {}),
      ...(Object.keys(attributes).length ? { attributes } : {}),
    };
    run.observations = [...observations.slice(-199), observation];
    this.#writeRun(run);
    return observation;
  }

  observation(id: string): { run: string } | null {
    for (const run of this.#records.runs.values())
      if (run.observations?.some((observation) => observation.id === id)) return { run: run.id };
    return null;
  }

  recordObservation(id: string, request: RecordObservationRequest): RunObservation {
    const run = this.#run(id);
    return this.#observe(run, request.kind, request.message, {
      source: request.source,
      coverage: request.coverage,
      trace: request.trace,
      attributes: request.attributes,
    });
  }

  observeTool(caller: Caller, operation: string, ok: boolean, status: number): void {
    if (caller.kind !== "agent") return;
    const run =
      (caller.wake ? this.#records.runs.get(caller.wake) : undefined) ??
      (caller.assess ? this.#records.runs.get(caller.assess) : undefined) ??
      (caller.session ? this.externalRunFor(caller.session) : undefined);
    if (!run || run.status !== "running") return;
    this.#observe(run, "tool.called", `${operation} ${ok ? "succeeded" : "failed"}`, {
      attributes: {
        "alps.tool.operation": operation,
        "alps.tool.ok": ok,
        "http.response.status_code": status,
      },
    });
  }

  /** Reads the records; throws a StateError when state.json cannot be used. Nothing is written yet. */
  constructor(root: string, deps: HarnessDeps) {
    this.root = root;
    this.#deps = deps;
    this.#digests = new DigestCache(root);
    this.#readSignature = stateSignature(root);
    this.#records = loadRecords(root);
    for (const { id, reason } of this.#records.unreadable)
      deps.log(`the record of run ${id} cannot be read: ${reason}`);
    for (const { id, reason } of this.#records.unreadableAssessments)
      deps.log(`the assessment of run ${id} cannot be read: ${reason}`);
  }

  /**
   * Called once the server owns the workspace: writes what loading changed and starts reporting.
   * Records that a stopping server wrote after they were read are read again.
   */
  start(hooks: HarnessHooks): void {
    this.#hooks = hooks;
    // Design children belong to this server process. A persisted "running" record from a
    // previous owner cannot be resumed or claimed as active after a server restart.
    const previousDesigns = path.join(recordPaths(this.root).dir, "designs");
    if (fs.existsSync(previousDesigns)) {
      for (const filename of fs.readdirSync(previousDesigns)) {
        if (!/^[A-Za-z0-9_-]{8,80}\.json$/.test(filename)) continue;
        const design = readDesign(this.root, filename.slice(0, -5));
        if (design?.status !== "running") continue;
        writeDesign(this.root, {
          ...design,
          status: "failed",
          updatedAt: Date.now(),
          error:
            "The previous design generation was interrupted when the runtime stopped. The request and draft are preserved; continue the design or start again.",
        });
      }
    }
    if (stateSignature(this.root) !== this.#readSignature) this.#records = loadRecords(this.root);
    if (this.#records.changes.convertedV1 !== null)
      this.#deps.log("converted state.json from version 1; the original is kept as state.v1.json");
    persist(this.root, this.#records);
    for (const run of this.#records.runs.values()) {
      if (run.status !== "running" || !run.execution || run.execution.method === "cli") continue;
      let locations: OutputLocation[] = [];
      let before: OutputSnapshot = new Map();
      let overlapping = new Set<string>();
      try {
        const saved = externalTracking.parse(
          JSON.parse(fs.readFileSync(this.#trackingFile(run.id), "utf8")),
        );
        locations = saved.locations;
        before = new Map(saved.before);
        overlapping = new Set(saved.overlapping);
      } catch (error) {
        // Never attribute all existing files to a run when its original snapshot is missing.
        if (run.kind === "process") {
          run.execution.attributionUnknown = true;
          this.#writeRun(run);
        }
        this.#deps.log(
          `Output attribution snapshot unavailable for ${run.id}: ${(error as Error).message}`,
        );
      }
      this.#active.set(run.id, {
        locations,
        before,
        overlapping,
        release: this.#hooks.hold(),
        timer: null,
        agent: null,
        stopping: null,
        reported: null,
      });
    }
  }

  /**
   * Stops the agents of the runs that have not ended, records those runs as interrupted, and
   * writes the records. Resolves once every agent's process group has ended (they get SIGKILL
   * after 5 seconds), or after a few seconds more.
   */
  close(): Promise<void> {
    this.#closing ??= (async () => {
      const waits: Promise<void>[] = [];
      for (const [id, active] of this.#activeDesigns) {
        active.agent.stop();
        if (active.timer) clearTimeout(active.timer);
        active.release();
        this.#activeDesigns.delete(id);
        fs.rmSync(active.cwd, { recursive: true, force: true });
        try {
          const session = readDesign(this.root, id);
          if (session?.status === "running") {
            const failed = {
              ...session,
              status: "failed" as const,
              updatedAt: Date.now(),
              error: "The harness server stopped before design generation ended.",
            };
            writeDesign(this.root, failed);
          }
        } catch (error) {
          this.#deps.log(
            `cannot record the end of design session ${id}: ${(error as Error).message}`,
          );
        }
      }
      for (const [id, active] of this.#active) {
        const run = this.#records.runs.get(id);
        if (!run?.execution || run.execution.method === "cli") continue;
        run.execution.disconnectedAt = Date.now();
        this.#writeRun(run);
        active.release();
        this.#active.delete(id);
      }
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
      if (run?.client?.session !== session) continue;
      if (run.execution && run.execution.method !== "cli") {
        run.execution.disconnectedAt = Date.now();
        if (run.execution.session)
          run.execution.session = {
            ...run.execution.session,
            coverage: "disconnected",
            capturedAt: Date.now(),
          };
        this.#observe(run, "run.disconnected", "The MCP connection for this host run closed.", {
          coverage: "reference-only",
        });
        this.#writeRun(run);
        this.#announce(run);
      } else this.#end(run, { status: "interrupted", error: SESSION_CLOSED_ERROR });
    }
  }

  get #state(): StateFile {
    return this.#records.state;
  }

  /** Bind one external attempt to an MCP connection; do not infer a host thread from that connection. */
  bindExternal(id: string, caller: Caller, sessionId?: string): { run: RunView; prompt: string } {
    const run = this.#run(id);
    if (
      caller.kind !== "agent" ||
      !caller.session ||
      !run.execution ||
      run.execution.method === "cli" ||
      run.status !== "running"
    )
      throw refuse("invalid-request", "error.externalSession", {});
    if (run.client?.session !== caller.session && !run.execution.sessionId)
      throw refuse("invalid-request", "error.externalIdentity", {});
    if (run.client?.session !== caller.session && !run.execution.disconnectedAt)
      throw refuse("already-running", "error.externalConnected", {});
    const bound = this.externalRunFor(caller.session);
    if (bound && bound.id !== id) throw refuse("already-running", "error.externalConnected", {});
    if (
      run.execution.sessionId &&
      run.execution.sessionId !== sessionId &&
      !(run.client?.session === caller.session && !sessionId)
    )
      throw refuse("invalid-request", "error.externalIdentity", {});
    run.client = { ...caller.client, session: caller.session };
    if (sessionId) {
      run.execution.sessionId = sessionId;
      run.execution.session = {
        id: sessionId,
        source: run.execution.session?.source ?? "claim",
        capturedAt: Date.now(),
        coverage: "reference-only",
        note: "ALPS has a host conversation id, but no transcript reader is attached.",
      };
    }
    delete run.execution.disconnectedAt;
    this.#writeRun(run);
    this.#observe(
      run,
      run.execution.session ? "run.reconnected" : "launch.claimed",
      "The host session claimed this run.",
      {
        coverage: sessionId ? "reference-only" : "observed",
        attributes: {
          "alps.mcp.session": caller.session,
          ...(sessionId ? { "alps.host.session": sessionId } : {}),
        },
      },
    );
    this.#announce(run);
    return { run: viewOf(run), prompt: run.prompt };
  }

  #trackingFile(id: string): string {
    return path.join(this.root, ".alps-harness", "runs", `${id}.tracking.json`);
  }
  #persistExternalActive(run: Run): void {
    if (!run.execution || run.execution.method === "cli") return;
    const active = this.#active.get(run.id);
    if (!active) return;
    const file = this.#trackingFile(run.id);
    fs.mkdirSync(path.dirname(file), { recursive: true, mode: 0o700 });
    fs.writeFileSync(
      `${file}.tmp`,
      JSON.stringify({
        locations: active.locations,
        before: [...active.before],
        overlapping: [...active.overlapping],
      }),
      { mode: 0o600 },
    );
    fs.renameSync(`${file}.tmp`, file);
  }
  runForLaunch(id: string): Run | undefined {
    return [...this.#records.runs.values()].find((run) => run.execution?.launchId === id);
  }
  runExecution(id: string): RunExecution | undefined {
    return this.#records.runs.get(id)?.execution;
  }
  externalRunFor(session: string): Run | undefined {
    return [...this.#records.runs.values()].find(
      (run) =>
        run.status === "running" &&
        run.execution &&
        run.execution.method !== "cli" &&
        run.client?.session === session,
    );
  }
  activeConversation(sessionId: string): boolean {
    return [...this.#records.runs.values()].some(
      (run) => run.status === "running" && run.execution?.sessionId === sessionId,
    );
  }

  externalDesignFor(session: string): DesignSession | undefined {
    const designs = path.join(this.root, ".alps-harness", "designs");
    if (!fs.existsSync(designs)) return undefined;
    for (const file of fs.readdirSync(designs)) {
      if (!file.endsWith(".json")) continue;
      const design = readDesign(this.root, file.slice(0, -5));
      if (design?.method === "desktop" && design.desktop?.mcpSession === session) return design;
    }
    return undefined;
  }

  externalCaller(caller: Caller): Caller {
    if (caller.kind !== "agent" || !caller.session) return caller;
    const runs = [...this.#records.runs.values()].filter(
      (run) =>
        run.status === "running" &&
        run.execution?.method !== "cli" &&
        run.execution &&
        run.client?.session === caller.session,
    );
    const wake = runs.find((run) => run.kind === "wake");
    const assess = runs.find((run) => run.kind === "assess");
    return { ...caller, wake: wake?.id ?? caller.wake, assess: assess?.id ?? caller.assess };
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
      if (error instanceof ModelRevisionError)
        throw refuse("invalid-request", "error.modelChanged", {});
      throw error;
    }
  }

  #describe(): { loaded: LoadedWorkspace; description: ModelDescription; revision: string } {
    const loaded = this.#loaded();
    const revision = this.#modelSignature(loaded.modelPath);
    return { loaded, description: describeModel(loaded, this.#deps.parseYaml, revision), revision };
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

  /** `POST /api/model`: replaces the model meaning file after checking the revision the UI read. */
  async updateModel(request: UpdateModelRequest): Promise<ModelView> {
    const { loaded, revision } = this.#describe();
    if (request.expectedRevision && request.expectedRevision !== revision)
      throw refuse("invalid-request", "error.modelChanged", {});
    try {
      const next = updateWorkspaceModel({
        root: this.root,
        modelPath: loaded.modelPath,
        request,
        parseYaml: this.#deps.parseYaml,
      });
      this.#workspace = { loaded: next, signature: this.#modelSignature(next.modelPath) };
      this.#agentChecks = null;
      const model = await this.model();
      this.#hooks.broadcast({ type: "model" });
      return model;
    } catch (error) {
      this.#workspace = null;
      if (error instanceof ModelRevisionError)
        throw refuse("invalid-request", "error.modelChanged", {});
      if (error instanceof ModelError)
        throw refuse("no-model", "error.model", { detail: error.message }, error.files);
      throw error;
    }
  }

  async designCapabilities(): Promise<DesignCapabilitiesResponse> {
    const loaded = this.#loaded();
    const specs = resolveAgents(loaded.config.agents);
    const agents = await this.#checkAgents(specs);
    const probe = await probeMcpServer(this.root).catch(() => null);
    return {
      ok: true,
      workspace: this.root,
      desktop: {
        supported: process.platform === "darwin",
        reason:
          process.platform === "darwin"
            ? null
            : "Desktop design handoff is currently supported on macOS.",
        tools: {
          claim: "claim_design",
          context: "get_design_context",
          questions: "submit_design_questions",
          proposal: "submit_design_proposal",
          available: probe?.designTools ?? false,
        },
      },
      sources: designSources(),
      agents: designAgentCapabilities(this.root, specs, agents, (spec) => {
        if (spec.format !== "claude" && spec.format !== "codex")
          return { available: false, reason: "This provider has no desktop design path." };
        if (!desktopProviderInstalled(spec.format))
          return {
            available: false,
            reason:
              "The desktop application is not installed or does not expose the expected URL scheme.",
          };
        const server = mcpServerForWorkspace(this.root);
        const config =
          spec.format === "claude"
            ? claudeProjectConfig(this.root, server)
            : codexProjectConfig(this.root, server);
        if (config.status !== "usable")
          return {
            available: false,
            reason: config.reason ?? "Install the ALPS project MCP config.",
          };
        if (!probe?.designTools)
          return {
            available: false,
            reason: probe?.error ?? "ALPS design MCP tools are not available.",
          };
        return { available: true, reason: null };
      }),
    };
  }

  #designSession(id: string): DesignSession {
    const session = readDesign(this.root, id);
    if (!session) throw refuse("not-found", "error.noDesign", { id });
    return session;
  }

  async #designDesktopReady(
    spec: AgentSpec,
  ): Promise<{ available: boolean; reason: string | null }> {
    if (spec.format !== "claude" && spec.format !== "codex")
      return { available: false, reason: "This provider has no desktop design path." };
    if (!desktopProviderInstalled(spec.format))
      return {
        available: false,
        reason:
          "The desktop application is not installed or does not expose the expected URL scheme.",
      };
    const server = mcpServerForWorkspace(this.root);
    const config =
      spec.format === "claude"
        ? claudeProjectConfig(this.root, server)
        : codexProjectConfig(this.root, server);
    if (config.status !== "usable")
      return { available: false, reason: config.reason ?? "Install the ALPS project MCP config." };
    const probe = await probeMcpServer(this.root);
    if (!probe.designTools)
      return {
        available: false,
        reason: probe.error ?? "ALPS design MCP tools are not available.",
      };
    return { available: true, reason: null };
  }

  #designProviderMatches(session: DesignSession, caller: Extract<Caller, { kind: "agent" }>): void {
    const spec = resolveAgents(this.#loaded().config.agents).find(
      (item) => item.id === session.agent,
    );
    const expected = spec?.format === "codex" ? /codex|chatgpt/i : /claude/i;
    if (!expected.test(caller.client.name))
      throw refuse("invalid-request", "error.designClient", {
        agent: spec?.label ?? session.agent,
      });
  }

  #trustedConversationUrl(format: AgentSpec["format"], url: string): string {
    let parsed: URL;
    try {
      parsed = new URL(url);
    } catch (error) {
      throw refuse("invalid-request", "error.designReference", {
        path: "conversationUrl",
        reason: (error as Error).message,
      });
    }
    const ok =
      format === "codex"
        ? parsed.protocol === "codex:" &&
          parsed.hostname === "threads" &&
          /^\/[A-Za-z0-9_-]+$/.test(parsed.pathname) &&
          parsed.pathname !== "/new" &&
          !parsed.search &&
          !parsed.hash
        : format === "claude"
          ? parsed.protocol === "claude:" &&
            !parsed.search &&
            !parsed.hash &&
            ((parsed.hostname === "code" &&
              /^\/[A-Za-z0-9_-]+$/.test(parsed.pathname) &&
              parsed.pathname !== "/new") ||
              (parsed.hostname === "claude.ai" && /^\/chat\/[A-Za-z0-9_-]+$/.test(parsed.pathname)))
          : false;
    if (!ok)
      throw refuse("invalid-request", "error.designReference", {
        path: "conversationUrl",
        reason: "The conversation URL is not a supported desktop provider link.",
      });
    return url;
  }

  #conversationUrlForProvider(format: AgentSpec["format"], sessionId?: string): string | null {
    if (format !== "codex" || !sessionId) return null;
    return `codex://threads/${encodeURIComponent(sessionId)}`;
  }

  #designPrompt(session: DesignSession): string {
    return [
      `Build the ALPS Process Model and its usable Skills in this project: ${this.root}`,
      `First check your actual working directory (pwd), then call claim_design with id ${session.id} and workspace set to the observed absolute directory. If it does not match this project, stop and explain the mismatch. Include the host-provided sessionId if available; never invent it.`,
      session.autoSave
        ? "The user requested construction: submit complete model and Skill file contents through submit_design_proposal. ALPS saves the validated bundle automatically, with no separate Apply step. Continue corrections in this same conversation."
        : "Submit complete model and Skill file contents through submit_design_proposal for review.",
      "Ask only necessary clarification. Do not execute business processes or use claim_launch, wake, run, assess, or finish_run. Check the returned save status before reporting completion.",
      "",
      "Request:",
      session.request,
    ].join("\n");
  }

  #designContextPrompt(session: DesignSession): string {
    const { loaded, revision } = this.#describe();
    if (revision !== session.expectedRevision)
      throw refuse("invalid-request", "error.modelChanged", {});
    const draftProposal = session.status === "applied" ? null : session.proposal;
    try {
      validateDesignInputs(this.root, session.references, session.sources);
      return buildDesignPrompt({
        delivery: "desktop",
        autoSave: session.autoSave === true,
        skillBaseline: session.skillBaseline ?? {},
        language: loaded.language,
        request: session.request,
        process: session.process,
        model: draftProposal?.model ?? modelWriteFromWorkspace(loaded, session.expectedRevision),
        modelMeaning: loaded.model,
        draftProposal,
        references: session.references,
        sources: session.sources,
        messages: session.messages
          .map((message) => ({ role: message.role, text: message.text }))
          .filter(
            (message): message is { role: "user" | "agent"; text: string } =>
              message.role === "user" || message.role === "agent",
          ),
        root: this.root,
      });
    } catch (error) {
      if (error instanceof HarnessError) throw error;
      throw refuse("invalid-request", "error.designReference", {
        path: "references",
        reason: (error as Error).message,
      });
    }
  }

  #assertDesignAgent(
    session: DesignSession,
    caller: Caller,
    claiming = false,
  ): Extract<Caller, { kind: "agent" }> {
    if (caller.kind !== "agent" || !caller.session)
      throw refuse("invalid-request", "error.externalSession", {});
    if (session.method !== "desktop") throw refuse("invalid-request", "error.designMethod", {});
    this.#designProviderMatches(session, caller);
    if (session.status === "canceled" || session.status === "failed")
      throw refuse("invalid-request", "error.designEnded", {
        id: session.id,
        status: session.status,
      });
    const bound = session.desktop?.mcpSession;
    if (!bound && !claiming) throw refuse("invalid-request", "error.externalSession", {});
    if (bound && bound !== caller.session)
      throw refuse("already-running", "error.externalConnected", {});
    return caller;
  }

  #designDedupeKey(request: CreateDesignRequest): string {
    return JSON.stringify({
      request: request.request,
      method: request.method,
      process: request.process ?? null,
      references: [...request.references],
      agent: request.agent ?? null,
      model: request.model ?? null,
      effort: request.effort ?? null,
      autoSave: request.autoSave ?? true,
      ...(request.workIds?.length ? { workIds: [...new Set(request.workIds)].sort() } : {}),
    });
  }

  async createDesign(request: CreateDesignRequest): Promise<DesignResponse> {
    if (this.#closing) throw refuse("server-unreachable", "error.stopping", {});
    const id = request.id ?? newDesignId();
    const key = this.#designDedupeKey(request);
    const pending = this.#pendingDesigns.get(id);
    if (pending) {
      if (pending.key !== key) throw refuse("invalid-request", "error.launchChanged", {});
      return pending.promise;
    }
    const known = readDesign(this.root, id);
    if (known) {
      if (
        (known.dedupeKey ??
          this.#designDedupeKey({
            id: known.id,
            request: known.request,
            method: known.method,
            process: known.process ?? undefined,
            references: known.references.map((reference) => reference.path),
            agent: known.agent,
            model: known.selection?.model,
            effort: known.selection?.effort,
            autoSave: known.autoSave ?? false,
            workIds: known.workIds,
          })) === key
      )
        return { ok: true, design: known };
      throw refuse("invalid-request", "error.launchChanged", {});
    }
    let promise!: Promise<DesignResponse>;
    promise = this.#createDesignNow(id, key, request).finally(() => {
      const latest = this.#pendingDesigns.get(id);
      if (latest?.promise === promise) this.#pendingDesigns.delete(id);
    });
    this.#pendingDesigns.set(id, { key, promise });
    return promise;
  }

  async #createDesignNow(
    id: string,
    dedupeKey: string,
    request: CreateDesignRequest,
  ): Promise<DesignResponse> {
    const sources = designSources();
    if (sources.some((source) => !source.available))
      throw refuse("invalid-request", "error.designSources", {});
    let references;
    try {
      references = readDesignReferences(this.root, request.references);
      validateDesignInputs(this.root, references, sources);
    } catch (error) {
      throw refuse("invalid-request", "error.designReference", {
        path: "references",
        reason: (error as Error).message,
      });
    }
    const { loaded, revision } = this.#describe();
    if (request.process) this.#process(loaded.model, request.process);
    const specs = resolveAgents(loaded.config.agents);
    const infos = request.method === "cli" ? await this.#checkAgents(specs) : [];
    const capable = specs.filter((spec) => {
      const info = infos.find((agent) => agent.id === spec.id);
      return Boolean(
        (spec.format === "claude" || spec.format === "codex") &&
        (request.method === "desktop" || (info?.available && spec.command)),
      );
    });
    const name =
      request.agent ??
      capable.find((spec) => spec.id === "claude-code")?.id ??
      capable.find((spec) => spec.id === "codex")?.id ??
      "claude-code";
    const spec = specs.find((item) => item.id === name);
    if (
      !spec ||
      (spec.format !== "claude" && spec.format !== "codex") ||
      (request.method === "cli" && !spec.command)
    )
      throw refuse("agent-unavailable", "error.designAgent", {
        agents: capable.map((agent) => agent.id).join(", "),
      });
    if (request.method === "cli") {
      const info = await this.#availability(spec, specs);
      if (!info.available)
        throw refuse("agent-unavailable", "error.agentUnavailable", {
          agent: spec.label,
          reason: info.reason ?? "it is not available",
        });
    }
    const selection = {
      ...(request.model ? { model: request.model } : {}),
      ...(request.effort ? { effort: request.effort } : {}),
    };
    if (request.method === "desktop" && (request.model || request.effort))
      throw refuse("invalid-request", "error.launchModel", {});
    if (request.method === "desktop") {
      const desktop = await this.#designDesktopReady(spec);
      if (!desktop.available) throw refuse("agent-unavailable", "error.desktopUnavailable", {});
    }
    if (request.method === "cli") await this.#validateSelection(spec, selection);
    const safeSpec = request.method === "cli" ? safeDesignSpec(spec, selection) : null;
    if (request.method === "cli" && !safeSpec)
      throw refuse("agent-unavailable", "error.designAgent", {
        agents: capable.map((agent) => agent.id).join(", "),
      });
    const skillBaseline = snapshotDesignSkills(this.root, loaded);
    let prompt: string;
    try {
      prompt = buildDesignPrompt({
        autoSave: request.autoSave ?? true,
        skillBaseline,
        language: loaded.language,
        request: request.request,
        process: request.process ?? null,
        model: modelWriteFromWorkspace(loaded, revision),
        modelMeaning: loaded.model,
        draftProposal: null,
        references,
        sources,
        messages: [],
        root: this.root,
      });
    } catch (error) {
      throw refuse("invalid-request", "error.designReference", {
        path: "references",
        reason: (error as Error).message,
      });
    }
    const now = Date.now();
    const session: DesignSession = {
      id,
      provider: spec.format,
      ...(request.workIds?.length ? { workIds: [...new Set(request.workIds)] } : {}),
      status: request.method === "cli" ? "running" : "pending",
      createdAt: now,
      updatedAt: now,
      request: request.request,
      dedupeKey,
      process: request.process ?? null,
      method: request.method,
      autoSave: request.autoSave ?? true,
      skillBaseline,
      references,
      agent: spec.id,
      ...(request.model || request.effort ? { selection } : {}),
      expectedRevision: revision,
      messages: [],
      proposal: null,
      error: null,
      command: null,
      sources,
    };
    if (request.method === "desktop")
      session.desktop = { provider: spec.format, prompt: this.#designPrompt(session) };
    writeDesign(this.root, session);
    if (request.method === "desktop") return this.openDesign(id, {});
    if (request.method === "cli" && safeSpec) this.#startDesignAgent(session, safeSpec, prompt);
    return { ok: true, design: this.#designSession(id) };
  }

  #stopDesign(id: string): void {
    const active = this.#activeDesigns.get(id);
    if (!active) return;
    active.agent.stop();
    if (active.timer) clearTimeout(active.timer);
    active.release();
    this.#activeDesigns.delete(id);
    fs.rmSync(active.cwd, { recursive: true, force: true });
  }

  #startDesignAgent(session: DesignSession, spec: AgentSpec, prompt: string): void {
    const cwd = isolatedCwd();
    const args = argsFor(spec, prompt);
    const next = {
      ...session,
      command: designCommand(spec, prompt),
      updatedAt: Date.now(),
    };
    writeDesign(this.root, next);
    const stdout: string[] = [];
    const stderr: string[] = [];
    let outputBytes = 0;
    let outputError: string | null = null;
    let handle: AgentHandle | null = null;
    const appendOutput = (target: string[], line: string): void => {
      if (outputError) return;
      outputBytes += Buffer.byteLength(line) + 1;
      if (outputBytes > MAX_DESIGN_OUTPUT_BYTES) {
        outputError = "The design agent returned too much output.";
        try {
          handle?.stop();
        } catch {
          // The process may already be stopping.
        }
        return;
      }
      target.push(line);
    };
    const release = this.#hooks.hold();
    try {
      handle = this.#deps.startAgent(
        {
          command: spec.command ?? "",
          args,
          cwd,
          unset: envLeftOut(spec),
          env: { ...spec.env, ALPS_DESIGN_ID: session.id, ALPS_WORKSPACE: this.root },
          stdin: spec.stdin ? prompt : null,
        },
        {
          stdout: (line) => appendOutput(stdout, line),
          stderr: (line) => appendOutput(stderr, line),
        },
      );
    } catch (error) {
      release();
      fs.rmSync(cwd, { recursive: true, force: true });
      writeDesign(this.root, {
        ...next,
        status: "failed",
        updatedAt: Date.now(),
        error: (error as Error).message,
      });
      return;
    }
    const runningHandle = handle;
    const active: ActiveDesign = {
      release,
      agent: runningHandle,
      cwd,
      timer: setTimeout(() => {
        outputError = outputError ?? "The design agent timed out.";
        runningHandle.stop();
      }, DESIGN_AGENT_TIMEOUT_MS),
    };
    this.#activeDesigns.set(session.id, active);
    const finish = async (): Promise<void> => {
      let ended: { exitCode: number | null; signal: string | null } | null = null;
      let rejected: Error | null = null;
      try {
        ended = await runningHandle.done;
      } catch (error) {
        rejected = error as Error;
      }
      if (this.#activeDesigns.get(session.id) !== active) return;
      this.#activeDesigns.delete(session.id);
      if (active.timer) clearTimeout(active.timer);
      active.release();
      fs.rmSync(active.cwd, { recursive: true, force: true });
      const current = readDesign(this.root, session.id) ?? next;
      if (current.status !== "running") return;
      const endError =
        outputError ??
        rejected?.message ??
        (ended && (ended.exitCode !== 0 || ended.signal)
          ? `The design agent exited before returning a usable proposal (exit=${
              ended.exitCode ?? ended.signal ?? "unknown"
            }).`
          : null);
      if (endError) {
        const detail = [endError, stderr.slice(-8).join("\n")].filter(Boolean).join("\n");
        writeDesign(this.root, {
          ...current,
          status: "failed",
          updatedAt: Date.now(),
          messages: [
            ...current.messages,
            { role: "system", text: detail.slice(0, 4000), at: Date.now() },
          ],
          error: detail.slice(0, 4000),
        });
        return;
      }
      try {
        const parsed = parseDesignOutput(spec.format, stdout, current.expectedRevision);
        const text =
          parsed.message ||
          parsed.questions.join("\n") ||
          parsed.proposal?.summary ||
          "The design agent returned a proposal.";
        const proposal = parsed.proposal
          ? proposalWithRevision(parsed.proposal, current.expectedRevision)
          : current.proposal;
        const ready: DesignSession = {
          ...current,
          status: parsed.proposal ? "ready" : "needs-input",
          updatedAt: Date.now(),
          messages: [...current.messages, { role: "agent", text, at: Date.now() }],
          proposal,
          error: null,
        };
        writeDesign(this.root, ready);
        if (parsed.proposal && proposal && ready.autoSave === true)
          await this.#autoApplyDesign(ready, proposal);
      } catch (error) {
        const detail = [(error as Error).message, stderr.slice(-8).join("\n")]
          .filter(Boolean)
          .join("\n");
        writeDesign(this.root, {
          ...current,
          status: "failed",
          updatedAt: Date.now(),
          messages: [
            ...current.messages,
            { role: "system", text: detail.slice(0, 4000), at: Date.now() },
          ],
          error: detail.slice(0, 4000),
        });
      }
    };
    void finish();
  }

  async design(id: string): Promise<DesignResponse> {
    return { ok: true, design: this.#designSession(id) };
  }

  workObjects(
    launches: readonly import("../shared/types.ts").LaunchRecord[],
  ): import("../shared/types.ts").WorkObjectsResponse {
    const { description } = this.#describe();
    const directory = path.join(recordPaths(this.root).dir, "designs");
    const files = fs.existsSync(directory) ? fs.readdirSync(directory) : [];
    const sourceDesigns = files
      .filter((file) => /^[A-Za-z0-9_-]{8,80}\.json$/.test(file))
      .map((file) => ({ id: file.slice(0, -5), design: readDesign(this.root, file.slice(0, -5)) }));
    const designs = sourceDesigns.flatMap((source) => (source.design ? [source.design] : []));
    return buildWorkObjects({
      runs: [...this.#records.runs.values()],
      instances: Object.values(this.#state.instances).map((instance) =>
        this.#view(instance, description),
      ),
      designs,
      launches,
      processes: description.processes,
      unreadableRecords: [...this.#records.unreadable, ...this.#records.unreadableAssessments]
        .map((item) => item.id)
        .concat(
          sourceDesigns.filter((source) => !source.design).map((source) => `design-${source.id}`),
        ),
    });
  }

  /** Authoring sessions remain separate from business runs and assessment records. */
  designs(offset = 0): import("../shared/types.ts").DesignsResponse {
    const directory = path.join(recordPaths(this.root).dir, "designs");
    const entries = fs.existsSync(directory) ? fs.readdirSync(directory) : [];
    const sessions = entries
      .filter((file) => /^[A-Za-z0-9_-]{8,80}\.json$/.test(file))
      .map((file) => readDesign(this.root, file.slice(0, -5)))
      .filter((session): session is DesignSession => session !== null)
      .sort((a, b) => b.createdAt - a.createdAt || a.id.localeCompare(b.id));
    const designs = sessions.slice(offset, offset + 30).map((session) => {
      const { id, status, createdAt, updatedAt, request, process, method, agent, appliedAt } =
        session;
      return { id, status, createdAt, updatedAt, request, process, method, agent, appliedAt };
    });
    return { ok: true, designs, next: offset + 30 < sessions.length ? offset + 30 : null };
  }

  async openDesign(id: string, _request: DesignOpenRequest): Promise<DesignResponse> {
    const session = this.#designSession(id);
    if (session.method !== "desktop" || !session.desktop)
      throw refuse("invalid-request", "error.designMethod", {});
    if (
      session.status !== "pending" &&
      session.status !== "connected" &&
      session.status !== "needs-input" &&
      session.status !== "ready" &&
      session.status !== "applied"
    )
      throw refuse("invalid-request", "error.designEnded", { id, status: session.status });
    const spec = resolveAgents(this.#loaded().config.agents).find(
      (item) => item.id === session.agent,
    );
    if (!spec || (spec.format !== "claude" && spec.format !== "codex"))
      throw refuse("agent-unavailable", "error.designAgent", { agents: session.agent });
    const prompt = this.#designPrompt(session);
    const conversationUrl = this.#conversationUrlForProvider(
      spec.format,
      session.desktop.sessionId,
    );
    const targetUrl =
      conversationUrl ??
      (session.desktop.connectedAt
        ? undefined
        : spec.format === "codex"
          ? `codex://new?${new URLSearchParams({ path: fs.realpathSync(this.root), prompt })}`
          : `claude://code/new?${new URLSearchParams({ folder: fs.realpathSync(this.root), q: prompt })}`);
    const openArgs = desktopProviderOpenArgs(spec.format, targetUrl);
    let opened = false;
    try {
      if (openArgs) {
        const child = Bun.spawn(["/usr/bin/open", ...openArgs], {
          stdin: "ignore",
          stdout: "ignore",
          stderr: "ignore",
        });
        opened = (await child.exited) === 0;
      }
    } catch {
      opened = false;
    }
    const openedAt = Date.now();
    const next: DesignSession = {
      ...session,
      updatedAt: openedAt,
      desktop: {
        ...session.desktop,
        prompt,
        ...(opened ? { openedAt } : {}),
      },
    };
    writeDesign(this.root, next);
    return { ok: true, design: next, prompt, opened };
  }

  async claimDesign(
    id: string,
    request: DesignClaimRequest,
    caller: Caller,
  ): Promise<DesignResponse> {
    const session = this.#designSession(id);
    const agent = this.#assertDesignAgent(session, caller, true);
    if (agent.wake || agent.assess || this.externalRunFor(agent.session!))
      throw refuse("invalid-request", "error.designMethod", {});
    if (!session.desktop) throw refuse("invalid-request", "error.designMethod", {});
    const provider = session.desktop.provider;
    if (!provider) throw refuse("invalid-request", "error.designMethod", {});
    if (request.conversationUrl) this.#trustedConversationUrl(provider, request.conversationUrl);
    const conversationUrl = this.#conversationUrlForProvider(provider, request.sessionId);
    let workspace: string | undefined;
    if (request.workspace) {
      try {
        if (!path.isAbsolute(request.workspace)) throw new Error("Relative workspace");
        workspace = fs.realpathSync(request.workspace);
        if (workspace !== fs.realpathSync(this.root)) throw new Error("Workspace mismatch");
      } catch {
        throw refuse("invalid-request", "error.designWorkspace", { workspace: this.root });
      }
    } else if (session.autoSave) {
      throw refuse("invalid-request", "error.designWorkspace", { workspace: this.root });
    }
    const next: DesignSession = {
      ...session,
      status: session.status === "pending" ? "connected" : session.status,
      updatedAt: Date.now(),
      desktop: {
        ...session.desktop,
        connectedAt: session.desktop.connectedAt ?? Date.now(),
        mcpSession: agent.session ?? undefined,
        client: agent.client,
        ...(workspace ? { workspace, workspaceConfirmedAt: Date.now() } : {}),
        ...(request.sessionId ? { sessionId: request.sessionId } : {}),
        ...(conversationUrl ? { conversationUrl } : {}),
      },
    };
    const prompt = this.#designContextPrompt(next);
    writeDesign(this.root, next);
    return { ok: true, design: next, prompt };
  }

  async designContext(id: string, caller: Caller): Promise<DesignResponse> {
    const session = this.#designSession(id);
    this.#assertDesignAgent(session, caller);
    return { ok: true, design: session, prompt: this.#designContextPrompt(session) };
  }

  async submitDesignQuestions(
    id: string,
    request: DesignSubmitQuestionsRequest,
    caller: Caller,
  ): Promise<DesignResponse> {
    const session = this.#designSession(id);
    this.#assertDesignAgent(session, caller);
    if (
      session.status !== "pending" &&
      session.status !== "connected" &&
      session.status !== "needs-input" &&
      session.status !== "ready" &&
      session.status !== "applied"
    )
      throw refuse("invalid-request", "error.designEnded", { id, status: session.status });
    const text = request.questions?.length
      ? `${request.message}\n\n${request.questions.map((question) => `- ${question}`).join("\n")}`
      : request.message;
    const next: DesignSession = {
      ...session,
      status: "needs-input",
      updatedAt: Date.now(),
      messages: [...session.messages, { role: "agent", text, at: Date.now() }],
      error: null,
    };
    writeDesign(this.root, next);
    return { ok: true, design: next, prompt: next.desktop?.prompt };
  }

  async submitDesignProposal(
    id: string,
    request: DesignSubmitProposalRequest,
    caller: Caller,
  ): Promise<DesignResponse> {
    const session = this.#designSession(id);
    this.#assertDesignAgent(session, caller);
    if (
      session.status !== "pending" &&
      session.status !== "connected" &&
      session.status !== "needs-input" &&
      session.status !== "ready" &&
      session.status !== "applied"
    )
      throw refuse("invalid-request", "error.designEnded", { id, status: session.status });
    const { revision } = this.#describe();
    if (revision !== session.expectedRevision)
      throw refuse("invalid-request", "error.modelChanged", {});
    try {
      validateDesignInputs(this.root, session.references, session.sources);
    } catch (error) {
      throw refuse("invalid-request", "error.designReference", {
        path: "references",
        reason: (error as Error).message,
      });
    }
    const proposal = proposalWithRevision(request.proposal, session.expectedRevision);
    const next: DesignSession = {
      ...session,
      status: "ready",
      updatedAt: Date.now(),
      messages: [
        ...session.messages,
        { role: "agent", text: request.message ?? proposal.summary, at: Date.now() },
      ],
      proposal,
      error: null,
    };
    writeDesign(this.root, next);
    if (next.autoSave === true) return this.#autoApplyDesign(next, proposal);
    return { ok: true, design: next, prompt: next.desktop?.prompt };
  }

  async messageDesign(id: string, request: DesignMessageRequest): Promise<DesignResponse> {
    if (this.#closing) throw refuse("server-unreachable", "error.stopping", {});
    const session = this.#designSession(id);
    if (session.method !== "cli") throw refuse("invalid-request", "error.designMethod", {});
    if (session.status === "canceled")
      throw refuse("invalid-request", "error.designEnded", { id, status: session.status });
    if (session.status === "running")
      throw refuse("already-running", "error.designRunning", { id });
    let draftProposal =
      request.proposal ?? (session.status === "applied" ? null : session.proposal);
    if (draftProposal)
      draftProposal = proposalWithRevision(draftProposal, session.expectedRevision);
    let prompt: string;
    const { loaded, revision } = this.#describe();
    if (revision !== session.expectedRevision)
      throw refuse("invalid-request", "error.modelChanged", {});
    try {
      validateDesignInputs(this.root, session.references, session.sources);
      prompt = buildDesignPrompt({
        autoSave: session.autoSave === true,
        skillBaseline: session.skillBaseline ?? {},
        language: loaded.language,
        request: session.request,
        process: session.process,
        model: draftProposal?.model ?? modelWriteFromWorkspace(loaded, session.expectedRevision),
        modelMeaning: loaded.model,
        draftProposal,
        references: session.references,
        sources: session.sources,
        messages: [
          ...session.messages,
          { role: "user" as const, text: request.text, at: Date.now() },
        ]
          .map((message) => ({ role: message.role, text: message.text }))
          .filter(
            (message): message is { role: "user" | "agent"; text: string } =>
              message.role === "user" || message.role === "agent",
          ),
        root: this.root,
      });
    } catch (error) {
      throw refuse("invalid-request", "error.designReference", {
        path: "references",
        reason: (error as Error).message,
      });
    }
    const specs = resolveAgents(loaded.config.agents);
    const spec = specs.find((item) => item.id === session.agent);
    const safeSpec = spec && spec.command ? safeDesignSpec(spec, session.selection ?? {}) : null;
    if (!safeSpec)
      throw refuse("agent-unavailable", "error.designAgent", {
        agents: specs
          .filter((item) => item.command && (item.format === "claude" || item.format === "codex"))
          .map((item) => item.id)
          .join(", "),
      });
    const messages = [
      ...session.messages,
      { role: "user" as const, text: request.text, at: Date.now() },
    ];
    const next: DesignSession = {
      ...session,
      status: "running",
      updatedAt: Date.now(),
      messages,
      proposal: draftProposal ?? session.proposal,
      error: null,
    };
    writeDesign(this.root, next);
    this.#startDesignAgent(next, safeSpec, prompt);
    return { ok: true, design: this.#designSession(id) };
  }

  async cancelDesign(id: string): Promise<DesignResponse> {
    const session = this.#designSession(id);
    if (session.status === "running") this.#stopDesign(id);
    const next: DesignSession = {
      ...session,
      status: "canceled",
      updatedAt: Date.now(),
      error: null,
    };
    writeDesign(this.root, next);
    return { ok: true, design: next };
  }

  async #saveDesignBundle(
    session: DesignSession,
    proposal: DesignProposal,
    mode: "full" | "skills-only",
  ): Promise<{ model?: ModelView; savedFiles: string[]; appliedRevision: string }> {
    const { loaded, revision } = this.#describe();
    try {
      validateDesignInputs(this.root, session.references, session.sources);
    } catch (error) {
      throw refuse("invalid-request", "error.designReference", {
        path: "references",
        reason: (error as Error).message,
      });
    }
    if (mode === "full") {
      try {
        const saved = saveDesignBundle({
          root: this.root,
          loaded,
          request: updateModelRequest.parse(proposal.model),
          skillFiles: proposal.skillFiles ?? [],
          skillBaseline: session.skillBaseline ?? {},
          parseYaml: this.#deps.parseYaml,
        });
        this.#workspace = {
          loaded: saved.loaded,
          signature: this.#modelSignature(saved.loaded.modelPath),
        };
        this.#agentChecks = null;
        const model = await this.model();
        this.#hooks.broadcast({ type: "model" });
        return { model, savedFiles: saved.savedFiles, appliedRevision: model.revision };
      } catch (error) {
        this.#workspace = null;
        if (error instanceof ModelRevisionError)
          throw refuse("invalid-request", "error.modelChanged", {});
        if (error instanceof ModelError)
          throw refuse("no-model", "error.model", { detail: error.message }, error.files);
        throw refuse("invalid-request", "error.designReference", {
          path: "skillFiles",
          reason: (error as Error).message,
        });
      }
    }
    try {
      const saved = saveMissingDesignSkills({
        root: this.root,
        loaded,
        request: updateModelRequest.parse(proposal.model),
        skillFiles: proposal.skillFiles ?? [],
        parseYaml: this.#deps.parseYaml,
      });
      const model = await this.model();
      this.#hooks.broadcast({ type: "model" });
      return { model, savedFiles: saved.savedFiles, appliedRevision: revision };
    } catch (error) {
      if (error instanceof ModelError)
        throw refuse("no-model", "error.model", { detail: error.message }, error.files);
      throw refuse("invalid-request", "error.designReference", {
        path: "skillFiles",
        reason: (error as Error).message,
      });
    }
  }

  async #applyDesignProposal(
    session: DesignSession,
    proposal: DesignProposal,
    mode: "full" | "skills-only" = "full",
  ): Promise<DesignResponse> {
    const saved = await this.#saveDesignBundle(session, proposal, mode);
    const now = Date.now();
    let skillBaseline = session.skillBaseline;
    try {
      skillBaseline = snapshotDesignSkills(this.root, this.#loaded());
    } catch {
      // Keep the previous baseline; the next operation will surface the model error.
    }
    const next: DesignSession = {
      ...session,
      status: "applied",
      updatedAt: now,
      appliedAt: session.appliedAt ?? now,
      expectedRevision: saved.appliedRevision,
      skillBaseline,
      proposal: proposalWithRevision(proposal, saved.appliedRevision),
      savedFiles: saved.savedFiles,
      appliedRevision: saved.appliedRevision,
      error: null,
    };
    writeDesign(this.root, next);
    return { ok: true, design: next, ...(saved.model ? { model: saved.model } : {}) };
  }

  async #autoApplyDesign(
    session: DesignSession,
    proposal: DesignProposal,
  ): Promise<DesignResponse> {
    try {
      return await this.#applyDesignProposal(session, proposal);
    } catch (error) {
      const detail = error instanceof HarnessError ? error.message : (error as Error).message;
      const next: DesignSession = {
        ...session,
        status: "ready",
        updatedAt: Date.now(),
        proposal,
        error: detail,
      };
      writeDesign(this.root, next);
      return { ok: true, design: next, prompt: next.desktop?.prompt };
    }
  }

  async applyDesign(id: string, request: DesignApplyRequest): Promise<DesignResponse> {
    const session = this.#designSession(id);
    if (session.status === "applied") {
      if (session.savedFiles !== undefined) return { ok: true, design: session };
      const repairProposal = request.proposal ?? session.proposal;
      if (!repairProposal) return { ok: true, design: session };
      return this.#applyDesignProposal(
        session,
        proposalWithRevision(repairProposal, session.expectedRevision),
        "skills-only",
      );
    }
    if (session.status === "running")
      throw refuse("already-running", "error.designRunning", { id });
    if (session.status !== "ready") throw refuse("invalid-request", "error.designNotReady", { id });
    const proposal = request.proposal ?? session.proposal;
    if (!proposal) throw refuse("invalid-request", "error.designNotReady", { id });
    const nextProposal = proposalWithRevision(proposal, session.expectedRevision);
    return this.#applyDesignProposal(session, nextProposal);
  }

  /** Metadata only; a short cache coalesces concurrent requests, and refresh bypasses completed entries. */
  async agentModels(agent: string, refresh = false): Promise<AgentModelsResponse> {
    const specs = resolveAgents(this.#loaded().config.agents);
    const spec = specs.find((s) => s.id === agent);
    if (!spec)
      throw refuse("agent-unavailable", "error.noAgent", {
        agent,
        agents: specs.map((s) => s.id).join(", "),
      });
    if (!takesMcpServer(spec))
      return { ok: true, agent, supported: false, models: [], fetchedAt: Date.now() };
    const key = JSON.stringify(spec);
    const known = this.#agentCatalogs.get(key);
    if (known && (known.pending || (!refresh && Date.now() - known.at < 60_000)))
      return known.result;
    // Expired configurations need no retained catalog; switching agents can reuse fresh results.
    for (const [other, entry] of this.#agentCatalogs)
      if (!entry.pending && Date.now() - entry.at >= 60_000) this.#agentCatalogs.delete(other);
    const entry = {
      at: Date.now(),
      pending: true,
      result: Promise.resolve(null as unknown as AgentModelsResponse),
    };
    entry.result = this.#deps
      .readAgentModels(spec, this.root)
      .then((models) => {
        if (models.length === 0) throw new Error("The agent returned an empty model catalog.");
        entry.at = Date.now();
        return { ok: true as const, agent, supported: true, models, fetchedAt: entry.at };
      })
      .catch((error: unknown) => {
        this.#agentCatalogs.delete(key);
        throw refuse("agent-unavailable", "error.agentModels", {
          agent: spec.label,
          detail: error instanceof Error ? error.message : String(error),
        });
      })
      .finally(() => {
        entry.pending = false;
      });
    this.#agentCatalogs.set(key, entry);
    return entry.result;
  }

  async #validateSelection(spec: AgentSpec, selection: AgentSelection): Promise<void> {
    if (!selection.model && !selection.effort) return;
    const invalid = (detail: string): never => {
      throw refuse("invalid-request", "error.agentSelection", { agent: spec.label, detail });
    };
    if (!takesMcpServer(spec)) invalid("This agent does not support model selection.");
    if (!selection.model) invalid("Choose a model before choosing its effort.");
    const catalog = await this.agentModels(spec.id);
    const model = catalog.models.find((m) => m.id === selection.model);
    if (!model)
      invalid(
        `Model ${selection.model} is not in the agent's current catalog. Refresh the model list.`,
      );
    if (selection.effort && !model!.efforts.includes(selection.effort))
      invalid(`Effort ${selection.effort} is not supported by ${selection.model}.`);
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
    if (definitionChanged(instance, description)) reasons.push({ kind: "definition", path: null });
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
    return {
      ...instance,
      facts: this.#facts(instance, description),
      evaluationContext: evaluationContext(instance, description),
      evaluationBasis: evaluationBasis(instance, description),
    };
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
    this.#refuseAssessing(caller);
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

  /**
   * `GET /api/runs` (`list_runs`): runs, newest first, a page at a time, each its summary with its
   * Process, agent, and cost; with a Process (id or name), an agent, a status, a kind, or the runs
   * that started at or after `since`.
   */
  runs(query: {
    process?: string;
    agent?: string;
    status?: RunStatus;
    kind?: RunKind;
    since?: number;
    limit: number;
    cursor?: string;
  }): { runs: ListedRun[]; next: string | null } {
    const process =
      query.process === undefined
        ? undefined
        : this.#process(this.#loaded().model, query.process).id;
    const before = query.cursor === undefined ? Number.POSITIVE_INFINITY : Number(query.cursor);
    const listed = (summary: RunSummary): ListedRun => {
      const record = this.#records.runs.get(summary.id);
      return {
        ...summary,
        process: record?.process ?? null,
        agent: record?.agent ?? null,
        costUsd: record?.usage?.costUsd ?? null,
      };
    };
    const matching = Object.values(this.#state.runs)
      .filter(
        (run) =>
          seqOf(run.id) < before &&
          (query.kind === undefined || run.kind === query.kind) &&
          (query.status === undefined || run.status === query.status) &&
          (query.since === undefined || run.startedAt >= query.since),
      )
      .map(listed)
      .filter(
        (run) =>
          (process === undefined || run.process === process) &&
          (query.agent === undefined || run.agent === query.agent),
      )
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
    execution: RunExecution = { method: "cli" },
    instruction?: string,
  ): Promise<{ run: RunView; prompt?: string }> {
    if (this.#closing) throw refuse("server-unreachable", "error.stopping", {});
    this.#refusePlanOnly(caller);
    this.#refuseAssessing(caller);
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
      if (execution.method === "cli" && startsProcess(spec)) {
        info = await this.#availability(spec, specs);
        if (!info.available)
          throw refuse("agent-unavailable", "error.agentUnavailable", {
            agent: spec.label,
            reason: info.reason ?? "it is not available",
          });
      }
    }
    if (execution.method === "cli")
      await this.#validateSelection(agentSpec(this.#loaded()).spec, request);
    // From here on nothing waits, so no other request comes between the checks and the record.
    if (this.#closing) throw refuse("server-unreachable", "error.stopping", {});
    const instance = this.#instance(instanceId);
    const { loaded, description } = this.#describe();
    const { model } = loaded;
    const spec = withAgentSelection(agentSpec(loaded).spec, request);
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
    const self = execution.method !== "cli" || spec.format === "self";
    const basePrompt = buildPrompt({
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
    const prompt =
      (instruction
        ? `${basePrompt}\n\nAdditional request from the person:\n${instruction}`
        : basePrompt) + workContextPrompt(execution.workContext, loaded.language);
    const args = !self && startsProcess(spec) ? argsFor(spec, prompt) : [];
    const run: Run = {
      id,
      kind: "process",
      execution: {
        ...execution,
        ...(spec.format === "claude" || spec.format === "codex" ? { provider: spec.format } : {}),
      },
      instance: instance.id,
      process: process.id,
      agent: spec.id,
      ...(request.model || request.effort
        ? {
            selection: {
              ...(request.model ? { model: request.model } : {}),
              ...(request.effort ? { effort: request.effort } : {}),
            },
          }
        : {}),
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
      command: !self && startsProcess(spec) ? commandLine(spec, args, prompt) : null,
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
    if (run.execution?.sessionId)
      run.execution.session = {
        id: run.execution.sessionId,
        source: run.execution.resumedFrom ? "resume" : "claim",
        capturedAt: now,
        coverage: "reference-only",
        note: "ALPS has a host conversation id, but no transcript reader is attached.",
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
      const related = this.#records.runs.get(other);
      if (related) this.#persistExternalActive(related);
    }
    this.#active.set(id, active);
    this.#persistExternalActive(run);
    this.#records.runs.set(id, run);
    this.#state.runs[id] = summaryOf(run);
    instance.runs.push(id);
    this.#observe(run, "run.started", "The run was recorded and started.", {
      coverage: run.execution?.method === "cli" ? "observed" : "reference-only",
      attributes: { "alps.execution.method": run.execution?.method ?? "cli" },
    });
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
            if (parsed.sessionId) {
              run.execution = {
                ...(run.execution ?? { method: "cli" }),
                sessionId: parsed.sessionId,
                session: {
                  id: parsed.sessionId,
                  source: "agent-output",
                  capturedAt: Date.now(),
                  coverage: "reference-only",
                  note: "The agent reported a host conversation id; transcript contents were not read.",
                },
              };
              this.#observe(
                run,
                "run.reconnected",
                "The agent output identified its host conversation.",
                {
                  coverage: "reference-only",
                  attributes: { "alps.host.session": parsed.sessionId },
                },
              );
              this.#writeRun(run);
            }
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
    if (run.kind !== "process")
      try {
        fs.rmSync(recordPaths(this.root).mcpConfig(run.id), { force: true });
      } catch (error) {
        this.#deps.log(
          `cannot remove the MCP configuration of run ${run.id}: ${(error as Error).message}`,
        );
      }
    // An assessment is the latest once its run has ended, whatever its status: what it recorded
    // was read and recorded in full (record_assessment takes all the items at once).
    if (run.kind === "assess" && this.#records.assessments.has(run.id))
      this.#state.latestAssessment = run.id;
    const seconds = Math.round((run.endedAt - run.startedAt) / 1000);
    this.#emit(run, { kind: "end", ...spoken("event.end", { status: end.status, seconds }) });
    this.#observe(run, "run.finished", `The run ended with status ${end.status}.`, {
      attributes: {
        "alps.run.status": end.status,
        "alps.run.duration_ms": run.endedAt - run.startedAt,
      },
    });
    this.#state.runs[run.id] = summaryOf(run);
    try {
      writeRun(this.root, run);
      this.#saveState();
      if (run.execution && run.execution.method !== "cli")
        fs.rmSync(this.#trackingFile(run.id), { force: true });
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
  async cancelRun(id: string, caller: Caller): Promise<{ run: RunView; canceled: boolean }> {
    this.#refuseAssessing(caller);
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
   * `POST /api/runs/:id/finish`: ends a self run with the session's report. The agent of a wake or
   * an assessment reports the same way, and its run ends when the agent's process does, right
   * after.
   */
  finishRun(id: string, request: FinishRequest): { run: RunView; outputs: RunOutput[] } {
    const run = this.#run(id);
    if (
      run.agent !== "self" &&
      run.execution?.method !== "desktop" &&
      run.execution?.method !== "terminal" &&
      run.kind === "process"
    )
      throw refuse("invalid-request", "error.notSelf", { run: id, agent: run.agent });
    if (run.status !== "running")
      throw refuse("invalid-request", "error.ended", { run: id, status: run.status });
    run.report = request.report;
    const active = this.#active.get(id);
    if (run.kind !== "process" && active?.agent) {
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
    execution: RunExecution = { method: "cli" },
  ): Promise<{ run: RunView; skipped: false } | { skipped: true; running: string }> {
    if (this.#closing) throw refuse("server-unreachable", "error.stopping", {});
    this.#refusePlanOnly(trigger.kind === "request" ? trigger.caller : null);
    this.#refuseAssessing(trigger.kind === "request" ? trigger.caller : null);
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
    const info =
      execution.method === "cli" ? await this.#availability(checked.spec, checked.specs) : null;
    if (info && !info.available)
      throw refuse("agent-unavailable", "error.agentUnavailable", {
        agent: checked.spec.label,
        reason: info.reason ?? "it is not available",
      });
    if (execution.method === "cli") await this.#validateSelection(checked.spec, request);
    const agents = await this.#checkAgents(checked.specs);
    // From here on nothing waits, so no other wake comes between the checks and the record.
    if (this.#closing) throw refuse("server-unreachable", "error.stopping", {});
    const other = this.#runningWake();
    if (other) return this.#skip(other, trigger);
    const { loaded, description } = this.#describe();
    const spec = withAgentSelection(agentSpec(loaded).spec, request);
    const now = Date.now();
    const id = this.#nextId("r");
    const since = this.#state.lastWakeAt;
    const prompt =
      this.#wakePrompt(id, since, loaded, description, agents, asked) +
      workContextPrompt(execution.workContext, loaded.language);
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
      execution: {
        ...execution,
        ...(spec.format === "claude" || spec.format === "codex" ? { provider: spec.format } : {}),
      },
      instance: null,
      process: null,
      agent: spec.id,
      ...(request.model || request.effort
        ? {
            selection: {
              ...(request.model ? { model: request.model } : {}),
              ...(request.effort ? { effort: request.effort } : {}),
            },
          }
        : {}),
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
      command: execution.method === "cli" ? commandLine(spec, args, prompt) : null,
      client:
        execution.method !== "cli" && trigger.kind === "request" && trigger.caller.kind === "agent"
          ? { ...trigger.caller.client, session: trigger.caller.session }
          : null,
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
    this.#persistExternalActive(run);
    this.#records.runs.set(id, run);
    this.#state.runs[id] = summaryOf(run);
    this.#state.lastWakeAt = now;
    writeRun(this.root, run);
    this.#saveState();
    this.#emit(run, { kind: "system", ...spoken("event.woken", wokenBy(trigger)) });
    if (execution.method !== "cli") {
      this.#emit(run, { kind: "system", ...spoken("event.self", {}) });
      this.#writeRun(run);
      this.#announce(run);
      return { run: viewOf(run), skipped: false };
    }
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
   * evidence. It replaces the instance's evaluation, which is kept at the front of its evaluations
   * (supersede). Who judged comes from the caller, not the request: a user, or an agent by its
   * MCP client's name, marked self when the judged run is a self run that the same MCP session
   * performed (performedBy).
   */
  evaluate(
    instanceId: string,
    request: EvaluateRequest,
    caller: Caller,
  ): { instance: InstanceView } {
    this.#refuseAssessing(caller);
    const instance = this.#instance(instanceId);
    const { loaded, description } = this.#describe();
    const process = this.#process(loaded.model, instance.process);
    const latestId = instance.runs.at(-1);
    const latest = latestId ? this.#state.runs[latestId] : undefined;
    if (!latest) throw refuse("not-found", "error.nothingToJudge", { instance: instance.id });
    if (request.expected) {
      const current = evaluationContext(instance, description);
      if (
        request.expected.runId !== current?.runId ||
        request.expected.fingerprint !== current.fingerprint
      )
        throw refuse("invalid-request", "error.evaluationChanged", {});
    }
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
    supersede(instance, {
      runId: latest.id,
      basis: evaluationBasis(instance, description),
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
    });
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
   * `GET /api/assessment`: what the harness observes (the statistics, all time by week or since
   * `since`; the checks, which follow from the records, the model, and the configuration; the
   * facts of each instance) and, apart from it, the latest assessment whose run has ended, with
   * what the records gained after its run started (countSince, within its scope).
   */
  async assessment(since?: number): Promise<AssessmentOverview> {
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
    const input = this.#statsInput(description, facts);
    const { stats } = computeStats(
      input,
      { period: "all", granularity: "week", ...(since === undefined ? {} : { since }) },
      { now: Date.now(), utcOffsetMinutes: localUtcOffset() },
    );
    const id = this.#state.latestAssessment;
    const latest = id === null ? null : (this.#records.assessments.get(id) ?? null);
    const started = latest ? (this.#records.runs.get(latest.runId)?.startedAt ?? latest.at) : null;
    return {
      stats,
      findings,
      instances: facts,
      latest,
      since:
        latest && started !== null
          ? countSince(input, started, {
              process: latest.scope.process,
              agent: latest.scope.agent,
            })
          : null,
    };
  }

  /** `GET /api/assessment?format=markdown`: the assessment as Markdown, in the workspace's language. */
  async assessmentMarkdown(since?: number): Promise<string> {
    const overview = await this.assessment(since);
    const { loaded, description } = this.#describe();
    const processOf = (id: string) => description.processes.find((p) => p.id === id);
    return assessmentMarkdown(overview, {
      language: loaded.language,
      model: description.name,
      processName: (id) => processOf(id)?.name ?? id,
      outcomeText: (id, outcome) => processOf(id)?.outcomes[outcome] ?? "",
    });
  }

  /* ---------- assessments ---------- */

  /** The assessment run that has not ended; there is at most one. */
  #runningAssessment(): Run | undefined {
    for (const id of this.#active.keys()) {
      const run = this.#records.runs.get(id);
      if (run?.kind === "assess") return run;
    }
    return undefined;
  }

  /**
   * The assessment run that the caller performs: the one whose agent the caller's MCP server
   * serves (X-Harness-Assess), or a self assessment run that the caller's MCP session performs
   * while it runs.
   */
  #assessmentOf(caller: Caller | null): Run | undefined {
    if (caller?.kind !== "agent") return undefined;
    if (caller.assess) {
      const run = this.#records.runs.get(caller.assess);
      return run?.kind === "assess" ? run : undefined;
    }
    const running = this.#runningAssessment();
    return running && performedBy(running.client, caller) ? running : undefined;
  }

  /**
   * Refuses an instance, a run, a wake, an evaluation, or a cancellation that the agent of an
   * assessment asks for: it reads the records and records what it finds, and changes neither the
   * records nor the workspace, whatever its prompt made of it. Reading, recording the assessment,
   * and reporting stay open.
   */
  #refuseAssessing(caller: Caller | null): void {
    const run = this.#assessmentOf(caller);
    if (run) throw refuse("invalid-request", "error.assessOnly", { run: run.id });
  }

  /** What an assessment is asked to read, checked against the model: its Process, by id. */
  #scope(request: AssessRequest): AssessScope {
    const { model } = this.#loaded();
    const { period, process, agent } = request.scope;
    return {
      ...(period ? { period } : {}),
      ...(process ? { process: this.#process(model, process).id } : {}),
      ...(agent ? { agent } : {}),
      ...(request.request ? { request: request.request } : {}),
    };
  }

  /**
   * `POST /api/assess`: records an assessment run (no instance) and starts its agent with this
   * harness's MCP server, through which it reads the records and records what it finds
   * (record_assessment), then reports with finish_run. With the agent self, the calling session
   * performs it: the result carries the prompt, and finish_run ends it. Only one assessment runs at
   * a time. The harness reads nothing for the agent and interprets nothing: the scope and the
   * point of view go into the prompt and the record as given.
   */
  async assess(
    request: AssessRequest,
    caller: Caller,
    execution: RunExecution = { method: "cli" },
  ): Promise<{ run: RunView; prompt?: string }> {
    if (this.#closing) throw refuse("server-unreachable", "error.stopping", {});
    this.#refusePlanOnly(caller);
    this.#refuseAssessing(caller);
    const scope = this.#scope(request);
    const earlier = this.#runningAssessment();
    if (earlier) throw refuse("already-running", "error.assessing", { run: earlier.id });
    const name = request.agent ?? ASSESS_AGENT;
    const agentSpec = (loaded: LoadedWorkspace): { spec: AgentSpec; specs: AgentSpec[] } => {
      const specs = resolveAgents(loaded.config.agents);
      const spec = specs.find((s) => s.id === name);
      const agents = specs.map((s) => s.id).join(", ");
      if (!spec)
        throw name === "self"
          ? refuse("agent-unavailable", "error.selfDisabled", { agents })
          : refuse("agent-unavailable", "error.noAgent", { agent: name, agents });
      // A self assessment is recorded by the MCP session that performs it, so only one may ask.
      if (spec.format === "self" && caller.kind !== "agent")
        throw refuse("invalid-request", "error.selfAssess", {});
      if (spec.format !== "self" && !takesMcpServer(spec))
        throw refuse("agent-unavailable", "error.assessAgent", {
          agent: spec.label,
          agents: specs
            .filter((s) => s.format === "self" || takesMcpServer(s))
            .map((s) => s.id)
            .join(", "),
        });
      return { spec, specs };
    };
    let info: AgentInfo | null = null;
    {
      const { spec, specs } = agentSpec(this.#loaded());
      if (execution.method === "cli" && startsProcess(spec)) {
        info = await this.#availability(spec, specs);
        if (!info.available)
          throw refuse("agent-unavailable", "error.agentUnavailable", {
            agent: spec.label,
            reason: info.reason ?? "it is not available",
          });
      }
    }
    if (execution.method === "cli")
      await this.#validateSelection(agentSpec(this.#loaded()).spec, request);
    // From here on nothing waits, so no other assessment comes between the checks and the record.
    if (this.#closing) throw refuse("server-unreachable", "error.stopping", {});
    const other = this.#runningAssessment();
    if (other) throw refuse("already-running", "error.assessing", { run: other.id });
    const { loaded, description } = this.#describe();
    const spec = withAgentSelection(agentSpec(loaded).spec, request);
    const self = execution.method !== "cli" || spec.format === "self";
    const now = Date.now();
    const id = this.#nextId("r");
    const prompt =
      buildAssessPrompt({
        language: loaded.language,
        root: this.root,
        run: id,
        server: self ? null : WAKE_MCP_SERVER,
        scope,
        processName: (process) =>
          loaded.model.processes.find((p) => p.id === process)?.name ?? process,
        modelPath: description.modelPath,
        guidance: (loaded.config.guidance ?? []).map((file) => ({
          path: file,
          found: fs.existsSync(path.resolve(this.root, file)),
        })),
      }) + workContextPrompt(execution.workContext, loaded.language);
    // The agent's MCP server names this assessment, so what it records is the run's.
    const server: McpServerLaunch = {
      name: WAKE_MCP_SERVER,
      command: this.#deps.mcpServer.command,
      args: [...this.#deps.mcpServer.args, "--assess", id],
      env: { ALPS_WORKSPACE: this.root },
    };
    const configFile = recordPaths(this.root).mcpConfig(id);
    const args = self
      ? []
      : argsFor({ ...spec, args: [...spec.args, ...mcpArgs(spec, server, configFile)] }, prompt);
    const run: Run = {
      id,
      kind: "assess",
      execution: {
        ...execution,
        ...(spec.format === "claude" || spec.format === "codex" ? { provider: spec.format } : {}),
      },
      instance: null,
      process: null,
      agent: spec.id,
      ...(request.model || request.effort
        ? {
            selection: {
              ...(request.model ? { model: request.model } : {}),
              ...(request.effort ? { effort: request.effort } : {}),
            },
          }
        : {}),
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
      command: self ? null : commandLine(spec, args, prompt),
      // As for a self process run, the session tells who performs it.
      client:
        self && caller.kind === "agent" ? { ...caller.client, session: caller.session } : null,
      prompt,
      git: this.#deps.gitInfo(this.root),
      skill: null,
      scope,
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
    this.#persistExternalActive(run);
    this.#records.runs.set(id, run);
    this.#state.runs[id] = summaryOf(run);
    writeRun(this.root, run);
    this.#saveState();
    if (self) {
      this.#emit(run, { kind: "system", ...spoken("event.self", {}) });
      this.#writeRun(run);
      this.#announce(run);
      return { run: viewOf(run), prompt };
    }
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
        return { run: viewOf(run) };
      }
    this.#runAgent(run, active, spec, info, args);
    this.#announce(run);
    return { run: viewOf(run) };
  }

  /**
   * `POST /api/assessments` (`record_assessment`): the result of the assessment run that the
   * caller performs, while it runs. Each item rests on evidence that the records have (an
   * unverified one may give none), and its subject is put in the model's ids. Recording again
   * replaces what the run recorded. The assessment becomes the latest once its run ends.
   */
  recordAssessment(request: RecordAssessmentRequest, caller: Caller): Assessment {
    const run = this.#assessmentOf(caller);
    if (!run || run.status !== "running") throw refuse("invalid-request", "error.noAssessRun", {});
    const { model } = this.#loaded();
    const drafts: ItemDraft[] = request.items.map((item, i) => {
      const n = i + 1;
      const { process, artifact, instance, agent, guidance } = item.subject;
      const subject: AssessmentItem["subject"] = {};
      if (process) {
        const found = byKey(model.processes, process);
        if (!found)
          throw refuse("invalid-request", "error.itemSubject", {
            n,
            kind: "process",
            name: process,
          });
        subject.process = found.id;
      }
      if (artifact) {
        const found = byKey(model.artifacts, artifact);
        if (!found)
          throw refuse("invalid-request", "error.itemSubject", {
            n,
            kind: "artifact",
            name: artifact,
          });
        subject.artifact = found.id;
      }
      if (agent) subject.agent = agent;
      if (guidance) subject.guidance = guidance;
      if (instance) {
        if (!this.#state.instances[instance])
          throw refuse("invalid-request", "error.itemSubject", {
            n,
            kind: "instance",
            name: instance,
          });
        subject.instance = instance;
      }
      // A cut of the statistics names its Process as the dashboard's filter does: by id.
      const evidence = item.evidence.map((cited) => {
        if (!("stat" in cited) || !cited.stat.filter.process) return cited;
        const found = byKey(model.processes, cited.stat.filter.process);
        if (!found)
          throw refuse("invalid-request", "error.evidenceProcess", {
            n,
            name: cited.stat.filter.process,
          });
        return { stat: { ...cited.stat, filter: { ...cited.stat.filter, process: found.id } } };
      });
      return {
        kind: item.kind,
        subject,
        statement: item.statement,
        evidence,
        ...(item.limits ? { limits: item.limits } : {}),
      };
    });
    const items = checkedItems(drafts, {
      run: (id) =>
        this.#state.runs[id] ? { events: this.#records.runs.get(id)?.events ?? null } : null,
      observation: (id) => this.observation(id),
      instance: (id) => {
        const instance = this.#state.instances[id];
        return instance
          ? { evaluated: instance.evaluation !== null || (instance.evaluations ?? []).length > 0 }
          : null;
      },
      path: (given, where) => {
        const inside = this.#pathIn(given, where);
        return fileState(this.root, artifactPath(inside)) ? inside : null;
      },
    });
    const assessment: Assessment = {
      id: run.id,
      runId: run.id,
      at: Date.now(),
      agent: run.agent,
      scope: run.scope ?? {},
      summary: request.summary,
      items,
      reviews: [],
    };
    writeAssessment(this.root, assessment);
    this.#records.assessments.set(run.id, assessment);
    this.#emit(run, {
      kind: "system",
      ...spoken("event.assessmentRecorded", { items: items.length }),
    });
    this.#writeRun(run);
    this.#hooks.broadcast({ type: "assessment", assessment });
    return assessment;
  }

  /** `GET /api/assessments`: the assessments recorded, newest first. */
  assessments(): Assessment[] {
    return [...this.#records.assessments.values()].sort((a, b) => seqOf(b.id) - seqOf(a.id));
  }

  /** `GET /api/assessments/:id`: one assessment. */
  assessmentRecord(id: string): Assessment {
    const assessment = this.#records.assessments.get(id);
    if (!assessment) throw refuse("not-found", "error.noAssessment", { id });
    return assessment;
  }

  /**
   * `POST /api/assessments/:id/items/:n/review`: a person's review of one item of an assessment
   * whose run has ended, added after the earlier ones, which stay. Only a person reviews (the
   * WebUI, which names no MCP client): an agent does not adopt what it found. Adopting an item
   * does nothing else: a request that follows from it is the person's to send.
   */
  review(id: string, n: number, request: ReviewRequest, caller: Caller): Assessment {
    if (caller.kind !== "user") throw refuse("invalid-request", "error.reviewByPerson", {});
    const assessment = this.assessmentRecord(id);
    if (this.#state.runs[assessment.runId]?.status === "running")
      throw refuse("invalid-request", "error.assessmentOpen", { id });
    if (!assessment.items.some((item) => item.n === n))
      throw refuse("not-found", "error.noItem", { id, n, count: assessment.items.length });
    const reviewed: Assessment = {
      ...assessment,
      reviews: [
        ...assessment.reviews,
        {
          n,
          judgment: request.judgment,
          ...(request.note ? { note: request.note } : {}),
          by: { kind: "user" },
          at: Date.now(),
        },
      ],
    };
    writeAssessment(this.root, reviewed);
    this.#records.assessments.set(id, reviewed);
    this.#hooks.broadcast({ type: "assessment", assessment: reviewed });
    return reviewed;
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
