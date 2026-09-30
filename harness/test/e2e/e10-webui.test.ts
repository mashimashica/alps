/*
 * E10 (screen design): opening / in a browser shows the WebUI. The server bundles the TSX when it
 * starts, so a UI that does not bundle stops the start, and what it serves does not depend on the
 * current directory. The page reads the token once from the URL fragment and keeps it in
 * sessionStorage, so that it survives a reload. The network draws the ring of 11 Processes and 15
 * pills; a pill opens the focus view and a blank click returns; the marks on the ring follow the
 * runs through SSE. The switch at the top right shows the page in Japanese, what the harness itself
 * said in a run included. The request box, the main action, starts a wake with a fake agent: the
 * file dropped on it is uploaded, the wake's record shows the request and the attachment, and the
 * board gains the instance that the agent makes, which links back to the wake.
 */

import { afterAll, describe, expect, test } from "bun:test";
import fs from "node:fs";
import path from "node:path";
import type { Browser, Page } from "playwright";
import { dayOf } from "../../src/shared/requests.ts";
import type {
  InstanceResponse,
  RunDetailResponse,
  RunStartResponse,
} from "../../src/shared/types.ts";
import { apiClient } from "../helpers/api.ts";
import { closeBrowser, killStrayBrowsers, launchBrowser } from "../helpers/browser.ts";
import { killStrayDaemons, startDaemon } from "../helpers/daemon.ts";
import { FAKES, HARNESS_ROOT, serverJson } from "../helpers/paths.ts";
import { exec, HOOK_TIMEOUT_MS, processCwd } from "../helpers/process.ts";
import { copyHarness, tmpWorkspace, type TmpWorkspace } from "../helpers/workspace.ts";

const workspaces: TmpWorkspace[] = [];
const workspace = (): TmpWorkspace => {
  const ws = tmpWorkspace();
  workspaces.push(ws);
  return ws;
};

afterAll(() => {
  killStrayBrowsers();
  killStrayDaemons();
  for (const ws of workspaces) ws.dispose();
}, HOOK_TIMEOUT_MS);

const serverLog = (root: string): string => path.join(root, ".alps-harness", "server.log");

/**
 * Opens the WebUI and collects what goes wrong on the page: console errors, page errors, and
 * failed responses. `locale` sets the browser's language, which the page starts in.
 */
async function openPage(
  browser: Browser,
  url: string,
  locale?: string,
): Promise<{ tab: Page; problems: string[] }> {
  const tab = await browser.newPage({ viewport: { width: 1280, height: 800 }, locale });
  const problems: string[] = [];
  tab.on("console", (message) => {
    if (message.type() === "error") problems.push(`console: ${message.text()}`);
  });
  tab.on("pageerror", (error) => problems.push(`page: ${error.message}`));
  tab.on("response", (response) => {
    if (response.status() >= 400) problems.push(`${response.status()} ${response.url()}`);
  });
  const response = await tab.goto(url);
  expect(response?.status()).toBe(200);
  return { tab, problems };
}

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

        const browser = await launchBrowser();
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
          await closeBrowser(browser);
        }
      } finally {
        await daemon.stop();
      }
    },
    { timeout: 60_000 },
  );

  test(
    "E10 the token is read once from the fragment and kept in sessionStorage, so that it survives a reload",
    async () => {
      const ws = workspace();
      const daemon = await startDaemon(ws.root, [], { cwd: "/" });
      const browser = await launchBrowser();
      try {
        const { tab, problems } = await openPage(browser, daemon.uiUrl);
        const healthy = async (): Promise<void> => {
          await tab
            .locator('[data-testid="health"][data-status="ok"]')
            .waitFor({ timeout: 10_000 });
          expect(await tab.getByTestId("health").textContent()).toContain(`pid ${daemon.info.pid}`);
        };
        const kept = (): Promise<string[]> => tab.evaluate(() => Object.values(sessionStorage));
        await healthy();
        // Read once: the token left the address bar and is kept in the tab's sessionStorage.
        expect(tab.url()).toBe(daemon.url);
        expect(await kept()).toContain(daemon.info.token);

        // The reloaded page has no fragment to read; the kept token still reaches the API.
        await tab.reload();
        expect(tab.url()).toBe(daemon.url);
        await healthy();
        expect(await kept()).toContain(daemon.info.token);
        expect(problems).toEqual([]);

        // A new tab of another context, opened without the fragment, has no token.
        const fresh = await (await browser.newContext()).newPage();
        expect((await fresh.goto(daemon.url))?.status()).toBe(200);
        await fresh
          .locator('[data-testid="health"][data-status="error"]')
          .waitFor({ timeout: 10_000 });
        expect(await fresh.evaluate(() => Object.values(sessionStorage))).not.toContain(
          daemon.info.token,
        );
      } finally {
        await closeBrowser(browser);
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

  test(
    "E10 the ring draws 11 processes and 15 pills; a pill opens the focus view and a blank click returns",
    async () => {
      const ws = workspace();
      const daemon = await startDaemon(ws.root, [], { cwd: "/" });
      const browser = await launchBrowser();
      try {
        const { tab, problems } = await openPage(browser, daemon.uiUrl);
        const ring = tab.getByTestId("ring");
        await ring.waitFor({ timeout: 10_000 });
        // The outer ring holds the model's Processes, the pills inside its Artifact types.
        expect(await ring.locator("[data-process]").count()).toBe(11);
        expect(await ring.locator("[data-type]").count()).toBe(15);
        expect(await ring.locator('[data-process="Solution Design"]').textContent()).toBe(
          "Solution Design",
        );

        // A pill opens the focus view of its type: the Processes that produce it and those that read it.
        await ring.locator('[data-type="Change brief"]').click();
        const focus = tab.locator('[data-testid="focus"][data-focus-kind="type"]');
        await focus.waitFor({ timeout: 5000 });
        expect(await focus.getAttribute("data-focus-id")).toBe("Change brief");
        expect(await tab.getByTestId("ring").count()).toBe(0);
        expect(await focus.locator('[data-node^="process:"]').count()).toBe(6);
        await tab.locator('[data-testid="panel-type"][data-type="Change brief"]').waitFor();

        // A Process there moves the focus to it: its five columns.
        await focus.locator('[data-node="process:Solution Design"]').click();
        const processFocus = tab.locator(
          '[data-testid="focus"][data-focus-kind="process"][data-focus-id="Solution Design"]',
        );
        await processFocus.waitFor({ timeout: 5000 });
        expect(await processFocus.locator(".column-title").count()).toBe(5);
        // Requirements Clarification and Feasibility Assessment produce the Change brief it reads;
        // Change Implementation uses the Design description it produces.
        expect(await processFocus.locator("[data-node]").count()).toBe(6);
        await tab
          .locator('[data-testid="panel-process"][data-process="Solution Design"]')
          .waitFor();

        // A click on the background returns to the whole ring.
        await tab.getByTestId("backdrop").click({ position: { x: 5, y: 5 } });
        await tab.getByTestId("ring").waitFor({ timeout: 5000 });
        expect(await tab.getByTestId("focus").count()).toBe(0);
        expect(problems).toEqual([]);
      } finally {
        await closeBrowser(browser);
        await daemon.stop();
      }
    },
    { timeout: 60_000 },
  );

  test(
    "E10 starting a run changes the ring marks through SSE",
    async () => {
      const ws = tmpWorkspace({
        agents: {
          "claude-code": {
            command: path.join(FAKES, "claude.ts"),
            env: { ALPS_FAKE_SCENARIO: "slow", ALPS_FAKE_DELAY_MS: "400" },
          },
        },
      });
      workspaces.push(ws);
      const daemon = await startDaemon(ws.root, [], { cwd: "/" });
      const api = apiClient(daemon);
      const brief = "docs/changes/CHG-001/change-brief.md";
      const { instance } = await api.ok<InstanceResponse>("POST", "/api/instances", {
        process: "Solution Design",
        inputs: { "Change brief": [brief] },
        outputs: { "Design description": "docs/changes/CHG-001/design/" },
      });
      const browser = await launchBrowser();
      try {
        const { tab, problems } = await openPage(browser, daemon.uiUrl);
        const mark = (name: string, value: boolean) =>
          tab.locator(
            `[data-testid="ring"] [data-process="Solution Design"][data-${name}="${value}"]`,
          );
        await mark("running", false).waitFor({ timeout: 10_000 });
        await mark("stale", false).waitFor();

        // The run starts elsewhere (as an MCP client starts one): the page hears of it on the event
        // stream and puts the dashed ring around the Process, until the run ends.
        const { run } = await api.ok<RunStartResponse>(
          "POST",
          `/api/instances/${instance.id}/run`,
          {
            agent: "claude-code",
          },
        );
        await mark("running", true).waitFor({ timeout: 10_000 });
        expect(await tab.getByTestId("running-count").getAttribute("data-count")).toBe("1");
        await mark("running", false).waitFor({ timeout: 30_000 });
        expect(await tab.getByTestId("running-count").getAttribute("data-count")).toBe("0");

        // Once the judged input changes on disk, the amber ring appears.
        await api.ok<InstanceResponse>("POST", `/api/instances/${instance.id}/evaluate`, {
          judgments: [
            { outcome: 0, judgment: "achieved", evidence: `Read the output of ${run.id}.` },
          ],
        });
        expect(await mark("stale", false).count()).toBe(1);
        fs.appendFileSync(path.join(ws.root, brief), "\n- Search results show the stock level.\n");
        await mark("stale", true).waitFor({ timeout: 10_000 });
        expect(await tab.getByTestId("stale-count").getAttribute("data-count")).toBe("1");
        expect(problems).toEqual([]);
      } finally {
        await closeBrowser(browser);
        await daemon.stop();
      }
    },
    { timeout: 90_000 },
  );

  test(
    "E10 the language switch at the top right shows a run in Japanese, with what the harness itself said in it: the end of its log and its error",
    async () => {
      // The fake Codex exits with code 3 without a word, so only the harness says why it failed.
      const ws = tmpWorkspace({
        agents: {
          codex: { command: path.join(FAKES, "codex.ts"), env: { ALPS_FAKE_SCENARIO: "exit" } },
        },
      });
      workspaces.push(ws);
      const daemon = await startDaemon(ws.root, [], { cwd: "/" });
      const api = apiClient(daemon);
      const { instance } = await api.ok<InstanceResponse>("POST", "/api/instances", {
        process: "Solution Design",
        inputs: { "Change brief": ["docs/changes/CHG-001/change-brief.md"] },
        outputs: { "Design description": "docs/changes/CHG-001/design/" },
      });
      const { run } = await api.ok<RunStartResponse>("POST", `/api/instances/${instance.id}/run`, {
        agent: "codex",
      });
      const ended = await api.ok<RunDetailResponse>("GET", `/api/runs/${run.id}?wait=30`);
      expect(ended.run.status).toBe("failed");
      const browser = await launchBrowser();
      try {
        // The browser's language is English, so the page starts in English.
        const { tab, problems } = await openPage(browser, daemon.uiUrl, "en-US");
        await tab.locator('[role="tab"][data-view="instances"]').click();
        await tab.locator(`button[data-instance="${instance.id}"]`).click();
        await tab
          .getByTestId("panel-instance")
          .getByRole("button", { name: run.id, exact: true })
          .first()
          .click();
        const panel = tab.locator(`[data-testid="panel-run"][data-run="${run.id}"]`);
        const log = panel.getByTestId("run-log");
        const error = panel.getByTestId("run-error");
        await log.filter({ hasText: "Failed (" }).waitFor({ timeout: 10_000 });
        expect(await log.textContent()).toMatch(/ end\s+Failed \(\d+ s\)/);
        expect(await log.textContent()).toContain("Started Codex (codex-cli 0.999.0)");
        expect(await error.textContent()).toBe("Codex exited with code 3.");

        // After the switch the harness's own lines and the run's error are in Japanese.
        await tab.locator("header button.language").click();
        await log.filter({ hasText: "異常終了" }).waitFor({ timeout: 5000 });
        expect(await log.textContent()).toMatch(/ end\s+異常終了（\d+ 秒）/);
        expect(await log.textContent()).toContain("Codex（codex-cli 0.999.0）を起動した");
        expect(await log.textContent()).not.toContain("Failed (");
        expect(await error.textContent()).toBe("Codex は終了コード 3 で終わった。");
        expect(await tab.locator('[role="tab"][data-view="instances"]').textContent()).toBe(
          "ボード",
        );
        expect(problems).toEqual([]);
      } finally {
        await closeBrowser(browser);
        await daemon.stop();
      }
    },
    { timeout: 60_000 },
  );

  test(
    "E10 a request from the request box starts a wake: its record shows in the panel, and the board gains the instance that the agent makes, which links back to the wake",
    async () => {
      // The fake wake agent serves the request: it instantiates the Process the request names with
      // the attachment as its input, runs it with the demo agent, and reports (test/fakes).
      const ws = tmpWorkspace({
        agents: {
          "claude-code": {
            command: path.join(FAKES, "wake-agent.ts"),
            env: { ALPS_FAKE_SCENARIO: "ok" },
          },
        },
      });
      workspaces.push(ws);
      const daemon = await startDaemon(ws.root, [], { cwd: "/" });
      const browser = await launchBrowser();
      try {
        const { tab, problems } = await openPage(browser, daemon.uiUrl, "en-US");
        await tab.locator('[data-testid="health"][data-status="ok"]').waitFor({ timeout: 10_000 });
        await tab.getByTestId("request-open").click();
        const box = tab.getByTestId("request");
        await box.waitFor({ timeout: 5000 });
        const request = "Clarify the requirements of CHG-002 from the memo.";
        await box.getByTestId("request-text").fill(request);
        await box.locator('[data-process="Requirements Clarification"] input').check();
        // A file dropped on the box is attached; it is uploaded when the request is sent.
        const dropped = await tab.evaluateHandle(() => {
          const data = new DataTransfer();
          data.items.add(new File(["# Memo\n"], "memo.md", { type: "text/markdown" }));
          return data;
        });
        await box.getByTestId("request-drop").dispatchEvent("drop", { dataTransfer: dropped });
        await box.getByTestId("request-attachments").getByText("memo.md").waitFor();
        await box.getByRole("button", { name: "Send request" }).click();

        // The box closes on the board, and the panel shows the wake's record: the request as given,
        // and the attachment where the upload saved it.
        const wake = tab.getByTestId("panel-run");
        await wake.waitFor({ timeout: 10_000 });
        const id = (await wake.getAttribute("data-run")) ?? "";
        expect(id).toMatch(/^r\d+$/);
        expect(await tab.getByTestId("request").count()).toBe(0);
        expect(
          await tab.locator('[role="tab"][data-view="instances"]').getAttribute("aria-selected"),
        ).toBe("true");
        expect(await wake.getByTestId("wake-request").textContent()).toBe(request);
        const attachment = `inbox/${dayOf(Date.now())}/memo.md`;
        expect(await wake.getByTestId("wake-attachments").textContent()).toContain(attachment);
        expect(fs.readFileSync(path.join(ws.root, attachment), "utf8")).toBe("# Memo\n");

        // The instance that the agent makes reaches the board through SSE, with a link to the wake.
        const card = tab.locator("button.instance-card");
        await card.first().waitFor({ timeout: 20_000 });
        expect(await card.count()).toBe(1);
        const origin = tab.locator(`.instance-card-origin[data-origin="${id}"]`);
        await origin.waitFor({ timeout: 5000 });
        // The wake ends with the report of its plan; it lists the instance it made and the run.
        await tab
          .locator(`[data-testid="panel-run"][data-run="${id}"][data-status="succeeded"]`)
          .waitFor({ timeout: 30_000 });
        expect(await wake.getByTestId("made-instances").locator("[data-instance]").count()).toBe(1);
        expect(await wake.getByTestId("started-runs").locator("li").count()).toBe(1);
        const made = await card.first().getAttribute("data-instance");
        expect(await wake.textContent()).toContain(
          `Planned Requirements Clarification as ${made} because the request names it.`,
        );
        // The card opens the instance, which names the wake; the card's link opens the wake again.
        await card.first().click();
        await tab.getByTestId("panel-instance").waitFor({ timeout: 5000 });
        expect(await tab.getByTestId("instance-origin").textContent()).toBe(id);
        await origin.click();
        await tab.locator(`[data-testid="panel-run"][data-run="${id}"]`).waitFor({ timeout: 5000 });
        expect(problems).toEqual([]);
      } finally {
        await closeBrowser(browser);
        await daemon.stop();
      }
    },
    { timeout: 90_000 },
  );
});
