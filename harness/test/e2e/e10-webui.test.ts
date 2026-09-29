/*
 * E10 (screen design): opening / in a browser shows the WebUI. The server bundles the TSX when it
 * starts, so a UI that does not bundle stops the start, and what it serves does not depend on the
 * current directory. The ring of 11 processes and 15 pills, the focus view, and SSE updates come
 * with the screens (stage 4).
 */

import { afterAll, describe, expect, test } from "bun:test";
import fs from "node:fs";
import path from "node:path";
import { chromium } from "playwright";
import { killStrayDaemons, startDaemon } from "../helpers/daemon.ts";
import { HARNESS_ROOT, serverJson } from "../helpers/paths.ts";
import { exec, processCwd } from "../helpers/process.ts";
import { copyHarness, tmpWorkspace, type TmpWorkspace } from "../helpers/workspace.ts";

const workspaces: TmpWorkspace[] = [];
const workspace = (): TmpWorkspace => {
  const ws = tmpWorkspace();
  workspaces.push(ws);
  return ws;
};

afterAll(() => {
  killStrayDaemons();
  for (const ws of workspaces) ws.dispose();
});

const serverLog = (root: string): string => path.join(root, ".alps-harness", "server.log");

/** Whether `dir` is `ancestor` or inside it. */
const within = (dir: string, ancestor: string): boolean => {
  const relative = path.relative(ancestor, dir);
  return relative === "" || (!relative.startsWith("..") && !path.isAbsolute(relative));
};

/** The same-origin scripts and stylesheets a page loads. */
const assetPaths = (html: string): string[] =>
  [...html.matchAll(/<(?:script|link)\b[^>]*?\b(?:src|href)="(\/[^"]*)"/g)].map((m) => m[1] ?? "");

describe("E10 WebUI", () => {
  test(
    "E10 the production daemon bundles the TSX at startup, serves / and its chunks from an unrelated directory, and the page shows its heading without console errors",
    async () => {
      const ws = workspace();
      // Started from /, the daemon runs in the workspace root, which is not an ancestor of src/ui/.
      const daemon = await startDaemon(ws.root, [], { cwd: "/" });
      try {
        const cwd = processCwd(daemon.info.pid);
        if (cwd !== null) {
          expect(cwd).toBe(fs.realpathSync(ws.root));
          expect(within(fs.realpathSync(path.join(HARNESS_ROOT, "src", "ui")), cwd)).toBe(false);
        }
        // The bundle was made when the server started, before anything but /api/health was requested.
        expect(fs.readFileSync(serverLog(ws.root), "utf8")).toMatch(
          /bundled the WebUI in \d+ ms \(\d+ files, [\d.]+ KiB\)/,
        );

        // The page and every chunk it loads are served; the TSX source is not referenced.
        const page = await fetch(daemon.url);
        expect(page.status).toBe(200);
        const html = await page.text();
        expect(html).not.toContain("main.tsx");
        const assets = assetPaths(html);
        expect(assets.length).toBeGreaterThan(0);
        for (const asset of assets) {
          const response = await fetch(new URL(asset, daemon.url));
          expect(response.status, asset).toBe(200);
          expect(response.headers.get("content-type") ?? "", asset).toMatch(/javascript|css/);
        }

        const browser = await chromium.launch();
        try {
          const tab = await browser.newPage();
          const problems: string[] = [];
          tab.on("console", (message) => {
            if (message.type() === "error") problems.push(`console: ${message.text()}`);
          });
          tab.on("pageerror", (error) => problems.push(`page: ${error.message}`));
          tab.on("response", (response) => {
            if (response.status() >= 400) problems.push(`${response.status()} ${response.url()}`);
          });

          // The URL that serve printed, with the token in the fragment.
          const response = await tab.goto(daemon.uiUrl);
          expect(response?.status()).toBe(200);

          // Preact renders the heading, and the page reaches the API with the per-start token.
          expect(await tab.locator("h1").textContent({ timeout: 10_000 })).toBe("ALPS Harness");
          await tab
            .locator('[data-testid="health"][data-status="ok"]')
            .waitFor({ timeout: 10_000 });
          expect(await tab.getByTestId("health").textContent()).toContain(`pid ${daemon.info.pid}`);
          // The page took the token from the fragment and removed it from the address bar.
          expect(tab.url()).toBe(daemon.url);
          expect(problems).toEqual([]);
        } finally {
          await browser.close();
        }
      } finally {
        await daemon.stop();
      }
    },
    { timeout: 60_000 },
  );

  test(
    "E10 a main.tsx that does not bundle makes the start fail, not the first request",
    async () => {
      const ws = workspace();
      const cli = copyHarness(ws.base);
      fs.appendFileSync(
        path.join(path.dirname(cli), "ui", "main.tsx"),
        "\nexport const broken: number = ;\n",
      );

      // The daemon ends before it listens; serve --daemon reports why from server.log.
      const daemon = await exec([process.execPath, cli, "serve", "--daemon", ws.root], {
        cwd: "/",
      });
      expect(daemon.code).toBe(1);
      expect(daemon.stderr).toContain("Cannot bundle the WebUI");
      expect(daemon.stderr).toMatch(/main\.tsx:\d+:\d+: Unexpected/);
      expect(daemon.stdout).not.toContain("http://127.0.0.1");
      expect(fs.readFileSync(serverLog(ws.root), "utf8")).toMatch(/main\.tsx:\d+:\d+: Unexpected/);
      expect(fs.existsSync(serverJson(ws.root))).toBe(false);

      // In the foreground, serve exits with the error instead of listening.
      const foreground = await exec([process.execPath, cli, "serve", ws.root], {
        cwd: "/",
        timeoutMs: 20_000,
      });
      expect(foreground.code).toBe(1);
      expect(foreground.stderr).toMatch(/main\.tsx:\d+:\d+: Unexpected/);
      expect(foreground.stdout).not.toContain("http://127.0.0.1");
      expect(fs.existsSync(serverJson(ws.root))).toBe(false);
    },
    { timeout: 60_000 },
  );

  test.todo("E10 the ring draws 11 processes and 15 pills; a pill opens the focus view and a blank click returns", () => {});
  test.todo("E10 starting a run changes the ring marks through SSE", () => {});
});
