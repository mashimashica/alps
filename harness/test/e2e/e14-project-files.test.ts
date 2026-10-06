import { afterAll, beforeAll, expect, test } from "bun:test";
import fs from "node:fs";
import path from "node:path";
import type { Failure, ProjectFilesResponse } from "../../src/shared/types.ts";
import { apiClient, type Api } from "../helpers/api.ts";
import { startDaemon, type Daemon } from "../helpers/daemon.ts";
import { HOOK_TIMEOUT_MS } from "../helpers/process.ts";
import { tmpWorkspace, type TmpWorkspace } from "../helpers/workspace.ts";

let ws: TmpWorkspace;
let daemon: Daemon;
let api: Api;
beforeAll(async () => {
  ws = tmpWorkspace({ server: { idleMinutes: 5 } });
  const folder = path.join(ws.root, "Unregistered", "subfolder");
  fs.mkdirSync(folder, { recursive: true });
  fs.writeFileSync(path.join(folder, "Brief.PDF"), Buffer.from([0, 255, 10, 99]));
  fs.writeFileSync(path.join(folder, "図.png"), Buffer.from([137, 80, 78, 71]));
  fs.mkdirSync(path.join(ws.root, ".git"));
  fs.writeFileSync(path.join(ws.root, ".git", "hidden.txt"), "Not material");
  fs.symlinkSync(ws.base, path.join(ws.root, "outside"));
  fs.symlinkSync(path.join(ws.root, ".git"), path.join(ws.root, "git-alias"));
  fs.symlinkSync(ws.root, path.join(folder, "loop"));
  daemon = await startDaemon(ws.root);
  fs.symlinkSync(path.join(ws.root, ".alps-harness"), path.join(ws.root, "records-alias"));
  api = apiClient(daemon);
}, HOOK_TIMEOUT_MS);
afterAll(async () => {
  await daemon?.stop();
  ws?.dispose();
}, HOOK_TIMEOUT_MS);

test("E14 user can browse and search unregistered binary materials without reading their contents", async () => {
  const top = await api.ok<ProjectFilesResponse>("GET", "/api/project-files");
  expect(top.path).toBe(".");
  expect(top.entries.some((entry) => entry.name === "Unregistered" && entry.directory)).toBe(true);
  expect(
    top.entries.some((entry) =>
      [".git", ".alps-harness", "git-alias", "records-alias"].includes(entry.name),
    ),
  ).toBe(false);
  expect(top.entries.find((entry) => entry.name === "outside")?.readable).toBe(false);
  const found = await api.ok<ProjectFilesResponse>(
    "GET",
    "/api/project-files?path=Unregistered&query=brief.pdf",
  );
  expect(found.entries).toEqual([
    {
      path: "Unregistered/subfolder/Brief.PDF",
      name: "Brief.PDF",
      directory: false,
      readable: true,
    },
  ]);
  expect(found.incomplete).toBe(false);
  const nested = await api.ok<ProjectFilesResponse>(
    "GET",
    "/api/project-files?path=Unregistered%2Fsubfolder",
  );
  expect(nested.entries.some((entry) => entry.name === "図.png" && entry.readable)).toBe(true);
  expect(
    (await api.ok<ProjectFilesResponse>("GET", "/api/project-files?query=brief.pdf")).entries,
  ).toHaveLength(1);
});

test("E14 pagination bounds responses; an exhausted search is explicitly incomplete", async () => {
  const directory = path.join(ws.root, "many");
  fs.mkdirSync(directory);
  for (let index = 0; index < 103; index++)
    fs.writeFileSync(path.join(directory, `${String(index).padStart(3, "0")}.txt`), "");
  const first = await api.ok<ProjectFilesResponse>("GET", "/api/project-files?path=many");
  expect(first.entries).toHaveLength(100);
  expect(first.next).toBe(100);
  const last = await api.ok<ProjectFilesResponse>(
    "GET",
    `/api/project-files?path=many&offset=${first.next}`,
  );
  expect(last.entries).toHaveLength(3);
  expect(last.next).toBeNull();
  expect(new Set([...first.entries, ...last.entries].map((entry) => entry.path)).size).toBe(103);
  const large = path.join(ws.root, "large");
  fs.mkdirSync(large);
  for (let index = 0; index < 10_002; index++)
    fs.writeFileSync(path.join(large, `${index}.txt`), "");
  const limited = await api.ok<ProjectFilesResponse>(
    "GET",
    "/api/project-files?path=large&query=absent",
  );
  expect(limited.entries).toEqual([]);
  expect(limited.incomplete).toBe(true);
}, 30_000);

test("E14 picker rejects escapes, system records, invalid paging and agent callers", async () => {
  for (const name of ["../", "outside", ".git", "git-alias", "records-alias", ".alps-harness"]) {
    const reply = await api.get(`/api/project-files?path=${encodeURIComponent(name)}`);
    expect((reply.body as Failure).ok).toBe(false);
    expect((reply.body as Failure).error.code).toBe("outside-workspace");
  }
  const missing = await api.get("/api/project-files?path=missing");
  expect((missing.body as Failure).error.code).toBe("not-found");
  const invalid = await api.get("/api/project-files?offset=-1");
  expect((invalid.body as Failure).ok).toBe(false);
  const response = await fetch(new URL("/api/project-files", daemon.url), {
    headers: {
      "X-Harness-Token": daemon.info.token,
      "X-Harness-Client": encodeURIComponent(JSON.stringify({ name: "test-agent", version: "1" })),
    },
  });
  const denied = (await response.json()) as Failure;
  expect(denied.ok).toBe(false);
  expect(denied.error.key).toBe("error.launchUser");
});

test("E14 inaccessible folders are unavailable and a partial search is not an empty complete result", async () => {
  // POSIX permissions cannot model this case when the suite itself runs as root or on Windows.
  if (process.platform === "win32" || process.getuid?.() === 0) return;
  const folder = path.join(ws.root, "locked");
  fs.mkdirSync(folder);
  fs.writeFileSync(path.join(folder, "hidden.pdf"), "");
  fs.chmodSync(folder, 0);
  try {
    const found = await api.ok<ProjectFilesResponse>("GET", "/api/project-files?query=locked");
    expect(found.entries.find((entry) => entry.name === "locked")?.readable).toBe(false);
    expect(found.incomplete).toBe(true);
    const denied = await api.get("/api/project-files?path=locked");
    expect((denied.body as Failure).ok).toBe(false);
  } finally {
    fs.chmodSync(folder, 0o700);
  }
});
