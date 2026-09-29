/*
 * E4 (MCP, self): run(self) returns the prompt; after the calling session writes a file,
 * finish_run records the output change. When the MCP connection closes before finish_run, the
 * run is interrupted (stage 3).
 */

import { afterAll, describe, expect, test } from "bun:test";
import fs from "node:fs";
import path from "node:path";
import type {
  ArtifactsResponse,
  FinishResponse,
  InstanceResponse,
  RunDetailResponse,
  RunStartResponse,
} from "../../src/shared/types.ts";
import { copyOf } from "../helpers/copy.ts";
import { killStrayDaemons, stopWorkspaceDaemon } from "../helpers/daemon.ts";
import { callTool, mcpClient, type McpSession } from "../helpers/mcp.ts";
import { until } from "../helpers/process.ts";
import { tmpWorkspace, type TmpWorkspace } from "../helpers/workspace.ts";

const workspaces: TmpWorkspace[] = [];
const sessions: McpSession[] = [];

afterAll(async () => {
  for (const session of sessions) await session.close().catch(() => {});
  for (const ws of workspaces) await stopWorkspaceDaemon(ws.root).catch(() => {});
  killStrayDaemons();
  for (const ws of workspaces) ws.dispose();
});

const INPUT = "docs/changes/CHG-002/stakeholders.md";
const OUTPUT = "docs/changes/CHG-002/change-brief.md";

async function session(ws: TmpWorkspace): Promise<McpSession> {
  const mcp = await mcpClient({ workspace: ws.root });
  sessions.push(mcp);
  return mcp;
}

async function instantiate(mcp: McpSession): Promise<string> {
  const { instance } = await callTool<InstanceResponse>(mcp, "instantiate", {
    process: "Requirements Clarification",
    inputs: { "Stakeholder information": [INPUT] },
    outputs: { "Change brief": OUTPUT },
  });
  return instance.id;
}

describe("E4 self mode", () => {
  test.todo(
    "E4 run(self) returns the prompt, and finish_run after writing a file records the output change",
    async () => {
      const ws = tmpWorkspace();
      workspaces.push(ws);
      const mcp = await session(ws);
      const instance = await instantiate(mcp);

      const started = await callTool<RunStartResponse>(mcp, "run", { instance, agent: "self" });
      expect(copyOf(started.run)).toMatchObject({
        agent: "self",
        status: "running",
        command: null,
        client: { name: "alps-harness-e2e", version: expect.any(String) },
      });
      // The prompt points to the Skill and the paths; the session reads them with its own tools.
      expect(started.prompt).toContain("skills/clarify-requirements/SKILL.md");
      expect(started.prompt).toContain(INPUT);
      expect(started.prompt).toContain(OUTPUT);
      expect(started.prompt).toContain("finish_run");

      fs.mkdirSync(path.dirname(path.join(ws.root, OUTPUT)), { recursive: true });
      fs.writeFileSync(
        path.join(ws.root, OUTPUT),
        "# Change brief (CHG-002)\n\n## Acceptance conditions\n\n- The export finishes within 10 s.\n",
      );
      const report =
        "Outcome 0: one acceptance condition, observable by timing the export. Unverified: the third stakeholder.";
      const finished = await callTool<FinishResponse>(mcp, "finish_run", {
        run: started.run.id,
        report,
        status: "succeeded",
      });
      expect(finished.outputs).toEqual([{ type: "Change brief", path: OUTPUT, change: "created" }]);
      expect(copyOf(finished.run)).toMatchObject({ status: "succeeded", report });

      const { artifacts } = await callTool<ArtifactsResponse>(mcp, "list_artifacts", {
        type: "Change brief",
      });
      expect(artifacts.find((artifact) => artifact.path === OUTPUT)?.producedBy).toBe(
        started.run.id,
      );
    },
    { timeout: 60_000 },
  );

  test.todo(
    "E4 a self run whose MCP connection closes before finish_run is interrupted",
    async () => {
      const ws = tmpWorkspace();
      workspaces.push(ws);
      const first = await session(ws);
      const { run } = await callTool<RunStartResponse>(first, "run", {
        instance: await instantiate(first),
        agent: "self",
      });
      await first.close();

      // The daemon outlives the session that started it and notices that its connection closed.
      const second = await session(ws);
      await until(
        async () =>
          (await callTool<RunDetailResponse>(second, "get_run", { run: run.id })).run.status ===
          "interrupted",
        15_000,
        "the self run to be interrupted",
      );
    },
    { timeout: 60_000 },
  );
});
