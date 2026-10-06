/** Object-oriented read model. Only recorded provenance or explicit work scopes create edges. */
import { createHash } from "node:crypto";
import type {
  AgentSessionObject,
  DesignSession,
  InstanceView,
  LaunchRecord,
  Process,
  ProcessApplicationObject,
  Run,
  WorkObject,
  WorkObjectRef,
  WorkObjectsResponse,
  WorkParticipation,
} from "../shared/types.ts";

export interface WorkObjectsInput {
  runs: readonly Run[];
  instances: readonly InstanceView[];
  designs: readonly DesignSession[];
  launches: readonly LaunchRecord[];
  processes: readonly Pick<Process, "id" | "name">[];
  unreadableRecords?: string[];
}

const key = (ref: WorkObjectRef): string => `${ref.kind}-${ref.id}`;
const unique = (values: readonly string[]): string[] => [...new Set(values)];
const title = (text: string | null, fallback: string): string =>
  text?.trim().replace(/\s+/g, " ").slice(0, 140) || fallback;
const sessionKey = (agent: string, id: string): string =>
  `session-${createHash("sha256").update(`${agent}\0${id}`).digest("hex").slice(0, 32)}`;

export function buildWorkObjects(input: WorkObjectsInput): WorkObjectsResponse {
  const runs = new Map(input.runs.map((run) => [run.id, run]));
  const instances = new Map(input.instances.map((instance) => [instance.id, instance]));
  const launchOfRun = new Map(
    input.launches.filter((launch) => launch.runId).map((launch) => [launch.runId!, launch]),
  );
  const parentRuns = new Map<string, string[]>();
  for (const run of input.runs)
    for (const child of run.started ?? [])
      parentRuns.set(child, [...(parentRuns.get(child) ?? []), run.id]);

  const works = new Map<string, WorkObject>();
  const applications = new Map<string, ProcessApplicationObject>();
  const participations = new Map<string, WorkParticipation>();
  const sessions = new Map<string, AgentSessionObject>();
  const explicit = new Map<string, string[]>();
  const alias = new Map<string, string>();
  const issues = [...(input.unreadableRecords ?? [])];
  const root = (
    origin: WorkObjectRef,
    request: string | null,
    kind: WorkObject["kind"],
    at: number | null,
    scope: WorkObject["scope"] = null,
  ): string => {
    const id = key(origin);
    if (!works.has(id))
      works.set(id, {
        id,
        origin,
        kind,
        title: title(request, `${origin.kind} · ${origin.id}`),
        request,
        scope,
        createdAt: at,
        updatedAt: at,
        status: "empty",
        applicationIds: [],
        participationIds: [],
        sessionIds: [],
        sources: [origin],
        report: "",
        reportSource: null,
      });
    return id;
  };

  // Roots identify the original request, including undelivered launches. A retry keeps its root.
  for (const launch of input.launches) {
    const id = root(
      { kind: "launch", id: launch.id },
      launch.request.request ?? launch.request.scope?.request ?? null,
      launch.request.kind === "assess" ? "assessment" : "work",
      launch.createdAt,
      launch.request.runs ?? null,
    );
    if (launch.request.workIds?.length) explicit.set(id, unique(launch.request.workIds));
    else if (launch.request.replacesLaunch)
      alias.set(id, `launch-${launch.request.replacesLaunch}`);
  }
  for (const design of input.designs) {
    const id = root(
      { kind: "design", id: design.id },
      design.request,
      "modeling",
      design.createdAt,
    );
    if (design.workIds?.length) explicit.set(id, unique(design.workIds));
  }
  for (const run of input.runs) {
    if (launchOfRun.has(run.id) || parentRuns.has(run.id) || run.kind === "process") continue;
    root(
      { kind: "run", id: run.id },
      run.request ?? run.scope?.request ?? null,
      run.kind === "assess" ? "assessment" : "work",
      run.createdAt,
      run.runs ?? null,
    );
  }

  // Explicit continuations may target a planned/orphan instance whose root otherwise would
  // not be discovered until after resolving runs. Unused candidates are filtered below.
  for (const instance of input.instances)
    root({ kind: "instance", id: instance.id }, null, "record", null);

  const resolveRoot = (id: string, visiting = new Set<string>()): string[] => {
    if (visiting.has(id)) return [];
    const next = new Set([...visiting, id]);
    const links = explicit.get(id) ?? (alias.has(id) ? [alias.get(id)!] : []);
    if (links.length) {
      const found = unique(links.flatMap((other) => resolveRoot(other, next)));
      if (found.length) return found;
      issues.push(id);
    }
    return works.has(id) ? [id] : [];
  };

  const runWorkCache = new Map<string, string[]>();
  const runWorks = (id: string, visiting = new Set<string>()): string[] => {
    const known = runWorkCache.get(id);
    if (known) return known;
    const run = runs.get(id);
    if (!run || visiting.has(id)) return [];
    const next = new Set([...visiting, id]);
    const launch = launchOfRun.get(id);
    let result: string[] = [];
    if (launch?.request.workIds?.length) result = resolveRoot(`launch-${launch.id}`);
    else if (run.execution?.resumedFrom) result = runWorks(run.execution.resumedFrom, next);
    else if (launch?.request.resumedFrom) result = runWorks(launch.request.resumedFrom, next);
    if (!result.length && launch) result = resolveRoot(`launch-${launch.id}`);
    if (!result.length)
      result = unique((parentRuns.get(id) ?? []).flatMap((parent) => runWorks(parent, next)));
    if (!result.length && works.has(`run-${id}`)) result = resolveRoot(`run-${id}`);
    const instance = run.instance ? instances.get(run.instance) : null;
    if (!result.length && instance?.createdBy) result = runWorks(instance.createdBy.run, next);
    if (!result.length && instance)
      result = [root({ kind: "instance", id: instance.id }, null, "record", run.createdAt)];
    runWorkCache.set(id, result);
    return result;
  };
  for (const run of input.runs) runWorks(run.id);

  const addSource = (workIds: string[], source: WorkObjectRef): void => {
    for (const id of workIds) {
      const work = works.get(id);
      if (work && !work.sources.some((ref) => key(ref) === key(source))) work.sources.push(source);
    }
  };
  for (const launch of input.launches) {
    const workIds = launch.runId ? runWorks(launch.runId) : resolveRoot(`launch-${launch.id}`);
    addSource(workIds, { kind: "launch", id: launch.id });
    if (!workIds.includes(`launch-${launch.id}`) && workIds.length)
      explicit.set(`launch-${launch.id}`, workIds);
  }

  for (const instance of input.instances) {
    let workIds = unique([
      ...instance.runs.flatMap((id) => runWorks(id)),
      ...(instance.createdBy ? runWorks(instance.createdBy.run) : []),
    ]);
    if (!workIds.length)
      workIds = [root({ kind: "instance", id: instance.id }, null, "record", null)];
    const process = input.processes.find((item) => item.id === instance.process);
    const subject = Object.values(instance.inputs).flat()[0];
    const name = `${process?.name ?? instance.process}${subject ? ` · ${subject}` : ""}`;
    const orphan = works.get(`instance-${instance.id}`);
    if (orphan) orphan.title = name;
    applications.set(`instance-${instance.id}`, {
      id: `instance-${instance.id}`,
      kind: "process",
      source: { kind: "instance", id: instance.id },
      processId: instance.process,
      descriptionSource: null,
      title: name,
      status: runs.get(instance.runs.at(-1) ?? "")?.status ?? "planned",
      workIds,
      participationIds: [],
      instance,
    });
    addSource(workIds, { kind: "instance", id: instance.id });
  }

  const sessionFor = (
    agent: string,
    reference: string | undefined,
    provider?: "claude" | "codex",
  ): string | null => {
    if (!reference) return null;
    const host = provider ?? `agent:${agent}`;
    const id = sessionKey(host, reference);
    if (!sessions.has(id))
      sessions.set(id, {
        id,
        provider: provider ?? null,
        agents: [],
        providerSessionId: reference,
        workIds: [],
        applicationIds: [],
        participationIds: [],
        links: [],
      });
    const session = sessions.get(id)!;
    if (!session.agents.includes(agent)) session.agents.push(agent);
    return id;
  };
  for (const run of input.runs) {
    const workIds = runWorks(run.id);
    let applicationId = run.instance ? `instance-${run.instance}` : null;
    if (run.kind === "assess") {
      applicationId = `assessment-${run.id}`;
      applications.set(applicationId, {
        id: applicationId,
        kind: "assessment",
        source: { kind: "run", id: run.id },
        processId: null,
        descriptionSource: "skills/assess-harness-records/SKILL.md",
        title: title(run.scope?.request ?? null, "Harness Record Assessment"),
        status: run.status,
        workIds,
        participationIds: [],
        instance: null,
      });
    }
    const id = `run-${run.id}`;
    participations.set(id, {
      id,
      source: { kind: "run", id: run.id },
      applicationId,
      sessionId: sessionFor(
        run.agent,
        run.execution?.session?.id ?? run.execution?.sessionId,
        run.execution?.provider,
      ),
      workIds,
      role:
        run.kind === "wake" ? "coordination" : run.kind === "assess" ? "assessment" : "execution",
      agent: run.agent,
      status: run.status,
      startedAt: run.startedAt,
      endedAt: run.endedAt,
      coverage: run.execution?.session?.coverage ?? "unverified",
    });
    addSource(workIds, { kind: "run", id: run.id });
  }
  for (const design of input.designs) {
    const workIds = resolveRoot(`design-${design.id}`);
    const applicationId = `design-${design.id}`;
    const id = `design-participation-${design.id}`;
    applications.set(applicationId, {
      id: applicationId,
      kind: "modeling",
      source: { kind: "design", id: design.id },
      processId: null,
      descriptionSource: "skills/design-process-description/SKILL.md",
      title: title(design.request, "Process Description Design"),
      status: design.status,
      workIds,
      participationIds: [],
      instance: null,
    });
    participations.set(id, {
      id,
      source: { kind: "design", id: design.id },
      applicationId,
      sessionId: sessionFor(
        design.agent,
        design.desktop?.sessionId,
        design.provider ?? design.desktop?.provider ?? undefined,
      ),
      workIds,
      role: "modeling",
      agent: design.agent,
      status: design.status,
      startedAt: design.createdAt,
      endedAt: ["applied", "failed", "canceled"].includes(design.status) ? design.updatedAt : null,
      coverage: design.desktop?.sessionId ? "reference-only" : "unverified",
    });
    addSource(workIds, { kind: "design", id: design.id });
  }

  // Build each direction from the same scoped participation, never a Cartesian join by session.
  for (const participation of participations.values()) {
    const application = participation.applicationId
      ? applications.get(participation.applicationId)
      : null;
    application?.participationIds.push(participation.id);
    for (const id of participation.workIds) works.get(id)?.participationIds.push(participation.id);
    if (participation.sessionId) {
      const session = sessions.get(participation.sessionId)!;
      session.participationIds.push(participation.id);
      session.workIds.push(...participation.workIds);
      if (application) session.applicationIds.push(application.id);
      for (const id of participation.workIds) works.get(id)?.sessionIds.push(session.id);
    }
  }
  for (const application of applications.values())
    for (const id of application.workIds) works.get(id)?.applicationIds.push(application.id);
  for (const run of input.runs) {
    const from = run.execution?.resumedFrom ?? launchOfRun.get(run.id)?.request.resumedFrom;
    const current = participations.get(`run-${run.id}`)?.sessionId;
    const previous = from ? participations.get(`run-${from}`)?.sessionId : null;
    if (current && previous && current !== previous)
      sessions.get(current)?.links.push({ sessionId: previous, kind: "handoff" });
  }
  for (const session of sessions.values()) {
    session.workIds = unique(session.workIds);
    session.applicationIds = unique(session.applicationIds);
  }
  const visible = [...works.values()].filter((work) => {
    if (work.participationIds.length || work.applicationIds.length) return true;
    return !explicit.has(work.id) && !alias.has(work.id) && work.origin.kind === "launch";
  });
  for (const work of visible) {
    work.applicationIds = unique(work.applicationIds);
    work.sessionIds = unique(work.sessionIds);
    const parts = work.participationIds.map((id) => participations.get(id)!);
    const launches = input.launches.filter((launch) =>
      work.sources.some((source) => source.kind === "launch" && source.id === launch.id),
    );
    work.status = parts.some((item) => ["running", "connected"].includes(item.status))
      ? "running"
      : parts.some((item) => ["pending", "needs-input", "ready"].includes(item.status)) ||
          launches.some((item) => ["pending", "starting"].includes(item.status))
        ? "waiting"
        : parts.length || launches.some((item) => ["failed", "canceled"].includes(item.status))
          ? "ended"
          : "empty";
    const times = [
      ...launches.map((launch) => launch.createdAt),
      ...parts.flatMap((part) => [part.startedAt, part.endedAt]),
    ].filter((at): at is number => at !== null);
    work.updatedAt = times.length ? Math.max(...times, work.createdAt ?? 0) : work.createdAt;
    const reports = work.sources.flatMap((source) => {
      if (source.kind === "run") {
        const run = runs.get(source.id);
        return run?.report ? [{ at: run.endedAt ?? run.startedAt, text: run.report, source }] : [];
      }
      if (source.kind === "design") {
        const design = input.designs.find((item) => item.id === source.id);
        return design?.proposal?.summary
          ? [{ at: design.updatedAt, text: design.proposal.summary, source }]
          : [];
      }
      return [];
    });
    const latest = reports.sort((a, b) => b.at - a.at)[0];
    work.report = latest?.text.slice(0, 20_000) ?? "";
    work.reportSource = latest?.source ?? null;
  }
  return {
    ok: true,
    works: visible.sort((a, b) => (b.updatedAt ?? 0) - (a.updatedAt ?? 0)),
    applications: [...applications.values()],
    sessions: [...sessions.values()],
    participations: [...participations.values()],
    coverage: {
      unidentifiedSessions: [...participations.values()].filter((part) => !part.sessionId).length,
      unreadableRecords: unique(issues),
    },
  };
}
