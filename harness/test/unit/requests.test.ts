/*
 * The files attached to a request (shared/requests.ts, model/load.ts): their names made harmless,
 * where each is saved (a directory for the day, -2 and -3 for a name taken there, up to -1000),
 * and which attachments directories a workspace may configure.
 */

import { describe, expect, test } from "bun:test";
import path from "node:path";
import { attachmentsLocation } from "../../src/model/index.ts";
import {
  attachmentPath,
  dayOf,
  FALLBACK_NAME,
  freeName,
  MAX_NAME_CANDIDATES,
  safeFileName,
} from "../../src/shared/requests.ts";

const bytes = (text: string): number => new TextEncoder().encode(text).length;

describe("attachment names", () => {
  test("only the last segment is kept, without control characters, `..`, and leading dots", () => {
    expect(safeFileName("notes.md")).toBe("notes.md");
    expect(safeFileName("../../.alps-harness/state.json")).toBe("state.json");
    expect(safeFileName("C:\\Users\\me\\report.pdf")).toBe("report.pdf");
    expect(safeFileName(".env")).toBe("env");
    expect(safeFileName("...hidden")).toBe("hidden");
    expect(safeFileName("a..b.txt")).toBe("ab.txt");
    expect(safeFileName("in\u0000voi\u001fce\u007f\u0085.md")).toBe("invoice.md");
    expect(safeFileName("  spaced name.md ")).toBe("spaced name.md");
    expect(safeFileName("日本語のメモ.md")).toBe("日本語のメモ.md");
  });

  test("a name that leaves nothing becomes attachment", () => {
    for (const given of ["", "..", "...", "/", "docs/", "\u0001", ". . ."])
      expect(safeFileName(given), JSON.stringify(given)).toBe(FALLBACK_NAME);
  });

  test("a long name is cut to 200 bytes before its extension, without splitting a character", () => {
    const name = safeFileName(`${"あ".repeat(100)}.md`);
    expect(bytes(name)).toBeLessThanOrEqual(200);
    expect(name).toMatch(/^あ+\.md$/);
    expect(safeFileName("x".repeat(300))).toBe("x".repeat(200));
  });
});

describe("where an attachment is saved", () => {
  test("in the day's directory under the attachments directory", () => {
    expect(attachmentPath("inbox/", "2026-10-01", "notes.md", () => false)).toBe(
      "inbox/2026-10-01/notes.md",
    );
    expect(attachmentPath("docs/requests/", "2026-10-01", "../x.md", () => false)).toBe(
      "docs/requests/2026-10-01/x.md",
    );
    // The workspace itself as the attachments directory.
    expect(attachmentPath("", "2026-10-01", ".env", () => false)).toBe("2026-10-01/env");
  });

  test("a name taken there gets -2, -3, … before its extension; another day's is not in the way", () => {
    const taken = new Set(["inbox/2026-10-01/notes.md", "inbox/2026-10-01/notes-2.md"]);
    const isTaken = (p: string): boolean => taken.has(p);
    expect(attachmentPath("inbox/", "2026-10-01", "notes.md", isTaken)).toBe(
      "inbox/2026-10-01/notes-3.md",
    );
    expect(attachmentPath("inbox/", "2026-10-02", "notes.md", isTaken)).toBe(
      "inbox/2026-10-02/notes.md",
    );
    expect(freeName("env", (name) => name === "env")).toBe("env-2");
    expect(freeName("archive.tar.gz", (name) => name === "archive.tar.gz")).toBe(
      "archive.tar-2.gz",
    );
  });

  test("the names end at -1000: when all are taken there is none", () => {
    const asked: string[] = [];
    const all = (name: string): boolean => {
      asked.push(name);
      return true;
    };
    expect(freeName("notes.md", all)).toBeNull();
    expect(asked).toHaveLength(MAX_NAME_CANDIDATES);
    expect(asked.at(-1)).toBe(`notes-${MAX_NAME_CANDIDATES}.md`);
    expect(freeName("notes.md", (name) => name !== `notes-${MAX_NAME_CANDIDATES}.md`)).toBe(
      `notes-${MAX_NAME_CANDIDATES}.md`,
    );
    expect(attachmentPath("inbox/", "2026-10-01", "notes.md", () => true)).toBeNull();
  });

  test("the day is the local date", () => {
    expect(dayOf(new Date(2026, 0, 5, 23, 59).getTime())).toBe("2026-01-05");
    expect(dayOf(new Date(2026, 11, 31, 0, 0).getTime())).toBe("2026-12-31");
  });
});

describe("the attachments directory", () => {
  const root = path.resolve("/tmp/workspace");

  test("inbox/ unless one is configured, relative to the workspace with a trailing slash", () => {
    expect(attachmentsLocation(root, undefined)).toEqual({ ok: true, dir: "inbox/" });
    expect(attachmentsLocation(root, "docs/requests")).toEqual({ ok: true, dir: "docs/requests/" });
    expect(attachmentsLocation(root, "./docs/../drop/")).toEqual({ ok: true, dir: "drop/" });
    expect(attachmentsLocation(root, path.join(root, "drop"))).toEqual({ ok: true, dir: "drop/" });
    expect(attachmentsLocation(root, ".")).toEqual({ ok: true, dir: "" });
    // A name that merely starts with two dots stays inside.
    expect(attachmentsLocation(root, "..inbox")).toEqual({ ok: true, dir: "..inbox/" });
  });

  test("one outside the workspace or in .alps-harness/ cannot be used", () => {
    for (const given of ["..", "../inbox", "/etc", "docs/../../inbox"])
      expect(attachmentsLocation(root, given), given).toEqual({ ok: false, reason: "outside" });
    for (const given of [
      ".alps-harness",
      ".alps-harness/inbox",
      ".ALPS-HARNESS/inbox",
      "docs/../.alps-harness/inbox",
    ])
      expect(attachmentsLocation(root, given), given).toEqual({ ok: false, reason: "records" });
  });
});
