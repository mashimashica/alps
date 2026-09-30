/*
 * Provenance: a run's outputs are the Artifacts that its output locations gained or changed while
 * it ran. The harness takes a snapshot of the locations when the run starts and when it ends. Runs
 * that run at the same time may change the same locations: only then, what one of them changed is
 * kept out of the others' outputs where their locations and inputs tell them apart, and marked as
 * shared where they do not.
 */

import { compilePattern } from "../model/index.ts";
import type { RunOutput } from "../shared/types.ts";

/** Each path found in the output locations, with its Artifact type and the signature of its state. */
export type OutputSnapshot = Map<string, { type: string; signature: string }>;

/**
 * Where a run's outputs of one Artifact type are looked for: the instance's concrete location (a
 * file or a directory, in `paths`), or else the patterns within which the agent decides where to
 * put them (the instance's own pattern, or the type's location patterns when the instance leaves
 * the location open).
 */
export interface OutputLocation {
  type: string;
  patterns: string[];
  paths: string[];
}

/**
 * The changes in the output locations: the paths that are new or whose signature changed between
 * the snapshots. A path that disappeared is not an output.
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

const segmentRegex = (segment: string): RegExp =>
  new RegExp(
    `^${segment
      .split("*")
      .map((part) => part.replace(/[.+?^$(){}|[\]\\]/g, "\\$&"))
      .join("[^/]*")}$`,
  );

/**
 * The values that a path gives to the wildcard directories of a location pattern, by their index,
 * read from the start as far as the path agrees with the pattern. For the Change brief's pattern,
 * whose third directory is `*`, the input docs/changes/CHG-003/stakeholders.md gives that directory
 * the value CHG-003. A `*` directory takes one directory (`CHG-*` one that it matches); a `**`
 * directory takes all the rest when it is the pattern's last directory, and otherwise ends the
 * reading, since where it ends is not known. The last segment, an Artifact's own name, is not read.
 * Empty when the path gives no wildcard a value.
 */
export function wildcardValues(pattern: string, path: string): Map<number, string> {
  const body = pattern
    .replace(/\\/g, "/")
    .replace(/^(?:\.\/)+/, "")
    .replace(/\/+$/, "");
  const directories = body.split("/").slice(0, -1);
  const given = path.replace(/\/+$/, "").split("/").slice(0, -1);
  const values = new Map<number, string>();
  for (let i = 0; i < directories.length && i < given.length; i++) {
    const segment = directories[i] ?? "";
    const value = given[i] ?? "";
    if (segment === "**") {
      if (i === directories.length - 1) values.set(i, given.slice(i).join("/"));
      break;
    }
    if (!segment.includes("*")) {
      if (segment !== value) break;
      continue;
    }
    if (segment.includes("**") || !segmentRegex(segment).test(value)) break;
    values.set(i, value);
  }
  return values;
}

/** What tells which of the changes in a run's output locations are the run's own. */
export interface Attribution {
  locations: readonly OutputLocation[];
  /** What changed in the locations while the run ran (diffOutputs). */
  changes: readonly RunOutput[];
  /** The concrete paths of the run's inputs and controls. */
  inputs: readonly string[];
  /** The concrete output locations of the runs that ran at the same time as this one. */
  claimed: readonly string[];
  /**
   * No run ran at the same time as this one: the inputs and `claimed` then narrow nothing, and
   * every change within the patterns is the run's output.
   */
  alone?: boolean;
}

/**
 * The run's outputs among the changes in its output locations. At a concrete location, only the
 * change of that file or directory is an output. Within patterns, a run that ran alone has all the
 * changes; runs that ran at the same time do not take each other's outputs:
 * - a change that one of them names as its concrete location (or that lies inside one) is not an
 *   output;
 * - of the rest, the ones whose directories agree with the values that an input of the run gives
 *   the pattern's wildcards (wildcardValues) are preferred: once a change of a type agrees with an
 *   input, the changes of that type that disagree with every input that gives values are left
 *   out. When none agrees, or no input gives values, all of them are kept.
 */
export function attributeOutputs(attribution: Attribution): RunOutput[] {
  const { locations, changes, inputs, claimed, alone = false } = attribution;
  const concrete = new Set(locations.flatMap((location) => location.paths));
  const isClaimed = (p: string): boolean =>
    claimed.some((location) => p === location || p.startsWith(`${location}/`));
  const readings = new Map(
    locations.map((location) => [
      location.type,
      location.patterns.map((pattern) => ({
        pattern,
        regex: compilePattern(pattern).regex,
        given: inputs.map((p) => wildcardValues(pattern, p)).filter((values) => values.size > 0),
      })),
    ]),
  );
  /**
   * Whether a change within the patterns agrees with an input, disagrees with every input that
   * gives values, or neither; "outside" when none of its type's patterns holds it.
   */
  const standing = (change: RunOutput): "agrees" | "disagrees" | "open" | "outside" => {
    const matched = (readings.get(change.type) ?? []).filter((r) => r.regex.test(change.path));
    if (matched.length === 0) return "outside";
    let open = false;
    for (const reading of matched) {
      if (reading.given.length === 0) {
        open = true;
        continue;
      }
      const own = wildcardValues(reading.pattern, change.path);
      if (reading.given.some((values) => [...values].every(([i, v]) => own.get(i) === v)))
        return "agrees";
    }
    return open ? "open" : "disagrees";
  };

  const candidates = changes.flatMap((change) => {
    if (concrete.has(change.path)) return [{ change, mine: true, standing: "agrees" as const }];
    const found = !alone && isClaimed(change.path) ? "outside" : standing(change);
    return found === "outside" ? [] : [{ change, mine: false, standing: found }];
  });
  if (alone) return candidates.map((c) => c.change);
  const preferred = new Set(
    candidates.filter((c) => !c.mine && c.standing === "agrees").map((c) => c.change.type),
  );
  return candidates
    .filter((c) => c.mine || c.standing !== "disagrees" || !preferred.has(c.change.type))
    .map((c) => c.change);
}

const markedWith = (output: RunOutput, run: string): RunOutput =>
  output.sharedWith?.includes(run)
    ? output
    : { ...output, sharedWith: [...(output.sharedWith ?? []), run] };

/**
 * Marks the outputs that a run holds together with runs that ran at the same time and have ended:
 * each of them found the change, and which one made it cannot be told. Returns the run's outputs,
 * and the new outputs of each of those runs that holds one of them, each marked with the other
 * run's id (`sharedWith`).
 */
export function shareOutputs(
  run: { id: string; outputs: readonly RunOutput[] },
  others: readonly { id: string; outputs: readonly RunOutput[] }[],
): { outputs: RunOutput[]; others: Map<string, RunOutput[]> } {
  let outputs = [...run.outputs];
  const changed = new Map<string, RunOutput[]>();
  for (const other of others) {
    if (other.id === run.id) continue;
    const theirs = new Set(other.outputs.map((output) => output.path));
    if (!outputs.some((output) => theirs.has(output.path))) continue;
    const mine = new Set(outputs.map((output) => output.path));
    outputs = outputs.map((output) =>
      theirs.has(output.path) ? markedWith(output, other.id) : output,
    );
    changed.set(
      other.id,
      other.outputs.map((output) => (mine.has(output.path) ? markedWith(output, run.id) : output)),
    );
  }
  return { outputs, others: changed };
}
