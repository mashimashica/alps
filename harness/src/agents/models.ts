/* Model catalogs are supplied by the installed agent, never by a harness-maintained list. */
import { z } from "zod";
import type { AgentModel, AgentSelection } from "../shared/types.ts";
import type { AgentSpec } from "./index.ts";

const name = z.string().min(1).max(200);
const claudeCatalog = z.object({
  models: z.array(
    z.object({
      value: name,
      displayName: name,
      description: z.string().optional(),
      supportedEffortLevels: z.array(name).optional(),
    }),
  ),
});
const codexCatalog = z.object({
  data: z.array(
    z.object({
      model: name,
      displayName: name,
      description: z.string().optional(),
      defaultReasoningEffort: name.optional(),
      supportedReasoningEfforts: z.array(z.object({ reasoningEffort: name })),
    }),
  ),
  nextCursor: z.string().nullish(),
});

export function claudeModels(value: unknown): AgentModel[] {
  return claudeCatalog.parse(value).models.map((model) => ({
    id: model.value,
    label: model.displayName,
    description: model.description ?? "",
    efforts: [...new Set(model.supportedEffortLevels ?? [])],
  }));
}

export function codexModels(value: unknown): { models: AgentModel[]; next: string | null } {
  const page = codexCatalog.parse(value);
  return {
    models: page.data.map((model) => ({
      id: model.model,
      label: model.displayName,
      description: model.description ?? "",
      efforts: [...new Set(model.supportedReasoningEfforts.map((item) => item.reasoningEffort))],
      ...(model.defaultReasoningEffort ? { defaultEffort: model.defaultReasoningEffort } : {}),
    })),
    next: page.nextCursor ?? null,
  };
}

/** Explicit choices replace the workspace's flags; omitted choices keep its defaults. */
export function withAgentSelection(spec: AgentSpec, selection: AgentSelection): AgentSpec {
  if (!selection.model && !selection.effort) return spec;
  const flags = new Set<string>([
    ...(selection.model ? ["--model", ...(spec.format === "codex" ? ["-m"] : [])] : []),
    ...(selection.effort && spec.format === "claude" ? ["--effort"] : []),
  ]);
  const configKey = (value: string): boolean => {
    const key = value.split("=", 1)[0]?.trim();
    return Boolean(
      (selection.model && key === "model") ||
      (selection.effort && key === "model_reasoning_effort"),
    );
  };
  const args: string[] = [];
  for (let i = 0; i < spec.args.length; i++) {
    const arg = spec.args[i]!;
    if (flags.has(arg)) {
      i++;
      continue;
    }
    if ([...flags].some((flag) => arg.startsWith(`${flag}=`))) continue;
    if (spec.format === "codex") {
      if ((arg === "-c" || arg === "--config") && configKey(spec.args[i + 1] ?? "")) {
        i++;
        continue;
      }
      if (arg.startsWith("--config=") && configKey(arg.slice(9))) continue;
    }
    args.push(arg);
  }
  const overrides = [
    ...(selection.model ? ["--model", selection.model] : []),
    ...(selection.effort
      ? spec.format === "claude"
        ? ["--effort", selection.effort]
        : ["-c", `model_reasoning_effort=${JSON.stringify(selection.effort)}`]
      : []),
  ];
  // Keep options before the positional prompt, including when it starts with a dash.
  const prompt = args.findIndex((arg) =>
    spec.format === "claude"
      ? arg === "-p" || arg === "--print"
      : arg === "{prompt}" || arg === "-",
  );
  args.splice(prompt < 0 ? args.length : prompt, 0, ...overrides);
  return { ...spec, args };
}
