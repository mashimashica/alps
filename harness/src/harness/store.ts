/*
 * The records in .alps-harness/: state.json (instances, provenance, the sequence, run summaries),
 * runs/<id>.json (each run in full, prompt included), runs/<id>.jsonl (its events),
 * runs/<id>.raw.log (the agent's own output), and, while a wake run of Claude Code runs,
 * runs/<id>.mcp.json (the harness's MCP server for it). Files are replaced atomically (written
 * aside, then renamed). Reading never writes: what loading changes (a conversion from version 1,
 * runs that were running when the last server stopped) is written by persist() once the server
 * owns the workspace.
 */

import fs from "node:fs";
import path from "node:path";
import { HARNESS_DIR } from "../model/index.ts";
import {
  formatIssues,
  runRecordSchema,
  stateFileSchema,
  stateFileV1Schema,
} from "../shared/schema.ts";
import type { Run, RunEvent, RunSummary, StateFile } from "../shared/types.ts";
import { INTERRUPTED_ERROR, migrateStateV1, runError } from "./migrate.ts";

export const STATE_VERSION = 2;

/** state.json cannot be used: it is not JSON, does not fit its schema, or is from a newer harness. */
export class StateError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "StateError";
  }
}

export const recordPaths = (root: string) => {
  const dir = path.join(root, HARNESS_DIR);
  return {
    dir,
    state: path.join(dir, "state.json"),
    /** Where a converted version 1 state.json is kept. */
    stateV1: path.join(dir, "state.v1.json"),
    runs: path.join(dir, "runs"),
    run: (id: string) => path.join(dir, "runs", `${id}.json`),
    events: (id: string) => path.join(dir, "runs", `${id}.jsonl`),
    raw: (id: string) => path.join(dir, "runs", `${id}.raw.log`),
    /** A wake run's --mcp-config for Claude Code, while the run runs. */
    mcpConfig: (id: string) => path.join(dir, "runs", `${id}.mcp.json`),
  };
};

export const emptyState = (): StateFile => ({
  schemaVersion: STATE_VERSION,
  instances: {},
  provenance: {},
  seq: 0,
  lastWakeAt: null,
  runs: {},
});

export const summaryOf = (run: Run): RunSummary => ({
  id: run.id,
  kind: run.kind,
  instance: run.instance,
  status: run.status,
  startedAt: run.startedAt,
  endedAt: run.endedAt,
});

export interface LoadedRecords {
  state: StateFile;
  runs: Map<string, Run>;
  /** Runs whose record is missing or unreadable, with why. */
  unreadable: { id: string; reason: string }[];
  /** What loading changed and persist() writes. */
  changes: {
    /** The text of a version 1 state.json that was converted. */
    convertedV1: string | null;
    /** Runs to write: converted ones and ones marked interrupted. */
    runs: Run[];
    /** Whether state.json itself changed. */
    state: boolean;
  };
}

/** Writes a file by writing it aside and renaming it over the old one. */
export function writeAtomic(file: string, text: string): void {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const aside = `${file}.${process.pid}.tmp`;
  fs.writeFileSync(aside, text);
  fs.renameSync(aside, file);
}

const readJson = (file: string): { ok: true; value: unknown } | { ok: false; reason: string } => {
  let text: string;
  try {
    text = fs.readFileSync(file, "utf8");
  } catch (error) {
    return { ok: false, reason: (error as Error).message };
  }
  try {
    return { ok: true, value: JSON.parse(text) as unknown };
  } catch (error) {
    return { ok: false, reason: `not valid JSON (${(error as Error).message})` };
  }
};

function readRunRecords(
  root: string,
  state: StateFile,
): Pick<LoadedRecords, "runs" | "unreadable"> {
  const paths = recordPaths(root);
  const runs = new Map<string, Run>();
  const unreadable: LoadedRecords["unreadable"] = [];
  for (const id of Object.keys(state.runs)) {
    const read = readJson(paths.run(id));
    if (!read.ok) {
      unreadable.push({ id, reason: read.reason });
      continue;
    }
    const parsed = runRecordSchema.safeParse(read.value);
    if (parsed.success) runs.set(id, parsed.data);
    else unreadable.push({ id, reason: formatIssues(`${id}.json`, parsed.error) });
  }
  return { runs, unreadable };
}

/**
 * Reads the records of the workspace. A missing state.json is an empty one; a version 1 state.json
 * is converted in memory. Runs that were running when the last server stopped are interrupted.
 */
export function loadRecords(root: string, now = Date.now()): LoadedRecords {
  const paths = recordPaths(root);
  if (!fs.existsSync(paths.state))
    return {
      state: emptyState(),
      runs: new Map(),
      unreadable: [],
      changes: { convertedV1: null, runs: [], state: false },
    };

  let text: string;
  try {
    text = fs.readFileSync(paths.state, "utf8");
  } catch (error) {
    throw new StateError(`Cannot read ${paths.state}: ${(error as Error).message}`);
  }
  let value: unknown;
  try {
    value = JSON.parse(text);
  } catch (error) {
    throw new StateError(
      `${paths.state} is not valid JSON (${(error as Error).message}). Repair it, or move it away to start with no records.`,
    );
  }
  const isObject = value !== null && typeof value === "object" && !Array.isArray(value);
  const version = isObject ? (value as { schemaVersion?: unknown }).schemaVersion : undefined;

  let loaded: LoadedRecords;
  if (version === undefined) {
    const parsed = stateFileV1Schema.safeParse(value);
    if (!parsed.success)
      throw new StateError(
        `${paths.state} has no schemaVersion and is not a harness 0.8 record:\n${formatIssues("state.json", parsed.error)}`,
      );
    const { state, runs } = migrateStateV1(parsed.data, now);
    loaded = {
      state,
      runs: new Map(runs.map((run) => [run.id, run])),
      unreadable: [],
      changes: { convertedV1: text, runs, state: true },
    };
  } else if (version === STATE_VERSION) {
    const parsed = stateFileSchema.safeParse(value);
    if (!parsed.success)
      throw new StateError(
        `${paths.state} is not a valid record:\n${formatIssues("state.json", parsed.error)}`,
      );
    loaded = {
      ...readRunRecords(root, parsed.data),
      state: parsed.data,
      changes: { convertedV1: null, runs: [], state: false },
    };
  } else {
    throw new StateError(
      `${paths.state} has schemaVersion ${JSON.stringify(version)}; this harness reads version ${STATE_VERSION}. Use the harness that wrote it.`,
    );
  }

  // No run survives the server that ran it.
  for (const summary of Object.values(loaded.state.runs)) {
    if (summary.status !== "running") continue;
    summary.status = "interrupted";
    summary.endedAt = now;
    loaded.changes.state = true;
    const run = loaded.runs.get(summary.id);
    if (!run) continue;
    run.status = "interrupted";
    run.endedAt = now;
    if (run.error === null) Object.assign(run, runError(INTERRUPTED_ERROR));
    if (!loaded.changes.runs.includes(run)) loaded.changes.runs.push(run);
  }
  return loaded;
}

/** The modification time and size of state.json, or "-" when there is none. */
export function stateSignature(root: string): string {
  try {
    const stat = fs.statSync(recordPaths(root).state);
    return `${stat.mtimeMs}:${stat.size}`;
  } catch {
    return "-";
  }
}

/** Whether persist() has something to write. */
export const hasChanges = (loaded: LoadedRecords): boolean =>
  loaded.changes.state || loaded.changes.runs.length > 0;

/**
 * Writes what loading changed. A converted version 1 state.json is kept as state.v1.json (or,
 * when that exists, state.v1-<time>.json) before state.json is replaced.
 */
export function persist(root: string, loaded: LoadedRecords): void {
  if (!hasChanges(loaded)) return;
  const paths = recordPaths(root);
  if (loaded.changes.convertedV1 !== null) {
    const keep = fs.existsSync(paths.stateV1)
      ? path.join(paths.dir, `state.v1-${Date.now()}.json`)
      : paths.stateV1;
    writeAtomic(keep, loaded.changes.convertedV1);
  }
  for (const run of loaded.changes.runs) writeRun(root, run);
  writeState(root, loaded.state);
  loaded.changes = { convertedV1: null, runs: [], state: false };
}

export const writeState = (root: string, state: StateFile): void =>
  writeAtomic(recordPaths(root).state, `${JSON.stringify(state, null, 2)}\n`);

export const writeRun = (root: string, run: Run): void =>
  writeAtomic(recordPaths(root).run(run.id), `${JSON.stringify(run, null, 2)}\n`);

export function appendEvent(root: string, runId: string, event: RunEvent): void {
  const file = recordPaths(root).events(runId);
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.appendFileSync(file, `${JSON.stringify(event)}\n`);
}

/** The last `tail` events of a run, and how many it has. Lines that are not events are skipped. */
export function readEvents(
  root: string,
  runId: string,
  tail: number,
): { events: RunEvent[]; total: number } {
  let text: string;
  try {
    text = fs.readFileSync(recordPaths(root).events(runId), "utf8");
  } catch {
    return { events: [], total: 0 };
  }
  const events: RunEvent[] = [];
  for (const line of text.split("\n")) {
    if (!line.trim()) continue;
    try {
      const event = JSON.parse(line) as RunEvent;
      if (typeof event.n === "number" && typeof event.kind === "string") events.push(event);
    } catch {
      // A line cut short when the server stopped is not an event.
    }
  }
  return { events: tail === 0 ? [] : events.slice(-tail), total: events.length };
}
