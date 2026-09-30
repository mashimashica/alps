#!/usr/bin/env bun
/*
 * A stand-in for the agent that a wake starts (E6); no model is called. Started as Claude Code or
 * Codex is, it reads the MCP server that the harness gives it: the file (or JSON) of --mcp-config
 * for Claude Code, the `-c mcp_servers.<name>.<key>=<value>` overrides for Codex (TOML values;
 * the harness writes JSON strings and arrays of strings, which are TOML too). It starts that
 * server on stdio with @modelcontextprotocol/client, as the real agents do, and does what a woken
 * agent does: get_model, instantiate, run (demo), get_run (wait), and finish_run for its own wake
 * run (ALPS_RUN_ID). Last it prints a final line as the agent would (stream-json, or codex --json)
 * with a message other than its report, and exits.
 *
 * ALPS_FAKE_SCENARIO picks what it does:
 *   ok    (the default) the calls above, then exit code 0
 *   slow  waits 30 s before it starts, so that the wake still runs
 * ALPS_FAKE_PROMPT names a file to write the prompt it received to.
 */

import { Client } from "@modelcontextprotocol/client";
import { StdioClientTransport } from "@modelcontextprotocol/client/stdio";
import fs from "node:fs";

interface Server {
  command: string;
  args: string[];
  env: Record<string, string>;
}

/** The instance that the fake starts: the one E2 runs with the demo agent. */
const WAKE_INSTANCE = {
  process: "Requirements Clarification",
  inputs: { "Stakeholder information": ["docs/changes/CHG-002/stakeholders.md"] },
  outputs: { "Change brief": "docs/changes/CHG-002/change-brief.md" },
};

/** What the fake reports with finish_run; its final output line says something else. */
const WAKE_REPORT = "Read the model and the guidance; started one run with the demo agent.";

const args = process.argv.slice(2);

/** Claude Code: `--mcp-config <file or JSON>`. */
function claudeServer(): Server | null {
  const at = args.indexOf("--mcp-config");
  if (at < 0) return null;
  const value = args[at + 1] ?? "";
  const text = value.trimStart().startsWith("{") ? value : fs.readFileSync(value, "utf8");
  const config = JSON.parse(text) as { mcpServers?: Record<string, Partial<Server>> };
  const [server] = Object.values(config.mcpServers ?? {});
  if (!server?.command) return null;
  return { command: server.command, args: server.args ?? [], env: server.env ?? {} };
}

/** Codex: `-c mcp_servers.<name>.command=…`, `….args=[…]`, `….env.<NAME>=…`. */
function codexServer(): Server | null {
  const server: Server = { command: "", args: [], env: {} };
  for (let i = 0; i < args.length; i++) {
    if (args[i] !== "-c") continue;
    const match = /^mcp_servers\.[^.=]+\.([^=]+)=(.*)$/s.exec(args[i + 1] ?? "");
    if (!match) continue;
    const [, key = "", raw = ""] = match;
    const value = JSON.parse(raw) as unknown;
    if (key === "command") server.command = String(value);
    else if (key === "args") server.args = (value as unknown[]).map(String);
    else if (key.startsWith("env.")) server.env[key.slice(4)] = String(value);
  }
  return server.command ? server : null;
}

/** The prompt, as each agent takes it: after -p (Claude Code) or as the positional argument (Codex), or on stdin. */
async function prompt(codex: boolean): Promise<string> {
  const readStdin = async (): Promise<string> => {
    const chunks: Buffer[] = [];
    for await (const chunk of process.stdin) chunks.push(Buffer.from(chunk as Buffer));
    return Buffer.concat(chunks).toString("utf8");
  };
  if (!codex) {
    const given = args[args.indexOf("-p") + 1];
    return given !== undefined && !given.startsWith("--") ? given : readStdin();
  }
  const positional = args.filter(
    (arg, i) =>
      arg !== "exec" && !arg.startsWith("-") && args[i - 1] !== "-c" && args[i - 1] !== "--sandbox",
  );
  const last = positional.at(-1) ?? "-";
  return last === "-" ? readStdin() : last;
}

async function call<T>(client: Client, name: string, input: Record<string, unknown>): Promise<T> {
  const result = await client.callTool({ name, arguments: input }, { timeout: 80_000 });
  if (result.isError)
    throw new Error(`${name} failed: ${JSON.stringify(result.structuredContent)}`);
  return result.structuredContent as T;
}

async function main(): Promise<number> {
  if (args.includes("--version")) {
    console.log("0.0.0 (fake wake agent)");
    return 0;
  }
  const codex = args.includes("exec");
  const text = await prompt(codex);
  if (process.env.ALPS_FAKE_PROMPT) fs.writeFileSync(process.env.ALPS_FAKE_PROMPT, text);
  const server = codex ? codexServer() : claudeServer();
  if (!server) {
    console.error("fake wake agent: no MCP server was given");
    return 3;
  }
  if (process.env.ALPS_FAKE_SCENARIO === "slow") await Bun.sleep(30_000);

  const wake = process.env.ALPS_RUN_ID ?? "";
  const client = new Client({ name: "fake-wake-agent", version: "0.0.0" });
  await client.connect(
    new StdioClientTransport({
      command: server.command,
      args: server.args,
      env: { ...(process.env as Record<string, string>), ...server.env },
      stderr: "inherit",
    }),
  );
  try {
    await call(client, "get_model", {});
    const { instance } = await call<{ instance: { id: string } }>(
      client,
      "instantiate",
      WAKE_INSTANCE,
    );
    const { run } = await call<{ run: { id: string } }>(client, "run", {
      instance: instance.id,
      agent: "demo",
    });
    await call(client, "get_run", { run: run.id, wait: 30 });
    await call(client, "finish_run", { run: wake, report: WAKE_REPORT, status: "succeeded" });
  } finally {
    await client.close();
  }
  if (codex) {
    console.log(
      JSON.stringify({
        type: "item.completed",
        item: { id: "item_0", type: "agent_message", text: "Done." },
      }),
    );
    console.log(
      JSON.stringify({
        type: "turn.completed",
        usage: { input_tokens: 1200, cached_input_tokens: 0, output_tokens: 80 },
      }),
    );
  } else
    console.log(
      JSON.stringify({
        type: "result",
        subtype: "success",
        is_error: false,
        num_turns: 5,
        result: "Done.",
        total_cost_usd: 0.0123,
        usage: { input_tokens: 1200, output_tokens: 80 },
      }),
    );
  return 0;
}

process.exitCode = await main();
