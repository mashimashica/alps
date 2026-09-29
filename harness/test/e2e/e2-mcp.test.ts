/*
 * E2 (MCP, data): over MCP, get_model returns the example model, and instantiate → run(demo) →
 * get_run(wait) succeeds with the outputs recorded in provenance (stage 3).
 */

import { SUPPORTED_PROTOCOL_VERSIONS } from "@modelcontextprotocol/client";
import { afterAll, beforeAll, describe, expect, test } from "bun:test";
import pkg from "../../package.json" with { type: "json" };
import type { ModelDescription } from "../../src/shared/types.ts";
import { mcpClient, type McpSession } from "../helpers/mcp.ts";
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

  test.todo("E2 instantiate → run(demo) → get_run(wait) succeeds and the outputs are recorded in provenance", () => {});
});
