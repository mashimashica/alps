/*
 * What a person writes in the WebUI, each in a dialog. A request (framework §7 tailoring, done by
 * an agent): what is needed in free text, attachments (files dropped or chosen, which are uploaded
 * when the request is sent, or Artifacts already in the workspace), the Processes that the plan
 * must include, the agent, and whether it runs what it plans or only instantiates it. Sending it
 * starts a wake; its record opens in the panel and its instances appear on the board as the agent
 * makes them. The criteria and notes of an instance: in free text, what each Outcome means in this
 * application and how to check it. Evaluation: the three-valued judgment of each Outcome with its
 * evidence and limits, and a Markdown note. Who judged is not sent: the harness records a person
 * for the WebUI. What cannot be sent is marked on its field (a request without text, a judgment
 * without evidence); files over the limits are refused as they are added, and the limits
 * themselves are in the drop zone's title. The dialogs carry no paragraphs of explanation: the
 * fields' names and examples say what to write, and where a distinction matters it is said where
 * it is made (a judgment's evidence field says that a run that ended is not evidence). The id of
 * the instance or the run is only in the subtitle's title. A failure of the server is shown in the
 * page's language.
 */

import { useEffect, useId, useRef, useState } from "preact/hooks";
import {
  MAX_ATTACHMENT_BYTES,
  MAX_ATTACHMENT_SIZE,
  MAX_ATTACHMENTS,
  MAX_REQUEST_LENGTH,
} from "../../shared/requests.ts";
import type {
  Artifact,
  ArtifactsResponse,
  AttachmentsResponse,
  InstanceResponse,
  Judgment,
  OutcomeCriterion,
  WakeResponse,
  WakeRuns,
} from "../../shared/types.ts";
import { describeError } from "../api.ts";
import { Button } from "../components/button.tsx";
import { Checkbox, Segmented } from "../components/checkbox.tsx";
import { Dialog } from "../components/dialog.tsx";
import { Alert } from "../components/feedback.tsx";
import { Icon } from "../components/icons.tsx";
import { Field, Input, Textarea } from "../components/input.tsx";
import { Select } from "../components/select.tsx";
import { cx } from "../components/util.ts";
import { useUi } from "../context.ts";
import { dateTime } from "../format.ts";
import { firstInput, Path, pathTail, processName, typeName } from "./common.tsx";
import { summaryOf } from "./panel.tsx";

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

/** The footer of a form dialog: its notice and failure, if any, then Cancel and the action. */
function Footer({
  failure,
  failureTitle,
  problem,
  notice,
  saving,
  action,
  busyLabel,
  onCancel,
}: {
  failure: unknown;
  failureTitle: string;
  problem?: string | null;
  /** What to know before trying again (the request was not started), as a warning. */
  notice?: string | null;
  saving: boolean;
  action: string;
  /** What the action says while it goes on; "Saving…" unless given. */
  busyLabel?: string;
  onCancel: () => void;
}) {
  const { t, language } = useUi();
  return (
    <div class="dialog-footer">
      {problem && <Alert tone="danger">{problem}</Alert>}
      {notice && (
        <Alert tone="warning" data-testid="form-notice">
          {notice}
        </Alert>
      )}
      {failure !== null && (
        <Alert tone="danger" title={failureTitle} data-testid="form-error">
          {describeError(failure, language)}
        </Alert>
      )}
      <Button variant="outline" onClick={onCancel}>
        {t("new.cancel")}
      </Button>
      <Button type="submit" busy={saving} disabled={saving}>
        {saving ? (busyLabel ?? t("new.saving")) : action}
      </Button>
    </div>
  );
}

/**
 * An attachment of a request: a file that is uploaded when the request is sent, or a path in the
 * workspace (an Artifact chosen there, or a file already uploaded by an earlier try).
 */
type Attachment = { kind: "file"; file: File } | { kind: "path"; path: string; uploaded: boolean };

const sameFile = (a: File, b: File): boolean =>
  a.name === b.name && a.size === b.size && a.lastModified === b.lastModified;

/** A size as a person reads it. */
function size(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

/** The files of a drop, and what was left out (folders cannot be uploaded). */
function droppedFiles(data: DataTransfer): { files: File[]; folders: string[] } {
  const files: File[] = [];
  const folders: string[] = [];
  const items = [...data.items].filter((item) => item.kind === "file");
  if (items.length === 0) return { files: [...data.files], folders };
  for (const item of items) {
    const entry = item.webkitGetAsEntry?.();
    if (entry?.isDirectory) {
      folders.push(entry.name);
      continue;
    }
    const file = item.getAsFile();
    if (file) files.push(file);
  }
  return { files, folders };
}

/**
 * The request box: what is needed, attachments, the Processes that the plan must include, the
 * agent to wake, and how far it goes. Sending uploads the files first, one at a time, as the
 * server takes them (each once: a retry sends the paths they were saved at), then starts the wake;
 * the page then shows the board with the wake's record in the panel. A wake that still runs means
 * this one is not started: the box stays open.
 */
function RequestDialog({ initial }: { initial?: string | undefined }) {
  const { model, t, client, select, setView, putRun, openForm } = useUi();
  const form = useRef<HTMLFormElement>(null);
  const picker = useRef<HTMLInputElement>(null);
  const modeLabel = useId();
  const [text, setText] = useState("");
  const [attachments, setAttachments] = useState<Attachment[]>([]);
  const [refused, setRefused] = useState<string[]>([]);
  const [found, setFound] = useState<Artifact[]>([]);
  const [processes, setProcesses] = useState<string[]>(initial ? [initial] : []);
  const [agent, setAgent] = useState("");
  const [runs, setRuns] = useState<WakeRuns>("run");
  const [over, setOver] = useState(false);
  const [tried, setTried] = useState(false);
  const [saving, setSaving] = useState(false);
  const [failure, setFailure] = useState<unknown>(null);
  const [skipped, setSkipped] = useState<string | null>(null);
  useEffect(() => {
    client.get<ArtifactsResponse>("/api/artifacts").then(
      (answer) => setFound(answer.artifacts),
      (error: unknown) => setFailure(error),
    );
  }, []);
  if (!model) return null;
  const close = (): void => openForm(null);
  // Only the agents that the harness can give its MCP server are woken: not the demo, not self.
  const agents = model.agents.filter((a) => a.id !== "demo" && a.id !== "self");
  const chosen =
    agents.find((a) => a.id === agent) ??
    agents.find((a) => a.id === "claude-code" && a.available) ??
    agents.find((a) => a.available) ??
    agents[0];
  const attached = new Set(attachments.flatMap((a) => (a.kind === "path" ? [a.path] : [])));
  const offered = [...new Map(found.map((a) => [a.path, a])).values()].filter(
    (a) => !attached.has(a.path),
  );
  const full = attachments.length >= MAX_ATTACHMENTS;

  const addFiles = (files: readonly File[], folders: readonly string[] = []): void => {
    const next = [...attachments];
    const notes = folders.map((name) => t("request.folder", { name }));
    for (const file of files) {
      if (file.size > MAX_ATTACHMENT_BYTES) {
        notes.push(t("request.tooLarge", { name: file.name, limit: MAX_ATTACHMENT_SIZE }));
        continue;
      }
      if (next.some((a) => a.kind === "file" && sameFile(a.file, file))) continue;
      if (next.length >= MAX_ATTACHMENTS) {
        notes.push(t("request.tooMany", { name: file.name, limit: MAX_ATTACHMENTS }));
        continue;
      }
      next.push({ kind: "file", file });
    }
    setAttachments(next);
    setRefused(notes);
  };

  const send = async (): Promise<void> => {
    setTried(true);
    if (!text.trim()) {
      focusFirstInvalid(form.current);
      return;
    }
    setSaving(true);
    setFailure(null);
    setSkipped(null);
    try {
      const list = [...attachments];
      // One file an upload, as the server takes them. A file saved is in the workspace from then
      // on: a second try sends its path, and uploads only the files not saved yet.
      for (const [i, a] of list.entries()) {
        if (a.kind !== "file") continue;
        const body = new FormData();
        body.append("files", a.file, a.file.name);
        const { paths } = await client.upload<AttachmentsResponse>("/api/attachments", body);
        list[i] = { kind: "path", path: paths[0] ?? "", uploaded: true };
        setAttachments([...list]);
      }
      const answer = await client.post<WakeResponse>("/api/wake", {
        ...(chosen ? { agent: chosen.id } : {}),
        request: text.trim(),
        attachments: list.flatMap((a) => (a.kind === "path" ? [a.path] : [])),
        processes,
        runs,
      });
      if (!answer.run) {
        setSkipped(answer.running ?? "");
        setSaving(false);
        return;
      }
      putRun(summaryOf(answer.run));
      close();
      // The board shows the instances as the agent makes them; the panel, the wake's record.
      setView("instances");
      select({ kind: "run", id: answer.run.id });
    } catch (error) {
      setFailure(error);
      setSaving(false);
    }
  };

  return (
    <Dialog
      title={t("request.title")}
      onClose={close}
      closeLabel={t("panel.close")}
      size="lg"
      testid="request"
    >
      <form
        ref={form}
        class="dialog-form"
        noValidate
        onSubmit={(event) => {
          event.preventDefault();
          void send();
        }}
        // Files dropped anywhere in the box are attached, and never opened by the browser instead.
        onDragOver={(event) => {
          if (!event.dataTransfer?.types.includes("Files")) return;
          event.preventDefault();
          event.dataTransfer.dropEffect = "copy";
          setOver(true);
        }}
        onDragLeave={(event) => {
          if (!event.currentTarget.contains(event.relatedTarget as Node | null)) setOver(false);
        }}
        onDrop={(event) => {
          if (!event.dataTransfer) return;
          event.preventDefault();
          setOver(false);
          const { files, folders } = droppedFiles(event.dataTransfer);
          addFiles(files, folders);
        }}
      >
        <div class="dialog-body">
          <Field
            label={t("request.text")}
            required
            error={tried && !text.trim() ? t("request.textRequired") : undefined}
          >
            {(control) => (
              <Textarea
                id={control.id}
                rows={5}
                maxLength={MAX_REQUEST_LENGTH}
                aria-required="true"
                aria-describedby={control.describedBy}
                invalid={control.invalid}
                placeholder={t("request.textPlaceholder")}
                data-testid="request-text"
                value={text}
                onInput={(event) => setText(event.currentTarget.value)}
              />
            )}
          </Field>
          <fieldset class="group">
            <legend>{t("request.attachments")}</legend>
            {/* The limits are in the title; a file over them is refused where it is added. */}
            <div
              class={cx("dropzone", over && "is-over")}
              data-testid="request-drop"
              title={t("request.limits", { count: MAX_ATTACHMENTS, size: MAX_ATTACHMENT_SIZE })}
            >
              <Icon name="upload" size={20} />
              <span class="dropzone-text">{t("request.drop")}</span>
              <Button
                variant="outline"
                size="sm"
                disabled={full}
                onClick={() => picker.current?.click()}
              >
                <Icon name="paperclip" />
                {t("request.chooseFiles")}
              </Button>
              <input
                ref={picker}
                type="file"
                multiple
                class="sr-only"
                tabIndex={-1}
                aria-hidden="true"
                data-testid="request-files"
                onChange={(event) => {
                  addFiles([...(event.currentTarget.files ?? [])]);
                  event.currentTarget.value = "";
                }}
              />
            </div>
            {refused.length > 0 && (
              <Alert tone="warning" data-testid="request-refused">
                {refused.map((note, i) => (
                  <p key={i}>{note}</p>
                ))}
              </Alert>
            )}
            <Field label={t("request.existing")}>
              {(control) => (
                <Select
                  id={control.id}
                  labelledBy={control.labelId}
                  value=""
                  placeholder={
                    offered.length > 0 ? t("request.chooseArtifact") : t("request.noArtifacts")
                  }
                  disabled={offered.length === 0 || full}
                  icon={<Icon name="file" />}
                  options={offered.map((a) => ({
                    value: a.path,
                    label: `${a.path}${a.dir ? "/" : ""}`,
                    hint: typeName(model, a.type),
                  }))}
                  onChange={(path) =>
                    setAttachments([...attachments, { kind: "path", path, uploaded: false }])
                  }
                  testid="request-artifact"
                />
              )}
            </Field>
            {attachments.length > 0 && (
              <ul class="list attachment-list" data-testid="request-attachments">
                {attachments.map((a, i) => {
                  const name = a.kind === "file" ? a.file.name : a.path;
                  return (
                    <li
                      key={a.kind === "file" ? `file:${i}:${a.file.name}` : `path:${a.path}`}
                      class="list-row"
                      data-attachment={a.kind === "path" ? a.path : undefined}
                    >
                      <span class="list-main attachment-name">
                        <Icon name={a.kind === "file" ? "paperclip" : "file"} size={14} />
                        <span class="mono small path-cell">
                          <Path path={name} />
                        </span>
                      </span>
                      <span class="list-end">
                        {/* The icon tells a file to upload from one in the workspace; the size is a file's. */}
                        {(a.kind === "file" || a.uploaded) && (
                          <span class="faint small">
                            {a.kind === "file" ? size(a.file.size) : t("request.uploaded")}
                          </span>
                        )}
                        <Button
                          variant="ghost"
                          size="icon-sm"
                          aria-label={t("request.remove", { name })}
                          title={t("request.remove", { name })}
                          onClick={() => setAttachments(attachments.filter((_, k) => k !== i))}
                        >
                          <Icon name="x" />
                        </Button>
                      </span>
                    </li>
                  );
                })}
              </ul>
            )}
          </fieldset>
          <fieldset class="group">
            <legend title={t("request.processesHint")}>{t("request.processes")}</legend>
            <div class="request-processes" data-testid="request-processes">
              {model.processes.map((p) => (
                <div key={p.id} data-process={p.id}>
                  <Checkbox
                    checked={processes.includes(p.id)}
                    onChange={(on) =>
                      setProcesses(
                        on ? [...processes, p.id] : processes.filter((id) => id !== p.id),
                      )
                    }
                    label={p.name}
                  />
                </div>
              ))}
            </div>
          </fieldset>
          <div class="request-options">
            <Field label={t("request.agent")}>
              {(control) => (
                <Select
                  id={control.id}
                  labelledBy={control.labelId}
                  value={chosen?.id ?? ""}
                  icon={<Icon name="terminal" />}
                  options={agents.map((a) => ({
                    value: a.id,
                    label: a.label,
                    disabled: !a.available,
                    ...(a.available
                      ? a.version
                        ? { hint: a.version }
                        : {}
                      : { hint: t("overview.unavailable", { reason: a.reason ?? "" }) }),
                  }))}
                  onChange={setAgent}
                  testid="request-agent"
                />
              )}
            </Field>
            <div class="field">
              <span class="field-label" id={modeLabel}>
                {t("request.mode")}
              </span>
              <Segmented
                name="request-runs"
                value={runs}
                labelledBy={modeLabel}
                options={[
                  { value: "run", label: t("request.run"), title: t("request.runHint") },
                  { value: "plan", label: t("request.plan"), title: t("request.planHint") },
                ]}
                onChange={setRuns}
              />
            </div>
          </div>
        </div>
        <Footer
          failure={failure}
          failureTitle={t("request.failed")}
          notice={skipped !== null ? t("request.skipped", { run: skipped }) : null}
          saving={saving}
          action={t("request.send")}
          busyLabel={t("request.sending")}
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
      description={
        <span title={`${t("panel.instance")} · ${instance.id}`}>
          {[processName(model, instance.process), firstInput(model, instance)]
            .filter(Boolean)
            .map((part, i) => (i === 0 ? part : pathTail(part ?? "")))
            .join(" · ")}
        </span>
      }
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
  const { model, instances, runs, t, language, client, select, putInstance, openForm } = useUi();
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
      description={
        <span title={`${t("panel.run")} · ${run.id}`}>
          {t("evaluate.of", {
            at: dateTime(run.startedAt, language),
            status: t(`status.${(runs.get(run.id) ?? run).status}`),
          })}
        </span>
      }
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
                          placeholder={t("evaluate.evidencePlaceholder")}
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
    case "request":
      return <RequestDialog initial={form.process} />;
    case "edit":
      return <EditDialog key={form.id} id={form.id} />;
    case "evaluate":
      return <EvaluateDialog key={form.id} id={form.id} />;
  }
}
