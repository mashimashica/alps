/* What the views of the WebUI share: the language, the API, the records they show, and the selection. */

import { createContext } from "preact";
import { useContext } from "preact/hooks";
import type {
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

/** The tabs of the panel of an instance. */
export type InstanceTab = "overview" | "runs" | "evaluation" | "log" | "skill";
/** The tabs of the panel of a Process. */
export type ProcessTab = "overview" | "instances" | "skill";

/** What the right panel shows (a Sheet over the page in narrow windows). */
export type Selection =
  | { kind: "process"; id: string; tab?: ProcessTab }
  | { kind: "type"; id: string }
  | { kind: "run"; id: string }
  | { kind: "instance"; id: string; tab?: InstanceTab }
  /** What a number of the dashboard counts. */
  | {
      kind: "members";
      title: string;
      subtitle: string;
      instances: string[];
      runs: StatsRun[];
    };

/** What a person writes, in a dialog: an instantiation, the criteria of one, or an evaluation. */
export type Form =
  | { kind: "new"; process?: string }
  | { kind: "edit"; id: string }
  | { kind: "evaluate"; id: string };

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
   * Whether the panel is a Sheet over the page (narrow windows), rather than a column or, in the
   * network of a narrow window, a part of the page under the diagram.
   */
  sheet: boolean;
  /** Closes the panel: nothing is selected (in a column, the model's overview shows). */
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
}

export const UiContext = createContext<Ui | null>(null);

export function useUi(): Ui {
  const ui = useContext(UiContext);
  if (!ui) throw new Error("useUi() outside the WebUI");
  return ui;
}
