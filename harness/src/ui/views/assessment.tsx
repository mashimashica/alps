/*
 * The analysis's upper part: the latest assessment, an agent's interpretation of the records, kept
 * apart from what the harness observes below it. A thin band and a quotation carry the
 * interpretation (whose it is, when, what it read, from what point of view, and its summary), with
 * what the records gained since, an observation, at its side. Under it, the opportunities that the
 * agent found: each with its kind, its subject, one sentence, and the evidence it rests on as chips
 * that open the record (a run, an instance, an evaluation, an event of a log, an Artifact or a
 * SKILL.md) or set the filter below (a cut of the statistics); and a person's review (adopted, on
 * hold, rejected, with a note). An adopted one can open a request with a draft of it, which the
 * person sends or not. Before any assessment the part is empty but for the request for one; while
 * one runs, its mark opens its run. Earlier assessments are chosen in the history; nothing
 * compares them. The evidence chips serve the checks below too.
 */

import { useState } from "preact/hooks";
import type {
  Artifact,
  Assessment,
  AssessmentItem,
  AssessmentItemKind,
  AssessmentOverview,
  AssessScope,
  Evidence,
  ModelView,
  Review,
  ReviewJudgment,
  StatCut,
} from "../../shared/types.ts";
import { describeError } from "../api.ts";
import { Badge, type Tone } from "../components/badge.tsx";
import { Button } from "../components/button.tsx";
import { Card, CardHeader } from "../components/card.tsx";
import { Alert, Empty, Skeleton } from "../components/feedback.tsx";
import { Icon, type IconName } from "../components/icons.tsx";
import { Select } from "../components/select.tsx";
import { cx } from "../components/util.ts";
import { useUi, type Selection, type Ui } from "../context.ts";
import { dateTime } from "../format.ts";
import {
  InstanceLink,
  Markdown,
  pathTail,
  ProcessLink,
  processName,
  RunLink,
  StatusText,
  TypeLink,
} from "./common.tsx";

/** What the upper part shows: the overview's latest, the assessments recorded, and the Artifacts (for the paths cited). */
export interface AssessmentData {
  overview: AssessmentOverview;
  history: Assessment[];
  artifacts: Artifact[];
}

export type Loaded<T> =
  | { status: "loading" }
  | { status: "ok"; value: T }
  | { status: "error"; error: unknown };

/** Not amber (stale evidence) and not the colours of the judgments; unverified is grey. */
const ITEM_TONE: Record<AssessmentItemKind, Tone> = {
  description: "info",
  configuration: "neutral",
  operation: "brand",
  unverified: "outline",
};

const REVIEW_TONE: Record<ReviewJudgment, Tone> = {
  adopted: "brand",
  held: "outline",
  rejected: "danger",
};

const EVIDENCE_ICON: Record<string, IconName> = {
  run: "activity",
  instance: "layers",
  evaluation: "target",
  stat: "dashboard",
  log: "terminal",
  path: "file",
};

/** The dashboard's name of a number that a cut of the statistics cites, or the name as given. */
function metricLabel(t: Ui["t"], metric: string): string {
  switch (metric) {
    case "achievement":
      return t("metric.achievement");
    case "unverified":
      return t("metric.unverified");
    case "stale":
    case "staleEvaluations":
      return t("metric.stale");
    case "runSuccess":
      return t("metric.runSuccess");
    case "duration":
      return t("metric.duration");
    case "cost":
    case "usage":
      return t("metric.cost");
    default:
      return metric;
  }
}

/** A Process of a cut or a scope, by id or name, as the model has it. */
const processOf = (model: ModelView | null, key: string | undefined) =>
  key ? model?.processes.find((p) => p.id === key || p.name === key) : undefined;

/**
 * Where a cited path opens: a SKILL.md in its Process's panel, an Artifact (or a file inside a
 * directory Artifact) among its type's; `null` for a path that is neither.
 */
export function pathTarget(
  path: string,
  model: ModelView | null,
  artifacts: readonly Artifact[],
): Selection | null {
  const skilled = model?.processes.find(
    (p) => p.skill !== null && "path" in p.skill && p.skill.path === path,
  );
  if (skilled) return { kind: "process", id: skilled.id, tab: "skill" };
  const artifact =
    artifacts.find((a) => a.path === path) ??
    artifacts.find((a) => a.dir && path.startsWith(`${a.path}/`));
  return artifact ? { kind: "type", id: artifact.type, path: artifact.path } : null;
}

/** What an evidence chip says and does. */
function evidenceView(
  ui: Ui,
  evidence: Evidence,
  artifacts: readonly Artifact[],
  onCut: ((cut: StatCut) => void) | undefined,
): { kind: string; label: string; title: string; open: (() => void) | null } {
  const { t, model, select, instances, runs } = ui;
  if ("run" in evidence) {
    const run = runs.get(evidence.run);
    return {
      kind: "run",
      label: evidence.run,
      title: run ? `${evidence.run} · ${t(`status.${run.status}`)}` : evidence.run,
      open: () => select({ kind: "run", id: evidence.run }),
    };
  }
  if ("instance" in evidence || "evaluation" in evidence) {
    const id = "instance" in evidence ? evidence.instance : evidence.evaluation;
    const instance = instances.get(id);
    const first = instance ? Object.values(instance.inputs).flat()[0] : undefined;
    const title = instance
      ? t("evidence.instance", { process: processName(model, instance.process), path: first ?? "" })
      : id;
    return "instance" in evidence
      ? {
          kind: "instance",
          label: id,
          title,
          open: () => select({ kind: "instance", id }),
        }
      : {
          kind: "evaluation",
          label: t("evidence.evaluation", { instance: id }),
          title,
          open: () => select({ kind: "instance", id, tab: "evaluation" }),
        };
  }
  if ("log" in evidence) {
    const { run, n } = evidence.log;
    return {
      kind: "log",
      label: t("evidence.log", { run, n }),
      title: t("evidence.log", { run, n }),
      open: () => select({ kind: "run", id: run, line: n }),
    };
  }
  if ("path" in evidence) {
    const target = pathTarget(evidence.path, model, artifacts);
    return {
      kind: "path",
      label: pathTail(evidence.path),
      title: evidence.path,
      open: target ? () => select(target) : null,
    };
  }
  const { filter, metric } = evidence.stat;
  const process = processOf(model, filter.process);
  const parts = [
    metricLabel(t, metric),
    ...(filter.process ? [process?.name ?? filter.process] : []),
    ...(filter.agent
      ? [model?.agents.find((a) => a.id === filter.agent)?.label ?? filter.agent]
      : []),
    t(`period.${filter.period ?? "all"}`),
  ];
  return {
    kind: "stat",
    label: parts.join(" · "),
    title: parts.join(" · "),
    open: onCut ? () => onCut({ ...filter, ...(process ? { process: process.id } : {}) }) : null,
  };
}

/** A record that an item or a check rests on: it opens the record, or sets the filter below. */
export function EvidenceChip({
  evidence,
  artifacts,
  onCut,
}: {
  evidence: Evidence;
  artifacts: readonly Artifact[];
  onCut?: (cut: StatCut) => void;
}) {
  const ui = useUi();
  const view = evidenceView(ui, evidence, artifacts, onCut);
  const content = (
    <>
      <Icon name={EVIDENCE_ICON[view.kind] ?? "file"} size={12} />
      <span class={cx(view.kind !== "stat" && "mono")}>{view.label}</span>
    </>
  );
  return view.open ? (
    <button
      type="button"
      class="chip chip-evidence"
      data-evidence={view.kind}
      title={view.title}
      onClick={view.open}
    >
      {content}
    </button>
  ) : (
    <span class="chip chip-evidence is-static" data-evidence={view.kind} title={view.title}>
      {content}
    </span>
  );
}

/** The latest review of an item: where it stands; the earlier ones stay in the record. */
const reviewOf = (assessment: Assessment, n: number): Review | undefined =>
  assessment.reviews.filter((r) => r.n === n).at(-1);

/** The draft of a request from an adopted opportunity: the person edits and sends it, or not. */
function draftOf(
  ui: Ui,
  assessment: Assessment,
  item: AssessmentItem,
  artifacts: readonly Artifact[],
): string {
  const { t } = ui;
  const evidence = item.evidence
    .map((e) => {
      const view = evidenceView(ui, e, artifacts, undefined);
      return view.kind === "path" ? view.title : view.label;
    })
    .join(", ");
  const draft = t("opportunity.draft", {
    statement: item.statement,
    assessment: assessment.id,
    n: item.n,
    evidence,
  });
  return item.kind === "description"
    ? `${draft}\n${t("opportunity.description")}`
    : item.kind === "configuration"
      ? `${draft}\n${t("opportunity.configuration")}`
      : draft;
}

function Opportunity({
  assessment,
  item,
  artifacts,
  onCut,
}: {
  assessment: Assessment;
  item: AssessmentItem;
  artifacts: readonly Artifact[];
  onCut: (cut: StatCut) => void;
}) {
  const ui = useUi();
  const { t, language, model, instances, openForm } = ui;
  const review = reviewOf(assessment, item.n);
  const instance = item.subject.instance ? instances.get(item.subject.instance) : undefined;
  // An instance names its Process already.
  const process =
    item.subject.process &&
    item.subject.process !== instance?.process &&
    model?.processes.some((p) => p.id === item.subject.process)
      ? item.subject.process
      : undefined;
  const artifact =
    item.subject.artifact && model?.artifacts.some((a) => a.id === item.subject.artifact)
      ? item.subject.artifact
      : undefined;
  const agent = item.subject.agent;
  const subject = process || artifact || agent || item.subject.guidance || instance;
  return (
    <li
      class={cx("opportunity", item.kind === "unverified" && "is-unverified")}
      data-item={item.n}
      data-kind={item.kind}
    >
      <Badge tone={ITEM_TONE[item.kind]} class="opportunity-kind">
        {t(`itemKind.${item.kind}`)}
      </Badge>
      <div class="opportunity-body">
        {subject && (
          <div class="chips">
            {process && <ProcessLink id={process} />}
            {artifact && <TypeLink id={artifact} />}
            {instance && <InstanceLink instance={instance} />}
            {agent && (
              <span class="chip chip-agent">
                {model?.agents.find((a) => a.id === agent)?.label ?? agent}
              </span>
            )}
            {item.subject.guidance && (
              <EvidenceChip evidence={{ path: item.subject.guidance }} artifacts={artifacts} />
            )}
          </div>
        )}
        <p class="opportunity-statement">{item.statement}</p>
        {item.evidence.length > 0 && (
          <div class="chips evidence-chips" data-testid="evidence">
            {item.evidence.map((evidence, i) => (
              <EvidenceChip key={i} evidence={evidence} artifacts={artifacts} onCut={onCut} />
            ))}
          </div>
        )}
        {item.limits && (
          <p class="opportunity-limits small" title={t("instance.limits")}>
            {item.limits}
          </p>
        )}
        <div class="opportunity-review" data-review={review?.judgment ?? "none"}>
          {review && (
            <>
              <Badge tone={REVIEW_TONE[review.judgment]} dot>
                {t(`review.${review.judgment}`)}
              </Badge>
              <span class="faint small">
                {t("review.by", { at: dateTime(review.at, language) })}
              </span>
              {review.note && <span class="small review-note">{review.note}</span>}
            </>
          )}
        </div>
      </div>
      <div class="opportunity-actions">
        <Button
          variant="ghost"
          size="sm"
          data-testid="review-open"
          onClick={() => openForm({ kind: "review", assessment: assessment.id, n: item.n })}
        >
          {t("review.open")}
        </Button>
        {review?.judgment === "adopted" && (
          <Button
            variant="ghost"
            size="sm"
            data-testid="opportunity-request"
            onClick={() =>
              openForm({ kind: "request", draft: draftOf(ui, assessment, item, artifacts) })
            }
          >
            <Icon name="send" />
            {t("opportunity.request")}
          </Button>
        )}
      </div>
    </li>
  );
}

/** The band of the interpretation: whose it is, when, what it read, and its summary, quoted. */
function Interpretation({
  assessment,
  since,
}: {
  assessment: Assessment;
  /** For the latest: what the records gained since (an observation). */
  since: AssessmentOverview["since"];
}) {
  const { t, language, model, runs } = useUi();
  const { scope } = assessment;
  const agent = model?.agents.find((a) => a.id === assessment.agent)?.label ?? assessment.agent;
  const run = runs.get(assessment.runId);
  const process = processOf(model, scope.process);
  return (
    <figure
      class="assessment-quote"
      data-testid="assessment-latest"
      data-assessment={assessment.id}
    >
      <figcaption class="assessment-by">
        <span class="assessment-label">{t("assessment.interpretation")}</span>
        <span class="assessment-agent">{agent}</span>
        <span class="faint">{dateTime(assessment.at, language)}</span>
        <span class="summary-id">
          <RunLink id={assessment.runId} />
        </span>
        {run && run.status !== "succeeded" && run.status !== "running" && (
          <StatusText status={run.status} />
        )}
        {since && (
          <span
            class="assessment-since"
            title={t("assessment.sinceHint")}
            data-testid="assessment-since"
            data-runs={since.runs}
            data-judgments={since.judgments}
          >
            {t("assessment.since", since)}
          </span>
        )}
      </figcaption>
      <div class="chips assessment-scope">
        <span class="chip chip-scope">{t(`period.${scope.period ?? "all"}`)}</span>
        {process && <ProcessLink id={process.id} />}
        {scope.agent && (
          <span class="chip chip-agent">
            {model?.agents.find((a) => a.id === scope.agent)?.label ?? scope.agent}
          </span>
        )}
      </div>
      {scope.request && (
        <p class="assessment-pov" title={t("assessment.pointOfView")}>
          {scope.request}
        </p>
      )}
      <blockquote class="assessment-summary" data-testid="assessment-summary">
        <Markdown source={assessment.summary} />
      </blockquote>
    </figure>
  );
}

/**
 * The upper part of the analysis. `scope` is the filter below, which a new assessment reads;
 * `onCut` sets that filter to a cut of the statistics that an item cites.
 */
export function AssessmentSection({
  data,
  retry,
  scope,
  onCut,
}: {
  data: Loaded<AssessmentData>;
  retry: () => void;
  scope: AssessScope;
  onCut: (cut: StatCut) => void;
}) {
  const { t, language, model, runs, select, openForm } = useUi();
  const [chosen, setChosen] = useState<string | null>(null);
  const running = [...runs.values()].find((r) => r.kind === "assess" && r.status === "running");
  const latest = data.status === "ok" ? data.value.overview.latest : null;
  // The history lists the assessments whose run has ended; the one being made is not shown yet.
  const history =
    data.status === "ok"
      ? data.value.history.filter((a) => runs.get(a.runId)?.status !== "running")
      : [];
  const shown =
    (chosen !== null ? history.find((a) => a.id === chosen) : undefined) ?? latest ?? undefined;
  const artifacts = data.status === "ok" ? data.value.artifacts : [];
  const ask = (
    <Button
      variant="outline"
      size="sm"
      data-testid="assess-open"
      disabled={!model || running !== undefined}
      onClick={() => openForm({ kind: "assess", scope })}
    >
      <Icon name="search" />
      {t("assessment.ask")}
    </Button>
  );
  const mark = running && (
    <button
      type="button"
      class="assessment-running"
      data-testid="assessment-running"
      data-run={running.id}
      title={t("assessment.running")}
      onClick={() => select({ kind: "run", id: running.id })}
    >
      <StatusText status="running" />
    </button>
  );
  return (
    <Card
      class="assessment-card"
      data-testid="assessment"
      data-state={shown ? "shown" : data.status === "ok" ? "empty" : data.status}
    >
      <CardHeader
        title={t("assessment.title")}
        icon={<Icon name="search" />}
        actions={
          (mark || shown) && (
            <>
              {mark}
              {shown && history.length > 1 && (
                <Select
                  label={t("assessment.history")}
                  value={shown.id}
                  size="sm"
                  icon={<Icon name="history" />}
                  options={history.map((a) => ({
                    value: a.id,
                    label: dateTime(a.at, language),
                    hint: model?.agents.find((agent) => agent.id === a.agent)?.label ?? a.agent,
                  }))}
                  onChange={setChosen}
                  testid="assessment-history"
                />
              )}
              {shown && ask}
            </>
          )
        }
      />
      <div class="card-body">
        {data.status === "loading" && (
          <div class="loading" role="status">
            <span class="sr-only">{t("loading")}</span>
            <Skeleton width="70%" />
            <Skeleton width="54%" />
          </div>
        )}
        {data.status === "error" && (
          <Alert
            tone="danger"
            title={t("assessment.error")}
            action={
              <Button variant="outline" size="sm" onClick={retry}>
                {t("retry")}
              </Button>
            }
          >
            {describeError(data.error, language)}
          </Alert>
        )}
        {data.status === "ok" && !shown && (
          <Empty
            icon="search"
            title={t("assessment.empty")}
            action={ask}
            class="assessment-empty"
          />
        )}
        {shown && (
          <>
            <Interpretation
              assessment={shown}
              since={
                shown.id === latest?.id && data.status === "ok" ? data.value.overview.since : null
              }
            />
            {shown.items.length === 0 ? (
              <p class="faint small">{t("assessment.noItems")}</p>
            ) : (
              <ol class="opportunities" data-testid="opportunities">
                {shown.items.map((item) => (
                  <Opportunity
                    key={item.n}
                    assessment={shown}
                    item={item}
                    artifacts={artifacts}
                    onCut={onCut}
                  />
                ))}
              </ol>
            )}
          </>
        )}
      </div>
    </Card>
  );
}
