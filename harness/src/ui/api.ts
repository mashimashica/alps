/*
 * The WebUI's side of the HTTP API: requests with the token, JSON bodies for writes, and failures
 * that carry the server's message key and arguments, so that they can be put in the page's
 * language. The event stream tells what changed; the page reads again what it shows.
 */

import { sayReceived } from "../shared/strings.ts";
import type { ErrorInfo, Language, ServerEvent } from "../shared/types.ts";

export class ApiError extends Error {
  readonly status: number;
  readonly info: ErrorInfo | null;

  constructor(status: number, info: ErrorInfo | null, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.info = info;
  }

  /** The server's message in a language (English when the key is not known). */
  describe(language: Language): string {
    return this.info
      ? sayReceived(language, this.info.key, this.info.args, this.info.message)
      : this.message;
  }
}

/** What went wrong, in the page's language. */
export const describeError = (error: unknown, language: Language): string =>
  error instanceof ApiError
    ? error.describe(language)
    : error instanceof Error
      ? error.message
      : String(error);

export type StreamState = "open" | "retrying" | "closed";

export interface Client {
  readonly token: string | null;
  get<T>(path: string): Promise<T>;
  post<T>(path: string, body?: unknown): Promise<T>;
  /** Opens the event stream; returns the function that closes it. */
  events(onEvent: (event: ServerEvent) => void, onState: (state: StreamState) => void): () => void;
}

/** A query string of the values that are set. */
export function query(values: Record<string, string | number | undefined | null>): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(values))
    if (value !== undefined && value !== null && value !== "") search.set(key, String(value));
  const text = search.toString();
  return text ? `?${text}` : "";
}

export function createClient(token: string | null): Client {
  async function send<T>(method: "GET" | "POST", path: string, body?: unknown): Promise<T> {
    if (!token) throw new ApiError(401, null, "This page has no token.");
    let response: Response;
    try {
      response = await fetch(path, {
        method,
        cache: "no-store",
        headers: {
          "X-Harness-Token": token,
          ...(method === "POST" ? { "Content-Type": "application/json" } : {}),
        },
        ...(method === "POST" ? { body: JSON.stringify(body ?? {}) } : {}),
      });
    } catch (error) {
      throw new ApiError(0, null, (error as Error).message);
    }
    let data: unknown = null;
    try {
      data = await response.json();
    } catch {
      // Not JSON: reported below by its status.
    }
    const failure = data as { ok?: boolean; error?: ErrorInfo } | null;
    if (!response.ok || failure?.ok !== true)
      throw new ApiError(
        response.status,
        failure?.error ?? null,
        failure?.error?.message ?? `${method} ${path} answered ${response.status}`,
      );
    return data as T;
  }

  return {
    token,
    get: (path) => send("GET", path),
    post: (path, body) => send("POST", path, body),
    events(onEvent, onState) {
      if (!token) {
        onState("closed");
        return () => {};
      }
      const source = new EventSource(`/api/events?token=${encodeURIComponent(token)}`);
      source.onopen = () => onState("open");
      source.onmessage = (message: MessageEvent<string>) => {
        let event: ServerEvent;
        try {
          event = JSON.parse(message.data) as ServerEvent;
        } catch {
          return;
        }
        onEvent(event);
      };
      source.onerror = () =>
        onState(source.readyState === EventSource.CLOSED ? "closed" : "retrying");
      return () => source.close();
    },
  };
}
