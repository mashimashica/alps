/*
 * E2 (MCP, data): over MCP, get_model returns the example model, and instantiate → run(demo) →
 * get_run(wait) succeeds with the outputs recorded in provenance (stage 3, when the MCP server
 * relays to the daemon; e2-http.test.ts runs the same scenario on the HTTP API).
 */

import { SUPPORTED_PROTOCOL_VERSIONS } from "@modelcontextprotocol/client";
import { afterAll, beforeAll, describe, expect, test } from "bun:test";
import pkg from "../../package.json" with { type: "json" };
import type {
  ArtifactsResponse,
  InstanceResponse,
  ModelDescription,
  RunDetailResponse,
  RunStartResponse,
} from "../../src/shared/types.ts";
import { stopWorkspaceDaemon } from "../helpers/daemon.ts";
import { callTool, mcpClient, type McpSession } from "../helpers/mcp.ts";
import { tmpWorkspace, type TmpWorkspace } from "../helpers/workspace.ts";

let ws: TmpWorkspace;
let session: McpSession;

beforeAll(async () => {
  ws = tmpWorkspace();
  session = await mcpClient({ workspace: ws.root });
});

afterAll(async () => {
  await session?.close();
  ws?.dispose();
});

/** The Skill path of each Process that has one, by Process name. */
const skillPaths = (model: ModelDescription): Record<string, string> =>
  Object.fromEntries(
    model.processes.flatMap((p) => (p.skill && "path" in p.skill ? [[p.name, p.skill.path]] : [])),
  );

describe("E2 MCP over stdio", () => {
  test("E2 mcp completes the handshake over stdio at the newest revision the client supports", () => {
    const { client } = session;
    // The client offers its newest revision (server/discover) and falls back to the 2025
    // initialize only if the server does not know it. Either way the version the server answers
    // with must be one the client accepts: a revision server/discover lists, which the client
    // chose from those it implements, or one of the client's 2025-era versions.
    const version = String(client.getNegotiatedProtocolVersion());
    const era = client.getProtocolEra();
    console.info(`E2 negotiated protocol version: ${version} (${era})`);
    if (era === "modern") {
      expect(client.getDiscoverResult()?.supportedVersions).toContain(version);
    } else {
      expect(era).toBe("legacy");
      expect(SUPPORTED_PROTOCOL_VERSIONS).toContain(version);
    }
    expect(client.getServerVersion()).toMatchObject({
      name: "alps-harness",
      version: pkg.version,
    });
    expect(client.getServerCapabilities()?.tools).toBeDefined();
  });

  test("E2 get_model returns the example model", async () => {
    const { tools } = await session.client.listTools();
    expect(tools.map((tool) => tool.name)).toContain("get_model");

    const result = await session.client.callTool({ name: "get_model", arguments: {} });
    expect(result.isError).toBeFalsy();
    const { ok, model } = result.structuredContent as { ok: boolean; model: ModelDescription };
    expect(ok).toBe(true);
    expect(model.processes).toHaveLength(11);
    expect(model.artifacts).toHaveLength(15);
    expect(model.workspace).toBe(ws.root);
    expect(model.language).toBe("en");
    // The declared location wins; the other Skills are found by their headings.
    expect(skillPaths(model)).toEqual({
      "Requirements Clarification": "skills/clarify-requirements/SKILL.md",
      "Solution Design": "skills/design-solution/SKILL.md",
      "Service Change Assessment": "../assess-service-change/SKILL.md",
      "Production Release": "skills/release-to-production/SKILL.md",
    });
    // The text content carries the same result for clients that ignore structuredContent.
    const [first] = result.content as { type: string; text: string }[];
    expect(JSON.parse(first?.text ?? "null")).toEqual(result.structuredContent);
  });

  test("E2 get_model returns the Japanese example model, whose Processes find the same Skills through the headings of their SKILL.ja.md", async () => {
    const ja = tmpWorkspace({ locale: "ja" });
    const jaSession = await mcpClient({ workspace: ja.root });
    try {
      const result = await jaSession.client.callTool({ name: "get_model", arguments: {} });
      expect(result.isError).toBeFalsy();
      const { ok, model } = result.structuredContent as { ok: boolean; model: ModelDescription };
      expect(ok).toBe(true);
      expect(model.processes).toHaveLength(11);
      expect(model.artifacts).toHaveLength(15);
      expect(model.workspace).toBe(ja.root);
      expect(model.language).toBe("ja");
      // Neither the Skills' names nor their directories match the Japanese Process names; the
      // headings of the translations in references/locales/ja/SKILL.ja.md do.
      expect(skillPaths(model)).toEqual({
        要件の明確化: "../../../service-change/skills/clarify-requirements/SKILL.md",
        解決案の設計: "../../../service-change/skills/design-solution/SKILL.md",
        サービス変更の評価: "../../../assess-service-change/SKILL.md",
        本番リリース: "../../../service-change/skills/release-to-production/SKILL.md",
      });
      expect(model.processes.find((p) => p.name === "本番リリース")?.skill).toMatchObject({
        translations: [
          {
            lang: "ja",
            path: "../../../service-change/skills/release-to-production/references/locales/ja/SKILL.ja.md",
          },
        ],
      });
    } finally {
      await jaSession.close();
      ja.dispose();
    }
  });

  test.todo(
    "E2 instantiate → run(demo) → get_run(wait) succeeds and the outputs are recorded in provenance",
    async () => {
      // The MCP server relays to the workspace's daemon, which it starts when there is none.
      const work = tmpWorkspace();
      const relay = await mcpClient({ workspace: work.root });
      try {
        const output = "docs/changes/CHG-002/change-brief.md";
        const { instance } = await callTool<InstanceResponse>(relay, "instantiate", {
          process: "Requirements Clarification",
          inputs: { "Stakeholder information": ["docs/changes/CHG-002/stakeholders.md"] },
          outputs: { "Change brief": output },
        });
        const { run } = await callTool<RunStartResponse>(relay, "run", {
          instance: instance.id,
          agent: "demo",
        });
        expect(run.status).toBe("running");
        const detail = await callTool<RunDetailResponse>(relay, "get_run", {
          run: run.id,
          wait: 30,
        });
        expect(detail.run.status).toBe("succeeded");
        expect(detail.run.outputs).toEqual([
          { type: "Change brief", path: output, change: "created" },
        ]);
        const { artifacts } = await callTool<ArtifactsResponse>(relay, "list_artifacts", {
          type: "Change brief",
        });
        expect(artifacts.find((artifact) => artifact.path === output)?.producedBy).toBe(run.id);
      } finally {
        await relay.close();
        await stopWorkspaceDaemon(work.root);
        work.dispose();
      }
    },
    { timeout: 60_000 },
  );
});
