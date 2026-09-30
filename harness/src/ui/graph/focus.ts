/*
 * The focus view (G4): only what surrounds the chosen Process or type. For a Process, five
 * columns: the Processes that produce its inputs, its inputs and controls, the Process, its
 * outputs, and the Processes that use them. For a type, three: the Processes that produce it, the
 * type, and those that read it. However many types the model has, the density stays the same.
 */

import {
  curve,
  fitText,
  rightHead,
  type Edge,
  type GraphModel,
  type GraphProcess,
  type Measure,
  type Role,
} from "./geometry.ts";

export const FOCUS = {
  /** The columns of a Process's focus: left edges and widths. */
  processColumns: [
    { x: 40, width: 190 },
    { x: 250, width: 200 },
    { x: 470, width: 200 },
    { x: 690, width: 200 },
    { x: 900, width: 190 },
  ],
  /** The columns of a type's focus. */
  typeColumns: [
    { x: 120, width: 200 },
    { x: 450, width: 200 },
    { x: 780, width: 200 },
  ],
  width: 1130,
  /** The height for a few nodes per column; more make it taller. */
  minHeight: 760,
  /** Vertical distance between the Processes of a column, and between the types. */
  processStep: 52,
  typeStep: 60,
  processHeight: 34,
  typeHeight: 30,
  focusHeight: { process: 72, type: 60 },
  /** Room above the nodes for the column titles, and below them. */
  top: 110,
  bottom: 90,
  /** The column titles' baseline. */
  titleY: 64,
  /** Pixels between a node's text and its border. */
  padding: 12,
  /** How far apart the input and the control lines reach the Process. */
  roleSpread: 6,
} as const;

export type FocusTarget = { kind: "process" | "type"; id: string };

/** What each column holds, for its title. */
export type FocusColumn =
  | "producers"
  | "inputs"
  | "process"
  | "outputs"
  | "consumers"
  | "typeProducers"
  | "type"
  | "typeConsumers";

export interface FocusNode {
  kind: "process" | "type";
  id: string;
  name: string;
  /** The name as it fits in the node. */
  label: string;
  /** The focused Process's purpose as it fits under its name, else "". */
  note: string;
  column: number;
  /** The node's left edge and vertical centre. */
  x: number;
  y: number;
  width: number;
  height: number;
  focused: boolean;
  /** A type that the focused Process reads only as a control is drawn dashed. */
  dashed: boolean;
}

export interface FocusLayout {
  target: FocusTarget;
  width: number;
  height: number;
  columns: { x: number; width: number; title: FocusColumn }[];
  nodes: FocusNode[];
  edges: Edge[];
}

/** The unique Processes of lists, in the order they first appear. */
const unique = (lists: GraphProcess[][]): GraphProcess[] => {
  const seen = new Set<string>();
  return lists.flat().filter((p) => (seen.has(p.id) ? false : (seen.add(p.id), true)));
};

const reads = (process: GraphProcess, type: string): boolean =>
  process.inputs.includes(type) || process.controls.includes(type);

/** How a consumer reads a type: as a control when it reads it only so. */
const readRole = (process: GraphProcess, type: string): Role =>
  process.controls.includes(type) && !process.inputs.includes(type) ? "control" : "input";

/** Vertical centres for `n` nodes `step` apart around `center`. */
const column =
  (n: number, step: number, center: number) =>
  (i: number): number =>
    center + (i - (n - 1) / 2) * step;

/** The focus view of a Process or a type; `null` when the model has no such node. */
export function focusLayout(
  model: GraphModel,
  target: FocusTarget,
  measure: Measure,
): FocusLayout | null {
  const typeName = (id: string): string => model.types.find((t) => t.id === id)?.name ?? id;
  const node = (
    kind: FocusNode["kind"],
    id: string,
    name: string,
    col: { x: number; width: number },
    columnIndex: number,
    y: number,
    extra: Partial<Pick<FocusNode, "focused" | "dashed" | "note" | "height">> = {},
  ): FocusNode => {
    const height = extra.height ?? (kind === "process" ? FOCUS.processHeight : FOCUS.typeHeight);
    const room = col.width - 2 * FOCUS.padding;
    return {
      kind,
      id,
      name,
      label: fitText(
        name,
        extra.focused ? "focus" : kind === "process" ? "process" : "type",
        room,
        measure,
      ),
      note: extra.note ? fitText(extra.note, "note", room, measure) : "",
      column: columnIndex,
      x: col.x,
      y,
      width: col.width,
      height,
      focused: extra.focused ?? false,
      dashed: extra.dashed ?? false,
    };
  };
  const heightFor = (extent: number): number =>
    Math.max(FOCUS.minHeight, FOCUS.top + extent + FOCUS.bottom);

  if (target.kind === "type") {
    if (!model.types.some((t) => t.id === target.id)) return null;
    const producers = model.processes.filter((p) => p.outputs.includes(target.id));
    const consumers = model.processes.filter((p) => reads(p, target.id));
    const [left, middle, right] = FOCUS.typeColumns;
    if (!left || !middle || !right) return null;
    const extent = Math.max(producers.length, consumers.length, 1) * FOCUS.processStep;
    const height = heightFor(extent);
    const cy = FOCUS.top + (height - FOCUS.top - FOCUS.bottom) / 2;
    const yLeft = column(producers.length, FOCUS.processStep, cy);
    const yRight = column(consumers.length, FOCUS.processStep, cy);
    const nodes: FocusNode[] = [
      node("type", target.id, typeName(target.id), middle, 1, cy, {
        focused: true,
        height: FOCUS.focusHeight.type,
      }),
    ];
    const edges: Edge[] = [];
    producers.forEach((p, k) => {
      nodes.push(node("process", p.id, p.name, left, 0, yLeft(k)));
      edges.push({
        role: "output",
        process: p.id,
        type: target.id,
        d: curve(left.x + left.width, yLeft(k), middle.x, cy),
        head: rightHead(middle.x, cy),
      });
    });
    consumers.forEach((p, k) => {
      nodes.push(node("process", p.id, p.name, right, 2, yRight(k)));
      edges.push({
        role: readRole(p, target.id),
        process: p.id,
        type: target.id,
        d: curve(middle.x + middle.width, cy, right.x, yRight(k)),
        head: rightHead(right.x, yRight(k)),
      });
    });
    return {
      target,
      width: FOCUS.width,
      height,
      columns: [
        { ...left, title: "typeProducers" },
        { ...middle, title: "type" },
        { ...right, title: "typeConsumers" },
      ],
      nodes,
      edges,
    };
  }

  const focused = model.processes.find((p) => p.id === target.id);
  if (!focused) return null;
  const [c0, c1, c2, c3, c4] = FOCUS.processColumns;
  if (!c0 || !c1 || !c2 || !c3 || !c4) return null;
  const others = model.processes.filter((p) => p.id !== focused.id);
  // Inputs first, then the controls that are not also inputs; a type read both ways has both lines.
  const ins = [
    ...focused.inputs.map((type) => ({
      type,
      role: "input" as const,
      both: focused.controls.includes(type),
    })),
    ...focused.controls
      .filter((type) => !focused.inputs.includes(type))
      .map((type) => ({ type, role: "control" as const, both: false })),
  ];
  const outs = focused.outputs;
  const producers = unique(ins.map((i) => others.filter((p) => p.outputs.includes(i.type))));
  const consumers = unique(outs.map((type) => others.filter((p) => reads(p, type))));

  const extent = Math.max(
    producers.length * FOCUS.processStep,
    ins.length * FOCUS.typeStep,
    outs.length * FOCUS.typeStep,
    consumers.length * FOCUS.processStep,
    FOCUS.focusHeight.process,
  );
  const height = heightFor(extent);
  const cy = FOCUS.top + (height - FOCUS.top - FOCUS.bottom) / 2;
  const yProducer = column(producers.length, FOCUS.processStep, cy);
  const yIn = column(ins.length, FOCUS.typeStep, cy);
  const yOut = column(outs.length, FOCUS.typeStep, cy);
  const yConsumer = column(consumers.length, FOCUS.processStep, cy);
  const spreadY = FOCUS.roleSpread;

  const nodes: FocusNode[] = [
    node("process", focused.id, focused.name, c2, 2, cy, {
      focused: true,
      note: focused.purpose ?? "",
      height: FOCUS.focusHeight.process,
    }),
  ];
  const edges: Edge[] = [];
  producers.forEach((p, k) => nodes.push(node("process", p.id, p.name, c0, 0, yProducer(k))));
  ins.forEach((input, k) => {
    const y = yIn(k);
    nodes.push(
      node("type", input.type, typeName(input.type), c1, 1, y, {
        dashed: input.role === "control",
      }),
    );
    for (const p of others.filter((q) => q.outputs.includes(input.type))) {
      const from = yProducer(producers.indexOf(p));
      edges.push({
        role: "output",
        process: p.id,
        type: input.type,
        d: curve(c0.x + c0.width, from, c1.x, y),
        head: rightHead(c1.x, y),
      });
    }
    const at = cy + (input.role === "input" ? -spreadY : spreadY);
    edges.push({
      role: input.role,
      process: focused.id,
      type: input.type,
      d: curve(c1.x + c1.width, y, c2.x, at),
      head: rightHead(c2.x, at),
    });
    if (input.both)
      edges.push({
        role: "control",
        process: focused.id,
        type: input.type,
        d: curve(c1.x + c1.width, y + spreadY, c2.x, cy + spreadY),
        head: rightHead(c2.x, cy + spreadY),
      });
  });
  outs.forEach((type, k) => {
    const y = yOut(k);
    nodes.push(node("type", type, typeName(type), c3, 3, y));
    edges.push({
      role: "output",
      process: focused.id,
      type,
      d: curve(c2.x + c2.width, cy, c3.x, y),
      head: rightHead(c3.x, y),
    });
    for (const p of others.filter((q) => reads(q, type))) {
      const to = yConsumer(consumers.indexOf(p));
      edges.push({
        role: readRole(p, type),
        process: p.id,
        type,
        d: curve(c3.x + c3.width, y, c4.x, to),
        head: rightHead(c4.x, to),
      });
    }
  });
  consumers.forEach((p, k) => nodes.push(node("process", p.id, p.name, c4, 4, yConsumer(k))));
  return {
    target,
    width: FOCUS.width,
    height,
    columns: [
      { ...c0, title: "producers" },
      { ...c1, title: "inputs" },
      { ...c2, title: "process" },
      { ...c3, title: "outputs" },
      { ...c4, title: "consumers" },
    ],
    nodes,
    edges,
  };
}
