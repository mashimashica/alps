/*
 * Opening the WebUI in a browser without putting the token on a command line, where `ps` shows it
 * to every user of the machine: the URL goes into .alps-harness/open.html, which only the owner
 * can read (0600, like server.json), and the browser is given that file. The page sends the
 * browser on to the URL at once.
 */

import fs from "node:fs";
import path from "node:path";
import type { ServerInfo } from "../shared/types.ts";
import { openBrowser } from "./browser.ts";
import { openPagePath, uiUrl } from "./info.ts";

const escapeHtml = (text: string): string =>
  text.replace(/[&<>"']/g, (c) => `&#${c.charCodeAt(0)};`);

/** Writes the page that forwards to `url` (mode 0600) and returns its path. */
export function writeOpenPage(root: string, url: string): string {
  const file = openPagePath(root);
  fs.mkdirSync(path.dirname(file), { recursive: true });
  // The URL is the harness's own: http://127.0.0.1:<port>/#token=<hex>[&view=<name>].
  const html = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="referrer" content="no-referrer">
<title>ALPS Harness</title>
<script>location.replace(${JSON.stringify(url).replace(/</g, "\\u003c")});</script>
<meta http-equiv="refresh" content="0; url=${escapeHtml(url)}">
</head>
<body><p><a href="${escapeHtml(url)}">Open the ALPS harness</a></p></body>
</html>
`;
  const aside = `${file}.${process.pid}.tmp`;
  fs.writeFileSync(aside, html, { mode: 0o600 });
  fs.chmodSync(aside, 0o600);
  fs.renameSync(aside, file);
  return file;
}

/** Removes the page (when the server that it points to stops). */
export function removeOpenPage(root: string): void {
  try {
    fs.unlinkSync(openPagePath(root));
  } catch {
    // Never written, or already gone.
  }
}

/**
 * The WebUI's URL (token in the fragment), opened in a browser when asked. Resolves whether a
 * browser was started.
 */
export async function openUi(
  root: string,
  info: Pick<ServerInfo, "port" | "token">,
  options: { view?: string; open: boolean },
): Promise<{ url: string; opened: boolean }> {
  const url = uiUrl(info, options.view);
  if (!options.open) return { url, opened: false };
  const page = writeOpenPage(root, url);
  return { url, opened: await openBrowser(page) };
}
