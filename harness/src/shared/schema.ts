/*
 * zod schemas for the files the harness reads and the requests its API accepts. The schemas of
 * the configuration and the model normalize YAML scalars, so the loader works with one shape per
 * file; the schemas of the records are typed against shared/types.ts, which defines their shapes.
 */

import { z } from "zod";
import { MAX_ATTACHMENTS, MAX_REQUEST_LENGTH } from "./requests.ts";
import { cronProblem } from "./cron.ts";
import type {
  Assessment,
  Evaluation,
  Evidence,
  Instance,
  Judge,
  Run,
  RunObservation,
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

/** One text or a list of texts for writes. Missing preserves the existing value; null clears it. */
const optionalTextList = z
  .union([text, z.array(text)])
  .nullish()
  .transform((value) => {
    if (value === undefined) return undefined;
    if (value === null) return [];
    return (Array.isArray(value) ? value : [value]).filter(Boolean);
  });

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
    scope: text.optional(),
    activities: z
      .array(
        z.looseObject({
          name: text,
          tasks: textList,
          supportsOutcomes: textList,
        }),
      )
      .nullish()
      .transform((value) => value ?? []),
    tasks: textList,
    constraints: textList,
    enablers: textList,
    entryCriteria: textList,
    exitCriteria: textList,
    references: textList,
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
export const processModelFileSchema = z
  .looseObject({
    name: text.optional(),
    description: text.optional(),
    draft: z.boolean().optional(),
    processes: z.array(processEntry),
    artifacts: z
      .array(artifactEntry)
      .nullish()
      .transform((value) => value ?? []),
  })
  .superRefine((model, context) => {
    if (model.processes.length === 0 && model.draft !== true)
      context.addIssue({
        code: "custom",
        path: ["processes"],
        message: "list at least one process under processes, or mark the model with draft: true",
      });
  });

export type ProcessModelFile = z.output<typeof processModelFileSchema>;

/** A Process entry accepted by the local model authoring endpoint. */
const modelWriteProcess = z
  .looseObject({
    id: text.optional(),
    name: text,
    purpose: text.optional(),
    outcomes: optionalTextList,
    scope: text.optional(),
    activities: z
      .array(
        z.looseObject({
          name: text,
          tasks: optionalTextList,
          supportsOutcomes: optionalTextList,
        }),
      )
      .nullish()
      .transform((value) => (value === undefined ? undefined : (value ?? []))),
    tasks: optionalTextList,
    constraints: optionalTextList,
    enablers: optionalTextList,
    entryCriteria: optionalTextList,
    exitCriteria: optionalTextList,
    references: optionalTextList,
    inputs: optionalTextList,
    controls: optionalTextList,
    outputs: optionalTextList,
    skill: text.nullish(),
  })
  .refine((entry) => Boolean(entry.name || entry.id), { error: "a process needs a name" });

/** An Artifact type entry accepted by the local model authoring endpoint. */
const modelWriteArtifact = z.preprocess(
  (value) => (typeof value === "string" || typeof value === "number" ? { name: value } : value),
  z
    .looseObject({
      id: text.optional(),
      name: text,
      description: text.optional(),
      kind: artifactKind.nullish(),
      paths: optionalTextList,
    })
    .refine((entry) => Boolean(entry.name || entry.id), { error: "an artifact type needs a name" }),
);

/** POST /api/model: replace the process-model.yaml meaning file through the local UI. */
export const updateModelRequest = z
  .looseObject({
    expectedRevision: z.string().min(1, { error: "expectedRevision is required" }),
    name: text.pipe(z.string().min(1, { error: "name the model" })),
    description: text.optional(),
    draft: z.boolean().optional(),
    processes: z.array(modelWriteProcess),
    artifacts: z
      .array(modelWriteArtifact)
      .nullish()
      .transform((value) => value ?? []),
  })
  .superRefine((model, context) => {
    if (model.processes.length === 0 && model.draft !== true)
      context.addIssue({
        code: "custom",
        path: ["processes"],
        message: "list at least one process under processes, or mark the model with draft: true",
      });
  });

export type UpdateModelRequest = z.output<typeof updateModelRequest>;

const designId = z.string().regex(/^[A-Za-z0-9_-]{8,80}$/, {
  error: "use the id returned when the design session was created",
});

const designReferencePath = text.pipe(z.string().min(1).max(500));

const designSkillFileDraft = z.looseObject({
  path: text.pipe(z.string().min(1).max(500)),
  content: z.string().max(300_000),
  expectedSha256: z.string().nullable().optional(),
});

export const designProposalRequest = z.looseObject({
  summary: text.pipe(z.string().min(1).max(4000)),
  model: updateModelRequest,
  skillFiles: z
    .array(designSkillFileDraft)
    .max(200)
    .nullish()
    .transform((value) => value ?? []),
});

/** `POST /api/designs`: start an AI-assisted Process Description design session. */
export const createDesignRequest = z.looseObject({
  id: designId.optional(),
  workIds: z
    .array(z.string().regex(/^(launch|run|instance|design)-[A-Za-z0-9_-]+$/))
    .max(100)
    .optional(),
  method: z.enum(["desktop", "cli"]).default("desktop"),
  autoSave: z.boolean().default(true),
  request: text.pipe(z.string().min(1).max(MAX_REQUEST_LENGTH)),
  process: text.optional(),
  references: z
    .array(designReferencePath)
    .max(MAX_ATTACHMENTS)
    .nullish()
    .transform((value) => value ?? []),
  agent: text.optional(),
  model: z.string().min(1).optional(),
  effort: z.string().min(1).optional(),
});

export type CreateDesignRequest = z.output<typeof createDesignRequest>;

export const designOpenRequest = z.looseObject({});
export type DesignOpenRequest = z.output<typeof designOpenRequest>;

export const designClaimRequest = z.looseObject({
  workspace: z.string().min(1).max(4000).optional(),
  sessionId: z.string().min(1).max(500).optional(),
  conversationUrl: z.string().min(1).max(2000).optional(),
});

export type DesignClaimRequest = z.output<typeof designClaimRequest>;

export const designSubmitQuestionsRequest = z.looseObject({
  message: text.pipe(z.string().min(1).max(MAX_REQUEST_LENGTH)),
  questions: z
    .array(text.pipe(z.string().min(1).max(1000)))
    .max(20)
    .optional(),
});

export type DesignSubmitQuestionsRequest = z.output<typeof designSubmitQuestionsRequest>;

export const designSubmitProposalRequest = z.looseObject({
  message: text.pipe(z.string().min(1).max(MAX_REQUEST_LENGTH)).optional(),
  proposal: designProposalRequest,
});

export type DesignSubmitProposalRequest = z.output<typeof designSubmitProposalRequest>;

/** `POST /api/designs/:id/messages`: add the person's answer or refinement and resume generation. */
export const designMessageRequest = z.looseObject({
  text: text.pipe(z.string().min(1).max(MAX_REQUEST_LENGTH)),
  proposal: designProposalRequest.optional(),
});

export type DesignMessageRequest = z.output<typeof designMessageRequest>;

/** `POST /api/designs/:id/apply`: apply the ready or edited model proposal. */
export const designApplyRequest = z.looseObject({
  proposal: designProposalRequest.optional(),
});

export type DesignApplyRequest = z.output<typeof designApplyRequest>;

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
  /**
   * Where the WebUI saves the files attached to a request, relative to the workspace (inbox/ by
   * default). Whether it stays inside the workspace and outside .alps-harness/ depends on the
   * workspace: loading checks it (model/load.ts).
   */
  attachments: text.optional(),
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
const runKind = z.enum(["process", "wake", "assess"]);
const period = z.enum(["7d", "30d", "90d", "all"]);
const judgment = z.enum(["achieved", "not-achieved", "unverified"]);
const judge: z.ZodType<Judge> = z.union([
  z.object({ kind: z.literal("user") }),
  z.object({ kind: z.literal("agent"), id: z.string().min(1), self: z.boolean().optional() }),
]);

const usage: z.ZodType<Usage> = z.object({
  costUsd: z.number().nullable(),
  turns: z.number().nullable(),
  inputTokens: z.number().nullable(),
  // Runs recorded before the harness read the cached tokens have none.
  cachedInputTokens: z.number().nullable().default(null),
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
  // Records written before the harness told concurrent runs apart have none.
  sharedWith: z.array(z.string()).optional(),
});
const observationKind = z.enum([
  "launch.submitted",
  "launch.claimed",
  "run.started",
  "run.finished",
  "run.disconnected",
  "run.reconnected",
  "tool.called",
  "telemetry.export",
]);
const observationCoverage = z.enum(["observed", "reference-only", "unavailable", "unverified"]);
const observationAttributes = z
  .record(z.string(), z.union([z.string(), z.number(), z.boolean()]))
  .refine((value) => Object.keys(value).length <= 20, {
    message: "at most 20 attributes",
  });
const runObservation: z.ZodType<RunObservation> = z.object({
  id: z.string().min(1),
  at: epochMs,
  source: z.enum(["alps", "otel", "host"]),
  kind: observationKind,
  coverage: observationCoverage,
  message: z.string().max(1000),
  trace: z.object({ traceId: z.string(), spanId: z.string() }).optional(),
  attributes: observationAttributes.optional(),
});
const gitInfo = z.object({ head: z.string(), dirty: z.boolean() }).nullable();
const skillUsed = z.object({ path: z.string(), sha256: z.string().nullable() }).nullable();

const evaluation: z.ZodType<Evaluation> = z.object({
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
  basis: z
    .object({
      modelRevision: z.string(),
      process: z.object({
        id: z.string(),
        name: z.string(),
        purpose: z.string(),
        outcomes: z.array(z.string()),
      }),
      criteria: z.array(
        z.object({ outcome: z.int().min(0), statement: z.string(), checks: z.string().optional() }),
      ),
      inputs: z.record(z.string(), z.array(z.string())),
      outputs: z.record(z.string(), z.string().nullable()),
    })
    .optional(),
});

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
  evaluation: evaluation.nullable(),
  // Instances evaluated before the harness kept the evaluations that later ones replaced have none.
  evaluations: z.array(evaluation).optional(),
  // Instances recorded before the harness kept what made them have none.
  createdBy: z.object({ run: z.string() }).nullable().optional(),
});

const runSummary: z.ZodType<RunSummary> = z.object({
  id: z.string(),
  kind: runKind,
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
  // State files written before the harness kept assessments have none.
  latestAssessment: z.string().nullable().default(null),
  runs: z.record(z.string(), runSummary),
});

/** What an assessment is asked to read (`Run.scope`, `Assessment.scope`). */
const assessScope = z.object({
  period: period.optional(),
  process: z.string().optional(),
  agent: z.string().optional(),
  request: z.string().optional(),
});

/** `.alps-harness/runs/<id>.json`. */
export const runRecordSchema: z.ZodType<Run, unknown> = z.object({
  id: z.string(),
  kind: runKind,
  instance: z.string().nullable(),
  process: z.string().nullable(),
  agent: z.string(),
  selection: z.object({ model: z.string().optional(), effort: z.string().optional() }).optional(),
  status: runStatus,
  createdAt: epochMs,
  startedAt: epochMs,
  endedAt: epochMs.nullable(),
  exitCode: z.number().nullable(),
  error: z.string().nullable(),
  // Records written before the harness kept the key of its error have none.
  errorKey: z.string().optional(),
  errorArgs: z.record(z.string(), z.union([z.string(), z.number(), z.boolean()])).optional(),
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
  observations: z.array(runObservation).optional(),
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
  execution: z
    .object({
      method: z.enum(["cli", "desktop", "terminal"]),
      provider: z.enum(["claude", "codex"]).optional(),
      launchId: z.string().optional(),
      workContext: z.string().optional(),
      sessionId: z.string().min(1).max(500).optional(),
      session: z
        .object({
          id: z.string().min(1).max(500),
          source: z.enum(["claim", "agent-output", "resume"]),
          capturedAt: epochMs,
          coverage: z.enum(["connected", "reference-only", "disconnected", "unverified"]),
          note: z.string().max(1000).optional(),
        })
        .optional(),
      resumedFrom: z.string().optional(),
      disconnectedAt: epochMs.optional(),
      attributionUnknown: z.boolean().optional(),
    })
    .optional(),
  git: gitInfo,
  skill: skillUsed,
  started: z.array(z.string()).optional(),
  // Wake runs recorded before the harness kept what a wake was asked have none of these.
  request: z.string().nullable().optional(),
  attachments: z.array(z.string()).optional(),
  processes: z.array(z.string()).optional(),
  runs: z.enum(["run", "plan"]).optional(),
  scope: assessScope.optional(),
});

/** A cut of the statistics that evidence names: the dashboard's filter. */
const statCut = z.strictObject({
  period: period.optional(),
  granularity: z.enum(["day", "week"]).optional(),
  process: z.string().min(1).optional(),
  agent: z.string().min(1).optional(),
});

/** A record that an assessment item rests on: one key, which says what kind of record it is. */
const evidence: z.ZodType<Evidence> = z.union([
  z.strictObject({ run: z.string().min(1) }),
  z.strictObject({ instance: z.string().min(1) }),
  z.strictObject({ evaluation: z.string().min(1) }),
  z.strictObject({ observation: z.string().min(1) }),
  z.strictObject({ stat: z.strictObject({ filter: statCut, metric: z.string().min(1) }) }),
  z.strictObject({ log: z.strictObject({ run: z.string().min(1), n: z.int().min(1) }) }),
  z.strictObject({ path: z.string().min(1) }),
]);

const itemKind = z.enum(["description", "configuration", "operation", "unverified"]);
const itemSubject = z.strictObject({
  process: z.string().min(1).optional(),
  artifact: z.string().min(1).optional(),
  agent: z.string().min(1).optional(),
  guidance: z.string().min(1).optional(),
  instance: z.string().min(1).optional(),
});

/** `.alps-harness/assessments/<run>.json`. */
export const assessmentRecordSchema: z.ZodType<Assessment> = z.object({
  id: z.string(),
  runId: z.string(),
  at: epochMs,
  agent: z.string(),
  scope: assessScope,
  summary: z.string(),
  items: z.array(
    z.object({
      n: z.int().min(1),
      kind: itemKind,
      subject: itemSubject,
      statement: z.string(),
      evidence: z.array(evidence),
      limits: z.string().optional(),
    }),
  ),
  reviews: z.array(
    z.object({
      n: z.int().min(1),
      judgment: z.enum(["adopted", "held", "rejected"]),
      note: z.string().optional(),
      by: z.object({ kind: z.literal("user") }),
      at: epochMs,
    }),
  ),
});

/** A run's usage in harness 0.8, which left out what an agent did not report (Codex's turns). */
const usageV1: z.ZodType<Usage, unknown> = z.object({
  costUsd: z.number().nullish().default(null),
  turns: z.number().nullish().default(null),
  inputTokens: z.number().nullish().default(null),
  cachedInputTokens: z.number().nullish().default(null),
  outputTokens: z.number().nullish().default(null),
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
        usage: usageV1.nullish().default(null),
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
const agentSelection = {
  model: z
    .string()
    .trim()
    .min(1)
    .max(200)
    .regex(/^[a-zA-Z0-9][^\s]*$/)
    .optional(),
  effort: z
    .string()
    .min(1)
    .max(40)
    .regex(/^[a-z][a-z0-9_-]*$/)
    .optional(),
};

export const runRequest = z.strictObject({
  ...agentSelection,
  agent: z.string().min(1),
});
export type RunRequest = z.output<typeof runRequest>;

/**
 * `POST /api/instances/:id/evaluate` (`evaluate`). Problems with `judgments` are
 * `invalid-judgment`. Who judged is not part of the body: the harness records the MCP client that
 * the X-Harness-Client header names, or a user when there is none (the WebUI).
 */
export const evaluateRequest = z.strictObject({
  expected: z
    .strictObject({ runId: z.string().min(1), fingerprint: z.string().regex(/^[a-f0-9]{64}$/) })
    .optional(),
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

/**
 * `POST /api/wake` (`wake`): the agent to wake, claude-code when none is given, and what the wake
 * is asked, if anything: the request in free text (the requester's instruction), the workspace
 * paths it attaches, the Processes (id or name) that the plan must include, and whether the agent
 * starts the runs it plans (`run`, the default) or only instantiates them (`plan`). The request is
 * kept, in the record and in the prompt alike, without the white space around it and with its
 * lines ending in \n; the lines themselves are as given.
 */
export const wakeRequest = z.strictObject({
  ...agentSelection,
  agent: z.string().min(1).optional(),
  request: freeText
    .max(MAX_REQUEST_LENGTH, {
      error: `the request is longer than ${MAX_REQUEST_LENGTH} characters; attach long text as a file`,
    })
    .transform((text) => text.replace(/\r\n?/g, "\n"))
    .optional(),
  attachments: z
    .array(z.string())
    .max(MAX_ATTACHMENTS, { error: `a request attaches at most ${MAX_ATTACHMENTS} paths` })
    .default([]),
  processes: z.array(z.string().min(1)).default([]),
  runs: z.enum(["run", "plan"]).default("run"),
});
export type WakeRequest = z.output<typeof wakeRequest>;

/**
 * `POST /api/assess` (`assess`): the agent that assesses (claude-code when none is given, codex, or
 * self for the calling session), what it reads (a period, a Process by id or name, an agent's
 * runs), and from what point of view (`request`, kept as the wake's request is).
 */
export const assessRequest = z.strictObject({
  ...agentSelection,
  agent: z.string().min(1).optional(),
  scope: z
    .strictObject({
      period: period.optional(),
      process: z.string().min(1).optional(),
      agent: z.string().min(1).optional(),
    })
    .default({}),
  request: freeText
    .max(MAX_REQUEST_LENGTH, {
      error: `the request is longer than ${MAX_REQUEST_LENGTH} characters`,
    })
    .transform((text) => text.replace(/\r\n?/g, "\n"))
    .optional(),
});
export type AssessRequest = z.output<typeof assessRequest>;

/**
 * `POST /api/assessments` (`record_assessment`): the result of the assessment run that the caller
 * performs. The harness numbers the items from 1; whether each rests on evidence that exists is
 * checked there (an item without evidence is refused unless it is unverified).
 */
export const recordAssessmentRequest = z.strictObject({
  summary: freeText.min(1, { error: "the summary cannot be empty" }),
  items: z.array(
    z.strictObject({
      kind: itemKind,
      subject: itemSubject.default({}),
      statement: freeText.min(1, { error: "an item needs a statement" }),
      evidence: z.array(evidence).default([]),
      limits: freeText.optional(),
    }),
  ),
});
export type RecordAssessmentRequest = z.output<typeof recordAssessmentRequest>;

/** `POST /api/assessments/:id/items/:n/review` (the WebUI): a person's review of one item. */
export const reviewRequest = z.strictObject({
  judgment: z.enum(["adopted", "held", "rejected"]),
  note: freeText.optional(),
});
export type ReviewRequest = z.output<typeof reviewRequest>;

/** `POST /api/open` (`open_ui`). */
export const openRequest = z.strictObject({
  view: z.enum(["network", "dashboard", "instances", "activity"]).optional(),
  /** Open the WebUI in a browser on the machine that runs the harness server. */
  open: z.boolean().default(false),
});

/** `POST /api/ui` (trusted local product shell): attach a UI bundle to an existing daemon. */
export const installUiRequest = z.strictObject({
  entry: z.string().min(1).max(2000),
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

/** The longest that `get_run` waits for a running run to end, in seconds. */
export const MAX_WAIT_SECONDS = 300;

/** `GET /api/runs/:id` (`get_run`). */
export const runQuery = z.object({
  /** How many of the last events to return. */
  tail: count.max(1000).default(50),
  /** Seconds to wait for a running run to end. */
  wait: count.max(MAX_WAIT_SECONDS).default(0),
});

/**
 * `GET /api/runs` (`list_runs`): newest first, a page at a time; with a Process (id or name), an
 * agent, a status, a kind, or the runs that started at or after `since`.
 */
export const runsQuery = z.object({
  process: z.string().min(1).optional(),
  agent: z.string().min(1).optional(),
  status: runStatus.optional(),
  kind: runKind.optional(),
  since: instant.optional(),
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

/** A person's delivery intent, identified before submitting so retries cannot duplicate work. */
export const launchRequest = z
  .strictObject({
    id: z.string().uuid(),
    workIds: z
      .array(z.string().regex(/^(launch|run|instance|design)-[A-Za-z0-9_-]+$/))
      .max(100)
      .optional(),
    kind: z.enum(["process", "wake", "assess"]),
    agent: z.string().min(1),
    method: z.enum(["cli", "desktop", "terminal"]),
    instance: z.string().min(1).optional(),
    request: z.string().max(20000).optional(),
    attachments: z.array(z.string()).max(10).optional(),
    processes: z.array(z.string()).optional(),
    runs: z.enum(["run", "plan"]).optional(),
    scope: assessScope.optional(),
    model: z.string().min(1).optional(),
    effort: z.string().min(1).optional(),
    resumedFrom: z
      .string()
      .regex(/^r\d+$/)
      .optional(),
    replacesLaunch: z.string().uuid().optional(),
  })
  .superRefine((value, ctx) => {
    if (value.kind === "wake" && !value.request?.trim())
      ctx.addIssue({ code: "custom", path: ["request"], message: "write the request" });
    if (value.kind !== "wake" && (value.processes || value.attachments || value.runs))
      ctx.addIssue({
        code: "custom",
        path: ["kind"],
        message: "processes, attachments and planning scope are for orchestration",
      });
    if (value.kind !== "assess" && value.scope)
      ctx.addIssue({
        code: "custom",
        path: ["scope"],
        message: "analysis scope is for assessments",
      });
    if (value.kind !== "process" && value.instance)
      ctx.addIssue({
        code: "custom",
        path: ["instance"],
        message: "only process runs have an instance",
      });
    if (value.resumedFrom && value.method !== "terminal")
      ctx.addIssue({
        code: "custom",
        path: ["resumedFrom"],
        message: "resume through the terminal",
      });
    if (value.kind === "process" && !value.instance)
      ctx.addIssue({ code: "custom", path: ["instance"], message: "name the instance" });
    if (value.method !== "cli" && (value.model || value.effort))
      ctx.addIssue({
        code: "custom",
        path: ["method"],
        message: "set model and effort in the application or terminal",
      });
    if (value.method === "terminal" && !value.resumedFrom)
      ctx.addIssue({
        code: "custom",
        path: ["resumedFrom"],
        message: "name the conversation to resume",
      });
  });
export const claimLaunchRequest = z.strictObject({
  workspace: z.string().min(1).max(4000).optional(),
  sessionId: z.string().min(1).max(500).optional(),
});
export const recordObservationRequest = z.strictObject({
  source: z.enum(["otel", "host"]).default("host"),
  kind: observationKind.default("telemetry.export"),
  coverage: observationCoverage.default("reference-only"),
  message: z.string().trim().min(1).max(1000),
  trace: z
    .strictObject({
      traceId: z.string().min(1).max(64),
      spanId: z.string().min(1).max(32),
    })
    .optional(),
  attributes: observationAttributes.optional(),
});
export type RecordObservationRequest = z.output<typeof recordObservationRequest>;

/** Private snapshot required to attribute an externally performed run after server restart. */
export const externalTracking = z.strictObject({
  locations: z.array(
    z.strictObject({ type: z.string(), patterns: z.array(z.string()), paths: z.array(z.string()) }),
  ),
  before: z.array(
    z.tuple([z.string(), z.strictObject({ type: z.string(), signature: z.string() })]),
  ),
  overlapping: z.array(z.string().regex(/^r\d+$/)),
});
