/*
 * E8 (Plugin structure, safety): requests with another Host header, without the token, with a
 * path outside the workspace (or in its .alps-harness/), or with a body that is not JSON are
 * rejected. With them, what makes the WebUI safe to open: the token reaches the browser only in
 * the URL fragment, never on a command line (serve --open and open_ui hand the browser a page
 * that only the owner can read), the page and its chunks hold no secret, no other site can use
 * the API or frame the page, and the server listens on 127.0.0.1 only.
 */

import { afterAll, beforeAll, describe, expect, test } from "bun:test";
import fs from "node:fs";
import net from "node:net";
import os from "node:os";
import path from "node:path";
import { chromium } from "playwright";
import type {
  Failure,
  InstanceResponse,
  InstancesResponse,
  OpenResponse,
} from "../../src/shared/types.ts";
import { apiClient } from "../helpers/api.ts";
import { killStrayDaemons, startDaemon, type Daemon } from "../helpers/daemon.ts";
import { callTool, mcpClient, toolFailure } from "../helpers/mcp.ts";
import { records } from "../helpers/paths.ts";
import { isAlive, waitFor } from "../helpers/process.ts";
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
  { method: "POST", path: "/api/open" },
  { method: "GET", path: "/api/unknown" },
] as const;

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
});

afterAll(async () => {
  await daemon?.stop().catch(() => {});
  killStrayDaemons();
  ws?.dispose();
});

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
      expect(own.headers.get("content-security-policy"), target).toBe("frame-ancestors 'none'");
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
      const browser = await chromium.launch();
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
        await browser.close();
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
        expect(sent.headers.get("content-security-policy"), route.path).toBe(
          "frame-ancestors 'none'",
        );
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

  test("E8 a POST that is not JSON answers 415", async () => {
    const { token } = daemon.info;
    // No type, and the three that another site can send without a CORS preflight, to every POST route.
    for (const route of ROUTES.filter((r) => r.method === "POST"))
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
});
