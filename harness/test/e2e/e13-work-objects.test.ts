import { afterAll, beforeAll, expect, test } from "bun:test";
import fs from "node:fs";
import path from "node:path";
import type {
  ArtifactContentResponse,
  Failure,
  InstanceResponse,
  RunDetailResponse,
  RunStartResponse,
} from "../../src/shared/types.ts";
import { apiClient, type Api } from "../helpers/api.ts";
import { startDaemon, type Daemon } from "../helpers/daemon.ts";
import { HOOK_TIMEOUT_MS } from "../helpers/process.ts";
import { tmpWorkspace, type TmpWorkspace } from "../helpers/workspace.ts";

let ws: TmpWorkspace;
let daemon: Daemon;
let api: Api;
beforeAll(async () => {
  ws = tmpWorkspace({
    server: { idleMinutes: 5 },
    agents: {
      "claude-code": {
        command: path.resolve(import.meta.dir, "../fakes/wake-agent.ts"),
        env: { ALPS_FAKE_SCENARIO: "ok" },
      },
    },
  });
  daemon = await startDaemon(ws.root);
  api = apiClient(daemon);
}, HOOK_TIMEOUT_MS);
afterAll(async () => {
  await daemon?.stop();
  ws?.dispose();
}, HOOK_TIMEOUT_MS);

async function completedInstance() {
  const { instance } = await api.ok<InstanceResponse>("POST", "/api/instances", {
    process: "Requirements Clarification",
  });
  const { run } = await api.ok<RunStartResponse>("POST", `/api/instances/${instance.id}/run`, {
    agent: "demo",
  });
  await api.ok<RunDetailResponse>("GET", `/api/runs/${run.id}?wait=30`);
  return (await api.ok<InstanceResponse>("GET", `/api/instances/${instance.id}`)).instance;
}

test("E13 a judgment remains bound to the displayed run and criteria, including after restart", async () => {
  const instance = await completedInstance();
  const context = instance.evaluationContext!;
  expect(context.runId).toBe(instance.runs.at(-1)!);
  const judgments = [
    { outcome: 0, judgment: "unverified", evidence: "The acceptance test is missing." },
  ];
  await api.ok("POST", "/api/instances", {
    instance: instance.id,
    criteria: [{ outcome: 0, statement: "The acceptance test covers the new requirement." }],
  });
  const stale = await api.post(`/api/instances/${instance.id}/evaluate`, {
    judgments,
    expected: context,
  });
  expect((stale.body as Failure).error.key).toBe("error.evaluationChanged");
  const current = (await api.ok<InstanceResponse>("GET", `/api/instances/${instance.id}`)).instance;
  const evaluated = await api.ok<InstanceResponse>(
    "POST",
    `/api/instances/${instance.id}/evaluate`,
    {
      judgments,
      expected: current.evaluationContext,
    },
  );
  expect(evaluated.instance.evaluation?.basis?.criteria[0]?.statement).toContain("new requirement");
  const { run } = await api.ok<RunStartResponse>("POST", `/api/instances/${instance.id}/run`, {
    agent: "demo",
  });
  await api.ok("GET", `/api/runs/${run.id}?wait=30`);
  const changedRun = await api.post(`/api/instances/${instance.id}/evaluate`, {
    judgments,
    expected: current.evaluationContext,
  });
  expect((changedRun.body as Failure).error.key).toBe("error.evaluationChanged");
  await daemon.stop();
  daemon = await startDaemon(ws.root);
  api = apiClient(daemon);
  const restored = (await api.ok<InstanceResponse>("GET", `/api/instances/${instance.id}`))
    .instance;
  expect(restored.evaluation?.runId).toBe(context.runId);
  expect(restored.evaluation?.basis).toEqual(evaluated.instance.evaluation?.basis);
}, 60_000);

test("E13 evidence preview shows bounded current content and refuses workspace escapes and runtime records", async () => {
  fs.mkdirSync(path.join(ws.root, "evidence"), { recursive: true });
  fs.writeFileSync(path.join(ws.root, "evidence", "check.md"), "# Check\nObserved result.\n");
  fs.writeFileSync(path.join(ws.root, "evidence", "large.txt"), "a".repeat(300_000));
  fs.symlinkSync(ws.base, path.join(ws.root, "evidence", "outside"));
  const preview = await api.ok<ArtifactContentResponse>(
    "GET",
    "/api/artifact-content?path=evidence%2Fcheck.md",
  );
  expect(preview.artifact.kind).toBe("text");
  expect(preview.artifact.text).toContain("Observed result");
  expect(preview.artifact.sha256).toMatch(/^[a-f0-9]{64}$/);
  const large = await api.ok<ArtifactContentResponse>(
    "GET",
    "/api/artifact-content?path=evidence%2Flarge.txt",
  );
  expect(large.artifact.truncated).toBe(true);
  expect(large.artifact.text!.length).toBeLessThanOrEqual(262144);
  const directory = await api.ok<ArtifactContentResponse>(
    "GET",
    "/api/artifact-content?path=evidence",
  );
  expect(directory.artifact.entries?.map((entry) => entry.path)).toContain("evidence/check.md");
  for (const unsafe of ["../outside", ".alps-harness/state.json", "evidence/outside"]) {
    const reply = await api.get(`/api/artifact-content?path=${encodeURIComponent(unsafe)}`);
    expect(reply.status).toBe(403);
  }
});

test("E13 the object view is read-only, stable through restart, and rejects unknown continuation scopes", async () => {
  const before = await api.ok<import("../../src/shared/types.ts").WorkObjectsResponse>(
    "GET",
    "/api/work-objects",
  );
  expect(before.applications.some((item) => item.kind === "process")).toBe(true);
  const invalid = await api.post("/api/launches", {
    id: crypto.randomUUID(),
    kind: "wake",
    method: "cli",
    agent: "demo",
    request: "Continue",
    workIds: ["run-missing"],
  });
  expect((invalid.body as Failure).error.code).toBe("invalid-request");
  const design = await api.post("/api/designs", {
    request: "Continue",
    method: "cli",
    references: [],
    workIds: ["run-missing"],
  });
  expect((design.body as Failure).error.code).toBe("invalid-request");
  await daemon.stop();
  daemon = await startDaemon(ws.root);
  api = apiClient(daemon);
  const after = await api.ok<import("../../src/shared/types.ts").WorkObjectsResponse>(
    "GET",
    "/api/work-objects",
  );
  expect(after.works.map((work) => work.id)).toEqual(before.works.map((work) => work.id));
  expect(after.participations).toEqual(before.participations);
});

test("E13 a continued plan carries source references without rewriting the request or authorizing execution", async () => {
  const graph = await api.ok<import("../../src/shared/types.ts").WorkObjectsResponse>(
    "GET",
    "/api/work-objects",
  );
  const workId = graph.works[0]!.id;
  const request = "Continue this work by planning the next confirmation.";
  const started = await api.ok<import("../../src/shared/types.ts").LaunchResponse>(
    "POST",
    "/api/launches",
    {
      id: crypto.randomUUID(),
      kind: "wake",
      method: "cli",
      agent: "claude-code",
      request,
      runs: "plan",
      workIds: [workId],
    },
  );
  expect(started.launch.request.request).toBe(request);
  const ended = await api.ok<RunDetailResponse>("GET", `/api/runs/${started.run!.id}?wait=30`);
  expect(ended.run.request).toBe(request);
  expect(ended.run.runs).toBe("plan");
  expect(ended.run.started ?? []).toEqual([]);
  expect(ended.run.execution?.workContext).toContain(workId);
  expect(ended.run.prompt).toContain("Continued work references");
  const next = await api.ok<import("../../src/shared/types.ts").WorkObjectsResponse>(
    "GET",
    "/api/work-objects",
  );
  expect(next.works).toHaveLength(graph.works.length);
  expect(next.participations.find((part) => part.source.id === ended.run.id)?.workIds).toEqual([
    workId,
  ]);
}, 60_000);
