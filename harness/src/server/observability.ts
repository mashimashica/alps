/*
 * Optional runtime telemetry. ALPS records canonical run state in .alps-harness; OpenTelemetry is
 * an opt-in observation channel for diagnostics and correlation. A telemetry failure must never
 * stop the daemon, a run, or an assessment.
 */

import { createHash } from "node:crypto";

import { SpanStatusCode } from "@opentelemetry/api";
import { OTLPTraceExporter } from "@opentelemetry/exporter-trace-otlp-http";
import { resourceFromAttributes } from "@opentelemetry/resources";
import { BatchSpanProcessor, BasicTracerProvider } from "@opentelemetry/sdk-trace-base";

export interface ObservabilityStatus {
  enabled: boolean;
  exporter: "otlp-http" | "none";
  endpoint: string | null;
}

export interface Observability {
  status(): ObservabilityStatus;
  record(
    name: string,
    attributes: Record<string, string | number | boolean>,
  ): { traceId: string; spanId: string } | null;
  shutdown(): Promise<void>;
}

const truthy = (value: string | undefined): boolean =>
  value === "1" || value === "true" || value === "yes" || value === "on";

const exportedAttributeKeys = new Set([
  "alps.execution.method",
  "alps.headless",
  "alps.host.session",
  "alps.instance",
  "alps.launch",
  "alps.mcp.session",
  "alps.observation",
  "alps.process",
  "alps.run",
  "alps.run.agent",
  "alps.run.duration_ms",
  "alps.run.kind",
  "alps.run.status",
  "alps.tool.ok",
  "alps.tool.operation",
  "alps.ui.mode",
  "http.response.status_code",
]);

function workspaceId(workspace: string): string {
  return createHash("sha256").update(workspace).digest("hex").slice(0, 16);
}

function safeAttributes(
  attributes: Record<string, string | number | boolean>,
): Record<string, string | number | boolean> {
  const safe: Record<string, string | number | boolean> = {};
  for (const [key, value] of Object.entries(attributes)) {
    if (!exportedAttributeKeys.has(key)) continue;
    if (typeof value === "string") safe[key] = value.slice(0, 200);
    else safe[key] = value;
  }
  return safe;
}

function traceEndpoint(): string {
  if (process.env.OTEL_EXPORTER_OTLP_TRACES_ENDPOINT)
    return process.env.OTEL_EXPORTER_OTLP_TRACES_ENDPOINT;
  const base = process.env.OTEL_EXPORTER_OTLP_ENDPOINT;
  if (base) return `${base.replace(/\/$/, "")}/v1/traces`;
  return "http://127.0.0.1:4318/v1/traces";
}

export function createObservability(options: {
  workspace: string;
  version: string;
  log: (line: string) => void;
}): Observability {
  if (!truthy(process.env.ALPS_OTEL_ENABLED ?? process.env.ALPS_OTEL)) {
    return {
      status: () => ({ enabled: false, exporter: "none", endpoint: null }),
      record: () => null,
      shutdown: async () => {},
    };
  }
  const endpoint = traceEndpoint();
  try {
    const exporter = new OTLPTraceExporter({ url: endpoint });
    const id = workspaceId(options.workspace);
    const provider = new BasicTracerProvider({
      resource: resourceFromAttributes({
        "service.name": "alps-harness",
        "service.version": options.version,
        "alps.workspace.id": id,
      }),
      spanProcessors: [
        new BatchSpanProcessor(exporter, {
          scheduledDelayMillis: 200,
          exportTimeoutMillis: 1000,
          maxQueueSize: 256,
          maxExportBatchSize: 32,
        }),
      ],
    });
    const tracer = provider.getTracer("alps-harness", options.version);
    return {
      status: () => ({ enabled: true, exporter: "otlp-http", endpoint }),
      record(name, attributes) {
        try {
          const span = tracer.startSpan(name, { attributes: safeAttributes(attributes) });
          span.setStatus({ code: SpanStatusCode.OK });
          const context = span.spanContext();
          span.end();
          return { traceId: context.traceId, spanId: context.spanId };
        } catch (error) {
          options.log(`telemetry ignored: ${(error as Error).message}`);
          return null;
        }
      },
      async shutdown() {
        try {
          await provider.shutdown();
        } catch (error) {
          options.log(`telemetry shutdown ignored: ${(error as Error).message}`);
        }
      },
    };
  } catch (error) {
    options.log(`telemetry disabled: ${(error as Error).message}`);
    return {
      status: () => ({ enabled: false, exporter: "none", endpoint: null }),
      record: () => null,
      shutdown: async () => {},
    };
  }
}
