/*
 * The harness server: the WebUI and the HTTP API. It listens on 127.0.0.1 only and answers
 * nothing to other Host headers (DNS rebinding). The page and its chunks are bundled at startup
 * and hold no secret: the per-start token reaches the browser only in the URL fragment
 * (`/#token=…`), which browsers never send to servers. The API requires the token, rejects
 * requests that browsers mark as coming from other sites, and accepts only JSON bodies for
 * writes. No response may be shown in a frame (clickjacking).
 */

import type { Server } from "bun";
import crypto from "node:crypto";
import type {
  Failure,
  HealthInfo,
  HttpErrorCode,
  ErrorCode,
  ServerEvent,
  ServerInfo,
} from "../shared/types.ts";
import { IdleTracker } from "./idle.ts";
import { probe, readServerInfo, removeServerInfo, serverUrl, writeServerInfo } from "./info.ts";
import { bundleUi, type UiBundle } from "./ui.ts";

/** Consecutive ports tried when the configured one is in use. */
const PORT_ATTEMPTS = 10;
const PING_MS = 20_000;
const MAX_BODY_BYTES = 1024 * 1024;

export interface ServeOptions {
  root: string;
  /** 0 lets the system choose a free port. */
  port: number;
  /** Minutes without connections before the server stops; `null` never stops (schedules are configured). */
  idleMinutes: number | null;
  /** Bun's development mode: the UI is an HTML import, bundled on request with HMR. */
  development: boolean;
  version: string;
  log: (line: string) => void;
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

/** Sent with every response: never cached, never framed, never sniffed, no referrer, no cross-origin reads. */
const HEADERS = {
  "Cache-Control": "no-store",
  "X-Content-Type-Options": "nosniff",
  "X-Frame-Options": "DENY",
  "Content-Security-Policy": "frame-ancestors 'none'",
  "Referrer-Policy": "no-referrer",
  "Cross-Origin-Resource-Policy": "same-origin",
};

const json = (status: number, body: unknown): Response =>
  Response.json(body, { status, headers: HEADERS });
const fail = (status: number, code: ErrorCode | HttpErrorCode, message: string): Response =>
  json(status, { ok: false, error: { code, message } } satisfies Failure);

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

/**
 * Starts the server for the workspace. Rejects with a UiBuildError, before listening, when the
 * WebUI does not bundle.
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

  const token = crypto.randomBytes(24).toString("hex");
  const startedAt = Date.now();
  const encoder = new TextEncoder();
  const streams = new Set<{ send(event: ServerEvent): void; close(): void }>();
  let stopping: Promise<void> | null = null;
  let resolveClosed: (reason: string) => void = () => {};
  const closed = new Promise<string>((resolve) => (resolveClosed = resolve));
  const idle = new IdleTracker(
    options.idleMinutes === null ? null : options.idleMinutes * 60_000,
    () => void stop("idle"),
  );

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

  /** Server-sent events. An open stream keeps the server from stopping when idle. */
  const openEvents = (request: Request, srv: Server<undefined>): Response => {
    srv.timeout(request, 0);
    const release = idle.hold();
    let ping: ReturnType<typeof setInterval> | undefined;
    let done = false;
    let stream: { send(event: ServerEvent): void; close(): void } | undefined;
    const finish = (): void => {
      if (done) return;
      done = true;
      clearInterval(ping);
      if (stream) streams.delete(stream);
      release();
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
        streams.add(stream);
        ping = setInterval(() => write(": ping\n\n"), PING_MS);
        request.signal.addEventListener("abort", finish, { once: true });
        write("retry: 2000\n\n");
        stream.send({ type: "hello", startedAt });
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
  };

  const handleApi = (request: Request, url: URL, srv: Server<undefined>): Response => {
    // Browsers say where a request comes from. Only the harness's own page (same-origin), the
    // address bar (none), and clients that are not browsers (no header) may use the API. A page
    // on another port of 127.0.0.1 is same-site and is refused too.
    const site = request.headers.get("sec-fetch-site");
    if (site !== null && site !== "same-origin" && site !== "none")
      return fail(403, "cross-site", "The API accepts requests only from the harness's own page.");
    // EventSource cannot send headers, so the event stream also accepts the token as a query parameter.
    const given =
      request.headers.get("x-harness-token") ??
      (url.pathname === "/api/events" ? url.searchParams.get("token") : null);
    if (!tokenMatches(given, token))
      return fail(
        401,
        "unauthorized",
        "The token is missing or wrong. Open the URL that alps-harness serve printed (…/#token=…).",
      );
    if (request.method !== "GET" && request.method !== "HEAD") {
      const type = (request.headers.get("content-type") ?? "").toLowerCase();
      if (!type.startsWith("application/json"))
        return fail(415, "unsupported-media-type", "Send the request body as JSON.");
    }

    switch (`${request.method} ${url.pathname}`) {
      case "GET /api/health":
        return json(200, health());
      case "GET /api/events":
        return openEvents(request, srv);
      case "POST /api/shutdown":
        setTimeout(() => void stop("stop"), 20);
        return json(200, { ok: true });
      default:
        return fail(404, "not-found", `${request.method} ${url.pathname} does not exist.`);
    }
  };

  /** The bundled page and its chunks, from memory. */
  const serveUi = (request: Request, url: URL): Response => {
    const asset =
      request.method === "GET" || request.method === "HEAD"
        ? ui?.assets.get(url.pathname)
        : undefined;
    if (!asset) return fail(404, "not-found", `${url.pathname} does not exist.`);
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
        if (!hostAllowed(request))
          return fail(403, "forbidden-host", "This host name is not accepted.");
        const url = new URL(request.url);
        return url.pathname.startsWith("/api/")
          ? handleApi(request, url, srv)
          : serveUi(request, url);
      },
      error(error) {
        log(`error: ${error.stack ?? error.message}`);
        return fail(500, "internal", "The server failed to handle the request.");
      },
    }),
  );

  const info: ServerInfo = { pid: process.pid, port: server.port ?? 0, token, startedAt };

  async function stop(reason: string): Promise<void> {
    stopping ??= (async () => {
      idle.stop();
      for (const stream of streams) {
        stream.send({ type: "shutdown" });
        stream.close();
      }
      removeServerInfo(root, info);
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
  idle.start();
  // The token stays out of the log: it is in server.json and in the URL that `serve` prints.
  log(`listening on ${serverUrl(info)} for ${root}${options.development ? " (development)" : ""}`);
  return { kind: "started", server: { info, url: serverUrl(info), closed, stop } };
}
