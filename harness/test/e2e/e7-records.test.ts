/*
 * E7 (data): a state.json without schemaVersion (harness 0.8) is converted when it is read: its
 * work items become instances and the case is gone. The old runs stay readable, and the original
 * file is kept beside the converted one.
 */

import { afterAll, describe, expect, test } from "bun:test";
import fs from "node:fs";
import path from "node:path";
import type {
  InstanceResponse,
  InstancesResponse,
  RunDetailResponse,
  StateFile,
  StateFileV1,
} from "../../src/shared/types.ts";
import { apiClient } from "../helpers/api.ts";
import { copyOf } from "../helpers/copy.ts";
import { killStrayDaemons, startDaemon } from "../helpers/daemon.ts";
import { FIXTURES, records } from "../helpers/paths.ts";
import { tmpWorkspace, type TmpWorkspace } from "../helpers/workspace.ts";

const workspaces: TmpWorkspace[] = [];

afterAll(() => {
  killStrayDaemons();
  for (const ws of workspaces) ws.dispose();
});

const readJson = <T>(file: string): T => JSON.parse(fs.readFileSync(file, "utf8")) as T;

describe("E7 records", () => {
  test(
    "E7 an unversioned state.json is converted when read: work items become instances and the case is gone",
    async () => {
      // The fixture's Processes have the names of the Japanese model (harness 0.8's example).
      const ws = tmpWorkspace({ locale: "ja" });
      workspaces.push(ws);
      const original = fs.readFileSync(path.join(FIXTURES, "state-v1.json"), "utf8");
      const v1 = JSON.parse(original) as StateFileV1;
      fs.mkdirSync(records(ws.root, "runs"), { recursive: true });
      fs.writeFileSync(records(ws.root, "state.json"), original);
      fs.copyFileSync(
        path.join(FIXTURES, "runs-v1", "r5.jsonl"),
        records(ws.root, "runs", "r5.jsonl"),
      );

      let daemon = await startDaemon(ws.root);
      try {
        const api = apiClient(daemon);
        const { instances } = await api.ok<InstancesResponse>("GET", "/api/instances");
        expect(instances.map((instance) => instance.id)).toEqual(["i6", "i4", "i1"]);
        const byId = Object.fromEntries(instances.map((instance) => [instance.id, instance]));

        // Inputs come from the last run's inputs, outputs from its concrete targets, and the review
        // becomes an evaluation by a user whose judgments have no evidence.
        expect(copyOf(byId.i1)).toMatchObject({
          process: "変更の実装",
          inputs: { 設計記述: ["docs/changes/CHG-001/design"] },
          outputs: { 候補版: null },
          criteria: [],
          notes: "",
          runs: ["r2", "r3"],
          evaluation: {
            runId: "r2",
            judgments: [
              { outcome: 0, judgment: "unverified", evidence: "" },
              { outcome: 1, judgment: "unverified", evidence: "" },
            ],
            by: { kind: "user" },
            at: v1.workItems.w1?.review?.at,
          },
          facts: { latestRun: { id: "r3", status: "succeeded" }, evaluatedRun: "r2" },
        });
        expect(copyOf(byId.i4)).toMatchObject({
          process: "解決案の設計",
          inputs: { 変更概要: ["docs/changes/CHG-001/change-summary.md"] },
          outputs: { 設計記述: "docs/changes/CHG-001/design/" },
          runs: ["r5"],
          evaluation: {
            runId: "r5",
            judgments: [
              { outcome: 0, judgment: "achieved", evidence: "" },
              { outcome: 1, judgment: "achieved", evidence: "" },
            ],
            by: { kind: "user" },
          },
        });
        // A work item that never ran becomes an instance without inputs; its case and planned dates are gone.
        expect(copyOf(byId.i6)).toMatchObject({
          process: "要件の明確化",
          inputs: {},
          outputs: {},
          runs: [],
          evaluation: null,
        });
        for (const instance of instances)
          for (const key of ["case", "plannedStart", "plannedEnd", "agent", "createdAt", "review"])
            expect(instance, `${instance.id}.${key}`).not.toHaveProperty(key);

        // Runs keep their ids and stay readable, with their old events: workItem is now instance,
        // summary is now report, and the case is gone.
        const r5 = await api.ok<RunDetailResponse>("GET", "/api/runs/r5?tail=3");
        expect(copyOf(r5.run)).toMatchObject({
          id: "r5",
          kind: "process",
          instance: "i4",
          process: "解決案の設計",
          agent: "demo",
          status: "succeeded",
          report: v1.runs.r5?.summary,
          outputs: [{ type: "設計記述", path: "docs/changes/CHG-001/design", change: "modified" }],
          inputs: [
            {
              type: "変更概要",
              role: "input",
              paths: ["docs/changes/CHG-001/change-summary.md"],
              missing: [],
            },
          ],
          client: null,
        });
        for (const key of ["case", "workItem", "summary"]) expect(r5.run).not.toHaveProperty(key);
        expect(r5.events.map((event) => event.n)).toEqual([5, 6, 7]);
        expect(r5.truncated).toBe(true);

        // On disk: state.json is version 2 without work items, each run has its record, and the
        // original is kept as state.v1.json.
        const state = readJson<StateFile>(records(ws.root, "state.json"));
        expect(state.schemaVersion).toBe(2);
        expect(state).not.toHaveProperty("workItems");
        expect(state.provenance).toEqual(v1.provenance);
        expect(state.lastWakeAt).toBeNull();
        expect(Object.keys(state.runs).sort()).toEqual(["r2", "r3", "r5"]);
        expect(state.runs.r2).toEqual({
          id: "r2",
          kind: "process",
          instance: "i1",
          status: "succeeded",
          startedAt: v1.runs.r2!.startedAt,
          endedAt: v1.runs.r2!.endedAt,
        });
        for (const id of ["r2", "r3", "r5"])
          expect(readJson<{ prompt: string }>(records(ws.root, "runs", `${id}.json`)).prompt).toBe(
            v1.runs[id]?.prompt ?? "",
          );
        expect(JSON.stringify(state)).not.toContain('"case"');
        expect(fs.readFileSync(records(ws.root, "state.v1.json"), "utf8")).toBe(original);

        // New ids continue the sequence.
        const created = await api.ok<InstanceResponse>("POST", "/api/instances", {
          process: "要件の明確化",
        });
        expect(created.instance.id).toBe("i7");
      } finally {
        await daemon.stop();
      }

      // The next server reads version 2 as it is: nothing is converted twice.
      daemon = await startDaemon(ws.root);
      try {
        const { instances } = await apiClient(daemon).ok<InstancesResponse>(
          "GET",
          "/api/instances",
        );
        expect(instances.map((instance) => instance.id)).toEqual(["i7", "i6", "i4", "i1"]);
        expect(
          fs.readdirSync(records(ws.root)).filter((name) => name.startsWith("state.v1")),
        ).toEqual(["state.v1.json"]);
      } finally {
        await daemon.stop();
      }
    },
    { timeout: 60_000 },
  );
});
