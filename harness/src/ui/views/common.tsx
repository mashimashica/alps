/* Small parts that the screens and the panel share. */

import { Fragment, type ComponentChildren } from "preact";
import type {
  InstanceView,
  Judgment,
  ModelView,
  OutcomeJudgment,
  RunStatus,
} from "../../shared/types.ts";
import { Badge, type Tone } from "../components/badge.tsx";
import { Button } from "../components/button.tsx";
import { Alert } from "../components/feedback.tsx";
import { Icon } from "../components/icons.tsx";
import { useUi } from "../context.ts";
import { renderMarkdown } from "../markdown.ts";

export const processName = (model: ModelView | null, id: string | null): string =>
  (id && model?.processes.find((p) => p.id === id)?.name) || id || "";

export const typeName = (model: ModelView | null, id: string): string =>
  model?.artifacts.find((a) => a.id === id)?.name ?? id;

/** The first input of an instance, its type and path, in the order of the Process's inputs and controls. */
export function firstInputOf(
  model: ModelView | null,
  instance: InstanceView,
): { type: string; path: string } | null {
  const process = model?.processes.find((p) => p.id === instance.process);
  const order = process ? [...process.inputs, ...process.controls] : [];
  for (const type of [...order, ...Object.keys(instance.inputs)]) {
    const path = instance.inputs[type]?.[0];
    if (path) return { type, path };
  }
  return null;
}

/** The first input path of an instance. */
export const firstInput = (model: ModelView | null, instance: InstanceView): string | null =>
  firstInputOf(model, instance)?.path ?? null;

/**
 * Brings an element into view within the box that scrolls it (the panel, a Sheet, a list),
 * without moving the page, whose header stays where it is.
 */
export function reveal(element: Element): void {
  for (let box = element.parentElement; box && box !== document.body; box = box.parentElement) {
    if (!/(auto|scroll)/.test(getComputedStyle(box).overflowY)) continue;
    if (box.scrollHeight <= box.clientHeight) continue;
    const offset = element.getBoundingClientRect().top - box.getBoundingClientRect().top;
    box.scrollTop = Math.max(0, box.scrollTop + offset - box.clientHeight / 3);
    return;
  }
}

/** Scrolls the page so that an element's top is just under the page's header. */
export function scrollUnderHeader(element: Element): void {
  const header = document.querySelector(".topbar")?.getBoundingClientRect().height ?? 0;
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  window.scrollTo({
    top: Math.max(0, element.getBoundingClientRect().top + window.scrollY - header - 12),
    behavior: reduced ? "auto" : "smooth",
  });
}

/** The last part of a path: the name of its file or folder. */
export function lastPart(path: string): string {
  const parts = path.split(/[\\/]+/).filter(Boolean);
  return parts[parts.length - 1] ?? path;
}

/**
 * The end of a path that tells it apart: its file or folder and the folder that holds it
 * (docs/changes/CHG-001/change-brief.md shows as CHG-001/change-brief.md). The screens show
 * this, and the whole path is in the title and in the details.
 */
export function pathTail(path: string): string {
  const parts = path.split("/").filter(Boolean);
  if (parts.length <= 2) return path;
  return `${parts.slice(-2).join("/")}${path.endsWith("/") ? "/" : ""}`;
}

/**
 * A path that breaks after its slashes, where it is too long for its line, and not at its hyphens:
 * each part with its slash is a box of its own (.path-part), which breaks inside only when it is
 * wider than the whole line. One element, so that a flex row takes it as one item.
 */
export function Path({ path }: { path: string }) {
  const parts = path.split("/");
  return (
    <span>
      {parts.map((part, i) => {
        const last = i === parts.length - 1;
        return last && !part ? null : (
          <Fragment key={i}>
            <span class="path-part">{last ? part : `${part}/`}</span>
            {!last && <wbr />}
          </Fragment>
        );
      })}
    </span>
  );
}

/** A path as its end, with the whole path (and its type, when known) in the title. */
export function PathTail({ path, type }: { path: string; type?: string }) {
  return (
    <span class="path-tail mono" title={type ? `${type}: ${path}` : path}>
      <Path path={pathTail(path)} />
    </span>
  );
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
  if (!judgments) return <span class="faint">{t("none")}</span>;
  const count = Math.max(outcomes, ...judgments.map((j) => j.outcome + 1));
  const marks = Array.from({ length: count }, (_, outcome) =>
    judgments.find((j) => j.outcome === outcome),
  );
  const described = marks
    .map((j, i) => `${i + 1}: ${j ? t(`judgment.${j.judgment}`) : t("evaluate.skip")}`)
    .join(", ");
  return (
    <span class="glyphs" role="img" aria-label={described} title={described}>
      {marks.map((j, i) => (
        <span key={i} class={j ? `g-${j.judgment}` : "g-none"} aria-hidden="true">
          {j ? GLYPH[j.judgment] : "·"}
        </span>
      ))}
    </span>
  );
}

const STATUS_TONE: Record<RunStatus, Tone> = {
  running: "info",
  succeeded: "success",
  failed: "danger",
  canceled: "neutral",
  interrupted: "outline",
};

/** A run's status. Its colours are not those of the judgments: a run that ended is not an achievement. */
export function StatusText({ status }: { status: RunStatus }) {
  const { t } = useUi();
  return (
    <Badge
      tone={STATUS_TONE[status]}
      dot
      pulse={status === "running"}
      class="status"
      data-status={status}
    >
      {t(`status.${status}`)}
    </Badge>
  );
}

export function Section({
  title,
  actions,
  children,
}: {
  title: ComponentChildren;
  actions?: ComponentChildren;
  children: ComponentChildren;
}) {
  return (
    <section class="section">
      <div class="section-head">
        <h3>{title}</h3>
        {actions}
      </div>
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
    <button type="button" class="chip chip-type" onClick={() => select({ kind: "type", id })}>
      {typeName(model, id)}
    </button>
  );
}

export function ProcessLink({ id }: { id: string }) {
  const { model, select } = useUi();
  return (
    <button type="button" class="chip chip-process" onClick={() => select({ kind: "process", id })}>
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

/** An instance as its Process and the end of its first input path (the whole path in the title). */
export function InstanceLink({ instance }: { instance: InstanceView }) {
  const { model, select } = useUi();
  const input = firstInputOf(model, instance);
  return (
    <button
      type="button"
      class="link instance-link"
      title={input ? `${typeName(model, input.type)}: ${input.path}` : instance.id}
      onClick={() => select({ kind: "instance", id: instance.id })}
    >
      <span class="instance-link-name">{processName(model, instance.process)}</span>
      <span class="mono faint instance-link-path">
        {input ? <Path path={pathTail(input.path)} /> : instance.id}
      </span>
    </button>
  );
}

/** The panel's heading: what kind of thing it shows, its name, and a close button. */
export function PanelHead({
  kicker,
  title,
  sub,
  closable = true,
}: {
  kicker: ComponentChildren;
  title: ComponentChildren;
  sub?: ComponentChildren;
  closable?: boolean;
}) {
  const { t, closePanel } = useUi();
  return (
    <div class="panel-head">
      <div class="panel-head-text">
        <p class="kicker">{kicker}</p>
        <h2>{title}</h2>
        {sub && <div class="sub">{sub}</div>}
      </div>
      {closable && (
        <Button
          variant="ghost"
          size="icon-sm"
          class="panel-close"
          aria-label={t("panel.close")}
          title={t("panel.close")}
          onClick={closePanel}
        >
          <Icon name="x" />
        </Button>
      )}
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
    <Alert tone="danger" title={t("model.error")} class="problem">
      <p>{message}</p>
      {files.length > 0 && (
        <>
          <p class="problem-files-title">{t("model.files")}</p>
          <ul class="mono small problem-files">
            {files.map((file) => (
              <li key={file}>{file}</li>
            ))}
          </ul>
        </>
      )}
    </Alert>
  );
}
