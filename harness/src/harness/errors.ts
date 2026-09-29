import type { ErrorCode, HttpErrorCode } from "../shared/types.ts";

/** The codes the harness core fails with: the MCP tools' codes and the two request-level ones. */
export type HarnessErrorCode =
  | ErrorCode
  | Extract<HttpErrorCode, "invalid-request" | "outside-workspace">;

/** A request that the harness refuses, with the code that the API and the MCP tools report. */
export class HarnessError extends Error {
  constructor(
    readonly code: HarnessErrorCode,
    message: string,
    /** `no-model`: the files looked at, or where a missing one can be placed. */
    readonly files?: string[],
  ) {
    super(message);
    this.name = "HarnessError";
  }
}

/** The HTTP status of each code. */
export const HTTP_STATUS: Record<HarnessErrorCode, number> = {
  "no-model": 503,
  "not-found": 404,
  "agent-unavailable": 409,
  "already-running": 409,
  "invalid-judgment": 400,
  "server-unreachable": 503,
  "invalid-request": 400,
  "outside-workspace": 403,
};
