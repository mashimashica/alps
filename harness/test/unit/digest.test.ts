/*
 * The digest of an Artifact (evaluation records): the harness takes it again when the content
 * changes, even when a write keeps the modification time and the size, as `cp -p` and `touch -r`
 * do. Only the status-change time and the inode are left to tell.
 */

import { describe, expect, test } from "bun:test";
import crypto from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { DigestCache } from "../../src/harness/digest.ts";

const sha256 = (text: string): string => crypto.createHash("sha256").update(text).digest("hex");

describe("digests", () => {
  test("a rewrite that keeps the modification time and the size still changes the digest", () => {
    const root = fs.mkdtempSync(path.join(os.tmpdir(), "alps-harness-digest-"));
    try {
      const file = path.join(root, "change-brief.md");
      // A whole second, which the file system keeps exactly when it is set again.
      const time = Math.floor(Date.now() / 1000) - 60;
      fs.writeFileSync(file, "The export finishes within 10 s.\n");
      fs.utimesSync(file, time, time);
      const digests = new DigestCache(root);
      expect(digests.of("change-brief.md")).toBe(sha256("The export finishes within 10 s.\n"));

      // Past the coarsest clock tick of a file system, so that the status-change time moves.
      Bun.sleepSync(20);
      const before = fs.statSync(file);
      fs.writeFileSync(file, "The export finishes within 90 s.\n");
      fs.utimesSync(file, time, time);
      const after = fs.statSync(file);
      expect([after.mtimeMs, after.size]).toEqual([before.mtimeMs, before.size]);

      expect(digests.of("change-brief.md")).toBe(sha256("The export finishes within 90 s.\n"));
    } finally {
      fs.rmSync(root, { recursive: true, force: true });
    }
  });
});
