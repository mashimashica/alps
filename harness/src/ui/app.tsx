/*
 * The WebUI: a sidebar with the model, the three screens (the dashboard, the network, the
 * instances), and the display setting; a header with the counts of running runs and stale
 * evidence at the top right (the only place they are shown), the state of the connection to the
 * server (its version, pid, and port in the title), the language, and the theme; and a
 * panel on the right for what is selected. In wide windows the panel is a column: the network
 * keeps it (the model's overview until something is picked), and the dashboard and the instances
 * open it for what is picked, so that their screens keep the whole width until then. In narrow
 * windows it is a Sheet over the page, and the sidebar is a drawer. In the network, a narrow
 * window keeps the panel in the page below the diagram instead: a Sheet would cover the focus
 * view and the background whose click returns to the whole ring.
 * Each screen's heading carries the main action, Request: a person says what is needed, and a
 * woken agent plans, instantiates, and runs the Processes that serve it (views/forms.tsx).
 * The page shows states by colour, shape, and place, not in sentences: what a screen is for, a
 * legend, and the details (full paths, ids, the server) are in the panel or in titles.
 * The records are read once and kept current through the event stream; the page only draws them.
 */

import { useCallback, useEffect, useMemo, useRef, useState } from "preact/hooks";
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
import { Button } from "./components/button.tsx";
import { Switch } from "./components/checkbox.tsx";
import { Sheet } from "./components/dialog.tsx";
import { Alert } from "./components/feedback.tsx";
import { Icon, type IconName } from "./components/icons.tsx";
import { Select } from "./components/select.tsx";
import { tabPanel, Tabs } from "./components/tabs.tsx";
import { Tooltip } from "./components/tooltip.tsx";
import { cx, useMedia } from "./components/util.ts";
import {
  NO_FILTER,
  UiContext,
  useUi,
  type Form,
  type InstanceFilter,
  type Selection,
  type Ui,
} from "./context.ts";
import type { FocusTarget } from "./graph/focus.ts";
import {
  applyDisplay,
  keepLanguage,
  keepTheme,
  keepTransparency,
  keepView,
  keptLanguage,
  keptTheme,
  keptTransparency,
  type Session,
  type Theme,
} from "./session.ts";
import { browserLanguage, translator } from "./strings.ts";
import { lastPart } from "./views/common.tsx";
import { DashboardView } from "./views/dashboard.tsx";
import { FormDialog } from "./views/forms.tsx";
import { InstancesView } from "./views/instances.tsx";
import { NetworkView } from "./views/network.tsx";
import { Panel, selectionLabel } from "./views/panel.tsx";

const VIEWS: readonly UiView[] = ["dashboard", "network", "instances"];
const VIEW_ICONS: Record<UiView, IconName> = {
  network: "network",
  dashboard: "dashboard",
  instances: "board",
};
const THEME_ICONS: Record<Theme, IconName> = { system: "monitor", light: "sun", dark: "moon" };
/** How many pages of runs (200 each) the page keeps; older runs are read when they are opened. */
const RUN_PAGES = 5;
/** From this width the panel is a column; narrower, a Sheet (in the network, under the diagram). */
const WIDE = "(min-width: 1180px)";
/** Up to this width the sidebar is a drawer. */
const NARROW = "(max-width: 760px)";
/** Between the drawer and this width, the sidebar is a rail of icons. */
const RAIL = "(min-width: 761px) and (max-width: 1059px)";

type Health =
  | { status: "loading" }
  | { status: "ok"; health: HealthInfo }
  | { status: "error"; error: unknown };

type Stream = StreamState | "connecting" | "shutdown";

/**
 * The page's link to the server at the top right: live, connecting, or offline by the colour of
 * its dot, with what GET /api/health said in its title (the server's version, pid, and port, or
 * why it cannot be reached) and in `data-status`. Once the event stream is lost for good, it is a
 * button that reconnects.
 */
function Connection({
  stream,
  health,
  onReconnect,
}: {
  stream: Stream;
  health: Health;
  onReconnect: () => void;
}) {
  const { t, language, client } = useUi();
  const status = client.token ? health.status : "error";
  const title = !client.token
    ? t("token.missing")
    : health.status === "ok"
      ? t("health.ok", {
          version: health.health.version,
          pid: health.health.pid,
          port: health.health.port,
        })
      : health.status === "error"
        ? t("health.error", { message: describeError(health.error, language) })
        : t("health.loading");
  if (client.token && (stream === "closed" || stream === "shutdown"))
    return (
      <Button
        variant="outline"
        size="sm"
        class="connection is-offline"
        data-testid="health"
        data-status={status}
        title={title}
        onClick={onReconnect}
      >
        <Icon name="refresh" />
        <span class="connection-text">{t("events.reconnect")}</span>
      </Button>
    );
  const state =
    status === "error" ? "offline" : stream === "open" && status === "ok" ? "live" : "connecting";
  return (
    <span
      class={cx("connection", `is-${state}`)}
      role="status"
      data-testid="health"
      data-status={status}
      title={title}
    >
      <span class="connection-dot" aria-hidden="true" />
      <span class="connection-text">
        {t(
          state === "live"
            ? "events.live"
            : state === "offline"
              ? "events.offline"
              : "events.connecting",
        )}
      </span>
    </span>
  );
}

/** The counts of running runs and of stale evidence at the top right; each lists its instances. */
function Counts({
  running,
  stale,
  show,
}: {
  running: number;
  stale: number;
  show: (filter: Partial<InstanceFilter>) => void;
}) {
  const { t } = useUi();
  return (
    <div class="counts">
      <Tooltip content={t("count.showRunning")}>
        {(tip) => (
          <button
            type="button"
            class={cx("count", running > 0 && "has-running")}
            data-testid="running-count"
            data-count={running}
            onClick={() => show({ status: "running" })}
            {...tip}
          >
            <span class="mark-running" aria-hidden="true" />
            <span class="count-text">{t("count.running", { n: running })}</span>
            <span class="count-n" aria-hidden="true">
              {running}
            </span>
          </button>
        )}
      </Tooltip>
      <Tooltip content={t("count.showStale")}>
        {(tip) => (
          <button
            type="button"
            class={cx("count", stale > 0 && "has-stale")}
            data-testid="stale-count"
            data-count={stale}
            onClick={() => show({ judgment: "stale" })}
            {...tip}
          >
            <span class="mark-stale" aria-hidden="true" />
            <span class="count-text">{t("count.stale", { n: stale })}</span>
            <span class="count-n" aria-hidden="true">
              {stale}
            </span>
          </button>
        )}
      </Tooltip>
    </div>
  );
}

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
  const [recordsLoaded, setRecordsLoaded] = useState(false);
  const [version, setVersion] = useState(0);
  const [selection, setSelection] = useState<Selection | null>(null);
  const [focus, setFocus] = useState<FocusTarget | null>(null);
  const [stream, setStream] = useState<Stream>("connecting");
  const [connection, setConnection] = useState(0);
  const [form, setForm] = useState<Form | null>(null);
  const [instanceFilter, setInstanceFilter] = useState<InstanceFilter>(NO_FILTER);
  /** Where the panel shows only on demand, the model's overview shows only when asked for. */
  const [overview, setOverview] = useState(false);
  const [drawer, setDrawer] = useState(false);
  const [theme, setTheme] = useState<Theme>(keptTheme);
  const [transparency, setTransparency] = useState<boolean | null>(keptTransparency);
  const wideWindow = useMedia(WIDE);
  const narrow = useMedia(NARROW);
  const rail = useMedia(RAIL);
  const systemOpaque = useMedia("(prefers-reduced-transparency: reduce)");
  const panelOpen = selection !== null || overview;
  /** The dashboard and the instances show the panel for what is picked; the network, always. */
  const onDemand = view !== "network";
  /** The panel as a column: in a wide window, while it has something to show. */
  const wide = wideWindow && (!onDemand || panelOpen);
  /** The network in a narrow window: the panel follows the diagram in the page. */
  const below = !wideWindow && !onDemand;
  const sheet = !wideWindow && onDemand;
  const menuButton = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    document.documentElement.lang = language;
  }, [language]);
  useEffect(() => applyDisplay(theme, transparency), [theme, transparency]);
  useEffect(() => {
    if (!narrow) setDrawer(false);
  }, [narrow]);
  // The drawer takes the focus when it opens and gives it back to the menu button when it closes.
  const drawerWasOpen = useRef(false);
  useEffect(() => {
    if (drawer) {
      document.getElementById(`view-tab-${view}`)?.focus();
      const onKey = (event: KeyboardEvent): void => {
        if (event.key === "Escape") setDrawer(false);
      };
      document.addEventListener("keydown", onKey);
      drawerWasOpen.current = true;
      return () => document.removeEventListener("keydown", onKey);
    }
    if (drawerWasOpen.current) menuButton.current?.focus();
    drawerWasOpen.current = false;
    return undefined;
  }, [drawer]);

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
      setRecordsLoaded(true);
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
          case "assessment":
            bump();
            break;
          case "shutdown":
            setStream("shutdown");
            break;
        }
      },
      (state) => setStream((known) => (known === "shutdown" ? known : state)),
    );
  }, [client, loadModel, loadRecords, bump, connection]);

  const closePanel = (): void => {
    setSelection(null);
    setOverview(false);
  };
  const setView = (next: UiView): void => {
    setViewState(next);
    keepView(next);
    // A selection belongs to the screen it was opened on. Do not cover the next screen with it.
    closePanel();
    window.scrollTo({ top: 0, behavior: "instant" });
  };
  const ui: Ui = {
    language,
    t,
    client,
    server: health.status === "ok" ? health.health : null,
    model,
    instances,
    runs,
    recordsLoaded,
    version,
    view,
    setView,
    selection,
    select: (next) => {
      setSelection(next);
      if (next && (next.kind === "process" || next.kind === "type"))
        setFocus({ kind: next.kind, id: next.id });
    },
    onDemand,
    closePanel,
    form,
    openForm: setForm,
    instanceFilter,
    setInstanceFilter: (next) => setInstanceFilter((known) => ({ ...known, ...next })),
    focus,
    setFocus,
    putInstance: (instance) => setInstances((known) => new Map(known).set(instance.id, instance)),
    putRun: (run) => setRuns((known) => new Map(known).set(run.id, run)),
    refresh: bump,
  };

  const running = [...runs.values()].filter((run) => run.status === "running").length;
  const stale = [...instances.values()].filter((instance) => instance.facts.stale).length;
  const switchLanguage = (): void => {
    const next: Language = language === "en" ? "ja" : "en";
    setLanguage(next);
    keepLanguage(next);
  };
  const showInstances = (filter: Partial<InstanceFilter>): void => {
    setDrawer(false);
    setInstanceFilter({ ...NO_FILTER, ...filter });
    setView("instances");
  };
  const reconnect = (): void => {
    setStream("connecting");
    setHealth({ status: "loading" });
    setConnection((n) => n + 1);
  };
  const opaque = transparency === null ? systemOpaque : !transparency;

  const notice = !client.token
    ? t("token.missing")
    : stream === "shutdown"
      ? t("events.shutdown")
      : stream === "closed"
        ? t("token.missing")
        : null;

  return (
    <UiContext.Provider value={ui}>
      <div class={cx("app", wide && "has-column", narrow && "is-narrow")}>
        <aside
          class={cx("sidebar", drawer && "is-open")}
          id="sidebar"
          aria-label={t("tabs.label")}
          inert={narrow && !drawer ? true : undefined}
        >
          <div class="brand">
            <span class="brand-mark" aria-hidden="true" />
            {/* The title's text is the name; its dot and capitals are drawn by the stylesheet. */}
            <h1 class="brand-title" aria-label={t("app.title")}>
              <span class="brand-name">{t("brand.name")}</span>{" "}
              <span class="brand-caption">{t("brand.product")}</span>
            </h1>
            {narrow && (
              <Button
                variant="ghost"
                size="icon-sm"
                class="drawer-close"
                aria-label={t("nav.close")}
                onClick={() => setDrawer(false)}
              >
                <Icon name="x" />
              </Button>
            )}
          </div>
          {/* The model and the folder of its workspace; the whole path is in the title and the overview. */}
          <button
            type="button"
            onClick={() => {
              setSelection(null);
              setOverview(true);
              setDrawer(false);
            }}
            aria-label={t("panel.open")}
            class="workspace-card"
            title={model ? `${model.name}\n${model.workspace}` : undefined}
          >
            <span class="workspace-icon" aria-hidden="true">
              <Icon name="layers" />
            </span>
            <span class="workspace-text">
              <strong>{model?.name ?? "—"}</strong>
              <span class="workspace-path mono">{model ? lastPart(model.workspace) : ""}</span>
            </span>
          </button>
          <nav class="sidebar-nav" aria-label={t("tabs.label")}>
            <Tabs
              value={view}
              onChange={(next) => {
                setView(next);
                setDrawer(false);
              }}
              items={VIEWS.map((name) => ({
                value: name,
                label: t(`tab.${name}`),
                title: rail ? t(`tab.${name}`) : undefined,
                icon: <Icon name={VIEW_ICONS[name]} size={17} />,
                attrs: { "data-view": name },
              }))}
              label={t("tabs.label")}
              base="view"
              orientation="vertical"
              variant="nav"
            />
          </nav>
          <div class="sidebar-spacer" />
          <div class="sidebar-section">
            <Switch
              checked={opaque}
              onChange={(off) => {
                setTransparency(!off);
                keepTransparency(!off);
                applyDisplay(theme, !off);
              }}
              label={t("display.transparency")}
              title={rail ? t("display.transparency") : undefined}
            />
          </div>
        </aside>
        {narrow && drawer && (
          <div class="drawer-overlay" aria-hidden="true" onClick={() => setDrawer(false)} />
        )}
        <div class="shell" inert={narrow && drawer ? true : undefined}>
          <header class="topbar">
            <div class="topbar-start">
              {narrow && (
                <button
                  ref={menuButton}
                  type="button"
                  class="btn btn-ghost btn-icon menu-button"
                  aria-label={t("nav.menu")}
                  aria-expanded={drawer}
                  aria-controls="sidebar"
                  onClick={() => setDrawer(true)}
                >
                  <Icon name="menu" size={18} />
                </button>
              )}
            </div>
            <div class="topbar-end">
              <Counts running={running} stale={stale} show={showInstances} />
              <Connection stream={stream} health={health} onReconnect={reconnect} />
              <button
                type="button"
                class="language btn btn-ghost btn-sm"
                onClick={switchLanguage}
                aria-label={t("language.label")}
                lang={language === "en" ? "ja" : "en"}
              >
                <Icon name="languages" />
                <span class="language-text">{t("language.switch")}</span>
              </button>
              <Select
                label={t("theme.label")}
                value={theme}
                size="sm"
                compact
                class="theme-select"
                options={(["system", "light", "dark"] as const).map((value) => ({
                  value,
                  label: t(`theme.${value}`),
                  icon: <Icon name={THEME_ICONS[value]} />,
                }))}
                onChange={(next) => {
                  setTheme(next);
                  keepTheme(next);
                  applyDisplay(next, transparency);
                }}
              />
              {onDemand && (
                <Tooltip content={t("panel.open")}>
                  {(tip) => (
                    <Button
                      variant="ghost"
                      size="icon"
                      aria-label={t("panel.open")}
                      onClick={() => {
                        setSelection(null);
                        setOverview(true);
                      }}
                      {...tip}
                    >
                      <Icon name="panel" />
                    </Button>
                  )}
                </Tooltip>
              )}
            </div>
          </header>
          <div class="banners">
            {notice && (
              <Alert
                tone="warning"
                action={
                  client.token ? (
                    <Button variant="outline" size="sm" onClick={reconnect}>
                      <Icon name="refresh" />
                      {t("events.reconnect")}
                    </Button>
                  ) : undefined
                }
              >
                {notice}
              </Alert>
            )}
            {stream === "retrying" && client.token && (
              <Alert
                tone="info"
                action={
                  <Button variant="outline" size="sm" onClick={reconnect}>
                    <Icon name="refresh" />
                    {t("events.reconnect")}
                  </Button>
                }
              >
                {t("events.retrying")}
              </Alert>
            )}
          </div>
          <div class="workarea">
            <main class="main" id="main">
              <div class="page-head">
                <div class="page-title">
                  <h2>{t(`tab.${view}`)}</h2>
                </div>
                {/* The main action on every screen: a request, which a woken agent turns into instances. */}
                <Button
                  onClick={() => setForm({ kind: "request" })}
                  disabled={!model}
                  data-testid="request-open"
                >
                  <Icon name="send" />
                  {t("request.open")}
                </Button>
              </div>
              <section class="view" data-view={view} {...tabPanel("view", view)} tabIndex={-1}>
                {view === "network" && <NetworkView modelError={modelError} />}
                {view === "dashboard" && <DashboardView modelError={modelError} />}
                {view === "instances" && <InstancesView modelError={modelError} />}
              </section>
              {below && (
                <aside class="panel panel-below" aria-label={t("panel.label")}>
                  <Panel modelError={modelError} />
                </aside>
              )}
            </main>
            {wide && (
              <aside class="panel" aria-label={t("panel.label")}>
                <Panel modelError={modelError} />
              </aside>
            )}
          </div>
        </div>
        {sheet && panelOpen && (
          <Sheet label={t("panel.label")} onClose={closePanel}>
            <Panel modelError={modelError} />
          </Sheet>
        )}
        <p class="sr-only" aria-live="polite">
          {selectionLabel(ui, selection)}
        </p>
        <FormDialog />
      </div>
    </UiContext.Provider>
  );
}
