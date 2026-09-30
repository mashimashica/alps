/*
 * The harness server: the WebUI and the HTTP API. It listens on 127.0.0.1 only and answers
 * nothing to other Host headers (DNS rebinding). The page and its chunks are bundled at startup
 * and hold no secret: the per-start token reaches the browser only in the URL fragment
 * (`/#token=…`), which browsers never send to servers. The API requires the token, rejects
 * requests that browsers mark as coming from other sites, and accepts only JSON bodies for
 * writes. No response may be shown in a frame (clickjacking).
 *
 * An MCP server holds a session with the harness server while its client is connected
 * (`GET /api/session`, a stream like the event stream). The session names the self runs that the
 * client performs; when it closes (the MCP server ends, or says so), those runs are interrupted.
 * The server also wakes agents on the schedules of alps-harness.yaml (schedule.ts).
 */

import type { Server } from "bun";
import crypto from "node:crypto";
import type { Harness } from "../harness/index.ts";
import { say, type MessageArgs, type MessageKey } from "../shared/strings.ts";
import type {
  ErrorCode,
  Failure,
  HealthInfo,
  HttpErrorCode,
  ServerEvent,
  ServerInfo,
  SessionEvent,
} from "../shared/types.ts";
import { createApi } from "./api.ts";
import { IdleTracker } from "./idle.ts";
import { probe, readServerInfo, removeServerInfo, serverUrl, writeServerInfo } from "./info.ts";
import { openUi, removeOpenPage } from "./open.ts";
import { startSchedules, type Schedules } from "./schedule.ts";
import { bundleUi, type UiBundle } from "./ui.ts";

/** Consecutive ports tried when the configured one is in use. */
const PORT_ATTEMPTS = 10;
const PING_MS = 20_000;
const MAX_BODY_BYTES = 1024 * 1024;
/** How often, while a WebUI is connected, the workspace is checked for edits made outside the harness. */
const POLL_MS = 3000;

export interface ServeOptions {
  root: string;
  /** 0 lets the system choose a free port. */
  port: number;
  /** Minutes without connections, running runs, or schedules before the server stops. */
  idleMinutes: number;
  /** Bun's development mode: the UI is an HTML import, bundled on request with HMR. */
  development: boolean;
  version: string;
  log: (line: string) => void;
  /**
   * Reads the workspace's records (it may throw a StateError). It is called before the server
   * listens; the harness writes nothing until the server owns the workspace.
   */
  openHarness: () => Harness;
}

export interface HarnessServer {
  info: ServerInfo;
  url: string;
  /** Resolves with the reason once the server has stopped and server.json is removed. */
  closed: Promise<string>;
  stop(reason: string): Promise<void>;
}

export type StartResult =
  | { kind: "started"; server: HarnessServer }
  | { kind: "running"; info: ServerInfo };

/**
 * The page may run only the bundle it is served with (no inline or other scripts, so Markdown
 * that gets through as HTML cannot run), load nothing from elsewhere, and never be framed.
 */
export const CONTENT_SECURITY_POLICY = [
  "default-src 'self'",
  "script-src 'self'",
  "style-src 'self'",
  "img-src 'self' data:",
  "connect-src 'self'",
  "object-src 'none'",
  "base-uri 'none'",
  "form-action 'none'",
  "frame-ancestors 'none'",
].join("; ");

/** Sent with every response: never cached, never framed, never sniffed, no referrer, no cross-origin reads. */
const HEADERS = {
  "Cache-Control": "no-store",
  "X-Content-Type-Options": "nosniff",
  "X-Frame-Options": "DENY",
  "Content-Security-Policy": CONTENT_SECURITY_POLICY,
  "Referrer-Policy": "no-referrer",
  "Cross-Origin-Resource-Policy": "same-origin",
};

const json = (status: number, body: unknown): Response =>
  Response.json(body, { status, headers: HEADERS });

function fail<K extends MessageKey>(
  status: number,
  code: ErrorCode | HttpErrorCode,
  key: K,
  args: MessageArgs<K>,
): Response {
  return json(status, {
    ok: false,
    error: {
      code,
      message: say("en", key, args),
      key,
      args: args as Record<string, string | number | boolean>,
    },
  } satisfies Failure);
}

function tokenMatches(given: string | null, token: string): boolean {
  if (!given) return false;
  const a = Buffer.from(given);
  const b = Buffer.from(token);
  return a.length === b.length && crypto.timingSafeEqual(a, b);
}

const formatSize = (bytes: number): string => `${(bytes / 1024).toFixed(1)} KiB`;

/** Tries the configured port and the next ones while they are in use. Port 0 is tried once. */
function listen(port: number, serve: (port: number) => Server<undefined>): Server<undefined> {
  const attempts = port === 0 ? 1 : PORT_ATTEMPTS;
  for (let i = 0; ; i++) {
    try {
      return serve(port === 0 ? 0 : port + i);
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code !== "EADDRINUSE" || i + 1 >= attempts) throw error;
    }
  }
}

/** An open stream of server-sent events. */
interface Stream<T> {
  send(event: T): void;
  close(): void;
}

/**
 * Starts the server for the workspace. Rejects, before listening, with a UiBuildError when the
 * WebUI does not bundle and with a StateError when the records cannot be read.
 */
export async function startServer(options: ServeOptions): Promise<StartResult> {
  const { root, log } = options;

  // The UI is bundled before the server listens, so a broken UI stops the start. Only --dev uses
  // the HTML import, for HMR; its page and assets are served by Bun's routes and therefore bypass
  // the fetch handler (no Host check, no security headers). They hold no secret either.
  let ui: UiBundle | null = null;
  let devPage: Bun.HTMLBundle | null = null;
  if (options.development) {
    devPage = (await import("../ui/index.html")).default;
  } else {
    ui = await bundleUi();
    log(
      `bundled the WebUI in ${Math.round(ui.ms)} ms (${ui.assets.size} files, ${formatSize(ui.bytes)})`,
    );
  }

  const harness = options.openHarness();
  const token = crypto.randomBytes(24).toString("hex");
  const startedAt = Date.now();
  const encoder = new TextEncoder();
  const streams = new Set<Stream<ServerEvent>>();
  const sessions = new Map<string, Stream<SessionEvent>>();
  let stopping: Promise<void> | null = null;
  let resolveClosed: (reason: string) => void = () => {};
  const closed = new Promise<string>((resolve) => (resolveClosed = resolve));
  const idle = new IdleTracker(options.idleMinutes * 60_000, () => void stop("idle"));
  let schedules: Schedules | null = null;

  const api = createApi(harness, {
    openUi: (open) => openUi(root, { port: server.port ?? 0, token }, open),
  });

  const health = (): HealthInfo => ({
    ok: true,
    name: "alps-harness",
    version: options.version,
    pid: process.pid,
    port: server.port ?? 0,
    startedAt,
    workspace: root,
    development: options.development,
  });

  const hostAllowed = (request: Request): boolean => {
    const host = request.headers.get("host");
    return host === `127.0.0.1:${server.port}` || host === `localhost:${server.port}`;
  };

  /**
   * A stream of server-sent events. An open stream counts as a connection: it keeps the server
   * from stopping when idle. `onClose` runs once, however the stream ends.
   */
  function openStream<T>(
    request: Request,
    srv: Server<undefined>,
    first: T,
    onOpen: (stream: Stream<T>) => void,
    onClose: (stream: Stream<T>) => void,
  ): Response {
    srv.timeout(request, 0);
    const release = idle.hold();
    let ping: ReturnType<typeof setInterval> | undefined;
    let done = false;
    let stream: Stream<T> | undefined;
    const finish = (): void => {
      if (done) return;
      done = true;
      clearInterval(ping);
      release();
      if (stream) onClose(stream);
    };
    const body = new ReadableStream<Uint8Array>({
      start(controller) {
        const write = (chunk: string): void => {
          if (done) return;
          try {
            controller.enqueue(encoder.encode(chunk));
          } catch {
            finish();
          }
        };
        stream = {
          send: (event) => write(`data: ${JSON.stringify(event)}\n\n`),
          close: () => {
            finish();
            try {
              controller.close();
            } catch {
              // Already closed by the client.
            }
          },
        };
        onOpen(stream);
        ping = setInterval(() => write(": ping\n\n"), PING_MS);
        request.signal.addEventListener("abort", finish, { once: true });
        write("retry: 2000\n\n");
        stream.send(first);
      },
      cancel: finish,
    });
    return new Response(body, {
      headers: {
        ...HEADERS,
        "Content-Type": "text/event-stream; charset=utf-8",
        Connection: "keep-alive",
      },
    });
  }

  // While a WebUI is connected, edits made outside the harness (the model, a SKILL.md, an input
  // of a judged run) reach it as events.
  let poller: ReturnType<typeof setInterval> | null = null;
  const poll = (): void => {
    try {
      for (const event of harness.poll()) for (const stream of streams) stream.send(event);
    } catch (error) {
      log(`cannot check the workspace for changes: ${(error as Error).message}`);
    }
  };
  const openEvents = (request: Request, srv: Server<undefined>): Response =>
    openStream<ServerEvent>(
      request,
      srv,
      { type: "hello", startedAt },
      (stream) => {
        streams.add(stream);
        if (poller) return;
        poll();
        poller = setInterval(poll, POLL_MS);
      },
      (stream) => {
        streams.delete(stream);
        if (streams.size > 0 || !poller) return;
        clearInterval(poller);
        poller = null;
      },
    );

  const openSession = (request: Request, srv: Server<undefined>): Response => {
    const id = `s${crypto.randomBytes(8).toString("hex")}`;
    return openStream<SessionEvent>(
      request,
      srv,
      { type: "session", id },
      (stream) => sessions.set(id, stream),
      () => {
        sessions.delete(id);
        harness.sessionClosed(id);
      },
    );
  };

  const handleApi = async (
    request: Request,
    url: URL,
    srv: Server<undefined>,
  ): Promise<Response> => {
    // Browsers say where a request comes from. Only the harness's own page (same-origin), the
    // address bar (none), and clients that are not browsers (no header) may use the API. A page
    // on another port of 127.0.0.1 is same-site and is refused too.
    const site = request.headers.get("sec-fetch-site");
    if (site !== null && site !== "same-origin" && site !== "none")
      return fail(403, "cross-site", "error.crossSite", {});
    // EventSource cannot send headers, so the event stream also accepts the token as a query parameter.
    const given =
      request.headers.get("x-harness-token") ??
      (url.pathname === "/api/events" ? url.searchParams.get("token") : null);
    if (!tokenMatches(given, token)) return fail(401, "unauthorized", "error.token", {});
    if (request.method !== "GET" && request.method !== "HEAD") {
      const type = (request.headers.get("content-type") ?? "").toLowerCase();
      if (!type.startsWith("application/json"))
        return fail(415, "unsupported-media-type", "error.mediaType", {});
    }

    switch (`${request.method} ${url.pathname}`) {
      case "GET /api/health":
        return json(200, health());
      case "GET /api/events":
        return openEvents(request, srv);
      case "GET /api/session":
        return openSession(request, srv);
      case "POST /api/shutdown":
        setTimeout(() => void stop("stop"), 20);
        return json(200, { ok: true });
    }
    const closing = /^\/api\/sessions\/([A-Za-z0-9]+)\/close$/.exec(url.pathname);
    if (closing && request.method === "POST") {
      await request.text();
      sessions.get(closing[1] ?? "")?.close();
      return json(200, { ok: true });
    }
    const reply = await api(request, url, () => srv.timeout(request, 0));
    return reply
      ? json(reply.status, reply.body)
      : fail(404, "not-found", "error.route", { method: request.method, path: url.pathname });
  };

  /** The bundled page and its chunks, from memory. */
  const serveUi = (request: Request, url: URL): Response => {
    const asset =
      request.method === "GET" || request.method === "HEAD"
        ? ui?.assets.get(url.pathname)
        : undefined;
    if (!asset)
      return fail(404, "not-found", "error.route", { method: request.method, path: url.pathname });
    return new Response(asset.body, { headers: { ...HEADERS, "Content-Type": asset.type } });
  };

  const server = listen(options.port, (port) =>
    Bun.serve({
      hostname: "127.0.0.1",
      port,
      development: options.development ? { hmr: true } : false,
      maxRequestBodySize: MAX_BODY_BYTES,
      routes: devPage ? { "/": devPage } : undefined,
      fetch(request, srv) {
        idle.touch();
        if (!hostAllowed(request)) return fail(403, "forbidden-host", "error.host", {});
        const url = new URL(request.url);
        return url.pathname.startsWith("/api/")
          ? handleApi(request, url, srv)
          : serveUi(request, url);
      },
      error(error) {
        log(`error: ${error.stack ?? error.message}`);
        return fail(500, "internal", "error.internal", {});
      },
    }),
  );

  const info: ServerInfo = { pid: process.pid, port: server.port ?? 0, token, startedAt };

  async function stop(reason: string): Promise<void> {
    stopping ??= (async () => {
      idle.stop();
      schedules?.stop();
      if (poller) clearInterval(poller);
      poller = null;
      // The records are complete before server.json goes, so a server started next reads them
      // whole. Running agents are stopped with their process groups first.
      try {
        await harness.close();
      } catch (error) {
        log(`cannot write the records: ${(error as Error).message}`);
      }
      for (const stream of streams) {
        stream.send({ type: "shutdown" });
        stream.close();
      }
      // Closing a session deletes its entry, which iterating the map allows.
      for (const session of sessions.values()) {
        session.send({ type: "shutdown" });
        session.close();
      }
      removeServerInfo(root, info);
      removeOpenPage(root);
      await server.stop(true);
      log(`stopped (${reason})`);
      resolveClosed(reason);
    })();
    return stopping;
  }

  // Two servers starting at once must not both claim the workspace: the first to write server.json wins.
  if (!writeServerInfo(root, info, true)) {
    const recorded = readServerInfo(root);
    if (recorded && (await probe(recorded))) {
      await server.stop(true);
      return { kind: "running", info: recorded };
    }
    writeServerInfo(root, info, false);
  }
  process.once("exit", () => removeServerInfo(root, info));
  try {
    harness.start({
      broadcast: (event) => {
        for (const stream of streams) stream.send(event);
      },
      hold: () => idle.hold(),
    });
  } catch (error) {
    removeServerInfo(root, info);
    await server.stop(true);
    throw error;
  }
  schedules = startSchedules({ harness, hold: () => idle.hold(), log });
  idle.start();
  // The token stays out of the log: it is in server.json and in the URL that `serve` prints.
  log(`listening on ${serverUrl(info)} for ${root}${options.development ? " (development)" : ""}`);
  return { kind: "started", server: { info, url: serverUrl(info), closed, stop } };
}
