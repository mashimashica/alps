/*
 * What the ring and the focus view share: the graph they draw (Processes connected only through
 * Artifact types), and the geometry of their lines and labels. Pure functions: no DOM. Text
 * widths come from a Measure that the page implements with a canvas and the tests with a rule.
 */

export interface GraphProcess {
  id: string;
  name: string;
  purpose?: string;
  inputs: readonly string[];
  controls: readonly string[];
  outputs: readonly string[];
}

export interface GraphType {
  id: string;
  name: string;
}

export interface GraphModel {
  processes: readonly GraphProcess[];
  types: readonly GraphType[];
}

/** The fonts the graph sets its text in. */
export type TextStyle = "process" | "type" | "focus" | "note";

/** The width of a text in pixels, in one of the graph's fonts. */
export type Measure = (text: string, style: TextStyle) => number;

/** How a line connects a Process and a type: the Process produces it, or reads it as an input or a control. */
export type Role = "output" | "input" | "control";

/** A line, and its arrowhead at the end the Artifact flows to. */
export interface Edge {
  role: Role;
  process: string;
  type: string;
  /** SVG path data. */
  d: string;
  head: string;
}

export type Point = readonly [number, number];

export const TAU = Math.PI * 2;

/** Coordinates in SVG path data. */
export const fx = (v: number): string => (Math.round(v * 10) / 10).toString();

/** An angle difference in (-π, π]. */
export const wrapAngle = (d: number): number => ((((d + Math.PI) % TAU) + TAU) % TAU) - Math.PI;

export const toPath = (points: readonly Point[]): string =>
  `M${points.map((p) => `${fx(p[0])} ${fx(p[1])}`).join("L")}`;

/**
 * A line between two rings: the radius changes evenly and the angle smoothly, so the line leaves
 * and reaches each node along the radius and never crosses a ring.
 */
export function band(
  fromAngle: number,
  toAngle: number,
  fromRadius: number,
  toRadius: number,
): Point[] {
  const d = wrapAngle(toAngle - fromAngle);
  const steps = Math.max(10, Math.ceil(Math.abs(d) * 22) + 8);
  const points: Point[] = [];
  for (let i = 0; i <= steps; i++) {
    const t = i / steps;
    const s = t * t * (3 - 2 * t);
    const rho = fromRadius + (toRadius - fromRadius) * t;
    const theta = fromAngle + d * s;
    points.push([rho * Math.cos(theta), rho * Math.sin(theta)]);
  }
  return points;
}

/** The points moved sideways by `offset` pixels, to set apart lines that share a path. */
export function offsetPoints(points: readonly Point[], offset: number): Point[] {
  if (offset === 0) return [...points];
  return points.map((p, i) => {
    const a = points[Math.max(0, i - 1)] ?? p;
    const b = points[Math.min(points.length - 1, i + 1)] ?? p;
    const dx = b[0] - a[0];
    const dy = b[1] - a[1];
    const length = Math.hypot(dx, dy) || 1;
    return [p[0] - (dy / length) * offset, p[1] + (dx / length) * offset] as const;
  });
}

/** An arrowhead whose tip is at `to`, pointing away from `from`. */
export function arrowHead(from: Point, to: Point): string {
  const dx = to[0] - from[0];
  const dy = to[1] - from[1];
  const length = Math.hypot(dx, dy) || 1;
  const ux = dx / length;
  const uy = dy / length;
  const bx = to[0] - 5 * ux;
  const by = to[1] - 5 * uy;
  return `M${fx(bx - 2.5 * uy)} ${fx(by + 2.5 * ux)}L${fx(to[0])} ${fx(to[1])}L${fx(bx + 2.5 * uy)} ${fx(by - 2.5 * ux)}Z`;
}

/** A horizontal S-curve from one column to the next. */
export function curve(x1: number, y1: number, x2: number, y2: number): string {
  const dx = (x2 - x1) * 0.45;
  return `M${fx(x1)} ${fx(y1)}C${fx(x1 + dx)} ${fx(y1)} ${fx(x2 - dx)} ${fx(y2)} ${fx(x2)} ${fx(y2)}`;
}

/** An arrowhead pointing right, with its tip at (x, y). */
export const rightHead = (x: number, y: number): string => arrowHead([x - 1, y], [x, y]);

/** A text cut to a width, with an ellipsis when it was cut. */
export function fitText(text: string, style: TextStyle, width: number, measure: Measure): string {
  if (measure(text, style) <= width) return text;
  const chars = [...text];
  let low = 0;
  let high = chars.length;
  while (low < high) {
    const mid = Math.ceil((low + high) / 2);
    if (measure(`${chars.slice(0, mid).join("")}…`, style) <= width) low = mid;
    else high = mid - 1;
  }
  return `${chars.slice(0, low).join("").trimEnd()}…`;
}

/**
 * Text widths by rule, for tests and before the fonts are known: CJK characters are one em wide,
 * other characters a little over half an em.
 */
export const estimateWidth: Measure = (text, style) => {
  const em = style === "process" ? 13 : style === "focus" ? 14 : style === "note" ? 11.5 : 12;
  let width = 0;
  for (const char of text) {
    const code = char.codePointAt(0) ?? 0;
    // CJK symbols and ideographs, Hangul, and full-width forms.
    const wide =
      (code >= 0x3000 && code <= 0x9fff) ||
      (code >= 0xac00 && code <= 0xd7af) ||
      (code >= 0xff00 && code <= 0xffef);
    width += wide ? em : em * 0.56;
  }
  return width;
};

/** Where each type is used: the Processes that produce it and those that read it. */
export function usesOf(
  model: GraphModel,
): Map<string, { producers: number[]; consumers: number[] }> {
  const uses = new Map(
    model.types.map((t) => [t.id, { producers: [] as number[], consumers: [] as number[] }]),
  );
  model.processes.forEach((process, index) => {
    for (const type of process.outputs) uses.get(type)?.producers.push(index);
    for (const type of new Set([...process.inputs, ...process.controls]))
      uses.get(type)?.consumers.push(index);
  });
  return uses;
}
