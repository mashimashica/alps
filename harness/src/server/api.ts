/*
 * The routes of the HTTP API. Each answers one tool of the MCP server, which relays to it, and the
 * WebUI uses the same routes. The safety checks (Host, token, Sec-Fetch-Site, JSON bodies) run in
 * http.ts before a route is chosen.
 *
 *   get_model       GET  /api/model
 *   list_artifacts  GET  /api/artifacts?type&changedSince
 *   list_instances  GET  /api/instances?process&path&limit&cursor
 *   instantiate     POST /api/instances
 *   run             POST /api/instances/:id/run
 *   get_run         GET  /api/runs/:id?tail&wait
 *   cancel_run      POST /api/runs/:id/cancel
 *   finish_run      POST /api/runs/:id/finish
 *   evaluate        POST /api/instances/:id/evaluate
 *   get_assessment  GET  /api/assessment?format
 */

import type { z } from "zod";
import { HTTP_STATUS, HarnessError, type Harness } from "../harness/index.ts";
import {
  artifactsQuery,
  assessmentQuery,
  createInstanceRequest,
  evaluateRequest,
  finishRequest,
  instancesQuery,
  runQuery,
  runRequest,
  updateInstanceRequest,
} from "../shared/schema.ts";
import type {
  ArtifactsResponse,
  AssessmentResponse,
  CancelResponse,
  Failure,
  FinishResponse,
  InstanceResponse,
  InstancesResponse,
  ModelResponse,
  RunDetailResponse,
  RunStartResponse,
} from "../shared/types.ts";

export interface ApiReply {
  status: number;
  body: { ok: true } | Failure;
}

interface RouteContext {
  request: Request;
  url: URL;
  /** The route's id. */
  id: string;
  /** Lets the request stay open longer than the server's idle timeout (a waiting get_run). */
  keepOpen(): void;
}

interface Route {
  method: "GET" | "POST";
  pattern: RegExp;
  handle(context: RouteContext): ApiReply | Promise<ApiReply>;
}

const ok = <T extends { ok: true }>(body: T, status = 200): ApiReply => ({ status, body });

const query = (url: URL): Record<string, string> => Object.fromEntries(url.searchParams);

/** The request's JSON body; an empty body is `{}`. */
async function body(request: Request): Promise<unknown> {
  const text = await request.text();
  if (!text.trim()) return {};
  try {
    return JSON.parse(text) as unknown;
  } catch (error) {
    throw new HarnessError("invalid-request", `The body is not JSON: ${(error as Error).message}`);
  }
}

/** Validates a body or query. With `judgments`, problems with the judgments are `invalid-judgment`. */
function parse<T extends z.ZodType>(
  schema: T,
  value: unknown,
  options: { judgments?: boolean } = {},
): z.output<T> {
  const parsed = schema.safeParse(value);
  if (parsed.success) return parsed.data;
  const issues = parsed.error.issues;
  const message = issues
    .map((issue) => `${issue.path.length > 0 ? issue.path.join(".") : "(body)"}: ${issue.message}`)
    .join("; ");
  const judgments = options.judgments && issues.some((issue) => issue.path[0] === "judgments");
  throw new HarnessError(judgments ? "invalid-judgment" : "invalid-request", message);
}

function routes(harness: Harness): Route[] {
  const id = "([A-Za-z0-9_-]+)";
  return [
    {
      method: "GET",
      pattern: /^\/api\/model$/,
      handle: async () => ok({ ok: true, model: await harness.model() } satisfies ModelResponse),
    },
    {
      method: "GET",
      pattern: /^\/api\/artifacts$/,
      handle: ({ url }) =>
        ok({
          ok: true,
          ...harness.artifacts(parse(artifactsQuery, query(url))),
        } satisfies ArtifactsResponse),
    },
    {
      method: "GET",
      pattern: /^\/api\/instances$/,
      handle: ({ url }) =>
        ok({
          ok: true,
          ...harness.instances(parse(instancesQuery, query(url))),
        } satisfies InstancesResponse),
    },
    {
      method: "POST",
      pattern: /^\/api\/instances$/,
      handle: async ({ request }) => {
        const given = await body(request);
        // One of two shapes; checking against the one meant gives the useful messages.
        const update = given !== null && typeof given === "object" && "instance" in given;
        const result = harness.instantiate(
          parse(update ? updateInstanceRequest : createInstanceRequest, given),
        );
        return ok({ ok: true, ...result } satisfies InstanceResponse, result.created ? 201 : 200);
      },
    },
    {
      method: "POST",
      pattern: new RegExp(`^/api/instances/${id}/run$`),
      handle: async ({ request, id: instance }) =>
        ok(
          {
            ok: true,
            ...harness.startRun(instance, parse(runRequest, await body(request))),
          } satisfies RunStartResponse,
          201,
        ),
    },
    {
      method: "POST",
      pattern: new RegExp(`^/api/instances/${id}/evaluate$`),
      handle: async ({ request, id: instance }) =>
        ok({
          ok: true,
          ...harness.evaluate(
            instance,
            parse(evaluateRequest, await body(request), { judgments: true }),
          ),
        } satisfies InstanceResponse),
    },
    {
      method: "GET",
      pattern: new RegExp(`^/api/runs/${id}$`),
      handle: async ({ request, url, id: run, keepOpen }) => {
        const options = parse(runQuery, query(url));
        if (options.wait > 0) keepOpen();
        return ok({
          ok: true,
          ...(await harness.getRun(run, options, request.signal)),
        } satisfies RunDetailResponse);
      },
    },
    {
      method: "POST",
      pattern: new RegExp(`^/api/runs/${id}/cancel$`),
      handle: async ({ request, id: run }) => {
        await body(request);
        return ok({ ok: true, ...harness.cancelRun(run) } satisfies CancelResponse);
      },
    },
    {
      method: "POST",
      pattern: new RegExp(`^/api/runs/${id}/finish$`),
      handle: async ({ request, id: run }) =>
        ok({
          ok: true,
          ...harness.finishRun(run, parse(finishRequest, await body(request))),
        } satisfies FinishResponse),
    },
    {
      method: "GET",
      pattern: /^\/api\/assessment$/,
      handle: ({ url }) => {
        parse(assessmentQuery, query(url));
        return ok({ ok: true, assessment: harness.assessment() } satisfies AssessmentResponse);
      },
    },
  ];
}

export type Api = (request: Request, url: URL, keepOpen: () => void) => Promise<ApiReply | null>;

/** The API over a harness. It answers `null` for a path it does not have. */
export function createApi(harness: Harness): Api {
  const table = routes(harness);
  return async (request, url, keepOpen) => {
    for (const route of table) {
      const match = route.pattern.exec(url.pathname);
      if (!match || route.method !== request.method) continue;
      try {
        return await route.handle({ request, url, id: match[1] ?? "", keepOpen });
      } catch (error) {
        if (!(error instanceof HarnessError)) throw error;
        const failure: Failure = {
          ok: false,
          error: {
            code: error.code,
            message: error.message,
            ...(error.files ? { files: error.files } : {}),
          },
        };
        return { status: HTTP_STATUS[error.code], body: failure };
      }
    }
    return null;
  };
}
