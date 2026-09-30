/*
 * E8 (Plugin structure, safety): requests with another Host header, without the token, with a
 * path outside the workspace (or in its .alps-harness/), or with a body that is not JSON are
 * rejected. With them, what makes the WebUI safe to open: the token reaches the browser only in
 * the URL fragment, never on a command line (serve --open and open_ui hand the browser a page
 * that only the owner can read), the page and its chunks hold no secret, no other site can use
 * the API or frame the page, and the server listens on 127.0.0.1 only. The one body that is not
 * JSON, the files attached to a request (POST /api/attachments, multipart/form-data), passes the
 * same checks, is saved only inside the workspace and outside .alps-harness/ under a harmless
 * name that is free there (a symlink that leads nowhere takes its name too), all the files of an
 * upload or none, and is refused over 20 MB a file, 10 files, or 21 MiB a body (unread when the
 * body says so); a JSON body over 1 MiB is refused too, on every route that reads one.
 */

import { afterAll, beforeAll, describe, expect, test } from "bun:test";
import fs from "node:fs";
import net from "node:net";
import os from "node:os";
import path from "node:path";
import { MAX_JSON_BYTES, MAX_UPLOAD_BYTES } from "../../src/server/api.ts";
import {
  dayOf,
  MAX_ATTACHMENT_BYTES,
  MAX_ATTACHMENTS,
  MAX_NAME_CANDIDATES,
} from "../../src/shared/requests.ts";
import type {
  AttachmentsResponse,
  Failure,
  InstanceResponse,
  InstancesResponse,
  OpenResponse,
} from "../../src/shared/types.ts";
import { apiClient } from "../helpers/api.ts";
import { closeBrowser, killStrayBrowsers, launchBrowser } from "../helpers/browser.ts";
import { killStrayDaemons, startDaemon, type Daemon } from "../helpers/daemon.ts";
import { callTool, mcpClient, toolFailure } from "../helpers/mcp.ts";
import { records } from "../helpers/paths.ts";
import { HOOK_TIMEOUT_MS, isAlive, waitFor } from "../helpers/process.ts";
import { tmpWorkspace, type TmpWorkspace } from "../helpers/workspace.ts";

/** Every route of the API, and one that does not exist: the checks come before routing. */
const ROUTES = [
  { method: "GET", path: "/api/health" },
  { method: "GET", path: "/api/events" },
  { method: "POST", path: "/api/shutdown" },
  { method: "GET", path: "/api/model" },
  { method: "GET", path: "/api/artifacts" },
  { method: "GET", path: "/api/session" },
  { method: "POST", path: "/api/sessions/s1/close" },
  { method: "GET", path: "/api/instances" },
  { method: "POST", path: "/api/instances" },
  { method: "GET", path: "/api/instances/i1" },
  { method: "POST", path: "/api/instances/i1/run" },
  { method: "POST", path: "/api/instances/i1/evaluate" },
  { method: "GET", path: "/api/runs" },
  { method: "GET", path: "/api/runs/r1" },
  { method: "POST", path: "/api/runs/r1/cancel" },
  { method: "POST", path: "/api/runs/r1/finish" },
  { method: "GET", path: "/api/assessment" },
  { method: "GET", path: "/api/stats" },
  { method: "GET", path: "/api/skill" },
  { method: "POST", path: "/api/wake" },
  { method: "POST", path: "/api/open" },
  { method: "POST", path: "/api/attachments" },
  { method: "GET", path: "/api/unknown" },
] as const;

/** The route whose body is files (multipart/form-data) rather than JSON. */
const UPLOAD = "/api/attachments";

/**
 * The Content-Security-Policy of every response: no page may frame it, and a page may run only
 * the scripts that the server serves (no inline script, nothing from elsewhere).
 */
function expectPolicy(policy: string | null, where: string): void {
  const directives = (policy ?? "").split(";").map((d) => d.trim());
  expect(directives, where).toContain("frame-ancestors 'none'");
  expect(directives, where).toContain("script-src 'self'");
  expect(directives, where).toContain("default-src 'self'");
}

let ws: TmpWorkspace;
let daemon: Daemon;
/** Where the stand-in browser writes the URL it was asked to open. */
let opened: string;

beforeAll(async () => {
  ws = tmpWorkspace({ server: { idleMinutes: 5 } });
  opened = path.join(ws.base, "opened.txt");
  // A stand-in for the browser: it records the URL that serve --open hands to $BROWSER.
  const browser = path.join(ws.base, "browser.sh");
  const script = `#!/bin/sh\nprintf '%s' "$1" > '${opened}.part' && mv '${opened}.part' '${opened}'\n`;
  fs.writeFileSync(browser, script, { mode: 0o755 });
  daemon = await startDaemon(ws.root, ["--open"], { env: { BROWSER: browser } });
}, HOOK_TIMEOUT_MS);

afterAll(async () => {
  killStrayBrowsers();
  await daemon?.stop().catch(() => {});
  killStrayDaemons();
  ws?.dispose();
}, HOOK_TIMEOUT_MS);

interface Sent {
  status: number;
  headers: Headers;
  body: string;
  /** `error.code` of a JSON failure. */
  code: string | undefined;
}

/** Reads an open event stream until it has sent `needle`, then closes it. */
async function readUntil(response: Response, needle: string, timeoutMs = 5000): Promise<string> {
  const reader = response.body!.getReader();
  const decoder = new TextDecoder();
  const timer = setTimeout(() => void reader.cancel(), timeoutMs);
  let text = "";
  try {
    while (!text.includes(needle)) {
      const { done, value } = await reader.read();
      if (done) break;
      text += decoder.decode(value, { stream: true });
    }
  } finally {
    clearTimeout(timer);
    await reader.cancel().catch(() => {});
  }
  return text;
}

/**
 * Sends one request to the daemon as a client that is not a browser, which may set any header.
 * The body is bytes, so no Content-Type is added unless `type` is given.
 */
async function send(request: {
  method?: string;
  path: string;
  host?: string;
  token?: string | null;
  site?: string;
  type?: string;
}): Promise<Sent> {
  const method = request.method ?? "GET";
  const headers: Record<string, string> = {};
  if (request.host) headers.Host = request.host;
  if (request.token) headers["X-Harness-Token"] = request.token;
  if (request.site) headers["Sec-Fetch-Site"] = request.site;
  if (request.type) headers["Content-Type"] = request.type;
  const response = await fetch(new URL(request.path, daemon.url), {
    method,
    headers,
    body: method === "POST" ? new TextEncoder().encode("{}") : undefined,
    redirect: "manual",
  });
  const stream = response.headers.get("content-type")?.startsWith("text/event-stream");
  const body = stream ? await readUntil(response, '"type":"hello"') : await response.text();
  let code: string | undefined;
  try {
    code = (JSON.parse(body) as { error?: { code?: string } }).error?.code;
  } catch {
    code = undefined;
  }
  return { status: response.status, headers: response.headers, body, code };
}

/**
 * Sends only the head of a POST whose body, it says, is `length` bytes long, and returns the
 * status that the daemon answers before any of the body is sent (a timeout when it waits for it).
 */
function answerToHead(pathname: string, type: string, length: number): Promise<number> {
  const { port, token } = daemon.info;
  return new Promise((resolve, reject) => {
    const socket = net.connect(port, "127.0.0.1", () =>
      socket.write(
        `POST ${pathname} HTTP/1.1\r\nHost: 127.0.0.1:${port}\r\nX-Harness-Token: ${token}\r\n` +
          `Content-Type: ${type}\r\nContent-Length: ${length}\r\n\r\n`,
      ),
    );
    socket.setTimeout(5000, () => {
      socket.destroy();
      reject(new Error(`${pathname} did not answer before the body was sent`));
    });
    socket.once("data", (data) => {
      socket.destroy();
      resolve(Number(/^HTTP\/1\.1 (\d{3})/.exec(data.toString())?.[1]));
    });
    socket.once("error", reject);
  });
}

/** A body that does not say its length: it is sent in chunks. */
const chunked = (text: string): ReadableStream<Uint8Array> =>
  new ReadableStream({
    start(controller) {
      controller.enqueue(new TextEncoder().encode(text));
      controller.close();
    },
  });

/**
 * Whether the daemon answers /api/health at `address`. A VPN tunnel may accept a connection on
 * any port of its own address and never reply, so being connected is not enough: the answer
 * must come from this daemon.
 */
async function answersAt(address: string): Promise<boolean> {
  const { port, token, pid } = daemon.info;
  const host = net.isIPv6(address) ? `[${address}]` : address;
  try {
    const response = await fetch(`http://${host}:${port}/api/health`, {
      headers: { Host: `127.0.0.1:${port}`, "X-Harness-Token": token },
      signal: AbortSignal.timeout(1500),
    });
    return ((await response.json()) as { pid?: number }).pid === pid;
  } catch {
    return false;
  }
}

/** This machine's addresses other than 127.0.0.1 (link-local IPv6 needs a scope and is left out). */
function otherAddresses(): string[] {
  const addresses = Object.values(os.networkInterfaces())
    .flat()
    .map((entry) => entry?.address ?? "")
    .filter((address) => address && address !== "127.0.0.1" && !/^fe80:/i.test(address));
  return [...new Set([...addresses, "::1"])];
}

/** The addresses a process listens on for TCP, from lsof (macOS, Linux), or null without lsof. */
function listeningAddresses(pid: number): string[] | null {
  try {
    const lsof = Bun.spawnSync([
      "lsof",
      "-nP",
      "-a",
      "-p",
      String(pid),
      "-iTCP",
      "-sTCP:LISTEN",
      "-Fn",
    ]);
    if (!lsof.success) return null;
    return lsof.stdout
      .toString()
      .split("\n")
      .filter((line) => line.startsWith("n"))
      .map((line) => line.slice(1));
  } catch {
    return null;
  }
}

/** The same-origin scripts and stylesheets a page loads. */
const assetPaths = (html: string): string[] =>
  [...html.matchAll(/<(?:script|link)\b[^>]*?\b(?:src|href)="(\/[^"]*)"/g)].map((m) => m[1] ?? "");

describe("E8 safety", () => {
  test("E8 serve prints the URL with the token in its fragment, --open hands the browser a page only the owner can read, and server.log does not hold the token", async () => {
    const { port, token } = daemon.info;
    // Browsers never send the fragment: not in the request line, not in Referer.
    expect(daemon.uiUrl).toBe(`http://127.0.0.1:${port}/#token=${token}`);
    await waitFor(() => fs.existsSync(opened), 10_000, "serve --open to start the browser");
    // The browser's command line, which ps shows to every user, names a page, not the URL.
    const page = fs.readFileSync(opened, "utf8");
    expect(page).toBe(records(ws.root, "open.html"));
    expect(page).not.toContain(token);
    expect(fs.statSync(page).mode & 0o777).toBe(0o600);
    // The page sends the browser on to the URL, token and all.
    const html = fs.readFileSync(page, "utf8");
    expect(html).toContain(`location.replace(${JSON.stringify(daemon.uiUrl)})`);
    expect(html).toContain(`content="0; url=${daemon.uiUrl}"`);
    expect(
      fs.readFileSync(path.join(ws.root, ".alps-harness", "server.log"), "utf8"),
    ).not.toContain(token);
  });

  test("E8 open_ui returns the URL with the token in its fragment, and with open: true the daemon opens it through the same page", async () => {
    const { port, token } = daemon.info;
    const mcp = await mcpClient({ workspace: ws.root });
    try {
      const shown = await callTool<OpenResponse>(mcp, "open_ui", { view: "instances" });
      expect(shown).toEqual({
        ok: true,
        url: `http://127.0.0.1:${port}/#token=${token}&view=instances`,
        opened: false,
      });
      fs.rmSync(opened, { force: true });
      const result = await callTool<OpenResponse>(mcp, "open_ui", { open: true });
      expect(result).toEqual({ ok: true, url: daemon.uiUrl, opened: true });
      await waitFor(() => fs.existsSync(opened), 10_000, "open_ui to start the browser");
      const page = fs.readFileSync(opened, "utf8");
      expect(page).toBe(records(ws.root, "open.html"));
      expect(fs.statSync(page).mode & 0o777).toBe(0o600);
      expect(fs.readFileSync(page, "utf8")).toContain(JSON.stringify(daemon.uiUrl));
      // A screen the WebUI does not have is refused before it reaches the daemon.
      const unknown = await mcp.client.callTool({
        name: "open_ui",
        arguments: { view: "timeline" },
      });
      expect(unknown.isError).toBe(true);
    } finally {
      await mcp.close();
    }
  });

  test("E8 every /api/* route answers 403 to another Host header", async () => {
    const { port, token } = daemon.info;
    const hosts = [
      `attacker.example:${port}`,
      "attacker.example",
      `127.0.0.1.attacker.example:${port}`,
      `127.0.0.1:${port + 1}`,
    ];
    for (const route of ROUTES) {
      for (const host of hosts) {
        const sent = await send({ ...route, host, token, type: "application/json" });
        expect(sent.status, `${route.method} ${route.path} for ${host}`).toBe(403);
        expect(sent.code).toBe("forbidden-host");
      }
    }
    // The server's own names pass, and the rejected shutdowns did not stop it.
    for (const host of [`127.0.0.1:${port}`, `localhost:${port}`])
      expect((await send({ path: "/api/health", host, token })).status).toBe(200);
    expect(isAlive(daemon.info.pid)).toBe(true);
  });

  test("E8 / and its chunks hold no secret, and another Host header gets none of them", async () => {
    const { port, token } = daemon.info;
    const page = await send({ path: "/" });
    expect(page.status).toBe(200);
    expect(page.headers.get("content-type")).toContain("text/html");
    const assets = assetPaths(page.body);
    expect(assets.length).toBeGreaterThan(0);
    for (const target of ["/", ...assets]) {
      const own = await send({ path: target });
      expect(own.status, target).toBe(200);
      expect(own.body, target).not.toContain(token);
      expect(own.headers.get("x-frame-options"), target).toBe("DENY");
      expectPolicy(own.headers.get("content-security-policy"), target);
      expect(own.headers.get("x-content-type-options"), target).toBe("nosniff");

      const other = await send({ path: target, host: `attacker.example:${port}` });
      expect(other.status, target).toBe(403);
      expect(other.body, target).not.toContain(token);
    }
    // Only the bundle is served: not the sources, and not the workspace's server.json.
    for (const target of [
      "/main.tsx",
      "/src/ui/main.tsx",
      "/package.json",
      "/.alps-harness/server.json",
    ])
      expect((await send({ path: target })).status, target).toBe(404);
  });

  test("E8 /api/* answers 403 when Sec-Fetch-Site is cross-site or same-site", async () => {
    const { token } = daemon.info;
    for (const route of ROUTES) {
      for (const site of ["cross-site", "same-site"]) {
        const sent = await send({ ...route, site, token, type: "application/json" });
        expect(sent.status, `${route.method} ${route.path} from ${site}`).toBe(403);
        expect(sent.code).toBe("cross-site");
      }
    }
    // The harness's own page, the address bar, and clients that are not browsers pass.
    for (const site of ["same-origin", "none", undefined])
      expect((await send({ path: "/api/health", site, token })).status, String(site)).toBe(200);
    expect(isAlive(daemon.info.pid)).toBe(true);
  });

  test(
    "E8 the WebUI does not work in a frame of another origin",
    async () => {
      // Another site (localhost is not the same site as 127.0.0.1) frames the WebUI, token and all.
      const other = Bun.serve({
        hostname: "127.0.0.1",
        port: 0,
        fetch: () =>
          new Response(
            `<!doctype html><title>Another site</title><iframe id="ui" src="${daemon.uiUrl}" width="800" height="300"></iframe>`,
            { headers: { "Content-Type": "text/html; charset=utf-8" } },
          ),
      });
      const otherUrl = `http://localhost:${other.port}/`;
      const origin = new URL(daemon.url).origin;
      const browser = await launchBrowser();
      try {
        const page = await browser.newPage();
        const api: string[] = [];
        const documents: { status: number; frameOptions: string | undefined }[] = [];
        page.on("request", (request) => {
          const url = new URL(request.url());
          if (url.origin === origin && url.pathname.startsWith("/api/")) api.push(url.pathname);
        });
        page.on("response", (response) => {
          if (response.request().resourceType() === "document" && response.url().startsWith(origin))
            documents.push({
              status: response.status(),
              frameOptions: response.headers()["x-frame-options"],
            });
        });
        const framed = page.frameLocator("#ui");

        // Control: with the two headers taken off the page, the framed UI gets the token and works.
        const isPage = (url: URL): boolean => url.origin === origin && url.pathname === "/";
        await page.route(isPage, async (route) => {
          const response = await route.fetch();
          const headers = { ...response.headers() };
          delete headers["x-frame-options"];
          delete headers["content-security-policy"];
          await route.fulfill({ response, headers });
        });
        await page.goto(otherUrl);
        await framed
          .locator('[data-testid="health"][data-status="ok"]')
          .waitFor({ timeout: 10_000 });
        expect(api).toContain("/api/health");
        await page.unroute(isPage);

        // As served, the browser refuses to show the page in the frame: it never runs or calls the API.
        api.length = 0;
        documents.length = 0;
        await page.goto(otherUrl, { waitUntil: "networkidle" });
        expect(documents).toEqual([{ status: 200, frameOptions: "DENY" }]);
        expect(api).toEqual([]);
        expect(await framed.getByTestId("health").count()).toBe(0);
      } finally {
        await closeBrowser(browser);
        await other.stop(true);
      }
    },
    { timeout: 60_000 },
  );

  test("E8 /api/* answers 401 without the token, and only /api/events takes it from the query", async () => {
    const { token } = daemon.info;
    for (const route of ROUTES) {
      for (const given of [null, "0".repeat(token.length), token.slice(1)]) {
        const sent = await send({ ...route, token: given, type: "application/json" });
        expect(sent.status, `${route.method} ${route.path} with ${given}`).toBe(401);
        expect(sent.code).toBe("unauthorized");
        // No answer of the API may be framed by another page.
        expect(sent.headers.get("x-frame-options"), route.path).toBe("DENY");
        expectPolicy(sent.headers.get("content-security-policy"), route.path);
      }
    }
    // EventSource cannot send headers, so the event stream, and only it, reads the token from the query.
    for (const route of ROUTES.filter((r) => r.path !== "/api/events")) {
      const sent = await send({
        ...route,
        path: `${route.path}?token=${token}`,
        type: "application/json",
      });
      expect(sent.status, `${route.method} ${route.path}?token=`).toBe(401);
    }
    const events = await send({ path: `/api/events?token=${token}` });
    expect(events.status).toBe(200);
    expect(events.headers.get("content-type")).toContain("text/event-stream");
    expect(events.body).toContain('"type":"hello"');
    expect(isAlive(daemon.info.pid)).toBe(true);
  });

  test("E8 a POST that is not JSON answers 415, and the attachments take multipart/form-data only", async () => {
    const { token } = daemon.info;
    // No type, and the three that another site can send without a CORS preflight, to every POST
    // route but the attachments.
    for (const route of ROUTES.filter((r) => r.method === "POST" && r.path !== UPLOAD))
      for (const type of [
        undefined,
        "text/plain",
        "application/x-www-form-urlencoded",
        "multipart/form-data; boundary=x",
      ]) {
        const sent = await send({ ...route, token, type });
        expect(sent.status, `${route.path} ${String(type)}`).toBe(415);
        expect(sent.code).toBe("unsupported-media-type");
      }
    // The attachments are files, as a form sends them; a form of another site cannot send the
    // token, and the checks above refuse it anyway. Any other body is refused there.
    for (const type of [
      undefined,
      "text/plain",
      "application/x-www-form-urlencoded",
      "application/json",
    ]) {
      const sent = await send({ method: "POST", path: UPLOAD, token, type });
      expect(sent.status, `${UPLOAD} ${String(type)}`).toBe(415);
      expect(sent.code).toBe("unsupported-media-type");
    }
    expect(isAlive(daemon.info.pid)).toBe(true);
    expect((await send({ path: "/api/health", token })).status).toBe(200);
  });

  test("E8 the server listens on 127.0.0.1 only", async () => {
    const { port, pid } = daemon.info;
    const listening = listeningAddresses(pid);
    if (listening !== null) expect(listening).toEqual([`127.0.0.1:${port}`]);

    // It answers on 127.0.0.1, and on no other address of this machine.
    expect(await answersAt("127.0.0.1")).toBe(true);
    const others = otherAddresses();
    expect(others.length).toBeGreaterThan(0);
    const answered = await Promise.all(others.map((address) => answersAt(address)));
    expect(Object.fromEntries(others.map((address, i) => [address, answered[i]]))).toEqual(
      Object.fromEntries(others.map((address) => [address, false])),
    );
  });

  test("E8 paths outside the workspace or in its .alps-harness/ are rejected as instance inputs and outputs", async () => {
    const api = apiClient(daemon);
    // A directory beside the workspace, a symlink in the workspace that leads to it, and a symlink
    // to a file there that does not exist yet.
    const outside = path.join(ws.base, "outside");
    fs.mkdirSync(outside, { recursive: true });
    fs.writeFileSync(path.join(outside, "notes.md"), "Not the workspace's.\n");
    fs.symlinkSync(outside, path.join(ws.root, "docs", "elsewhere"));
    fs.symlinkSync(path.join(outside, "later.md"), path.join(ws.root, "docs", "later.md"));
    // The harness's own records, directly and through a symlink.
    fs.symlinkSync(path.join(ws.root, ".alps-harness"), path.join(ws.root, "docs", "records"));
    const refused = [
      "../outside/notes.md",
      "docs/../../outside/notes.md",
      path.join(outside, "notes.md"),
      "/etc/hosts",
      "docs/elsewhere/notes.md",
      "docs/elsewhere/new.md",
      "docs/later.md",
      ".alps-harness/state.json",
      "./.alps-harness/runs/r1.jsonl",
      "docs/../.alps-harness/server.json",
      ".ALPS-HARNESS/state.json",
      path.join(ws.root, ".alps-harness", "notes.md"),
      "docs/records/state.json",
    ];
    for (const given of refused) {
      for (const body of [
        { process: "Requirements Clarification", inputs: { "Stakeholder information": [given] } },
        { process: "Requirements Clarification", outputs: { "Change brief": given } },
      ]) {
        const sent = await api.post("/api/instances", body);
        expect(sent.status, JSON.stringify(body)).toBe(403);
        expect((sent.body as Failure).error.code).toBe("outside-workspace");
      }
    }
    expect((await api.ok<InstancesResponse>("GET", "/api/instances")).instances).toEqual([]);

    // The MCP server relays the same refusal.
    const mcp = await mcpClient({ workspace: ws.root });
    try {
      const { error } = await toolFailure(mcp, "instantiate", {
        process: "Requirements Clarification",
        inputs: { "Stakeholder information": [".alps-harness/state.json"] },
      });
      expect(error.code).toBe("outside-workspace");
    } finally {
      await mcp.close();
    }

    // An input is a concrete path, not a pattern.
    const pattern = await api.post("/api/instances", {
      process: "Requirements Clarification",
      inputs: { "Stakeholder information": ["docs/changes/*/stakeholders.md"] },
    });
    expect([pattern.status, (pattern.body as Failure).error.code]).toEqual([
      400,
      "invalid-request",
    ]);

    // A name that merely starts with two dots stays inside.
    const dotted = await api.post<InstanceResponse>("/api/instances", {
      process: "Requirements Clarification",
      inputs: { "Stakeholder information": ["..notes.md", "docs/..draft.md"] },
    });
    expect(dotted.status).toBe(201);
    expect((dotted.body as InstanceResponse).instance.inputs).toEqual({
      "Stakeholder information": ["..notes.md", "docs/..draft.md"],
    });

    // A path inside, relative or absolute, is kept relative to the workspace.
    const inside = await api.post<InstanceResponse>("/api/instances", {
      process: "Requirements Clarification",
      inputs: {
        "Stakeholder information": [
          path.join(ws.root, "docs", "changes", "CHG-002", "stakeholders.md"),
        ],
      },
      outputs: { "Change brief": "./docs/changes/CHG-002/change-brief.md" },
    });
    expect(inside.status).toBe(201);
    expect((inside.body as InstanceResponse).instance).toMatchObject({
      inputs: { "Stakeholder information": ["docs/changes/CHG-002/stakeholders.md"] },
      outputs: { "Change brief": "docs/changes/CHG-002/change-brief.md" },
    });
  });

  test("E8 attachments are saved in the attachments directory under harmless names that are free there, all or none; too large (a file or a body), too many, other sites, and a directory outside the workspace, in .alps-harness/, or that is a file are refused; JSON bodies over 1 MiB are refused on every route", async () => {
    const { token } = daemon.info;
    const upload = async (
      files: { name: string; data: string | Uint8Array<ArrayBuffer> }[],
      headers: Record<string, string> = { "X-Harness-Token": token },
    ): Promise<{ status: number; body: AttachmentsResponse | Failure }> => {
      const form = new FormData();
      for (const file of files) form.append("files", new File([file.data], file.name));
      const response = await fetch(new URL(UPLOAD, daemon.url), {
        method: "POST",
        headers,
        body: form,
      });
      return { status: response.status, body: (await response.json()) as AttachmentsResponse };
    };
    const code = (reply: { body: AttachmentsResponse | Failure }): string | undefined =>
      "error" in reply.body ? reply.body.error.code : undefined;
    const folder = `inbox/${dayOf(Date.now())}`;
    const saved = (): string[] =>
      fs.existsSync(path.join(ws.root, folder))
        ? fs.readdirSync(path.join(ws.root, folder)).sort()
        : [];

    // The same checks as every route: another site, no token.
    const crossSite = await upload([{ name: "x.md", data: "x" }], {
      "X-Harness-Token": token,
      "Sec-Fetch-Site": "cross-site",
    });
    expect([crossSite.status, code(crossSite)]).toEqual([403, "cross-site"]);
    const anonymous = await upload([{ name: "x.md", data: "x" }], {});
    expect([anonymous.status, code(anonymous)]).toEqual([401, "unauthorized"]);
    expect(saved()).toEqual([]);

    // Only the last segment of a name is kept, without control characters, `..`, and leading
    // dots; a name taken that day gets -2. Nothing reaches the harness's records.
    const records = fs.readdirSync(path.join(ws.root, ".alps-harness")).sort();
    const sent = await upload([
      { name: "notes.md", data: "# Notes\n" },
      { name: "../../.alps-harness/state.json", data: "{}" },
      { name: ".env", data: "A=1\n" },
      { name: "a\u0001b.txt", data: "ab" },
      { name: "notes.md", data: "# Again\n" },
    ]);
    expect(sent.status).toBe(201);
    expect((sent.body as AttachmentsResponse).paths).toEqual([
      `${folder}/notes.md`,
      `${folder}/state.json`,
      `${folder}/env`,
      `${folder}/ab.txt`,
      `${folder}/notes-2.md`,
    ]);
    expect(fs.readFileSync(path.join(ws.root, folder, "notes-2.md"), "utf8")).toBe("# Again\n");
    expect(fs.readFileSync(path.join(ws.root, folder, "state.json"), "utf8")).toBe("{}");
    expect(fs.readdirSync(path.join(ws.root, ".alps-harness")).sort()).toEqual(records);

    // A part whose filename is empty is saved as attachment, with the other files of its upload.
    const unnamed = await upload([
      { name: "first.md", data: "# First\n" },
      { name: "", data: "no name" },
    ]);
    expect(unnamed.status).toBe(201);
    expect((unnamed.body as AttachmentsResponse).paths).toEqual([
      `${folder}/first.md`,
      `${folder}/attachment`,
    ]);
    expect(fs.readFileSync(path.join(ws.root, folder, "attachment"), "utf8")).toBe("no name");

    // Whatever is there takes its name, a symlink that leads nowhere too: the file is saved beside
    // it, and nothing is written through it.
    const nowhere = path.join(ws.base, "nowhere", "dangling.md");
    fs.symlinkSync(nowhere, path.join(ws.root, folder, "dangling.md"));
    const dangling = await upload([{ name: "dangling.md", data: "beside" }]);
    expect(dangling.status).toBe(201);
    expect((dangling.body as AttachmentsResponse).paths).toEqual([`${folder}/dangling-2.md`]);
    expect(fs.existsSync(nowhere)).toBe(false);

    // A name taken with each of -2 to -1000 is refused, before any file of the upload is written:
    // the files of an upload are saved all or none.
    for (let n = 1; n <= MAX_NAME_CANDIDATES; n++)
      fs.writeFileSync(path.join(ws.root, folder, n === 1 ? "same.md" : `same-${n}.md`), "");
    const taken = saved();
    const exhausted = await upload([
      { name: "fresh.md", data: "x" },
      { name: "same.md", data: "x" },
    ]);
    expect([exhausted.status, code(exhausted)]).toEqual([400, "invalid-request"]);
    expect((exhausted.body as Failure).error.message).toContain(
      `${folder}/ already holds same.md and that name with each of -2 to -${MAX_NAME_CANDIDATES}`,
    );
    expect(saved()).toEqual(taken);

    // Over 20 MB a file, over 10 files, or no file: refused, and nothing is written.
    const before = saved();
    const large = await upload([
      { name: "small.md", data: "x" },
      { name: "big.bin", data: new Uint8Array(MAX_ATTACHMENT_BYTES + 1) },
    ]);
    expect([large.status, code(large)]).toEqual([413, "too-large"]);
    expect((large.body as Failure).error.message).toContain("big.bin is larger than 20 MB");
    const many = await upload(
      Array.from({ length: MAX_ATTACHMENTS + 1 }, (_, i) => ({ name: `f${i}.md`, data: "x" })),
    );
    expect([many.status, code(many)]).toEqual([400, "invalid-request"]);
    const none = await upload([]);
    expect([none.status, code(none)]).toEqual([400, "invalid-request"]);
    // An upload is one attachment at its limit and the form around it (the WebUI sends one file
    // at a time): a body that says it is longer is refused before any of it is sent, and one that
    // does not say its length (chunked) is refused once read, no more of it kept than that.
    expect(
      await answerToHead(UPLOAD, "multipart/form-data; boundary=x", MAX_UPLOAD_BYTES + 1),
    ).toBe(413);
    const overlong = await fetch(new URL(UPLOAD, daemon.url), {
      method: "POST",
      headers: { "X-Harness-Token": token, "Content-Type": "multipart/form-data; boundary=x" },
      body: chunked("x".repeat(MAX_UPLOAD_BYTES + 1)),
    });
    expect([overlong.status, ((await overlong.json()) as Failure).error.code]).toEqual([
      413,
      "too-large",
    ]);
    expect(saved()).toEqual(before);

    // A JSON body over 1 MiB is refused on every route that reads one, the close of an MCP
    // session too: before it is read when it says its length, and once read when it does not
    // (chunked); the connection stays usable for the next request either way.
    expect(await answerToHead("/api/instances", "application/json", MAX_JSON_BYTES + 1)).toBe(413);
    const long = JSON.stringify({ process: "Solution Design", notes: "x".repeat(MAX_JSON_BYTES) });
    for (const route of ["/api/instances", "/api/sessions/s1/close"])
      for (const sized of [true, false]) {
        const huge = await fetch(new URL(route, daemon.url), {
          method: "POST",
          headers: { "X-Harness-Token": token, "Content-Type": "application/json" },
          body: sized ? long : chunked(long),
        });
        expect(huge.status, `${route} ${sized ? "sized" : "chunked"}`).toBe(413);
        expect(((await huge.json()) as Failure).error.code).toBe("too-large");
        expect((await send({ path: "/api/health", token })).status).toBe(200);
      }

    // The attachments directory must lie inside the workspace and outside .alps-harness/: a
    // configuration that says otherwise is an error of the file (no-model), and a directory that
    // leads out through a symlink is refused when a file would be saved.
    const config = path.join(ws.root, "alps-harness.yaml");
    const original = fs.readFileSync(config, "utf8");
    const configure = (attachments: string): void =>
      fs.writeFileSync(config, JSON.stringify({ ...JSON.parse(original), attachments }, null, 2));
    try {
      for (const [dir, words] of [
        [".alps-harness/inbox", "is in .alps-harness/"],
        ["../outside-inbox", "is outside the workspace"],
      ] as const) {
        configure(dir);
        const refused = await upload([{ name: "x.md", data: "x" }]);
        expect([refused.status, code(refused)], dir).toEqual([503, "no-model"]);
        expect((refused.body as Failure).error.message).toContain(`attachments: ${dir} ${words}`);
      }
      expect(fs.existsSync(path.join(ws.root, ".alps-harness", "inbox"))).toBe(false);
      expect(fs.existsSync(path.join(ws.base, "outside-inbox"))).toBe(false);
      const elsewhere = path.join(ws.base, "elsewhere-inbox");
      fs.mkdirSync(elsewhere);
      fs.symlinkSync(elsewhere, path.join(ws.root, "linked-inbox"));
      configure("linked-inbox/");
      const linked = await upload([{ name: "x.md", data: "x" }]);
      expect([linked.status, code(linked)]).toEqual([403, "outside-workspace"]);
      expect(fs.readdirSync(elsewhere)).toEqual([]);
      // A directory there cannot be a file: a configuration that names one is an error of the
      // file, and a file where the day's directory would be is refused when a file is saved.
      fs.writeFileSync(path.join(ws.root, "drop"), "a file\n");
      configure("drop");
      const file = await upload([{ name: "x.md", data: "x" }]);
      expect([file.status, code(file)]).toEqual([503, "no-model"]);
      expect((file.body as Failure).error.message).toContain(
        "attachments: drop cannot hold the files attached to requests: drop is not a directory",
      );
      const day = dayOf(Date.now());
      fs.mkdirSync(path.join(ws.root, "later"));
      fs.writeFileSync(path.join(ws.root, "later", day), "a file\n");
      configure("later/");
      const blocked = await upload([{ name: "x.md", data: "x" }]);
      expect([blocked.status, code(blocked)]).toEqual([503, "no-model"]);
      expect((blocked.body as Failure).error.message).toContain(
        `The attachments cannot be saved in later/${day}/`,
      );
    } finally {
      fs.writeFileSync(config, original);
    }
    expect((await upload([{ name: "after.md", data: "x" }])).status).toBe(201);
  });
});
