/* Metadata-only CLI handshakes: no user message, thread, or inference is started. */
import { envLeftOut, type AgentSpec } from "../agents/index.ts";
import { claudeModels, codexModels } from "../agents/models.ts";
import type { AgentModel } from "../shared/types.ts";
import { agentEnv } from "./agent-process.ts";

const TIMEOUT_MS = 25_000;
const MAX_OUTPUT_BYTES = 2 * 1024 * 1024;

/** Forward configuration selectors so discovery uses the same provider/profile as execution. */
function configurationArgs(spec: AgentSpec): string[] {
  const flags =
    spec.format === "codex"
      ? ["-c", "--config", "-p", "--profile", "--enable", "--disable"]
      : ["--settings", "--setting-sources"];
  const args: string[] = [];
  for (let i = 0; i < spec.args.length; i++) {
    const arg = spec.args[i]!;
    if (flags.includes(arg) && spec.args[i + 1] !== undefined) {
      args.push(arg, spec.args[++i]!);
    } else if (flags.some((flag) => arg.startsWith(`${flag}=`))) args.push(arg);
  }
  return args;
}

export async function readAgentModels(spec: AgentSpec, root: string): Promise<AgentModel[]> {
  if (!spec.command || (spec.format !== "codex" && spec.format !== "claude")) return [];
  const codex = spec.format === "codex";
  const args = codex
    ? ["app-server", ...configurationArgs(spec)]
    : [
        "-p",
        "--input-format",
        "stream-json",
        "--output-format",
        "stream-json",
        "--verbose",
        "--no-session-persistence",
        "--strict-mcp-config",
        "--mcp-config",
        '{"mcpServers":{}}',
        "--tools",
        "",
        ...configurationArgs(spec),
        "--settings",
        '{"disableAllHooks":true}',
      ];
  const child = Bun.spawn([spec.command, ...args], {
    cwd: root,
    env: agentEnv(process.env, { unset: envLeftOut(spec), env: spec.env }),
    stdin: "pipe",
    stdout: "pipe",
    stderr: "ignore",
    detached: process.platform !== "win32",
    windowsHide: true,
  });
  const stop = (): void => {
    try {
      if (process.platform === "win32") child.kill();
      else process.kill(-child.pid, "SIGTERM");
    } catch {
      /* Already exited. */
    }
  };
  let timedOut = false;
  const timer = setTimeout(() => {
    timedOut = true;
    stop();
  }, TIMEOUT_MS);
  const force = setTimeout(() => {
    try {
      if (process.platform === "win32") child.kill("SIGKILL");
      else process.kill(-child.pid, "SIGKILL");
    } catch {
      /* Already exited. */
    }
  }, TIMEOUT_MS + 1500);
  const send = (value: unknown): void => {
    child.stdin.write(`${JSON.stringify(value)}\n`);
  };
  try {
    send(
      codex
        ? {
            id: 1,
            method: "initialize",
            params: { clientInfo: { name: "alps_harness", version: "1" } },
          }
        : { type: "control_request", request_id: "models", request: { subtype: "initialize" } },
    );
    const decoder = new TextDecoder();
    let buffer = "";
    let bytes = 0;
    const models: AgentModel[] = [];
    const cursors = new Set<string>();
    for await (const chunk of child.stdout) {
      bytes += chunk.byteLength;
      if (bytes > MAX_OUTPUT_BYTES) throw new Error("The agent's model catalog is too large.");
      buffer += decoder.decode(chunk, { stream: true });
      let end: number;
      while ((end = buffer.indexOf("\n")) >= 0) {
        const line = buffer.slice(0, end);
        buffer = buffer.slice(end + 1);
        let message;
        try {
          message = JSON.parse(line);
        } catch {
          continue;
        }
        if (!message || typeof message !== "object") continue;
        if (
          !codex &&
          message.type === "control_response" &&
          message.response?.request_id === "models"
        ) {
          if (message.response.subtype !== "success")
            throw new Error("Claude Code refused the model catalog request.");
          return claudeModels(message.response.response);
        }
        if (codex && (message.id === 1 || message.id === 2)) {
          if (message.error) throw new Error("Codex refused the model catalog request.");
          if (message.id === 1) {
            send({ method: "initialized", params: {} });
            send({ id: 2, method: "model/list", params: { limit: 100, includeHidden: false } });
          } else {
            const page = codexModels(message.result);
            models.push(...page.models);
            if (!page.next) return [...new Map(models.map((m) => [m.id, m])).values()];
            if (cursors.has(page.next)) throw new Error("The agent repeated a model catalog page.");
            cursors.add(page.next);
            send({
              id: 2,
              method: "model/list",
              params: { limit: 100, includeHidden: false, cursor: page.next },
            });
          }
        }
      }
    }
    throw new Error(
      timedOut
        ? "The agent's model catalog request timed out."
        : "The agent exited without a model catalog. Update its CLI and check its sign-in.",
    );
  } finally {
    clearTimeout(timer);
    child.stdin.end();
    stop();
    await Promise.race([child.exited, new Promise((resolve) => setTimeout(resolve, 1500))]);
    try {
      if (process.platform !== "win32") process.kill(-child.pid, "SIGKILL");
      else if (child.exitCode === null) child.kill("SIGKILL");
    } catch {
      /* Already exited. */
    }
    clearTimeout(force);
  }
}
