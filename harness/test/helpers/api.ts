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

/** A client of the daemon's HTTP API, as the MCP server and the WebUI use it: token header, JSON bodies. */
export function apiClient(daemon: Pick<Daemon, "url" | "info">): Api {
  const send = async <T>(method: string, path: string, body?: unknown): Promise<Reply<T>> => {
    const response = await fetch(new URL(path, daemon.url), {
      method,
      headers: {
        "X-Harness-Token": daemon.info.token,
        ...(method === "POST" ? { "Content-Type": "application/json" } : {}),
      },
      body: method === "POST" ? JSON.stringify(body ?? {}) : undefined,
    });
    return { status: response.status, body: (await response.json()) as T | Failure };
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
