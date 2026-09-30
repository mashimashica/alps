/*
 * The network: the whole model as the ring (R1a), or, once a Process or a type is clicked, only
 * what surrounds it (the focus view, G4). A click on the background, Esc, or the "Whole model"
 * crumb returns to the ring. A Process with a running run has a dashed ring around its dot; one
 * with stale evidence, an amber ring. The lines are the relationships of Artifact types (which
 * Processes produce and read each), not an order of execution, and the legend says so. The
 * layout is computed by the pure functions of ../graph/.
 */

import { flushSync } from "preact/compat";
import { useEffect, useLayoutEffect, useMemo, useRef, useState } from "preact/hooks";
import type { InstanceView, ModelView, RunSummary } from "../../shared/types.ts";
import { Badge } from "../components/badge.tsx";
import { Button } from "../components/button.tsx";
import { Card } from "../components/card.tsx";
import { Skeleton } from "../components/feedback.tsx";
import { Icon } from "../components/icons.tsx";
import { useUi } from "../context.ts";
import { FOCUS, focusLayout, type FocusLayout, type FocusNode } from "../graph/focus.ts";
import {
  estimateWidth,
  type Edge,
  type GraphModel,
  type Measure,
  type TextStyle,
} from "../graph/geometry.ts";
import { RING, ringLayout, type RingLayout } from "../graph/ring.ts";
import { ModelProblem, processName, typeName } from "./common.tsx";

/** The page's sans-serif stack (tokens.css), which the labels are measured and drawn in. */
const FAMILY =
  'Inter, "IBM Plex Sans JP", -apple-system, BlinkMacSystemFont, "Hiragino Sans", "Yu Gothic UI", sans-serif';
/** The weight and the size in pixels of each style, as views.css draws them in the focus view. */
const FONTS: Record<TextStyle, readonly [number, number]> = {
  process: [500, 13],
  type: [400, 12],
  focus: [600, 14],
  note: [400, 11.5],
};
/**
 * The ring's names are a size up (views.css draws them so): the ring is scaled down to fit its
 * box, and there they keep a legible size.
 */
const RING_SIZES: Partial<Record<TextStyle, number>> = { process: 14, type: 13 };

let canvas: CanvasRenderingContext2D | null | undefined;
/** Text widths in the page's fonts, measured on a canvas, in the styles' sizes or in `sizes`. */
const measureIn =
  (sizes: Partial<Record<TextStyle, number>> = {}): Measure =>
  (text, style) => {
    const [weight, size] = FONTS[style];
    const px = sizes[style] ?? size;
    if (canvas === undefined) canvas = document.createElement("canvas").getContext("2d");
    if (!canvas) return (estimateWidth(text, style) * px) / size;
    canvas.font = `${weight} ${px}px ${FAMILY}`;
    return canvas.measureText(text).width;
  };
const measure = measureIn();
const measureRing = measureIn(RING_SIZES);

export const graphOf = (model: ModelView): GraphModel => ({
  processes: model.processes.map((p) => ({
    id: p.id,
    name: p.name,
    purpose: p.purpose,
    inputs: p.inputs,
    controls: p.controls,
    outputs: p.outputs,
  })),
  types: model.artifacts.map((a) => ({ id: a.id, name: a.name })),
});

export interface ProcessMarks {
  running: boolean;
  stale: boolean;
}

/**
 * The marks of each Process: running when the latest run of one of its instances is running
 * (only the latest can be), stale when one of its instances has stale evidence.
 */
export function marksOf(
  instances: ReadonlyMap<string, InstanceView>,
  runs: ReadonlyMap<string, RunSummary>,
): Map<string, ProcessMarks> {
  const marks = new Map<string, ProcessMarks>();
  const mark = (process: string): ProcessMarks => {
    let found = marks.get(process);
    if (!found) {
      found = { running: false, stale: false };
      marks.set(process, found);
    }
    return found;
  };
  for (const instance of instances.values()) {
    if (instance.facts.stale) mark(instance.process).stale = true;
    const latest = instance.facts.latestRun;
    // The run's own event may be newer than the instance's facts.
    if (latest && (runs.get(latest.id) ?? latest).status === "running")
      mark(instance.process).running = true;
  }
  return marks;
}

type EdgeHighlight = { kind: "process" | "type"; id: string };

function Edges({ edges, highlight }: { edges: readonly Edge[]; highlight?: EdgeHighlight | null }) {
  return (
    <g class="edges">
      {edges.map((edge, i) => (
        <path
          key={`e${i}`}
          class={`edge edge-${edge.role}`}
          data-emphasis={
            highlight ? (edge[highlight.kind] === highlight.id ? "active" : "muted") : undefined
          }
          d={edge.d}
        />
      ))}
    </g>
  );
}

let networkTransition: ViewTransition | null = null;

/** Capture both layouts so the graph and its card can crossfade and resize together. */
function transitionNetwork(mode: "ring" | "focus", update: () => void): void {
  networkTransition?.skipTransition();
  if (!document.startViewTransition || matchMedia("(prefers-reduced-motion: reduce)").matches) {
    update();
    return;
  }
  document.documentElement.dataset.networkTransition = mode;
  const transition = document.startViewTransition(() => flushSync(update));
  networkTransition = transition;
  void transition.finished
    .catch(() => {})
    .finally(() => {
      if (networkTransition !== transition) return;
      networkTransition = null;
      delete document.documentElement.dataset.networkTransition;
    });
}

/** Keyboard use of a node: Enter or Space picks it. */
const onKeys =
  (pick: () => void) =>
  (event: KeyboardEvent): void => {
    if (event.key !== "Enter" && event.key !== " ") return;
    event.preventDefault();
    pick();
  };

function Ring({
  layout,
  marks,
  label,
  onBlank,
}: {
  layout: RingLayout;
  marks: Map<string, ProcessMarks>;
  label: string;
  onBlank: () => void;
}) {
  const { select } = useUi();
  const { x, y, width, height } = layout.viewBox;
  const [hovered, setHovered] = useState<EdgeHighlight | null>(null);
  const [keyboardFocus, setKeyboardFocus] = useState<EdgeHighlight | null>(null);
  return (
    <svg
      class="graph"
      data-testid="ring"
      viewBox={`${x} ${y} ${width} ${height}`}
      preserveAspectRatio="xMidYMid meet"
      role="group"
      aria-label={label}
    >
      <rect
        class="backdrop"
        data-testid="backdrop"
        x={x}
        y={y}
        width={width}
        height={height}
        onClick={onBlank}
      />
      <circle class="orbit" cx={0} cy={0} r={layout.radius} />
      <Edges edges={layout.edges} highlight={hovered ?? keyboardFocus} />
      {layout.processes.map((p) => {
        const mark = marks.get(p.id) ?? { running: false, stale: false };
        const pick = (): void =>
          transitionNetwork("focus", () => select({ kind: "process", id: p.id }));
        const left =
          p.label.anchor === "start"
            ? p.label.x
            : p.label.anchor === "end"
              ? p.label.x - p.label.width
              : p.label.x - p.label.width / 2;
        return (
          <g
            key={p.id}
            class="proc"
            data-process={p.id}
            data-running={String(mark.running)}
            data-stale={String(mark.stale)}
            role="button"
            tabindex={0}
            aria-label={p.name}
            onMouseEnter={() => setHovered({ kind: "process", id: p.id })}
            onMouseLeave={() => setHovered(null)}
            onFocus={() => setKeyboardFocus({ kind: "process", id: p.id })}
            onBlur={() => setKeyboardFocus(null)}
            onClick={pick}
            onKeyDown={onKeys(pick)}
          >
            <rect
              class="hit label-bg"
              x={left - 10}
              y={p.label.y - 16}
              width={p.label.width + 20}
              height={32}
              rx={10}
            />
            <circle class="hit" cx={p.x} cy={p.y} r={16} />
            {mark.stale && <circle class="mark stale" cx={p.x} cy={p.y} r={11.5} />}
            {mark.running && (
              <circle class="mark running" cx={p.x} cy={p.y} r={mark.stale ? 16 : 11.5} />
            )}
            <circle class="dot" cx={p.x} cy={p.y} r={RING.dot} />
            <text
              x={p.label.x}
              y={p.label.y}
              text-anchor={p.label.anchor}
              dominant-baseline="central"
            >
              {p.name}
            </text>
          </g>
        );
      })}
      {layout.pills.map((pill) => {
        const pick = (): void =>
          transitionNetwork("focus", () => select({ kind: "type", id: pill.id }));
        return (
          <g
            key={pill.id}
            class="pill"
            data-type={pill.id}
            role="button"
            tabindex={0}
            aria-label={pill.name}
            onMouseEnter={() => setHovered({ kind: "type", id: pill.id })}
            onMouseLeave={() => setHovered(null)}
            onFocus={() => setKeyboardFocus({ kind: "type", id: pill.id })}
            onBlur={() => setKeyboardFocus(null)}
            onClick={pick}
            onKeyDown={onKeys(pick)}
          >
            <rect
              x={pill.x - pill.width / 2}
              y={pill.y - pill.height / 2}
              width={pill.width}
              height={pill.height}
              rx={pill.height / 2}
            />
            <text x={pill.x} y={pill.y} text-anchor="middle" dominant-baseline="central">
              {pill.name}
            </text>
          </g>
        );
      })}
    </svg>
  );
}

function FocusNodeView({ node, sub }: { node: FocusNode; sub: string }) {
  const { select } = useUi();
  const pick = (): void =>
    transitionNetwork("focus", () => select({ kind: node.kind, id: node.id }));
  const cx = node.x + node.width / 2;
  const note = node.note || (node.focused ? sub : "");
  const classes = [
    "fnode",
    node.kind,
    node.focused ? "focused" : "",
    node.dashed ? "dashed" : "",
  ].filter(Boolean);
  return (
    <g
      class={classes.join(" ")}
      data-node={`${node.kind}:${node.id}`}
      role="button"
      tabindex={0}
      aria-label={node.name}
      onClick={pick}
      onKeyDown={onKeys(pick)}
    >
      <title>{node.name}</title>
      <rect
        x={node.x}
        y={node.y - node.height / 2}
        width={node.width}
        height={node.height}
        rx={node.kind === "type" ? node.height / 2 : 9}
      />
      {note ? (
        <>
          <text class="name" x={cx} y={node.y - 9} text-anchor="middle" dominant-baseline="central">
            {node.label}
          </text>
          <text
            class="note"
            x={cx}
            y={node.y + 12}
            text-anchor="middle"
            dominant-baseline="central"
          >
            {note}
          </text>
        </>
      ) : (
        <text class="name" x={cx} y={node.y} text-anchor="middle" dominant-baseline="central">
          {node.label}
        </text>
      )}
    </g>
  );
}

/**
 * The part of a focus layout to show: its columns and nodes with a margin, and the column titles
 * just above the nodes (the layout leaves room for many nodes, which a few do not fill).
 */
function focusFrame(layout: FocusLayout): {
  x: number;
  y: number;
  width: number;
  height: number;
  titleY: number;
} {
  const margin = 24;
  const top = Math.min(...layout.nodes.map((n) => n.y - n.height / 2));
  const bottom = Math.max(...layout.nodes.map((n) => n.y + n.height / 2));
  const left = Math.min(...layout.columns.map((c) => c.x));
  const right = Math.max(...layout.columns.map((c) => c.x + c.width));
  const titleY = Math.max(FOCUS.titleY, top - 30);
  const y = titleY - 22 - margin / 2;
  return {
    x: left - margin,
    y,
    width: right - left + margin * 2,
    height: bottom + margin * 1.5 - y,
    titleY,
  };
}

function Focus({ layout, onBlank }: { layout: FocusLayout; onBlank: () => void }) {
  const { t } = useUi();
  const producers = layout.nodes.filter((n) => n.column === 0).length;
  const consumers = layout.nodes.filter((n) => n.column === 2).length;
  const sub =
    layout.target.kind === "type"
      ? producers > 0
        ? t("focus.typeSub", { producers, consumers })
        : t("focus.givenSub", { consumers })
      : "";
  const frame = focusFrame(layout);
  return (
    <svg
      class="graph"
      data-testid="focus"
      data-focus-kind={layout.target.kind}
      data-focus-id={layout.target.id}
      viewBox={`${frame.x} ${frame.y} ${frame.width} ${frame.height}`}
      preserveAspectRatio="xMidYMid meet"
      role="group"
      aria-label={layout.target.id}
    >
      <rect
        class="backdrop"
        data-testid="backdrop"
        x={frame.x}
        y={frame.y}
        width={frame.width}
        height={frame.height}
        onClick={onBlank}
      />
      {layout.columns.map((column) => (
        <text key={column.title} class="column-title" x={column.x} y={frame.titleY}>
          {t(`focus.${column.title}`)}
        </text>
      ))}
      <Edges edges={layout.edges} />
      {layout.nodes.map((node) => (
        <FocusNodeView key={`${node.column}:${node.kind}:${node.id}`} node={node} sub={sub} />
      ))}
    </svg>
  );
}

function Legend({ focused }: { focused: boolean }) {
  const { t } = useUi();
  return (
    <div class="legend">
      <div class="legend-group">
        <span class="legend-title">{t("legend.relations")}</span>
        <span>
          <span class="legend-line line-output" aria-hidden="true" />
          {t("legend.output")}
        </span>
        <span>
          <span class="legend-line line-input" aria-hidden="true" />
          {t("legend.input")}
        </span>
        <span>
          <span class="legend-line line-control" aria-hidden="true" />
          {t("legend.control")}
        </span>
      </div>
      <div class="legend-group">
        <span class="legend-title">{t("legend.marks")}</span>
        <span>
          <span class="mark-running" aria-hidden="true" />
          {t("legend.running")}
        </span>
        <span>
          <span class="mark-stale-ring" aria-hidden="true" />
          {t("legend.stale")}
        </span>
      </div>
      <p class="legend-note">{t("legend.notOrder")}</p>
      <p class="legend-hint">
        <Icon name="info" size={14} />
        {focused ? t("legend.focusHint") : t("legend.ringHint")}
      </p>
    </div>
  );
}

export function NetworkView({ modelError }: { modelError: unknown }) {
  const { model, instances, runs, focus, setFocus, select, t } = useUi();
  const graph = useMemo(() => (model ? graphOf(model) : null), [model]);
  const ring = useMemo(() => (graph ? ringLayout(graph, measureRing) : null), [graph]);
  const focused = useMemo(
    () => (graph && focus ? focusLayout(graph, focus, measure) : null),
    [graph, focus],
  );
  const marks = useMemo(() => marksOf(instances, runs), [instances, runs]);
  // Where the graph is wider than its box (narrow windows), it opens at its middle.
  const canvasBox = useRef<HTMLDivElement>(null);
  useLayoutEffect(() => {
    const box = canvasBox.current;
    if (box && box.scrollWidth > box.clientWidth)
      box.scrollLeft = (box.scrollWidth - box.clientWidth) / 2;
  }, [focused, ring]);
  const back = (): void =>
    transitionNetwork("ring", () => {
      setFocus(null);
      select(null);
    });
  useEffect(() => {
    if (!focused) return;
    const onKey = (event: KeyboardEvent): void => {
      // A dialog or a list that is open takes its own Esc.
      if (
        event.key === "Escape" &&
        !event.defaultPrevented &&
        !document.querySelector("dialog[open]")
      )
        back();
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  });

  if (!model)
    return modelError ? (
      <ModelProblem error={modelError} />
    ) : (
      <Card class="network-card">
        <div class="network-canvas network-loading" role="status">
          <span class="sr-only">{t("loading")}</span>
          <Skeleton class="ring-skeleton" />
        </div>
      </Card>
    );
  const focusName = !focus
    ? ""
    : focus.kind === "process"
      ? processName(model, focus.id)
      : typeName(model, focus.id);
  return (
    <Card class="network-card" data-mode={focused ? "focus" : "ring"}>
      {/* The heading and the toolbar share a row where they fit, to leave the height to the ring. */}
      <div class="network-head">
        <div class="network-heading">
          <p class="eyebrow" aria-hidden="true">
            {t("network.eyebrow")}
          </p>
          <h3>{t("network.heading")}</h3>
        </div>
        <div class="network-toolbar">
          <nav class="crumbs" aria-label={t("tab.network")}>
            {focused ? (
              <Button variant="ghost" size="sm" class="crumb" onClick={back}>
                <Icon name="network" />
                {t("network.whole")}
              </Button>
            ) : (
              <span class="crumb crumb-current" aria-current="location">
                <Icon name="network" />
                {t("network.whole")}
              </span>
            )}
            {focused && focus && (
              <>
                <Icon name="chevronRight" class="crumb-separator" size={14} />
                <span class="crumb crumb-current" aria-current="location">
                  <span class="crumb-name">{focusName}</span>
                  <Badge tone="brand">
                    {focus.kind === "process" ? t("panel.process") : t("panel.type")}
                  </Badge>
                </span>
              </>
            )}
          </nav>
          <Badge tone="outline" class="network-counts">
            {t("overview.counts", {
              processes: model.processes.length,
              types: model.artifacts.length,
            })}
          </Badge>
        </div>
      </div>
      <div class="network-canvas" ref={canvasBox}>
        {focused ? (
          <Focus layout={focused} onBlank={back} />
        ) : (
          ring && <Ring layout={ring} marks={marks} label={t("network.label")} onBlank={back} />
        )}
      </div>
      <Legend focused={focused !== null} />
    </Card>
  );
}
