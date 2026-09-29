/*
 * The WebUI bundle. At startup, Bun.build() bundles src/ui/index.html and the TSX it loads in
 * memory (nothing is written to disk), and the server's own fetch handler serves the outputs, so
 * the Host check and the security headers cover the page and its chunks as they cover the API.
 * A UI that does not bundle stops the server from starting instead of failing the first request.
 * Nothing here depends on the current directory.
 */

import path from "node:path";
import { fileURLToPath } from "node:url";

/** The WebUI's entry point. */
export const UI_ENTRY = fileURLToPath(new URL("../ui/index.html", import.meta.url));

export interface UiAsset {
  body: Blob;
  /** The media type, with its charset. */
  type: string;
}

export interface UiBundle {
  /** The bundled files by URL path; the page itself is `/`. */
  assets: ReadonlyMap<string, UiAsset>;
  /** How long bundling took. */
  ms: number;
  /** The total size of the bundled files. */
  bytes: number;
}

/** The WebUI does not bundle, for example because main.tsx has a syntax error. */
export class UiBuildError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "UiBuildError";
  }
}

type BuildLog = Awaited<ReturnType<typeof Bun.build>>["logs"][number];

const formatLog = ({ message, position }: BuildLog): string =>
  position ? `${position.file}:${position.line}:${position.column}: ${message}` : message;

export async function bundleUi(): Promise<UiBundle> {
  const started = performance.now();
  let result: Awaited<ReturnType<typeof Bun.build>>;
  try {
    result = await Bun.build({
      entrypoints: [UI_ENTRY],
      target: "browser",
      minify: true,
      // Chunk URLs are absolute (/chunk-….js), whatever path the page is opened at.
      publicPath: "/",
      // Nothing from the server's environment is inlined into what the browser receives.
      env: "disable",
      throw: false,
    });
  } catch (error) {
    throw new UiBuildError(`Cannot bundle the WebUI (${UI_ENTRY}): ${(error as Error).message}`);
  }
  if (!result.success) {
    const errors = result.logs.filter((log) => log.level === "error");
    const lines = (errors.length > 0 ? errors : result.logs).map(formatLog);
    throw new UiBuildError(`Cannot bundle the WebUI (${UI_ENTRY}):\n  ${lines.join("\n  ")}`);
  }

  const page = path.basename(UI_ENTRY);
  const assets = new Map<string, UiAsset>();
  let bytes = 0;
  for (const output of result.outputs) {
    const name = output.path.replace(/^\.\//, "");
    assets.set(name === page ? "/" : `/${name}`, { body: output, type: output.type });
    bytes += output.size;
  }
  if (!assets.has("/")) throw new UiBuildError(`Bundling ${UI_ENTRY} produced no page.`);
  return { assets, ms: performance.now() - started, bytes };
}
