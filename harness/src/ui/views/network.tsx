/*
 * The network: the whole model as the ring (R1a), or, once a Process or a type is clicked, only
 * what surrounds it (the focus view, G4). A click on the background returns to the ring. A
 * Process with a running run has a dashed ring around its dot; one with stale evidence, an amber
 * ring. The layout is computed by the pure functions of ../graph/.
 */

import { useEffect, useMemo } from "preact/hooks";
import type { InstanceView, ModelView, RunSummary } from "../../shared/types.ts";
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
import { ModelProblem } from "./common.tsx";

const FAMILY =
  '"IBM Plex Sans JP", "IBM Plex Sans", "Hiragino Sans", "Hiragino Kaku Gothic ProN", "Yu Gothic UI", Meiryo, system-ui, sans-serif';
const FONTS: Record<TextStyle, string> = {
  process: `500 13px ${FAMILY}`,
  type: `400 12px ${FAMILY}`,
  focus: `600 14px ${FAMILY}`,
  note: `400 11.5px ${FAMILY}`,
};

let canvas: CanvasRenderingContext2D | null | undefined;
/** Text widths in the page's fonts, measured on a canvas. */
const measure: Measure = (text, style) => {
  if (canvas === undefined) canvas = document.createElement("canvas").getContext("2d");
  if (!canvas) return estimateWidth(text, style);
  canvas.font = FONTS[style];
  return canvas.measureText(text).width;
};

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

function Edges({ edges }: { edges: readonly Edge[] }) {
  return (
    <>
      <g class="edges">
        {edges.map((edge, i) => (
          <path key={`e${i}`} class={`edge ${edge.role}`} d={edge.d} />
        ))}
      </g>
      <g class="heads">
        {edges.map((edge, i) => (
          <path key={`h${i}`} class={`head ${edge.role}`} d={edge.head} />
        ))}
      </g>
    </>
  );
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
      <Edges edges={layout.edges} />
      {layout.processes.map((p) => {
        const mark = marks.get(p.id) ?? { running: false, stale: false };
        const pick = (): void => select({ kind: "process", id: p.id });
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
            onClick={pick}
            onKeyDown={onKeys(pick)}
          >
            <rect
              class="hit"
              x={left - 4}
              y={p.label.y - 12}
              width={p.label.width + 8}
              height={24}
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
        const pick = (): void => select({ kind: "type", id: pill.id });
        return (
          <g
            key={pill.id}
            class="pill"
            data-type={pill.id}
            role="button"
            tabindex={0}
            aria-label={pill.name}
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
  const pick = (): void => select({ kind: node.kind, id: node.id });
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
        rx={node.kind === "type" ? node.height / 2 : 8}
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
  return (
    <svg
      class="graph"
      data-testid="focus"
      data-focus-kind={layout.target.kind}
      data-focus-id={layout.target.id}
      viewBox={`0 0 ${layout.width} ${layout.height}`}
      preserveAspectRatio="xMidYMid meet"
      role="group"
      aria-label={layout.target.id}
    >
      <rect
        class="backdrop"
        data-testid="backdrop"
        x={0}
        y={0}
        width={layout.width}
        height={layout.height}
        onClick={onBlank}
      />
      {layout.columns.map((column) => (
        <text key={column.title} class="column-title" x={column.x} y={FOCUS.titleY}>
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
      <span>
        <span class="line output" />
        {t("legend.output")}
      </span>
      <span>
        <span class="line input" />
        {t("legend.input")}
      </span>
      <span>
        <span class="line control" />
        {t("legend.control")}
      </span>
      <span>
        <span class="mark-running" />
        {t("legend.running")}
      </span>
      <span>
        <span class="mark-stale-ring" />
        {t("legend.stale")}
      </span>
      <span class="hint">{focused ? t("legend.focusHint") : t("legend.ringHint")}</span>
    </div>
  );
}

export function NetworkView({ modelError }: { modelError: unknown }) {
  const { model, instances, runs, focus, setFocus, select, t } = useUi();
  const graph = useMemo(() => (model ? graphOf(model) : null), [model]);
  const ring = useMemo(() => (graph ? ringLayout(graph, measure) : null), [graph]);
  const focused = useMemo(
    () => (graph && focus ? focusLayout(graph, focus, measure) : null),
    [graph, focus],
  );
  const marks = useMemo(() => marksOf(instances, runs), [instances, runs]);
  const back = (): void => {
    setFocus(null);
    select(null);
  };
  useEffect(() => {
    if (!focused) return;
    const onKey = (event: KeyboardEvent): void => {
      if (event.key === "Escape") back();
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  });

  if (!model)
    return modelError ? (
      <ModelProblem error={modelError} />
    ) : (
      <p class="muted pad">{t("loading")}</p>
    );
  return (
    <div class="stage">
      {focused && (
        <button type="button" class="back" onClick={back}>
          ← {t("network.back")}
        </button>
      )}
      {focused ? (
        <Focus layout={focused} onBlank={back} />
      ) : (
        ring && <Ring layout={ring} marks={marks} label={t("network.label")} onBlank={back} />
      )}
      <Legend focused={focused !== null} />
    </div>
  );
}
