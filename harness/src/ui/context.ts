/* What the views of the WebUI share: the language, the API, the records they show, and the selection. */

import { createContext } from "preact";
import { useContext } from "preact/hooks";
import type {
  InstanceView,
  Language,
  ModelView,
  RunSummary,
  StatsRun,
  UiView,
} from "../shared/types.ts";
import type { Client } from "./api.ts";
import type { FocusTarget } from "./graph/focus.ts";
import type { Translate } from "./strings.ts";

/** What the right panel shows. */
export type Selection =
  | { kind: "process"; id: string }
  | { kind: "type"; id: string }
  | { kind: "run"; id: string }
  | { kind: "instance"; id: string }
  | { kind: "new"; process?: string }
  | { kind: "edit"; id: string }
  | { kind: "evaluate"; id: string }
  /** What a number of the dashboard counts. */
  | {
      kind: "members";
      title: string;
      subtitle: string;
      instances: string[];
      runs: StatsRun[];
    };

export interface Ui {
  language: Language;
  t: Translate;
  client: Client;
  model: ModelView | null;
  /** Every instance, by id. */
  instances: ReadonlyMap<string, InstanceView>;
  /** The latest runs, by id. */
  runs: ReadonlyMap<string, RunSummary>;
  /** Grows whenever the records change; what a view reads besides them, it reads again then. */
  version: number;
  view: UiView;
  setView(view: UiView): void;
  selection: Selection | null;
  /** Shows something in the right panel; a Process or a type also becomes the network's focus. */
  select(selection: Selection | null): void;
  focus: FocusTarget | null;
  setFocus(target: FocusTarget | null): void;
  /** Keeps what an answer of the API returned. */
  putInstance(instance: InstanceView): void;
  putRun(run: RunSummary): void;
  /** Shows a failure at the top of the page. */
  fail(error: unknown): void;
}

export const UiContext = createContext<Ui | null>(null);

export function useUi(): Ui {
  const ui = useContext(UiContext);
  if (!ui) throw new Error("useUi() outside the WebUI");
  return ui;
}
