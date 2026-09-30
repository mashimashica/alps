/*
 * The routes of the HTTP API. Each answers one tool of the MCP server, which relays to it, and the
 * WebUI uses the same routes. The safety checks (Host, token, Sec-Fetch-Site, JSON bodies) run in
 * http.ts before a route is chosen.
 *
 *   get_model       GET  /api/model
 *   list_artifacts  GET  /api/artifacts?type&changedSince
 *   list_instances  GET  /api/instances?process&path&limit&cursor
 *   instantiate     POST /api/instances
 *   (resource)      GET  /api/instances/:id
 *   run             POST /api/instances/:id/run
 *   (resource)      GET  /api/runs?limit&cursor
 *   get_run         GET  /api/runs/:id?tail&wait
 *   cancel_run      POST /api/runs/:id/cancel
 *   finish_run      POST /api/runs/:id/finish
 *   evaluate        POST /api/instances/:id/evaluate
 *   get_assessment  GET  /api/assessment?format&since
 *   wake            POST /api/wake
 *   open_ui         POST /api/open
 *   (WebUI)         GET  /api/stats?period&granularity&process&agent&tz
 *   (WebUI)         GET  /api/skill?process
 *
 * Who calls is not in any body. The MCP server names its client in X-Harness-Client (and the
 * session it holds in X-Harness-Session); a request without it comes from a person (the WebUI).
 * The MCP server that a wake gives its agent also names the wake run in X-Harness-Wake, so the
 * runs that the agent starts are listed in that wake's started.
 */

import type { z } from "zod";
import { HTTP_STATUS, HarnessError, refuse, type Caller, type Harness } from "../harness/index.ts";
import {
  artifactsQuery,
  assessmentQuery,
  clientHeader,
  createInstanceRequest,
  evaluateRequest,
  finishRequest,
  instancesQuery,
  openRequest,
  runQuery,
  runRequest,
  runsQuery,
  skillQuery,
  statsQuery,
  updateInstanceRequest,
  wakeRequest,
} from "../shared/schema.ts";
import type {
  ArtifactsResponse,
  AssessmentMarkdownResponse,
  AssessmentResponse,
  CancelResponse,
  Failure,
  FinishResponse,
  InstanceResponse,
  InstancesResponse,
  ModelResponse,
  OpenResponse,
  RunDetailResponse,
  RunStartResponse,
  RunsResponse,
  SkillResponse,
  StatsResponse,
  WakeResponse,
} from "../shared/types.ts";

export interface ApiReply {
  status: number;
  body: { ok: true } | Failure;
}

/** What the API needs from the server around it. */
export interface ApiHost {
  /** The WebUI's URL with the token in the fragment, opened in a browser when asked. */
  openUi(options: { view?: string; open: boolean }): Promise<{ url: string; opened: boolean }>;
}

interface RouteContext {
  request: Request;
  url: URL;
  /** The route's id. */
  id: string;
  caller: Caller;
  /** Lets the request stay open longer than the server's idle timeout (a waiting get_run, a cancel). */
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
    throw refuse("invalid-request", "error.notJson", { detail: (error as Error).message });
  }
}

const describeIssues = (issues: readonly z.core.$ZodIssue[]): string =>
  issues
    .map((issue) => `${issue.path.length > 0 ? issue.path.join(".") : "(body)"}: ${issue.message}`)
    .join("; ");

/** Validates a body or query. With `judgments`, problems with the judgments are `invalid-judgment`. */
function parse<T extends z.ZodType>(
  schema: T,
  value: unknown,
  options: { judgments?: boolean } = {},
): z.output<T> {
  const parsed = schema.safeParse(value);
  if (parsed.success) return parsed.data;
  const issues = parsed.error.issues;
  const detail = describeIssues(issues);
  const judgments = options.judgments && issues.some((issue) => issue.path[0] === "judgments");
  throw judgments
    ? refuse("invalid-judgment", "error.judgment", { detail })
    : refuse("invalid-request", "error.request", { detail });
}

/** Who calls: the MCP client that X-Harness-Client names, or a person. */
export function callerOf(request: Request): Caller {
  const header = request.headers.get("x-harness-client");
  if (header === null) return { kind: "user" };
  let value: unknown;
  try {
    value = JSON.parse(decodeURIComponent(header));
  } catch (error) {
    throw refuse("invalid-request", "error.client", { detail: (error as Error).message });
  }
  const parsed = clientHeader.safeParse(value);
  if (!parsed.success)
    throw refuse("invalid-request", "error.client", {
      detail: describeIssues(parsed.error.issues),
    });
  return {
    kind: "agent",
    client: parsed.data,
    session: request.headers.get("x-harness-session") || null,
    wake: request.headers.get("x-harness-wake") || null,
  };
}

function routes(harness: Harness, host: ApiHost): Route[] {
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
      method: "GET",
      pattern: new RegExp(`^/api/instances/${id}$`),
      handle: ({ id: instance }) =>
        ok({ ok: true, instance: harness.instance(instance) } satisfies InstanceResponse),
    },
    {
      method: "POST",
      pattern: new RegExp(`^/api/instances/${id}/run$`),
      handle: async ({ request, id: instance, caller }) =>
        ok(
          {
            ok: true,
            ...(await harness.startRun(instance, parse(runRequest, await body(request)), caller)),
          } satisfies RunStartResponse,
          201,
        ),
    },
    {
      method: "POST",
      pattern: new RegExp(`^/api/instances/${id}/evaluate$`),
      handle: async ({ request, id: instance, caller }) =>
        ok({
          ok: true,
          ...harness.evaluate(
            instance,
            parse(evaluateRequest, await body(request), { judgments: true }),
            caller,
          ),
        } satisfies InstanceResponse),
    },
    {
      method: "GET",
      pattern: /^\/api\/runs$/,
      handle: ({ url }) =>
        ok({ ok: true, ...harness.runs(parse(runsQuery, query(url))) } satisfies RunsResponse),
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
      handle: async ({ request, id: run, keepOpen }) => {
        await body(request);
        keepOpen();
        return ok({ ok: true, ...(await harness.cancelRun(run)) } satisfies CancelResponse);
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
      handle: async ({ url }) => {
        const { format, since } = parse(assessmentQuery, query(url));
        return format === "markdown"
          ? ok({
              ok: true,
              markdown: await harness.assessmentMarkdown(since),
            } satisfies AssessmentMarkdownResponse)
          : ok({
              ok: true,
              assessment: await harness.assessment(since),
            } satisfies AssessmentResponse);
      },
    },
    {
      method: "GET",
      pattern: /^\/api\/stats$/,
      handle: ({ url }) => {
        const { tz, ...filter } = parse(statsQuery, query(url));
        return ok({ ok: true, ...harness.stats(filter, tz) } satisfies StatsResponse);
      },
    },
    {
      method: "GET",
      pattern: /^\/api\/skill$/,
      handle: ({ url }) =>
        ok({
          ok: true,
          ...harness.skill(parse(skillQuery, query(url)).process),
        } satisfies SkillResponse),
    },
    {
      method: "POST",
      pattern: /^\/api\/wake$/,
      handle: async ({ request, caller }) => {
        const result = await harness.wake(parse(wakeRequest, await body(request)), {
          kind: "request",
          caller,
        });
        return ok({ ok: true, ...result } satisfies WakeResponse, result.skipped ? 200 : 201);
      },
    },
    {
      method: "POST",
      pattern: /^\/api\/open$/,
      handle: async ({ request }) => {
        const options = parse(openRequest, await body(request));
        const opened = await host.openUi({
          open: options.open,
          ...(options.view ? { view: options.view } : {}),
        });
        return ok({ ok: true, ...opened } satisfies OpenResponse);
      },
    },
  ];
}

export type Api = (request: Request, url: URL, keepOpen: () => void) => Promise<ApiReply | null>;

const failure = (error: HarnessError): ApiReply => ({
  status: HTTP_STATUS[error.code],
  body: { ok: false, error: error.info } satisfies Failure,
});

/** The API over a harness. It answers `null` for a path it does not have. */
export function createApi(harness: Harness, host: ApiHost): Api {
  const table = routes(harness, host);
  return async (request, url, keepOpen) => {
    for (const route of table) {
      const match = route.pattern.exec(url.pathname);
      if (!match || route.method !== request.method) continue;
      try {
        return await route.handle({
          request,
          url,
          id: match[1] ?? "",
          caller: callerOf(request),
          keepOpen,
        });
      } catch (error) {
        if (error instanceof HarnessError) return failure(error);
        throw error;
      }
    }
    return null;
  };
}
