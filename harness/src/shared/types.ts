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

/** What `get_model` and `GET /api/model` return once agent detection is available. */
export interface ModelView extends ModelDescription {
  agents: AgentInfo[];
}

/* ---------- instances, runs, and evaluations ---------- */

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
  outcome: number;
  judgment: Judgment;
  /** Never empty. */
  evidence: string;
  limits?: string;
}

/** Who judged: a person in the WebUI, or an agent through MCP (`self` when the agent also performed the run). */
export type Judge = { kind: "user" } | { kind: "agent"; id: string; self?: boolean };

export interface Evaluation {
  runId: string;
  judgments: OutcomeJudgment[];
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
  /** Concrete paths per Artifact type. An empty list means the Artifact does not exist yet. */
  inputs: Record<string, string[]>;
  /** Location per Artifact type. `null` means the running agent decides and reports it. */
  outputs: Record<string, string | null>;
  criteria: OutcomeCriterion[];
  notes: string;
  runs: string[];
  evaluation: Evaluation | null;
}

export type RunKind = "process" | "wake";

export type RunStatus = "running" | "succeeded" | "failed" | "canceled" | "interrupted";

export interface RunInput {
  type: string;
  role: "input" | "control";
  paths: string[];
}

export interface RunTarget {
  type: string;
  path: string | null;
  concrete: boolean;
}

export interface RunOutput {
  type: string;
  path: string;
  change: "created" | "modified";
}

export interface Usage {
  costUsd: number | null;
  turns: number | null;
  inputTokens: number | null;
  outputTokens: number | null;
}

/** The MCP client that performs a `self` run. */
export interface ClientInfo {
  name: string;
  version: string;
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
  error: string | null;
  agentError: string | null;
  inputs: RunInput[];
  targets: RunTarget[];
  outputs: RunOutput[];
  usage: Usage | null;
  report: string;
  events: number;
  /** `null` for `self` runs, which have `client` instead. */
  command: string | null;
  client: ClientInfo | null;
  prompt: string;
  git: { head: string; dirty: boolean } | null;
  skill: { path: string; sha256: string | null } | null;
  /** Wake runs only: the runs this wake started. */
  started?: string[];
}

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
  text: string;
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
  seq: number;
  lastWakeAt: number | null;
  runs: Record<string, RunSummary>;
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

/** Messages on `GET /api/events` (server-sent events). */
export type ServerEvent = { type: "hello"; startedAt: number } | { type: "shutdown" };

/** Error codes of the MCP tools, also used by the HTTP API. */
export type ErrorCode =
  | "no-model"
  | "not-found"
  | "agent-unavailable"
  | "already-running"
  | "invalid-judgment"
  | "server-unreachable";

/** Rejections by the HTTP layer's safety checks. */
export type HttpErrorCode =
  | "forbidden-host"
  | "cross-site"
  | "unauthorized"
  | "unsupported-media-type"
  | "internal";

export interface ErrorInfo {
  code: ErrorCode | HttpErrorCode;
  message: string;
  /** `no-model`: where the missing file can be placed. */
  files?: string[];
}

/** The body of every failed API response and failed tool result. */
export interface Failure {
  ok: false;
  error: ErrorInfo;
}

/* ---------- dashboard and assessment ---------- */

export type Period = "7d" | "30d" | "90d" | "all";
export type Granularity = "day" | "week";

export interface StatsFilter {
  period: Period;
  granularity: Granularity;
  process?: string;
  agent?: string;
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

/** The metric tiles. Wake runs are excluded from all statistics. */
export interface StatsMetrics {
  /** Achieved among judged Outcomes. */
  achievement: Ratio;
  /** Unverified among judged Outcomes, with the instances whose run ended but have no judgment yet. */
  unverified: Ratio & { awaitingJudgment: number };
  /** Instances whose inputs or SKILL.md changed after the judgment. */
  staleEvaluations: number;
  /** Process runs in the period that succeeded. */
  runSuccess: Ratio;
  duration: DurationStats;
  usage: {
    costUsd: number | null;
    inputTokens: number | null;
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
  metrics: StatsMetrics;
  trends: TrendBucket[];
  breakdowns: {
    process: ProcessBreakdown[];
    agent: AgentBreakdown[];
    outcome: OutcomeBreakdown[];
    judge: JudgeBreakdown[];
  };
}

/** A finding: a description problem, a configuration problem, or something unverified. */
export type FindingKind = "description" | "configuration" | "unverified";

export interface Finding {
  kind: FindingKind;
  subject: { process?: string; outcome?: number; artifact?: string; instance?: string };
  message: string;
  evidence: string[];
}

/** The facts of one instance, as `list_instances` and the assessment report them. */
export interface InstanceFacts {
  instance: string;
  process: string;
  latestRun: { id: string; status: RunStatus } | null;
  judgments: OutcomeJudgment[] | null;
  stale: boolean;
}

/** `GET /api/assessment` and the `get_assessment` tool (JSON form). */
export interface Assessment {
  stats: Stats;
  findings: Finding[];
  instances: InstanceFacts[];
}
