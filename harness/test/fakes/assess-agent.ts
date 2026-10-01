#!/usr/bin/env bun
/*
 * A stand-in for the agent of an assessment run (E12); no model is called. Started as Claude Code
 * or Codex is, it reads the MCP server that the harness gives it (--mcp-config for Claude Code, the
 * `-c mcp_servers.<name>.<key>=<value>` overrides for Codex), starts that server on stdio with
 * @modelcontextprotocol/client, as the real agents do, and does what an assessing agent does: it
 * reads the records with get_assessment, list_runs, list_instances, and get_run, records what it
 * finds with record_assessment, and reports with finish_run for its own run (ALPS_RUN_ID). Last it
 * prints a final line as the agent would (stream-json, or codex --json), and exits.
 *
 * What it records rests on the newest process run that list_runs lists: a configuration item about
 * that run's Process, with the run, the first event of its log, its first output (when it has
 * one), and the Process's run success as evidence; a description item about the newest instance
 * that has an evaluation, with that evaluation as evidence (when there is one); and an unverified
 * item without evidence. With no process run, it records only the unverified item.
 *
 * ALPS_FAKE_SCENARIO picks what it does:
 *   ok    (the default) the calls above, then exit code 0
 *   slow  waits ALPS_FAKE_DELAY_MS (30 s by default) before it starts, so the run still runs
 * ALPS_FAKE_PROMPT names a file to write the prompt it received to. With ALPS_FAKE_TRY_RUN set, it
 * also calls instantiate, run, and wake, which the harness refuses for an assessment, and its
 * report says how each was answered.
 */

import { Client } from "@modelcontextprotocol/client";
import { StdioClientTransport } from "@modelcontextprotocol/client/stdio";
import fs from "node:fs";

interface Server {
  command: string;
  args: string[];
  env: Record<string, string>;
}

interface ListedRun {
  id: string;
  kind: string;
  instance: string | null;
  process: string | null;
  status: string;
}

interface InstanceListed {
  id: string;
  process: string;
  evaluation: unknown;
  evaluations?: unknown[];
}

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

/** The prompt, as each agent takes it: after -p (Claude Code) or as the last argument (Codex). */
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

/** How a call that the harness is to refuse was answered: `refused (<code>)` or `accepted`. */
async function attempt(
  client: Client,
  name: string,
  input: Record<string, unknown>,
): Promise<string> {
  const result = await client.callTool({ name, arguments: input }, { timeout: 80_000 });
  const body = result.structuredContent as { error?: { code?: string } };
  return result.isError ? `refused (${body.error?.code ?? "no code"})` : "accepted";
}

/** Reads the records, records what it finds, and returns its report. */
async function assess(client: Client): Promise<string> {
  const { assessment } = await call<{
    assessment: { findings: unknown[]; latest: { id: string } | null };
  }>(client, "get_assessment", {});
  const { runs } = await call<{ runs: ListedRun[] }>(client, "list_runs", { kind: "process" });
  const { instances } = await call<{ instances: InstanceListed[] }>(client, "list_instances", {});
  const items: Record<string, unknown>[] = [];
  const [newest] = runs;
  if (newest) {
    const { run } = await call<{
      run: { events: number; outputs: { path: string }[] };
    }>(client, "get_run", { run: newest.id });
    const evidence: Record<string, unknown>[] = [{ run: newest.id }];
    if (run.events > 0) evidence.push({ log: { run: newest.id, n: 1 } });
    const [output] = run.outputs;
    if (output) evidence.push({ path: output.path });
    if (newest.process)
      evidence.push({
        stat: { filter: { period: "all", process: newest.process }, metric: "runSuccess" },
      });
    items.push({
      kind: "configuration",
      subject: newest.process ? { process: newest.process } : {},
      statement: `Run ${newest.id} ${newest.status} with the demo agent, which writes placeholders: no agent did the work of its Process.`,
      evidence,
      limits: "The content of the outputs was not read.",
    });
  }
  const judged = instances.find((i) => i.evaluation !== null);
  if (judged)
    items.push({
      kind: "description",
      subject: { instance: judged.id, process: judged.process },
      statement: `The judgments of ${judged.id} changed ${judged.evaluations?.length ?? 0} time(s): the criteria of its Outcomes may be read in more than one way.`,
      evidence: [{ evaluation: judged.id }, { instance: judged.id }],
    });
  items.push({
    kind: "unverified",
    statement: "Whether the guidance is followed cannot be told from the records alone.",
  });
  const summary = [
    `Read the statistics and ${assessment.findings.length} check result(s), ${runs.length} process run(s), and ${instances.length} instance(s)${assessment.latest ? `, after assessment ${assessment.latest.id}` : ""}.`,
    "Did not read the content of the Artifacts.",
  ].join("\n\n");
  await call(client, "record_assessment", { summary, items });
  const tried = process.env.ALPS_FAKE_TRY_RUN
    ? [
        `instantiate ${await attempt(client, "instantiate", { process: "Requirements Clarification" })}`,
        `run ${await attempt(client, "run", { instance: instances[0]?.id ?? "i1", agent: "demo" })}`,
        `wake ${await attempt(client, "wake", { request: "Run it." })}`,
      ]
    : [];
  return tried.length > 0 ? `${summary}\n\nTried anyway: ${tried.join("; ")}.` : summary;
}

async function main(): Promise<number> {
  if (args.includes("--version")) {
    console.log("0.0.0 (fake assessment agent)");
    return 0;
  }
  const codex = args.includes("exec");
  const text = await prompt(codex);
  if (process.env.ALPS_FAKE_PROMPT) fs.writeFileSync(process.env.ALPS_FAKE_PROMPT, text);
  const server = codex ? codexServer() : claudeServer();
  if (!server) {
    console.error("fake assessment agent: no MCP server was given");
    return 3;
  }
  if (process.env.ALPS_FAKE_SCENARIO === "slow")
    await Bun.sleep(Number(process.env.ALPS_FAKE_DELAY_MS ?? 30_000));

  const own = process.env.ALPS_RUN_ID ?? "";
  const client = new Client({ name: "fake-assessment-agent", version: "0.0.0" });
  await client.connect(
    new StdioClientTransport({
      command: server.command,
      args: server.args,
      env: { ...(process.env as Record<string, string>), ...server.env },
      stderr: "inherit",
    }),
  );
  try {
    const report = await assess(client);
    await call(client, "finish_run", { run: own, report, status: "succeeded" });
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
        usage: { input_tokens: 900, cached_input_tokens: 0, output_tokens: 60 },
      }),
    );
  } else
    console.log(
      JSON.stringify({
        type: "result",
        subtype: "success",
        is_error: false,
        num_turns: 6,
        result: "Done.",
        total_cost_usd: 0.0091,
        usage: { input_tokens: 900, output_tokens: 60 },
      }),
    );
  return 0;
}

process.exitCode = await main();
