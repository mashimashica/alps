/*
 * What the harness says, in English and Japanese. The server answers a failure with the key and
 * arguments of its message besides the English text, and records what it writes itself in a run
 * (its own events and the run's error) the same way, so each client puts it in its own language:
 * the MCP server in the workspace's `language` (alps-harness.yaml), the WebUI in the person's.
 * The MCP server's own texts (the summary that follows each tool result) are here too, and so is
 * what the demo agent writes into the workspace, which follows the workspace's language.
 */

import type { Language, RunStatus } from "./types.ts";

/** A value in a message. */
export type MessageArg = string | number | boolean;

const plural = (count: number, one: string, many = `${one}s`): string =>
  `${count} ${count === 1 ? one : many}`;

const STATUS_EN: Record<RunStatus, string> = {
  running: "has not ended yet (running)",
  succeeded: "succeeded",
  failed: "failed",
  canceled: "was canceled",
  interrupted: "was interrupted",
};

const STATUS_JA: Record<RunStatus, string> = {
  running: "まだ終わっていない（running）",
  succeeded: "正常に終了した（succeeded）",
  failed: "異常終了した（failed）",
  canceled: "中止された（canceled）",
  interrupted: "中断された（interrupted）",
};

const statusOf = (status: string, words: Record<RunStatus, string>): string =>
  words[status as RunStatus] ?? status;

type EndStatus = Exclude<RunStatus, "running">;

const END_EN: Record<EndStatus, string> = {
  succeeded: "Succeeded",
  failed: "Failed",
  canceled: "Canceled",
  interrupted: "Interrupted",
};

const END_JA: Record<EndStatus, string> = {
  succeeded: "正常終了",
  failed: "異常終了",
  canceled: "中止",
  interrupted: "中断",
};

/** What woke a wake run: a schedule (its cron), an MCP client's request (its name), or a request. */
type WokenBy = { by: "schedule" | "client" | "request"; cron: string; client: string };

const wokenEn = (a: WokenBy): string =>
  a.by === "schedule"
    ? `by the schedule "${a.cron}"`
    : a.by === "client"
      ? `on request of ${a.client}`
      : "on request";

const wokenJa = (a: WokenBy): string =>
  a.by === "schedule"
    ? `スケジュール「${a.cron}」による`
    : a.by === "client"
      ? `${a.client} の求めによる`
      : "求めによる";

const TOKEN_NOTE_EN =
  "The part after # is the access token: give the URL only to the person who asked for it.";
const TOKEN_NOTE_JA = "# の後ろは合い言葉なので、URL は求めた本人にだけ渡すこと。";

const en = {
  "error.launchProcess": (a: { process: string }) => `Process ${a.process} is not in this model.`,
  "error.externalSession": () => "Connect the ALPS MCP server before starting this request.",
  "error.externalConnected": () =>
    "This connection or conversation already has active work. Finish it before starting another request.",
  "error.externalIdentity": () =>
    "Reconnect the same recorded conversation to continue this attempt.",
  "error.launchMissing": () => "This saved request could not be found.",
  "error.launchChanged": () =>
    "This request has already been saved with different conditions. Start a new request.",
  "error.launchModel": () => "Choose the model and effort in the application or terminal.",
  "error.launchProvider": () => "This agent does not support this start method.",
  "error.desktopUnavailable": () =>
    "Install the desktop application before using this start method.",
  "error.terminalUnavailable": () => "Opening a native terminal is currently supported on macOS.",
  "error.launchClaim": () =>
    "This request is no longer waiting to start. Check its record before trying again.",
  "error.launchClient": (a: { agent: string }) => `Start this request from ${a.agent}.`,
  "error.launchWakeRunning": (a: { run: string }) =>
    `Orchestration ${a.run} is still running. This request was not started.`,
  "error.launchFailed": () => "Could not start this request.",
  "error.launchUser": () => "Start or open this request from the ALPS interface.",
  "error.launchWorkspace": (a: { workspace: string }) =>
    `Check your working directory and reconnect from ${a.workspace}. The request has not confirmed this project.`,
  "error.resumeRunning": () => "Wait for the current run to end before resuming this conversation.",
  "error.resumeMissing": () => "No saved conversation id is available for this run.",
  "error.nativeOpen": () => "The application could not be opened. The saved request is kept.",
  "error.uiUnavailable": () =>
    "The WebUI could not be prepared for this harness server. Check the server log and try again.",
  "done.launch": (a: { run: string }) =>
    `Started attempt ${a.run} in this conversation. Follow the returned prompt and finish with finish_run.`,

  /* ---------- failures of the harness ---------- */
  "error.model": (a: { detail: string }) => a.detail,
  "error.modelChanged": () =>
    "The process model changed while this form was open. Review the latest model and save again.",
  "error.noDesign": (a: { id: string }) => `No design session ${a.id}.`,
  "error.designRunning": (a: { id: string }) =>
    `Design session ${a.id} is still running. Wait for it or cancel it before continuing.`,
  "error.designNotReady": (a: { id: string }) =>
    `Design session ${a.id} has no proposal ready to apply.`,
  "error.designEnded": (a: { id: string; status: string }) =>
    `Design session ${a.id} already ended (${a.status}). Start a new design session.`,
  "error.designAgent": (a: { agents: string }) =>
    `Process design needs Claude Code or Codex. Available design agents: ${a.agents || "none"}.`,
  "error.designClient": (a: { agent: string }) =>
    `This design session is for ${a.agent}; connect from that provider's desktop app.`,
  "error.designMethod": () =>
    "This design session uses another conversation path. Start a new design session with the intended method.",
  "error.designOnly": () =>
    "This connection is for model construction. Submit the model and Skill bundle through the design tools. Business execution is not available in this conversation.",
  "error.designWorkspace": (a: { workspace: string }) =>
    `Check your working directory and reconnect from ${a.workspace}. The design connection has not confirmed this project.`,
  "error.designReference": (a: { path: string; reason: string }) =>
    `Reference ${a.path} cannot be used for design: ${a.reason}.`,
  "error.designSources": () =>
    "The required design-process-description, design-agent-work-system, and skill-creator sources are not all available.",
  "error.stopping": () => "The harness server is stopping. Call again once it has restarted.",
  "error.noProcess": (a: { name: string; processes: string }) =>
    `No Process "${a.name}" in the model. Its Processes are: ${a.processes}.`,
  "error.noType": (a: { name: string; types: string }) =>
    `No Artifact type "${a.name}" in the model. Its types are: ${a.types}.`,
  "error.noInstance": (a: { id: string }) => `No instance ${a.id}.`,
  "error.noRun": (a: { id: string }) => `No run ${a.id}.`,
  "error.runRecord": (a: { id: string }) =>
    `The record of run ${a.id} (runs/${a.id}.json) is missing or unreadable.`,
  "error.emptyPath": (a: { where: string; path: string }) =>
    `${a.where}: "${a.path}" names no file or directory in the workspace.`,
  "error.outside": (a: { where: string; path: string; root: string }) =>
    `${a.where}: ${a.path} is outside the workspace (${a.root}). Instances and requests name only paths inside it.`,
  "error.records": (a: { where: string; path: string }) =>
    `${a.where}: ${a.path} is in .alps-harness/, the harness's own records. Instances and requests name only the workspace's own files.`,
  "error.pattern": (a: { where: string; path: string }) =>
    `${a.where}: ${a.path} is a pattern. The inputs of an instance are concrete paths: name each file or directory (list_artifacts lists the candidates).`,
  "error.notInput": (a: { type: string; process: string; allowed: string }) =>
    `inputs: ${a.type} is not an input or control of ${a.process}. They are: ${a.allowed || "none"}.`,
  "error.notOutput": (a: { type: string; process: string; outputs: string }) =>
    `outputs: ${a.type} is not an output of ${a.process}. Its outputs are: ${a.outputs || "none"}.`,
  "error.noOutcome": (a: { where: string; process: string; count: number; outcome: number }) =>
    `${a.where}${a.process} has ${plural(a.count, "Outcome")} (numbered from 0); there is no Outcome ${a.outcome}.`,
  "error.judgedTwice": (a: { outcome: number }) => `Outcome ${a.outcome} is judged twice.`,
  "error.agentModels": (a: { agent: string; detail: string }) =>
    `Cannot read ${a.agent}'s models: ${a.detail}`,
  "error.agentSelection": (a: { agent: string; detail: string }) =>
    `Cannot use these settings for ${a.agent}: ${a.detail}`,
  "error.noAgent": (a: { agent: string; agents: string }) =>
    `No agent "${a.agent}" in this workspace. Its agents are: ${a.agents}.`,
  "error.selfDisabled": (a: { agents: string }) =>
    `The self mode is off in this workspace (agents.self is false in alps-harness.yaml). Its agents are: ${a.agents}.`,
  "error.agentUnavailable": (a: { agent: string; reason: string }) =>
    `${a.agent} cannot be started: ${a.reason}.`,
  "error.wakeAgent": (a: { agent: string; agents: string }) =>
    `${a.agent} cannot be woken: a wake needs the harness's MCP server, which the harness can give to Claude Code (--mcp-config) and Codex (-c mcp_servers) only. The agents that can be woken here: ${a.agents || "none"}.`,
  "error.planOnly": (a: { run: string }) =>
    `Wake run ${a.run} plans only (runs: plan): its agent instantiates what it plans and starts no run and no wake, so that the requester reviews the plan first. Report the plan with finish_run.`,
  "error.running": (a: { run: string; instance: string }) =>
    `Run ${a.run} of instance ${a.instance} has not ended. Wait for it (get_run with wait) or cancel it (cancel_run).`,
  "error.notSelf": (a: { run: string; agent: string }) =>
    `Run ${a.run} is a ${a.agent} run. finish_run ends only the self and wake runs that the calling session performs.`,
  "error.ended": (a: { run: string; status: string }) =>
    `Run ${a.run} has already ended (${a.status}). See it with get_run.`,
  "error.nothingToJudge": (a: { instance: string }) =>
    `Instance ${a.instance} has no run to evaluate. Run it first.`,
  "error.judgeRunning": (a: { run: string; instance: string }) =>
    `Run ${a.run} of instance ${a.instance} has not ended. Evaluate its results once it has (get_run with wait).`,
  "error.notJson": (a: { detail: string }) => `The body is not JSON: ${a.detail}`,
  "error.request": (a: { detail: string }) => `The request does not fit: ${a.detail}`,
  "error.judgment": (a: { detail: string }) => `The judgments do not fit: ${a.detail}`,
  "error.client": (a: { detail: string }) =>
    `The X-Harness-Client header is not {name, version} as JSON: ${a.detail}`,
  "error.noSkill": (a: { process: string }) => `${a.process} has no readable SKILL.md.`,
  "error.noAttachment": (a: { where: string; path: string }) =>
    `${a.where}: ${a.path} does not exist in the workspace. A request attaches files and directories that exist there.`,
  "error.attachmentCount": (a: { count: number; limit: number }) =>
    `Sent ${plural(a.count, "file")}; one request attaches at most ${a.limit}.`,
  "error.attachmentSize": (a: { name: string; limit: string }) =>
    `${a.name} is larger than ${a.limit}, the most that one attachment may be. Put a larger file in the workspace and attach its path.`,
  "error.noFiles": () => "The body holds no file to attach.",
  "error.multipart": (a: { detail: string }) =>
    `The body is not a form with files (multipart/form-data): ${a.detail}`,
  "error.attachmentNames": (a: { name: string; folder: string; limit: number }) =>
    `${a.folder} already holds ${a.name} and that name with each of -2 to -${a.limit}. Rename the file, or move the others out of the directory.`,
  "error.attachmentsDir": (a: { folder: string; detail: string }) =>
    `The attachments cannot be saved in ${a.folder}: something other than a directory (a file, or a symlink that leads nowhere) is on its path (${a.detail}). Move it, or name another directory in attachments (alps-harness.yaml).`,
  "error.assessOnly": (a: { run: string }) =>
    `Run ${a.run} is an assessment (assess): its agent reads the records and records what it finds with record_assessment; it makes no instance, starts no run or wake, and neither evaluates nor cancels. Report with finish_run.`,
  "error.assessAgent": (a: { agent: string; agents: string }) =>
    `${a.agent} cannot assess: an assessment needs the harness's MCP server, which the harness can give to Claude Code (--mcp-config) and Codex (-c mcp_servers) only, or a session that performs it itself (self). The agents that can assess here: ${a.agents || "none"}.`,
  "error.assessing": (a: { run: string }) =>
    `Assessment run ${a.run} has not ended, and one assessment runs at a time. Wait for it (get_run with wait) or cancel it (cancel_run).`,
  "error.noAssessRun": () =>
    "record_assessment records the result of a running assessment run, for the agent that performs it: the agent that assess started, or the session that started one with the agent self. The caller performs none.",
  "error.selfAssess": () =>
    "With the agent self, the MCP session that asks performs the assessment, and this request comes from no MCP client. Choose another agent, or call assess through the harness's MCP server.",
  "error.noEvidence": (a: { n: number }) =>
    `Item ${a.n} gives no evidence. Every item but an unverified one rests on records: a run, an instance, an evaluation, a cut of the statistics, an event of a log, or a path.`,
  "error.evidenceRun": (a: { n: number; run: string }) =>
    `Item ${a.n} cites run ${a.run}, which the records do not have.`,
  "error.evidenceInstance": (a: { n: number; instance: string }) =>
    `Item ${a.n} cites instance ${a.instance}, which the records do not have.`,
  "error.evidenceEvaluation": (a: { n: number; instance: string }) =>
    `Item ${a.n} cites the evaluation of instance ${a.instance}, which has none.`,
  "error.evidenceObservation": (a: { n: number; observation: string }) =>
    `Item ${a.n} cites observation ${a.observation}, which the records do not have.`,
  "error.evidenceLog": (a: { n: number; run: string; event: number; events: number }) =>
    `Item ${a.n} cites event ${a.event} of run ${a.run}, whose log has ${plural(a.events, "event")} (numbered from 1).`,
  "error.evidencePath": (a: { n: number; path: string }) =>
    `Item ${a.n} cites ${a.path}, which does not exist in the workspace.`,
  "error.evidenceProcess": (a: { n: number; name: string }) =>
    `Item ${a.n} cites the statistics of the Process ${a.name}, which the model does not have.`,
  "error.itemSubject": (a: { n: number; kind: string; name: string }) =>
    `Item ${a.n} is about ${a.kind === "process" ? "the Process" : a.kind === "artifact" ? "the Artifact type" : "the instance"} ${a.name}, which the workspace does not have.`,
  "error.noAssessment": (a: { id: string }) => `No assessment ${a.id}.`,
  "error.noItem": (a: { id: string; n: number; count: number }) =>
    `Assessment ${a.id} has ${plural(a.count, "item")} (numbered from 1); there is no item ${a.n}.`,
  "error.assessmentOpen": (a: { id: string }) =>
    `Assessment ${a.id} is still being made: its run has not ended. Review it once the run has.`,
  "error.reviewByPerson": () =>
    "Only a person reviews the items of an assessment (in the WebUI): an agent does not adopt what it found.",

  /* ---------- rejections of the HTTP layer ---------- */
  "error.host": () => "This host name is not accepted.",
  "error.crossSite": () => "The API accepts requests only from the harness's own page.",
  "error.token": () =>
    "The token is missing or wrong. Open the URL that alps-harness serve printed (…/#token=…).",
  "error.mediaType": () => "Send the request body as JSON.",
  "error.multipartType": () => "Send the attachments as multipart/form-data.",
  "error.bodySize": (a: { limit: string }) => `The request body is larger than ${a.limit}.`,
  "error.route": (a: { method: string; path: string }) => `${a.method} ${a.path} does not exist.`,
  "error.internal": () => "The server failed to handle the request.",

  /* ---------- failures of the MCP server ---------- */
  "error.noWorkspace": (a: { start: string }) =>
    `No alps-harness.yaml or process-model.yaml in ${a.start} or its parent directories. Pass the project's directory in ALPS_WORKSPACE, or start the harness in that directory; the workspace is the directory that holds one of these files.`,
  "error.unreachable": (a: { port: number; serverJson: string; detail: string }) =>
    `The harness server could not be reached or started (port ${a.port}, ${a.serverJson}): ${a.detail}`,

  /* ---------- findings of the assessment ---------- */
  "finding.skillMissing": (a: { process: string; location: string }) =>
    `The Skill declared for ${a.process} (${a.location}) is not a readable SKILL.md.`,
  "finding.awaiting": (a: { run: string; status: string }) =>
    `Run ${a.run} ended (${a.status}) and its results have no judgment yet.`,
  "finding.stale": (a: { run: string; paths: string }) =>
    `The judgment of run ${a.run} no longer rests on the workspace: ${a.paths} changed since the run used them.`,
  "finding.noSkill": (a: { process: string }) =>
    `No SKILL.md is found for ${a.process}: its runs get only the Process's description from the model.`,
  "finding.skillChanged": (a: { process: string; run: string; path: string }) =>
    `${a.path} changed after run ${a.run} of ${a.process} used it: no run has used the Skill as it is now.`,
  "finding.noLocation": (a: { type: string }) =>
    `The Artifact type ${a.type} has no location (artifacts in alps-harness.yaml): its Artifacts are not listed, and runs are given no place for them.`,
  "finding.notProduced": (a: { type: string; consumers: string }) =>
    `No Process produces ${a.type}; it comes from outside the model (read by ${a.consumers}).`,
  "finding.notRead": (a: { type: string; producers: string }) =>
    `No Process reads ${a.type} (produced by ${a.producers}).`,
  "finding.unused": (a: { type: string }) => `No Process produces or reads ${a.type}.`,
  "finding.agentUnavailable": (a: { agent: string; reason: string }) =>
    `${a.agent} cannot be started: ${a.reason}.`,
  "finding.sharedOrigin": (a: { path: string; runs: string }) =>
    `Which run made ${a.path} cannot be told: runs ${a.runs} ran at the same time, and each holds its change as an output.`,

  /* ---------- what the MCP tools report on success ---------- */
  "done.model": (a: { name: string; processes: number; types: number }) =>
    `The model "${a.name}" has ${plural(a.processes, "Process", "Processes")} and ${plural(a.types, "Artifact type")}. Read each SKILL.md and Artifact with your own file tools.`,
  "done.artifacts": (a: { count: number; truncated: boolean }) =>
    `${plural(a.count, "Artifact")}.${a.truncated ? " A location had more matches than one scan reads (truncated), so the list is incomplete." : ""}`,
  "done.instances": (a: { count: number; next: string }) =>
    `${plural(a.count, "instance")}.${a.next ? ` More with cursor ${a.next}.` : ""}`,
  "done.created": (a: { id: string; process: string }) =>
    `Created instance ${a.id} of ${a.process}. Nothing has run yet: start it with run.`,
  "done.updated": (a: { id: string }) =>
    `Replaced the criteria and notes of instance ${a.id} as given; its inputs and outputs are unchanged.`,
  "done.started": (a: { run: string; agent: string }) =>
    `Started run ${a.run} (${a.agent}). That is all this success means: starting achieves no Outcome. Wait with get_run (wait), then judge the outputs with evaluate.`,
  "done.self": (a: { run: string }) =>
    `Run ${a.run} is yours to perform: follow the prompt, then end it with finish_run. If this MCP connection closes first, the run is recorded as interrupted.`,
  "done.run": (a: { run: string; status: string; truncated: boolean }) =>
    `Run ${a.run} ${statusOf(a.status, STATUS_EN)}.${a.status === "running" ? " Call get_run again to wait further." : ""}${a.status === "succeeded" ? " That the agent ended normally does not mean that any Outcome is achieved." : ""}${a.truncated ? " Earlier events were left out (truncated)." : ""}`,
  "done.canceled": (a: { run: string; canceled: boolean; status: string }) =>
    a.canceled
      ? a.status === "running"
        ? `Run ${a.run} is being stopped; its agent has not ended yet. Check with get_run.`
        : `Canceled run ${a.run}.`
      : `Run ${a.run} had already ended (${a.status}); nothing was changed.`,
  "done.finished": (a: { run: string; status: string; outputs: number }) =>
    `Run ${a.run} ended (${a.status}); ${plural(a.outputs, "output change")} recorded as its outputs.`,
  "done.wakeReported": (a: { run: string; status: string }) =>
    `Recorded your report for wake run ${a.run} (${a.status}). The run ends when your process exits: end now.`,
  "done.evaluated": (a: { instance: string; run: string; self: boolean }) =>
    `Recorded the evaluation of run ${a.run} for instance ${a.instance}.${a.self ? " This MCP session also performed that run, so the evaluation is marked self: true." : ""}`,
  "done.assessment": (a: {
    findings: number;
    instances: number;
    achieved: number;
    judged: number;
    stale: number;
    latest: string;
    items: number;
  }) =>
    `The checks found ${plural(a.findings, "thing")} about the records, the model, and the configuration, with ${plural(a.instances, "instance")}. ${a.achieved} of ${plural(a.judged, "judged Outcome")} achieved; ${plural(a.stale, "evaluation")} on stale evidence. ${a.latest ? `The latest assessment, an agent's interpretation, is that of run ${a.latest} (${plural(a.items, "item")}).` : "No assessment has been made (latest: null)."}`,
  "done.runs": (a: { count: number; next: string }) =>
    `${plural(a.count, "run")}.${a.next ? ` More with cursor ${a.next}.` : ""}`,
  "done.assess": (a: { run: string; agent: string }) =>
    `Started assessment run ${a.run} (${a.agent}): its agent reads the records and records what it finds with record_assessment. Starting finds nothing by itself; the result is get_assessment's latest once the run has ended (get_run with wait).`,
  "done.assessSelf": (a: { run: string }) =>
    `Assessment run ${a.run} is yours to perform: follow the prompt, record what you find with record_assessment, and end the run with finish_run. If this MCP connection closes first, the run is recorded as interrupted.`,
  "done.recorded": (a: { run: string; items: number }) =>
    `Recorded the assessment of run ${a.run} with ${plural(a.items, "item")}; calling again replaces it while the run runs. It becomes get_assessment's latest once the run has ended: end it with finish_run.`,
  "done.reported": (a: { run: string; status: string }) =>
    `Recorded your report for run ${a.run} (${a.status}). The run ends when your process exits: end now.`,
  "done.woke": (a: { run: string; agent: string; plan: boolean }) =>
    `Started wake run ${a.run} (${a.agent}): the agent reads the model, the guidance, and the state, and decides what to run${a.plan ? ", but only instantiates what it plans (plan) and starts no run" : ""}. Starting achieves nothing by itself; the runs it starts are listed in the wake run's started, and what it planned and why comes in the wake run's report (get_run).`,
  "done.wakeSkipped": (a: { running: string }) =>
    `No wake was started: wake run ${a.running} still runs. The skip is recorded in its events.`,
  "done.ui": (a: { url: string; open: boolean; opened: boolean }) =>
    `The WebUI is at ${a.url}.${a.opened ? " It was opened in the browser." : a.open ? " No browser could be started; open the URL yourself." : ""} ${TOKEN_NOTE_EN}`,

  /* ---------- the run log that the MCP server gives (alps://run/<id>/log) ---------- */
  "log.head": (a: { run: string; agent: string; status: string }) =>
    `# Log of run ${a.run} (${a.agent}, ${a.status})`,
  "log.cut": (a: { count: number }) => `(${a.count} earlier events left out)`,

  /* ---------- what the harness itself writes in a run's events ---------- */
  "event.self": () => "The calling session performs the run (self). It ends with finish_run.",
  "event.started": (a: { agent: string; version: string }) =>
    `Started ${a.agent}${a.version ? ` (${a.version})` : ""}`,
  "event.notStarted": (a: { agent: string; detail: string }) =>
    `${a.agent} could not be started: ${a.detail}`,
  "event.end": (a: { status: string; seconds: number }) =>
    `${END_EN[a.status as EndStatus] ?? a.status} (${a.seconds} s)`,
  "event.woken": (a: WokenBy) => `Woken ${wokenEn(a)}.`,
  "event.wakeSkipped": (a: WokenBy) => `Skipped a wake ${wokenEn(a)}: this wake still runs.`,
  "event.wakeReported": (a: { status: string }) =>
    `The agent reported with finish_run (${a.status}); the run ends when its process exits.`,
  "event.attached": (a: { run: string; agent: string; instance: string }) =>
    `Started run ${a.run} (${a.agent}) of instance ${a.instance}.`,
  "event.instantiated": (a: { instance: string; process: string }) =>
    `Created instance ${a.instance} of ${a.process}.`,
  "event.mcpConfig": (a: { agent: string; detail: string }) =>
    `The MCP configuration for ${a.agent} could not be written: ${a.detail}`,
  "event.assessmentRecorded": (a: { items: number }) =>
    `Recorded the assessment (${plural(a.items, "item")}).`,

  /* ---------- why the harness considers a run failed or stopped (its error) ---------- */
  "runError.interrupted": () => "The harness server stopped while the run was running.",
  "runError.sessionClosed": () =>
    "The MCP connection of the session that performs the run closed before finish_run.",
  "runError.exited": (a: { agent: string; code: number }) =>
    `${a.agent} exited with code ${a.code}.`,
  "runError.signal": (a: { agent: string; signal: string }) =>
    `${a.agent} was stopped by ${a.signal || "a signal"}.`,
  "runError.lost": (a: { agent: string; detail: string }) =>
    `The harness lost ${a.agent}: ${a.detail}`,
  "runError.demoOutside": (a: { path: string }) =>
    `The demo does not write ${a.path}: it is outside the workspace.`,
  "runError.demoWrite": (a: { path: string; detail: string }) =>
    `The demo could not write ${a.path}: ${a.detail}`,
  "runError.demoStopped": (a: { detail: string }) => `The demo stopped: ${a.detail}`,

  /* ---------- what the demo agent says in its events, and writes ---------- */
  "demo.start": () => "Running as a demo (no agent is started)",
  "demo.aim": (a: { process: string }) =>
    `Preparing the outputs toward the Outcomes of "${a.process}".`,
  "demo.report": () =>
    "This was a demo: no agent ran, and whether each Outcome is achieved was not checked. Judge from the content of the outputs.",
  "demo.note": (a: { run: string; process: string }) =>
    `Written by demo run ${a.run} (${a.process}). An agent's run writes the actual content.`,
} satisfies Record<string, (args: never) => string>;

export type MessageKey = keyof typeof en;
/** The arguments of a message; `{}` for one that has none. */
export type MessageArgs<K extends MessageKey> =
  Parameters<(typeof en)[K]> extends [infer A] ? A : Record<string, never>;

const ja: { [K in MessageKey]: (typeof en)[K] } = {
  "error.launchProcess": (a) => `プロセス${a.process}はこのモデルにありません。`,
  "error.externalSession": () => "この依頼を開始するには、ALPSのMCP接続が必要です。",
  "error.externalConnected": () =>
    "この接続または会話で作業が進行中です。終了してから次の依頼を開始してください。",
  "error.externalIdentity": () => "この実行に記録された同じ会話から再接続してください。",
  "error.launchMissing": () => "保存した依頼が見つかりません。",
  "error.launchChanged": () => "この依頼は別の条件で保存済みです。新しい依頼として送ってください。",
  "error.launchModel": () => "モデルとエフォートは、アプリまたはターミナルで設定してください。",
  "error.launchProvider": () => "このエージェントは、この開始方法に対応していません。",
  "error.desktopUnavailable": () =>
    "この開始方法を使うには、デスクトップアプリのインストールが必要です。",
  "error.terminalUnavailable": () => "ターミナルを開く機能は現在macOSに対応しています。",
  "error.launchClaim": () => "この依頼は開始待ちではありません。記録を確認してください。",
  "error.launchClient": (a) => `この依頼は${a.agent}から開始してください。`,
  "error.launchWakeRunning": (a) =>
    `オーケストレーション${a.run}が進行中です。この依頼は開始されませんでした。`,
  "error.launchFailed": () => "この依頼を開始できませんでした。",
  "error.launchUser": () => "この依頼の開始・表示はALPSの画面から行ってください。",
  "error.launchWorkspace": (a) =>
    `作業ディレクトリを確認し、${a.workspace} から接続してください。この依頼はまだこのプロジェクトを確認できていません。`,
  "error.resumeRunning": () => "この会話を再開するには、現在の実行が終わるまで待ってください。",
  "error.resumeMissing": () => "この実行には、再開できる会話IDが記録されていません。",
  "error.nativeOpen": () => "アプリを開けませんでした。保存した依頼は保持されています。",
  "error.uiUnavailable": () =>
    "このハーネスサーバーのWebUIを準備できませんでした。サーバーログを確認して、もう一度試してください。",
  "done.launch": (a) =>
    `この会話で実行${a.run}を開始しました。返された指示に従い、finish_runで報告してください。`,

  "error.model": (a) => `プロセスモデルか設定を読めない。${a.detail}`,
  "error.modelChanged": () =>
    "このフォームを開いている間にプロセスモデルが変わりました。最新のモデルを確認してから保存してください。",
  "error.noDesign": (a) => `設計セッション ${a.id} はありません。`,
  "error.designRunning": (a) =>
    `設計セッション ${a.id} はまだ進行中です。続ける前に完了を待つか中止してください。`,
  "error.designNotReady": (a) => `設計セッション ${a.id} には、適用できる提案がまだありません。`,
  "error.designEnded": (a) =>
    `設計セッション ${a.id} はすでに終了しています（${a.status}）。新しい設計セッションを開始してください。`,
  "error.designAgent": (a) =>
    `プロセス設計には Claude Code または Codex が必要です。利用できる設計エージェント: ${a.agents || "なし"}。`,
  "error.designClient": (a) =>
    `この設計セッションは ${a.agent} 用です。そのデスクトップアプリから接続してください。`,
  "error.designMethod": () =>
    "この設計セッションは別の会話経路を使っています。意図した方法で新しい設計セッションを開始してください。",
  "error.designOnly": () =>
    "この接続はモデル構築用です。設計用ツールからモデルとSkillファイルを提出してください。この会話から業務は実行できません。",
  "error.designWorkspace": (a) =>
    `作業フォルダーを確認し、${a.workspace} から接続し直してください。このプロジェクトへの接続はまだ確認できていません。`,
  "error.designReference": (a) => `参照 ${a.path} は設計に使えません: ${a.reason}。`,
  "error.designSources": () =>
    "design-process-description、design-agent-work-system、skill-creator の参照元のいずれかが利用できません。",
  "error.stopping": () =>
    "ハーネスサーバーが停止しているところである。再起動してから呼び直すこと。",
  "error.noProcess": (a) =>
    `モデルにプロセス「${a.name}」はない。プロセスは次のとおり: ${a.processes}。`,
  "error.noType": (a) =>
    `モデルにアーティファクトの型「${a.name}」はない。型は次のとおり: ${a.types}。`,
  "error.noInstance": (a) => `インスタンス ${a.id} はない。`,
  "error.noRun": (a) => `実行 ${a.id} はない。`,
  "error.runRecord": (a) => `実行 ${a.id} の記録（runs/${a.id}.json）がないか、読めない。`,
  "error.emptyPath": (a) =>
    `${a.where}: 「${a.path}」はワークスペースのファイルもディレクトリも指していない。`,
  "error.outside": (a) =>
    `${a.where}: ${a.path} はワークスペース（${a.root}）の外にある。インスタンスと依頼が指せるのはその中のパスだけである。`,
  "error.records": (a) =>
    `${a.where}: ${a.path} はハーネス自身の記録（.alps-harness/）の中にある。インスタンスと依頼が指せるのはワークスペース自身のファイルだけである。`,
  "error.pattern": (a) =>
    `${a.where}: ${a.path} はパターンである。インスタンスの入力は具体的なパスにし、ファイルかディレクトリを一つずつ挙げること（候補は list_artifacts で得られる）。`,
  "error.notInput": (a) =>
    `inputs: ${a.type} は ${a.process} の入力でも統制事項でもない。入力と統制事項は次のとおり: ${a.allowed || "なし"}。`,
  "error.notOutput": (a) =>
    `outputs: ${a.type} は ${a.process} の出力ではない。出力は次のとおり: ${a.outputs || "なし"}。`,
  "error.noOutcome": (a) =>
    `${a.where}${a.process} の成果は ${a.count} 件（番号は 0 から）で、成果 ${a.outcome} はない。`,
  "error.judgedTwice": (a) => `成果 ${a.outcome} を二度判断している。`,
  "error.agentModels": (a) => `${a.agent} のモデル一覧を取得できません: ${a.detail}`,
  "error.agentSelection": (a) => `${a.agent} でこの設定を使用できません: ${a.detail}`,
  "error.noAgent": (a) =>
    `このワークスペースにエージェント「${a.agent}」はない。エージェントは次のとおり: ${a.agents}。`,
  "error.selfDisabled": (a) =>
    `このワークスペースでは self モードを使えない（alps-harness.yaml の agents.self が false）。エージェントは次のとおり: ${a.agents}。`,
  "error.agentUnavailable": (a) => `${a.agent} を起動できない（${a.reason}）。`,
  "error.wakeAgent": (a) =>
    `${a.agent} は目覚めに使えない。目覚めにはハーネスの MCP サーバーが要り、ハーネスがそれを渡せるのは Claude Code（--mcp-config）と Codex（-c mcp_servers）だけである。ここで目覚めに使えるエージェント: ${a.agents || "なし"}。`,
  "error.planOnly": (a) =>
    `目覚めの実行 ${a.run} は計画だけである（runs: plan）。依頼者が先に計画を確かめるので、そのエージェントは計画したものをインスタンス化するだけで、実行も目覚めも起動しない。計画は finish_run で報告すること。`,
  "error.running": (a) =>
    `インスタンス ${a.instance} の実行 ${a.run} がまだ終わっていない。get_run（wait）で待つか、cancel_run で中止すること。`,
  "error.notSelf": (a) =>
    `実行 ${a.run} は ${a.agent} の実行である。finish_run で終えられるのは、呼び出し元のセッションが行う self と目覚めの実行だけである。`,
  "error.ended": (a) =>
    `実行 ${a.run} はすでに終わっている（${a.status}）。get_run で確かめること。`,
  "error.nothingToJudge": (a) =>
    `インスタンス ${a.instance} には評価する実行がない。先に実行すること。`,
  "error.judgeRunning": (a) =>
    `インスタンス ${a.instance} の実行 ${a.run} がまだ終わっていない。終わってから（get_run の wait で待つ）評価すること。`,
  "error.notJson": (a) => `本文が JSON ではない: ${a.detail}`,
  "error.request": (a) => `要求の形が合わない: ${a.detail}`,
  "error.judgment": (a) => `判断の形が合わない: ${a.detail}`,
  "error.client": (a) =>
    `X-Harness-Client ヘッダーが {name, version} の JSON ではない: ${a.detail}`,
  "error.noSkill": (a) => `${a.process} には読める SKILL.md がない。`,
  "error.noAttachment": (a) =>
    `${a.where}: ${a.path} はワークスペースにない。依頼に添付できるのは、そこにあるファイルとディレクトリである。`,
  "error.attachmentCount": (a) =>
    `${a.count} 件のファイルが送られた。一回の依頼で添付できるのは ${a.limit} 件までである。`,
  "error.attachmentSize": (a) =>
    `${a.name} は一件の添付の上限（${a.limit}）より大きい。大きなファイルはワークスペースに置き、そのパスを添付すること。`,
  "error.noFiles": () => "本文に添付するファイルがない。",
  "error.multipart": (a) =>
    `本文がファイルを含むフォーム（multipart/form-data）ではない: ${a.detail}`,
  "error.attachmentNames": (a) =>
    `${a.folder} には ${a.name} と、その名前に -2 から -${a.limit} までを付けたものがすべてある。ファイルの名前を変えるか、ほかのファイルをそのディレクトリから移すこと。`,
  "error.attachmentsDir": (a) =>
    `${a.folder} に添付を保存できない。そのパスの途中にディレクトリでないもの（ファイルか、行き先のない symlink）がある（${a.detail}）。それを移すか、alps-harness.yaml の attachments で別のディレクトリを指すこと。`,
  "error.assessOnly": (a) =>
    `実行 ${a.run} はアセスメント（assess）である。そのエージェントは記録を読み、見つけたことを record_assessment で記録する。インスタンスは作らず、実行も目覚めも起動せず、評価も中止もしない。報告は finish_run で行うこと。`,
  "error.assessAgent": (a) =>
    `${a.agent} はアセスメントに使えない。アセスメントにはハーネスの MCP サーバーか、自分で行うセッション（self）が要り、ハーネスが MCP サーバーを渡せるのは Claude Code（--mcp-config）と Codex（-c mcp_servers）だけである。ここでアセスメントに使えるエージェント: ${a.agents || "なし"}。`,
  "error.assessing": (a) =>
    `アセスメントの実行 ${a.run} がまだ終わっていない。アセスメントは一度に一つだけである。get_run（wait）で待つか、cancel_run で中止すること。`,
  "error.noAssessRun": () =>
    "record_assessment は、動いているアセスメントの実行の結果を、それを行うエージェントが記録するものである（assess が起動したエージェントか、エージェント self で始めたセッション）。呼び出し元はどれも行っていない。",
  "error.selfAssess": () =>
    "エージェント self では、求めた MCP のセッションがアセスメントを行う。この要求は MCP クライアントからではない。別のエージェントを選ぶか、ハーネスの MCP サーバーの assess を使うこと。",
  "error.noEvidence": (a) =>
    `項目 ${a.n} に根拠がない。未確認の項目のほかは、記録（実行、インスタンス、評価、統計の切り口、ログのイベント、パス）を根拠にすること。`,
  "error.evidenceRun": (a) => `項目 ${a.n} が挙げる実行 ${a.run} は記録にない。`,
  "error.evidenceInstance": (a) => `項目 ${a.n} が挙げるインスタンス ${a.instance} は記録にない。`,
  "error.evidenceEvaluation": (a) =>
    `項目 ${a.n} はインスタンス ${a.instance} の評価を挙げるが、その評価はない。`,
  "error.evidenceObservation": (a) => `項目 ${a.n} が挙げる観測 ${a.observation} は記録にない。`,
  "error.evidenceLog": (a) =>
    `項目 ${a.n} は実行 ${a.run} のイベント ${a.event} を挙げるが、そのログのイベントは ${a.events} 件（番号は 1 から）である。`,
  "error.evidencePath": (a) => `項目 ${a.n} が挙げる ${a.path} はワークスペースにない。`,
  "error.evidenceProcess": (a) =>
    `項目 ${a.n} はプロセス ${a.name} の統計を挙げるが、そのプロセスはモデルにない。`,
  "error.itemSubject": (a) =>
    `項目 ${a.n} の対象の${a.kind === "process" ? "プロセス" : a.kind === "artifact" ? "アーティファクトの型" : "インスタンス"} ${a.name} は、このワークスペースにない。`,
  "error.noAssessment": (a) => `アセスメント ${a.id} はない。`,
  "error.noItem": (a) =>
    `アセスメント ${a.id} の項目は ${a.count} 件（番号は 1 から）で、項目 ${a.n} はない。`,
  "error.assessmentOpen": (a) =>
    `アセスメント ${a.id} はまだ作られている途中で、その実行が終わっていない。実行が終わってから確認すること。`,
  "error.reviewByPerson": () =>
    "アセスメントの項目を確認するのは人だけである（WebUI）。エージェントは自分の見つけたことを採用しない。",

  "error.host": () => "このホスト名は受け付けない。",
  "error.crossSite": () => "API はハーネス自身のページからの要求だけを受け付ける。",
  "error.token": () =>
    "合い言葉がないか、違う。alps-harness serve が印字した URL（…/#token=…）を開くこと。",
  "error.mediaType": () => "要求の本文は JSON で送ること。",
  "error.multipartType": () => "添付は multipart/form-data で送ること。",
  "error.bodySize": (a) => `要求の本文が ${a.limit} より大きい。`,
  "error.route": (a) => `${a.method} ${a.path} はない。`,
  "error.internal": () => "サーバーが要求を処理できなかった。",

  "error.noWorkspace": (a) =>
    `${a.start} とその親ディレクトリに alps-harness.yaml も process-model.yaml もない。ALPS_WORKSPACE にプロジェクトのディレクトリを渡すか、そのディレクトリで起動すること。ワークスペースは、どちらかがあるディレクトリになる。`,
  "error.unreachable": (a) =>
    `ハーネスサーバーに接続も起動もできなかった（ポート ${a.port}、${a.serverJson}）: ${a.detail}`,

  "finding.skillMissing": (a) =>
    `${a.process} に指定されたスキル（${a.location}）は、読める SKILL.md ではない。`,
  "finding.awaiting": (a) =>
    `実行 ${a.run} は終わった（${a.status}）が、その結果はまだ判断されていない。`,
  "finding.stale": (a) =>
    `実行 ${a.run} についての判断は、今のワークスペースに基づかなくなった。実行が使った後に変わったもの: ${a.paths}。`,
  "finding.noSkill": (a) =>
    `${a.process} の SKILL.md が見つからない。実行にはモデルにあるプロセスの記述だけが渡る。`,
  "finding.skillChanged": (a) =>
    `${a.process} の実行 ${a.run} が使った後に ${a.path} が変わった。今のスキルを使った実行はまだない。`,
  "finding.noLocation": (a) =>
    `アーティファクトの型 ${a.type} に置き場所がない（alps-harness.yaml の artifacts）。実体を一覧できず、実行にも置き場所を渡せない。`,
  "finding.notProduced": (a) =>
    `${a.type} を作るプロセスはなく、モデルの外から与えられる（読むプロセス: ${a.consumers}）。`,
  "finding.notRead": (a) => `${a.type} を読むプロセスはない（作るプロセス: ${a.producers}）。`,
  "finding.unused": (a) => `${a.type} を作るプロセスも読むプロセスもない。`,
  "finding.agentUnavailable": (a) => `${a.agent} を起動できない（${a.reason}）。`,
  "finding.sharedOrigin": (a) =>
    `${a.path} をどの実行が作ったかは分からない。同時に動いた実行 ${a.runs} のそれぞれが、その変化を出力として持つ。`,

  "done.model": (a) =>
    `モデル「${a.name}」には ${a.processes} のプロセスと ${a.types} のアーティファクトの型がある。SKILL.md とアーティファクトは自分のファイルツールで読むこと。`,
  "done.artifacts": (a) =>
    `アーティファクトは ${a.count} 件。${a.truncated ? "一回の走査で読める数を超えた置き場所があるため（truncated）、一覧は不完全である。" : ""}`,
  "done.instances": (a) =>
    `インスタンスは ${a.count} 件。${a.next ? `続きは cursor ${a.next} で得られる。` : ""}`,
  "done.created": (a) =>
    `${a.process} のインスタンス ${a.id} を作った。まだ何も実行していないので、run で実行すること。`,
  "done.updated": (a) =>
    `インスタンス ${a.id} の基準と注記を指定どおりに置き換えた。入力と出力は変わらない。`,
  "done.started": (a) =>
    `実行 ${a.run}（${a.agent}）を開始した。この成功の意味はそれだけで、開始によって成果が達成されたわけではない。get_run（wait）で待ち、出力を見て evaluate で判断すること。`,
  "done.self": (a) =>
    `実行 ${a.run} はあなた自身が行う。プロンプトに従って作業し、finish_run で終えること。先にこの MCP の接続が切れると、実行は中断として記録される。`,
  "done.run": (a) =>
    `実行 ${a.run} は${statusOf(a.status, STATUS_JA)}。${a.status === "running" ? "さらに待つには get_run を呼び直すこと。" : ""}${a.status === "succeeded" ? "エージェントが正常に終わったことは、成果の達成を意味しない。" : ""}${a.truncated ? "それより前のイベントは省いた（truncated）。" : ""}`,
  "done.canceled": (a) =>
    a.canceled
      ? a.status === "running"
        ? `実行 ${a.run} を止めているところで、エージェントはまだ終わっていない。get_run で確かめること。`
        : `実行 ${a.run} を中止した。`
      : `実行 ${a.run} はすでに終わっていた（${a.status}）。何も変えていない。`,
  "done.finished": (a) =>
    `実行 ${a.run} を終えた（${a.status}）。出力の変化 ${a.outputs} 件をこの実行の出力として記録した。`,
  "done.wakeReported": (a) =>
    `目覚めの実行 ${a.run} の報告を記録した（${a.status}）。実行はあなたのプロセスが終わった時点で終わるので、このまま終了すること。`,
  "done.evaluated": (a) =>
    `インスタンス ${a.instance} について、実行 ${a.run} の評価を記録した。${a.self ? "その実行もこの MCP セッションが行ったので、評価には self: true が付く。" : ""}`,
  "done.assessment": (a) =>
    `記録・モデル・設定の検査で見つかったことは ${a.findings} 件、インスタンスは ${a.instances} 件。判断された成果 ${a.judged} 件のうち達成は ${a.achieved} 件、根拠が古い評価は ${a.stale} 件。${a.latest ? `最新のアセスメント（エージェントの解釈）は実行 ${a.latest} のもの（項目 ${a.items} 件）。` : "アセスメントはまだ行われていない（latest は null）。"}`,
  "done.runs": (a) =>
    `実行は ${a.count} 件。${a.next ? `続きは cursor ${a.next} で得られる。` : ""}`,
  "done.assess": (a) =>
    `アセスメントの実行 ${a.run}（${a.agent}）を開始した。エージェントが記録を読み、見つけたことを record_assessment で記録する。開始しただけでは何も見つかっていない。結果は、実行が終わった後（get_run の wait で待つ）の get_assessment の latest に来る。`,
  "done.assessSelf": (a) =>
    `アセスメントの実行 ${a.run} はあなた自身が行う。プロンプトに従い、見つけたことを record_assessment で記録し、finish_run で実行を終えること。先にこの MCP の接続が切れると、実行は中断として記録される。`,
  "done.recorded": (a) =>
    `実行 ${a.run} のアセスメントを項目 ${a.items} 件で記録した。実行が動いているあいだは、呼び直すと置き換わる。実行が終わると get_assessment の latest になるので、finish_run で終えること。`,
  "done.reported": (a) =>
    `実行 ${a.run} の報告を記録した（${a.status}）。実行はあなたのプロセスが終わった時点で終わるので、このまま終了すること。`,
  "done.woke": (a) =>
    `目覚めの実行 ${a.run}（${a.agent}）を開始した。エージェントがモデル・案内・現状を読み、何を走らせるかを判断する${a.plan ? "（計画だけ：計画したものをインスタンス化し、実行は起動しない）" : ""}。開始しただけでは何も達成されない。起動された実行は目覚めの実行の started に並び、何をなぜ計画したかは目覚めの実行の report に来る（get_run）。`,
  "done.wakeSkipped": (a) =>
    `目覚めは開始しなかった。目覚めの実行 ${a.running} がまだ動いている。見送りはその実行のイベントに記録した。`,
  "done.ui": (a) =>
    `WebUI は ${a.url} にある。${a.opened ? "ブラウザで開いた。" : a.open ? "ブラウザを起動できなかったので、URL を自分で開くこと。" : ""}${TOKEN_NOTE_JA}`,

  "log.head": (a) => `# 実行 ${a.run} のログ（${a.agent}、${a.status}）`,
  "log.cut": (a) => `（イベント ${a.count} 件を省いた）`,

  "event.self": () => "呼び出し元のセッションが自分で実行する（self）。finish_run で終わる。",
  "event.started": (a) => `${a.agent}${a.version ? `（${a.version}）` : ""}を起動した`,
  "event.notStarted": (a) => `${a.agent} を起動できなかった: ${a.detail}`,
  "event.end": (a) => `${END_JA[a.status as EndStatus] ?? a.status}（${a.seconds} 秒）`,
  "event.woken": (a) => `${wokenJa(a)}目覚め。`,
  "event.wakeSkipped": (a) => `${wokenJa(a)}目覚めを見送った。この目覚めがまだ動いている。`,
  "event.wakeReported": (a) =>
    `エージェントが finish_run で報告した（${a.status}）。実行はそのプロセスが終わった時点で終わる。`,
  "event.attached": (a) => `インスタンス ${a.instance} の実行 ${a.run}（${a.agent}）を起動した。`,
  "event.instantiated": (a) => `${a.process} のインスタンス ${a.instance} を作った。`,
  "event.mcpConfig": (a) => `${a.agent} の MCP 設定を書き込めなかった: ${a.detail}`,
  "event.assessmentRecorded": (a) => `アセスメントを記録した（項目 ${a.items} 件）。`,

  "runError.interrupted": () => "実行中にハーネスサーバーが停止した。",
  "runError.sessionClosed": () => "実行を行うセッションの MCP の接続が、finish_run の前に切れた。",
  "runError.exited": (a) => `${a.agent} は終了コード ${a.code} で終わった。`,
  "runError.signal": (a) =>
    a.signal
      ? `${a.agent} はシグナル ${a.signal} で止められた。`
      : `${a.agent} はシグナルで止められた。`,
  "runError.lost": (a) => `ハーネスが ${a.agent} を見失った: ${a.detail}`,
  "runError.demoOutside": (a) => `デモは ${a.path} に書かない。ワークスペースの外にある。`,
  "runError.demoWrite": (a) => `デモは ${a.path} を書けなかった: ${a.detail}`,
  "runError.demoStopped": (a) => `デモが止まった: ${a.detail}`,

  "demo.start": () => "デモとして実行（エージェントは起動しない）",
  "demo.aim": (a) => `「${a.process}」の成果に向けて、出力を用意する。`,
  "demo.report": () =>
    "デモのため、エージェントは起動しておらず、各成果の達成は確かめていない。出力の中身を見て判断すること。",
  "demo.note": (a) =>
    `デモ実行 ${a.run}（${a.process}）が作成した記録。実際の内容はエージェントの実行で作られる。`,
};

const CATALOG: Record<Language, { [K in MessageKey]: (typeof en)[K] }> = { en, ja };

/** A message in the given language. */
export function say<K extends MessageKey>(
  language: Language,
  key: K,
  args: MessageArgs<K>,
): string {
  const message = CATALOG[language][key] as (args: MessageArgs<K>) => string;
  return message(args);
}

/** A message as the harness records it: the English text, with its key and arguments for other languages. */
export interface Spoken<K extends MessageKey = MessageKey> {
  text: string;
  key: K;
  args: Record<string, MessageArg>;
}

/** The message `key` with `args`, as the harness records it. */
export const spoken = <K extends MessageKey>(key: K, args: MessageArgs<K>): Spoken<K> => ({
  text: say("en", key, args),
  key,
  args: args as Record<string, MessageArg>,
});

export const isMessageKey = (key: unknown): key is MessageKey =>
  typeof key === "string" && Object.hasOwn(en, key);

/**
 * A message that arrived as a key and arguments (from the harness server), in the given language;
 * `fallback` when the key is unknown or its arguments do not fit.
 */
export function sayReceived(
  language: Language,
  key: unknown,
  args: unknown,
  fallback: string,
): string {
  if (!isMessageKey(key) || args === null || typeof args !== "object") return fallback;
  try {
    const text = (CATALOG[language][key] as (args: unknown) => string)(args);
    return text.includes("undefined") ? fallback : text;
  } catch {
    return fallback;
  }
}
