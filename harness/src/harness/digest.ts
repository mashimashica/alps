/*
 * The SHA-256 of an Artifact's content: a file's bytes, or, for a directory, the paths and digests
 * of the files in it (as deep and as many as a scan reads). A run keeps the digests of its inputs,
 * and an evaluation of the run is stale once they differ (stale.ts). The digest decides; the path's
 * state (modification and status-change times, size, inode) only says when a digest cached for it
 * has to be taken again. The status-change time is in it because a write can keep the other two
 * (`cp -p`, `touch -r`), but not that.
 */

import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { MAX_DIR_FILES, MAX_DIR_LEVELS, SKIP_DIRS, fileState, signature } from "../model/index.ts";

const CHUNK_BYTES = 1024 * 1024;

function fileDigest(abs: string): string {
  const hash = crypto.createHash("sha256");
  const fd = fs.openSync(abs, "r");
  try {
    const buffer = Buffer.allocUnsafe(CHUNK_BYTES);
    for (;;) {
      const read = fs.readSync(fd, buffer, 0, CHUNK_BYTES, null);
      if (read === 0) break;
      hash.update(buffer.subarray(0, read));
    }
  } finally {
    fs.closeSync(fd);
  }
  return hash.digest("hex");
}

function dirDigest(abs: string): string {
  const hash = crypto.createHash("sha256");
  let count = 0;
  const walk = (dir: string, relative: string, depth: number): void => {
    let entries: fs.Dirent[];
    try {
      entries = fs.readdirSync(dir, { withFileTypes: true });
    } catch {
      return;
    }
    for (const entry of entries.sort((a, b) => (a.name < b.name ? -1 : a.name > b.name ? 1 : 0))) {
      if (SKIP_DIRS.has(entry.name) || count >= MAX_DIR_FILES) continue;
      const child = path.join(dir, entry.name);
      const name = relative ? `${relative}/${entry.name}` : entry.name;
      if (entry.isFile()) {
        count += 1;
        try {
          hash.update(`${name}\0${fileDigest(child)}\n`);
        } catch {
          // A file removed while reading is not part of the content.
        }
      } else if (entry.isDirectory() && depth < MAX_DIR_LEVELS) walk(child, name, depth + 1);
    }
  };
  walk(abs, "", 0);
  return hash.digest("hex");
}

/** Digests of workspace paths, taken again whenever a path's state (its signature) changes. */
export class DigestCache {
  readonly #root: string;
  readonly #known = new Map<string, { signature: string; sha256: string | null }>();

  constructor(root: string) {
    this.#root = root;
  }

  /** The digest of a workspace-relative path now; `null` when nothing is there or it cannot be read. */
  of(relPath: string): string | null {
    const state = fileState(this.#root, relPath);
    if (!state) {
      this.#known.delete(relPath);
      return null;
    }
    const current = signature(state);
    const known = this.#known.get(relPath);
    if (known?.signature === current) return known.sha256;
    let sha256: string | null;
    try {
      const abs = path.join(this.#root, relPath);
      sha256 = state.dir ? dirDigest(abs) : fileDigest(abs);
    } catch {
      sha256 = null;
    }
    this.#known.set(relPath, { signature: current, sha256 });
    return sha256;
  }
}
