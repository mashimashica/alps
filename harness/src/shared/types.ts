/*
 * The shapes of the harness's records and views, shared by the server, the MCP
 * server, and the UI. Record shapes are defined here and nowhere else.
 */

/* ---------- model ---------- */

/** The language of prompts and MCP responses (`language` in alps-harness.yaml). */
export type Language = "en" | "ja";

/** ALPS output categories: product, information item, service. */
export type ArtifactKind = "information" | "product" | "service";

/** An Artifact type of the process model, with where its Artifacts live in the workspace. */
export interface ArtifactType {
  id: string;
  name: string;
  description: string;
  kind: ArtifactKind | null;
  /** Location patterns relative to the workspace. Only `*` and `**` are wildcards; a trailing `/` makes a directory one Artifact. */
  paths: string[];
}

/** A Process of the process model. Inputs, controls, and outputs are Artifact type ids. */
export interface Process {
  id: string;
  name: string;
  purpose: string;
  outcomes: string[];
  constraints: string[];
  enablers: string[];
  inputs: string[];
  controls: string[];
  outputs: string[];
  /** The Skill location declared in the model or in alps-harness.yaml, if any. */
  skill: string | null;
}

/** The meaning of the work, read from process-model.yaml and never written by the harness. */
export interface ProcessModel {
  name: string;
  description: string;
  processes: Process[];
  artifacts: ArtifactType[];
}

/** A SKILL.md found for a Process. Paths are relative to the workspace. */
export interface SkillLocation {
  path: string;
  dir: string;
  name: string;
  description: string;
  titles: string[];
  translations: { lang: string; path: string }[];
}

/** A declared Skill location that does not resolve to a readable SKILL.md. */
export interface MissingSkill {
  missing: string;
}

export type ProcessView = Omit<Process, "skill"> & { skill: SkillLocation | MissingSkill | null };

export type AgentId = "claude-code" | "codex" | "demo" | "self" | (string & {});

export interface AgentInfo {
  id: AgentId;
  label: string;
  available: boolean;
  version: string | null;
  reason: string | null;
}

/** The model as the workspace realizes it: Processes with their Skills, Artifact types with their locations. */
export interface ModelDescription {
  workspace: string;
  modelPath: string;
  configPath: string | null;
  language: Language;
  name: string;
  description: string;
  processes: ProcessView[];
  artifacts: ArtifactType[];
}

/** What `get_model` and `GET /api/model` return: the model with the agents that can run its Processes. */
export interface ModelView extends ModelDescription {
  agents: AgentInfo[];
}

/* ---------- artifacts ---------- */

/** A file or directory of the workspace that matches a location pattern of an Artifact type. */
export interface Artifact {
  /** The Artifact type id. */
  type: string;
  /** Relative to the workspace, with forward slashes and no trailing slash. */
  path: string;
  dir: boolean;
  /** Bytes, for a file. */
  size: number | null;
  /** The number of files inside, for a directory. */
  items: number | null;
  /** The latest modification time; for a directory, that of its newest file. */
  mtime: number;
  /** The run that last created or modified it, from provenance. */
  producedBy: string | null;
}

/* ---------- instances and evaluations ---------- */

/** The three-valued judgment of one Outcome. Only these are counted by the dashboard. */
export type Judgment = "achieved" | "not-achieved" | "unverified";

/** What an Outcome means for this application (application-specific success criterion), in free text. */
export interface OutcomeCriterion {
  /** Index into the Process's outcomes. */
  outcome: number;
  statement: string;
  checks?: string;
}

export interface OutcomeJudgment {
  /** Index into the Process's outcomes. */
  outcome: number;
  judgment: Judgment;
  /**
   * Never empty in a judgment recorded by `evaluate`. Empty only in a judgment converted from a
   * version 1 state.json, which recorded judgments without evidence.
   */
  evidence: string;
  limits?: string;
}

/** Who judged: a person in the WebUI, or an agent through MCP (`self` when the agent also performed the run). */
export type Judge = { kind: "user" } | { kind: "agent"; id: string; self?: boolean };

export interface Evaluation {
  /** The run whose results were judged. */
  runId: string;
  judgments: OutcomeJudgment[];
  /** Markdown. */
  note?: string;
  by: Judge;
  at: number;
}

/**
 * One application of a Process (Process Framework §7 instantiation): which Process, for which concrete
 * inputs, where to put the outputs, and what each Outcome means here. The display name is derived from
 * the Process name and the first input path; an instance has no title and no dates.
 */
export interface Instance {
  id: string;
  process: string;
  /** Concrete paths per Artifact type (inputs and controls). An empty list means the Artifact does not exist yet. */
  inputs: Record<string, string[]>;
  /** Location per output Artifact type. `null` means the running agent decides and reports it. */
  outputs: Record<string, string | null>;
  criteria: OutcomeCriterion[];
  notes: string;
  /** Run ids, oldest first. */
  runs: string[];
  evaluation: Evaluation | null;
  /**
   * The evaluations that later ones replaced, newest first: `evaluate` moves the current one here
   * before it records the new one, so that an assessment can tell how the judgments changed.
   * Instances evaluated before the harness kept them have none.
   */
  evaluations?: Evaluation[];
  /**
   * The wake run whose agent made the instance through the harness's MCP server (X-Harness-Wake);
   * `null` for an instance made otherwise (a person, another MCP client). Instances recorded
   * before the harness kept it have none.
   */
  createdBy?: { run: string } | null;
}

/* ---------- runs ---------- */

/**
 * A run of a Process; a wake, whose agent decides what to run; or an assessment, whose agent
 * reads the records and records the opportunities to improve the processes that it finds.
 */
export type RunKind = "process" | "wake" | "assess";

/** How far the agent of a wake goes: it starts the runs it plans (`run`), or only instantiates (`plan`). */
export type WakeRuns = "run" | "plan";

export type RunStatus = "running" | "succeeded" | "failed" | "canceled" | "interrupted";

export interface RunInput {
  type: string;
  role: "input" | "control";
  paths: string[];
  /** The paths that did not exist when the run started. */
  missing: string[];
  /**
   * The SHA-256 of each path's content as the run used it: taken when the run started, and again
   * when it ended for a path that the run itself created or modified (an input that is also an
   * output). A directory's digest covers its files. An evaluation of the run is stale once the
   * content differs (StaleReason).
   */
  sha256: Record<string, string>;
}

export interface RunTarget {
  type: string;
  /** The instance's output location, or else the type's first location pattern. */
  path: string | null;
  /** Whether `path` names one file or directory rather than a pattern. */
  concrete: boolean;
}

export interface RunOutput {
  type: string;
  path: string;
  change: "created" | "modified";
  /**
   * The runs that ran at the same time and whose outputs hold the same change: which of them made
   * it cannot be told, and the assessment says so. Absent for a change that only this run holds,
   * and in records written before the harness looked.
   */
  sharedWith?: string[];
}

/**
 * What an agent's output says it used; `null` where it says nothing (Codex reports no cost or
 * turns). Tokens are counted alike for every agent: the input tokens include those written to and
 * read from the prompt cache.
 */
export interface Usage {
  costUsd: number | null;
  /**
   * As the agent counts them. Claude Code's num_turns is its tool round trips plus one, a
   * different unit from its --max-turns, which counts the requests to the model (one request can
   * call several tools).
   */
  turns: number | null;
  inputTokens: number | null;
  /** Of the input tokens, those read from the prompt cache. */
  cachedInputTokens: number | null;
  outputTokens: number | null;
}

/** An MCP client, as its MCP server names it to the harness server (the X-Harness-Client header). */
export interface ClientInfo {
  name: string;
  version: string;
}

/** Who performs a `self` run: the MCP client, and the session through which it started the run. */
export interface RunClient extends ClientInfo {
  /**
   * The session that the client's MCP server held with the harness server (`GET /api/session`);
   * `null` when it could not open one, and in records written before sessions were kept.
   */
  session: string | null;
}

/** One attempt by an agent (`.alps-harness/runs/<id>.json`, prompt included). */
export interface Run {
  id: string;
  kind: RunKind;
  /** `null` for wake runs. */
  instance: string | null;
  process: string | null;
  agent: AgentId;
  status: RunStatus;
  createdAt: number;
  startedAt: number;
  endedAt: number | null;
  exitCode: number | null;
  /** Why the harness considers the run failed or stopped, in English. */
  error: string | null;
  /**
   * The key and arguments of `error` in shared/strings.ts, for a client that says it in another
   * language. Records written before the harness kept them have none.
   */
  errorKey?: string;
  errorArgs?: Record<string, string | number | boolean>;
  /** The failure the agent itself reported, as the agent said it. */
  agentError: string | null;
  inputs: RunInput[];
  targets: RunTarget[];
  /** The Artifacts that the run created or modified, found by comparing the output locations before and after it. */
  outputs: RunOutput[];
  usage: Usage | null;
  /** The agent's final report. */
  report: string;
  /** The number of events in runs/<id>.jsonl. */
  events: number;
  /** The command line that was started, with the prompt left out; `null` when no process is started (demo, self). */
  command: string | null;
  /** `self` runs only: the MCP client and session that perform the run. */
  client: RunClient | null;
  prompt: string;
  git: { head: string; dirty: boolean } | null;
  skill: { path: string; sha256: string | null } | null;
  /** Wake runs only: the runs that its agent started through the harness's MCP server, oldest first. */
  started?: string[];
  /**
   * Wake runs only: what the wake was asked. `request` is the requester's text, the one that the
   * prompt quotes: as given, without the white space around it and with lines ending in \n
   * (`null` for a wake without one, as a schedule's); `attachments` are the workspace paths it
   * attaches; `processes` are the ids of the Processes that the plan must include (none: the agent
   * chooses); `runs` says whether the agent was to start the runs it plans, and with `plan` the
   * harness refuses the runs and wakes that its agent would start. The reasons of the plan are in
   * `report`. Wake runs recorded before requests were kept have none of them.
   */
  request?: string | null;
  attachments?: string[];
  processes?: string[];
  runs?: WakeRuns;
  /** Assessment runs only: what the assessment was asked to read, and from what point of view. */
  scope?: AssessScope;
}

/**
 * What an assessment is asked to read: the records of a period (all time when none is given), of a
 * Process, and of an agent's runs, and from what point of view (`request`, the requester's words).
 */
export interface AssessScope {
  period?: Period;
  /** A Process id. */
  process?: string;
  agent?: string;
  request?: string;
}

/** A run as the API lists it: the record without its prompt. */
export type RunView = Omit<Run, "prompt">;

/** A normalized event of a run (`.alps-harness/runs/<id>.jsonl`). */
export interface RunEvent {
  n: number;
  t: number;
  kind:
    | "system"
    | "message"
    | "thinking"
    | "tool"
    | "output"
    | "stderr"
    | "error"
    | "result"
    | "end";
  /** In English for what the harness itself says; as the agent wrote it otherwise. */
  text: string;
  /**
   * What the harness itself says (the system and end events, and its own errors): the key and
   * arguments of `text` in shared/strings.ts, for a client that shows it in another language.
   */
  key?: string;
  args?: Record<string, string | number | boolean>;
}

/** The summary of a run kept in state.json; the full record is in runs/<id>.json. */
export interface RunSummary {
  id: string;
  kind: RunKind;
  instance: string | null;
  status: RunStatus;
  startedAt: number;
  endedAt: number | null;
}

/** `.alps-harness/state.json`. */
export interface StateFile {
  schemaVersion: 2;
  instances: Record<string, Instance>;
  /** Artifact path to the id of the run that last created or modified it. */
  provenance: Record<string, string>;
  /** The last number used for an instance or run id. */
  seq: number;
  lastWakeAt: number | null;
  /**
   * The latest assessment whose run has ended (its id, which is its run's); `null` before any, and
   * in state files written before the harness kept assessments.
   */
  latestAssessment: string | null;
  runs: Record<string, RunSummary>;
}

/* ---------- version 1 records (read only to convert them) ---------- */

/** A run in a state.json without schemaVersion (harness 0.8 and earlier). */
export interface RunV1 {
  id: string;
  process: string;
  case: string | null;
  agent: string;
  workItem: string | null;
  status: RunStatus;
  createdAt: number;
  startedAt: number;
  endedAt: number | null;
  exitCode: number | null;
  error: string | null;
  agentError: string | null;
  usage: Usage | null;
  summary: string;
  inputs: { type: string; role: "input" | "control"; paths: string[] }[];
  targets: RunTarget[];
  outputs: RunOutput[];
  events: number;
  command: string | null;
  prompt: string;
  git: { head: string; dirty: boolean } | null;
  skill: { path: string; sha256: string | null } | null;
}

/** A work item: planned or repeated runs of a Process for a case, judged per Outcome without evidence. */
export interface WorkItemV1 {
  id: string;
  process: string;
  case: string | null;
  agent: string | null;
  plannedStart: number | null;
  plannedEnd: number | null;
  createdAt: number;
  runs: string[];
  review: { runId: string; judgments: string[]; note: string; at: number } | null;
}

/** A state.json without schemaVersion. Runs are kept inline. */
export interface StateFileV1 {
  seq: number;
  runs: Record<string, RunV1>;
  workItems: Record<string, WorkItemV1>;
  provenance: Record<string, string>;
}

/* ---------- facts about instances ---------- */

/** Why an evaluation no longer rests on what the workspace holds now. */
export type StaleReason =
  /**
   * An input's content differs from what the judged run used (by SHA-256): modified, created
   * although it was missing then, or removed although it was there.
   */
  | { kind: "input"; type: string; path: string; change: "modified" | "created" | "removed" }
  /** The Process's SKILL.md differs from the one the judged run used (`path` is the current one, if any). */
  | { kind: "skill"; path: string | null };

/** The facts of one instance, as `list_instances` and the assessment report them. */
export interface InstanceFacts {
  instance: string;
  process: string;
  latestRun: RunSummary | null;
  /** The judgments of the evaluation, or `null` before any. They are about `evaluatedRun`, which may precede `latestRun`. */
  judgments: OutcomeJudgment[] | null;
  evaluatedRun: string | null;
  /** Whether an input or the SKILL.md differs from what the judged run used. */
  stale: boolean;
  staleness: StaleReason[];
}

/** An instance with its facts. */
export interface InstanceView extends Instance {
  facts: InstanceFacts;
}

/* ---------- server ---------- */

/** `.alps-harness/server.json`: the running daemon. Removed when the daemon exits. */
export interface ServerInfo {
  pid: number;
  port: number;
  token: string;
  startedAt: number;
}

/** `GET /api/health`. */
export interface HealthInfo {
  ok: true;
  name: "alps-harness";
  version: string;
  pid: number;
  port: number;
  startedAt: number;
  workspace: string;
  development: boolean;
}

/** Messages on `GET /api/session`, the connection that an MCP server holds while its client is connected. */
export type SessionEvent = { type: "session"; id: string } | { type: "shutdown" };

/** Messages on `GET /api/events` (server-sent events). */
export type ServerEvent =
  | { type: "hello"; startedAt: number }
  | { type: "shutdown" }
  /** An instance was created, updated, run, or evaluated. */
  | { type: "instance"; instance: InstanceView }
  /** A run started or ended. */
  | { type: "run"; run: RunSummary }
  /** Artifacts may have changed (a run ended); list them again. */
  | { type: "artifacts" }
  /** The model, the configuration, or a SKILL.md changed on disk; read the model again. */
  | { type: "model" }
  /** An assessment was recorded, or a person reviewed one of its items. */
  | { type: "assessment"; assessment: Assessment };

/** Error codes of the MCP tools, also used by the HTTP API. */
export type ErrorCode =
  | "no-model"
  | "not-found"
  | "agent-unavailable"
  | "already-running"
  | "invalid-judgment"
  | "server-unreachable";

/** Rejections by the HTTP layer: its safety checks, and requests that do not fit the API. */
export type HttpErrorCode =
  | "forbidden-host"
  | "cross-site"
  | "unauthorized"
  | "unsupported-media-type"
  /**
   * The body or query does not fit the endpoint, or names what the Process does not have, or the
   * agent of a wake that plans only asks for a run or a wake.
   */
  | "invalid-request"
  /** An instance's input or output path, or an attachment, lies outside the workspace. */
  | "outside-workspace"
  /** A body over the server's limits: a JSON body over 1 MiB, an upload over 21 MiB, or an attachment over 20 MB. */
  | "too-large"
  | "internal";

export interface ErrorInfo {
  code: ErrorCode | HttpErrorCode;
  /** In English. */
  message: string;
  /** The message's key and arguments in shared/strings.ts, for a client that shows it in another language. */
  key?: string;
  args?: Record<string, string | number | boolean>;
  /** `no-model`: the files looked at, or where a missing one can be placed; `server-unreachable`: server.json and server.log. */
  files?: string[];
}

/** The body of every failed API response and failed tool result. */
export interface Failure {
  ok: false;
  error: ErrorInfo;
}

/* ---------- HTTP API responses (the MCP tools return the same) ---------- */

/** `GET /api/model` (`get_model`). */
export interface ModelResponse {
  ok: true;
  model: ModelView;
}

/** `GET /api/artifacts` (`list_artifacts`): newest first. */
export interface ArtifactsResponse {
  ok: true;
  artifacts: Artifact[];
  /** Whether a location had more matches than the scan reads. */
  truncated: boolean;
}

/** `GET /api/instances` (`list_instances`): newest first; `next` is the cursor of the next page. */
export interface InstancesResponse {
  ok: true;
  instances: InstanceView[];
  next: string | null;
}

/** A run as `GET /api/runs` (`list_runs`) lists it: its summary, with its Process, agent, and cost. */
export interface ListedRun extends RunSummary {
  process: string | null;
  /** `null` when the run's record cannot be read. */
  agent: AgentId | null;
  costUsd: number | null;
}

/** `GET /api/runs` (`list_runs`): runs, newest first; `next` is the cursor of the next page. */
export interface RunsResponse {
  ok: true;
  runs: ListedRun[];
  next: string | null;
}

/**
 * `POST /api/instances` (`instantiate`), `GET /api/instances/:id`, and
 * `POST /api/instances/:id/evaluate` (`evaluate`).
 */
export interface InstanceResponse {
  ok: true;
  instance: InstanceView;
  /** `instantiate` only: whether a new instance was created rather than an existing one updated. */
  created?: boolean;
}

/** `POST /api/instances/:id/run` (`run`). Success means that the run started, not that any Outcome is achieved. */
export interface RunStartResponse {
  ok: true;
  run: RunView;
  /** `self` runs only: what the calling session is to do. */
  prompt?: string;
}

/** `GET /api/runs/:id` (`get_run`). */
export interface RunDetailResponse {
  ok: true;
  run: Run;
  /** The last events, oldest first. */
  events: RunEvent[];
  /** Whether earlier events were left out. */
  truncated: boolean;
}

/** `POST /api/runs/:id/cancel` (`cancel_run`). It answers once the run has ended. */
export interface CancelResponse {
  ok: true;
  run: RunView;
  /** Whether this request stopped the run; `false` when it had already ended. */
  canceled: boolean;
}

/** `POST /api/runs/:id/finish` (`finish_run`). */
export interface FinishResponse {
  ok: true;
  run: RunView;
  /** The output changes found by comparing the output locations with their state when the run started. */
  outputs: RunOutput[];
}

/**
 * `POST /api/wake` (`wake`): the wake run that started, or, while an earlier wake still runs, that
 * none was (the skip is recorded in the running wake's events).
 */
export interface WakeResponse {
  ok: true;
  /** The wake run that started; absent when the wake was skipped. */
  run?: RunView;
  skipped: boolean;
  /** When skipped: the wake run that still runs. */
  running?: string;
}

/**
 * `POST /api/attachments` (the WebUI, multipart/form-data): where the files attached to a request
 * were saved, relative to the workspace, in the order they were sent. A wake request lists them in
 * its `attachments`.
 */
export interface AttachmentsResponse {
  ok: true;
  paths: string[];
}

/** `GET /api/assessment` (`get_assessment`, JSON form). */
export interface AssessmentResponse {
  ok: true;
  assessment: AssessmentOverview;
}

/**
 * `POST /api/assess` (`assess`): the assessment run that started. Success means that it started;
 * its result is the latest assessment of `GET /api/assessment` once it has ended.
 */
export interface AssessResponse {
  ok: true;
  run: RunView;
  /** `self` runs only: what the calling session is to do. */
  prompt?: string;
}

/**
 * `POST /api/assessments` (`record_assessment`), `GET /api/assessments/:id`, and
 * `POST /api/assessments/:id/items/:n/review` (the WebUI).
 */
export interface AssessmentRecordResponse {
  ok: true;
  assessment: Assessment;
}

/** `GET /api/assessments`: the assessments recorded, newest first. */
export interface AssessmentsResponse {
  ok: true;
  assessments: Assessment[];
}

/** `GET /api/assessment?format=markdown` (`get_assessment`, Markdown form, in the workspace's language). */
export interface AssessmentMarkdownResponse {
  ok: true;
  markdown: string;
}

/** `GET /api/stats` (the dashboard): the statistics, and what each of their numbers counts. */
export interface StatsResponse {
  ok: true;
  stats: Stats;
  members: StatsMembers;
}

/** `GET /api/skill?process=` (the WebUI): the SKILL.md of a Process, as text. */
export interface SkillResponse {
  ok: true;
  skill: SkillLocation;
  text: string;
  /** Whether the file was longer than what is returned. */
  truncated: boolean;
}

/** The screens of the WebUI that `open_ui` can open. */
export type UiView = "network" | "dashboard" | "instances";

/** `POST /api/open` (`open_ui`). */
export interface OpenResponse {
  ok: true;
  /** The WebUI's URL with the token in its fragment. */
  url: string;
  /** Whether the server opened it in a browser. */
  opened: boolean;
}

/* ---------- dashboard and assessment ---------- */

export type Period = "7d" | "30d" | "90d" | "all";
export type Granularity = "day" | "week";

export interface StatsFilter {
  period: Period;
  granularity: Granularity;
  process?: string;
  agent?: string;
  /** `get_assessment`'s `since` (epoch milliseconds): the window starts there instead of with the period. */
  since?: number;
}

/** A share with its counts; `value` is `null` when the denominator is 0. */
export interface Ratio {
  numerator: number;
  denominator: number;
  value: number | null;
}

export interface DurationStats {
  medianMs: number | null;
  p90Ms: number | null;
}

/** The metric tiles. Wake and assessment runs are excluded from all statistics. */
export interface StatsMetrics {
  /** Achieved among judged Outcomes. */
  achievement: Ratio;
  /** Unverified among judged Outcomes, with the instances whose run ended but have no judgment yet. */
  unverified: Ratio & { awaitingJudgment: number };
  /**
   * Instances whose inputs or SKILL.md changed after the judgment: the state now, whatever the
   * window, as the WebUI's count at the top right. A Process filter applies; an agent filter
   * does not.
   */
  staleEvaluations: number;
  /** Process runs in the period that succeeded. */
  runSuccess: Ratio;
  duration: DurationStats;
  usage: {
    costUsd: number | null;
    inputTokens: number | null;
    cachedInputTokens: number | null;
    outputTokens: number | null;
    costPerAchievedOutcome: number | null;
  };
}

/** One period bucket of the trends; all four trends share the period and granularity. */
export interface TrendBucket {
  start: number;
  runs: Record<Exclude<RunStatus, "running">, number>;
  judgments: Record<Judgment, number>;
  achievementRate: number | null;
  costByAgent: Record<string, number>;
  duration: DurationStats;
}

export interface ProcessBreakdown {
  process: string;
  instances: number;
  runs: number;
  runSuccess: Ratio;
  duration: DurationStats;
  achievement: Ratio;
  unverified: Ratio;
  costUsd: number | null;
}

export interface AgentBreakdown {
  agent: AgentId;
  runs: number;
  runSuccess: Ratio;
  achievement: Ratio;
  costPerAchievedOutcome: number | null;
  runsPerInstance: number | null;
}

export interface OutcomeBreakdown {
  process: string;
  outcome: number;
  counts: Record<Judgment, number>;
}

export interface JudgeBreakdown {
  judge: "user" | "agent" | "self";
  judgments: number;
  achievement: Ratio;
}

export interface Stats {
  filter: StatsFilter;
  /**
   * The runs that started and the judgments made in this window count (the stale evaluations are
   * the state now). `start` is `null` for all time; the periods of days start at midnight, the
   * period's first day included.
   */
  window: { start: number | null; end: number };
  metrics: StatsMetrics;
  trends: TrendBucket[];
  breakdowns: {
    process: ProcessBreakdown[];
    agent: AgentBreakdown[];
    outcome: OutcomeBreakdown[];
    judge: JudgeBreakdown[];
  };
}

/** A process run that the statistics count, for listing what a number is made of. */
export interface StatsRun {
  id: string;
  instance: string | null;
  process: string | null;
  agent: AgentId;
  status: RunStatus;
  startedAt: number;
  endedAt: number | null;
  costUsd: number | null;
}

/** An instance that the statistics count, and which of the numbers it is in. */
export interface StatsInstance {
  id: string;
  process: string;
  /** Its evaluation is in the window (and its judgments count). */
  judged: boolean;
  /** Its latest run ended in the window and has no judgment yet. */
  awaiting: boolean;
  /** Its evaluation's evidence is stale now (whatever the window). */
  stale: boolean;
}

/** What the numbers of the statistics count; the WebUI lists them when a number is clicked. */
export interface StatsMembers {
  instances: StatsInstance[];
  runs: StatsRun[];
}

/** A finding: a description problem, a configuration problem, or something unverified. */
export type FindingKind = "description" | "configuration" | "unverified";

export interface Finding {
  kind: FindingKind;
  subject: {
    process?: string;
    outcome?: number;
    artifact?: string;
    instance?: string;
    /** The agent that cannot be started. */
    agent?: string;
  };
  /** In English. */
  message: string;
  /** The message's key and arguments in shared/strings.ts, for a client that shows it in another language. */
  key?: string;
  args?: Record<string, string | number | boolean>;
  evidence: string[];
}

/**
 * `GET /api/assessment` and the `get_assessment` tool (JSON form): what the harness observes (the
 * statistics, the checks, the facts of the instances) and the latest assessment, an agent's
 * interpretation, apart from them.
 */
export interface AssessmentOverview {
  /** The dashboard's statistics: all time by week, or since `since`. */
  stats: Stats;
  /** The checks: what fixed tests of the records, the model, and the configuration find. */
  findings: Finding[];
  instances: InstanceFacts[];
  /** The latest assessment whose run has ended; `null` before any. */
  latest: Assessment | null;
  /**
   * What the records gained after the latest assessment's run started, within its scope's Process
   * and agent: the process runs that started, and the Outcome judgments made (those that later
   * evaluations replaced included). `null` without an assessment.
   */
  since: { runs: number; judgments: number } | null;
}

/* ---------- assessments ---------- */

/**
 * What an assessment item is about: the Process Description (`description`, for
 * design-process-description), the configuration that realizes it (`configuration`, for
 * design-agent-work-system), how the work is operated (`operation`: guidance, schedules, requests),
 * or what the records cannot settle (`unverified`).
 */
export type AssessmentItemKind = "description" | "configuration" | "operation" | "unverified";

/** A cut of the statistics: the dashboard's filter. */
export type StatCut = Partial<Pick<StatsFilter, "period" | "granularity" | "process" | "agent">>;

/** A record that an assessment item rests on. */
export type Evidence =
  | { run: string }
  | { instance: string }
  /** The evaluation of an instance, and the evaluations it replaced. */
  | { evaluation: string }
  /** A number of the statistics (`metric`, as the dashboard names it) for a cut. */
  | { stat: { filter: StatCut; metric: string } }
  /** One event of a run's log, by its number. */
  | { log: { run: string; n: number } }
  /** A file or directory of the workspace, relative to it. */
  | { path: string };

/** One opportunity to improve the processes, as an assessment's agent found it. */
export interface AssessmentItem {
  /** From 1, in the order recorded. */
  n: number;
  kind: AssessmentItemKind;
  subject: {
    process?: string;
    /** An Artifact type id. */
    artifact?: string;
    agent?: string;
    /** A guidance file, relative to the workspace. */
    guidance?: string;
    instance?: string;
  };
  /** One sentence. */
  statement: string;
  /** Never empty, except for an unverified item. */
  evidence: Evidence[];
  /** What the evidence does not cover. */
  limits?: string;
}

/** A person's review of an assessment item. */
export type ReviewJudgment = "adopted" | "held" | "rejected";

export interface Review {
  /** The item's number. */
  n: number;
  judgment: ReviewJudgment;
  note?: string;
  /** Only a person reviews (the WebUI): an agent does not adopt its own findings. */
  by: { kind: "user" };
  at: number;
}

/**
 * An agent's assessment of the records (`.alps-harness/assessments/<run>.json`): its
 * interpretation, which the harness keeps apart from what it observes. One assessment run records
 * one; its id is the run's.
 */
export interface Assessment {
  id: string;
  runId: string;
  /** When it was recorded (record_assessment). */
  at: number;
  agent: AgentId;
  scope: AssessScope;
  /** Markdown: what the agent read and did not read, and what it found. */
  summary: string;
  items: AssessmentItem[];
  /** Oldest first. A later review of an item comes after the earlier ones, which stay. */
  reviews: Review[];
}
