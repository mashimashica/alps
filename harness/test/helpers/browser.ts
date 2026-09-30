/*
 * Chromium for the tests that drive the WebUI (E8, E10), with a close that cannot hang a test.
 * Playwright's browser.close() waits for the browser process to end, and once it did not come
 * back for minutes after every assertion had passed. So closing has a limit: the contexts, then
 * the browser, within CLOSE_LIMIT_MS; past it, the browser's process group is killed, as
 * Playwright itself kills it (it starts the browser as the leader of a new group). In Playwright
 * 1.62 only a BrowserServer exposes its process, not the Browser that chromium.launch() returns,
 * so launchBrowser notes the process it started: the new child of this process that has
 * Playwright's debugging pipe.
 */

import { chromium, type Browser } from "playwright";
import { isAlive, waitFor } from "./process.ts";

/** How long closing a browser may take before its processes are killed. */
export const CLOSE_LIMIT_MS = 10_000;

/** The browser process of each browser that launchBrowser started and closeBrowser has not closed. */
const launched = new Map<Browser, number | null>();

/** The children of this process that are browsers Playwright started (`--remote-debugging-pipe`). */
function browserChildren(): number[] {
  if (process.platform === "win32") return [];
  const ps = Bun.spawnSync(["ps", "-ax", "-ww", "-o", "pid=,ppid=,command="]);
  return ps.stdout
    .toString()
    .split("\n")
    .flatMap((line) => {
      const match = /^\s*(\d+)\s+(\d+)\s+(.*)$/.exec(line);
      return match &&
        Number(match[2]) === process.pid &&
        match[3]?.includes("--remote-debugging-pipe")
        ? [Number(match[1])]
        : [];
    });
}

/** Kills a browser's process group (and the process, if it leads none). */
function kill(pid: number): void {
  for (const target of [-pid, pid]) {
    try {
      process.kill(target, "SIGKILL");
    } catch {
      // Already gone, or not a group.
    }
  }
}

/** Launches Chromium headless and notes its process, for closeBrowser and killStrayBrowsers. */
export async function launchBrowser(): Promise<Browser> {
  const before = new Set(browserChildren());
  const browser = await chromium.launch();
  const started = browserChildren().filter((pid) => !before.has(pid));
  launched.set(browser, started.length === 1 ? (started[0] ?? null) : null);
  return browser;
}

/**
 * Closes a browser that launchBrowser started: its contexts, then the browser (the order that
 * Playwright's documentation gives for a graceful close), within `limitMs`. Past the limit, it
 * kills the browser's processes and says so on stderr, since the page's assertions are done by
 * then and only the browser's own shutdown is stuck.
 */
export async function closeBrowser(browser: Browser, limitMs = CLOSE_LIMIT_MS): Promise<void> {
  const pid = launched.get(browser) ?? null;
  launched.delete(browser);
  const closing = (async () => {
    for (const context of browser.contexts()) await context.close();
    await browser.close();
  })();
  let timer: ReturnType<typeof setTimeout> | undefined;
  const late = new Promise<"late">((resolve) => {
    timer = setTimeout(() => resolve("late"), limitMs);
  });
  try {
    if ((await Promise.race([closing, late])) !== "late") return;
  } finally {
    clearTimeout(timer);
  }
  closing.catch(() => {});
  console.warn(
    `closeBrowser: the browser did not close within ${limitMs} ms; killing its processes (pid ${pid ?? "unknown"})`,
  );
  if (pid === null) return;
  kill(pid);
  await waitFor(() => !isAlive(pid), 5000, `browser ${pid} to end`).catch(() => {});
}

/** Kills the browsers that a failed or timed-out test did not close. */
export function killStrayBrowsers(): void {
  for (const pid of launched.values()) if (pid !== null) kill(pid);
  launched.clear();
}
