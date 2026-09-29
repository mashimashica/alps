import { say, type MessageArg, type MessageArgs, type MessageKey } from "../shared/strings.ts";
import type { ErrorCode, ErrorInfo, HttpErrorCode } from "../shared/types.ts";

/** The codes the harness core fails with: the MCP tools' codes and the two request-level ones. */
export type HarnessErrorCode =
  | ErrorCode
  | Extract<HttpErrorCode, "invalid-request" | "outside-workspace">;

/**
 * A request that the harness refuses, with the code that the API and the MCP tools report. Its
 * message is English; the key and arguments let a client say it in another language.
 */
export class HarnessError extends Error {
  readonly key: MessageKey;
  readonly args: Record<string, MessageArg>;

  constructor(
    readonly code: HarnessErrorCode,
    message: { key: MessageKey; args: Record<string, MessageArg> },
    /** `no-model`: the files looked at, or where a missing one can be placed. */
    readonly files?: string[],
  ) {
    super(say("en", message.key, message.args as never));
    this.name = "HarnessError";
    this.key = message.key;
    this.args = message.args;
  }

  /** What a failed response carries. */
  get info(): ErrorInfo {
    return {
      code: this.code,
      message: this.message,
      key: this.key,
      args: this.args,
      ...(this.files ? { files: this.files } : {}),
    };
  }
}

/** A HarnessError whose message arguments are checked against the key. */
export const refuse = <K extends MessageKey>(
  code: HarnessErrorCode,
  key: K,
  args: MessageArgs<K>,
  files?: string[],
): HarnessError => new HarnessError(code, { key, args: args as Record<string, MessageArg> }, files);

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
