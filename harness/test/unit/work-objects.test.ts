import { expect, test } from "bun:test";
import type { DesignSession, InstanceView, LaunchRecord, Run } from "../../src/shared/types.ts";
import { buildWorkObjects } from "../../src/harness/work-objects.ts";

const run = (id: string, extra: Partial<Run> = {}): Run => ({
  id,
  kind: "process",
  instance: "i1",
  process: "P",
  agent: "codex",
  status: "succeeded",
  createdAt: 1,
  startedAt: 1,
  endedAt: 2,
  exitCode: 0,
  error: null,
  agentError: null,
  inputs: [],
  targets: [],
  outputs: [],
  usage: null,
  report: "Recorded result",
  events: 0,
  command: null,
  client: null,
  prompt: "private prompt",
  git: null,
  skill: null,
  ...extra,
});
const instance = (id: string, runs: string[]): InstanceView => ({
  id,
  process: "P",
  inputs: {},
  outputs: {},
  criteria: [],
  notes: "",
  runs,
  evaluation: null,
  facts: {
    instance: id,
    process: "P",
    latestRun: null,
    judgments: null,
    evaluatedRun: null,
    stale: false,
    staleness: [],
  },
});

test("shared sessions and applications do not attribute every participant to every work", () => {
  const records = [
    run("r1", { kind: "wake", instance: null, request: "Release A", started: ["r3"] }),
    run("r2", { kind: "wake", instance: null, request: "Release B", started: ["r4"] }),
    run("r3", {
      execution: {
        method: "cli",
        session: {
          id: "same-session",
          source: "agent-output",
          capturedAt: 1,
          coverage: "reference-only",
        },
      },
    }),
    run("r4", {
      execution: {
        method: "cli",
        session: {
          id: "other-session",
          source: "agent-output",
          capturedAt: 1,
          coverage: "reference-only",
        },
      },
    }),
    run("r5", {
      instance: "i2",
      execution: {
        method: "cli",
        session: {
          id: "same-session",
          source: "agent-output",
          capturedAt: 1,
          coverage: "reference-only",
        },
      },
    }),
  ];
  const graph = buildWorkObjects({
    runs: records,
    instances: [instance("i1", ["r3", "r4"]), instance("i2", ["r5"])],
    designs: [],
    launches: [],
    processes: [],
  });
  expect(graph.applications.find((item) => item.id === "instance-i1")?.workIds.sort()).toEqual([
    "run-r1",
    "run-r2",
  ]);
  expect(graph.participations.find((item) => item.id === "run-r3")?.workIds).toEqual(["run-r1"]);
  expect(graph.participations.find((item) => item.id === "run-r4")?.workIds).toEqual(["run-r2"]);
  expect(graph.sessions).toHaveLength(2);
  expect(
    graph.sessions.find((item) => item.providerSessionId === "same-session")?.applicationIds.sort(),
  ).toEqual(["instance-i1", "instance-i2"]);
  expect(JSON.stringify(graph)).not.toContain("private prompt");
});

test("MCP transport identities and unidentified executions are not fabricated provider sessions", () => {
  const graph = buildWorkObjects({
    runs: [run("r1", { client: { name: "codex", version: "1", session: "transport-1" } })],
    instances: [instance("i1", ["r1"])],
    designs: [],
    launches: [],
    processes: [],
  });
  expect(graph.sessions).toEqual([]);
  expect(graph.coverage.unidentifiedSessions).toBe(1);
  expect(graph.participations[0]?.sessionId).toBeNull();
});

test("explicit continued work keeps the original scope and two requests can share one application", () => {
  const original = run("r1", {
    kind: "wake",
    instance: null,
    request: "Release A",
    started: ["r3"],
  });
  const launch: LaunchRecord = {
    id: "next",
    createdAt: 3,
    status: "started",
    request: {
      id: "next",
      kind: "wake",
      agent: "codex",
      method: "cli",
      request: "Continue checking",
      workIds: ["run-r1"],
    },
    runId: "r2",
    error: null,
  };
  const graph = buildWorkObjects({
    runs: [
      original,
      run("r2", { kind: "wake", instance: null, request: "Continue checking", started: ["r4"] }),
      run("r3"),
      run("r4"),
    ],
    instances: [instance("i1", ["r3", "r4"])],
    designs: [],
    launches: [launch],
    processes: [],
  });
  expect(graph.works).toHaveLength(1);
  expect(graph.works[0]?.id).toBe("run-r1");
  expect(graph.works[0]?.sources).toContainEqual({ kind: "launch", id: "next" });
  expect(graph.participations.find((item) => item.id === "run-r4")?.workIds).toEqual(["run-r1"]);
});

test("resume provenance does not create a second work and retains session handoff", () => {
  const records = [
    run("r1", {
      kind: "wake",
      instance: null,
      request: "Original",
      execution: { method: "cli", sessionId: "s1" },
    }),
    run("r2", {
      kind: "wake",
      instance: null,
      request: "Resume",
      execution: { method: "cli", sessionId: "s2", resumedFrom: "r1" },
    }),
  ];
  const launch: LaunchRecord = {
    id: "resume",
    createdAt: 3,
    status: "started",
    request: {
      id: "resume",
      kind: "wake",
      agent: "codex",
      method: "cli",
      request: "Resume",
      resumedFrom: "r1",
    },
    runId: "r2",
    error: null,
  };
  const graph = buildWorkObjects({
    runs: records,
    instances: [],
    designs: [],
    launches: [launch],
    processes: [],
  });
  expect(graph.works.map((work) => work.id)).toEqual(["run-r1"]);
  expect(
    graph.sessions.find((session) => session.providerSessionId === "s2")?.links[0]?.sessionId,
  ).toBe(graph.sessions.find((session) => session.providerSessionId === "s1")?.id);
});

test("a pending continuation can belong to multiple works without claiming execution", () => {
  const records = [
    run("r1", { kind: "wake", instance: null, request: "A" }),
    run("r2", { kind: "wake", instance: null, request: "B" }),
  ];
  const launch: LaunchRecord = {
    id: "next",
    createdAt: 10,
    status: "pending",
    request: {
      id: "next",
      kind: "wake",
      agent: "codex",
      method: "desktop",
      request: "Compare",
      workIds: ["run-r1", "run-r2"],
    },
    runId: null,
    error: null,
  };
  const graph = buildWorkObjects({
    runs: records,
    instances: [],
    designs: [],
    launches: [launch],
    processes: [],
  });
  expect(graph.works).toHaveLength(2);
  for (const work of graph.works) {
    expect(work.status).toBe("waiting");
    expect(work.updatedAt).toBe(10);
    expect(work.sources).toContainEqual({ kind: "launch", id: "next" });
    expect(work.participationIds).toHaveLength(1);
  }
});

test("an assessment applies its own process; reading a target is not performing that target", () => {
  const records = [
    run("r1"),
    run("r2", {
      kind: "assess",
      instance: null,
      process: null,
      scope: { process: "P" },
      request: "Assess P",
    }),
  ];
  const graph = buildWorkObjects({
    runs: records,
    instances: [instance("i1", ["r1"])],
    designs: [],
    launches: [],
    processes: [],
  });
  const assessment = graph.applications.find((item) => item.id === "assessment-r2")!;
  expect(assessment.kind).toBe("assessment");
  expect(assessment.instance).toBeNull();
  expect(assessment.workIds).toEqual(["run-r2"]);
  expect(graph.applications.find((item) => item.id === "instance-i1")?.workIds).not.toContain(
    "run-r2",
  );
});

test("modeling participates in its explicit works without inventing a business instance or execution", () => {
  const design: DesignSession = {
    id: "design-01",
    workIds: ["run-r1", "run-r2"],
    provider: "codex",
    status: "needs-input",
    createdAt: 3,
    updatedAt: 4,
    request: "Improve the shared process description",
    process: "P",
    references: [],
    method: "desktop",
    agent: "designer",
    expectedRevision: "revision",
    messages: [],
    proposal: null,
    error: null,
    command: null,
    sources: [],
    desktop: { provider: "codex", prompt: "private prompt", sessionId: "conversation" },
  };
  const graph = buildWorkObjects({
    runs: [
      run("r1", { kind: "wake", instance: null, request: "A" }),
      run("r2", { kind: "wake", instance: null, request: "B" }),
    ],
    instances: [],
    designs: [design],
    launches: [],
    processes: [],
  });
  expect(graph.works).toHaveLength(2);
  expect(graph.works.every((work) => work.status === "waiting")).toBe(true);
  expect(graph.applications).toHaveLength(1);
  expect(graph.applications[0]?.kind).toBe("modeling");
  expect(graph.applications[0]?.instance).toBeNull();
  expect(graph.applications[0]?.workIds).toEqual(["run-r1", "run-r2"]);
  expect(graph.sessions[0]?.workIds).toEqual(["run-r1", "run-r2"]);
  expect(graph.participations.find((part) => part.role === "modeling")?.source).toEqual({
    kind: "design",
    id: design.id,
  });
  expect(JSON.stringify(graph)).not.toContain("private prompt");
});

test("continuing multiple planned instance roots resolves them before the new launch", () => {
  const launch: LaunchRecord = {
    id: "next",
    createdAt: 10,
    status: "started",
    request: {
      id: "next",
      kind: "wake",
      agent: "codex",
      method: "cli",
      request: "Compare",
      workIds: ["instance-i1", "instance-i2"],
    },
    runId: "r1",
    error: null,
  };
  const graph = buildWorkObjects({
    runs: [run("r1", { kind: "wake", instance: null })],
    instances: [instance("i1", []), instance("i2", [])],
    designs: [],
    launches: [launch],
    processes: [],
  });
  expect(graph.works.map((work) => work.id).sort()).toEqual(["instance-i1", "instance-i2"]);
  expect(graph.participations[0]?.workIds.sort()).toEqual(["instance-i1", "instance-i2"]);
  expect(graph.coverage.unreadableRecords).toEqual([]);
});

test("agent configurations on the same provider do not split one observed conversation", () => {
  const graph = buildWorkObjects({
    runs: [
      run("r1", {
        agent: "reviewer",
        execution: { method: "cli", provider: "codex", sessionId: "conversation" },
      }),
      run("r2", {
        agent: "implementer",
        execution: { method: "cli", provider: "codex", sessionId: "conversation" },
      }),
    ],
    instances: [instance("i1", ["r1", "r2"])],
    designs: [],
    launches: [],
    processes: [],
  });
  expect(graph.sessions).toHaveLength(1);
  expect(graph.sessions[0]?.provider).toBe("codex");
  expect(graph.sessions[0]?.agents.sort()).toEqual(["implementer", "reviewer"]);
});
