/*
 * Public runtime contract for products that serve their own UI while using this harness as the
 * only execution and record writer. Version numbers move only when the corresponding public
 * surface changes incompatibly.
 */

export const RUNTIME_CONTRACT = {
  version: "2026-10-02",
  schemaVersion: 2,
  api: "http+sse",
  eventVersion: 1,
  uiBundleVersion: 1,
  capabilities: [
    "headless-daemon",
    "reference-ui",
    "custom-ui",
    "runtime-ui-attach",
    "mcp-stdio",
    "launch-intents",
    "desktop-launch-claims",
    "terminal-log-view",
    "execution-preflight",
    "project-mcp-config",
    "model-authoring",
    "process-design-sessions",
    "desktop-process-design-sessions",
    "process-design-bundles",
    "design-session-index",
    "work-object-views",
    "evaluation-context",
    "artifact-content",
    "optional-observability",
    "observation-records",
    "single-workspace-writer",
  ],
} as const satisfies RuntimeContract;

export type RuntimeCapability = (typeof RUNTIME_CONTRACT.capabilities)[number];

export const PRODUCT_UI_CONTRACT = "external-ui-entry-v1" as const;

export interface RuntimeContract {
  version: "2026-10-02";
  schemaVersion: 2;
  api: "http+sse";
  eventVersion: number;
  uiBundleVersion: number;
  capabilities: readonly string[];
}

export interface RuntimeContractResponse {
  ok: true;
  contract: RuntimeContract;
  uiContract: typeof PRODUCT_UI_CONTRACT;
  runtime: {
    version: string;
    workspace: string;
  };
}

export interface ProductContractRequirement {
  api: RuntimeContract["api"];
  eventVersion: number;
  schemaVersion?: number;
  uiBundleVersion?: number;
  capabilities?: readonly string[];
}

export function runtimeCompatible(
  contract: Pick<
    RuntimeContract,
    "api" | "eventVersion" | "schemaVersion" | "uiBundleVersion" | "capabilities"
  >,
  requirement: ProductContractRequirement,
): boolean {
  return (
    requirement.api === contract.api &&
    requirement.eventVersion === contract.eventVersion &&
    (requirement.schemaVersion === undefined ||
      requirement.schemaVersion === contract.schemaVersion) &&
    (requirement.uiBundleVersion === undefined ||
      requirement.uiBundleVersion === contract.uiBundleVersion) &&
    (requirement.capabilities ?? []).every((capability) =>
      contract.capabilities.includes(capability),
    )
  );
}

export function productCompatible(requirement: ProductContractRequirement): boolean {
  return runtimeCompatible(RUNTIME_CONTRACT, requirement);
}
