/*
 * The layout of the network view (Screen design): the ring R1a (Processes in the order of the
 * flow, type pills at the centroid of their Processes, set apart and on alternating radii) and
 * the focus view G4 (five columns around a Process, three around a type), on the example model.
 */

import { describe, expect, test } from "bun:test";
import fs from "node:fs";
import path from "node:path";
import { focusLayout, FOCUS } from "../../src/ui/graph/focus.ts";
import {
  estimateWidth,
  fitText,
  TAU,
  wrapAngle,
  type GraphModel,
} from "../../src/ui/graph/geometry.ts";
import { centroidAngle, ringLayout, ringOrder, RING, spread } from "../../src/ui/graph/ring.ts";
import { EXAMPLES } from "../helpers/paths.ts";

interface ModelFile {
  processes: {
    name: string;
    purpose?: string;
    inputs?: string[];
    controls?: string[];
    outputs?: string[];
  }[];
  artifacts: { name: string }[];
}

/** An example model (11 Processes, 15 types); ids are the names, as the model gives no ids. */
function exampleModel(...segments: string[]): GraphModel {
  const file = Bun.YAML.parse(
    fs.readFileSync(
      path.join(EXAMPLES, ...segments, "service-change", "process-model.yaml"),
      "utf8",
    ),
  ) as ModelFile;
  return {
    processes: file.processes.map((p) => ({
      id: p.name,
      name: p.name,
      purpose: p.purpose ?? "",
      inputs: p.inputs ?? [],
      controls: p.controls ?? [],
      outputs: p.outputs ?? [],
    })),
    types: file.artifacts.map((a) => ({ id: a.name, name: a.name })),
  };
}
const example = exampleModel();
/** The Japanese counterpart, whose names the design prototypes used. */
const japanese = exampleModel("locales", "ja");

const graph = (
  processes: [string, { inputs?: string[]; controls?: string[]; outputs?: string[] }][],
  types: string[],
): GraphModel => ({
  processes: processes.map(([id, p]) => ({
    id,
    name: id,
    inputs: p.inputs ?? [],
    controls: p.controls ?? [],
    outputs: p.outputs ?? [],
  })),
  types: types.map((id) => ({ id, name: id })),
});

describe("the ring (R1a)", () => {
  test("the Processes follow the flow: each after those whose outputs it reads, a cycle cut where a search in the model's order closes it", () => {
    // The example model lists its Processes in the order of the flow already.
    expect(ringOrder(example)).toEqual([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]);
    const shuffled = graph(
      [
        ["C", { inputs: ["y"] }],
        ["A", { outputs: ["x"], inputs: ["z"] }],
        ["B", { inputs: ["x"], outputs: ["y"] }],
        ["D", { inputs: ["y"], outputs: ["z"] }],
      ],
      ["x", "y", "z"],
    );
    // A → B → C and D; D → A closes a cycle, which is cut there.
    expect(ringOrder(shuffled).map((i) => shuffled.processes[i]?.id)).toEqual(["A", "B", "C", "D"]);
  });

  test("spreading keeps neighbours at least the gap apart around the circle, or nearly evenly spaced when that cannot be kept", () => {
    const items = [0.1, 0.12, 0.13, 3, -3].map((angle) => ({ angle }));
    spread(items, 0.34);
    const sorted = items.map((i) => i.angle);
    for (let i = 0; i < sorted.length; i++) {
      const next = i + 1 < sorted.length ? sorted[i + 1]! : sorted[0]! + TAU;
      expect(next - sorted[i]!).toBeGreaterThanOrEqual(0.34 - 1e-6);
    }
    const crowded = Array.from({ length: 30 }, () => ({ angle: 1 }));
    spread(crowded, 0.34);
    const gaps = crowded.map((item, i) =>
      i + 1 < crowded.length
        ? crowded[i + 1]!.angle - item.angle
        : crowded[0]!.angle + TAU - item.angle,
    );
    expect(Math.min(...gaps)).toBeGreaterThanOrEqual((TAU / 30) * 0.95);
    expect(centroidAngle([0, Math.PI])).toBeNull();
    expect(centroidAngle([0, Math.PI / 2])).toBeCloseTo(Math.PI / 4);
  });

  test("the example model gives 11 Processes on the ring, 15 pills inside, and a line for each role of each Process", () => {
    const layout = ringLayout(example, estimateWidth);
    expect(layout.processes).toHaveLength(11);
    expect(layout.pills).toHaveLength(15);
    expect(new Set(layout.pills.map((p) => p.id)).size).toBe(15);
    // Requirements Clarification: 3 inputs and 1 output; …; Production Release: 2 inputs, 2 controls, 1 output.
    expect(layout.edges).toHaveLength(40);
    expect(layout.edges.filter((e) => e.role === "control")).toHaveLength(9);
    // The first Process is just right of the top, and the Processes go round clockwise.
    const first = layout.processes[0]!;
    expect(first.angle).toBeCloseTo(-Math.PI / 2 + Math.PI / 11);
    expect(first.label.anchor).toBe("start");
    expect(layout.processes[6]!.label.anchor).toBe("end");
    for (const p of layout.processes) expect(Math.hypot(p.x, p.y)).toBeCloseTo(layout.radius);
  });

  test("pills alternate between two radii, and no two overlap or reach the ring of the Processes, however long their names", () => {
    for (const model of [example, japanese]) {
      const { pills, radius } = ringLayout(model, estimateWidth);
      const radii = pills.map((p) => p.radius / radius);
      expect(radii.filter((r) => Math.abs(r - RING.inner) < 1e-9)).toHaveLength(8);
      expect(radii.filter((r) => Math.abs(r - RING.outer) < 1e-9)).toHaveLength(7);
      pills.forEach((a, i) => {
        expect(
          Math.hypot(Math.abs(a.x) + a.width / 2, Math.abs(a.y) + a.height / 2),
        ).toBeLessThanOrEqual(radius - RING.dot);
        expect(a.width).toBeCloseTo(estimateWidth(a.name, "type") + RING.pillPadding);
        for (const b of pills.slice(i + 1)) {
          const apart =
            Math.abs(a.x - b.x) >= (a.width + b.width) / 2 ||
            Math.abs(a.y - b.y) >= (a.height + b.height) / 2;
          expect(apart, `${a.name} and ${b.name}`).toBe(true);
        }
      });
    }
  });

  test("with the short names of the design (the Japanese model), the ring keeps the design's size; longer names make it grow", () => {
    expect(ringLayout(japanese, estimateWidth).radius).toBe(RING.radius);
    expect(ringLayout(example, estimateWidth).radius).toBeGreaterThan(RING.radius);
  });

  test("a pill sits at the centroid of the Processes it connects, and one that connects none goes into the widest gap", () => {
    const layout = ringLayout(
      graph(
        [
          ["P", { outputs: ["only P"] }],
          ["Q", { inputs: ["only P"] }],
          ["R", {}],
          ["S", {}],
        ],
        ["only P", "loose"],
      ),
      estimateWidth,
    );
    const [p, q] = layout.processes;
    const shared = layout.pills.find((pill) => pill.id === "only P")!;
    expect(shared.angle).toBeCloseTo(centroidAngle([p!.angle, q!.angle])!);
    const loose = layout.pills.find((pill) => pill.id === "loose")!;
    expect(Math.abs(wrapAngle(loose.angle - shared.angle))).toBeCloseTo(Math.PI);
  });

  test("lines end at a pill's edge, and the drawing holds every name", () => {
    const layout = ringLayout(example, estimateWidth);
    const { x, y, width, height } = layout.viewBox;
    for (const p of layout.processes) {
      const left =
        p.label.anchor === "start"
          ? p.label.x
          : p.label.anchor === "end"
            ? p.label.x - p.label.width
            : p.label.x - p.label.width / 2;
      expect(left).toBeGreaterThanOrEqual(x);
      expect(left + p.label.width).toBeLessThanOrEqual(x + width);
      expect(p.label.y).toBeGreaterThanOrEqual(y);
      expect(p.label.y).toBeLessThanOrEqual(y + height);
    }
    // The inward-bowing curve reaches the pill's boundary from the centre of the diagram.
    const edge = layout.edges.find((e) => e.role === "output" && e.type === "Design description")!;
    const pill = layout.pills.find((p) => p.id === "Design description")!;
    const tip = /L(-?[\d.]+) (-?[\d.]+)L/.exec(edge.head)!;
    const distance = Math.hypot(Number(tip[1]), Number(tip[2]));
    expect(distance).toBeLessThan(pill.radius);
    expect(distance).toBeGreaterThan(pill.radius - Math.hypot(pill.width, pill.height) / 2 - 2);
    const [tipX, tipY] = [Number(tip[1]), Number(tip[2])];
    expect(
      Math.abs(tipX - pill.x) >= pill.width / 2 || Math.abs(tipY - pill.y) >= pill.height / 2,
    ).toBe(true);
  });
});

describe("the focus view (G4)", () => {
  test("a Process's focus has five columns: the producers of its inputs, its inputs and controls, itself, its outputs, and their users", () => {
    const layout = focusLayout(
      example,
      { kind: "process", id: "Service Change Assessment" },
      estimateWidth,
    )!;
    expect(layout.columns.map((c) => c.title)).toEqual([
      "producers",
      "inputs",
      "process",
      "outputs",
      "consumers",
    ]);
    const inColumn = (n: number) =>
      layout.nodes.filter((node) => node.column === n).map((node) => node.id);
    expect(inColumn(0)).toEqual(["Pilot Measurement"]);
    expect(inColumn(1)).toEqual(["Request measurements", "Pilot conditions"]);
    expect(inColumn(2)).toEqual(["Service Change Assessment"]);
    expect(inColumn(3)).toEqual(["Pilot assessment"]);
    expect(inColumn(4)).toEqual(["Production Release Decision", "Change Retrospective"]);
    // Pilot conditions is an input and a control: two lines reach the Process from it.
    expect(layout.edges.map((e) => `${e.role} ${e.process} ${e.type}`)).toEqual([
      "output Pilot Measurement Request measurements",
      "input Service Change Assessment Request measurements",
      "input Service Change Assessment Pilot conditions",
      "control Service Change Assessment Pilot conditions",
      "output Service Change Assessment Pilot assessment",
      "input Production Release Decision Pilot assessment",
      "input Change Retrospective Pilot assessment",
    ]);
    const focused = layout.nodes.find((n) => n.focused)!;
    expect(focused).toMatchObject({
      x: FOCUS.processColumns[2]!.x,
      height: FOCUS.focusHeight.process,
    });
    expect(focused.note.length).toBeGreaterThan(0);
  });

  test("a type read only as a control is dashed, and the Process itself is left out of its neighbours", () => {
    const layout = focusLayout(
      example,
      { kind: "process", id: "Pilot Measurement" },
      estimateWidth,
    )!;
    const types = layout.nodes.filter((n) => n.column === 1);
    expect(types.map((n) => [n.id, n.dashed])).toEqual([
      ["Release candidate", false],
      ["Pilot conditions", true],
    ]);
    const itself = focusLayout(
      example,
      { kind: "process", id: "Requirements Clarification" },
      estimateWidth,
    )!;
    expect(itself.nodes.filter((n) => n.id === "Requirements Clarification")).toHaveLength(1);
    expect(itself.nodes.filter((n) => n.column === 0).map((n) => n.id)).toEqual([
      "Feasibility Assessment",
      "Change Retrospective",
    ]);
  });

  test("a type's focus has three columns: the Processes that produce it, the type, and those that read it", () => {
    const layout = focusLayout(example, { kind: "type", id: "Change brief" }, estimateWidth)!;
    expect(layout.columns.map((c) => c.title)).toEqual(["typeProducers", "type", "typeConsumers"]);
    expect(layout.nodes.filter((n) => n.column === 0).map((n) => n.id)).toEqual([
      "Requirements Clarification",
      "Feasibility Assessment",
    ]);
    expect(layout.nodes.filter((n) => n.column === 2).map((n) => n.id)).toEqual([
      "Requirements Clarification",
      "Feasibility Assessment",
      "Solution Design",
      "Production Release Decision",
    ]);
    const given = focusLayout(example, { kind: "type", id: "Acceptance criteria" }, estimateWidth)!;
    expect(given.nodes.filter((n) => n.column === 0)).toEqual([]);
    expect(given.edges.map((e) => e.role)).toEqual(["control", "control"]);
    expect(focusLayout(example, { kind: "type", id: "No such type" }, estimateWidth)).toBeNull();
    expect(
      focusLayout(example, { kind: "process", id: "No such Process" }, estimateWidth),
    ).toBeNull();
  });

  test("the focus view grows taller with more nodes, and names that do not fit are cut with an ellipsis", () => {
    const types = Array.from({ length: 20 }, (_, i) => `type ${i}`);
    const wide = focusLayout(
      graph([["P", { inputs: types }]], types),
      { kind: "process", id: "P" },
      estimateWidth,
    )!;
    expect(wide.height).toBeGreaterThan(FOCUS.minHeight);
    const ys = wide.nodes.filter((n) => n.column === 1).map((n) => n.y);
    expect(Math.min(...ys)).toBeGreaterThanOrEqual(FOCUS.top);
    expect(Math.max(...ys)).toBeLessThanOrEqual(wide.height - FOCUS.bottom);
    const long = "A very long type name that cannot fit into one node of the focus view";
    const cut = fitText(long, "type", 176, estimateWidth);
    expect(cut.endsWith("…")).toBe(true);
    expect(estimateWidth(cut, "type")).toBeLessThanOrEqual(176);
  });
});
