/*
 * The instances: each application of a Process to concrete inputs, with the facts that the harness
 * records about it (its latest run, the judgments, whether their evidence is stale), newest
 * activity first. Filters by Process, by the latest run's result, by whether it is judged, and by
 * a part of an input or output path; the counts at the top right set these filters too. A row
 * opens the instance in the panel.
 */

import type { InstanceView, RunStatus } from "../../shared/types.ts";
import { Badge } from "../components/badge.tsx";
import { Button } from "../components/button.tsx";
import { Card } from "../components/card.tsx";
import { Empty, Skeleton } from "../components/feedback.tsx";
import { Icon } from "../components/icons.tsx";
import { Field, Input } from "../components/input.tsx";
import { Select } from "../components/select.tsx";
import { rowActions, Table } from "../components/table.tsx";
import { NO_FILTER, useUi, type InstanceFilter } from "../context.ts";
import { dateTime } from "../format.ts";
import { firstInput, Glyphs, ModelProblem, processName, StatusText, updatedAt } from "./common.tsx";

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
        <div class="toolbar-end">
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
      </div>
      <Card class="table-card">
        {!recordsLoaded ? (
          <div class="table-loading" role="status">
            <span class="sr-only">{t("loading")}</span>
            {Array.from({ length: 5 }, (_, i) => (
              <Skeleton key={i} height="18px" width={`${96 - i * 7}%`} />
            ))}
          </div>
        ) : all.length === 0 ? (
          <Empty
            icon="layers"
            title={t("instances.empty")}
            action={
              <Button onClick={() => openForm({ kind: "new" })}>
                <Icon name="plus" />
                {t("process.newInstance")}
              </Button>
            }
          />
        ) : shown.length === 0 ? (
          <Empty
            icon="search"
            title={t("instances.none")}
            action={
              <Button variant="outline" onClick={() => setFilter(NO_FILTER)}>
                {t("instances.clear")}
              </Button>
            }
          />
        ) : (
          <Table label={t("tab.instances")} class="instance-table">
            <thead role="rowgroup">
              <tr role="row">
                <th role="columnheader">{t("col.process")}</th>
                <th role="columnheader">{t("col.firstInput")}</th>
                <th role="columnheader">{t("col.latestRun")}</th>
                <th role="columnheader">{t("col.judgments")}</th>
                <th role="columnheader">{t("col.evidence")}</th>
                <th role="columnheader">{t("col.updated")}</th>
              </tr>
            </thead>
            <tbody role="rowgroup">
              {shown.map((instance) => {
                const status = statusOf(instance);
                const outcomes =
                  model?.processes.find((p) => p.id === instance.process)?.outcomes.length ?? 0;
                const at = updatedAt(instance);
                const input = firstInput(model, instance);
                return (
                  <tr
                    key={instance.id}
                    role="row"
                    data-instance={instance.id}
                    data-selected={selected === instance.id ? "true" : undefined}
                    {...rowActions(() => select({ kind: "instance", id: instance.id }))}
                  >
                    <td role="cell" class="cell-name">
                      <span class="cell-title">{processName(model, instance.process)}</span>
                      <span class="cell-id mono faint">{instance.id}</span>
                    </td>
                    <td role="cell" class="cell-path mono" title={input ?? ""}>
                      {input ?? <span class="faint">{t("instance.notYet")}</span>}
                    </td>
                    <td role="cell" class="cell-status">
                      {status ? (
                        <StatusText status={status} />
                      ) : (
                        <span class="faint">{t("instances.notRun")}</span>
                      )}
                    </td>
                    <td role="cell" class="cell-judgments">
                      <Glyphs judgments={instance.facts.judgments} outcomes={outcomes} />
                    </td>
                    <td role="cell" class="cell-evidence">
                      {!instance.evaluation ? (
                        <span class="faint">{t("none")}</span>
                      ) : instance.facts.stale ? (
                        <Badge tone="warning" dot>
                          {t("instances.stale")}
                        </Badge>
                      ) : (
                        <span class="muted">{t("instances.currentEvidence")}</span>
                      )}
                    </td>
                    <td role="cell" class="cell-updated faint nowrap tabular">
                      {at > 0 ? dateTime(at, language) : t("none")}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </Table>
        )}
      </Card>
    </div>
  );
}
