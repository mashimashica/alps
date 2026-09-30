/* Small parts that the screens and the panel share. */

import type { ComponentChildren } from "preact";
import type {
  InstanceView,
  Judgment,
  ModelView,
  OutcomeJudgment,
  RunStatus,
} from "../../shared/types.ts";
import { useUi } from "../context.ts";
import { renderMarkdown } from "../markdown.ts";

export const processName = (model: ModelView | null, id: string | null): string =>
  (id && model?.processes.find((p) => p.id === id)?.name) || id || "";

export const typeName = (model: ModelView | null, id: string): string =>
  model?.artifacts.find((a) => a.id === id)?.name ?? id;

/** The first input path of an instance, in the order of the Process's inputs and controls. */
export function firstInput(model: ModelView | null, instance: InstanceView): string | null {
  const process = model?.processes.find((p) => p.id === instance.process);
  const order = process ? [...process.inputs, ...process.controls] : [];
  for (const type of [...order, ...Object.keys(instance.inputs)]) {
    const path = instance.inputs[type]?.[0];
    if (path) return path;
  }
  return null;
}

/** When an instance last changed: its latest run or its evaluation, whichever is later. */
export function updatedAt(instance: InstanceView): number {
  const run = instance.facts.latestRun;
  return Math.max(run?.endedAt ?? run?.startedAt ?? 0, instance.evaluation?.at ?? 0);
}

const GLYPH: Record<Judgment, string> = { achieved: "●", "not-achieved": "×", unverified: "○" };

/** One mark per Outcome: ● achieved, × not achieved, ○ unverified, · not judged. */
export function Glyphs({
  judgments,
  outcomes,
}: {
  judgments: readonly OutcomeJudgment[] | null;
  outcomes: number;
}) {
  const { t } = useUi();
  if (!judgments) return <span class="muted">{t("none")}</span>;
  const count = Math.max(outcomes, ...judgments.map((j) => j.outcome + 1));
  const marks = Array.from({ length: count }, (_, outcome) =>
    judgments.find((j) => j.outcome === outcome),
  );
  return (
    <span
      class="glyphs"
      title={marks
        .map((j, i) => `${i + 1}: ${j ? t(`judgment.${j.judgment}`) : t("evaluate.skip")}`)
        .join(", ")}
    >
      {marks.map((j, i) => (
        <span key={i} class={j ? `g-${j.judgment}` : "g-none"}>
          {j ? GLYPH[j.judgment] : "·"}
        </span>
      ))}
    </span>
  );
}

export function StatusText({ status }: { status: RunStatus }) {
  const { t } = useUi();
  return <span class={`status s-${status}`}>{t(`status.${status}`)}</span>;
}

export function Section({ title, children }: { title: string; children: ComponentChildren }) {
  return (
    <section class="section">
      <h3>{title}</h3>
      {children}
    </section>
  );
}

/** Markdown, made harmless (markdown.ts). */
export function Markdown({ source }: { source: string }) {
  // The HTML comes from renderMarkdown only, which escapes any HTML in the text.
  return <div class="md" dangerouslySetInnerHTML={{ __html: renderMarkdown(source) }} />;
}

export function TypeLink({ id }: { id: string }) {
  const { model, select } = useUi();
  return (
    <button type="button" class="chip" onClick={() => select({ kind: "type", id })}>
      {typeName(model, id)}
    </button>
  );
}

export function ProcessLink({ id }: { id: string }) {
  const { model, select } = useUi();
  return (
    <button type="button" class="link" onClick={() => select({ kind: "process", id })}>
      {processName(model, id)}
    </button>
  );
}

export function RunLink({ id }: { id: string }) {
  const { select } = useUi();
  return (
    <button type="button" class="link mono" onClick={() => select({ kind: "run", id })}>
      {id}
    </button>
  );
}

export function InstanceLink({ instance }: { instance: InstanceView }) {
  const { model, select } = useUi();
  return (
    <button
      type="button"
      class="link"
      onClick={() => select({ kind: "instance", id: instance.id })}
    >
      {processName(model, instance.process)}{" "}
      <span class="mono muted">{firstInput(model, instance) ?? instance.id}</span>
    </button>
  );
}

/** The panel's heading: what kind of thing it shows, its name, and a close button. */
export function PanelHead({
  kicker,
  title,
  sub,
}: {
  kicker: string;
  title: ComponentChildren;
  sub?: ComponentChildren;
}) {
  const { t, select } = useUi();
  return (
    <div class="panel-head">
      <div>
        <div class="kicker">{kicker}</div>
        <h2>{title}</h2>
        {sub && <div class="sub">{sub}</div>}
      </div>
      <button
        type="button"
        class="close"
        aria-label={t("panel.close")}
        title={t("panel.close")}
        onClick={() => select(null)}
      >
        ×
      </button>
    </div>
  );
}

/** Why the model cannot be shown, with the files that were looked at. */
export function ModelProblem({ error }: { error: unknown }) {
  const { t, language } = useUi();
  const files =
    error && typeof error === "object" && "info" in error
      ? ((error as { info: { files?: string[] } | null }).info?.files ?? [])
      : [];
  const message =
    error && typeof error === "object" && "describe" in error
      ? (error as { describe(l: typeof language): string }).describe(language)
      : String(error);
  return (
    <div class="problem" role="alert">
      <h2>{t("model.error")}</h2>
      <p>{message}</p>
      {files.length > 0 && (
        <>
          <h3>{t("model.files")}</h3>
          <ul class="mono">
            {files.map((file) => (
              <li key={file}>{file}</li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}
