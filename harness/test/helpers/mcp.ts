import { Client } from "@modelcontextprotocol/client";
import { StdioClientTransport } from "@modelcontextprotocol/client/stdio";
import type { Failure } from "../../src/shared/types.ts";
import { CLI, HARNESS_ROOT } from "./paths.ts";
import { cleanEnv } from "./process.ts";

export interface McpSession {
  client: Client;
  transport: StdioClientTransport;
  /** What the server wrote to stderr so far. */
  stderr(): string;
  close(): Promise<void>;
}

/** The name the tests' MCP clients give, which the harness records as who judged. */
export const CLIENT_NAME = "alps-harness-e2e";

/**
 * How long a test waits for a tool's result by default. It is longer than the longest get_run
 * wait the tests give (60 s), so that a run that does not end shows as status running in the
 * harness's answer instead of as the client giving up (the SDK's own default is 60 s).
 */
export const TOOL_TIMEOUT_MS = 120_000;

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
    /** The client's name (CLIENT_NAME by default). */
    name?: string;
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
    { name: options.name ?? CLIENT_NAME, version: "0.0.0" },
    { versionNegotiation: { mode: options.negotiation ?? "auto" } },
  );
  await client.connect(transport);
  return { client, transport, stderr: () => stderr, close: () => client.close() };
}

/**
 * Calls a tool and returns its structured result (`{ ok: true, … }`, the HTTP API's answer). A
 * failed call throws with the error it reported. `timeout` is the client's request timeout in
 * milliseconds.
 */
export async function callTool<T>(
  session: McpSession,
  name: string,
  args: Record<string, unknown> = {},
  timeout = TOOL_TIMEOUT_MS,
): Promise<T> {
  const result = await session.client.callTool({ name, arguments: args }, { timeout });
  if (result.isError)
    throw new Error(
      `${name} failed: ${JSON.stringify(result.structuredContent ?? result.content)}`,
    );
  return result.structuredContent as T;
}

/**
 * Calls a tool that is to fail and returns its error: the structured failure, and the texts
 * (the JSON and the sentence in the workspace's language that follows it). `timeout` is the
 * client's request timeout in milliseconds.
 */
export async function toolFailure(
  session: McpSession,
  name: string,
  args: Record<string, unknown> = {},
  timeout = TOOL_TIMEOUT_MS,
): Promise<{ error: Failure["error"]; texts: string[] }> {
  const result = await session.client.callTool({ name, arguments: args }, { timeout });
  if (!result.isError)
    throw new Error(`${name} did not fail: ${JSON.stringify(result.structuredContent)}`);
  const texts = (result.content as { type: string; text?: string }[]).map(
    (part) => part.text ?? "",
  );
  return { error: (result.structuredContent as Failure).error, texts };
}
