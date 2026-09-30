/*
 * The environment of an agent (Agents): a Claude Code agent does not inherit the variables by
 * which a Claude Code session marks the processes it starts; the rest of the harness server's
 * environment stays, the user's credentials and PATH among it, and the agent's `env` in
 * alps-harness.yaml still sets any variable. That a started agent, and its version check, get
 * this environment is E3's (test/e2e/e3-agents.test.ts).
 */

import { describe, expect, test } from "bun:test";
import {
  CLAUDE_SESSION_VARIABLES,
  envLeftOut,
  resolveAgents,
  type AgentSpec,
} from "../../src/agents/index.ts";
import { agentEnv } from "../../src/server/agent-process.ts";

const spec = (id: string, specs: AgentSpec[] = resolveAgents(undefined)): AgentSpec => {
  const found = specs.find((s) => s.id === id);
  if (!found) throw new Error(`no agent ${id}`);
  return found;
};

describe("agent launch", () => {
  test("a Claude Code agent leaves out exactly the variables that mark a Claude Code session", () => {
    // What a session of Claude Code (the CLI, its IDE extension, and the desktop app) sets for
    // the processes it starts (stage 7b: scratchpad clean-env.sh), without the user's settings.
    expect(CLAUDE_SESSION_VARIABLES).toEqual([
      "CLAUDECODE",
      "CLAUDE_CODE_ENTRYPOINT",
      "CLAUDE_CODE_SSE_PORT",
      "CLAUDE_EFFORT",
      "CLAUDE_CODE_SESSION_ID",
      "CLAUDE_CODE_HOST_SESSION_ID",
      "CLAUDE_CODE_CHILD_SESSION",
      "CLAUDE_CODE_SESSION_ATTENDED",
      "CLAUDE_CODE_MESSAGING_SOCKET",
      "CLAUDE_CODE_MESSAGING_TOKEN",
      "CLAUDE_CODE_TERMINAL_MCP_TOOLS",
      "CLAUDE_CODE_SDK_HAS_HOST_AUTH_REFRESH",
      "CLAUDE_CODE_DESKTOP_APP_VERSION",
      "CLAUDE_AGENT_SDK_VERSION",
      "CLAUDE_CODE_EXECPATH",
      "CLAUDE_PID",
    ]);
    for (const kept of [
      "ANTHROPIC_API_KEY",
      "ANTHROPIC_AUTH_TOKEN",
      "CLAUDE_CODE_OAUTH_TOKEN",
      "ANTHROPIC_BASE_URL",
      "CLAUDE_CONFIG_DIR",
      "DISABLE_AUTOUPDATER",
      "PATH",
      "HOME",
    ])
      expect(CLAUDE_SESSION_VARIABLES).not.toContain(kept);

    // By the format: any agent read as Claude Code, and no other.
    expect(envLeftOut(spec("claude-code"))).toEqual(CLAUDE_SESSION_VARIABLES);
    expect(envLeftOut(spec("codex"))).toEqual([]);
    const custom = resolveAgents({
      opus: { command: "claude", format: "claude", args: ["-p", "{prompt}"] },
      "claude-code": { format: "text" },
    });
    expect(envLeftOut(spec("opus", custom))).toEqual(CLAUDE_SESSION_VARIABLES);
    expect(envLeftOut(spec("claude-code", custom))).toEqual([]);
  });

  test("the agent's environment keeps the rest, and env in alps-harness.yaml still sets any variable", () => {
    const inherited = {
      CLAUDECODE: "1",
      CLAUDE_CODE_ENTRYPOINT: "claude-desktop",
      CLAUDE_EFFORT: "low",
      ANTHROPIC_API_KEY: "the user's key",
      PATH: "/usr/bin",
    };
    const claude = resolveAgents({ "claude-code": { env: { CLAUDE_EFFORT: "high" } } });
    const launch = {
      unset: envLeftOut(spec("claude-code", claude)),
      env: spec("claude-code", claude).env,
    };
    expect(agentEnv(inherited, launch)).toEqual({
      CLAUDE_EFFORT: "high",
      ANTHROPIC_API_KEY: "the user's key",
      PATH: "/usr/bin",
    });
    // Codex inherits all of it.
    expect(agentEnv(inherited, { unset: envLeftOut(spec("codex")), env: {} })).toEqual(inherited);
  });
});
