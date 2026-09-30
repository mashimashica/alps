/*
 * What a person writes in the WebUI. Instantiation (framework §7): the Process, the concrete
 * inputs of each type (Artifacts found in its locations, or other paths), where each output goes
 * (or the agent decides), and, in free text, what each Outcome means in this application and how
 * to check it. Evaluation: the three-valued judgment of each Outcome with its evidence and
 * limits, and a Markdown note. Who judged is not sent: the harness records a person for the WebUI.
 */

import { useEffect, useState } from "preact/hooks";
import type {
  Artifact,
  ArtifactsResponse,
  InstanceResponse,
  Judgment,
  OutcomeCriterion,
} from "../../shared/types.ts";
import { useUi } from "../context.ts";
import { PanelHead, processName, typeName } from "./common.tsx";

const JUDGMENTS: Judgment[] = ["achieved", "not-achieved", "unverified"];

/** The criteria of each Outcome as text fields; empty statements are left out when saved. */
type CriteriaDraft = { statement: string; checks: string }[];

const draftOf = (outcomes: number, criteria: readonly OutcomeCriterion[]): CriteriaDraft =>
  Array.from({ length: outcomes }, (_, outcome) => {
    const found = criteria.find((c) => c.outcome === outcome);
    return { statement: found?.statement ?? "", checks: found?.checks ?? "" };
  });

const criteriaOf = (draft: CriteriaDraft): OutcomeCriterion[] =>
  draft.flatMap((c, outcome) =>
    c.statement.trim()
      ? [
          {
            outcome,
            statement: c.statement.trim(),
            ...(c.checks.trim() ? { checks: c.checks.trim() } : {}),
          },
        ]
      : [],
  );

function CriteriaFields({
  outcomes,
  draft,
  setDraft,
}: {
  outcomes: readonly string[];
  draft: CriteriaDraft;
  setDraft: (draft: CriteriaDraft) => void;
}) {
  const { t } = useUi();
  const change = (i: number, key: "statement" | "checks", value: string): void =>
    setDraft(draft.map((c, k) => (k === i ? { ...c, [key]: value } : c)));
  return (
    <fieldset class="criteria">
      <legend>{t("new.criteria")}</legend>
      {outcomes.map((outcome, i) => (
        <div key={i} class="criterion">
          <p class="small">
            <strong>{i + 1}.</strong> {outcome}
          </p>
          <label>
            {t("new.statement")}
            <textarea
              rows={2}
              value={draft[i]?.statement ?? ""}
              onInput={(e) =>
                change(i, "statement", (e.currentTarget as HTMLTextAreaElement).value)
              }
            />
          </label>
          <label>
            {t("new.checks")}
            <input
              type="text"
              value={draft[i]?.checks ?? ""}
              onInput={(e) => change(i, "checks", (e.currentTarget as HTMLInputElement).value)}
            />
          </label>
        </div>
      ))}
    </fieldset>
  );
}

/** The paths chosen for one input type: Artifacts found in its locations, and others typed in. */
function InputChoice({
  type,
  control,
  found,
  chosen,
  setChosen,
}: {
  type: string;
  control: boolean;
  found: readonly Artifact[];
  chosen: readonly string[];
  setChosen: (paths: string[]) => void;
}) {
  const { t, model } = useUi();
  const [other, setOther] = useState("");
  const candidates = found.map((a) => `${a.path}${a.dir ? "/" : ""}`);
  const extra = chosen.filter((p) => !candidates.includes(p));
  const toggle = (path: string, on: boolean): void =>
    setChosen(on ? [...chosen, path] : chosen.filter((p) => p !== path));
  const add = (): void => {
    const path = other.trim();
    if (path && !chosen.includes(path)) setChosen([...chosen, path]);
    setOther("");
  };
  return (
    <div class="choice" data-input-type={type}>
      <div class="choice-head">
        <strong>{typeName(model, type)}</strong>
        {control && <span class="muted small"> · {t("new.control")}</span>}
      </div>
      {candidates.length === 0 && <p class="muted small">{t("new.none")}</p>}
      {candidates.map((path) => (
        <label key={path} class="check">
          <input
            type="checkbox"
            checked={chosen.includes(path)}
            onChange={(e) => toggle(path, (e.currentTarget as HTMLInputElement).checked)}
          />
          <span class="mono small">{path}</span>
        </label>
      ))}
      {extra.map((path) => (
        <label key={path} class="check">
          <input
            type="checkbox"
            checked
            onChange={() => toggle(path, false)}
            aria-label={t("new.remove", { path })}
          />
          <span class="mono small">{path}</span>
        </label>
      ))}
      <div class="inline">
        <input
          type="text"
          placeholder={t("new.path")}
          aria-label={`${typeName(model, type)}: ${t("new.path")}`}
          value={other}
          onInput={(e) => setOther((e.currentTarget as HTMLInputElement).value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault();
              add();
            }
          }}
        />
        <button type="button" class="secondary" onClick={add}>
          {t("new.add")}
        </button>
      </div>
    </div>
  );
}

export function InstantiateForm({ process: initial }: { process?: string | undefined }) {
  const { model, t, client, select, putInstance, fail } = useUi();
  const [processId, setProcessId] = useState(initial ?? "");
  const [found, setFound] = useState<Artifact[]>([]);
  const [inputs, setInputs] = useState<Record<string, string[]>>({});
  const [outputs, setOutputs] = useState<Record<string, string>>({});
  const [criteria, setCriteria] = useState<CriteriaDraft>([]);
  const [notes, setNotes] = useState("");
  const [saving, setSaving] = useState(false);
  const process = model?.processes.find((p) => p.id === processId);

  useEffect(() => setProcessId(initial ?? ""), [initial]);
  useEffect(() => {
    setInputs({});
    setOutputs({});
    setCriteria(draftOf(process?.outcomes.length ?? 0, []));
  }, [processId]);
  useEffect(() => {
    client
      .get<ArtifactsResponse>("/api/artifacts")
      .then((answer) => setFound(answer.artifacts), fail);
  }, []);

  if (!model) return null;
  const types = process
    ? [
        ...process.inputs.map((type) => ({ type, control: false })),
        ...process.controls
          .filter((c) => !process.inputs.includes(c))
          .map((type) => ({ type, control: true })),
      ]
    : [];
  const create = (): void => {
    if (!process) return;
    setSaving(true);
    const given = Object.fromEntries(
      Object.entries(inputs).filter(([, paths]) => paths.length > 0),
    );
    const places = Object.fromEntries(
      process.outputs.map((type) => [
        type,
        outputs[type]?.trim() ? (outputs[type] ?? "").trim() : null,
      ]),
    );
    client
      .post<InstanceResponse>("/api/instances", {
        process: process.id,
        inputs: given,
        outputs: places,
        criteria: criteriaOf(criteria),
        notes,
      })
      .then((answer) => {
        putInstance(answer.instance);
        select({ kind: "instance", id: answer.instance.id });
      }, fail)
      .finally(() => setSaving(false));
  };
  return (
    <form
      class="form"
      data-testid="instantiate"
      onSubmit={(e) => {
        e.preventDefault();
        create();
      }}
    >
      <PanelHead kicker={t("panel.instance")} title={t("new.title")} />
      <label>
        {t("new.process")}
        <select
          value={processId}
          onChange={(e) => setProcessId((e.currentTarget as HTMLSelectElement).value)}
        >
          <option value="">{t("new.choose")}</option>
          {model.processes.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name}
            </option>
          ))}
        </select>
      </label>
      {process && (
        <>
          {process.purpose && <p class="muted small">{process.purpose}</p>}
          <fieldset>
            <legend>{t("new.inputs")}</legend>
            {types.map(({ type, control }) => (
              <InputChoice
                key={type}
                type={type}
                control={control}
                found={found.filter((a) => a.type === type)}
                chosen={inputs[type] ?? []}
                setChosen={(paths) => setInputs({ ...inputs, [type]: paths })}
              />
            ))}
          </fieldset>
          <fieldset>
            <legend>{t("new.outputs")}</legend>
            {process.outputs.map((type) => {
              const list = `outputs-${type.replace(/\W+/g, "-")}`;
              const pattern = model.artifacts.find((a) => a.id === type)?.paths[0] ?? "";
              return (
                <label key={type}>
                  {typeName(model, type)}
                  <input
                    type="text"
                    list={list}
                    placeholder={
                      pattern ? `${t("new.agentDecides")} (${pattern})` : t("new.agentDecides")
                    }
                    value={outputs[type] ?? ""}
                    onInput={(e) =>
                      setOutputs({
                        ...outputs,
                        [type]: (e.currentTarget as HTMLInputElement).value,
                      })
                    }
                  />
                  <datalist id={list}>
                    {found
                      .filter((a) => a.type === type)
                      .map((a) => (
                        <option key={a.path} value={`${a.path}${a.dir ? "/" : ""}`} />
                      ))}
                  </datalist>
                </label>
              );
            })}
          </fieldset>
          <CriteriaFields outcomes={process.outcomes} draft={criteria} setDraft={setCriteria} />
          <label>
            {t("new.notes")}
            <textarea
              rows={3}
              value={notes}
              onInput={(e) => setNotes((e.currentTarget as HTMLTextAreaElement).value)}
            />
          </label>
          <div class="actions">
            <button type="submit" class="primary" disabled={saving}>
              {saving ? t("new.saving") : t("new.create")}
            </button>
            <button type="button" class="secondary" onClick={() => select(null)}>
              {t("new.cancel")}
            </button>
          </div>
        </>
      )}
    </form>
  );
}

export function EditForm({ id }: { id: string }) {
  const { model, instances, t, client, select, putInstance, fail } = useUi();
  const instance = instances.get(id);
  const process = model?.processes.find((p) => p.id === instance?.process);
  const [criteria, setCriteria] = useState<CriteriaDraft>(() =>
    draftOf(process?.outcomes.length ?? 0, instance?.criteria ?? []),
  );
  const [notes, setNotes] = useState(instance?.notes ?? "");
  const [saving, setSaving] = useState(false);
  if (!model || !instance || !process) return null;
  const save = (): void => {
    setSaving(true);
    client
      .post<InstanceResponse>("/api/instances", {
        instance: id,
        criteria: criteriaOf(criteria),
        notes,
      })
      .then((answer) => {
        putInstance(answer.instance);
        select({ kind: "instance", id });
      }, fail)
      .finally(() => setSaving(false));
  };
  return (
    <form
      class="form"
      data-testid="edit-instance"
      onSubmit={(e) => {
        e.preventDefault();
        save();
      }}
    >
      <PanelHead
        kicker={`${t("panel.instance")} · ${id}`}
        title={processName(model, instance.process)}
        sub={t("instance.edit")}
      />
      <CriteriaFields outcomes={process.outcomes} draft={criteria} setDraft={setCriteria} />
      <label>
        {t("new.notes")}
        <textarea
          rows={3}
          value={notes}
          onInput={(e) => setNotes((e.currentTarget as HTMLTextAreaElement).value)}
        />
      </label>
      <div class="actions">
        <button type="submit" class="primary" disabled={saving}>
          {saving ? t("new.saving") : t("new.save")}
        </button>
        <button type="button" class="secondary" onClick={() => select({ kind: "instance", id })}>
          {t("new.cancel")}
        </button>
      </div>
    </form>
  );
}

interface JudgmentDraft {
  judgment: Judgment | "";
  evidence: string;
  limits: string;
}

export function EvaluateForm({ id }: { id: string }) {
  const { model, instances, t, client, select, putInstance, fail } = useUi();
  const instance = instances.get(id);
  const process = model?.processes.find((p) => p.id === instance?.process);
  const run = instance?.facts.latestRun ?? null;
  // An evaluation of the same run is the starting point; one of an earlier run is not.
  const earlier = instance?.evaluation?.runId === run?.id ? instance?.evaluation : null;
  const [drafts, setDrafts] = useState<JudgmentDraft[]>(() =>
    Array.from({ length: process?.outcomes.length ?? 0 }, (_, outcome) => {
      const found = earlier?.judgments.find((j) => j.outcome === outcome);
      return {
        judgment: found?.judgment ?? "",
        evidence: found?.evidence ?? "",
        limits: found?.limits ?? "",
      };
    }),
  );
  const [note, setNote] = useState(earlier?.note ?? "");
  const [problem, setProblem] = useState(false);
  const [saving, setSaving] = useState(false);
  if (!model || !instance || !process || !run) return null;
  const change = (i: number, next: Partial<JudgmentDraft>): void =>
    setDrafts(drafts.map((d, k) => (k === i ? { ...d, ...next } : d)));
  const save = (): void => {
    const judged = drafts.flatMap((d, outcome) =>
      d.judgment
        ? [
            {
              outcome,
              judgment: d.judgment,
              evidence: d.evidence.trim(),
              ...(d.limits.trim() ? { limits: d.limits.trim() } : {}),
            },
          ]
        : [],
    );
    if (judged.length === 0 || judged.some((j) => !j.evidence)) {
      setProblem(true);
      return;
    }
    setProblem(false);
    setSaving(true);
    client
      .post<InstanceResponse>(`/api/instances/${encodeURIComponent(id)}/evaluate`, {
        judgments: judged,
        ...(note.trim() ? { note } : {}),
      })
      .then((answer) => {
        putInstance(answer.instance);
        select({ kind: "instance", id });
      }, fail)
      .finally(() => setSaving(false));
  };
  return (
    <form
      class="form"
      data-testid="evaluate"
      onSubmit={(e) => {
        e.preventDefault();
        save();
      }}
    >
      <PanelHead
        kicker={`${t("evaluate.title")} · ${id}`}
        title={processName(model, instance.process)}
        sub={t("evaluate.of", { run: run.id })}
      />
      <p class="muted small">{t("evaluate.hint")}</p>
      {process.outcomes.map((outcome, i) => {
        const draft = drafts[i] ?? { judgment: "", evidence: "", limits: "" };
        const criterion = instance.criteria.find((c) => c.outcome === i);
        return (
          <fieldset key={i} class="judgment-field" data-outcome={i}>
            <legend>
              {i + 1}. {outcome}
            </legend>
            {criterion && <p class="small muted">{criterion.statement}</p>}
            <div class="radios" role="radiogroup">
              {JUDGMENTS.map((value) => (
                <label key={value} class="radio">
                  <input
                    type="radio"
                    name={`judgment-${i}`}
                    value={value}
                    checked={draft.judgment === value}
                    onChange={() => change(i, { judgment: value })}
                  />
                  {t(`judgment.${value}`)}
                </label>
              ))}
              <label class="radio">
                <input
                  type="radio"
                  name={`judgment-${i}`}
                  value=""
                  checked={draft.judgment === ""}
                  onChange={() => change(i, { judgment: "" })}
                />
                {t("evaluate.skip")}
              </label>
            </div>
            {draft.judgment && (
              <>
                <label>
                  {t("evaluate.evidence")}
                  <textarea
                    rows={2}
                    required
                    value={draft.evidence}
                    onInput={(e) =>
                      change(i, { evidence: (e.currentTarget as HTMLTextAreaElement).value })
                    }
                  />
                </label>
                <label>
                  {t("evaluate.limits")}
                  <input
                    type="text"
                    value={draft.limits}
                    onInput={(e) =>
                      change(i, { limits: (e.currentTarget as HTMLInputElement).value })
                    }
                  />
                </label>
              </>
            )}
          </fieldset>
        );
      })}
      <label>
        {t("evaluate.note")}
        <textarea
          rows={4}
          value={note}
          onInput={(e) => setNote((e.currentTarget as HTMLTextAreaElement).value)}
        />
      </label>
      {problem && (
        <p class="fail-text" role="alert">
          {t("evaluate.needOne")}
        </p>
      )}
      <div class="actions">
        <button type="submit" class="primary" disabled={saving}>
          {saving ? t("new.saving") : t("evaluate.save")}
        </button>
        <button type="button" class="secondary" onClick={() => select({ kind: "instance", id })}>
          {t("new.cancel")}
        </button>
      </div>
    </form>
  );
}
