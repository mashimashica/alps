/*
 * What a person writes in the WebUI, each in a dialog. Instantiation (framework §7): the Process,
 * the concrete inputs of each type (Artifacts found in its locations, or other paths), where each
 * output goes (or the agent decides), and, in free text, what each Outcome means in this
 * application and how to check it. Evaluation: the three-valued judgment of each Outcome with
 * its evidence and limits, and a Markdown note. Who judged is not sent: the harness records a
 * person for the WebUI. What cannot be saved is marked on its field (a Process not chosen, a path
 * that is empty or a pattern, a judgment without evidence); a path outside its type's locations
 * is saved as written, with a warning. A failure of the server is shown in the page's language.
 */

import { useEffect, useRef, useState } from "preact/hooks";
import { compilePattern } from "../../model/patterns.ts";
import type {
  Artifact,
  ArtifactsResponse,
  InstanceResponse,
  Judgment,
  OutcomeCriterion,
} from "../../shared/types.ts";
import { describeError } from "../api.ts";
import { Badge } from "../components/badge.tsx";
import { Button } from "../components/button.tsx";
import { Checkbox, Segmented } from "../components/checkbox.tsx";
import { Dialog } from "../components/dialog.tsx";
import { Alert } from "../components/feedback.tsx";
import { Icon } from "../components/icons.tsx";
import { Field, Input, Textarea } from "../components/input.tsx";
import { Select } from "../components/select.tsx";
import { useUi } from "../context.ts";
import { processName, typeName } from "./common.tsx";

const JUDGMENTS: Judgment[] = ["achieved", "not-achieved", "unverified"];
/** How many existing Artifacts are offered as places of an output. */
const SUGGESTED = 4;

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

/** Moves the focus to the first field marked invalid, once the marks are drawn. */
const focusFirstInvalid = (form: HTMLFormElement | null): void => {
  requestAnimationFrame(() => {
    const marked = form?.querySelector<HTMLElement>('[aria-invalid="true"]');
    const control = marked?.matches("input, textarea, button")
      ? marked
      : marked?.querySelector<HTMLElement>("input, textarea, button");
    control?.focus();
  });
};

/** Whether a path is in one of a type's locations (only `*` and `**` are wildcards). */
function fitsType(patterns: readonly string[], path: string): boolean {
  if (patterns.length === 0) return true;
  const relative = path
    .replace(/\\/g, "/")
    .replace(/^(?:\.\/)+/, "")
    .replace(/\/+$/, "");
  return patterns.some((pattern) => compilePattern(pattern).regex.test(relative));
}

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
    <fieldset class="group">
      <legend>{t("new.criteria")}</legend>
      {outcomes.map((outcome, i) => (
        <div key={i} class="criterion">
          <p class="criterion-outcome">
            <span class="criterion-number">{i + 1}</span>
            {outcome}
          </p>
          <Field label={t("new.statement")}>
            {(control) => (
              <Textarea
                id={control.id}
                rows={2}
                value={draft[i]?.statement ?? ""}
                onInput={(event) => change(i, "statement", event.currentTarget.value)}
              />
            )}
          </Field>
          <Field label={t("new.checks")}>
            {(control) => (
              <Input
                id={control.id}
                type="text"
                value={draft[i]?.checks ?? ""}
                onInput={(event) => change(i, "checks", event.currentTarget.value)}
              />
            )}
          </Field>
        </div>
      ))}
    </fieldset>
  );
}

type PathProblem = "empty" | "pattern" | "chosen";
const PROBLEM_KEY = {
  empty: "new.pathEmpty",
  pattern: "new.pathPattern",
  chosen: "new.pathChosen",
} as const;

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
  const [problem, setProblem] = useState<PathProblem | null>(null);
  const name = typeName(model, type);
  const patterns = model?.artifacts.find((a) => a.id === type)?.paths ?? [];
  const candidates = found.map((a) => `${a.path}${a.dir ? "/" : ""}`);
  const extra = chosen.filter((p) => !candidates.includes(p));
  const toggle = (path: string, on: boolean): void =>
    setChosen(on ? [...chosen, path] : chosen.filter((p) => p !== path));
  const add = (): void => {
    const path = other.trim().replace(/^(?:\.\/)+/, "");
    const next: PathProblem | null = !path
      ? "empty"
      : path.includes("*")
        ? "pattern"
        : chosen.includes(path)
          ? "chosen"
          : null;
    setProblem(next);
    if (next) return;
    setChosen([...chosen, path]);
    setOther("");
  };
  return (
    <div class="choice" data-input-type={type}>
      <div class="choice-head">
        <strong>{name}</strong>
        {control && <Badge tone="outline">{t("new.control")}</Badge>}
        {patterns.length > 0 && (
          <span class="mono faint small choice-pattern">{patterns.join(", ")}</span>
        )}
      </div>
      {candidates.length === 0 && <p class="faint small">{t("new.none")}</p>}
      <div class="choice-list">
        {candidates.map((path) => (
          <Checkbox
            key={path}
            checked={chosen.includes(path)}
            onChange={(on) => toggle(path, on)}
            label={<span class="mono">{path}</span>}
          />
        ))}
        {extra.map((path) => (
          <Checkbox
            key={path}
            checked
            onChange={() => toggle(path, false)}
            ariaLabel={t("new.remove", { path })}
            label={<span class="mono">{path}</span>}
            description={
              fitsType(patterns, path) ? undefined : (
                <span class="warning-text">
                  {t("new.pathNotType", { type: name, patterns: patterns.join(", ") })}
                </span>
              )
            }
          />
        ))}
      </div>
      <Field
        label={
          <>
            <span class="sr-only">{name}: </span>
            {t("new.path")}
          </>
        }
        error={problem ? t(PROBLEM_KEY[problem]) : undefined}
      >
        {(field) => (
          <div class="inline">
            <Input
              id={field.id}
              type="text"
              class="mono"
              placeholder={patterns[0] ?? ""}
              aria-describedby={field.describedBy}
              invalid={field.invalid}
              value={other}
              onInput={(event) => {
                setOther(event.currentTarget.value);
                if (problem) setProblem(null);
              }}
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  event.preventDefault();
                  add();
                }
              }}
            />
            <Button variant="outline" onClick={add}>
              <Icon name="plus" />
              {t("new.add")}
            </Button>
          </div>
        )}
      </Field>
    </div>
  );
}

/** The footer of a form dialog: its failure, if any, then Cancel and the action. */
function Footer({
  failure,
  failureTitle,
  problem,
  saving,
  action,
  onCancel,
}: {
  failure: unknown;
  failureTitle: string;
  problem?: string | null;
  saving: boolean;
  action: string;
  onCancel: () => void;
}) {
  const { t, language } = useUi();
  return (
    <div class="dialog-footer">
      {problem && <Alert tone="danger">{problem}</Alert>}
      {failure !== null && (
        <Alert tone="danger" title={failureTitle} data-testid="form-error">
          {describeError(failure, language)}
        </Alert>
      )}
      <Button variant="outline" onClick={onCancel}>
        {t("new.cancel")}
      </Button>
      <Button type="submit" busy={saving} disabled={saving}>
        {saving ? t("new.saving") : action}
      </Button>
    </div>
  );
}

function InstantiateDialog({ initial }: { initial?: string | undefined }) {
  const { model, t, client, select, putInstance, openForm } = useUi();
  const form = useRef<HTMLFormElement>(null);
  const outcomesOf = (id: string): number =>
    model?.processes.find((p) => p.id === id)?.outcomes.length ?? 0;
  const [processId, setProcessId] = useState(initial ?? "");
  const [found, setFound] = useState<Artifact[]>([]);
  const [inputs, setInputs] = useState<Record<string, string[]>>({});
  const [outputs, setOutputs] = useState<Record<string, string>>({});
  const [criteria, setCriteria] = useState<CriteriaDraft>(() =>
    draftOf(outcomesOf(initial ?? ""), []),
  );
  const [notes, setNotes] = useState("");
  const [tried, setTried] = useState(false);
  const [saving, setSaving] = useState(false);
  const [failure, setFailure] = useState<unknown>(null);
  useEffect(() => {
    client.get<ArtifactsResponse>("/api/artifacts").then(
      (answer) => setFound(answer.artifacts),
      (error: unknown) => setFailure(error),
    );
  }, []);
  if (!model) return null;
  const process = model.processes.find((p) => p.id === processId);
  const close = (): void => openForm(null);
  const chooseProcess = (id: string): void => {
    setProcessId(id);
    setInputs({});
    setOutputs({});
    setCriteria(draftOf(outcomesOf(id), []));
  };
  const types = process
    ? [
        ...process.inputs.map((type) => ({ type, control: false })),
        ...process.controls
          .filter((c) => !process.inputs.includes(c))
          .map((type) => ({ type, control: true })),
      ]
    : [];
  const create = (): void => {
    setTried(true);
    if (!process) {
      focusFirstInvalid(form.current);
      return;
    }
    setSaving(true);
    setFailure(null);
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
      .then(
        (answer) => {
          putInstance(answer.instance);
          select({ kind: "instance", id: answer.instance.id });
          close();
        },
        (error: unknown) => {
          setFailure(error);
          setSaving(false);
        },
      );
  };
  return (
    <Dialog
      title={t("new.title")}
      description={process?.purpose || undefined}
      onClose={close}
      closeLabel={t("panel.close")}
      size="lg"
      testid="instantiate"
    >
      <form
        ref={form}
        class="dialog-form"
        noValidate
        onSubmit={(event) => {
          event.preventDefault();
          create();
        }}
      >
        <div class="dialog-body">
          <Field
            label={t("new.process")}
            required
            error={tried && !process ? t("new.processRequired") : undefined}
          >
            {(control) => (
              <Select
                id={control.id}
                labelledBy={control.labelId}
                describedBy={control.describedBy}
                invalid={control.invalid}
                value={processId}
                placeholder={t("new.choose")}
                icon={<Icon name="network" />}
                options={model.processes.map((p) => ({ value: p.id, label: p.name }))}
                onChange={chooseProcess}
              />
            )}
          </Field>
          {process && (
            <>
              <fieldset class="group">
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
              <fieldset class="group">
                <legend>{t("new.outputs")}</legend>
                {process.outputs.map((type) => {
                  const pattern = model.artifacts.find((a) => a.id === type)?.paths[0] ?? "";
                  const existing = found
                    .filter((a) => a.type === type)
                    .slice(0, SUGGESTED)
                    .map((a) => `${a.path}${a.dir ? "/" : ""}`);
                  return (
                    <Field key={type} label={typeName(model, type)}>
                      {(control) => (
                        <div class="output-field">
                          <Input
                            id={control.id}
                            type="text"
                            class="mono"
                            placeholder={
                              pattern
                                ? `${t("new.agentDecides")} (${pattern})`
                                : t("new.agentDecides")
                            }
                            value={outputs[type] ?? ""}
                            onInput={(event) =>
                              setOutputs({ ...outputs, [type]: event.currentTarget.value })
                            }
                          />
                          {existing.length > 0 && (
                            <div class="suggestions">
                              {existing.map((path) => (
                                <button
                                  key={path}
                                  type="button"
                                  class="chip chip-path mono"
                                  onClick={() => setOutputs({ ...outputs, [type]: path })}
                                >
                                  {path}
                                </button>
                              ))}
                            </div>
                          )}
                        </div>
                      )}
                    </Field>
                  );
                })}
              </fieldset>
              <CriteriaFields outcomes={process.outcomes} draft={criteria} setDraft={setCriteria} />
              <Field label={t("new.notes")}>
                {(control) => (
                  <Textarea
                    id={control.id}
                    rows={3}
                    value={notes}
                    onInput={(event) => setNotes(event.currentTarget.value)}
                  />
                )}
              </Field>
            </>
          )}
        </div>
        <Footer
          failure={failure}
          failureTitle={t("new.failed")}
          saving={saving}
          action={t("new.create")}
          onCancel={close}
        />
      </form>
    </Dialog>
  );
}

function EditDialog({ id }: { id: string }) {
  const { model, instances, t, client, select, putInstance, openForm } = useUi();
  const instance = instances.get(id);
  const process = model?.processes.find((p) => p.id === instance?.process);
  const [criteria, setCriteria] = useState<CriteriaDraft>(() =>
    draftOf(process?.outcomes.length ?? 0, instance?.criteria ?? []),
  );
  const [notes, setNotes] = useState(instance?.notes ?? "");
  const [saving, setSaving] = useState(false);
  const [failure, setFailure] = useState<unknown>(null);
  if (!model || !instance || !process) return null;
  const close = (): void => openForm(null);
  const save = (): void => {
    setSaving(true);
    setFailure(null);
    client
      .post<InstanceResponse>("/api/instances", {
        instance: id,
        criteria: criteriaOf(criteria),
        notes,
      })
      .then(
        (answer) => {
          putInstance(answer.instance);
          select({ kind: "instance", id, tab: "overview" });
          close();
        },
        (error: unknown) => {
          setFailure(error);
          setSaving(false);
        },
      );
  };
  return (
    <Dialog
      title={t("instance.edit")}
      description={`${processName(model, instance.process)} · ${id}`}
      onClose={close}
      closeLabel={t("panel.close")}
      size="lg"
      testid="edit-instance"
    >
      <form
        class="dialog-form"
        noValidate
        onSubmit={(event) => {
          event.preventDefault();
          save();
        }}
      >
        <div class="dialog-body">
          <CriteriaFields outcomes={process.outcomes} draft={criteria} setDraft={setCriteria} />
          <Field label={t("new.notes")}>
            {(control) => (
              <Textarea
                id={control.id}
                rows={3}
                value={notes}
                onInput={(event) => setNotes(event.currentTarget.value)}
              />
            )}
          </Field>
        </div>
        <Footer
          failure={failure}
          failureTitle={t("new.failed")}
          saving={saving}
          action={t("new.save")}
          onCancel={close}
        />
      </form>
    </Dialog>
  );
}

interface JudgmentDraft {
  judgment: Judgment | "";
  evidence: string;
  limits: string;
}

function EvaluateDialog({ id }: { id: string }) {
  const { model, instances, t, client, select, putInstance, openForm } = useUi();
  const form = useRef<HTMLFormElement>(null);
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
  const [tried, setTried] = useState(false);
  const [saving, setSaving] = useState(false);
  const [failure, setFailure] = useState<unknown>(null);
  if (!model || !instance || !process || !run) return null;
  const close = (): void => openForm(null);
  const change = (i: number, next: Partial<JudgmentDraft>): void =>
    setDrafts(drafts.map((d, k) => (k === i ? { ...d, ...next } : d)));
  const lacksEvidence = (d: JudgmentDraft): boolean => d.judgment !== "" && !d.evidence.trim();
  const noneJudged = drafts.every((d) => d.judgment === "");
  const save = (): void => {
    setTried(true);
    if (noneJudged || drafts.some(lacksEvidence)) {
      focusFirstInvalid(form.current);
      return;
    }
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
    setSaving(true);
    setFailure(null);
    client
      .post<InstanceResponse>(`/api/instances/${encodeURIComponent(id)}/evaluate`, {
        judgments: judged,
        ...(note.trim() ? { note } : {}),
      })
      .then(
        (answer) => {
          putInstance(answer.instance);
          select({ kind: "instance", id, tab: "evaluation" });
          close();
        },
        (error: unknown) => {
          setFailure(error);
          setSaving(false);
        },
      );
  };
  return (
    <Dialog
      title={`${t("evaluate.title")} · ${processName(model, instance.process)}`}
      description={t("evaluate.of", { run: run.id })}
      onClose={close}
      closeLabel={t("panel.close")}
      size="lg"
      testid="evaluate"
    >
      <form
        ref={form}
        class="dialog-form"
        noValidate
        onSubmit={(event) => {
          event.preventDefault();
          save();
        }}
      >
        <div class="dialog-body">
          <Alert tone="info" live={false}>
            {t("evaluate.hint")}
          </Alert>
          {process.outcomes.map((outcome, i) => {
            const draft = drafts[i] ?? { judgment: "", evidence: "", limits: "" };
            const criterion = instance.criteria.find((c) => c.outcome === i);
            const legend = `evaluate-${id}-${i}`;
            return (
              <fieldset key={i} class="group outcome-field" data-outcome={i}>
                <legend id={legend}>
                  <span class="criterion-number">{i + 1}</span>
                  {outcome}
                </legend>
                {criterion && <p class="criterion-note">{criterion.statement}</p>}
                <Segmented
                  name={`judgment-${i}`}
                  value={draft.judgment}
                  labelledBy={legend}
                  invalid={tried && noneJudged && i === 0}
                  options={[
                    ...JUDGMENTS.map((value) => ({
                      value,
                      label: t(`judgment.${value}`),
                      tone: value,
                    })),
                    { value: "" as const, label: t("evaluate.skip"), tone: "none" },
                  ]}
                  onChange={(judgment) => change(i, { judgment })}
                />
                {draft.judgment && (
                  <div class="judgment-detail">
                    <Field
                      label={t("evaluate.evidence")}
                      error={
                        tried && lacksEvidence(draft) ? t("evaluate.evidenceRequired") : undefined
                      }
                    >
                      {(control) => (
                        <Textarea
                          id={control.id}
                          rows={2}
                          aria-required="true"
                          aria-describedby={control.describedBy}
                          invalid={control.invalid}
                          value={draft.evidence}
                          onInput={(event) => change(i, { evidence: event.currentTarget.value })}
                        />
                      )}
                    </Field>
                    <Field label={t("evaluate.limits")}>
                      {(control) => (
                        <Input
                          id={control.id}
                          type="text"
                          value={draft.limits}
                          onInput={(event) => change(i, { limits: event.currentTarget.value })}
                        />
                      )}
                    </Field>
                  </div>
                )}
              </fieldset>
            );
          })}
          <Field label={t("evaluate.note")}>
            {(control) => (
              <Textarea
                id={control.id}
                rows={4}
                value={note}
                onInput={(event) => setNote(event.currentTarget.value)}
              />
            )}
          </Field>
        </div>
        <Footer
          failure={failure}
          failureTitle={t("evaluate.failed")}
          problem={tried && noneJudged ? t("evaluate.needOne") : null}
          saving={saving}
          action={t("evaluate.save")}
          onCancel={close}
        />
      </form>
    </Dialog>
  );
}

/** The dialog of the form that is open, if any. */
export function FormDialog() {
  const { form } = useUi();
  if (!form) return null;
  switch (form.kind) {
    case "new":
      return <InstantiateDialog initial={form.process} />;
    case "edit":
      return <EditDialog key={form.id} id={form.id} />;
    case "evaluate":
      return <EvaluateDialog key={form.id} id={form.id} />;
  }
}
