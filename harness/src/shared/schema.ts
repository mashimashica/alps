/*
 * zod schemas for the files the harness reads and the requests its API accepts. The schemas of
 * the configuration and the model normalize YAML scalars, so the loader works with one shape per
 * file; the schemas of the records are typed against shared/types.ts, which defines their shapes.
 */

import { z } from "zod";
import { cronProblem } from "./cron.ts";
import type {
  Instance,
  Judge,
  Run,
  RunOutput,
  RunSummary,
  RunTarget,
  StateFile,
  StateFileV1,
  Usage,
} from "./types.ts";

/** A YAML scalar read as text: strings are trimmed and numbers are stringified. */
const text = z.union([z.string(), z.number()]).transform((value) => String(value).trim());

/** One text or a list of texts. Empty entries are dropped; a missing or null value is an empty list. */
const textList = z
  .union([text, z.array(text)])
  .nullish()
  .transform((value) =>
    (value === null || value === undefined ? [] : Array.isArray(value) ? value : [value]).filter(
      Boolean,
    ),
  );

/** ALPS output categories. The Japanese names of the existing format are accepted as aliases. */
const KIND_ALIASES = {
  information: "information",
  情報項目: "information",
  product: "product",
  製品: "product",
  service: "service",
  サービス: "service",
} as const;

const artifactKind = z
  .enum(
    Object.keys(KIND_ALIASES) as [keyof typeof KIND_ALIASES, ...(keyof typeof KIND_ALIASES)[]],
    {
      error: "kind must be information, product, or service",
    },
  )
  .transform((kind) => KIND_ALIASES[kind]);

/* ---------- process-model.yaml ---------- */

const processEntry = z
  .looseObject({
    id: text.optional(),
    name: text.optional(),
    purpose: text.optional(),
    outcomes: textList,
    constraints: textList,
    enablers: textList,
    inputs: textList,
    controls: textList,
    outputs: textList,
    skill: text.nullish(),
  })
  .refine((entry) => Boolean(entry.name || entry.id), { error: "a process needs a name" });

const artifactEntry = z.preprocess(
  (value) => (typeof value === "string" || typeof value === "number" ? { name: value } : value),
  z
    .looseObject({
      id: text.optional(),
      name: text.optional(),
      description: text.optional(),
      kind: artifactKind.nullish(),
      paths: textList,
    })
    .refine((entry) => Boolean(entry.name || entry.id), { error: "an artifact type needs a name" }),
);

/** process-model.yaml: the meaning of the work. Its format is shared with the ALPS process model viewer. */
export const processModelFileSchema = z.looseObject({
  name: text.optional(),
  description: text.optional(),
  processes: z.array(processEntry).min(1, { error: "list at least one process under processes" }),
  artifacts: z
    .array(artifactEntry)
    .nullish()
    .transform((value) => value ?? []),
});

export type ProcessModelFile = z.output<typeof processModelFileSchema>;

/* ---------- alps-harness.yaml ---------- */

/** `artifacts.<type>`: a map, or a path or list of paths as a shorthand for `{ paths }`. */
const artifactConfig = z.preprocess(
  (value) => (typeof value === "string" || Array.isArray(value) ? { paths: value } : value),
  z.looseObject({
    kind: artifactKind.optional(),
    paths: textList.optional(),
  }),
);

const agentConfig = z.looseObject({
  label: text.optional(),
  command: text.optional(),
  args: z.array(text).optional(),
  env: z.record(z.string(), text).optional(),
  stdin: z.boolean().optional(),
  format: z.enum(["claude", "codex", "demo", "text"]).optional(),
});

/** alps-harness.yaml: how the workspace realizes the model. It never changes the model's meaning. */
export const harnessConfigSchema = z.looseObject({
  model: text.optional(),
  language: z.enum(["en", "ja"]).optional(),
  artifacts: z.record(z.string(), artifactConfig).nullish(),
  skills: z.record(z.string(), text.nullable()).nullish(),
  skillRoots: textList.optional(),
  /** `false` or `null` removes an agent; `self: false` forbids the self mode. */
  agents: z.record(z.string(), z.union([z.literal(false), z.null(), agentConfig])).nullish(),
  prompt: text.optional(),
  server: z
    .looseObject({
      /** 0 lets the system choose a free port. */
      port: z.int().min(0).max(65_535).optional(),
      /** Minutes without connections and running runs before the daemon exits. Fractions are allowed. */
      idleMinutes: z.number().positive().optional(),
    })
    .optional(),
  /** Markdown files, relative to the workspace, that a woken agent reads; the harness never interprets them. */
  guidance: textList.optional(),
  /** When the daemon wakes an agent (crontab's five fields, local time); none keeps it from stopping when idle. */
  schedules: z
    .array(
      z.looseObject({
        cron: text.check((context) => {
          const problem = cronProblem(context.value);
          if (problem)
            context.issues.push({ code: "custom", message: problem, input: context.value });
        }),
        // Whether it names an agent that can be woken depends on `agents`: loading checks it (model/load.ts).
        agent: text.pipe(z.string().min(1, { error: "name the agent to wake" })),
      }),
    )
    .optional(),
});

export type HarnessConfig = z.output<typeof harnessConfigSchema>;

/* ---------- .alps-harness records ---------- */

const epochMs = z.number().nonnegative();
const runStatus = z.enum(["running", "succeeded", "failed", "canceled", "interrupted"]);
const judgment = z.enum(["achieved", "not-achieved", "unverified"]);
const judge: z.ZodType<Judge> = z.union([
  z.object({ kind: z.literal("user") }),
  z.object({ kind: z.literal("agent"), id: z.string().min(1), self: z.boolean().optional() }),
]);

const usage: z.ZodType<Usage> = z.object({
  costUsd: z.number().nullable(),
  turns: z.number().nullable(),
  inputTokens: z.number().nullable(),
  outputTokens: z.number().nullable(),
});
const runTarget: z.ZodType<RunTarget> = z.object({
  type: z.string(),
  path: z.string().nullable(),
  concrete: z.boolean(),
});
const runOutput: z.ZodType<RunOutput> = z.object({
  type: z.string(),
  path: z.string(),
  change: z.enum(["created", "modified"]),
});
const gitInfo = z.object({ head: z.string(), dirty: z.boolean() }).nullable();
const skillUsed = z.object({ path: z.string(), sha256: z.string().nullable() }).nullable();

const instance: z.ZodType<Instance> = z.object({
  id: z.string(),
  process: z.string(),
  inputs: z.record(z.string(), z.array(z.string())),
  outputs: z.record(z.string(), z.string().nullable()),
  criteria: z.array(
    z.object({ outcome: z.int().min(0), statement: z.string(), checks: z.string().optional() }),
  ),
  notes: z.string(),
  runs: z.array(z.string()),
  evaluation: z
    .object({
      runId: z.string(),
      judgments: z.array(
        z.object({
          outcome: z.int().min(0),
          judgment,
          evidence: z.string(),
          limits: z.string().optional(),
        }),
      ),
      note: z.string().optional(),
      by: judge,
      at: epochMs,
    })
    .nullable(),
});

const runSummary: z.ZodType<RunSummary> = z.object({
  id: z.string(),
  kind: z.enum(["process", "wake"]),
  instance: z.string().nullable(),
  status: runStatus,
  startedAt: epochMs,
  endedAt: epochMs.nullable(),
});

/** `.alps-harness/state.json`, version 2. */
export const stateFileSchema: z.ZodType<StateFile> = z.object({
  schemaVersion: z.literal(2),
  instances: z.record(z.string(), instance),
  provenance: z.record(z.string(), z.string()),
  seq: z.int().min(0),
  lastWakeAt: epochMs.nullable(),
  runs: z.record(z.string(), runSummary),
});

/** `.alps-harness/runs/<id>.json`. */
export const runRecordSchema: z.ZodType<Run, unknown> = z.object({
  id: z.string(),
  kind: z.enum(["process", "wake"]),
  instance: z.string().nullable(),
  process: z.string().nullable(),
  agent: z.string(),
  status: runStatus,
  createdAt: epochMs,
  startedAt: epochMs,
  endedAt: epochMs.nullable(),
  exitCode: z.number().nullable(),
  error: z.string().nullable(),
  agentError: z.string().nullable(),
  inputs: z.array(
    z.object({
      type: z.string(),
      role: z.enum(["input", "control"]),
      paths: z.array(z.string()),
      missing: z.array(z.string()),
      // Records written before the harness kept the content of inputs have none.
      sha256: z.record(z.string(), z.string()).default({}),
    }),
  ),
  targets: z.array(runTarget),
  outputs: z.array(runOutput),
  usage: usage.nullable(),
  report: z.string(),
  events: z.int().min(0),
  command: z.string().nullable(),
  client: z
    .object({
      name: z.string(),
      version: z.string(),
      // Records written before the harness kept the session have none.
      session: z.string().nullable().default(null),
    })
    .nullable(),
  prompt: z.string(),
  git: gitInfo,
  skill: skillUsed,
  started: z.array(z.string()).optional(),
});

/**
 * A state.json without schemaVersion (harness 0.8 and earlier). Only what the conversion reads is
 * checked; missing optional values get the defaults the old harness used.
 */
export const stateFileV1Schema: z.ZodType<StateFileV1, unknown> = z.object({
  seq: z.int().min(0).default(0),
  runs: z
    .record(
      z.string(),
      z.object({
        id: z.string(),
        process: z.string(),
        case: z.string().nullish().default(null),
        agent: z.string(),
        workItem: z.string().nullish().default(null),
        status: runStatus,
        createdAt: epochMs,
        startedAt: epochMs,
        endedAt: epochMs.nullish().default(null),
        exitCode: z.number().nullish().default(null),
        error: z.string().nullish().default(null),
        agentError: z.string().nullish().default(null),
        usage: usage.nullish().default(null),
        summary: z
          .string()
          .nullish()
          .transform((value) => value ?? ""),
        inputs: z
          .array(
            z.object({
              type: z.string(),
              role: z.enum(["input", "control"]),
              paths: z.array(z.string()),
            }),
          )
          .default([]),
        targets: z.array(runTarget).default([]),
        outputs: z.array(runOutput).default([]),
        events: z.int().min(0).default(0),
        command: z.string().nullish().default(null),
        prompt: z.string().default(""),
        git: gitInfo.optional().default(null),
        skill: skillUsed.optional().default(null),
      }),
    )
    .default({}),
  workItems: z
    .record(
      z.string(),
      z.object({
        id: z.string(),
        process: z.string(),
        case: z.string().nullish().default(null),
        agent: z.string().nullish().default(null),
        plannedStart: epochMs.nullish().default(null),
        plannedEnd: epochMs.nullish().default(null),
        createdAt: epochMs.default(0),
        runs: z.array(z.string()).default([]),
        review: z
          .object({
            runId: z.string(),
            judgments: z.array(z.string()),
            note: z.string().default(""),
            at: epochMs,
          })
          .nullish()
          .default(null),
      }),
    )
    .default({}),
  provenance: z.record(z.string(), z.string()).default({}),
});

/* ---------- HTTP API requests (and the arguments of the MCP tools that relay them) ---------- */

/** One path or a list of paths. */
const pathList = z
  .union([z.string(), z.array(z.string())])
  .transform((value) => (Array.isArray(value) ? value : [value]));
const freeText = z.string().trim();

const criterion = z.strictObject({
  outcome: z.int().min(0),
  statement: freeText.min(1, { error: "a criterion needs a statement" }),
  checks: freeText.optional(),
});

/** `instantiate` of a new instance. Types and the Process are named by id or name. */
export const createInstanceRequest = z.strictObject({
  process: z.string().min(1),
  inputs: z.record(z.string(), pathList).default({}),
  outputs: z.record(z.string(), z.string().nullable()).default({}),
  criteria: z.array(criterion).default([]),
  notes: z.string().default(""),
});

/** `instantiate` with an existing `instance`: new criteria and notes for it. */
export const updateInstanceRequest = z.strictObject({
  instance: z.string().min(1),
  criteria: z.array(criterion).optional(),
  notes: z.string().optional(),
});

/** `POST /api/instances` (`instantiate`): a new instance of `process`, or, with `instance`, an update. */
export const instantiateRequest = z.union([updateInstanceRequest, createInstanceRequest]);
export type InstantiateRequest = z.output<typeof instantiateRequest>;

/**
 * `POST /api/instances/:id/run` (`run`). Who starts the run is not part of the body: the MCP server
 * names its client in the X-Harness-Client header (clientHeader).
 */
export const runRequest = z.strictObject({
  agent: z.string().min(1),
});
export type RunRequest = z.output<typeof runRequest>;

/**
 * `POST /api/instances/:id/evaluate` (`evaluate`). Problems with `judgments` are
 * `invalid-judgment`. Who judged is not part of the body: the harness records the MCP client that
 * the X-Harness-Client header names, or a user when there is none (the WebUI).
 */
export const evaluateRequest = z.strictObject({
  judgments: z
    .array(
      z.strictObject({
        outcome: z.int().min(0),
        judgment,
        evidence: freeText.min(1, { error: "evidence cannot be empty" }),
        limits: freeText.optional(),
      }),
    )
    .min(1, { error: "judge at least one Outcome" }),
  note: z.string().optional(),
});
export type EvaluateRequest = z.output<typeof evaluateRequest>;

/**
 * The X-Harness-Client header, which the MCP server sends with every request it relays: its
 * client's name and version as JSON, percent-encoded.
 */
export const clientHeader = z.strictObject({
  name: z.string().trim().min(1).max(200),
  version: z.string().max(100),
});

/** `POST /api/wake` (`wake`): the agent to wake, claude-code when none is given. */
export const wakeRequest = z.strictObject({
  agent: z.string().min(1).optional(),
});
export type WakeRequest = z.output<typeof wakeRequest>;

/** `POST /api/open` (`open_ui`). */
export const openRequest = z.strictObject({
  view: z.enum(["network", "dashboard", "instances"]).optional(),
  /** Open the WebUI in a browser on the machine that runs the harness server. */
  open: z.boolean().default(false),
});

/** `POST /api/runs/:id/finish` (`finish_run`). */
export const finishRequest = z.strictObject({
  report: freeText.min(1, { error: "the report cannot be empty" }),
  status: z.enum(["succeeded", "failed"]),
});
export type FinishRequest = z.output<typeof finishRequest>;

/** A query parameter as a non-negative integer. */
const count = z.coerce.number().int().min(0);

/** `GET /api/instances` (`list_instances`). */
export const instancesQuery = z.object({
  process: z.string().min(1).optional(),
  /** A part of an input or output path. */
  path: z.string().min(1).optional(),
  limit: count.min(1).max(200).default(50),
  cursor: z
    .string()
    .regex(/^\d+$/, { error: "use the next value of the previous page" })
    .optional(),
});

/** Epoch milliseconds or an ISO 8601 date. */
const instant = z.string().transform((value, context) => {
  const ms = /^\d+$/.test(value) ? Number(value) : Date.parse(value);
  if (Number.isNaN(ms))
    context.addIssue({ code: "custom", message: "use epoch milliseconds or an ISO 8601 date" });
  return ms;
});

/** `GET /api/artifacts` (`list_artifacts`). */
export const artifactsQuery = z.object({
  type: z.string().min(1).optional(),
  changedSince: instant.optional(),
});

/** `GET /api/runs/:id` (`get_run`). */
export const runQuery = z.object({
  /** How many of the last events to return. */
  tail: count.max(1000).default(50),
  /** Seconds to wait for a running run to end. */
  wait: count.max(300).default(0),
});

/** `GET /api/runs`: newest first, a page at a time. */
export const runsQuery = z.object({
  limit: count.min(1).max(200).default(50),
  cursor: z
    .string()
    .regex(/^\d+$/, { error: "use the next value of the previous page" })
    .optional(),
});

/**
 * `GET /api/assessment` (`get_assessment`). The statistics cover all time by week, or the runs
 * that started and the judgments made since `since`.
 */
export const assessmentQuery = z.object({
  format: z.enum(["json", "markdown"]).default("json"),
  since: instant.optional(),
});

/** Minutes east of UTC, where days and weeks start (the WebUI sends the browser's). */
const utcOffset = z.coerce
  .number()
  .int()
  .min(-14 * 60)
  .max(14 * 60);

/** `GET /api/stats` (the dashboard). */
export const statsQuery = z.object({
  period: z.enum(["7d", "30d", "90d", "all"]).default("30d"),
  granularity: z.enum(["day", "week"]).default("week"),
  process: z.string().min(1).optional(),
  agent: z.string().min(1).optional(),
  tz: utcOffset.optional(),
});

/** `GET /api/skill` (the WebUI): a Process, by id or name. */
export const skillQuery = z.object({
  process: z.string().min(1),
});

/** One line per issue: `<file>: <path>: <message>`. */
export function formatIssues(file: string, error: z.ZodError): string {
  return error.issues
    .map(
      (issue) =>
        `${file}: ${issue.path.length ? issue.path.join(".") : "(top level)"}: ${issue.message}`,
    )
    .join("\n");
}
