/*
 * The MCP server's connection to the workspace's harness server. The MCP server keeps no state of
 * its own: it reads .alps-harness/server.json, checks /api/health, and relays every tool call to
 * the HTTP API; when no server answers, it starts one (`serve` detached, as `serve --daemon`
 * does) and waits for server.json. While its client is connected it holds a session with the
 * server (GET /api/session) and names the session and the client in every request, so the server
 * knows who calls and which self runs to interrupt when the connection closes. The MCP server that
 * a wake gives its agent also names that wake run (X-Harness-Wake), and the one that an assessment
 * gives its agent, that assessment run (X-Harness-Assess).
 */

import fs from "node:fs";
import path from "node:path";
import { CONFIG_FILES, DEFAULT_PORT, type ParseYaml } from "../model/index.ts";
import { harnessConfigSchema } from "../shared/schema.ts";
import type { ClientInfo, Language, ServerInfo, SessionEvent } from "../shared/types.ts";
import { DaemonError, startDaemon } from "./daemon.ts";
import { liveServer, serverJsonPath, serverLogPath, serverUrl } from "./info.ts";

/** How long the MCP server waits to tell the harness server that its session ends. */
const CLOSE_TIMEOUT_MS = 1000;
/** How long the MCP server waits for the harness server to name the session it opened. */
const SESSION_TIMEOUT_MS = 5000;

/** The harness server could not be reached or started. */
export class RelayError extends Error {
  readonly files: string[];
  constructor(root: string, message: string) {
    super(message);
    this.name = "RelayError";
    this.files = [serverJsonPath(root), serverLogPath(root)];
  }
}

export interface Reply {
  status: number;
  body: unknown;
}

/** What the MCP server reads from alps-harness.yaml itself: its language, and the port for messages. */
export interface RelaySettings {
  language: Language;
  port: number;
}

interface Link {
  info: ServerInfo;
  /** The session the server gave, or `null` when it could not be opened. */
  session: string | null;
  stream: AbortController;
  ended: boolean;
}

const HEADLESS_DAEMON_ARGS = ["--headless"] as const;

/** Reads server-sent events from a stream until it ends. */
async function readEvents(
  body: ReadableStream<Uint8Array>,
  onEvent: (event: SessionEvent) => void,
): Promise<void> {
  const decoder = new TextDecoder();
  let buffer = "";
  try {
    for await (const chunk of body) {
      buffer += decoder.decode(chunk, { stream: true });
      for (let end = buffer.indexOf("\n\n"); end >= 0; end = buffer.indexOf("\n\n")) {
        const data = buffer
          .slice(0, end)
          .split("\n")
          .find((line) => line.startsWith("data: "));
        buffer = buffer.slice(end + 2);
        if (!data) continue;
        try {
          onEvent(JSON.parse(data.slice(6)) as SessionEvent);
        } catch {
          // Not an event of this protocol.
        }
      }
    }
  } catch {
    // The connection broke off.
  }
}

/** A request that no server received, so it may be sent again. */
const refused = (error: unknown): boolean =>
  (error as { code?: unknown } | null)?.code === "ConnectionRefused";

export class DaemonLink {
  readonly root: string;
  readonly #parseYaml: ParseYaml;
  /** The wake run whose agent this link serves, if any. */
  readonly #wake: string | null;
  /** The assessment run whose agent this link serves, if any. */
  readonly #assess: string | null;
  #link: Link | null = null;
  #connecting: Promise<Link> | null = null;
  #closed = false;
  #settings: { signature: string; value: RelaySettings } | null = null;

  constructor(
    root: string,
    parseYaml: ParseYaml,
    options: { wake?: string | null; assess?: string | null } = {},
  ) {
    this.root = root;
    this.#parseYaml = parseYaml;
    this.#wake = options.wake ?? null;
    this.#assess = options.assess ?? null;
  }

  /** The workspace's language and port; the defaults when alps-harness.yaml cannot be read. */
  settings(): RelaySettings {
    const file = CONFIG_FILES.map((name) => path.join(this.root, name)).find((candidate) =>
      fs.existsSync(candidate),
    );
    let signature = "-";
    if (file)
      try {
        const stat = fs.statSync(file);
        signature = `${file}:${stat.mtimeMs}:${stat.size}`;
      } catch {
        signature = "-";
      }
    if (this.#settings?.signature === signature) return this.#settings.value;
    let value: RelaySettings = { language: "en", port: DEFAULT_PORT };
    if (file)
      try {
        const text = fs.readFileSync(file, "utf8");
        const raw = /\.json$/i.test(file) ? JSON.parse(text) : this.#parseYaml(text);
        const parsed = harnessConfigSchema.safeParse(raw ?? {});
        if (parsed.success)
          value = {
            language: parsed.data.language ?? "en",
            port: parsed.data.server?.port ?? DEFAULT_PORT,
          };
      } catch {
        // The harness server reports what is wrong with the file (no-model).
      }
    this.#settings = { signature, value };
    return value;
  }

  /** Connects now, as the MCP server does when it starts; a failure is reported by the next request. */
  warmUp(): void {
    void this.#ensure().catch(() => {});
  }

  #ensure(serveArgs: readonly string[] = HEADLESS_DAEMON_ARGS): Promise<Link> {
    if (this.#link && !this.#link.ended) return Promise.resolve(this.#link);
    this.#connecting ??= this.#connect(serveArgs).finally(() => {
      this.#connecting = null;
    });
    return this.#connecting;
  }

  async #connect(serveArgs: readonly string[]): Promise<Link> {
    let info: ServerInfo;
    try {
      info =
        (await liveServer(this.root))?.info ?? (await startDaemon(this.root, [...serveArgs])).info;
    } catch (error) {
      if (error instanceof DaemonError) throw new RelayError(this.root, error.message);
      throw new RelayError(this.root, (error as Error).message);
    }
    const link: Link = { info, session: null, stream: new AbortController(), ended: false };
    link.session = await this.#openSession(link);
    this.#link = link;
    if (this.#closed) await this.#closeLink(link);
    return link;
  }

  /** Opens the session and keeps reading it; the link ends when the server closes it. */
  async #openSession(link: Link): Promise<string | null> {
    let response: Response;
    try {
      response = await fetch(new URL("api/session", serverUrl(link.info)), {
        headers: { "X-Harness-Token": link.info.token },
        signal: link.stream.signal,
        timeout: false,
      } as RequestInit);
    } catch {
      link.ended = true;
      return null;
    }
    // A server that answers without a session (one of another version) is still used, without it.
    if (!response.ok || !response.body) return null;
    return new Promise((resolve) => {
      let id: string | null = null;
      // The session's id is the stream's first event; a server that sends none is used without one.
      const timer = setTimeout(() => resolve(null), SESSION_TIMEOUT_MS);
      void readEvents(response.body as ReadableStream<Uint8Array>, (event) => {
        if (event.type === "session" && id === null) {
          id = event.id;
          clearTimeout(timer);
          resolve(id);
        }
      }).finally(() => {
        clearTimeout(timer);
        link.ended = true;
        resolve(id);
      });
    });
  }

  async #closeLink(link: Link): Promise<void> {
    if (link.session && !link.ended)
      await fetch(new URL(`api/sessions/${link.session}/close`, serverUrl(link.info)), {
        method: "POST",
        headers: { "X-Harness-Token": link.info.token, "Content-Type": "application/json" },
        body: "{}",
        signal: AbortSignal.timeout(CLOSE_TIMEOUT_MS),
      }).catch(() => {});
    link.ended = true;
    link.stream.abort();
  }

  /** Forgets a link whose server no longer answers, so the next request connects again. */
  #drop(link: Link): void {
    if (this.#link === link) this.#link = null;
    link.ended = true;
    link.stream.abort();
  }

  /**
   * Relays one request to the harness server, naming the session and the client. A server that
   * is gone is connected to (or started) again once, but only when the request cannot have
   * reached it. Throws a RelayError when no server can be reached.
   */
  async request(
    method: "GET" | "POST",
    route: string,
    options: {
      body?: unknown;
      client?: ClientInfo;
      signal?: AbortSignal;
      /** Arguments used only if this call has to start the daemon. */
      serveArgs?: readonly string[];
    } = {},
  ): Promise<Reply> {
    for (let attempt = 0; ; attempt++) {
      const link = await this.#ensure(options.serveArgs);
      let response: Response;
      try {
        response = await fetch(new URL(route.replace(/^\//, ""), serverUrl(link.info)), {
          method,
          headers: {
            "X-Harness-Token": link.info.token,
            ...(link.session ? { "X-Harness-Session": link.session } : {}),
            ...(options.client
              ? { "X-Harness-Client": encodeURIComponent(JSON.stringify(options.client)) }
              : {}),
            ...(this.#wake ? { "X-Harness-Wake": this.#wake } : {}),
            ...(this.#assess ? { "X-Harness-Assess": this.#assess } : {}),
            ...(method === "POST" ? { "Content-Type": "application/json" } : {}),
          },
          body: method === "POST" ? JSON.stringify(options.body ?? {}) : undefined,
          ...(options.signal ? { signal: options.signal } : {}),
          // get_run may wait 300 s for a run to end; Bun's fetch would give up after 300 s.
          timeout: false,
        } as RequestInit);
      } catch (error) {
        if (options.signal?.aborted) throw error;
        this.#drop(link);
        if (attempt === 0 && refused(error)) continue;
        throw new RelayError(
          this.root,
          `The request to the harness server on port ${link.info.port} failed: ${(error as Error).message}`,
        );
      }
      // Another server has taken the port (the one recorded stopped): connect again once.
      if (response.status === 401 && attempt === 0) {
        this.#drop(link);
        continue;
      }
      let body: unknown = null;
      try {
        body = await response.json();
      } catch {
        body = null;
      }
      return { status: response.status, body };
    }
  }

  /** Ends the session: the harness server interrupts the self runs this client has not finished. */
  async close(): Promise<void> {
    this.#closed = true;
    const link = this.#link;
    this.#link = null;
    if (link) await this.#closeLink(link);
  }
}
