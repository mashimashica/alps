/*
 * The routes of the HTTP API. Each answers one tool of the MCP server, which relays to it, and the
 * WebUI uses the same routes. The safety checks (Host, token, Sec-Fetch-Site, JSON bodies) run in
 * http.ts before a route is chosen. The one body that is not JSON is that of the attachments a
 * person uploads with a request (multipart/form-data); the MCP server has no such tool.
 *
 *   (WebUI)            GET  /api/agents/:id/models?refresh
 *   get_model          GET  /api/model
 *   (WebUI)            POST /api/model
 *   (WebUI)            GET  /api/designs/capabilities
 *   (WebUI)            POST /api/designs
 *   (WebUI)            GET  /api/designs/:id
 *   (WebUI)            POST /api/designs/:id/open
 *   (WebUI/CLI)        POST /api/designs/:id/messages
 *   (design MCP)       POST /api/designs/:id/claim
 *   (design MCP)       GET  /api/designs/:id/context
 *   (design MCP)       POST /api/designs/:id/questions
 *   (design MCP)       POST /api/designs/:id/proposal
 *   (WebUI)            POST /api/designs/:id/cancel
 *   (WebUI)            POST /api/designs/:id/apply
 *   list_artifacts     GET  /api/artifacts?type&changedSince
 *   list_instances     GET  /api/instances?process&path&limit&cursor
 *   instantiate        POST /api/instances
 *   (resource)         GET  /api/instances/:id
 *   run                POST /api/instances/:id/run
 *   list_runs          GET  /api/runs?process&agent&status&kind&since&limit&cursor
 *   get_run            GET  /api/runs/:id?tail&wait
 *   (collector)        POST /api/runs/:id/observations
 *   cancel_run         POST /api/runs/:id/cancel
 *   finish_run         POST /api/runs/:id/finish
 *   evaluate           POST /api/instances/:id/evaluate
 *   get_assessment     GET  /api/assessment?format&since
 *   assess             POST /api/assess
 *   record_assessment  POST /api/assessments
 *   (WebUI)            GET  /api/assessments
 *   (WebUI)            GET  /api/assessments/:id
 *   (WebUI)            POST /api/assessments/:id/items/:n/review
 *   (WebUI)            POST /api/execution/mcp-config
 *   (local product)    POST /api/ui
 *   wake               POST /api/wake
 *   open_ui            POST /api/open
 *   (WebUI)            GET  /api/stats?period&granularity&process&agent&tz
 *   (WebUI)            GET  /api/skill?process
 *   (WebUI)            POST /api/attachments  (multipart/form-data)
 *
 * Who calls is not in any body. The MCP server names its client in X-Harness-Client (and the
 * session it holds in X-Harness-Session); a request without it comes from a person (the WebUI).
 * The MCP server that a wake gives its agent also names the wake run in X-Harness-Wake, so the
 * runs that the agent starts are listed in that wake's started; the one that an assessment gives
 * its agent names the assessment run in X-Harness-Assess, so what the agent records is that
 * run's.
 */

import type { z } from "zod";
import { Launches } from "./launches.ts";
import { artifactContent } from "../harness/artifact-content.ts";
import {
  HTTP_STATUS,
  HarnessError,
  refuse,
  type AttachedFile,
  type Caller,
  type Harness,
} from "../harness/index.ts";
import {
  MAX_ATTACHMENT_BYTES,
  MAX_ATTACHMENT_SIZE,
  MAX_ATTACHMENTS,
  safeFileName,
} from "../shared/requests.ts";
import {
  artifactsQuery,
  assessmentQuery,
  assessRequest,
  clientHeader,
  createInstanceRequest,
  evaluateRequest,
  finishRequest,
  installUiRequest,
  instancesQuery,
  openRequest,
  recordObservationRequest,
  recordAssessmentRequest,
  reviewRequest,
  runQuery,
  runRequest,
  runsQuery,
  skillQuery,
  statsQuery,
  updateInstanceRequest,
  updateModelRequest,
  createDesignRequest,
  designApplyRequest,
  designClaimRequest,
  designMessageRequest,
  designOpenRequest,
  designSubmitProposalRequest,
  designSubmitQuestionsRequest,
  wakeRequest,
  launchRequest,
  claimLaunchRequest,
} from "../shared/schema.ts";
import {
  PRODUCT_UI_CONTRACT,
  RUNTIME_CONTRACT,
  type RuntimeContractResponse,
} from "../shared/contract.ts";
import type {
  ArtifactsResponse,
  AttachmentsResponse,
  AssessResponse,
  AssessmentMarkdownResponse,
  AssessmentRecordResponse,
  AssessmentResponse,
  AssessmentsResponse,
  CancelResponse,
  DesignCapabilitiesResponse,
  DesignResponse,
  Failure,
  FinishResponse,
  InstanceResponse,
  InstancesResponse,
  InstallUiResponse,
  ModelResponse,
  ObservationResponse,
  OpenResponse,
  ExecutionMcpConfigSave,
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
  version: string;
  /** The WebUI's URL with the token in the fragment, opened in a browser when asked. */
  openUi(options: { view?: string; open: boolean }): Promise<{ url: string; opened: boolean }>;
  /** Attach a UI bundle to this daemon without restarting the runtime or active jobs. */
  installUi(entry: string): Promise<InstallUiResponse["ui"]>;
}

interface RouteContext {
  request: Request;
  url: URL;
  /** The route's id. */
  id: string;
  /** What the route's pattern matched after the id (an item's number). */
  rest: string[];
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

/** The most that a JSON body may be. */
export const MAX_JSON_BYTES = 1024 * 1024;
/**
 * The most that the body of an upload may be: one attachment at its limit, and the form around
 * it. The WebUI sends the files of a request one at a time.
 */
export const MAX_UPLOAD_BYTES = MAX_ATTACHMENT_BYTES + MAX_JSON_BYTES;

/** A limit as the messages say it. */
export const mebibytes = (bytes: number): string => `${Math.round(bytes / 1024 / 1024)} MiB`;

/**
 * The request's body, refused when it is longer than `limit`. A body that says it is longer is
 * read to its end, none of it kept, and refused then (http.ts). One that does not say its length
 * (chunked) is read to its end with no more than the limit kept, and refused then: a client that
 * stops sending on an early answer and sends its next request on the same connection would have
 * that request taken for the rest.
 */
async function bytesOf(request: Request, limit: number): Promise<Uint8Array<ArrayBuffer>> {
  const chunks: Uint8Array[] = [];
  let size = 0;
  if (request.body) {
    const reader = request.body.getReader();
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;
      size += value.byteLength;
      if (size <= limit) chunks.push(value);
    }
  }
  if (size > limit) throw refuse("too-large", "error.bodySize", { limit: mebibytes(limit) });
  const bytes = new Uint8Array(size);
  let at = 0;
  for (const chunk of chunks) {
    bytes.set(chunk, at);
    at += chunk.byteLength;
  }
  return bytes;
}

/** The request's body as text, refused when it is longer than a JSON body may be (1 MiB). */
export async function textOf(request: Request): Promise<string> {
  const bytes = await bytesOf(request, MAX_JSON_BYTES);
  return Buffer.from(bytes.buffer, bytes.byteOffset, bytes.byteLength).toString("utf8");
}

/** The request's JSON body; an empty body is `{}`. */
async function body(request: Request): Promise<unknown> {
  const text = await textOf(request);
  if (!text.trim()) return {};
  try {
    return JSON.parse(text) as unknown;
  } catch (error) {
    throw refuse("invalid-request", "error.notJson", { detail: (error as Error).message });
  }
}

/** A file's name as the form gives it: a part whose filename is empty comes without one. */
const nameOf = (file: Blob): string =>
  "name" in file && typeof file.name === "string" ? file.name : "";

/**
 * The files of an upload (multipart/form-data), read once all of them are within the limits: a
 * body of at most 21 MiB (no more of it is kept), with at most ten files, none larger than 20 MB.
 * The form's other fields are ignored.
 */
async function attachedFiles(request: Request): Promise<AttachedFile[]> {
  const bytes = await bytesOf(request, MAX_UPLOAD_BYTES);
  let form: FormData;
  try {
    form = await new Response(bytes, {
      headers: { "Content-Type": request.headers.get("content-type") ?? "" },
    }).formData();
  } catch (error) {
    throw refuse("invalid-request", "error.multipart", { detail: (error as Error).message });
  }
  const files: Blob[] = [];
  form.forEach((value) => {
    if (typeof value !== "string") files.push(value);
  });
  if (files.length === 0) throw refuse("invalid-request", "error.noFiles", {});
  if (files.length > MAX_ATTACHMENTS)
    throw refuse("invalid-request", "error.attachmentCount", {
      count: files.length,
      limit: MAX_ATTACHMENTS,
    });
  const large = files.find((file) => file.size > MAX_ATTACHMENT_BYTES);
  if (large)
    throw refuse("too-large", "error.attachmentSize", {
      name: safeFileName(nameOf(large)),
      limit: MAX_ATTACHMENT_SIZE,
    });
  return Promise.all(
    files.map(async (file) => ({
      name: nameOf(file),
      data: new Uint8Array(await file.arrayBuffer()),
    })),
  );
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
    assess: request.headers.get("x-harness-assess") || null,
  };
}

function routes(harness: Harness, host: ApiHost, launches: Launches): Route[] {
  const id = "([A-Za-z0-9_-]+)";
  const validateWorks = (ids: string[] | undefined): void => {
    if (!ids?.length) return;
    const known = new Set(harness.workObjects(launches.list()).works.map((work) => work.id));
    if (ids.some((value) => !known.has(value)))
      throw refuse("invalid-request", "error.request", {
        detail:
          "A continued work scope no longer exists. Reopen its recorded work before continuing.",
      });
  };
  return [
    {
      method: "GET",
      pattern: /^\/api\/work-objects$/,
      handle: () => ok(harness.workObjects(launches.list())),
    },
    {
      method: "GET",
      pattern: /^\/api\/artifact-content$/,
      handle: ({ url, caller }) => {
        if (caller.kind !== "user") throw refuse("invalid-request", "error.launchUser", {});
        return ok({
          ok: true,
          artifact: artifactContent(harness.root, url.searchParams.get("path") ?? ""),
        });
      },
    },
    {
      method: "GET",
      pattern: /^\/api\/execution$/,
      handle: async () => ok(await launches.capabilities()),
    },
    {
      method: "POST",
      pattern: /^\/api\/execution\/mcp-config$/,
      handle: async ({ request, caller }) => {
        await body(request);
        if (caller.kind !== "user") throw refuse("invalid-request", "error.launchUser", {});
        return ok(launches.saveMcpConfigs() satisfies ExecutionMcpConfigSave);
      },
    },
    {
      method: "POST",
      pattern: /^\/api\/ui$/,
      handle: async ({ request, caller }) => {
        if (caller.kind !== "user") throw refuse("invalid-request", "error.launchUser", {});
        const options = parse(installUiRequest, await body(request));
        return ok({
          ok: true,
          ui: await host.installUi(options.entry),
        } satisfies InstallUiResponse);
      },
    },
    {
      method: "GET",
      pattern: /^\/api\/contract$/,
      handle: () =>
        ok({
          ok: true,
          contract: RUNTIME_CONTRACT,
          uiContract: PRODUCT_UI_CONTRACT,
          runtime: { version: host.version, workspace: harness.root },
        } satisfies RuntimeContractResponse),
    },
    {
      method: "GET",
      pattern: /^\/api\/launches$/,
      handle: () => ok({ ok: true, launches: launches.list() }),
    },
    {
      method: "POST",
      pattern: /^\/api\/launches$/,
      handle: async ({ request, caller }) => {
        if (caller.kind !== "user") throw refuse("invalid-request", "error.launchUser", {});
        const options = parse(launchRequest, await body(request));
        validateWorks(options.workIds);
        return ok(await launches.submit(options), 201);
      },
    },
    {
      method: "GET",
      pattern: new RegExp(`^/api/launches/${id}$`),
      handle: async ({ id }) => ok(await launches.answer(id)),
    },
    {
      method: "POST",
      pattern: new RegExp(`^/api/launches/${id}/claim$`),
      handle: async ({ id, request, caller }) => {
        const options = parse(claimLaunchRequest, await body(request));
        return ok(await launches.claim(id, caller, options.sessionId, options.workspace));
      },
    },
    {
      method: "POST",
      pattern: new RegExp(`^/api/launches/${id}/open$`),
      handle: async ({ id, request, caller }) => {
        await body(request);
        if (caller.kind !== "user") throw refuse("invalid-request", "error.launchUser", {});
        return ok(await launches.open(id));
      },
    },
    {
      method: "POST",
      pattern: new RegExp(`^/api/launches/${id}/cancel$`),
      handle: async ({ id, request, caller }) => {
        await body(request);
        if (caller.kind !== "user") throw refuse("invalid-request", "error.launchUser", {});
        return ok({ ok: true, launch: launches.cancel(id) });
      },
    },
    {
      method: "POST",
      pattern: new RegExp(`^/api/runs/${id}/terminal$`),
      handle: async ({ id, request, caller }) => {
        await body(request);
        if (caller.kind !== "user") throw refuse("invalid-request", "error.launchUser", {});
        await launches.openLog(id);
        return ok({ ok: true });
      },
    },
    {
      method: "GET",
      pattern: /^\/api\/model$/,
      handle: async () => ok({ ok: true, model: await harness.model() } satisfies ModelResponse),
    },
    {
      method: "POST",
      pattern: /^\/api\/model$/,
      handle: async ({ request, caller }) => {
        if (caller.kind !== "user") throw refuse("invalid-request", "error.launchUser", {});
        return ok({
          ok: true,
          model: await harness.updateModel(parse(updateModelRequest, await body(request))),
        } satisfies ModelResponse);
      },
    },
    {
      method: "GET",
      pattern: new RegExp(`^/api/agents/${id}/models$`),
      handle: async ({ id: agent, url }) =>
        ok(await harness.agentModels(agent, url.searchParams.get("refresh") === "1")),
    },
    {
      method: "GET",
      pattern: /^\/api\/designs\/capabilities$/,
      handle: async ({ caller }) => {
        if (caller.kind !== "user") throw refuse("invalid-request", "error.launchUser", {});
        return ok((await harness.designCapabilities()) satisfies DesignCapabilitiesResponse);
      },
    },
    {
      method: "GET",
      pattern: /^\/api\/designs$/,
      handle: async ({ caller, url }) => {
        if (caller.kind !== "user") throw refuse("invalid-request", "error.launchUser", {});
        const offset = Number(url.searchParams.get("offset") ?? "0");
        if (!Number.isSafeInteger(offset) || offset < 0)
          throw refuse("invalid-request", "error.request", {
            detail: "offset must be a non-negative integer",
          });
        return ok(harness.designs(offset));
      },
    },
    {
      method: "POST",
      pattern: /^\/api\/designs$/,
      handle: async ({ request, caller }) => {
        if (caller.kind !== "user") throw refuse("invalid-request", "error.launchUser", {});
        const options = parse(createDesignRequest, await body(request));
        validateWorks(options.workIds);
        return ok((await harness.createDesign(options)) satisfies DesignResponse, 201);
      },
    },
    {
      method: "GET",
      pattern: new RegExp(`^/api/designs/${id}$`),
      handle: async ({ id: design, caller }) => {
        if (caller.kind !== "user") throw refuse("invalid-request", "error.launchUser", {});
        return ok((await harness.design(design)) satisfies DesignResponse);
      },
    },
    {
      method: "POST",
      pattern: new RegExp(`^/api/designs/${id}/open$`),
      handle: async ({ id: design, request, caller }) => {
        if (caller.kind !== "user") throw refuse("invalid-request", "error.launchUser", {});
        return ok(
          (await harness.openDesign(
            design,
            parse(designOpenRequest, await body(request)),
          )) satisfies DesignResponse,
        );
      },
    },
    {
      method: "POST",
      pattern: new RegExp(`^/api/designs/${id}/claim$`),
      handle: async ({ id: design, request, caller }) =>
        ok(
          (await harness.claimDesign(
            design,
            parse(designClaimRequest, await body(request)),
            caller,
          )) satisfies DesignResponse,
        ),
    },
    {
      method: "GET",
      pattern: new RegExp(`^/api/designs/${id}/context$`),
      handle: async ({ id: design, caller }) =>
        ok((await harness.designContext(design, caller)) satisfies DesignResponse),
    },
    {
      method: "POST",
      pattern: new RegExp(`^/api/designs/${id}/questions$`),
      handle: async ({ id: design, request, caller }) =>
        ok(
          (await harness.submitDesignQuestions(
            design,
            parse(designSubmitQuestionsRequest, await body(request)),
            caller,
          )) satisfies DesignResponse,
        ),
    },
    {
      method: "POST",
      pattern: new RegExp(`^/api/designs/${id}/proposal$`),
      handle: async ({ id: design, request, caller }) =>
        ok(
          (await harness.submitDesignProposal(
            design,
            parse(designSubmitProposalRequest, await body(request)),
            caller,
          )) satisfies DesignResponse,
        ),
    },
    {
      method: "POST",
      pattern: new RegExp(`^/api/designs/${id}/messages$`),
      handle: async ({ id: design, request, caller }) => {
        if (caller.kind !== "user") throw refuse("invalid-request", "error.launchUser", {});
        return ok(
          (await harness.messageDesign(
            design,
            parse(designMessageRequest, await body(request)),
          )) satisfies DesignResponse,
        );
      },
    },
    {
      method: "POST",
      pattern: new RegExp(`^/api/designs/${id}/cancel$`),
      handle: async ({ id: design, request, caller }) => {
        await body(request);
        if (caller.kind !== "user") throw refuse("invalid-request", "error.launchUser", {});
        return ok((await harness.cancelDesign(design)) satisfies DesignResponse);
      },
    },
    {
      method: "POST",
      pattern: new RegExp(`^/api/designs/${id}/apply$`),
      handle: async ({ id: design, request, caller }) => {
        if (caller.kind !== "user") throw refuse("invalid-request", "error.launchUser", {});
        return ok(
          (await harness.applyDesign(
            design,
            parse(designApplyRequest, await body(request)),
          )) satisfies DesignResponse,
        );
      },
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
      handle: async ({ request, caller }) => {
        const given = await body(request);
        // One of two shapes; checking against the one meant gives the useful messages.
        const update = given !== null && typeof given === "object" && "instance" in given;
        const result = harness.instantiate(
          parse(update ? updateInstanceRequest : createInstanceRequest, given),
          caller,
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
      pattern: new RegExp(`^/api/runs/${id}/observations$`),
      handle: async ({ request, id: run }) =>
        ok(
          {
            ok: true,
            observation: harness.recordObservation(
              run,
              parse(recordObservationRequest, await body(request)),
            ),
          } satisfies ObservationResponse,
          201,
        ),
    },
    {
      method: "POST",
      pattern: new RegExp(`^/api/runs/${id}/cancel$`),
      handle: async ({ request, id: run, keepOpen, caller }) => {
        await body(request);
        keepOpen();
        return ok({ ok: true, ...(await harness.cancelRun(run, caller)) } satisfies CancelResponse);
      },
    },
    {
      method: "POST",
      pattern: new RegExp(`^/api/runs/${id}/finish$`),
      handle: async ({ request, id: run, caller }) => {
        const execution = harness.runExecution(run);
        if (
          execution &&
          execution.method !== "cli" &&
          (caller.kind !== "agent" ||
            !caller.session ||
            harness.externalRunFor(caller.session)?.id !== run)
        )
          throw refuse("invalid-request", "error.externalSession", {});
        return ok({
          ok: true,
          ...harness.finishRun(run, parse(finishRequest, await body(request))),
        } satisfies FinishResponse);
      },
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
      method: "POST",
      pattern: /^\/api\/assess$/,
      handle: async ({ request, caller }) =>
        ok(
          {
            ok: true,
            ...(await harness.assess(parse(assessRequest, await body(request)), caller)),
          } satisfies AssessResponse,
          201,
        ),
    },
    {
      method: "GET",
      pattern: /^\/api\/assessments$/,
      handle: () =>
        ok({ ok: true, assessments: harness.assessments() } satisfies AssessmentsResponse),
    },
    {
      method: "POST",
      pattern: /^\/api\/assessments$/,
      handle: async ({ request, caller }) =>
        ok(
          {
            ok: true,
            assessment: harness.recordAssessment(
              parse(recordAssessmentRequest, await body(request)),
              caller,
            ),
          } satisfies AssessmentRecordResponse,
          201,
        ),
    },
    {
      method: "GET",
      pattern: new RegExp(`^/api/assessments/${id}$`),
      handle: ({ id: assessment }) =>
        ok({
          ok: true,
          assessment: harness.assessmentRecord(assessment),
        } satisfies AssessmentRecordResponse),
    },
    {
      method: "POST",
      pattern: new RegExp(`^/api/assessments/${id}/items/(\\d+)/review$`),
      handle: async ({ request, id: assessment, rest, caller }) =>
        ok({
          ok: true,
          assessment: harness.review(
            assessment,
            Number(rest[0]),
            parse(reviewRequest, await body(request)),
            caller,
          ),
        } satisfies AssessmentRecordResponse),
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
      pattern: /^\/api\/attachments$/,
      handle: async ({ request }) =>
        ok(
          {
            ok: true,
            paths: harness.attach(await attachedFiles(request)),
          } satisfies AttachmentsResponse,
          201,
        ),
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

const designAllowedForAgent = (path: string, method: string): boolean => {
  if (
    method === "GET" &&
    (path === "/api/model" || path === "/api/artifacts" || path === "/api/skill")
  )
    return true;
  return /^\/api\/designs\/[^/]+\/(claim|context|questions|proposal)$/.test(path);
};

const failure = (error: HarnessError): ApiReply => ({
  status: HTTP_STATUS[error.code],
  body: { ok: false, error: error.info } satisfies Failure,
});

/** The API over a harness. It answers `null` for a path it does not have. */
export function createApi(harness: Harness, host: ApiHost): Api {
  const table = routes(harness, host, new Launches(harness));
  return async (request, url, keepOpen) => {
    for (const route of table) {
      const match = route.pattern.exec(url.pathname);
      if (!match || route.method !== request.method) continue;
      const caller = harness.externalCaller(callerOf(request));
      try {
        if (
          caller.kind === "agent" &&
          caller.session &&
          harness.externalDesignFor(caller.session) &&
          !designAllowedForAgent(url.pathname, request.method)
        )
          throw refuse("invalid-request", "error.designOnly", {});
        const reply = await route.handle({
          request,
          url,
          id: match[1] ?? "",
          rest: match.slice(2).map((part) => part ?? ""),
          caller,
          keepOpen,
        });
        harness.observeTool(caller, `${request.method} ${url.pathname}`, true, reply.status);
        return reply;
      } catch (error) {
        if (caller.kind === "agent")
          harness.observeTool(caller, `${request.method} ${url.pathname}`, false, 500);
        if (error instanceof HarnessError) return failure(error);
        throw error;
      }
    }
    return null;
  };
}
