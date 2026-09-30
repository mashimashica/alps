/*
 * E2 (MCP, data): over MCP, get_model returns the example model, and instantiate → run(demo) →
 * get_run(wait) succeeds with the outputs recorded in provenance. The MCP server relays to the
 * workspace's daemon, which it starts when there is none; e2-http.test.ts runs the same scenario
 * on the HTTP API. With it: the twelve tools and five resources, the failures that the MCP server
 * answers itself (no workspace, no server), and responses in the workspace's language.
 */

import { SUPPORTED_PROTOCOL_VERSIONS } from "@modelcontextprotocol/client";
import { afterAll, beforeAll, describe, expect, test } from "bun:test";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import pkg from "../../package.json" with { type: "json" };
import type {
  ArtifactsResponse,
  AssessmentMarkdownResponse,
  InstanceResponse,
  ModelDescription,
  RunDetailResponse,
  RunStartResponse,
  WakeResponse,
} from "../../src/shared/types.ts";
import { copyOf } from "../helpers/copy.ts";
import { readServerInfo, stopWorkspaceDaemon } from "../helpers/daemon.ts";
import { callTool, mcpClient, toolFailure, type McpSession } from "../helpers/mcp.ts";
import { FAKES, records } from "../helpers/paths.ts";
import { HOOK_TIMEOUT_MS } from "../helpers/process.ts";
import { tmpWorkspace, type TmpWorkspace } from "../helpers/workspace.ts";

const TOOLS = [
  "get_model",
  "list_artifacts",
  "list_instances",
  "instantiate",
  "run",
  "get_run",
  "cancel_run",
  "finish_run",
  "evaluate",
  "get_assessment",
  "wake",
  "open_ui",
];

let ws: TmpWorkspace;
let session: McpSession;
const others: TmpWorkspace[] = [];
const dirs: string[] = [];

beforeAll(async () => {
  ws = tmpWorkspace();
  session = await mcpClient({ workspace: ws.root });
}, HOOK_TIMEOUT_MS);

afterAll(async () => {
  await session?.close();
  for (const workspace of [ws, ...others]) if (workspace) await stopWorkspaceDaemon(workspace.root);
  for (const workspace of [ws, ...others]) workspace?.dispose();
  for (const dir of dirs) fs.rmSync(dir, { recursive: true, force: true });
}, HOOK_TIMEOUT_MS);

/** The Skill path of each Process that has one, by Process name. */
const skillPaths = (model: ModelDescription): Record<string, string> =>
  Object.fromEntries(
    model.processes.flatMap((p) => (p.skill && "path" in p.skill ? [[p.name, p.skill.path]] : [])),
  );

/** The text blocks of a tool result: the JSON, then the sentence in the workspace's language. */
const texts = (result: { content?: unknown }): string[] =>
  ((result.content ?? []) as { type: string; text?: string }[]).map((part) => part.text ?? "");

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
    expect(client.getServerCapabilities()?.resources).toBeDefined();
  });

  test("E2 the MCP server lists the twelve tools, each with a description of its results", async () => {
    const { tools } = await session.client.listTools();
    expect(tools.map((tool) => tool.name).sort()).toEqual([...TOOLS].sort());
    for (const tool of tools) {
      // Success, failure, and incomplete results are told apart in every description.
      expect(tool.description, tool.name).toContain("ok: true");
      expect(tool.description, tool.name).toContain("error.code");
    }
    const described = Object.fromEntries(tools.map((tool) => [tool.name, tool.description ?? ""]));
    expect(described.run).toContain("Success means only that the run started");
    expect(described.evaluate).toContain("cannot be empty");
    for (const name of ["instantiate", "run", "finish_run"])
      expect(described[name], name).toMatch(/look with (get_run|list_instances)/);
    expect(described.list_artifacts).toContain("truncated");
  });

  test("E2 get_model returns the example model, answered by the daemon", async () => {
    const result = await session.client.callTool({ name: "get_model", arguments: {} });
    expect(result.isError).toBeFalsy();
    const { ok, model } = result.structuredContent as {
      ok: boolean;
      model: ModelDescription & { agents: { id: string }[] };
    };
    expect(ok).toBe(true);
    expect(model.processes).toHaveLength(11);
    expect(model.artifacts).toHaveLength(15);
    expect(model.workspace).toBe(ws.root);
    expect(model.language).toBe("en");
    // Only the daemon checks the agents; the MCP server started it, as server.json says.
    expect(model.agents.map((agent) => agent.id)).toEqual(["claude-code", "codex", "demo", "self"]);
    expect(readServerInfo(ws.root)?.pid).toEqual(expect.any(Number));
    // The declared location wins; the other Skills are found by their headings.
    expect(skillPaths(model)).toEqual({
      "Requirements Clarification": "skills/clarify-requirements/SKILL.md",
      "Solution Design": "skills/design-solution/SKILL.md",
      "Service Change Assessment": "../assess-service-change/SKILL.md",
      "Production Release": "skills/release-to-production/SKILL.md",
    });
    // The first text block carries the same result for clients that ignore structuredContent;
    // the second says what happened, in the workspace's language (English here).
    const [json, said] = texts(result);
    expect(JSON.parse(json ?? "null")).toEqual(result.structuredContent);
    expect(said).toContain("has 11 Processes and 15 Artifact types");
  });

  test("E2 get_model returns the Japanese example model, whose Processes find the same Skills through the headings of their SKILL.ja.md, and says so in Japanese", async () => {
    const ja = tmpWorkspace({ locale: "ja" });
    others.push(ja);
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
      // The MCP server's responses follow `language: ja`, successes and failures alike.
      expect(texts(result)[1]).toContain("11 のプロセスと 15 のアーティファクトの型がある");
      const missing = await toolFailure(jaSession, "get_run", { run: "r999" });
      expect(missing.error.code).toBe("not-found");
      expect(missing.error.message).toBe("実行 r999 はない。");
      expect(missing.texts[1]).toBe("実行 r999 はない。");
    } finally {
      await jaSession.close();
    }
  });

  test(
    "E2 instantiate → run(demo) → get_run(wait) succeeds and the outputs are recorded in provenance",
    async () => {
      const output = "docs/changes/CHG-002/change-brief.md";
      const { instance } = await callTool<InstanceResponse>(session, "instantiate", {
        process: "Requirements Clarification",
        inputs: { "Stakeholder information": ["docs/changes/CHG-002/stakeholders.md"] },
        outputs: { "Change brief": output },
      });
      const started = await session.client.callTool({
        name: "run",
        arguments: { instance: instance.id, agent: "demo" },
      });
      const { run } = started.structuredContent as RunStartResponse;
      expect(run.status).toBe("running");
      // Starting is all that the success of run means.
      expect(texts(started)[1]).toContain("starting achieves no Outcome");
      const detail = await callTool<RunDetailResponse>(session, "get_run", {
        run: run.id,
        wait: 30,
      });
      expect(detail.run.status).toBe("succeeded");
      expect(detail.run.outputs).toEqual([
        { type: "Change brief", path: output, change: "created" },
      ]);
      const { artifacts } = await callTool<ArtifactsResponse>(session, "list_artifacts", {
        type: "Change brief",
      });
      expect(artifacts.find((artifact) => artifact.path === output)?.producedBy).toBe(run.id);
    },
    { timeout: 60_000 },
  );

  test(
    "E2 the five resources read the model, a Process, an instance, a run's log, and the assessment, with ttlMs and cacheScope",
    async () => {
      const { instance } = await callTool<InstanceResponse>(session, "instantiate", {
        process: "Solution Design",
        inputs: { "Change brief": ["docs/changes/CHG-001/change-brief.md"] },
      });
      const { run } = await callTool<RunStartResponse>(session, "run", {
        instance: instance.id,
        agent: "demo",
      });
      await callTool<RunDetailResponse>(session, "get_run", { run: run.id, wait: 30 });

      const { resources } = await session.client.listResources();
      const uris = resources.map((resource) => resource.uri);
      expect(uris).toContain("alps://model");
      expect(uris).toContain("alps://assessment");
      expect(uris).toContain(`alps://process/${encodeURIComponent("Solution Design")}`);
      expect(uris).toContain(`alps://instance/${instance.id}`);
      expect(uris).toContain(`alps://run/${run.id}/log`);
      const { resourceTemplates } = await session.client.listResourceTemplates();
      expect(resourceTemplates.map((template) => template.uriTemplate).sort()).toEqual([
        "alps://instance/{id}",
        "alps://process/{id}",
        "alps://run/{id}/log",
      ]);

      const read = async (uri: string) => {
        const result = (await session.client.readResource({ uri })) as {
          contents: { uri: string; mimeType?: string; text?: string }[];
          ttlMs?: number;
          cacheScope?: string;
        };
        return { ...result, text: result.contents[0]?.text ?? "" };
      };
      const model = await read("alps://model");
      expect((JSON.parse(model.text) as ModelDescription).processes).toHaveLength(11);
      const process = await read(`alps://process/${encodeURIComponent("Solution Design")}`);
      expect(JSON.parse(process.text)).toMatchObject({
        process: {
          name: "Solution Design",
          skill: { path: "skills/design-solution/SKILL.md" },
        },
        artifacts: [{ name: "Change brief" }, { name: "Design description" }],
      });
      const one = await read(`alps://instance/${instance.id}`);
      expect(JSON.parse(one.text)).toMatchObject({ id: instance.id, runs: [run.id] });
      const log = await read(`alps://run/${run.id}/log`);
      expect(log.contents[0]?.mimeType).toBe("text/plain");
      expect(log.text).toContain(`Log of run ${run.id} (demo, succeeded)`);
      expect(log.text).toMatch(/\] \S+ end\s+Succeeded/);
      const assessment = await read("alps://assessment");
      expect(assessment.contents[0]?.mimeType).toBe("text/markdown");
      expect(assessment.text).toContain("## Findings");
      expect(assessment.text).toContain(
        `| ${instance.id} | Solution Design | ${run.id} (succeeded) |`,
      );
      // get_assessment answers the same Markdown.
      const markdown = await callTool<AssessmentMarkdownResponse>(session, "get_assessment", {
        format: "markdown",
      });
      expect(markdown.markdown).toBe(assessment.text);

      // Records change with every run: nothing is cached, and nothing is shared. An ended run's
      // log no longer changes and may be kept for an hour.
      if (session.client.getProtocolEra() === "modern") {
        for (const result of [model, process, one, assessment])
          expect(copyOf({ ttlMs: result.ttlMs, cacheScope: result.cacheScope })).toEqual({
            ttlMs: 0,
            cacheScope: "private",
          });
        expect(copyOf({ ttlMs: log.ttlMs, cacheScope: log.cacheScope })).toEqual({
          ttlMs: 3_600_000,
          cacheScope: "private",
        });
      }

      // A resource that does not exist is an MCP error, not an empty resource.
      await expect(session.client.readResource({ uri: "alps://instance/i999" })).rejects.toThrow();
    },
    { timeout: 60_000 },
  );

  test(
    "E2 wake relays to the harness server, which starts a wake run: no instance, an agent given its MCP server",
    async () => {
      // The shared workspace has no Claude Code; this one has the fake, which ends as it does
      // for a Process (E6 has the fake that uses the MCP server it is given).
      const woken = tmpWorkspace({
        agents: { "claude-code": { command: path.join(FAKES, "claude.ts") } },
      });
      others.push(woken);
      const relay = await mcpClient({ workspace: woken.root });
      try {
        const result = await relay.client.callTool({ name: "wake", arguments: {} });
        expect(result.isError).toBeFalsy();
        const { run, skipped } = result.structuredContent as WakeResponse;
        expect(skipped).toBe(false);
        expect(copyOf(run)).toMatchObject({
          kind: "wake",
          instance: null,
          process: null,
          agent: "claude-code",
          status: "running",
        });
        expect(run?.command).toContain("--mcp-config");
        expect(texts(result)[1]).toContain(`Started wake run ${run?.id} (claude-code)`);
        const ended = await callTool<RunDetailResponse>(relay, "get_run", {
          run: run?.id,
          wait: 30,
        });
        expect(ended.run.status).toBe("succeeded");
        expect(ended.run.started).toEqual([]);
      } finally {
        await relay.close();
      }
      // Here claude-code cannot be started, and the demo is no agent that can be woken.
      const unavailable = await toolFailure(session, "wake", {});
      expect(unavailable.error.code).toBe("agent-unavailable");
      const demo = await toolFailure(session, "wake", { agent: "demo" });
      expect(demo.error.code).toBe("agent-unavailable");
      expect(demo.error.message).toContain("Demo cannot be woken");
    },
    { timeout: 60_000 },
  );

  test("E2 without a workspace, the tools answer no-model and say where to put the files", async () => {
    const empty = fs.mkdtempSync(path.join(os.tmpdir(), "alps-harness-e2-empty-"));
    dirs.push(empty);
    const lost = await mcpClient({ workspace: empty });
    try {
      for (const name of ["get_model", "list_instances"]) {
        const { error } = await toolFailure(lost, name);
        expect(error.code, name).toBe("no-model");
        expect(error.files, name).toEqual([
          path.join(empty, "alps-harness.yaml"),
          path.join(empty, "process-model.yaml"),
        ]);
        // The server may have started outside the project (in a Plugin's root): the message says
        // how to give it the project's directory.
        expect(error.message, name).toContain("ALPS_WORKSPACE");
      }
      // No daemon was started for a directory that is not a workspace.
      expect(fs.existsSync(records(empty))).toBe(false);
    } finally {
      await lost.close();
    }
  });

  test(
    "E2 when the harness server cannot start, the tools answer server-unreachable with the port and server.json",
    async () => {
      const broken = tmpWorkspace();
      others.push(broken);
      fs.mkdirSync(records(broken.root), { recursive: true });
      fs.writeFileSync(records(broken.root, "state.json"), "{ not json");
      const relay = await mcpClient({ workspace: broken.root });
      try {
        const { error } = await toolFailure(relay, "get_model");
        expect(error.code).toBe("server-unreachable");
        expect(error.message).toContain(records(broken.root, "server.json"));
        expect(error.message).toContain("port 0");
        expect(error.message).toContain("not valid JSON");
        expect(error.files).toEqual([
          records(broken.root, "server.json"),
          records(broken.root, "server.log"),
        ]);
      } finally {
        await relay.close();
      }
    },
    { timeout: 60_000 },
  );
});
