/*
 * Provenance: a run's outputs are the Artifacts that its output locations gained or changed while
 * it ran. The harness takes a snapshot of the locations when the run starts and when it ends.
 */

import type { RunOutput } from "../shared/types.ts";

/** Each path found in the output locations, with its Artifact type and the signature of its state. */
export type OutputSnapshot = Map<string, { type: string; signature: string }>;

/**
 * The outputs of a run: the paths that are new or whose signature changed between the snapshots.
 * A path that disappeared is not an output.
 */
export function diffOutputs(before: OutputSnapshot, after: OutputSnapshot): RunOutput[] {
  const outputs: RunOutput[] = [];
  for (const [path, now] of after) {
    const was = before.get(path);
    if (was?.signature === now.signature) continue;
    outputs.push({ type: now.type, path, change: was ? "modified" : "created" });
  }
  return outputs;
}
