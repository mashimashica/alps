/* Opening the WebUI in the user's browser (`serve --open`). */

import { spawn } from "node:child_process";

/**
 * The command that opens a URL: the BROWSER environment variable when set (a command, given the
 * URL as its only argument; `none` opens nothing), otherwise the platform's opener.
 */
function opener(url: string): [string, string[]] | null {
  const browser = process.env.BROWSER?.trim();
  if (browser === "none") return null;
  if (browser) return [browser, [url]];
  if (process.platform === "darwin") return ["open", [url]];
  if (process.platform === "win32") return ["cmd", ["/c", "start", "", url]];
  return ["xdg-open", [url]];
}

/**
 * Starts the browser detached from this process. Resolves false when it could not be started;
 * BROWSER=none is not a failure.
 */
export function openBrowser(url: string): Promise<boolean> {
  const command = opener(url);
  if (!command) return Promise.resolve(true);
  return new Promise((resolve) => {
    try {
      const child = spawn(command[0], command[1], {
        detached: true,
        stdio: "ignore",
        windowsHide: true,
      });
      child.once("error", () => resolve(false));
      child.once("spawn", () => {
        child.unref();
        resolve(true);
      });
    } catch {
      resolve(false);
    }
  });
}
