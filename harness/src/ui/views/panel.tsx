/*
 * The panel on the right (in narrow windows a Sheet over the page, or under the network's
 * diagram): the details of what is selected. A Process (its purpose, Outcomes, inputs, controls,
 * outputs; its instances; its SKILL.md), an Artifact type (its locations, the Artifacts found
 * there, and the run that made each), a run (its record and its log, followed while it runs), an
 * instance (in tabs: its inputs and criteria, its runs with starting and canceling, its
 * evaluation, the log of its latest run, and its Process's SKILL.md), or what a number of the
 * dashboard counts. With nothing selected, the model and the record of wakes. A wake run lists
 * the runs that its agent started.
 */

import { Fragment } from "preact";
import { useEffect, useId, useLayoutEffect, useRef, useState } from "preact/hooks";
import { sayReceived } from "../../shared/strings.ts";
import type {
  ArtifactsResponse,
  CancelResponse,
  InstanceView,
  Judgment,
  RunDetailResponse,
  RunStartResponse,
  RunSummary,
  RunView,
  SkillResponse,
  StaleReason,
} from "../../shared/types.ts";
import { describeError, query } from "../api.ts";
import { Badge, type Tone } from "../components/badge.tsx";
import { Button } from "../components/button.tsx";
import { Alert, Empty, Loading } from "../components/feedback.tsx";
import { Icon } from "../components/icons.tsx";
import { Select } from "../components/select.tsx";
import { tabPanel, Tabs } from "../components/tabs.tsx";
import { useUi, type InstanceTab, type ProcessTab, type Selection, type Ui } from "../context.ts";
import { clock, count, dateTime, duration, money } from "../format.ts";
import { splitFrontmatter } from "../markdown.ts";
import {
  firstInput,
  Glyphs,
  InstanceLink,
  Markdown,
  ModelProblem,
  PanelHead,
  ProcessLink,
  processName,
  RunLink,
  Section,
  StatusText,
  TypeLink,
  typeName,
  updatedAt,
} from "./common.tsx";

export const summaryOf = (run: RunView): RunSummary => ({
  id: run.id,
  kind: run.kind,
  instance: run.instance,
  status: run.status,
  startedAt: run.startedAt,
  endedAt: run.endedAt,
});

/** How many wake runs the overview lists, newest first. */
const WAKES_LISTED = 10;
/** How often the log of a running run is read again. */
const FOLLOW_MS = 1500;

type Loaded<T> =
  | { status: "loading" }
  | { status: "ok"; value: T }
  | { status: "error"; error: unknown };

const JUDGMENT_TONE: Record<Judgment, Tone> = {
  achieved: "brand",
  "not-achieved": "danger",
  unverified: "neutral",
};

function Retry({ onRetry }: { onRetry: () => void }) {
  const { t } = useUi();
  return (
    <Button variant="outline" size="sm" onClick={onRetry}>
      <Icon name="refresh" />
      {t("retry")}
    </Button>
  );
}

/** The record of wakes: the latest wake runs, each a link to its record and the runs it started. */
function Wakes() {
  const { runs, t, language } = useUi();
  const wakes = [...runs.values()]
    .filter((run) => run.kind === "wake")
    .sort((a, b) => b.startedAt - a.startedAt)
    .slice(0, WAKES_LISTED);
  return (
    <Section title={t("overview.wakes")}>
      {wakes.length === 0 ? (
        <p class="faint small">{t("overview.noWakes")}</p>
      ) : (
        <ul class="list" data-testid="wakes">
          {wakes.map((run) => (
            <li key={run.id} class="list-row">
              <span class="list-main">
                <RunLink id={run.id} />
                <span class="faint small">{dateTime(run.startedAt, language)}</span>
              </span>
              <StatusText status={run.status} />
            </li>
          ))}
        </ul>
      )}
    </Section>
  );
}

function Overview({ modelError }: { modelError: unknown }) {
  const { model, t, openForm, sheet } = useUi();
  if (!model)
    return modelError ? <ModelProblem error={modelError} /> : <Loading label={t("loading")} />;
  return (
    <div data-testid="panel-overview">
      <PanelHead
        kicker={t("panel.model")}
        title={model.name}
        sub={t("overview.counts", {
          processes: model.processes.length,
          types: model.artifacts.length,
        })}
        closable={sheet}
      />
      {model.description && <p class="panel-text">{model.description}</p>}
      <Section title={t("overview.workspace")}>
        <p class="mono small path-block" title={model.workspace}>
          {model.workspace}
        </p>
      </Section>
      <Section title={t("overview.agents")}>
        <ul class="list">
          {model.agents.map((agent) => (
            <li key={agent.id} class="list-row list-row-stack">
              <span class="list-main">
                <span class="strong">{agent.label}</span>
                {agent.available && (
                  <Badge tone="success" dot>
                    {t("overview.available")}
                  </Badge>
                )}
              </span>
              {agent.available ? (
                agent.version && <span class="faint small">{agent.version}</span>
              ) : (
                <span class="danger-text small">
                  {t("overview.unavailable", { reason: agent.reason ?? "" })}
                </span>
              )}
            </li>
          ))}
        </ul>
      </Section>
      <Wakes />
      <p class="faint small panel-hint">{t("overview.hint")}</p>
      <Button onClick={() => openForm({ kind: "new" })}>
        <Icon name="plus" />
        {t("process.newInstance")}
      </Button>
    </div>
  );
}

function TypeList({ ids }: { ids: readonly string[] }) {
  const { t } = useUi();
  if (ids.length === 0) return <p class="faint small">{t("type.nobody")}</p>;
  return (
    <div class="chips">
      {ids.map((id) => (
        <TypeLink key={id} id={id} />
      ))}
    </div>
  );
}

/** The SKILL.md of a Process, read when it is shown. */
function SkillView({ process }: { process: string }) {
  const { client, t, language } = useUi();
  const [state, setState] = useState<Loaded<SkillResponse>>({ status: "loading" });
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    let live = true;
    setState({ status: "loading" });
    client.get<SkillResponse>(`/api/skill${query({ process })}`).then(
      (value) => {
        if (live) setState({ status: "ok", value });
      },
      (error: unknown) => {
        if (live) setState({ status: "error", error });
      },
    );
    return () => {
      live = false;
    };
  }, [process, attempt]);
  if (state.status === "loading") return <Loading label={t("loading")} lines={6} />;
  if (state.status === "error")
    return (
      <Alert
        tone="danger"
        title={t("error.title")}
        action={<Retry onRetry={() => setAttempt((n) => n + 1)} />}
      >
        {describeError(state.error, language)}
      </Alert>
    );
  const skill = state.value;
  const parts = splitFrontmatter(skill.text);
  return (
    <div class="skill" data-testid="skill">
      <p class="mono small faint skill-path">
        <Icon name="file" size={14} />
        {skill.skill.path}
      </p>
      {parts.front.length > 0 && (
        <dl class="front">
          {parts.front.map(([key, value]) => (
            <Fragment key={key}>
              <dt>{key}</dt>
              <dd>{value}</dd>
            </Fragment>
          ))}
        </dl>
      )}
      <Markdown source={parts.body} />
      {skill.truncated && <p class="faint small">{t("process.truncated")}</p>}
    </div>
  );
}

/** The SKILL.md tab of a Process: the file, or why there is none. */
function SkillTab({ process }: { process: string }) {
  const { model, t } = useUi();
  const skill = model?.processes.find((p) => p.id === process)?.skill ?? null;
  if (!skill) return <Empty icon="file" title={t("process.noSkill")} />;
  if ("missing" in skill)
    return <Alert tone="warning">{t("process.skillMissing", { location: skill.missing })}</Alert>;
  return <SkillView process={process} />;
}

function ProcessPanel({ id, initial }: { id: string; initial: ProcessTab }) {
  const { model, t, instances, openForm } = useUi();
  const base = useId();
  const [tab, setTab] = useState<ProcessTab>(initial);
  const process = model?.processes.find((p) => p.id === id);
  if (!process) return <Overview modelError={null} />;
  const own = [...instances.values()]
    .filter((i) => i.process === id)
    .sort((a, b) => updatedAt(b) - updatedAt(a));
  return (
    <div data-testid="panel-process" data-process={id}>
      <PanelHead kicker={t("panel.process")} title={process.name} />
      <Tabs
        value={tab}
        onChange={setTab}
        label={t("panel.tabs")}
        base={base}
        items={[
          { value: "overview", label: t("tab.overview") },
          { value: "instances", label: t("process.instances"), count: own.length },
          { value: "skill", label: t("tab.skill") },
        ]}
      />
      <div class="panel-tab" {...tabPanel(base, tab)}>
        {tab === "overview" && (
          <>
            {process.purpose && <p class="purpose">{process.purpose}</p>}
            <Section title={t("process.outcomes")}>
              <ol class="outcomes">
                {process.outcomes.map((outcome, i) => (
                  <li key={i}>{outcome}</li>
                ))}
              </ol>
            </Section>
            <Section title={t("process.inputs")}>
              <TypeList ids={process.inputs} />
            </Section>
            {process.controls.length > 0 && (
              <Section title={t("process.controls")}>
                <TypeList ids={process.controls} />
              </Section>
            )}
            <Section title={t("process.outputs")}>
              <TypeList ids={process.outputs} />
            </Section>
            {process.constraints.length > 0 && (
              <Section title={t("process.constraints")}>
                <ul class="bullets">
                  {process.constraints.map((c, i) => (
                    <li key={i}>{c}</li>
                  ))}
                </ul>
              </Section>
            )}
            {process.enablers.length > 0 && (
              <Section title={t("process.enablers")}>
                <ul class="bullets">
                  {process.enablers.map((c, i) => (
                    <li key={i}>{c}</li>
                  ))}
                </ul>
              </Section>
            )}
          </>
        )}
        {tab === "instances" && (
          <>
            {own.length === 0 ? (
              <Empty icon="layers" title={t("process.noInstances")} />
            ) : (
              <ul class="list">
                {own.map((instance) => (
                  <li key={instance.id} class="list-row">
                    <InstanceLink instance={instance} />
                    <Glyphs
                      judgments={instance.facts.judgments}
                      outcomes={process.outcomes.length}
                    />
                  </li>
                ))}
              </ul>
            )}
            <Button onClick={() => openForm({ kind: "new", process: id })}>
              <Icon name="plus" />
              {t("process.newInstance")}
            </Button>
          </>
        )}
        {tab === "skill" && <SkillTab process={id} />}
      </div>
    </div>
  );
}

function TypePanel({ id }: { id: string }) {
  const { model, t, client, version, language } = useUi();
  const [found, setFound] = useState<Loaded<ArtifactsResponse>>({ status: "loading" });
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    let live = true;
    client.get<ArtifactsResponse>(`/api/artifacts${query({ type: id })}`).then(
      (value) => {
        if (live) setFound({ status: "ok", value });
      },
      (error: unknown) => {
        if (live) setFound({ status: "error", error });
      },
    );
    return () => {
      live = false;
    };
  }, [id, version, attempt]);
  const type = model?.artifacts.find((a) => a.id === id);
  if (!model || !type) return <Overview modelError={null} />;
  const producers = model.processes.filter((p) => p.outputs.includes(id));
  const readers = model.processes.filter((p) => p.inputs.includes(id) || p.controls.includes(id));
  return (
    <div data-testid="panel-type" data-type={id}>
      <PanelHead
        kicker={t("panel.type")}
        title={type.name}
        sub={`${t("type.kind")}: ${type.kind ? t(`kind.${type.kind}`) : t("kind.none")}`}
      />
      {type.description && <p class="panel-text">{type.description}</p>}
      <Section title={t("type.locations")}>
        {type.paths.length === 0 ? (
          <Alert tone="warning">{t("type.noLocation")}</Alert>
        ) : (
          <ul class="list mono small">
            {type.paths.map((p) => (
              <li key={p} class="path-block">
                {p}
              </li>
            ))}
          </ul>
        )}
      </Section>
      <Section title={t("type.producedBy")}>
        {producers.length === 0 ? (
          <p class="faint small">{t("type.nobody")}</p>
        ) : (
          <div class="chips">
            {producers.map((p) => (
              <ProcessLink key={p.id} id={p.id} />
            ))}
          </div>
        )}
      </Section>
      <Section title={t("type.readBy")}>
        {readers.length === 0 ? (
          <p class="faint small">{t("type.nobody")}</p>
        ) : (
          <div class="chips">
            {readers.map((p) => (
              <ProcessLink key={p.id} id={p.id} />
            ))}
          </div>
        )}
      </Section>
      <Section title={t("type.artifacts")}>
        {found.status === "loading" && <Loading label={t("loading")} />}
        {found.status === "error" && (
          <Alert
            tone="danger"
            title={t("error.title")}
            action={<Retry onRetry={() => setAttempt((n) => n + 1)} />}
          >
            {describeError(found.error, language)}
          </Alert>
        )}
        {found.status === "ok" &&
          (found.value.artifacts.length === 0 ? (
            <p class="faint small">{t("type.noArtifacts")}</p>
          ) : (
            <ul class="list" data-testid="artifacts">
              {found.value.artifacts.map((artifact) => (
                <li key={artifact.path} class="list-row list-row-stack">
                  <span class="mono small path-cell" title={artifact.path}>
                    {artifact.path}
                    {artifact.dir ? "/" : ""}
                  </span>
                  <span class="faint small">
                    {artifact.dir && artifact.items !== null
                      ? `${t("type.items", { n: artifact.items })} · `
                      : ""}
                    {dateTime(artifact.mtime, language)} ·{" "}
                    {artifact.producedBy ? <RunLink id={artifact.producedBy} /> : t("type.notMade")}
                  </span>
                </li>
              ))}
            </ul>
          ))}
        {found.status === "ok" && found.value.truncated && (
          <p class="faint small">{t("type.truncated")}</p>
        )}
      </Section>
    </div>
  );
}

/** A run's record, read again when the records change and every FOLLOW_MS while it runs. */
function useRun(id: string | null) {
  const { client, version } = useUi();
  const [detail, setDetail] = useState<RunDetailResponse | null>(null);
  const [error, setError] = useState<unknown>(null);
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    if (!id) return;
    let live = true;
    let timer: ReturnType<typeof setTimeout> | undefined;
    const load = (): void => {
      client
        .get<RunDetailResponse>(`/api/runs/${encodeURIComponent(id)}${query({ tail: 200 })}`)
        .then(
          (answer) => {
            if (!live) return;
            setDetail(answer);
            setError(null);
            // Follow the log while the run runs.
            if (answer.run.status === "running") timer = setTimeout(load, FOLLOW_MS);
          },
          (failure: unknown) => {
            if (live) setError(failure);
          },
        );
    };
    load();
    return () => {
      live = false;
      clearTimeout(timer);
    };
  }, [id, version, attempt]);
  return {
    detail: detail && detail.run.id === id ? detail : null,
    error,
    retry: () => setAttempt((n) => n + 1),
  };
}

/**
 * A run's log, one event per line, what the harness itself said in the page's language. While the
 * run runs, the box stays at its end unless it was scrolled up.
 */
function RunLog({ detail }: { detail: RunDetailResponse }) {
  const { t, language } = useUi();
  const box = useRef<HTMLPreElement>(null);
  const atEnd = useRef(true);
  const { run, events, truncated } = detail;
  const last = events[events.length - 1];
  useLayoutEffect(() => {
    const element = box.current;
    if (element && atEnd.current) element.scrollTop = element.scrollHeight;
  }, [events.length, last?.t]);
  return (
    <>
      {truncated && <p class="faint small">{t("run.earlier")}</p>}
      <pre
        ref={box}
        class="log"
        data-testid="run-log"
        tabIndex={0}
        aria-label={t("run.log")}
        onScroll={(event) => {
          const element = event.currentTarget;
          atEnd.current = element.scrollHeight - element.scrollTop - element.clientHeight < 24;
        }}
      >
        {events.map((event, i) => (
          <Fragment key={i}>
            {i > 0 && "\n"}
            <span class={`log-line k-${event.kind}`}>
              <span class="log-time">{clock(event.t, language)}</span>{" "}
              <span class="log-kind">{event.kind.padEnd(8)}</span>{" "}
              <span class="log-text">
                {sayReceived(language, event.key, event.args, event.text)}
              </span>
            </span>
          </Fragment>
        ))}
      </pre>
      {run.status === "running" && (
        <p class="following">
          <span class="live-dot" aria-hidden="true" />
          {t("run.following")}
        </p>
      )}
    </>
  );
}

function RunPanel({ id }: { id: string }) {
  const { client, t, language, putRun, instances, model, runs } = useUi();
  const { detail, error, retry } = useRun(id);
  const [canceling, setCanceling] = useState(false);
  const [cancelError, setCancelError] = useState<unknown>(null);
  if (!detail)
    return error ? (
      <Alert tone="danger" title={t("error.title")} action={<Retry onRetry={retry} />}>
        {describeError(error, language)}
      </Alert>
    ) : (
      <Loading label={t("loading")} lines={5} />
    );
  const { run } = detail;
  const instance = run.instance ? instances.get(run.instance) : undefined;
  const agent = model?.agents.find((a) => a.id === run.agent)?.label ?? run.agent;
  const cancel = (): void => {
    setCanceling(true);
    setCancelError(null);
    client
      .post<CancelResponse>(`/api/runs/${encodeURIComponent(id)}/cancel`)
      .then((answer) => putRun(summaryOf(answer.run)), setCancelError)
      .finally(() => setCanceling(false));
  };
  return (
    <div data-testid="panel-run" data-run={id} data-status={run.status}>
      <PanelHead
        kicker={run.kind === "wake" ? t("run.wake") : t("panel.run")}
        title={<span class="mono">{run.id}</span>}
        sub={
          <span class="head-status">
            <StatusText status={run.status} />
            {run.process && <span>{processName(model, run.process)}</span>}
          </span>
        }
      />
      <dl class="facts">
        <dt>{t("run.agent")}</dt>
        <dd>
          {agent}
          {run.client ? ` · ${t("run.self")}` : ""}
        </dd>
        {instance && (
          <>
            <dt>{t("run.instance")}</dt>
            <dd>
              <InstanceLink instance={instance} />
            </dd>
          </>
        )}
        <dt>{t("run.started")}</dt>
        <dd>{dateTime(run.startedAt, language)}</dd>
        {run.endedAt !== null && (
          <>
            <dt>{t("run.ended")}</dt>
            <dd>{dateTime(run.endedAt, language)}</dd>
            <dt>{t("run.duration")}</dt>
            <dd>{duration(run.endedAt - run.startedAt, language)}</dd>
          </>
        )}
        {run.usage && (
          <>
            <dt>{t("run.usage")}</dt>
            <dd>
              {t("run.usageValue", {
                cost: money(run.usage.costUsd),
                input: count(run.usage.inputTokens, language),
                cached:
                  run.usage.cachedInputTokens === null
                    ? null
                    : count(run.usage.cachedInputTokens, language),
                output: count(run.usage.outputTokens, language),
              })}
            </dd>
          </>
        )}
      </dl>
      {run.status === "running" && (
        <Button
          variant="destructive"
          size="sm"
          busy={canceling}
          disabled={canceling}
          onClick={cancel}
        >
          <Icon name="stop" />
          {canceling ? t("run.canceling") : t("run.cancel")}
        </Button>
      )}
      {cancelError !== null && (
        <Alert tone="danger" title={t("run.cancelFailed")}>
          {describeError(cancelError, language)}
        </Alert>
      )}
      {(run.error || run.agentError) && (
        <Section title={t("run.error")}>
          <Alert tone="danger" live={false}>
            <p class="pre" data-testid="run-error">
              {[
                run.error && sayReceived(language, run.errorKey, run.errorArgs, run.error),
                run.agentError,
              ]
                .filter(Boolean)
                .join("\n")}
            </p>
          </Alert>
        </Section>
      )}
      <Section title={t("run.report")}>
        {run.report ? (
          <Markdown source={run.report} />
        ) : (
          <p class="faint small">{t("run.noReport")}</p>
        )}
      </Section>
      {run.kind === "wake" && (
        <Section title={t("run.startedRuns")}>
          {(run.started ?? []).length === 0 ? (
            <p class="faint small">{t("run.noStartedRuns")}</p>
          ) : (
            <ul class="list" data-testid="started-runs">
              {(run.started ?? []).map((started) => {
                const known = runs.get(started);
                const target = known?.instance ? instances.get(known.instance) : undefined;
                return (
                  <li key={started} class="list-row list-row-stack">
                    <span class="list-main">
                      <RunLink id={started} />
                      {known && <StatusText status={known.status} />}
                    </span>
                    {target && <InstanceLink instance={target} />}
                  </li>
                );
              })}
            </ul>
          )}
        </Section>
      )}
      {run.kind === "process" && (
        <Section title={t("run.outputs")}>
          {run.outputs.length === 0 ? (
            <p class="faint small">{t("run.noOutputs")}</p>
          ) : (
            <ul class="list">
              {run.outputs.map((output) => (
                <li key={output.path} class="list-row list-row-stack">
                  <span class="mono small path-cell" title={output.path}>
                    {output.path}
                  </span>
                  <span class="faint small">
                    {typeName(model, output.type)} · {t(`run.${output.change}`)}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </Section>
      )}
      {run.inputs.length > 0 && (
        <Section title={t("run.inputs")}>
          <ul class="list">
            {run.inputs.flatMap((input) =>
              input.paths.map((p) => (
                <li key={`${input.type}:${p}`} class="list-row list-row-stack">
                  <span class="mono small path-cell" title={p}>
                    {p}
                  </span>
                  <span class="faint small">
                    {typeName(model, input.type)}
                    {input.missing.includes(p) ? ` · ${t("run.missing")}` : ""}
                  </span>
                </li>
              )),
            )}
          </ul>
        </Section>
      )}
      <Section title={t("run.log")}>
        <RunLog detail={detail} />
      </Section>
    </div>
  );
}

function staleText(t: Ui["t"], reason: StaleReason): string {
  if (reason.kind === "skill") return t("stale.skill", { path: reason.path ?? "SKILL.md" });
  return t(`stale.${reason.change}`, { path: reason.path });
}

/** The log tab of an instance: its latest run's log, followed while it runs. */
function LatestLog({ run }: { run: string }) {
  const { t, language } = useUi();
  const { detail, error, retry } = useRun(run);
  return (
    <>
      <p class="tab-lead">
        <span class="faint small">{t("instance.logOf", { run })}</span>
        <RunLink id={run} />
      </p>
      {detail ? (
        <RunLog detail={detail} />
      ) : error ? (
        <Alert tone="danger" title={t("error.title")} action={<Retry onRetry={retry} />}>
          {describeError(error, language)}
        </Alert>
      ) : (
        <Loading label={t("loading")} lines={5} />
      )}
    </>
  );
}

function InstancePanel({ id, initial }: { id: string; initial: InstanceTab }) {
  const { model, instances, runs, t, language, client, putRun, openForm } = useUi();
  const base = useId();
  const [tab, setTab] = useState<InstanceTab>(initial);
  const [agent, setAgent] = useState<string>("");
  const [busy, setBusy] = useState(false);
  const [actionError, setActionError] = useState<{
    what: "start" | "cancel";
    error: unknown;
  } | null>(null);
  const instance = instances.get(id);
  if (!model || !instance) return <Overview modelError={null} />;
  const agents = model.agents.filter((a) => a.id !== "self");
  const process = model.processes.find((p) => p.id === instance.process);
  const latest = instance.facts.latestRun;
  const status = latest ? (runs.get(latest.id) ?? latest).status : null;
  const chosen =
    agents.find((a) => a.id === agent && a.available) ?? agents.find((a) => a.available) ?? null;
  const start = (): void => {
    if (!chosen) return;
    setBusy(true);
    setActionError(null);
    client
      .post<RunStartResponse>(`/api/instances/${encodeURIComponent(id)}/run`, { agent: chosen.id })
      .then(
        (answer) => {
          putRun(summaryOf(answer.run));
          setTab("log");
        },
        (error: unknown) => setActionError({ what: "start", error }),
      )
      .finally(() => setBusy(false));
  };
  const cancel = (): void => {
    if (!latest) return;
    setBusy(true);
    setActionError(null);
    client
      .post<CancelResponse>(`/api/runs/${encodeURIComponent(latest.id)}/cancel`)
      .then(
        (answer) => putRun(summaryOf(answer.run)),
        (error: unknown) => setActionError({ what: "cancel", error }),
      )
      .finally(() => setBusy(false));
  };
  const types = process
    ? [...process.inputs, ...process.controls.filter((c) => !process.inputs.includes(c))]
    : Object.keys(instance.inputs);
  const outputs = process ? process.outputs : Object.keys(instance.outputs);
  const evaluation = instance.evaluation;
  const by = !evaluation
    ? ""
    : evaluation.by.kind === "user"
      ? t("judge.user")
      : evaluation.by.self
        ? t("judge.self", { id: evaluation.by.id })
        : evaluation.by.id;
  const outcomes = process?.outcomes.length ?? 0;
  const evaluate = latest && status !== "running" && (
    <Button onClick={() => openForm({ kind: "evaluate", id })}>
      <Icon name="check" />
      {t("instance.evaluate")}
    </Button>
  );
  return (
    <div data-testid="panel-instance" data-instance={id}>
      <PanelHead
        kicker={`${t("panel.instance")} · ${instance.id}`}
        title={processName(model, instance.process)}
        sub={<span class="mono path-cell">{firstInput(model, instance) ?? ""}</span>}
      />
      <Tabs
        value={tab}
        onChange={setTab}
        label={t("panel.tabs")}
        base={base}
        items={[
          { value: "overview", label: t("tab.overview") },
          { value: "runs", label: t("instance.runs"), count: instance.runs.length },
          { value: "evaluation", label: t("instance.evaluation") },
          { value: "log", label: t("run.log") },
          { value: "skill", label: t("tab.skill") },
        ]}
      />
      <div class="panel-tab" {...tabPanel(base, tab)}>
        {tab === "overview" && (
          <>
            <dl class="summary">
              <div>
                <dt>{t("instance.latest")}</dt>
                <dd>
                  {latest && status ? (
                    <span class="summary-run">
                      <RunLink id={latest.id} />
                      <StatusText status={status} />
                      <span class="faint small">{dateTime(latest.startedAt, language)}</span>
                    </span>
                  ) : (
                    <span class="faint">{t("instance.noRuns")}</span>
                  )}
                </dd>
              </div>
              <div>
                <dt>{t("instance.judgments")}</dt>
                <dd>
                  <span class="summary-run">
                    <Glyphs judgments={instance.facts.judgments} outcomes={outcomes} />
                    {evaluation &&
                      (instance.facts.stale ? (
                        <Badge tone="warning" dot>
                          {t("instances.stale")}
                        </Badge>
                      ) : (
                        <span class="muted small">{t("instances.currentEvidence")}</span>
                      ))}
                  </span>
                </dd>
              </div>
            </dl>
            <p class="faint small">{t("instance.runVsOutcome")}</p>
            <Section title={t("instance.inputs")}>
              <dl class="facts">
                {types.map((type) => (
                  <Fragment key={type}>
                    <dt>{typeName(model, type)}</dt>
                    <dd class="mono small pre path-cell">
                      {(instance.inputs[type] ?? []).length === 0
                        ? t("instance.notYet")
                        : (instance.inputs[type] ?? []).join("\n")}
                    </dd>
                  </Fragment>
                ))}
              </dl>
            </Section>
            <Section title={t("instance.outputs")}>
              <dl class="facts">
                {outputs.map((type) => (
                  <Fragment key={type}>
                    <dt>{typeName(model, type)}</dt>
                    <dd class="mono small path-cell">
                      {instance.outputs[type] ?? t("instance.decided")}
                    </dd>
                  </Fragment>
                ))}
              </dl>
            </Section>
            <Section
              title={t("instance.criteria")}
              actions={
                <Button variant="ghost" size="sm" onClick={() => openForm({ kind: "edit", id })}>
                  {t("instance.edit")}
                </Button>
              }
            >
              {instance.criteria.length === 0 ? (
                <p class="faint small">{t("instance.noCriteria")}</p>
              ) : (
                <ol class="criteria-list">
                  {instance.criteria.map((c) => (
                    <li key={c.outcome}>
                      <span class="criterion-number">{c.outcome + 1}</span>
                      <div>
                        <p>{c.statement}</p>
                        {c.checks && (
                          <p class="faint small">
                            {t("instance.checks")}: {c.checks}
                          </p>
                        )}
                      </div>
                    </li>
                  ))}
                </ol>
              )}
              {instance.notes && (
                <>
                  <h4>{t("instance.notes")}</h4>
                  <p class="pre panel-text">{instance.notes}</p>
                </>
              )}
            </Section>
          </>
        )}
        {tab === "runs" && (
          <>
            {status === "running" && latest ? (
              <div class="action-row">
                <span class="action-text">
                  <span class="live-dot" aria-hidden="true" />
                  {t("instance.running", { run: latest.id })}
                </span>
                <Button
                  variant="destructive"
                  size="sm"
                  busy={busy}
                  disabled={busy}
                  onClick={cancel}
                >
                  <Icon name="stop" />
                  {busy ? t("run.canceling") : t("run.cancel")}
                </Button>
              </div>
            ) : agents.some((a) => a.available) ? (
              <div class="action-row">
                <Select
                  label={t("instance.agent")}
                  value={chosen?.id ?? ""}
                  options={agents.map((a) => ({
                    value: a.id,
                    label: a.available ? a.label : t("instance.unavailable", { label: a.label }),
                    hint: a.available ? (a.version ?? undefined) : (a.reason ?? undefined),
                    disabled: !a.available,
                  }))}
                  onChange={setAgent}
                  class="action-select"
                />
                <Button busy={busy} disabled={busy} onClick={start} data-testid="start-run">
                  <Icon name="play" />
                  {busy ? t("instance.starting") : t("instance.start")}
                </Button>
              </div>
            ) : (
              <Alert tone="warning">{t("instance.noAgent")}</Alert>
            )}
            {actionError && (
              <Alert
                tone="danger"
                title={actionError.what === "start" ? t("run.startFailed") : t("run.cancelFailed")}
              >
                {describeError(actionError.error, language)}
              </Alert>
            )}
            {instance.runs.length === 0 ? (
              <Empty icon="activity" title={t("instance.noRuns")} />
            ) : (
              <ul class="list">
                {[...instance.runs].reverse().map((runId) => {
                  const run = runs.get(runId) ?? (latest?.id === runId ? latest : undefined);
                  return (
                    <li key={runId} class="list-row">
                      <span class="list-main">
                        <RunLink id={runId} />
                        {run && (
                          <span class="faint small">{dateTime(run.startedAt, language)}</span>
                        )}
                      </span>
                      {run && <StatusText status={run.status} />}
                    </li>
                  );
                })}
              </ul>
            )}
          </>
        )}
        {tab === "evaluation" && (
          <>
            {!evaluation ? (
              <Empty
                icon="target"
                title={t("instance.noEvaluation")}
                action={evaluate || undefined}
              />
            ) : (
              <>
                <p class="faint small">
                  {t("instance.judgedRun", {
                    run: evaluation.runId,
                    by,
                    at: dateTime(evaluation.at, language),
                  })}
                </p>
                {instance.facts.stale ? (
                  <Alert tone="warning" title={t("instance.staleTitle")} data-testid="stale">
                    <ul class="bullets">
                      {instance.facts.staleness.map((reason, i) => (
                        <li key={i}>{staleText(t, reason)}</li>
                      ))}
                    </ul>
                  </Alert>
                ) : (
                  <Alert tone="success" live={false}>
                    {t("instance.current")}
                  </Alert>
                )}
                <ul class="judgments">
                  {evaluation.judgments.map((j) => (
                    <li key={j.outcome} class="judgment-item">
                      <div class="judgment-head">
                        <Badge tone={JUDGMENT_TONE[j.judgment]}>
                          {t(`judgment.${j.judgment}`)}
                        </Badge>
                        <span class="small">
                          <span class="criterion-number">{j.outcome + 1}</span>
                          {process?.outcomes[j.outcome] ?? ""}
                        </span>
                      </div>
                      <p class="small">
                        <strong>{t("instance.evidence")}:</strong> {j.evidence}
                      </p>
                      {j.limits && (
                        <p class="small muted">
                          <strong>{t("instance.limits")}:</strong> {j.limits}
                        </p>
                      )}
                    </li>
                  ))}
                </ul>
                {evaluation.note && (
                  <>
                    <h4>{t("instance.note")}</h4>
                    <Markdown source={evaluation.note} />
                  </>
                )}
                {evaluate}
              </>
            )}
          </>
        )}
        {tab === "log" &&
          (latest ? (
            <LatestLog run={latest.id} />
          ) : (
            <Empty icon="activity" title={t("instance.noRuns")} />
          ))}
        {tab === "skill" && <SkillTab process={instance.process} />}
      </div>
    </div>
  );
}

function MembersPanel({ selection }: { selection: Extract<Selection, { kind: "members" }> }) {
  const { t, instances, model, language } = useUi();
  const listed = selection.instances
    .map((id) => instances.get(id))
    .filter((i): i is InstanceView => i !== undefined);
  return (
    <div data-testid="panel-members">
      <PanelHead kicker={t("tab.dashboard")} title={selection.title} sub={selection.subtitle} />
      {listed.length === 0 && selection.runs.length === 0 && (
        <Empty icon="list" title={t("members.none")} />
      )}
      {listed.length > 0 && (
        <Section title={`${t("members.instances")} (${listed.length})`}>
          <ul class="list">
            {listed.map((instance) => (
              <li key={instance.id} class="list-row">
                <InstanceLink instance={instance} />
                <span class="list-end">
                  <Glyphs
                    judgments={instance.facts.judgments}
                    outcomes={
                      model?.processes.find((p) => p.id === instance.process)?.outcomes.length ?? 0
                    }
                  />
                  {instance.facts.stale && (
                    <Badge tone="warning" dot>
                      {t("instances.stale")}
                    </Badge>
                  )}
                </span>
              </li>
            ))}
          </ul>
        </Section>
      )}
      {selection.runs.length > 0 && (
        <Section title={`${t("members.runs")} (${selection.runs.length})`}>
          <ul class="list">
            {selection.runs.map((run) => (
              <li key={run.id} class="list-row list-row-stack">
                <span class="list-main">
                  <RunLink id={run.id} />
                  <StatusText status={run.status} />
                </span>
                <span class="faint small">
                  {processName(model, run.process)} · {run.agent}
                  {run.endedAt !== null
                    ? ` · ${duration(run.endedAt - run.startedAt, language)}`
                    : ""}
                  {run.costUsd !== null ? ` · ${money(run.costUsd)}` : ""}
                </span>
              </li>
            ))}
          </ul>
        </Section>
      )}
    </div>
  );
}

export function Panel({ modelError }: { modelError: unknown }) {
  const { selection } = useUi();
  if (!selection) return <Overview modelError={modelError} />;
  switch (selection.kind) {
    case "process":
      return (
        <ProcessPanel
          key={`${selection.id}:${selection.tab ?? ""}`}
          id={selection.id}
          initial={selection.tab ?? "overview"}
        />
      );
    case "type":
      return <TypePanel key={selection.id} id={selection.id} />;
    case "run":
      return <RunPanel key={selection.id} id={selection.id} />;
    case "instance":
      return (
        <InstancePanel
          key={`${selection.id}:${selection.tab ?? ""}`}
          id={selection.id}
          initial={selection.tab ?? "overview"}
        />
      );
    case "members":
      return <MembersPanel selection={selection} />;
  }
}

/** What the panel shows, in words, for the polite announcement when it changes. */
export function selectionLabel(ui: Ui, selection: Selection | null): string {
  const { t, model } = ui;
  if (!selection) return model ? `${t("panel.model")}: ${model.name}` : "";
  switch (selection.kind) {
    case "process":
      return `${t("panel.process")}: ${processName(model, selection.id)}`;
    case "type":
      return `${t("panel.type")}: ${typeName(model, selection.id)}`;
    case "run":
      return `${t("panel.run")}: ${selection.id}`;
    case "instance": {
      const instance = ui.instances.get(selection.id);
      return `${t("panel.instance")}: ${instance ? processName(model, instance.process) : selection.id}`;
    }
    case "members":
      return selection.title;
  }
}
