/*
 * A stand-in for Claude Code and Codex in the E2E tests; no model is called. It answers
 * --version, takes the prompt from its arguments or standard input as the real agent does, prints
 * the output lines of test/fixtures/agents/<agent>-<ok|fail>.jsonl, and writes a file at each
 * output location that the prompt names. The lines were recorded from the real agents (stage 7,
 * 2026-09-30), with this machine's paths, ids, and file contents made placeholders:
 *   codex-ok     `codex exec --json` (codex-cli 0.158.0) running Requirements Clarification
 *   codex-fail   the same with a model the API refuses
 *   claude-fail  `claude -p --output-format stream-json --verbose` (Claude Code 2.1.96), not
 *                logged in
 *   claude-ok    the same, logged in, running Requirements Clarification (stage 7b): every line
 *                of the run in its order, its texts neutral sentences, and the tools, MCP servers,
 *                Skills, and commands of the user's account and Plugins left out of its first line
 * The warnings that Codex printed about the user's own config.toml are left out, and so is what
 * the real agents print on standard error (Codex: "Reading additional input from stdin...").
 *
 * ALPS_FAKE_SCENARIO picks what it does:
 *   ok    (the default) the work, then exit code 0
 *   fail  the agent reports a failure; exit code 1
 *   slow  ok, with a pause between lines (ALPS_FAKE_DELAY_MS, 1000 ms by default)
 *   hang  prints its first line, starts a child process, writes its own pid and the child's to
 *         the file ALPS_FAKE_PIDS names (one per line), ignores SIGTERM, and waits to be killed
 *   exit  prints nothing and exits with code 3, so only the harness can say why the run failed
 * ALPS_FAKE_PROMPT names a file to write the prompt it received to. ALPS_FAKE_ENV_DUMP names a
 * file to which each start, --version included, adds a line of JSON: `start` (version or run),
 * the `names` of the variables in its environment, and the `values` of those named ALPS_* (the
 * tests' own; the others may hold the user's credentials).
 */

import { fakeModels } from "./models.ts";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

export type FakeAgent = "claude" | "codex";

const FIXTURES = fileURLToPath(new URL("../fixtures/agents/", import.meta.url));

const VERSIONS: Record<FakeAgent, string> = {
  claude: "2.1.999 (Claude Code)",
  codex: "codex-cli 0.999.0",
};

/** Writes a file whole: aside, then renamed, so a reader never sees half of it. */
function writeWhole(file: string, text: string): void {
  const aside = `${file}.${process.pid}.tmp`;
  fs.writeFileSync(aside, text);
  fs.renameSync(aside, file);
}

/** Adds this start's environment to the file ALPS_FAKE_ENV_DUMP names: the names, and the ALPS_* values. */
function dumpEnv(start: "version" | "run"): void {
  const file = process.env.ALPS_FAKE_ENV_DUMP;
  if (!file) return;
  const names = Object.keys(process.env).sort();
  const values = Object.fromEntries(
    names.filter((name) => name.startsWith("ALPS_")).map((name) => [name, process.env[name]]),
  );
  fs.appendFileSync(file, `${JSON.stringify({ start, names, values })}\n`);
}

async function readStdin(): Promise<string> {
  const chunks: Buffer[] = [];
  for await (const chunk of process.stdin) chunks.push(Buffer.from(chunk as Buffer));
  return Buffer.concat(chunks).toString("utf8");
}

/** The prompt and how the output is asked for, from the arguments as each agent reads them. */
async function invocation(
  agent: FakeAgent,
  args: string[],
): Promise<{ prompt: string; format: "stream" | "json" | "text" }> {
  if (agent === "claude") {
    const at = args.indexOf("-p");
    const given = at >= 0 ? args[at + 1] : undefined;
    const prompt = given !== undefined && !given.startsWith("--") ? given : await readStdin();
    const format = args[args.indexOf("--output-format") + 1];
    return {
      prompt,
      format: format === "stream-json" ? "stream" : format === "json" ? "json" : "text",
    };
  }
  const last = args.at(-1) ?? "";
  return {
    prompt: last === "-" ? await readStdin() : last,
    format: args.includes("--json") ? "stream" : "text",
  };
}

interface PromptFacts {
  skill: string;
  input: string;
  outputs: { name: string; path: string }[];
}

/** The entries (`- name: value`) of the prompt's section whose heading matches. */
function section(lines: string[], heading: RegExp): { name: string; value: string }[] {
  const start = lines.findIndex((line) => heading.test(line));
  if (start < 0) return [];
  const entries: { name: string; value: string }[] = [];
  for (let i = start + 1; i < lines.length && lines[i]?.startsWith("- "); i++) {
    const entry = (lines[i] ?? "").slice(2);
    const colon = entry.indexOf(": ");
    if (colon > 0) entries.push({ name: entry.slice(0, colon), value: entry.slice(colon + 2) });
  }
  return entries;
}

/** A location as the prompt gives it, made concrete: a path, or a pattern whose wildcards are filled. */
function concrete(value: string): string | null {
  const pattern = /[(（]([^()（）\s]+)[)）]/.exec(value)?.[1];
  const location = pattern ?? value.trim();
  if (/\s/.test(location) || !/[./]/.test(location)) return null;
  return location.replace(/\*\*\//g, "").replace(/\*+/g, "fake");
}

/** What the fake needs from the prompt: the Skill, the first input, and the output locations. */
function readPrompt(prompt: string): PromptFacts {
  const lines = prompt.split("\n");
  const skill =
    lines.map((line) => /^- (\S*SKILL\.md)\s*$/.exec(line)?.[1]).find(Boolean) ?? "(none)";
  const input =
    section(lines, /^(Inputs \(|入力（)/)
      .flatMap(({ value }) => value.split(", ").map((p) => p.replace(/\s.*$/, "")))
      .find((p) => /[./]/.test(p)) ?? "(none)";
  const outputs = section(lines, /^(Outputs \(|出力（)/).flatMap(({ name, value }) => {
    const location = concrete(value);
    if (!location) return [];
    return [{ name, path: location.endsWith("/") ? `${location}fake-agent.md` : location }];
  });
  return { skill, input, outputs };
}

/** Writes each output inside the working directory (the workspace the harness runs it in). */
function writeOutputs(agent: FakeAgent, facts: PromptFacts): void {
  const root = process.cwd();
  for (const output of facts.outputs) {
    const file = path.resolve(root, output.path);
    const relative = path.relative(root, file);
    if (relative.startsWith("..") || path.isAbsolute(relative)) continue;
    fs.mkdirSync(path.dirname(file), { recursive: true });
    fs.writeFileSync(
      file,
      `# ${output.name}\n\nWritten by the fake ${agent} for run ${process.env.ALPS_RUN_ID ?? "(unknown)"}.\n`,
    );
  }
}

/** The fixture's lines with their placeholders filled; `writes` marks the line that tells of the writing. */
function fixtureLines(
  agent: FakeAgent,
  outcome: "ok" | "fail",
  facts: PromptFacts,
): { text: string; writes: boolean }[] {
  const outputs = facts.outputs.map((output) => output.path);
  const report = `Outcome 0: the output was written from the input ${facts.input}. Unverified: whether the Outcomes are achieved (a fake agent judges nothing). Created or updated: ${outputs.join(", ") || "nothing"}.`;
  const values: Record<string, string> = {
    CWD: process.cwd(),
    SESSION: `fake-${process.pid}`,
    SKILL: facts.skill,
    INPUT: facts.input,
    OUTPUT: outputs[0] ?? "(none)",
    REPORT: report,
  };
  const fill = (value: unknown): unknown => {
    if (typeof value === "string")
      return value.replace(/\{\{(\w+)\}\}/g, (_, key: string) => values[key] ?? "");
    if (Array.isArray(value)) return value.map(fill);
    if (value && typeof value === "object")
      return Object.fromEntries(Object.entries(value).map(([key, entry]) => [key, fill(entry)]));
    return value;
  };
  return fs
    .readFileSync(path.join(FIXTURES, `${agent}-${outcome}.jsonl`), "utf8")
    .split("\n")
    .filter((line) => line.trim())
    .map((line) => ({
      text: JSON.stringify(fill(JSON.parse(line))),
      writes: line.includes("{{OUTPUT}}"),
    }));
}

const sleep = (ms: number): Promise<void> => new Promise((resolve) => setTimeout(resolve, ms));

export async function runFake(agent: FakeAgent): Promise<void> {
  const args = process.argv.slice(2);
  if (await fakeModels(args)) return;
  if (args.includes("--version")) {
    dumpEnv("version");
    console.log(VERSIONS[agent]);
    return;
  }
  dumpEnv("run");
  const { prompt, format } = await invocation(agent, args);
  if (process.env.ALPS_FAKE_PROMPT) writeWhole(process.env.ALPS_FAKE_PROMPT, prompt);
  const scenario = process.env.ALPS_FAKE_SCENARIO ?? "ok";
  if (scenario === "exit") {
    process.exitCode = 3;
    return;
  }
  const facts = readPrompt(prompt);
  const lines = fixtureLines(agent, scenario === "fail" ? "fail" : "ok", facts);

  if (scenario === "hang") {
    console.log(lines[0]?.text ?? "");
    // The child stays in this process group; only a signal to the group reaches it.
    const child = Bun.spawn(["sleep", "3600"], { stdio: ["ignore", "ignore", "ignore"] });
    process.on("SIGTERM", () => {});
    if (process.env.ALPS_FAKE_PIDS)
      writeWhole(process.env.ALPS_FAKE_PIDS, `${process.pid}\n${child.pid}\n`);
    setInterval(() => {}, 60_000);
    await new Promise(() => {});
  }

  const delay = Number(process.env.ALPS_FAKE_DELAY_MS ?? (scenario === "slow" ? 1000 : 10));
  let written = false;
  for (const line of lines) {
    if (line.writes && !written && scenario !== "fail") {
      writeOutputs(agent, facts);
      written = true;
    }
    if (format === "stream") console.log(line.text);
    await sleep(delay);
  }
  const last = JSON.parse(lines.at(-1)?.text ?? "{}") as { result?: string };
  if (format === "json") console.log(JSON.stringify(last));
  if (format === "text") console.log(last.result ?? "");
  process.exitCode = scenario === "fail" ? 1 : 0;
}
