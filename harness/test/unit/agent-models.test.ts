import { describe, expect, test } from "bun:test";
import { claudeModels, codexModels, withAgentSelection } from "../../src/agents/models.ts";
import { argsFor, resolveAgents } from "../../src/agents/index.ts";

describe("agent model choices", () => {
  test("Claude's future models and their effort levels come from initialization, not a built-in list", () => {
    expect(
      claudeModels({
        models: [
          {
            value: "future-model",
            displayName: "Future",
            supportedEffortLevels: ["gentle", "deep"],
          },
          { value: "fast", displayName: "Fast" },
        ],
        account: { email: "not returned" },
      }),
    ).toEqual([
      { id: "future-model", label: "Future", description: "", efforts: ["gentle", "deep"] },
      { id: "fast", label: "Fast", description: "", efforts: [] },
    ]);
    expect(() => claudeModels({ error: "not signed in" })).toThrow();
  });

  test("Codex keeps pagination and each model's own reasoning levels", () => {
    expect(
      codexModels({
        data: [
          {
            model: "new-model",
            displayName: "New model",
            supportedReasoningEfforts: [
              { reasoningEffort: "minimal" },
              { reasoningEffort: "ultra" },
            ],
            defaultReasoningEffort: "minimal",
          },
        ],
        nextCursor: "page-2",
      }),
    ).toEqual({
      models: [
        {
          id: "new-model",
          label: "New model",
          description: "",
          efforts: ["minimal", "ultra"],
          defaultEffort: "minimal",
        },
      ],
      next: "page-2",
    });
    expect(() => codexModels({ data: [{ model: "broken" }] })).toThrow();
  });

  test("overrides replace repeated model and effort options without changing sandbox or MCP configuration", () => {
    const codex = resolveAgents({
      codex: {
        args: [
          "exec",
          "--model=old",
          "-m",
          "older",
          "-c",
          'model="oldest"',
          "--config=model_reasoning_effort=high",
          "--sandbox",
          "workspace-write",
          "-c",
          'mcp_servers.alps.command="bun"',
          "{prompt}",
        ],
      },
    }).find((a) => a.id === "codex")!;
    expect(withAgentSelection(codex, {})).toBe(codex);
    const selected = withAgentSelection(codex, { model: "new", effort: "low" });
    expect(argsFor(selected, "A request")).toEqual([
      "exec",
      "--sandbox",
      "workspace-write",
      "-c",
      'mcp_servers.alps.command="bun"',
      "--model",
      "new",
      "-c",
      'model_reasoning_effort="low"',
      "A request",
    ]);
    const claude = resolveAgents({
      "claude-code": {
        args: [
          "-p",
          "{prompt}",
          "--model",
          "old",
          "--effort=high",
          "--permission-mode",
          "acceptEdits",
        ],
      },
    }).find((a) => a.id === "claude-code")!;
    expect(
      argsFor(withAgentSelection(claude, { model: "new", effort: "medium" }), "A request"),
    ).toEqual([
      "--model",
      "new",
      "--effort",
      "medium",
      "-p",
      "A request",
      "--permission-mode",
      "acceptEdits",
    ]);
    expect(argsFor({ ...selected, stdin: true }, "A request").at(-1)).toBe("-");
  });
});
