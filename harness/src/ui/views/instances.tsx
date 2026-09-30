/*
 * The instances: each application of a Process to concrete inputs, with the facts that the harness
 * records about it (its latest run, the judgments, whether their evidence is stale), newest
 * activity first. Filters by Process, by the latest run's result, by whether it is judged, and by
 * a part of an input or output path. A row opens the instance in the panel.
 */

import { useState } from "preact/hooks";
import type { InstanceView, RunStatus } from "../../shared/types.ts";
import { useUi } from "../context.ts";
import { dateTime } from "../format.ts";
import { firstInput, Glyphs, processName, StatusText, updatedAt } from "./common.tsx";

type StatusFilter = "" | RunStatus | "none";
type JudgmentFilter = "" | "judged" | "unjudged" | "stale";

let kept = { process: "", status: "" as StatusFilter, judgment: "" as JudgmentFilter, path: "" };

const STATUSES: RunStatus[] = ["running", "succeeded", "failed", "canceled", "interrupted"];

const mentions = (instance: InstanceView, part: string): boolean =>
  Object.values(instance.inputs).some((paths) => paths.some((p) => p.includes(part))) ||
  Object.values(instance.outputs).some((p) => p !== null && p.includes(part));

export function InstancesView() {
  const { model, instances, runs, t, language, select } = useUi();
  const [filter, setFilterState] = useState(kept);
  const setFilter = (next: Partial<typeof kept>): void => {
    kept = { ...filter, ...next };
    setFilterState(kept);
  };

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

  return (
    <div class="instances" data-testid="instances">
      <div class="filters">
        <label>
          {t("filter.process")}
          <select
            value={filter.process}
            onChange={(e) => setFilter({ process: (e.currentTarget as HTMLSelectElement).value })}
          >
            <option value="">{t("filter.all")}</option>
            {model?.processes.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          {t("instances.status")}
          <select
            value={filter.status}
            onChange={(e) =>
              setFilter({ status: (e.currentTarget as HTMLSelectElement).value as StatusFilter })
            }
          >
            <option value="">{t("instances.any")}</option>
            {STATUSES.map((s) => (
              <option key={s} value={s}>
                {t(`status.${s}`)}
              </option>
            ))}
            <option value="none">{t("instances.notRun")}</option>
          </select>
        </label>
        <label>
          {t("instances.judgment")}
          <select
            value={filter.judgment}
            onChange={(e) =>
              setFilter({
                judgment: (e.currentTarget as HTMLSelectElement).value as JudgmentFilter,
              })
            }
          >
            <option value="">{t("instances.any")}</option>
            <option value="judged">{t("instances.judged")}</option>
            <option value="unjudged">{t("instances.unjudged")}</option>
            <option value="stale">{t("instances.staleOnly")}</option>
          </select>
        </label>
        <label>
          {t("instances.path")}
          <input
            type="search"
            value={filter.path}
            onInput={(e) => setFilter({ path: (e.currentTarget as HTMLInputElement).value })}
          />
        </label>
        <span class="spacer" />
        <span class="muted">{t("instances.count", { n: shown.length, total: all.length })}</span>
        <button type="button" class="primary" onClick={() => select({ kind: "new" })}>
          {t("process.newInstance")}
        </button>
      </div>
      {all.length === 0 ? (
        <p class="muted pad">{t("instances.empty")}</p>
      ) : shown.length === 0 ? (
        <p class="muted pad">{t("instances.none")}</p>
      ) : (
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>{t("col.process")}</th>
                <th>{t("col.firstInput")}</th>
                <th>{t("col.latestRun")}</th>
                <th>{t("col.judgments")}</th>
                <th>{t("col.evidence")}</th>
                <th>{t("col.updated")}</th>
              </tr>
            </thead>
            <tbody>
              {shown.map((instance) => {
                const status = statusOf(instance);
                const outcomes =
                  model?.processes.find((p) => p.id === instance.process)?.outcomes.length ?? 0;
                const at = updatedAt(instance);
                return (
                  <tr
                    key={instance.id}
                    class="clickable"
                    data-instance={instance.id}
                    tabindex={0}
                    onClick={() => select({ kind: "instance", id: instance.id })}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") select({ kind: "instance", id: instance.id });
                    }}
                  >
                    <td class="strong">{processName(model, instance.process)}</td>
                    <td class="path" title={firstInput(model, instance) ?? ""}>
                      {firstInput(model, instance) ?? t("instance.notYet")}
                    </td>
                    <td>
                      {status ? (
                        <StatusText status={status} />
                      ) : (
                        <span class="muted">{t("instances.notRun")}</span>
                      )}
                    </td>
                    <td>
                      <Glyphs judgments={instance.facts.judgments} outcomes={outcomes} />
                    </td>
                    <td>
                      {!instance.evaluation ? (
                        <span class="muted">{t("none")}</span>
                      ) : instance.facts.stale ? (
                        <span class="stale-text">{t("instances.stale")}</span>
                      ) : (
                        <span class="muted">{t("instances.currentEvidence")}</span>
                      )}
                    </td>
                    <td class="muted nowrap">{at > 0 ? dateTime(at, language) : t("none")}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
