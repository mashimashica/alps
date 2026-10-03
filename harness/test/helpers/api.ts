import type { Failure } from "../../src/shared/types.ts";
import type { Daemon } from "./daemon.ts";

export interface Reply<T> {
  status: number;
  body: T | Failure;
}

export interface Api {
  get<T>(path: string): Promise<Reply<T>>;
  post<T>(path: string, body?: unknown): Promise<Reply<T>>;
  /** Like get and post, but fails the test unless the answer is a success. */
  ok<T>(method: "GET" | "POST", path: string, body?: unknown): Promise<T>;
}

/**
 * How long a request may take before it fails with its method and path, shorter than the tests'
 * own timeouts so that a test that stops says where. A request that asks to wait (`?wait=` in
 * seconds) gets that wait on top.
 */
export const REQUEST_TIMEOUT_MS = 20_000;

/** A client of the daemon's HTTP API, as the MCP server and the WebUI use it: token header, JSON bodies. */
export function apiClient(daemon: Pick<Daemon, "url" | "info">): Api {
  const send = async <T>(method: string, path: string, body?: unknown): Promise<Reply<T>> => {
    const url = new URL(path, daemon.url);
    const wait = Number(url.searchParams.get("wait") ?? 0);
    const limit = REQUEST_TIMEOUT_MS + (Number.isFinite(wait) && wait > 0 ? wait * 1000 : 0);
    try {
      const response = await fetch(url, {
        method,
        headers: {
          "X-Harness-Token": daemon.info.token,
          ...(method === "POST" ? { "Content-Type": "application/json" } : {}),
        },
        body: method === "POST" ? JSON.stringify(body ?? {}) : undefined,
        signal: AbortSignal.timeout(limit),
      });
      return { status: response.status, body: (await response.json()) as T | Failure };
    } catch (error) {
      if ((error as Error).name === "TimeoutError")
        throw new Error(`${method} ${path} did not answer within ${limit} ms`, { cause: error });
      throw error;
    }
  };
  return {
    get: (path) => send("GET", path),
    post: (path, body) => send("POST", path, body),
    async ok<T>(method: "GET" | "POST", path: string, body?: unknown): Promise<T> {
      const reply = await send<T>(method, path, body);
      if (reply.status >= 300 || (reply.body as { ok?: boolean }).ok !== true)
        throw new Error(
          `${method} ${path} answered ${reply.status}: ${JSON.stringify(reply.body)}`,
        );
      return reply.body as T;
    },
  };
}
