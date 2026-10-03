# Runtime and product boundary

[Japanese translation](locales/ja/runtime-product-boundary.md)

ALPS remains a public, independently usable runtime and plugin. A product consumes a pinned
runtime revision through the published connection contract. Its UI, desktop shell, onboarding,
and optional service integration can be developed separately. The runtime does not import
product code or require access to a private repository.

## Responsibilities

| Public ALPS runtime | Product |
| --- | --- |
| Process definitions, Skills, CLI and native plugin/MCP adapters | Product UI, navigation and design system |
| Instantiation, execution, evaluation, assessment and provenance | Presentation and contextual actions over the public API |
| Workspace ownership and the only writer of harness records | Workspace selection and runtime lifecycle integration |
| Launch scope, claim, completion, continuation and cancellation rules | Choosing execution intent separately from where to start or inspect it |
| Connection contract, schemas, capabilities and optional observability adapters | Compatibility checks, setup, diagnostics and optional local collection |
| Optional reference WebUI | Separately built product UI and desktop packaging |

Products must not copy execution or storage implementation into their own repositories. They
must preserve the runtime's workspace ownership, authorization, idempotency and scope rules.
Sharing observations with the runtime uses its interface rather than a second file writer.

## Execution and inspection

Planning versus execution is a scope decision. CLI versus a desktop application is a start
method. Opening a recorded log in a terminal is an inspection action. These decisions remain
separate: opening a window does not claim a launch or authorize more work, and reopening a
log does not start another agent.

A launch can precede a run. Submission failures and unavailable connections must remain
visible without inventing a run. A successful MCP initialization establishes transport and
tool availability; the host must still claim the saved launch before doing its work. A
disconnected desktop run has an uncertain external execution state until reconnection or an
explicit report resolves it.

On macOS, Claude Code and Codex desktop handoffs require an installed application URL handler,
usable workspace MCP settings and a successful `claim_launch` tool probe. Their links open a
new composer with the workspace and saved request; they do not send it. The user still confirms
workspace trust and submits the request in the host. Codex uses the documented
[`codex://new` parameters](https://learn.chatgpt.com/docs/reference/commands).
Preflight does not prove that a particular native session loaded its configuration. A native
host check must verify the claim and completion independently of link construction, and an
unverified host check must not be reported as passed.

A wake is an orchestration occasion, not an instance. It can create several instances, start
several runs, or record a report with no new instance. Instance records and assessment records
remain attached to their subjects, with links between them. This boundary introduces no new
claim that unrecorded judgments or human approval states already exist.

## Records and observations

ALPS records establish what the harness accepted and recorded. Provider conversation records
can supply the conversation and its retained content. OpenTelemetry supplies observed events,
errors, timings and usage where emitted and collected. Neither a completed run nor a trace
establishes achievement of a Process Outcome.

ALPS launch/run/instance IDs, provider conversation IDs, MCP connection IDs, and trace/span IDs
identify different things. Correlation must preserve those distinctions and the collection
source, interval, known omissions, and content policy. One conversation may contain several
ALPS runs. Missing telemetry and unavailable conversation content are unknown, not zero or
evidence that no work occurred. A hash or application link alone does not retain an old version.

Observation is optional. A collector outage must not prevent starting, claiming, finishing,
or saving work. Prompt text, tool content and unrelated sessions are excluded from the initial
product collection policy. The public runtime's optional telemetry export uses an allowlist of
correlation attributes and a short workspace identifier; absolute workspace paths and arbitrary
collector-supplied attributes are not exported by default. The actual installed host and Bun
integration must be verified; documentation support alone does not establish end-to-end operation
on a machine.

## Distribution and compatibility

The runtime can start without building a UI. Its reference UI and a product UI are explicit
presentation choices over the same runtime. A user-authenticated product may attach its UI
entry to an already running headless runtime on the same workspace when the runtime advertises
the required capability. That attachment changes only the presentation entry recorded in
`server.json`; it must not stop the daemon, duplicate the runtime, import private code into
the public runtime, or change the runtime's write ownership. A product checks the API, event
and storage contract and required capabilities before enabling operations, and pins the exact
runtime revision it distributes. A source checkout, installed plugin, and workspace configuration
have distinct locations; unresolved host-specific variables must not be used as project paths.

Existing public code retains its applicable license. Distributing a runtime or derived assets
requires preserving the applicable licenses, notices and modification attribution. Separating
future product development does not revoke rights already granted for public code.

Artifact delivery and new format-specific preview infrastructure remain a separate design
subject. This split preserves existing artifact access and evaluation requirements; it does
not claim Office/PDF fidelity, snapshot retention or new preview support.
