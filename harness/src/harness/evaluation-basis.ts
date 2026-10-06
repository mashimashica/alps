import { createHash } from "node:crypto";
import type {
  EvaluationBasis,
  EvaluationContext,
  Instance,
  ModelDescription,
} from "../shared/types.ts";

export function evaluationBasis(instance: Instance, model: ModelDescription): EvaluationBasis {
  const process = model.processes.find((item) => item.id === instance.process);
  return {
    modelRevision: model.revision,
    process: {
      id: instance.process,
      name: process?.name ?? instance.process,
      purpose: process?.purpose ?? "",
      outcomes: [...(process?.outcomes ?? [])],
    },
    criteria: instance.criteria.map((item) => ({ ...item })),
    inputs: Object.fromEntries(
      Object.entries(instance.inputs).map(([key, paths]) => [key, [...paths]]),
    ),
    outputs: { ...instance.outputs },
  };
}

export function evaluationContext(
  instance: Instance,
  model: ModelDescription,
): EvaluationContext | null {
  const runId = instance.runs.at(-1);
  if (!runId) return null;
  return {
    runId,
    fingerprint: createHash("sha256")
      .update(
        JSON.stringify({
          basis: evaluationBasis(instance, model),
          previous: instance.evaluation,
        }),
      )
      .digest("hex"),
  };
}

export function definitionChanged(instance: Instance, model: ModelDescription): boolean {
  const previous = instance.evaluation?.basis;
  if (!previous) return false;
  const current = evaluationBasis(instance, model);
  // Changes elsewhere in the model do not invalidate this application's criteria.
  return (
    JSON.stringify({ ...previous, modelRevision: "" }) !==
    JSON.stringify({ ...current, modelRevision: "" })
  );
}
