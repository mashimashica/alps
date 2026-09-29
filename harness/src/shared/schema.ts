/*
 * zod schemas for the files the harness reads. Each schema validates the file and
 * normalizes YAML scalars, so the loader works with one shape per file.
 */

import { z } from "zod";

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
  guidance: textList.optional(),
  schedules: z.array(z.looseObject({ cron: text, agent: text })).optional(),
});

export type HarnessConfig = z.output<typeof harnessConfigSchema>;

/** One line per issue: `<file>: <path>: <message>`. */
export function formatIssues(file: string, error: z.ZodError): string {
  return error.issues
    .map(
      (issue) =>
        `${file}: ${issue.path.length ? issue.path.join(".") : "(top level)"}: ${issue.message}`,
    )
    .join("\n");
}
