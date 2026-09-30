/*
 * The panel on the right: the details of what is selected. A Process (its purpose, Outcomes,
 * inputs, controls, outputs, and SKILL.md), an Artifact type (its locations, the Artifacts found
 * there, and the run that made each), a run (its record and its log, followed while it runs), an
 * instance (its inputs, criteria, runs, and evaluation, with the actions on it), or what a number
 * of the dashboard counts. With nothing selected, the model and the record of wakes. A wake run
 * lists the runs that its agent started.
 */

import { Fragment } from "preact";
import { useEffect, useState } from "preact/hooks";
import type {
  ArtifactsResponse,
  CancelResponse,
  InstanceView,
  RunDetailResponse,
  RunStartResponse,
  RunSummary,
  RunView,
  SkillResponse,
  StaleReason,
} from "../../shared/types.ts";
import { sayReceived } from "../../shared/strings.ts";
import { query } from "../api.ts";
import { useUi, type Selection } from "../context.ts";
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
import { EditForm, EvaluateForm, InstantiateForm } from "./forms.tsx";

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
        <p class="muted small">{t("overview.noWakes")}</p>
      ) : (
        <ul class="plain" data-testid="wakes">
          {wakes.map((run) => (
            <li key={run.id}>
              <RunLink id={run.id} /> <StatusText status={run.status} />{" "}
              <span class="muted small">{dateTime(run.startedAt, language)}</span>
            </li>
          ))}
        </ul>
      )}
    </Section>
  );
}

function Overview({ modelError }: { modelError: unknown }) {
  const { model, t, select } = useUi();
  if (!model)
    return modelError ? <ModelProblem error={modelError} /> : <p class="muted">{t("loading")}</p>;
  return (
    <div data-testid="panel-overview">
      <div class="panel-head">
        <div>
          <div class="kicker">{t("panel.model")}</div>
          <h2>{model.name}</h2>
          <div class="sub">
            {t("overview.counts", {
              processes: model.processes.length,
              types: model.artifacts.length,
            })}
          </div>
        </div>
      </div>
      {model.description && <p>{model.description}</p>}
      <Section title={t("overview.workspace")}>
        <p class="mono small">{model.workspace}</p>
      </Section>
      <Section title={t("overview.agents")}>
        <ul class="plain">
          {model.agents.map((agent) => (
            <li key={agent.id}>
              {agent.label}{" "}
              <span class={agent.available ? "muted" : "fail-text"}>
                {agent.available
                  ? `${t("overview.available")}${agent.version ? ` · ${agent.version}` : ""}`
                  : t("overview.unavailable", { reason: agent.reason ?? "" })}
              </span>
            </li>
          ))}
        </ul>
      </Section>
      <Wakes />
      <p class="muted small">{t("overview.hint")}</p>
      <button type="button" class="primary" onClick={() => select({ kind: "new" })}>
        {t("process.newInstance")}
      </button>
    </div>
  );
}

function TypeList({ ids }: { ids: readonly string[] }) {
  const { t } = useUi();
  if (ids.length === 0) return <p class="muted">{t("type.nobody")}</p>;
  return (
    <div class="chips">
      {ids.map((id) => (
        <TypeLink key={id} id={id} />
      ))}
    </div>
  );
}

function SkillView({ process }: { process: string }) {
  const { client, t, fail } = useUi();
  const [skill, setSkill] = useState<SkillResponse | null>(null);
  const [open, setOpen] = useState(false);
  useEffect(() => {
    setSkill(null);
    setOpen(false);
  }, [process]);
  const toggle = (): void => {
    setOpen((was) => !was);
    if (skill) return;
    client.get<SkillResponse>(`/api/skill${query({ process })}`).then(setSkill, fail);
  };
  const parts = skill ? splitFrontmatter(skill.text) : null;
  return (
    <>
      <button type="button" class="secondary" onClick={toggle} aria-expanded={open}>
        {open ? t("process.hideSkill") : t("process.showSkill")}
      </button>
      {open && parts && (
        <div class="skill" data-testid="skill">
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
          {skill?.truncated && <p class="muted small">{t("process.truncated")}</p>}
        </div>
      )}
    </>
  );
}

function ProcessPanel({ id }: { id: string }) {
  const { model, t, instances, select } = useUi();
  const process = model?.processes.find((p) => p.id === id);
  if (!process) return <Overview modelError={null} />;
  const own = [...instances.values()]
    .filter((i) => i.process === id)
    .sort((a, b) => updatedAt(b) - updatedAt(a));
  const skill = process.skill;
  return (
    <div data-testid="panel-process" data-process={id}>
      <PanelHead kicker={t("panel.process")} title={process.name} />
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
          <ul>
            {process.constraints.map((c, i) => (
              <li key={i}>{c}</li>
            ))}
          </ul>
        </Section>
      )}
      {process.enablers.length > 0 && (
        <Section title={t("process.enablers")}>
          <ul>
            {process.enablers.map((c, i) => (
              <li key={i}>{c}</li>
            ))}
          </ul>
        </Section>
      )}
      <Section title={t("process.skill")}>
        {!skill ? (
          <p class="muted">{t("process.noSkill")}</p>
        ) : "missing" in skill ? (
          <p class="fail-text">{t("process.skillMissing", { location: skill.missing })}</p>
        ) : (
          <>
            <p class="mono small">{skill.path}</p>
            <SkillView process={id} />
          </>
        )}
      </Section>
      <Section title={t("process.instances")}>
        {own.length === 0 ? (
          <p class="muted">{t("process.noInstances")}</p>
        ) : (
          <ul class="rows">
            {own.map((instance) => (
              <li key={instance.id}>
                <InstanceLink instance={instance} />
                <Glyphs judgments={instance.facts.judgments} outcomes={process.outcomes.length} />
              </li>
            ))}
          </ul>
        )}
        <button type="button" class="primary" onClick={() => select({ kind: "new", process: id })}>
          {t("process.newInstance")}
        </button>
      </Section>
    </div>
  );
}

function TypePanel({ id }: { id: string }) {
  const { model, t, client, version, language, fail } = useUi();
  const [found, setFound] = useState<ArtifactsResponse | null>(null);
  useEffect(() => {
    let live = true;
    client.get<ArtifactsResponse>(`/api/artifacts${query({ type: id })}`).then(
      (answer) => {
        if (live) setFound(answer);
      },
      (error: unknown) => {
        if (live) fail(error);
      },
    );
    return () => {
      live = false;
    };
  }, [id, version]);
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
      {type.description && <p>{type.description}</p>}
      <Section title={t("type.locations")}>
        {type.paths.length === 0 ? (
          <p class="fail-text">{t("type.noLocation")}</p>
        ) : (
          <ul class="plain mono small">
            {type.paths.map((p) => (
              <li key={p}>{p}</li>
            ))}
          </ul>
        )}
      </Section>
      <Section title={t("type.producedBy")}>
        {producers.length === 0 ? (
          <p class="muted">{t("type.nobody")}</p>
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
          <p class="muted">{t("type.nobody")}</p>
        ) : (
          <div class="chips">
            {readers.map((p) => (
              <ProcessLink key={p.id} id={p.id} />
            ))}
          </div>
        )}
      </Section>
      <Section title={t("type.artifacts")}>
        {!found ? (
          <p class="muted">{t("loading")}</p>
        ) : found.artifacts.length === 0 ? (
          <p class="muted">{t("type.noArtifacts")}</p>
        ) : (
          <ul class="rows" data-testid="artifacts">
            {found.artifacts.map((artifact) => (
              <li key={artifact.path}>
                <span class="mono small path-cell" title={artifact.path}>
                  {artifact.path}
                  {artifact.dir ? "/" : ""}
                </span>
                <span class="muted small">
                  {artifact.dir && artifact.items !== null
                    ? `${t("type.items", { n: artifact.items })} · `
                    : ""}
                  {dateTime(artifact.mtime, language)} ·{" "}
                  {artifact.producedBy ? <RunLink id={artifact.producedBy} /> : t("type.notMade")}
                </span>
              </li>
            ))}
          </ul>
        )}
        {found?.truncated && <p class="muted small">{t("type.truncated")}</p>}
      </Section>
    </div>
  );
}

function RunPanel({ id }: { id: string }) {
  const { client, t, language, version, fail, putRun, instances, model, runs } = useUi();
  const [detail, setDetail] = useState<RunDetailResponse | null>(null);
  const [canceling, setCanceling] = useState(false);
  useEffect(() => {
    let live = true;
    let timer: ReturnType<typeof setTimeout> | undefined;
    const load = (): void => {
      client
        .get<RunDetailResponse>(`/api/runs/${encodeURIComponent(id)}${query({ tail: 200 })}`)
        .then(
          (answer) => {
            if (!live) return;
            setDetail(answer);
            // Follow the log while the run runs.
            if (answer.run.status === "running") timer = setTimeout(load, 1500);
          },
          (error: unknown) => {
            if (live) fail(error);
          },
        );
    };
    load();
    return () => {
      live = false;
      clearTimeout(timer);
    };
  }, [id, version]);
  if (!detail) return <p class="muted">{t("loading")}</p>;
  const { run, events, truncated } = detail;
  const instance = run.instance ? instances.get(run.instance) : undefined;
  const agent = model?.agents.find((a) => a.id === run.agent)?.label ?? run.agent;
  const cancel = (): void => {
    setCanceling(true);
    client
      .post<CancelResponse>(`/api/runs/${encodeURIComponent(id)}/cancel`)
      .then((answer) => putRun(summaryOf(answer.run)), fail)
      .finally(() => setCanceling(false));
  };
  return (
    <div data-testid="panel-run" data-run={id} data-status={run.status}>
      <PanelHead
        kicker={run.kind === "wake" ? t("run.wake") : t("panel.run")}
        title={
          <>
            <span class="mono">{run.id}</span> <StatusText status={run.status} />
          </>
        }
        sub={run.process ? processName(model, run.process) : undefined}
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
                output: count(run.usage.outputTokens, language),
              })}
            </dd>
          </>
        )}
      </dl>
      {run.status === "running" && (
        <button type="button" class="secondary danger" disabled={canceling} onClick={cancel}>
          {canceling ? t("run.canceling") : t("run.cancel")}
        </button>
      )}
      {(run.error || run.agentError) && (
        <Section title={t("run.error")}>
          <p class="fail-text pre" data-testid="run-error">
            {[
              run.error && sayReceived(language, run.errorKey, run.errorArgs, run.error),
              run.agentError,
            ]
              .filter(Boolean)
              .join("\n")}
          </p>
        </Section>
      )}
      <Section title={t("run.report")}>
        {run.report ? <Markdown source={run.report} /> : <p class="muted">{t("run.noReport")}</p>}
      </Section>
      {run.kind === "wake" && (
        <Section title={t("run.startedRuns")}>
          {(run.started ?? []).length === 0 ? (
            <p class="muted">{t("run.noStartedRuns")}</p>
          ) : (
            <ul class="plain" data-testid="started-runs">
              {(run.started ?? []).map((started) => {
                const known = runs.get(started);
                const instance = known?.instance ? instances.get(known.instance) : undefined;
                return (
                  <li key={started}>
                    <RunLink id={started} /> {known && <StatusText status={known.status} />}{" "}
                    {instance && <InstanceLink instance={instance} />}
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
            <p class="muted">{t("run.noOutputs")}</p>
          ) : (
            <ul class="plain">
              {run.outputs.map((output) => (
                <li key={output.path}>
                  <span class="mono small">{output.path}</span>{" "}
                  <span class="muted small">
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
          <ul class="plain">
            {run.inputs.flatMap((input) =>
              input.paths.map((p) => (
                <li key={`${input.type}:${p}`}>
                  <span class="mono small">{p}</span>{" "}
                  <span class="muted small">
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
        {truncated && <p class="muted small">{t("run.earlier")}</p>}
        <pre class="log" data-testid="run-log">
          {events
            .map(
              (event) =>
                `${clock(event.t, language)} ${event.kind.padEnd(8)} ${sayReceived(language, event.key, event.args, event.text)}`,
            )
            .join("\n")}
        </pre>
        {run.status === "running" && <p class="muted small">{t("run.following")}</p>}
      </Section>
    </div>
  );
}

function staleText(t: ReturnType<typeof useUi>["t"], reason: StaleReason): string {
  if (reason.kind === "skill") return t("stale.skill", { path: reason.path ?? "SKILL.md" });
  return t(`stale.${reason.change}`, { path: reason.path });
}

function InstancePanel({ id }: { id: string }) {
  const { model, instances, runs, t, language, client, select, putRun, fail } = useUi();
  const instance = instances.get(id);
  const agents = (model?.agents ?? []).filter((a) => a.id !== "self");
  const [agent, setAgent] = useState<string>("");
  const [busy, setBusy] = useState(false);
  if (!model || !instance) return <Overview modelError={null} />;
  const process = model.processes.find((p) => p.id === instance.process);
  const latest = instance.facts.latestRun;
  const status = latest ? (runs.get(latest.id) ?? latest).status : null;
  const chosen =
    agents.find((a) => a.id === agent && a.available) ?? agents.find((a) => a.available) ?? null;
  const start = (): void => {
    if (!chosen) return;
    setBusy(true);
    client
      .post<RunStartResponse>(`/api/instances/${encodeURIComponent(id)}/run`, { agent: chosen.id })
      .then((answer) => putRun(summaryOf(answer.run)), fail)
      .finally(() => setBusy(false));
  };
  const cancel = (): void => {
    if (!latest) return;
    setBusy(true);
    client
      .post<CancelResponse>(`/api/runs/${encodeURIComponent(latest.id)}/cancel`)
      .then((answer) => putRun(summaryOf(answer.run)), fail)
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
  return (
    <div data-testid="panel-instance" data-instance={id}>
      <PanelHead
        kicker={`${t("panel.instance")} · ${instance.id}`}
        title={processName(model, instance.process)}
        sub={<span class="mono">{firstInput(model, instance) ?? ""}</span>}
      />
      <Section title={t("instance.inputs")}>
        <dl class="facts">
          {types.map((type) => (
            <Fragment key={type}>
              <dt>{typeName(model, type)}</dt>
              <dd class="mono small pre">
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
              <dd class="mono small">{instance.outputs[type] ?? t("instance.decided")}</dd>
            </Fragment>
          ))}
        </dl>
      </Section>
      <Section title={t("instance.criteria")}>
        {instance.criteria.length === 0 ? (
          <p class="muted small">{t("instance.noCriteria")}</p>
        ) : (
          <ul class="plain">
            {instance.criteria.map((c) => (
              <li key={c.outcome}>
                <strong>{c.outcome + 1}.</strong> {c.statement}
                {c.checks && (
                  <div class="muted small">
                    {t("instance.checks")}: {c.checks}
                  </div>
                )}
              </li>
            ))}
          </ul>
        )}
        {instance.notes && (
          <>
            <h4>{t("instance.notes")}</h4>
            <p class="pre">{instance.notes}</p>
          </>
        )}
        <button type="button" class="secondary" onClick={() => select({ kind: "edit", id })}>
          {t("instance.edit")}
        </button>
      </Section>
      <Section title={t("instance.runs")}>
        {status === "running" && latest ? (
          <div class="actions">
            <span>{t("instance.running", { run: latest.id })}</span>
            <button type="button" class="secondary danger" disabled={busy} onClick={cancel}>
              {busy ? t("run.canceling") : t("run.cancel")}
            </button>
          </div>
        ) : agents.some((a) => a.available) ? (
          <div class="actions">
            <label>
              {t("instance.agent")}
              <select
                value={chosen?.id ?? ""}
                onChange={(e) => setAgent((e.currentTarget as HTMLSelectElement).value)}
              >
                {agents.map((a) => (
                  <option
                    key={a.id}
                    value={a.id}
                    disabled={!a.available}
                    title={a.available ? undefined : (a.reason ?? undefined)}
                  >
                    {a.available ? a.label : t("instance.unavailable", { label: a.label })}
                  </option>
                ))}
              </select>
            </label>
            <button
              type="button"
              class="primary"
              disabled={busy}
              onClick={start}
              data-testid="start-run"
            >
              {busy ? t("instance.starting") : t("instance.start")}
            </button>
          </div>
        ) : (
          <p class="muted">{t("instance.noAgent")}</p>
        )}
        {instance.runs.length === 0 ? (
          <p class="muted">{t("instance.noRuns")}</p>
        ) : (
          <ul class="rows">
            {[...instance.runs].reverse().map((runId) => {
              const run = runs.get(runId) ?? (latest?.id === runId ? latest : undefined);
              return (
                <li key={runId}>
                  <RunLink id={runId} />
                  {run && <StatusText status={run.status} />}
                  {run && <span class="muted small">{dateTime(run.startedAt, language)}</span>}
                </li>
              );
            })}
          </ul>
        )}
      </Section>
      <Section title={t("instance.evaluation")}>
        {!evaluation ? (
          <p class="muted">{t("instance.noEvaluation")}</p>
        ) : (
          <>
            <p class="muted small">
              {t("instance.judgedRun", {
                run: evaluation.runId,
                by,
                at: dateTime(evaluation.at, language),
              })}
            </p>
            {instance.facts.stale ? (
              <div class="stale-box" data-testid="stale">
                <strong>{t("instance.staleTitle")}</strong>
                <ul>
                  {instance.facts.staleness.map((reason, i) => (
                    <li key={i}>{staleText(t, reason)}</li>
                  ))}
                </ul>
              </div>
            ) : (
              <p class="muted small">{t("instance.current")}</p>
            )}
            <ul class="judgments">
              {evaluation.judgments.map((j) => (
                <li key={j.outcome}>
                  <div>
                    <span class={`judgment j-${j.judgment}`}>{t(`judgment.${j.judgment}`)}</span>{" "}
                    <span class="muted small">
                      {j.outcome + 1}. {process?.outcomes[j.outcome] ?? ""}
                    </span>
                  </div>
                  <div class="small">
                    <strong>{t("instance.evidence")}:</strong> {j.evidence}
                  </div>
                  {j.limits && (
                    <div class="small muted">
                      <strong>{t("instance.limits")}:</strong> {j.limits}
                    </div>
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
          </>
        )}
        {latest && status !== "running" && (
          <button type="button" class="primary" onClick={() => select({ kind: "evaluate", id })}>
            {t("instance.evaluate")}
          </button>
        )}
      </Section>
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
        <p class="muted">{t("members.none")}</p>
      )}
      {listed.length > 0 && (
        <Section title={`${t("members.instances")} (${listed.length})`}>
          <ul class="rows">
            {listed.map((instance) => (
              <li key={instance.id}>
                <InstanceLink instance={instance} />
                <span>
                  <Glyphs
                    judgments={instance.facts.judgments}
                    outcomes={
                      model?.processes.find((p) => p.id === instance.process)?.outcomes.length ?? 0
                    }
                  />
                  {instance.facts.stale && (
                    <span class="stale-text small"> {t("instances.stale")}</span>
                  )}
                </span>
              </li>
            ))}
          </ul>
        </Section>
      )}
      {selection.runs.length > 0 && (
        <Section title={`${t("members.runs")} (${selection.runs.length})`}>
          <ul class="rows">
            {selection.runs.map((run) => (
              <li key={run.id}>
                <span>
                  <RunLink id={run.id} />{" "}
                  <span class="small">{processName(model, run.process)}</span>
                </span>
                <span class="small">
                  <StatusText status={run.status} />{" "}
                  <span class="muted">
                    {run.agent}
                    {run.endedAt !== null
                      ? ` · ${duration(run.endedAt - run.startedAt, language)}`
                      : ""}
                    {run.costUsd !== null ? ` · ${money(run.costUsd)}` : ""}
                  </span>
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
      return <ProcessPanel id={selection.id} />;
    case "type":
      return <TypePanel id={selection.id} />;
    case "run":
      return <RunPanel id={selection.id} />;
    case "instance":
      return <InstancePanel id={selection.id} />;
    case "new":
      return <InstantiateForm process={selection.process} />;
    case "edit":
      return <EditForm id={selection.id} />;
    case "evaluate":
      return <EvaluateForm id={selection.id} />;
    case "members":
      return <MembersPanel selection={selection} />;
  }
}
