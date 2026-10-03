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
 * A wake given a request (its record, read with get_run, has a request, attachments, Processes, or
 * runs: plan) is served as a tailoring agent would, without judging anything: the fake plans the
 * Processes that the request names (Requirements Clarification when it names none), instantiates
 * each with the attachments as the inputs of its first input type, a criterion taken from the
 * request, and its assumption in the notes, leaves the output locations to the run, starts each
 * with the demo agent and waits for it unless the request asks for a plan only, and reports what
 * it planned and why, its assumption, and what to confirm.
 *
 * ALPS_FAKE_SCENARIO picks what it does:
 *   ok    (the default) the calls above, then exit code 0
 *   slow  waits 30 s before it starts, so that the wake still runs
 * ALPS_FAKE_PROMPT names a file to write the prompt it received to. With ALPS_FAKE_TRY_RUN set, a
 * request for a plan only is disobeyed: the fake also calls run (demo) for the first instance it
 * made, and wake, and its report says how each was answered.
 */

import { fakeModels } from "./models.ts";
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

/** What the fake plans when a request names no Process. */
const DEFAULT_PROCESS = "Requirements Clarification";
/** The assumption that the fake writes in the notes of the instances it makes for a request. */
const REQUEST_ASSUMPTION = "Assumed that the attachments are the inputs of the first input type.";

/** The part of a wake run's record that says what the wake was asked. */
interface WakeRecord {
  id: string;
  request?: string | null;
  attachments?: string[];
  processes?: string[];
  runs?: "run" | "plan";
}

interface ModelProcess {
  id: string;
  name: string;
  inputs: string[];
  controls: string[];
}

const args = process.argv.slice(2);
if (await fakeModels(args)) process.exit(0);

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

/** How a call that may be refused was answered: `refused (<code>)`, `skipped`, or `started`. */
async function attempt(
  client: Client,
  name: string,
  input: Record<string, unknown>,
): Promise<string> {
  const result = await client.callTool({ name, arguments: input }, { timeout: 80_000 });
  const body = result.structuredContent as { skipped?: boolean; error?: { code?: string } };
  if (result.isError) return `refused (${body.error?.code ?? "no code"})`;
  return body.skipped ? "skipped" : "started";
}

/** Serves the request of wake run `wake`: plans, instantiates, runs unless asked for a plan only, and reports. */
async function serveRequest(
  client: Client,
  wake: string,
  asked: WakeRecord,
  processes: ModelProcess[],
): Promise<void> {
  const named = asked.processes ?? [];
  const planned = (named.length > 0 ? named : [DEFAULT_PROCESS]).map((key) => {
    const process = processes.find((p) => p.id === key || p.name === key);
    if (!process) throw new Error(`no Process ${key} in the model`);
    return process;
  });
  const attachments = asked.attachments ?? [];
  const firstLine = (asked.request ?? "").split("\n")[0]?.trim() || "the attachments";
  const made: { id: string; process: string }[] = [];
  for (const process of planned) {
    const type = process.inputs[0] ?? process.controls[0];
    const { instance } = await call<{ instance: { id: string } }>(client, "instantiate", {
      process: process.id,
      inputs: type && attachments.length > 0 ? { [type]: attachments } : {},
      criteria: [{ outcome: 0, statement: `For this request: ${firstLine}` }],
      notes: REQUEST_ASSUMPTION,
    });
    made.push({ id: instance.id, process: process.name });
  }
  const ran: string[] = [];
  if (asked.runs !== "plan")
    for (const instance of made) {
      const { run } = await call<{ run: { id: string } }>(client, "run", {
        instance: instance.id,
        agent: "demo",
      });
      const ended = await call<{ run: { id: string; status: string } }>(client, "get_run", {
        run: run.id,
        wait: 30,
      });
      ran.push(`${ended.run.id} (${ended.run.status})`);
    }
  // An agent that does not keep to a plan only tries the run and the wake it was not to start.
  const [first] = made;
  const tried =
    asked.runs === "plan" && process.env.ALPS_FAKE_TRY_RUN && first
      ? [
          `run ${await attempt(client, "run", { instance: first.id, agent: "demo" })}`,
          `wake ${await attempt(client, "wake", { request: "Run the plan." })}`,
        ]
      : [];
  const why = named.length > 0 ? "the request names it" : "it serves the request";
  const report = [
    `Planned ${made.map((m) => `${m.process} as ${m.id}`).join(", ")} because ${why}.`,
    asked.runs === "plan"
      ? "Started no run: the request asks for a plan only."
      : `Ran ${ran.join(", ")} with the demo agent.`,
    ...(tried.length > 0 ? [`Tried anyway: ${tried.join("; ")}.`] : []),
    `Assumption: ${REQUEST_ASSUMPTION}`,
    "To confirm: the criteria that were derived from the request.",
  ].join(" ");
  await call(client, "finish_run", { run: wake, report, status: "succeeded" });
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
    const { model } = await call<{ model: { processes: ModelProcess[] } }>(client, "get_model", {});
    const { run: self } = await call<{ run: WakeRecord }>(client, "get_run", { run: wake });
    const requested =
      Boolean(self.request) ||
      (self.attachments ?? []).length > 0 ||
      (self.processes ?? []).length > 0 ||
      self.runs === "plan";
    if (requested) await serveRequest(client, wake, self, model.processes);
    else {
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
    }
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
