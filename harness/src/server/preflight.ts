import fs from "node:fs";
import path from "node:path";
import { mcpConfigFile, type McpServerLaunch } from "../agents/index.ts";
import type {
  ExecutionMcpConfig,
  ExecutionMcpConfigSave,
  ExecutionMcpProbe,
} from "../shared/types.ts";
import { CLI_PATH } from "./daemon.ts";

const PROBE_TIMEOUT_MS = 10000;
const MCP_PROTOCOL = "2026-07-28";

const text = (bytes: Uint8Array): string =>
  Buffer.from(bytes.buffer, bytes.byteOffset, bytes.byteLength).toString("utf8");

const unresolved = (value: unknown): boolean =>
  typeof value === "string" && /\$\{[A-Z0-9_]+\}/.test(value);

const timestamp = (): string => new Date().toISOString().replace(/[:.]/g, "-");

function backupIfChanged(file: string, next: string): string | null {
  if (!fs.existsSync(file)) return null;
  const current = fs.readFileSync(file, "utf8");
  if (current === next) return null;
  const backup = `${file}.alps-backup-${timestamp()}`;
  fs.copyFileSync(file, backup, fs.constants.COPYFILE_EXCL);
  return backup;
}

function writeChanged(file: string, next: string): { changed: boolean; backup: string | null } {
  const current = fs.existsSync(file) ? fs.readFileSync(file, "utf8") : null;
  if (current === next) return { changed: false, backup: null };
  fs.mkdirSync(path.dirname(file), { recursive: true, mode: 0o700 });
  const backup = backupIfChanged(file, next);
  fs.writeFileSync(`${file}.tmp`, next, { mode: 0o600 });
  fs.renameSync(`${file}.tmp`, file);
  return { changed: true, backup };
}

export function mcpServerForWorkspace(root: string): McpServerLaunch {
  return {
    name: "harness",
    command: process.execPath,
    args: [CLI_PATH, "mcp"],
    env: { ALPS_WORKSPACE: root },
  };
}

export function claudeProjectConfig(root: string, server: McpServerLaunch): ExecutionMcpConfig {
  const file = path.join(root, ".mcp.json");
  const recommended = mcpConfigFile(server);
  if (!fs.existsSync(file))
    return {
      path: file,
      exists: false,
      status: "missing",
      reason: "No project MCP config is present for this workspace.",
      recommended,
    };
  try {
    const parsed = JSON.parse(fs.readFileSync(file, "utf8")) as {
      mcpServers?: Record<string, { command?: unknown; args?: unknown; env?: unknown }>;
    };
    const configured = parsed.mcpServers?.[server.name];
    if (!configured)
      return {
        path: file,
        exists: true,
        status: "unusable",
        reason: `No ${server.name} MCP server is configured in this project file.`,
        recommended,
      };
    const values = [
      configured.command,
      ...(Array.isArray(configured.args) ? configured.args : []),
      ...Object.values(configured.env && typeof configured.env === "object" ? configured.env : {}),
    ];
    if (values.some(unresolved))
      return {
        path: file,
        exists: true,
        status: "plugin-template",
        reason:
          "This project config still contains plugin template variables; a directly opened project needs concrete paths.",
        recommended,
      };
    const usable =
      configured.command === server.command &&
      Array.isArray(configured.args) &&
      JSON.stringify(configured.args) === JSON.stringify(server.args) &&
      JSON.stringify(configured.env ?? {}) === JSON.stringify(server.env);
    return {
      path: file,
      exists: true,
      status: usable ? "usable" : "unusable",
      reason: usable ? null : "This project config does not match the current ALPS runtime.",
      recommended,
    };
  } catch (error) {
    return {
      path: file,
      exists: true,
      status: "unusable",
      reason: `Could not read this project MCP config: ${(error as Error).message}`,
      recommended,
    };
  }
}

const tomlString = (value: string): string => JSON.stringify(value);
const codexServerConfig = (server: McpServerLaunch): string =>
  [
    `[mcp_servers.${server.name}]`,
    `command = ${tomlString(server.command)}`,
    `args = [${server.args.map(tomlString).join(", ")}]`,
    `tool_timeout_sec = 90`,
    "",
    `[mcp_servers.${server.name}.env]`,
    ...Object.entries(server.env).map(([name, value]) => `${name} = ${tomlString(value)}`),
    "",
  ].join("\n");

const codexSection = (server: McpServerLaunch): RegExp =>
  new RegExp(
    `(^|\\n)\\[mcp_servers\\.${server.name.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}\\][\\s\\S]*?(?=\\n\\[(?!mcp_servers\\.${server.name.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}(?:\\.|\\]))[^\\n]+\\]|$)`,
  );

export function codexProjectConfig(root: string, server: McpServerLaunch): ExecutionMcpConfig {
  const file = path.join(root, ".codex", "config.toml");
  const recommended = codexServerConfig(server);
  if (!fs.existsSync(file))
    return {
      path: file,
      exists: false,
      status: "missing",
      reason: "No Codex project config is present for this workspace.",
      recommended,
    };
  try {
    const text = fs.readFileSync(file, "utf8");
    const match = codexSection(server).exec(text);
    if (!match)
      return {
        path: file,
        exists: true,
        status: "unusable",
        reason: `No ${server.name} MCP server is configured in this Codex project file.`,
        recommended,
      };
    const block = match[0].trim();
    const expected = recommended.trim();
    return {
      path: file,
      exists: true,
      status: block === expected ? "usable" : "unusable",
      reason:
        block === expected
          ? null
          : "This Codex project config does not match the current ALPS runtime.",
      recommended,
    };
  } catch (error) {
    return {
      path: file,
      exists: true,
      status: "unusable",
      reason: `Could not read this Codex project config: ${(error as Error).message}`,
      recommended,
    };
  }
}

export function saveProjectMcpConfigs(
  root: string,
  server: McpServerLaunch,
): ExecutionMcpConfigSave {
  const claudePath = path.join(root, ".mcp.json");
  const codexPath = path.join(root, ".codex", "config.toml");
  let claudeExisting: Record<string, unknown> = {};
  if (fs.existsSync(claudePath)) {
    try {
      claudeExisting = JSON.parse(fs.readFileSync(claudePath, "utf8")) as Record<string, unknown>;
    } catch {
      claudeExisting = {};
    }
  }
  const mcpServers =
    claudeExisting.mcpServers && typeof claudeExisting.mcpServers === "object"
      ? (claudeExisting.mcpServers as Record<string, unknown>)
      : {};
  const claudeServer = JSON.parse(mcpConfigFile(server)) as {
    mcpServers: Record<string, unknown>;
  };
  const claudeNext = `${JSON.stringify(
    {
      ...claudeExisting,
      mcpServers: {
        ...mcpServers,
        [server.name]: claudeServer.mcpServers[server.name],
      },
    },
    null,
    2,
  )}\n`;
  const claude = writeChanged(claudePath, claudeNext);

  const codexBlock = codexServerConfig(server).trimEnd();
  const codexCurrent = fs.existsSync(codexPath) ? fs.readFileSync(codexPath, "utf8") : "";
  const pattern = codexSection(server);
  const codexNext = pattern.test(codexCurrent)
    ? `${codexCurrent.replace(pattern, (match, prefix: string) => `${prefix}${codexBlock}`)}\n`
    : `${codexCurrent.trimEnd()}${codexCurrent.trim() ? "\n\n" : ""}${codexBlock}\n`;
  const codex = writeChanged(codexPath, codexNext);

  return {
    ok: true,
    server,
    claude: {
      ...claudeProjectConfig(root, server),
      changed: claude.changed,
      backup: claude.backup,
    },
    codex: { ...codexProjectConfig(root, server), changed: codex.changed, backup: codex.backup },
  };
}

export async function probeMcpServer(root: string): Promise<ExecutionMcpProbe> {
  const child = Bun.spawn([process.execPath, CLI_PATH, "mcp"], {
    cwd: root,
    stdin: "pipe",
    stdout: "pipe",
    stderr: "pipe",
    env: { ...process.env, ALPS_WORKSPACE: root },
  });
  const encoder = new TextEncoder();
  const replies = new Map<number, unknown>();
  const errors: string[] = [];
  let initialized = false;
  let toolsListed = false;
  let claimTool = false;
  let designTools = false;
  let toolCount = 0;
  let askedTools = false;

  const send = async (message: unknown): Promise<void> => {
    child.stdin.write(encoder.encode(`${JSON.stringify(message)}\n`));
    await child.stdin.flush();
  };

  await send({
    jsonrpc: "2.0",
    id: 1,
    method: "initialize",
    params: {
      protocolVersion: MCP_PROTOCOL,
      capabilities: {},
      clientInfo: { name: "alps-preflight", version: "0" },
    },
  });

  const reader = child.stdout.getReader();
  let buffer = "";
  const started = Date.now();
  try {
    for (;;) {
      const remaining = PROBE_TIMEOUT_MS - (Date.now() - started);
      if (remaining <= 0) throw new Error("MCP probe timed out.");
      const read = await Promise.race([
        reader.read(),
        new Promise<never>((_, reject) =>
          setTimeout(() => reject(new Error("MCP probe timed out.")), remaining),
        ),
      ]);
      if (read.done) break;
      buffer += text(read.value);
      for (;;) {
        const end = buffer.indexOf("\n");
        if (end < 0) break;
        const line = buffer.slice(0, end).trim();
        buffer = buffer.slice(end + 1);
        if (!line) continue;
        try {
          const message = JSON.parse(line) as {
            id?: unknown;
            error?: { message?: string };
            result?: { tools?: { name?: string }[] };
          };
          if (typeof message.id === "number") replies.set(message.id, message);
          if (message.error?.message) errors.push(message.error.message);
          if (message.id === 1 && !message.error) {
            initialized = true;
            if (!askedTools) {
              askedTools = true;
              await send({
                jsonrpc: "2.0",
                method: "notifications/initialized",
                params: {},
              });
              await send({ jsonrpc: "2.0", id: 2, method: "tools/list", params: {} });
            }
          }
          if (message.id === 2 && !message.error) {
            toolsListed = true;
            const tools = Array.isArray(message.result?.tools) ? message.result.tools : [];
            toolCount = tools.length;
            const names = new Set(tools.map((tool) => tool.name).filter(Boolean));
            claimTool = names.has("claim_launch");
            designTools =
              names.has("claim_design") &&
              names.has("get_design_context") &&
              names.has("submit_design_questions") &&
              names.has("submit_design_proposal");
            break;
          }
        } catch (error) {
          errors.push((error as Error).message);
        }
      }
      if (toolsListed) break;
    }
  } catch (error) {
    errors.push((error as Error).message);
  } finally {
    child.stdin.end();
    child.kill();
    await child.exited.catch(() => {});
  }
  return {
    ok: initialized && toolsListed && claimTool,
    initialized,
    toolsListed,
    claimTool,
    designTools,
    toolCount,
    error:
      errors[0] ??
      (replies.has(2) && !claimTool
        ? "claim_launch is not listed."
        : replies.has(2) && !designTools
          ? "design tools are not listed."
          : null),
  };
}
