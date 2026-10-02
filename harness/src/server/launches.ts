/* Delivery intents, separate from runs. Native windows are viewers, never the run's lifecycle. */
import fs from "node:fs";
import path from "node:path";
import { isDeepStrictEqual } from "node:util";
import {
  CLAUDE_SESSION_VARIABLES,
  mcpArgs,
  mcpConfigFile,
  resolveAgents,
  startsProcess,
  type AgentSpec,
} from "../agents/index.ts";
import { HarnessError, refuse, type Caller, type Harness } from "../harness/index.ts";
import { loadWorkspace } from "../model/index.ts";
import { wakeRequest, assessRequest, launchRequest } from "../shared/schema.ts";
import type {
  ExecutionCapabilities,
  ExecutionDesktopStatus,
  ExecutionMcpConfigSave,
  LaunchRecord,
  LaunchRequest,
  LaunchResponse,
  RunExecution,
  RunView,
} from "../shared/types.ts";
import { CLI_PATH } from "./daemon.ts";
import {
  claudeProjectConfig,
  codexProjectConfig,
  mcpServerForWorkspace,
  probeMcpServer,
  saveProjectMcpConfigs,
} from "./preflight.ts";
import { parseYaml } from "./yaml.ts";

const UUID = /^[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}$/i;
const quote = (value: string): string => `'${value.replace(/'/g, "'\\''")}'`;
const launchScope = ({
  id: _id,
  method: _method,
  agent: _agent,
  model: _model,
  effort: _effort,
  replacesLaunch: _replacesLaunch,
  ...scope
}: LaunchRequest): Omit<
  LaunchRequest,
  "id" | "method" | "agent" | "model" | "effort" | "replacesLaunch"
> => scope;
const sameLaunchScope = (left: LaunchRequest, right: LaunchRequest): boolean =>
  isDeepStrictEqual(launchScope(left), launchScope(right));

export class Launches {
  readonly #records = new Map<string, LaunchRecord>();
  readonly #pending = new Map<string, Promise<LaunchResponse>>();
  readonly #dir: string;
  readonly #startingConversations = new Set<string>();
  #capabilities: { at: number; value: ExecutionCapabilities } | null = null;
  constructor(readonly harness: Harness) {
    this.#dir = path.join(harness.root, ".alps-harness", "launches");
    if (fs.existsSync(this.#dir))
      for (const file of fs.readdirSync(this.#dir)) {
        if (!/^[0-9a-f-]{36}\.json$/i.test(file)) continue;
        try {
          const record = JSON.parse(
            fs.readFileSync(path.join(this.#dir, file), "utf8"),
          ) as LaunchRecord;
          if (
            UUID.test(record.id) &&
            launchRequest.safeParse(record.request).success &&
            record.request?.id === record.id &&
            ["pending", "starting", "started", "canceled", "failed"].includes(record.status)
          )
            this.#records.set(record.id, record);
        } catch {
          /* An incomplete or unreadable intent is not evidence of a completed launch. */
        }
      }
    for (const record of this.#records.values()) this.#recover(record);
  }
  #recover(record: LaunchRecord): void {
    if (record.status !== "starting") return;
    const run = this.harness.runForLaunch(record.id);
    if (run) {
      record.runId = run.id;
      record.status = "started";
      record.error = null;
    } else {
      record.status = "failed";
      record.error = {
        code: "internal",
        key: "error.launchFailed",
        args: {},
        message: "Start was interrupted; no run was recorded.",
      };
    }
    this.#write(record);
  }
  #write(record: LaunchRecord): void {
    fs.mkdirSync(this.#dir, { recursive: true, mode: 0o700 });
    const file = path.join(this.#dir, `${record.id}.json`);
    fs.writeFileSync(`${file}.tmp`, JSON.stringify(record, null, 2), { mode: 0o600 });
    fs.renameSync(`${file}.tmp`, file);
    this.#records.set(record.id, record);
  }
  get(id: string): LaunchRecord {
    const record = this.#records.get(id);
    if (!record) throw refuse("not-found", "error.launchMissing", {});
    return record;
  }
  list(): LaunchRecord[] {
    return [...this.#records.values()].sort((a, b) => b.createdAt - a.createdAt);
  }
  #spec(agent: string): AgentSpec {
    const specs = resolveAgents(loadWorkspace(this.harness.root, { parseYaml }).config.agents);
    const found = specs.find((spec) => spec.id === agent);
    if (!found)
      throw refuse("agent-unavailable", "error.noAgent", {
        agent,
        agents: specs.map((s) => s.id).join(", "),
      });
    return found;
  }
  async capabilities(): Promise<ExecutionCapabilities> {
    if (this.#capabilities && Date.now() - this.#capabilities.at < 5000)
      return this.#capabilities.value;
    const specs = resolveAgents(loadWorkspace(this.harness.root, { parseYaml }).config.agents);
    const model = await this.harness.model().catch(() => null);
    const cli = new Map((model?.agents ?? []).map((agent) => [agent.id, agent]));
    const installed = (
      names: string[],
      scheme: "claude" | "codex",
      ready: boolean,
      readyReason: string | null,
    ): ExecutionDesktopStatus => {
      const unsupported = (reason: string): ExecutionDesktopStatus => ({
        supported: false,
        installed: false,
        scheme,
        canOpen: false,
        canStartFromAlps: false,
        reason,
      });
      if (process.platform !== "darwin")
        return unsupported("Desktop handoff is currently supported on macOS.");
      const found = names.some((name) =>
        ["/Applications", path.join(process.env.HOME ?? "", "Applications")].some((dir) => {
          const file = path.join(dir, name, "Contents", "Info.plist");
          if (!fs.existsSync(file)) return false;
          try {
            const result = Bun.spawnSync(["/usr/bin/plutil", "-convert", "json", "-o", "-", file], {
              stderr: "ignore",
              timeout: 2000,
            });
            if (!result.success) return false;
            const bundle = JSON.parse(result.stdout.toString());
            const vendor = scheme === "codex" ? "com.openai." : "com.anthropic.";
            return (
              typeof bundle.CFBundleIdentifier === "string" &&
              bundle.CFBundleIdentifier.startsWith(vendor) &&
              Array.isArray(bundle.CFBundleURLTypes) &&
              bundle.CFBundleURLTypes.some((item: { CFBundleURLSchemes?: string[] }) =>
                item.CFBundleURLSchemes?.includes(scheme),
              )
            );
          } catch {
            return false;
          }
        }),
      );
      if (!found)
        return {
          supported: true,
          installed: false,
          scheme,
          canOpen: false,
          canStartFromAlps: false,
          reason: "The desktop application is not installed or does not expose its URL scheme.",
        };
      return {
        supported: true,
        installed: true,
        scheme,
        canOpen: true,
        canStartFromAlps: ready,
        reason: ready ? null : readyReason,
      };
    };
    const server = mcpServerForWorkspace(this.harness.root);
    const probe = await probeMcpServer(this.harness.root);
    const claudeConfig = claudeProjectConfig(this.harness.root, server);
    const codexConfig = codexProjectConfig(this.harness.root, server);
    const connectionFor = (
      provider: "claude" | "codex",
    ): { ready: boolean; reason: string | null } => {
      const config = provider === "claude" ? claudeConfig : codexConfig;
      if (config.status !== "usable")
        return { ready: false, reason: config.reason ?? "Install the ALPS project MCP config." };
      if (!probe.claimTool)
        return { ready: false, reason: probe.error ?? "ALPS MCP tools are not available." };
      return { ready: true, reason: null };
    };
    const value: ExecutionCapabilities = {
      ok: true,
      workspace: this.harness.root,
      terminal: process.platform === "darwin",
      runtime: { command: server.command, args: server.args },
      mcp: {
        server,
        claudeProjectConfig: claudeConfig,
        codexProjectConfig: codexConfig,
        probe,
        claim: { tool: "claim_launch", available: probe.claimTool, requiresPendingLaunch: true },
      },
      agents: specs.map((spec) => {
        const provider = spec.format === "claude" || spec.format === "codex" ? spec.format : null;
        const connection = provider ? connectionFor(provider) : { ready: false, reason: null };
        const desktopStatus =
          spec.format === "claude"
            ? installed(["Claude.app"], "claude", connection.ready, connection.reason)
            : spec.format === "codex"
              ? installed(
                  ["Codex.app", "ChatGPT.app"],
                  "codex",
                  connection.ready,
                  connection.reason,
                )
              : {
                  supported: false,
                  installed: false,
                  scheme: null,
                  canOpen: false,
                  canStartFromAlps: false,
                  reason: "This agent has no supported desktop handoff.",
                };
        return {
          id: spec.id,
          provider,
          desktop: desktopStatus.canStartFromAlps,
          cli: {
            available: cli.get(spec.id)?.available ?? !startsProcess(spec),
            version: cli.get(spec.id)?.version ?? null,
            reason: cli.get(spec.id)?.reason ?? null,
          },
          desktopStatus,
          mcp: {
            supported: spec.format === "claude" || spec.format === "codex",
            claimTool: probe.claimTool && connection.ready,
            reason: connection.reason,
          },
        };
      }),
    };
    this.#capabilities = { at: Date.now(), value };
    return value;
  }
  saveMcpConfigs(): ExecutionMcpConfigSave {
    const saved = saveProjectMcpConfigs(
      this.harness.root,
      mcpServerForWorkspace(this.harness.root),
    );
    this.#capabilities = null;
    return saved;
  }
  async submit(request: LaunchRequest): Promise<LaunchResponse> {
    const prior = this.#records.get(request.id);
    if (prior) {
      if (!isDeepStrictEqual(prior.request, request))
        throw refuse("invalid-request", "error.launchChanged", {});
      const pending = this.#pending.get(request.id);
      if (pending) return pending;
      // Recover the receipt after a crash between writing the run and its delivery record.
      if (prior.status === "starting") {
        const linked = this.harness.runForLaunch(prior.id);
        if (linked) {
          prior.runId = linked.id;
          prior.status = "started";
          this.#write(prior);
        } else {
          prior.status = "failed";
          prior.error = {
            code: "internal",
            key: "error.launchFailed",
            args: {},
            message: "Start was interrupted; no run was recorded.",
          };
          this.#write(prior);
        }
      }
      return this.#answer(prior);
    }
    if (request.method !== "cli") {
      if (request.model || request.effort) throw refuse("invalid-request", "error.launchModel", {});
      const spec = this.#spec(request.agent);
      if (spec.format !== "claude" && spec.format !== "codex")
        throw refuse("agent-unavailable", "error.launchProvider", {});
      const capabilities = await this.capabilities();
      const capability = capabilities.agents.find((item) => item.id === request.agent);
      if (request.method === "desktop" && !capability?.desktopStatus.canStartFromAlps)
        throw refuse("agent-unavailable", "error.desktopUnavailable", {});
      if (request.method === "terminal") await this.#resumeSource(request);
    }
    // Validate saved targets before exposing an intent in the UI. The harness validates again at start.
    const model = await this.harness.model();
    for (const process of request.processes ?? [])
      if (!model.processes.some((item) => item.id === process || item.name === process))
        throw refuse("not-found", "error.launchProcess", { process });
    if (request.kind === "process") this.harness.instance(request.instance ?? "");
    if (request.replacesLaunch) {
      const previous = this.get(request.replacesLaunch);
      if (previous.status !== "pending" || !sameLaunchScope(previous.request, request))
        throw refuse("already-running", "error.launchClaim", {});
    }
    const record: LaunchRecord = {
      id: request.id,
      createdAt: Date.now(),
      status: request.method === "cli" ? "starting" : "pending",
      request,
      runId: null,
      error: null,
    };
    this.#write(record);
    if (request.replacesLaunch) {
      const previous = this.get(request.replacesLaunch);
      if (previous.status === "pending") {
        previous.status = "canceled";
        previous.error = null;
        this.#write(previous);
      }
    }
    if (request.method !== "cli") return this.#answer(record);
    const starting = this.#start(record, { kind: "user" });
    this.#pending.set(record.id, starting);
    try {
      return await starting;
    } finally {
      this.#pending.delete(record.id);
    }
  }
  async #answer(record: LaunchRecord): Promise<LaunchResponse> {
    return {
      ok: true,
      launch: record,
      ...(record.runId
        ? { run: (await this.harness.getRun(record.runId, { tail: 0, wait: 0 })).run }
        : {}),
      ...(record.status === "pending" ? { prompt: this.prompt(record) } : {}),
    };
  }
  prompt(record: LaunchRecord): string {
    return `Continue this ALPS request in workspace ${this.harness.root}.\nFirst call the ALPS MCP tool claim_launch with id ${record.id}. If the tool is unavailable, connect the ALPS plugin/MCP server for this workspace first; do not perform the work before claim_launch succeeds. The tool returns the current instructions and records the start. Follow those instructions and report with finish_run. The saved scope (${record.request.kind}${record.request.kind === "wake" ? `, ${record.request.runs ?? "plan"}` : ""}) applies; changing this composer does not authorize expanding it. If you know this application's opaque conversation id, pass it as sessionId; do not guess one.\n\nRequest:\n${record.request.request ?? "Read the instructions returned by claim_launch."}`;
  }
  async claim(id: string, caller: Caller, sessionId?: string): Promise<LaunchResponse> {
    if (caller.kind !== "agent" || !caller.session)
      throw refuse("invalid-request", "error.externalSession", {});
    const record = this.get(id);
    if (record.request.method === "cli") throw refuse("invalid-request", "error.launchClaim", {});
    const spec = this.#spec(record.request.agent);
    const expected = spec.format === "codex" ? /codex|chatgpt/i : /claude/i;
    if (!expected.test(caller.client.name))
      throw refuse("invalid-request", "error.launchClient", { agent: spec.label });
    const current = this.harness.externalCaller(caller);
    if (record.runId) {
      const bound = this.harness.bindExternal(record.runId, caller, sessionId);
      return { ok: true, launch: record, ...bound };
    }
    if (
      current.kind === "agent" &&
      (current.wake || current.assess || this.harness.externalRunFor(caller.session))
    )
      throw refuse("already-running", "error.externalConnected", {});
    if (record.status !== "pending") throw refuse("invalid-request", "error.launchClaim", {});
    if (record.request.method === "terminal") {
      const source = await this.#resumeSource(record.request);
      if (sessionId && sessionId !== source.execution?.sessionId)
        throw refuse("invalid-request", "error.externalIdentity", {});
      sessionId = source.execution?.sessionId;
    }
    if (this.#pending.has(id)) throw refuse("already-running", "error.externalConnected", {});
    if (
      sessionId &&
      (this.harness.activeConversation(sessionId) || this.#startingConversations.has(sessionId))
    )
      throw refuse("already-running", "error.externalConnected", {});
    if (sessionId) this.#startingConversations.add(sessionId);
    record.status = "starting";
    this.#write(record);
    const starting = this.#start(record, caller, sessionId);
    this.#pending.set(id, starting);
    try {
      return await starting;
    } finally {
      this.#pending.delete(id);
      if (sessionId) this.#startingConversations.delete(sessionId);
    }
  }
  async #start(record: LaunchRecord, caller: Caller, sessionId?: string): Promise<LaunchResponse> {
    const request = record.request;
    const execution: RunExecution = {
      method: request.method,
      launchId: record.id,
      ...(sessionId ? { sessionId } : {}),
      ...(request.resumedFrom ? { resumedFrom: request.resumedFrom } : {}),
    };
    try {
      const selection = {
        agent: request.agent,
        ...(request.model ? { model: request.model } : {}),
        ...(request.effort ? { effort: request.effort } : {}),
      };
      let result: { run: RunView; prompt?: string };
      if (request.kind === "process")
        result = await this.harness.startRun(
          request.instance ?? "",
          selection,
          caller,
          execution,
          request.request,
        );
      else if (request.kind === "assess")
        result = await this.harness.assess(
          assessRequest.parse({
            ...selection,
            scope: request.scope ?? {},
            ...(request.request ? { request: request.request } : {}),
          }),
          caller,
          execution,
        );
      else {
        const wake = await this.harness.wake(
          wakeRequest.parse({
            ...selection,
            request: request.request,
            attachments: request.attachments ?? [],
            processes: request.processes ?? [],
            runs: request.runs ?? "plan",
          }),
          { kind: "request", caller },
          execution,
        );
        if (wake.skipped)
          throw refuse("already-running", "error.launchWakeRunning", { run: wake.running });
        result = { run: wake.run };
      }
      record.runId = result.run.id;
      record.status = "started";
      record.error = null;
      this.#write(record);
      const detail = await this.harness.getRun(result.run.id, { tail: 0, wait: 0 });
      return {
        ok: true,
        launch: record,
        run: result.run,
        ...(request.method !== "cli" ? { prompt: detail.run.prompt } : {}),
      };
    } catch (error) {
      const linked = this.harness.runForLaunch(record.id);
      if (linked) {
        record.runId = linked.id;
        record.status = "started";
        record.error = null;
        this.#write(record);
        return this.#answer(record);
      }
      record.status = "failed";
      record.error =
        error instanceof HarnessError
          ? error.info
          : {
              code: "internal",
              message: "Could not start this request.",
              key: "error.launchFailed",
              args: {},
            };
      this.#write(record);
      throw error;
    }
  }
  cancel(id: string): LaunchRecord {
    const record = this.get(id);
    if (record.status === "pending") {
      record.status = "canceled";
      this.#write(record);
    }
    return record;
  }
  async #resumeSource(request: LaunchRequest): Promise<RunView> {
    if (!(await this.capabilities()).terminal)
      throw refuse("agent-unavailable", "error.terminalUnavailable", {});
    const run = (await this.harness.getRun(request.resumedFrom ?? "", { tail: 0, wait: 0 })).run;
    if (run.execution?.method === "desktop")
      throw refuse("invalid-request", "error.resumeMissing", {});
    if (run.status === "running") throw refuse("already-running", "error.resumeRunning", {});
    if (!run.execution?.sessionId) throw refuse("invalid-request", "error.resumeMissing", {});
    if (
      run.agent !== request.agent ||
      run.kind !== request.kind ||
      run.instance !== (request.instance ?? null)
    )
      throw refuse("invalid-request", "error.launchChanged", {});
    if (this.harness.activeConversation(run.execution.sessionId))
      throw refuse("already-running", "error.externalConnected", {});
    const active = this.list().find(
      (item) =>
        this.harness.runExecution(item.request.resumedFrom ?? "")?.sessionId ===
          run.execution?.sessionId &&
        item.id !== request.id &&
        (item.status === "pending" || item.status === "starting"),
    );
    if (active) throw refuse("already-running", "error.externalConnected", {});
    return run;
  }
  async #open(command: string, args: string[]): Promise<void> {
    const child = Bun.spawn([command, ...args], {
      stdin: "ignore",
      stdout: "ignore",
      stderr: "ignore",
    });
    if ((await child.exited) !== 0) throw refuse("agent-unavailable", "error.nativeOpen", {});
  }
  async open(id: string): Promise<void> {
    const record = this.get(id);
    if (record.status !== "pending") throw refuse("invalid-request", "error.launchClaim", {});
    const spec = this.#spec(record.request.agent);
    try {
      if (record.request.method === "desktop") {
        const params = new URLSearchParams(
          spec.format === "codex"
            ? { path: this.harness.root, prompt: this.prompt(record) }
            : { folder: this.harness.root, q: this.prompt(record) },
        );
        await this.#open("/usr/bin/open", [
          spec.format === "codex" ? `codex://new?${params}` : `claude://code/new?${params}`,
        ]);
      } else if (record.request.method === "terminal") {
        const source = await this.#resumeSource(record.request);
        const server = {
          name: "alps-harness",
          command: process.execPath,
          args: [CLI_PATH, "mcp"],
          env: { ALPS_WORKSPACE: this.harness.root },
        };
        const config = path.join(this.#dir, `${id}.mcp.json`);
        if (spec.format === "claude")
          fs.writeFileSync(config, mcpConfigFile(server), { mode: 0o600 });
        const args =
          spec.format === "codex"
            ? ["resume", source.execution!.sessionId!, "--cd", this.harness.root]
            : ["--resume", source.execution!.sessionId!];
        await this.#terminal(id, [
          spec.command ?? "",
          ...args,
          ...mcpArgs(spec, server, config),
          this.prompt(record),
        ]);
      }
      record.error = null;
      this.#write(record);
    } catch (error) {
      record.error =
        error instanceof HarnessError
          ? error.info
          : {
              code: "internal",
              key: "error.nativeOpen",
              args: {},
              message: "Could not open the application.",
            };
      this.#write(record);
      throw error;
    }
  }
  async #terminal(id: string, argv: string[]): Promise<void> {
    if (process.platform !== "darwin")
      throw refuse("agent-unavailable", "error.terminalUnavailable", {});
    fs.mkdirSync(this.#dir, { recursive: true, mode: 0o700 });
    const file = path.join(this.#dir, `${id}.command`);
    const unset = CLAUDE_SESSION_VARIABLES;
    fs.writeFileSync(
      file,
      `#!/bin/sh\ncd ${quote(this.harness.root)} || exit 1\nunset ${unset.join(" ")}\n${argv.map(quote).join(" ")}\nprintf '\\nPress Return to close. '\nread reply\n`,
      { mode: 0o700 },
    );
    await this.#open("/usr/bin/open", ["-a", "Terminal", file]);
  }
  async openLog(runId: string): Promise<void> {
    await this.harness.getRun(runId, { tail: 0, wait: 0 });
    if (!/^r\d+$/.test(runId)) throw refuse("invalid-request", "error.launchChanged", {});
    await this.#terminal(`log-${runId}`, [
      process.execPath,
      CLI_PATH,
      "terminal-log",
      this.harness.root,
      "--run",
      runId,
    ]);
  }
}
