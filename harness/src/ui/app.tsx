/*
 * The WebUI: three screens (the network, the dashboard, the instances), the counts of running runs
 * and stale evidence at the top right, and a panel on the right for what is selected. The records
 * are read once and kept current through the event stream; the page only draws them.
 */

import { useCallback, useEffect, useMemo, useState } from "preact/hooks";
import type {
  HealthInfo,
  InstanceView,
  InstancesResponse,
  Language,
  ModelResponse,
  ModelView,
  RunSummary,
  RunsResponse,
  UiView,
} from "../shared/types.ts";
import { createClient, describeError, query, type StreamState } from "./api.ts";
import { UiContext, type Selection, type Ui } from "./context.ts";
import type { FocusTarget } from "./graph/focus.ts";
import { keepLanguage, keepView, keptLanguage, type Session } from "./session.ts";
import { browserLanguage, translator } from "./strings.ts";
import { DashboardView } from "./views/dashboard.tsx";
import { InstancesView } from "./views/instances.tsx";
import { NetworkView } from "./views/network.tsx";
import { Panel } from "./views/panel.tsx";

const VIEWS: readonly UiView[] = ["network", "dashboard", "instances"];
/** How many pages of runs (200 each) the page keeps; older runs are read when they are opened. */
const RUN_PAGES = 5;

type Health =
  | { status: "loading" }
  | { status: "ok"; health: HealthInfo }
  | { status: "error"; error: unknown };

export function App({ session }: { session: Session }) {
  const client = useMemo(() => createClient(session.token), [session.token]);
  const [language, setLanguage] = useState<Language>(
    () => keptLanguage() ?? browserLanguage(navigator.languages ?? [navigator.language]),
  );
  const t = useMemo(() => translator(language), [language]);
  const [view, setViewState] = useState<UiView>(session.view);
  const [health, setHealth] = useState<Health>({ status: "loading" });
  const [model, setModel] = useState<ModelView | null>(null);
  const [modelError, setModelError] = useState<unknown>(null);
  const [instances, setInstances] = useState<ReadonlyMap<string, InstanceView>>(new Map());
  const [runs, setRuns] = useState<ReadonlyMap<string, RunSummary>>(new Map());
  const [version, setVersion] = useState(0);
  const [selection, setSelection] = useState<Selection | null>(null);
  const [focus, setFocus] = useState<FocusTarget | null>(null);
  const [stream, setStream] = useState<StreamState | "connecting" | "shutdown">("connecting");
  const [failure, setFailure] = useState<unknown>(null);

  useEffect(() => {
    document.documentElement.lang = language;
  }, [language]);

  const bump = useCallback(() => setVersion((v) => v + 1), []);

  const loadModel = useCallback(async () => {
    try {
      const answer = await client.get<ModelResponse>("/api/model");
      setModel(answer.model);
      setModelError(null);
    } catch (error) {
      setModelError(error);
    }
  }, [client]);

  const loadRecords = useCallback(async () => {
    try {
      const found = new Map<string, InstanceView>();
      let cursor: string | null = null;
      do {
        const page: InstancesResponse = await client.get(
          `/api/instances${query({ limit: 200, cursor })}`,
        );
        for (const instance of page.instances) found.set(instance.id, instance);
        cursor = page.next;
      } while (cursor);
      setInstances(found);
      const recent = new Map<string, RunSummary>();
      cursor = null;
      for (let pages = 0; pages === 0 || (cursor && pages < RUN_PAGES); pages++) {
        const page: RunsResponse = await client.get(`/api/runs${query({ limit: 200, cursor })}`);
        for (const run of page.runs) recent.set(run.id, run);
        cursor = page.next;
      }
      setRuns(recent);
      bump();
    } catch (error) {
      // Without a model there are no instances to list; the views say why.
      setModelError((known: unknown) => known ?? error);
    }
  }, [client, bump]);

  useEffect(() => {
    if (!client.token) return;
    client.get<HealthInfo>("/api/health").then(
      (answer) => setHealth({ status: "ok", health: answer }),
      (error: unknown) => setHealth({ status: "error", error }),
    );
    void loadModel();
    void loadRecords();
    let hellos = 0;
    return client.events(
      (event) => {
        switch (event.type) {
          case "hello":
            // After a reconnection, events may have been missed: read everything again.
            if (hellos++ > 0) {
              void loadModel();
              void loadRecords();
            }
            break;
          case "instance":
            setInstances((known) => new Map(known).set(event.instance.id, event.instance));
            bump();
            break;
          case "run":
            setRuns((known) => new Map(known).set(event.run.id, event.run));
            bump();
            break;
          case "artifacts":
            bump();
            break;
          case "model":
            void loadModel();
            bump();
            break;
          case "shutdown":
            setStream("shutdown");
            break;
        }
      },
      (state) => setStream((known) => (known === "shutdown" ? known : state)),
    );
  }, [client, loadModel, loadRecords, bump]);

  const ui: Ui = {
    language,
    t,
    client,
    model,
    instances,
    runs,
    version,
    view,
    setView: (next) => {
      setViewState(next);
      keepView(next);
    },
    selection,
    select: (next) => {
      setSelection(next);
      if (next && (next.kind === "process" || next.kind === "type"))
        setFocus({ kind: next.kind, id: next.id });
    },
    focus,
    setFocus,
    putInstance: (instance) => setInstances((known) => new Map(known).set(instance.id, instance)),
    putRun: (run) => setRuns((known) => new Map(known).set(run.id, run)),
    fail: setFailure,
  };

  const running = [...runs.values()].filter((run) => run.status === "running").length;
  const stale = [...instances.values()].filter((instance) => instance.facts.stale).length;
  const switchLanguage = (): void => {
    const next: Language = language === "en" ? "ja" : "en";
    setLanguage(next);
    keepLanguage(next);
  };

  const notice = !client.token
    ? t("token.missing")
    : stream === "shutdown"
      ? t("events.shutdown")
      : stream === "closed"
        ? t("token.missing")
        : null;

  return (
    <UiContext.Provider value={ui}>
      <div class="app">
        <header class="top">
          <div class="brand">
            <h1>{t("app.title")}</h1>
            <nav class="tabs" role="tablist" aria-label={t("tabs.label")}>
              {VIEWS.map((name) => (
                <button
                  type="button"
                  role="tab"
                  key={name}
                  data-view={name}
                  aria-selected={view === name}
                  onClick={() => ui.setView(name)}
                >
                  {t(`tab.${name}`)}
                </button>
              ))}
            </nav>
          </div>
          <div class="counts">
            <span data-testid="running-count" data-count={running}>
              <span class="mark-running" aria-hidden="true" />
              {t("count.running", { n: running })}
            </span>
            <span data-testid="stale-count" data-count={stale}>
              <span class="mark-stale" aria-hidden="true" />
              {t("count.stale", { n: stale })}
            </span>
            <button
              type="button"
              class="language"
              onClick={switchLanguage}
              aria-label={t("language.label")}
              lang={language === "en" ? "ja" : "en"}
            >
              {t("language.switch")}
            </button>
          </div>
        </header>
        {notice && (
          <p class="notice" role="status">
            {notice}
          </p>
        )}
        {stream === "retrying" && client.token && health.status === "ok" && (
          <p class="notice subtle" role="status">
            {t("events.retrying")}
          </p>
        )}
        {failure !== null && (
          <div class="notice error" role="alert">
            <span>{describeError(failure, language)}</span>
            <button type="button" class="link" onClick={() => setFailure(null)}>
              {t("error.dismiss")}
            </button>
          </div>
        )}
        <main class="body">
          <section class="view" data-view={view}>
            {view === "network" && <NetworkView modelError={modelError} />}
            {view === "dashboard" && <DashboardView modelError={modelError} />}
            {view === "instances" && <InstancesView />}
          </section>
          <aside class="panel" aria-live="polite">
            <Panel modelError={modelError} />
          </aside>
        </main>
        <footer class="status">
          <span data-testid="health" data-status={client.token ? health.status : "error"}>
            {!client.token && t("token.missing")}
            {client.token && health.status === "loading" && t("health.loading")}
            {health.status === "ok" &&
              t("health.ok", {
                version: health.health.version,
                pid: health.health.pid,
                port: health.health.port,
                workspace: health.health.workspace,
              })}
            {health.status === "error" &&
              t("health.error", { message: describeError(health.error, language) })}
          </span>
        </footer>
      </div>
    </UiContext.Provider>
  );
}
