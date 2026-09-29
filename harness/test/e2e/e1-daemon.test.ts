/*
 * E1 (Plugin structure): `serve --daemon` writes server.json, /api/health answers, and the
 * daemon exits when idle. A second `mcp` process connects to the existing daemon (stage 3).
 */

import { afterAll, describe, expect, test } from "bun:test";
import fs from "node:fs";
import type { HealthInfo } from "../../src/shared/types.ts";
import { killStrayDaemons, startDaemon } from "../helpers/daemon.ts";
import { serverJson } from "../helpers/paths.ts";
import { cli, isAlive, waitFor } from "../helpers/process.ts";
import { tmpWorkspace, type TmpWorkspace } from "../helpers/workspace.ts";

const workspaces: TmpWorkspace[] = [];
const workspace = (overrides?: Parameters<typeof tmpWorkspace>[0]): TmpWorkspace => {
  const ws = tmpWorkspace(overrides);
  workspaces.push(ws);
  return ws;
};

afterAll(() => {
  killStrayDaemons();
  for (const ws of workspaces) ws.dispose();
});

/** The process group of a pid (macOS and Linux). */
function processGroup(pid: number): number {
  const ps = Bun.spawnSync(["ps", "-o", "pgid=", "-p", String(pid)]);
  return Number(ps.stdout.toString().trim());
}

describe("E1 serve --daemon", () => {
  test(
    "E1 daemon writes server.json and exits when idle",
    async () => {
      const ws = workspace({ server: { idleMinutes: 0.05 } });
      const daemon = await startDaemon(ws.root);

      // The detached child outlives the process that started it, in a process group of its own.
      expect(daemon.parent.code).toBe(0);
      expect(daemon.info.pid).not.toBe(daemon.parent.pid);
      expect(isAlive(daemon.parent.pid)).toBe(false);
      expect(isAlive(daemon.info.pid)).toBe(true);
      if (process.platform !== "win32") expect(processGroup(daemon.info.pid)).toBe(daemon.info.pid);

      expect(daemon.info).toEqual({
        pid: expect.any(Number),
        port: expect.any(Number),
        token: expect.stringMatching(/^[0-9a-f]{48}$/),
        startedAt: expect.any(Number),
      });
      expect(fs.statSync(serverJson(ws.root)).mode & 0o777).toBe(0o600);

      const response = await fetch(`${daemon.url}api/health`, {
        headers: { "X-Harness-Token": daemon.info.token },
      });
      expect(response.status).toBe(200);
      expect((await response.json()) as HealthInfo).toMatchObject({
        ok: true,
        name: "alps-harness",
        pid: daemon.info.pid,
        port: daemon.info.port,
        workspace: ws.root,
        development: false,
      });

      // With no connections and no runs, it stops after server.idleMinutes (3 s) and removes server.json.
      await waitFor(() => !isAlive(daemon.info.pid), 15_000, "the idle daemon to exit");
      expect(fs.existsSync(serverJson(ws.root))).toBe(false);
    },
    { timeout: 30_000 },
  );

  test(
    "E1 alps-harness stop stops the daemon",
    async () => {
      const ws = workspace();
      const daemon = await startDaemon(ws.root);
      const result = await cli(["stop", ws.root]);
      expect(result.code).toBe(0);
      expect(isAlive(daemon.info.pid)).toBe(false);
      expect(fs.existsSync(serverJson(ws.root))).toBe(false);
    },
    { timeout: 30_000 },
  );

  test.todo("E1 a second mcp process connects to the existing daemon", () => {});
});
