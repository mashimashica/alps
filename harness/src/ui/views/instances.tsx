/*
 * The instances: each application of a Process to concrete inputs, with the facts that the harness
 * records about it (its latest run, the judgments, whether their evidence is stale), newest
 * activity first. Filters by Process, by the latest run's result, by whether it is judged, and by
 * a part of an input or output path; the counts at the top right set these filters too. Cards
 * are grouped by the latest run, independently of Outcome judgments, and open the detail panel.
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
import { firstInput, Glyphs, ModelProblem, processName, StatusText, updatedAt } from "./common.tsx";

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
      </div>
      <div class="instance-board-heading">
        <div class="instance-board-view">
          <Icon name="board" />
          <span>{t("board.label")}</span>
        </div>
        <p>{t("board.hint")}</p>
        <div class="instance-board-actions">
          <span class="faint small tabular" aria-live="polite">
            {t("instances.count", { n: shown.length, total: all.length })}
          </span>
          {filtered(filter) && (
            <Button variant="ghost" size="sm" onClick={() => setFilter(NO_FILTER)}>
              <Icon name="x" />
              {t("instances.clear")}
            </Button>
          )}
        </div>
        <span class="instance-board-order">
          <Icon name="clock" size={13} />
          {t("board.order")}
        </span>
      </div>
      {recordsLoaded && (all.length === 0 || shown.length === 0) && (
        <Card class="instance-board-empty">
          <Empty
            icon={all.length === 0 ? "layers" : "search"}
            title={t(all.length === 0 ? "instances.empty" : "instances.none")}
            action={
              all.length === 0 ? (
                <Button onClick={() => openForm({ kind: "new" })}>
                  <Icon name="plus" />
                  {t("process.newInstance")}
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
              ) : members.length === 0 ? (
                <div class="instance-lane-empty">
                  <span>
                    <Icon name={lane.icon} size={21} />
                  </span>
                  <p>{t("board.emptyLane")}</p>
                </div>
              ) : (
                <ol class="instance-lane-cards">
                  {members.map((instance) => {
                    const status = statusOf(instance);
                    const outcomes =
                      model?.processes.find((p) => p.id === instance.process)?.outcomes.length ?? 0;
                    const at = updatedAt(instance);
                    const input = firstInput(model, instance);
                    const name = processName(model, instance.process);
                    return (
                      <li key={instance.id}>
                        <button
                          type="button"
                          class="instance-card"
                          data-instance={instance.id}
                          data-selected={selected === instance.id ? "true" : undefined}
                          aria-label={t("board.open", { process: name, id: instance.id })}
                          onClick={() => select({ kind: "instance", id: instance.id })}
                        >
                          <span class="instance-card-meta">
                            <span class="instance-card-id mono">{instance.id}</span>
                            {status ? (
                              <StatusText status={status} />
                            ) : (
                              <Badge tone="outline">{t("instances.notRun")}</Badge>
                            )}
                          </span>
                          <strong class="instance-card-title">{name}</strong>
                          <span class="instance-card-path" title={input ?? ""}>
                            <Icon name="file" size={14} />
                            <span class="mono">{input ?? t("instance.notYet")}</span>
                          </span>
                          <span class="instance-card-facts">
                            <span class="instance-card-fact">
                              <span>{t("col.judgments")}</span>
                              {instance.facts.judgments ? (
                                <Glyphs judgments={instance.facts.judgments} outcomes={outcomes} />
                              ) : (
                                <span class="instance-card-unjudged">
                                  {t("instances.unjudged")}
                                </span>
                              )}
                            </span>
                            <span class="instance-card-fact">
                              <span>{t("col.evidence")}</span>
                              {!instance.evaluation ? (
                                <span>{t("none")}</span>
                              ) : instance.facts.stale ? (
                                <Badge tone="warning" dot>
                                  {t("instances.staleOnly")}
                                </Badge>
                              ) : (
                                <span class="instance-card-current">
                                  {t("instances.currentEvidence")}
                                </span>
                              )}
                            </span>
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
                            <Icon name="chevronRight" size={14} />
                          </span>
                        </button>
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
