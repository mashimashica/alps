/*
 * The instances: each application of a Process to concrete inputs, with the facts that the harness
 * records about it (its latest run, the judgments, whether their evidence is stale), newest
 * activity first. Filters by Process, by the latest run's result, by whether it is judged, and by
 * a part of an input or output path; the counts at the top right set these filters too. Cards
 * are grouped by the latest run, independently of Outcome judgments, and open the detail panel.
 * The two are told apart by place and shape, not in words: a card's lane is its latest run's
 * result, and its Judgments row carries one mark per Outcome (● × ○ ·) and the amber mark of
 * stale evidence. A card names its Process and the end of its first input path (the whole path
 * in the title); its id is in the detail. A card that a woken agent made for a request carries
 * the request's mark, a link to that wake's record.
 */

import type { InstanceView, RunStatus } from "../../shared/types.ts";
import { Badge } from "../components/badge.tsx";
import { Button } from "../components/button.tsx";
import { Card } from "../components/card.tsx";
import { Empty, Skeleton } from "../components/feedback.tsx";
import { Icon } from "../components/icons.tsx";
import { Field, Input } from "../components/input.tsx";
import { Select } from "../components/select.tsx";
import { NO_FILTER, useUi, type InstanceFilter } from "../context.ts";
import { dateTime } from "../format.ts";
import {
  firstInputOf,
  Glyphs,
  ModelProblem,
  Path,
  pathTail,
  processName,
  StatusText,
  typeName,
  updatedAt,
} from "./common.tsx";

const LANES = [
  { id: "not-run", title: "instances.notRun", icon: "layers" },
  { id: "running", title: "status.running", icon: "play" },
  { id: "succeeded", title: "status.succeeded", icon: "check" },
  { id: "stopped", title: "board.stopped", icon: "alert" },
] as const;

type Lane = (typeof LANES)[number]["id"];
const LANE_OF: Record<RunStatus, Lane> = {
  running: "running",
  succeeded: "succeeded",
  failed: "stopped",
  canceled: "stopped",
  interrupted: "stopped",
};

const STATUSES: RunStatus[] = ["running", "succeeded", "failed", "canceled", "interrupted"];

const mentions = (instance: InstanceView, part: string): boolean =>
  Object.values(instance.inputs).some((paths) => paths.some((p) => p.includes(part))) ||
  Object.values(instance.outputs).some((p) => p !== null && p.includes(part));

const filtered = (filter: InstanceFilter): boolean =>
  filter.process !== "" || filter.status !== "" || filter.judgment !== "" || filter.path !== "";

export function InstancesView({ modelError }: { modelError: unknown }) {
  const {
    model,
    instances,
    runs,
    t,
    language,
    select,
    selection,
    recordsLoaded,
    instanceFilter: filter,
    setInstanceFilter: setFilter,
    openForm,
  } = useUi();

  if (!model && modelError) return <ModelProblem error={modelError} />;

  const all = [...instances.values()].sort(
    (a, b) => updatedAt(b) - updatedAt(a) || b.id.localeCompare(a.id, "en", { numeric: true }),
  );
  const statusOf = (instance: InstanceView): RunStatus | null => {
    const latest = instance.facts.latestRun;
    return latest ? (runs.get(latest.id) ?? latest).status : null;
  };
  const shown = all.filter((instance) => {
    if (filter.process && instance.process !== filter.process) return false;
    const status = statusOf(instance);
    if (filter.status === "none" ? status !== null : filter.status && status !== filter.status)
      return false;
    if (filter.judgment === "judged" && !instance.evaluation) return false;
    if (filter.judgment === "unjudged" && instance.evaluation) return false;
    if (filter.judgment === "stale" && !instance.facts.stale) return false;
    if (filter.path && !mentions(instance, filter.path)) return false;
    return true;
  });
  const lanes = new Map<Lane, InstanceView[]>(LANES.map(({ id }) => [id, []]));
  for (const instance of shown) {
    const status = statusOf(instance);
    lanes.get(status ? LANE_OF[status] : "not-run")?.push(instance);
  }
  const selected = selection?.kind === "instance" ? selection.id : null;
  const any = { value: "" as const, label: t("instances.any") };

  return (
    <div class="instances" data-testid="instances">
      <div class="toolbar filters">
        <Field label={t("filter.process")}>
          {(control) => (
            <Select
              id={control.id}
              labelledBy={control.labelId}
              value={filter.process}
              icon={<Icon name="network" />}
              options={[
                { value: "", label: t("filter.allProcesses") },
                ...(model?.processes ?? []).map((p) => ({ value: p.id, label: p.name })),
              ]}
              onChange={(process) => setFilter({ process })}
            />
          )}
        </Field>
        <Field label={t("instances.status")}>
          {(control) => (
            <Select
              id={control.id}
              labelledBy={control.labelId}
              value={filter.status}
              options={[
                any,
                ...STATUSES.map((s) => ({ value: s, label: t(`status.${s}`) })),
                { value: "none" as const, label: t("instances.notRun") },
              ]}
              onChange={(status) => setFilter({ status })}
            />
          )}
        </Field>
        <Field label={t("instances.judgment")}>
          {(control) => (
            <Select
              id={control.id}
              labelledBy={control.labelId}
              value={filter.judgment}
              options={[
                any,
                { value: "judged" as const, label: t("instances.judged") },
                { value: "unjudged" as const, label: t("instances.unjudged") },
                { value: "stale" as const, label: t("instances.staleOnly") },
              ]}
              onChange={(judgment) => setFilter({ judgment })}
            />
          )}
        </Field>
        <Field label={t("instances.path")} class="field-grow">
          {(control) => (
            <Input
              id={control.id}
              type="search"
              icon="search"
              placeholder={t("instances.pathPlaceholder")}
              value={filter.path}
              onInput={(event) => setFilter({ path: event.currentTarget.value })}
            />
          )}
        </Field>
        {/* How many match shows only while the filters leave some out. */}
        <div class="toolbar-end" aria-live="polite">
          {filtered(filter) && (
            <>
              <span class="faint small tabular" data-testid="instances-count">
                {t("instances.count", { n: shown.length, total: all.length })}
              </span>
              <Button variant="ghost" size="sm" onClick={() => setFilter(NO_FILTER)}>
                <Icon name="x" />
                {t("instances.clear")}
              </Button>
            </>
          )}
        </div>
      </div>
      {recordsLoaded && (all.length === 0 || shown.length === 0) && (
        <Card class="instance-board-empty">
          <Empty
            icon={all.length === 0 ? "layers" : "search"}
            title={t(all.length === 0 ? "instances.empty" : "instances.none")}
            action={
              all.length === 0 ? (
                <Button onClick={() => openForm({ kind: "request" })}>
                  <Icon name="send" />
                  {t("request.open")}
                </Button>
              ) : (
                <Button variant="outline" onClick={() => setFilter(NO_FILTER)}>
                  {t("instances.clear")}
                </Button>
              )
            }
          />
        </Card>
      )}
      <div
        class="instance-board"
        data-testid="instance-board"
        role="region"
        aria-label={t("board.label")}
        tabindex={0}
        aria-busy={!recordsLoaded}
      >
        {!recordsLoaded && (
          <span class="sr-only" role="status">
            {t("loading")}
          </span>
        )}
        {LANES.map((lane) => {
          const members = lanes.get(lane.id) ?? [];
          const titleId = `instance-lane-${lane.id}`;
          return (
            <section
              key={lane.id}
              class="instance-lane"
              data-lane={lane.id}
              aria-labelledby={titleId}
            >
              <header class="instance-lane-heading">
                <span class="instance-lane-icon">
                  <Icon name={lane.icon} size={15} />
                </span>
                <h3 id={titleId}>{t(lane.title)}</h3>
                <span class="instance-lane-count tabular">
                  {recordsLoaded ? members.length : "—"}
                </span>
              </header>
              {!recordsLoaded ? (
                <div class="instance-lane-loading">
                  {[0, 1].map((i) => (
                    <div key={i} class="instance-card-skeleton">
                      <Skeleton height="10px" width="30%" />
                      <Skeleton height="16px" width="76%" />
                      <Skeleton height="32px" width="100%" />
                      <Skeleton height="10px" width="55%" />
                    </div>
                  ))}
                </div>
              ) : members.length === 0 ? null : (
                <ol class="instance-lane-cards">
                  {members.map((instance) => {
                    const status = statusOf(instance);
                    const outcomes =
                      model?.processes.find((p) => p.id === instance.process)?.outcomes.length ?? 0;
                    const at = updatedAt(instance);
                    const input = firstInputOf(model, instance);
                    const name = processName(model, instance.process);
                    const origin = instance.createdBy?.run ?? null;
                    return (
                      <li key={instance.id} class={origin ? "has-origin" : undefined}>
                        <button
                          type="button"
                          class="instance-card"
                          data-instance={instance.id}
                          data-selected={selected === instance.id ? "true" : undefined}
                          aria-label={t("board.open", { process: name, id: instance.id })}
                          onClick={() => select({ kind: "instance", id: instance.id })}
                        >
                          <span class="instance-card-head">
                            <strong class="instance-card-title">{name}</strong>
                            {/* The lane is the result; only the stopped lane holds several. */}
                            {status && lane.id === "stopped" && <StatusText status={status} />}
                          </span>
                          <span
                            class="instance-card-path"
                            title={
                              input ? `${typeName(model, input.type)}: ${input.path}` : undefined
                            }
                          >
                            <Icon name="file" size={13} />
                            <span class="mono">
                              {input ? <Path path={pathTail(input.path)} /> : t("instance.notYet")}
                            </span>
                          </span>
                          {/* Not judged yet: a dash, as in the panel. */}
                          <span class="instance-card-fact">
                            <span class="instance-card-fact-label">{t("col.judgments")}</span>
                            <Glyphs judgments={instance.facts.judgments} outcomes={outcomes} />
                            {instance.evaluation && instance.facts.stale && (
                              <Badge tone="warning" dot class="instance-card-stale">
                                {t("instances.staleOnly")}
                              </Badge>
                            )}
                          </span>
                          <span class="instance-card-footer">
                            <span
                              title={
                                at > 0
                                  ? `${t("col.updated")}: ${dateTime(at, language)}`
                                  : undefined
                              }
                            >
                              <Icon name="clock" size={12} />
                              {at > 0 ? (
                                <time dateTime={new Date(at).toISOString()}>
                                  {dateTime(at, language)}
                                </time>
                              ) : (
                                t("none")
                              )}
                            </span>
                            {origin && (
                              <span class="instance-card-origin-space" aria-hidden="true" />
                            )}
                            <Icon name="chevronRight" size={14} />
                          </span>
                        </button>
                        {/* Beside the card, not in it (a button cannot hold another): the wake that
                            made it, as the request's mark; its id is in the title. */}
                        {origin && (
                          <button
                            type="button"
                            class="instance-card-origin"
                            data-origin={origin}
                            aria-label={t("board.origin", { run: origin })}
                            title={t("board.origin", { run: origin })}
                            onClick={() => select({ kind: "run", id: origin })}
                          >
                            <Icon name="send" size={12} />
                          </button>
                        )}
                      </li>
                    );
                  })}
                </ol>
              )}
            </section>
          );
        })}
      </div>
    </div>
  );
}
