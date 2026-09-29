import { Client } from "@modelcontextprotocol/client";
import { StdioClientTransport } from "@modelcontextprotocol/client/stdio";
import { CLI, HARNESS_ROOT } from "./paths.ts";
import { cleanEnv } from "./process.ts";

export interface McpSession {
  client: Client;
  transport: StdioClientTransport;
  /** What the server wrote to stderr so far. */
  stderr(): string;
  close(): Promise<void>;
}

/**
 * Spawns `bun <cli> mcp` through the SDK's stdio transport and completes the handshake.
 * `auto` (the default) offers the newest protocol revision the client supports through
 * `server/discover` and falls back to `initialize` only for a server that does not know it;
 * `legacy` runs the 2025 `initialize` handshake, as hosts that predate 2026-07-28 do.
 */
export async function mcpClient(
  options: {
    workspace?: string;
    cli?: string;
    cwd?: string;
    env?: Record<string, string>;
    negotiation?: "auto" | "legacy";
  } = {},
): Promise<McpSession> {
  const transport = new StdioClientTransport({
    command: process.execPath,
    args: [options.cli ?? CLI, "mcp"],
    cwd: options.cwd ?? HARNESS_ROOT,
    env: cleanEnv({ ...options.env, ALPS_WORKSPACE: options.workspace }),
    stderr: "pipe",
  });
  let stderr = "";
  transport.stderr?.on("data", (chunk: Buffer | string) => (stderr += String(chunk)));
  const client = new Client(
    { name: "alps-harness-e2e", version: "0.0.0" },
    { versionNegotiation: { mode: options.negotiation ?? "auto" } },
  );
  await client.connect(transport);
  return { client, transport, stderr: () => stderr, close: () => client.close() };
}
