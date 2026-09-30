/*
 * The ring of the network view (R1a): the Processes on the outer ring in the order of the flow,
 * and the Artifact types inside as horizontal pills, each at the centroid of the Processes it
 * connects, neighbours on alternating radii so that their names do not overlap. Lines run only
 * between the two rings. The order is for reading the picture: the model has no order.
 */

import {
  TAU,
  arrowHead,
  band,
  offsetPoints,
  toPath,
  usesOf,
  wrapAngle,
  type Edge,
  type GraphModel,
  type Measure,
  type Point,
  type Role,
} from "./geometry.ts";

export const RING = {
  /** The outer ring's radius for up to 11 Processes; it grows with more of them. */
  radius: 300,
  /** Pixels of the outer ring per Process beyond that. */
  perProcess: 28,
  /** The pills' two radii, as shares of the outer ring's. */
  inner: 148 / 300,
  outer: 212 / 300,
  /** The smallest angle between neighbouring pills (less when there are too many to keep it). */
  gap: 0.34,
  pillHeight: 26,
  /** The pill's width beyond its name. */
  pillPadding: 18,
  /** Pixels between a Process's dot and its name. */
  labelGap: 16,
  labelHeight: 18,
  dot: 6,
  /** Where lines leave the outer ring, inside the dots. */
  lineInset: 9,
  /** Pixels between the lines of one Process and one type, for each role they have. */
  roleSpacing: 3,
  /**
   * Around everything. The drawing is scaled down to its box, and what it holds besides the names
   * shrinks the names with it: enough for the names' backgrounds and the focus ring.
   */
  margin: 16,
  /** Pixels kept between pills, and between a pill and the ring of the Processes. */
  pillClearance: 2,
  /** How far apart overlapping pills move at a time, and how many times at most. */
  separateStep: 0.01,
  separateIterations: 400,
  /** How much the ring grows when the pills do not fit, and how many times at most. */
  growth: 1.08,
  growths: 8,
} as const;

export interface RingProcess {
  id: string;
  name: string;
  angle: number;
  x: number;
  y: number;
  /** Where the name goes: its anchor point (the middle of its height) and how it is anchored. */
  label: { x: number; y: number; anchor: "start" | "middle" | "end"; width: number };
}

export interface RingPill {
  id: string;
  name: string;
  angle: number;
  radius: number;
  /** The pill's centre. */
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface RingLayout {
  /** The area that holds everything, in the coordinates of the drawing (the centre is 0, 0). */
  viewBox: { x: number; y: number; width: number; height: number };
  radius: number;
  processes: RingProcess[];
  pills: RingPill[];
  edges: Edge[];
}

/**
 * The Processes in the order of the flow, as indexes: each Process after those whose outputs it
 * reads. A cycle is cut where a depth-first search in the model's order closes it; among those
 * that are free to come next, the model's order decides.
 */
export function ringOrder(model: GraphModel): number[] {
  const n = model.processes.length;
  const successors = model.processes.map(() => new Set<number>());
  for (const { producers, consumers } of usesOf(model).values())
    for (const u of producers) for (const v of consumers) if (u !== v) successors[u]?.add(v);

  const state = Array.from({ length: n }, () => 0);
  const back = new Set<string>();
  const visit = (u: number): void => {
    state[u] = 1;
    for (const v of [...(successors[u] ?? [])].sort((a, b) => a - b)) {
      if (state[v] === 1) back.add(`${u}>${v}`);
      else if (state[v] === 0) visit(v);
    }
    state[u] = 2;
  };
  for (let i = 0; i < n; i++) if (state[i] === 0) visit(i);

  const indegree = Array.from({ length: n }, () => 0);
  for (let u = 0; u < n; u++)
    for (const v of successors[u] ?? [])
      if (!back.has(`${u}>${v}`)) indegree[v] = (indegree[v] ?? 0) + 1;
  const ready: number[] = [];
  for (let i = 0; i < n; i++) if (indegree[i] === 0) ready.push(i);
  const order: number[] = [];
  while (ready.length > 0) {
    ready.sort((a, b) => a - b);
    const u = ready.shift() ?? 0;
    order.push(u);
    for (const v of successors[u] ?? []) {
      if (back.has(`${u}>${v}`)) continue;
      indegree[v] = (indegree[v] ?? 0) - 1;
      if (indegree[v] === 0) ready.push(v);
    }
  }
  return order;
}

/**
 * Moves angles apart until neighbours are at least `gap` apart (around the circle), pushing each
 * close pair equally. Sorts the items by angle.
 */
export function spread(items: { angle: number }[], gap: number): void {
  const m = items.length;
  if (m < 2) return;
  const g = Math.min(gap, TAU / m);
  items.sort((a, b) => a.angle - b.angle);
  for (let iteration = 0; iteration < 400; iteration++) {
    let moved = false;
    for (let i = 0; i < m; i++) {
      const j = (i + 1) % m;
      const a = items[i];
      const b = items[j];
      if (!a || !b) continue;
      const next = j === 0 ? b.angle + TAU : b.angle;
      const d = next - a.angle;
      if (d < g - 1e-6) {
        const push = (g - d) / 2;
        a.angle -= push;
        b.angle += push;
        moved = true;
      }
    }
    if (!moved) break;
  }
}

/** The direction of the sum of unit vectors at the angles; `null` when they cancel out. */
export function centroidAngle(angles: readonly number[]): number | null {
  let x = 0;
  let y = 0;
  for (const angle of angles) {
    x += Math.cos(angle);
    y += Math.sin(angle);
  }
  return Math.hypot(x, y) > 1e-6 ? Math.atan2(y, x) : null;
}

/** The middle of the widest gap between the angles. */
function widestGap(angles: readonly number[]): number {
  const sorted = [...angles].sort((a, b) => a - b);
  if (sorted.length === 0) return -Math.PI / 2;
  let best = sorted[0] ?? 0;
  let widest = -1;
  sorted.forEach((angle, i) => {
    const next = i + 1 < sorted.length ? (sorted[i + 1] ?? angle) : (sorted[0] ?? angle) + TAU;
    if (next - angle > widest) {
      widest = next - angle;
      best = angle + widest / 2;
    }
  });
  return best;
}

/** How far from its centre a pill's edge is, along the radius at `angle`. */
function pillReach(angle: number, width: number, height: number): number {
  const c = Math.abs(Math.cos(angle));
  const s = Math.abs(Math.sin(angle));
  return Math.min(c > 1e-6 ? width / 2 / c : Infinity, s > 1e-6 ? height / 2 / s : Infinity);
}

/** Whether two pills overlap, with `pad` pixels to spare. */
const overlapping = (a: RingPill, b: RingPill, pad: number): boolean =>
  Math.abs(a.x - b.x) < (a.width + b.width) / 2 + pad &&
  Math.abs(a.y - b.y) < (a.height + b.height) / 2 + pad;

/** How far from the centre a pill's farthest corner is. */
const farthest = (pill: RingPill): number =>
  Math.hypot(Math.abs(pill.x) + pill.width / 2, Math.abs(pill.y) + pill.height / 2);

const moveTo = (pill: RingPill, angle: number): void => {
  pill.angle = angle;
  pill.x = pill.radius * Math.cos(angle);
  pill.y = pill.radius * Math.sin(angle);
};

/**
 * Pills that still overlap once they are spread (long names) move apart along their radii, a
 * little at a time. Whether no pill overlaps another or reaches the ring of the Processes.
 */
function separate(pills: RingPill[], radius: number): boolean {
  const inside = (pill: RingPill): boolean =>
    farthest(pill) <= radius - RING.dot - RING.pillClearance;
  for (let iteration = 0; iteration < RING.separateIterations; iteration++) {
    let moved = false;
    for (let i = 0; i < pills.length; i++)
      for (let j = i + 1; j < pills.length; j++) {
        const a = pills[i];
        const b = pills[j];
        if (!a || !b || !overlapping(a, b, RING.pillClearance)) continue;
        // The one behind (counterclockwise) steps back, the other forward.
        const ahead = wrapAngle(b.angle - a.angle) >= 0;
        moveTo(a, a.angle + (ahead ? -RING.separateStep : RING.separateStep));
        moveTo(b, b.angle + (ahead ? RING.separateStep : -RING.separateStep));
        moved = true;
      }
    if (!moved) return pills.every(inside);
  }
  return false;
}

export function ringLayout(model: GraphModel, measure: Measure): RingLayout {
  const n = model.processes.length;
  const angleOf = new Map<number, number>();
  ringOrder(model).forEach((index, k) => {
    angleOf.set(index, -Math.PI / 2 + ((k + 0.5) * TAU) / Math.max(1, n));
  });

  // Each type sits at the centroid of the Processes it connects; one that connects none goes into
  // the widest gap.
  const uses = usesOf(model);
  const placed: { index: number; angle: number }[] = [];
  const loose: number[] = [];
  model.types.forEach((type, index) => {
    const use = uses.get(type.id);
    const linked = [...new Set([...(use?.producers ?? []), ...(use?.consumers ?? [])])];
    if (linked.length === 0) {
      loose.push(index);
      return;
    }
    const angles = linked.map((p) => angleOf.get(p) ?? 0);
    placed.push({ index, angle: centroidAngle(angles) ?? (angles[0] ?? 0) + Math.PI / 2 });
  });
  for (const index of loose) placed.push({ index, angle: widestGap(placed.map((p) => p.angle)) });
  spread(placed, RING.gap);

  // Neighbours alternate between the two radii. When long names still overlap after they move
  // apart, or reach the Processes, the whole ring grows.
  let radius = RING.radius + Math.max(0, n - 11) * RING.perProcess;
  let pills: RingPill[] = [];
  for (let attempt = 0; attempt <= RING.growths; attempt++) {
    const r = radius;
    pills = placed.map(({ index, angle }, rank) => {
      const type = model.types[index] ?? { id: "", name: "" };
      const pillRadius = r * (rank % 2 === 1 ? RING.outer : RING.inner);
      return {
        id: type.id,
        name: type.name,
        angle,
        radius: pillRadius,
        x: pillRadius * Math.cos(angle),
        y: pillRadius * Math.sin(angle),
        width: measure(type.name, "type") + RING.pillPadding,
        height: RING.pillHeight,
      };
    });
    if (separate(pills, radius) || attempt === RING.growths) break;
    radius *= RING.growth;
  }
  const pillOf = new Map(pills.map((pill) => [pill.id, pill]));

  const processes: RingProcess[] = model.processes.map((process, index) => {
    const angle = angleOf.get(index) ?? 0;
    const x = radius * Math.cos(angle);
    const y = radius * Math.sin(angle);
    const c = Math.cos(angle);
    const width = measure(process.name, "process");
    const label: RingProcess["label"] =
      Math.abs(c) < 0.15
        ? { x, y: Math.sin(angle) > 0 ? y + 23 : y - 23, anchor: "middle", width }
        : c > 0
          ? { x: x + RING.labelGap, y, anchor: "start", width }
          : { x: x - RING.labelGap, y, anchor: "end", width };
    return { id: process.id, name: process.name, angle, x, y, label };
  });

  // The lines of a Process and a type, one per role, set apart when there are several.
  const edges: Edge[] = [];
  const order: Role[] = ["input", "control", "output"];
  model.processes.forEach((process, index) => {
    const angle = angleOf.get(index) ?? 0;
    const roles = new Map<string, Role[]>();
    const add = (type: string, role: Role): void => {
      const list = roles.get(type) ?? [];
      if (!list.includes(role)) list.push(role);
      roles.set(type, list);
    };
    for (const type of process.inputs) add(type, "input");
    for (const type of process.controls) add(type, "control");
    for (const type of process.outputs) add(type, "output");
    for (const [type, list] of roles) {
      const pill = pillOf.get(type);
      if (!pill) continue;
      list.sort((a, b) => order.indexOf(a) - order.indexOf(b));
      const end = pill.radius + pillReach(pill.angle, pill.width, pill.height) + 1;
      const base = band(angle, pill.angle, radius - RING.lineInset, end);
      list.forEach((role, j) => {
        const offset = (j - (list.length - 1) / 2) * RING.roleSpacing;
        // An output flows from the Process to the type; an input or a control the other way.
        const points: Point[] =
          role === "output"
            ? offsetPoints(base, offset)
            : offsetPoints([...base].reverse(), -offset);
        const last = points[points.length - 1] ?? [0, 0];
        const before = points[points.length - 2] ?? last;
        edges.push({
          role,
          process: process.id,
          type,
          d: toPath(points),
          head: arrowHead(before, last),
        });
      });
    }
  });

  // Everything, with a margin.
  let left = -radius;
  let right = radius;
  let top = -radius;
  let bottom = radius;
  const include = (x1: number, y1: number, x2: number, y2: number): void => {
    left = Math.min(left, x1);
    right = Math.max(right, x2);
    top = Math.min(top, y1);
    bottom = Math.max(bottom, y2);
  };
  for (const p of processes) {
    const { label } = p;
    const x1 =
      label.anchor === "start"
        ? label.x
        : label.anchor === "end"
          ? label.x - label.width
          : label.x - label.width / 2;
    include(x1, label.y - RING.labelHeight / 2, x1 + label.width, label.y + RING.labelHeight / 2);
    include(p.x - RING.dot, p.y - RING.dot, p.x + RING.dot, p.y + RING.dot);
  }
  for (const pill of pills)
    include(
      pill.x - pill.width / 2,
      pill.y - pill.height / 2,
      pill.x + pill.width / 2,
      pill.y + pill.height / 2,
    );
  const m = RING.margin;
  return {
    viewBox: { x: left - m, y: top - m, width: right - left + 2 * m, height: bottom - top + 2 * m },
    radius,
    processes,
    pills,
    edges,
  };
}
