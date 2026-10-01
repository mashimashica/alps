/* What the views of the WebUI share: the language, the API, the records they show, and the selection. */

import { createContext } from "preact";
import { useContext } from "preact/hooks";
import type {
  AssessScope,
  HealthInfo,
  InstanceView,
  Language,
  ModelView,
  RunStatus,
  RunSummary,
  StatsRun,
  UiView,
} from "../shared/types.ts";
import type { Client } from "./api.ts";
import type { FocusTarget } from "./graph/focus.ts";
import type { Translate } from "./strings.ts";

/**
 * The tabs of the panel of an instance. A run's log is in the run's panel, and the SKILL.md in the
 * Process's: the instance links to them.
 */
export type InstanceTab = "overview" | "runs" | "evaluation";
/** The tabs of the panel of a Process. */
export type ProcessTab = "overview" | "instances" | "skill";

/** What the right panel shows (a Sheet over the page in narrow windows). */
export type Selection =
  | { kind: "process"; id: string; tab?: ProcessTab }
  /** With `path`, that Artifact is marked among those of the type (cited as evidence). */
  | { kind: "type"; id: string; path?: string }
  /** With `line`, that event of the log is marked (cited as evidence). */
  | { kind: "run"; id: string; line?: number }
  | { kind: "instance"; id: string; tab?: InstanceTab }
  /** What a number of the dashboard counts. */
  | {
      kind: "members";
      title: string;
      subtitle: string;
      instances: string[];
      runs: StatsRun[];
    };

/**
 * What a person writes, in a dialog: a request, which a woken agent turns into instances (with a
 * Process chosen beforehand, when it is opened from one, or a draft, when it is opened from an
 * opportunity of an assessment), the criteria and notes of an instance, an evaluation, a request
 * for an assessment (its scope is the analysis's filter), or the review of an assessment's item.
 */
export type Form =
  | { kind: "request"; process?: string; draft?: string }
  | { kind: "edit"; id: string }
  | { kind: "evaluate"; id: string }
  | { kind: "assess"; scope: AssessScope }
  | { kind: "review"; assessment: string; n: number };

/** The filters of the list of instances; the counts at the top right set them too. */
export interface InstanceFilter {
  process: string;
  status: "" | RunStatus | "none";
  judgment: "" | "judged" | "unjudged" | "stale";
  path: string;
}

export const NO_FILTER: InstanceFilter = { process: "", status: "", judgment: "", path: "" };

export interface Ui {
  language: Language;
  t: Translate;
  client: Client;
  /** What GET /api/health said, once it answered: the server's version, pid, and port. */
  server: HealthInfo | null;
  model: ModelView | null;
  /** Every instance, by id. */
  instances: ReadonlyMap<string, InstanceView>;
  /** The latest runs, by id. */
  runs: ReadonlyMap<string, RunSummary>;
  /** Whether the instances and runs have been read once. */
  recordsLoaded: boolean;
  /** Grows whenever the records change; what a view reads besides them, it reads again then. */
  version: number;
  view: UiView;
  setView(view: UiView): void;
  selection: Selection | null;
  /** Shows something in the right panel; a Process or a type also becomes the network's focus. */
  select(selection: Selection | null): void;
  /**
   * Whether the panel shows only what is asked for (the dashboard and the instances: a column in
   * wide windows, a Sheet over the page in narrow ones), rather than always (the network: a column,
   * or in a narrow window a part of the page under the diagram, with the model's overview).
   */
  onDemand: boolean;
  /** Closes the panel: nothing is selected (in the network, the model's overview shows). */
  closePanel(): void;
  form: Form | null;
  openForm(form: Form | null): void;
  instanceFilter: InstanceFilter;
  setInstanceFilter(filter: Partial<InstanceFilter>): void;
  focus: FocusTarget | null;
  setFocus(target: FocusTarget | null): void;
  /** Keeps what an answer of the API returned. */
  putInstance(instance: InstanceView): void;
  putRun(run: RunSummary): void;
  /** Has the views read again what they show besides the records (after a change they made). */
  refresh(): void;
}

export const UiContext = createContext<Ui | null>(null);

export function useUi(): Ui {
  const ui = useContext(UiContext);
  if (!ui) throw new Error("useUi() outside the WebUI");
  return ui;
}
