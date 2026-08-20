# ALPS Local Runtime v0 implementation specification

**Status:** Final proposal before implementation
**Scope:** Runtime, Web UI, MCP/Hook/Host adapters, persistence, and conformance tests
**Working UI reference:** [Frosted Minimal UI mock](prototypes/local-runtime-ui/index.html)
**Japanese:** [日本語](ja/local-runtime-v0.md)

## 1. Purpose and authority

ALPS Local Runtime discovers and validates Skills, Plugins, and Process Models in user, project, and Agent Host environments; adopts selected revisions as immutable assets; and records Skill application, Artifacts, Decisions, evidence, assessments, and model usage as shared Runs for Agents and humans.

ALPS continues to define Process, Process Description, Skill lifecycle, and Conformance semantics. This document defines an informative reference runtime and environment binding. It does not add a programming language, database, package layout, vendor, or execution environment to ALPS itself.

When sources conflict, use this order:

1. this implementation specification;
2. versioned JSON Schemas, OpenAPI, and event schemas;
3. conformance tests;
4. the working UI reference;
5. other informative design material.

The UI mock defines information hierarchy and interaction intent. Its sample data and in-memory behaviour are not normative.

## 2. Product principles

- **Local-first:** state, history, Artifacts, and Decisions remain under user control.
- **Auditable:** revisions, Actors, Authority, evidence, and Decisions are traceable.
- **Agent–human shared runtime:** Agents and humans use the same Runs, Artifacts, Decisions, and Events.
- **Host-neutral:** Claude Code, Codex, Cursor, GitHub Copilot CLI, and Visual Studio Code are peers.
- **Explicit adoption:** discovery does not make an external asset managed.
- **Discovery without execution:** discovery never executes Scripts, Hooks, MCP servers, LSP servers, Apps, or installers.
- **Minimal UI:** show only information that changes the current decision or operation.
- **Adapter isolation:** host- and vendor-specific semantics do not enter the Core Domain.

Canonical responsibilities are:

> A Skill is the semantic unit of Process work; a Plugin is a distribution unit for capabilities; a Process Model Descriptor describes Skill composition; a Run records one application; and the Runtime is the system of record for execution, decisions, and audit evidence.

## 3. Systems of record

| Subject | System of record |
| --- | --- |
| Process and Skill meaning | `SKILL.md` and ALPS |
| Process composition | Process Model Descriptor |
| Adopted revisions | Runtime database |
| Runs, Decisions, and Assessments | Runtime database |
| Artifact bytes | Content-addressed blob store |
| Audit history | ALPS Domain Event Journal |
| Plugin installed/enabled state | Agent Host |
| External authentication and authorization | External system |
| Telemetry | Derived signals from Domain Events and Observations |

OpenTelemetry, frontend caches, SSE messages, analytical projections, and Host Hook output must not be the sole system of record for business state or audit history.

## 4. v0 scope

v0 must provide:

1. discovery of Skills, Plugins, and Process Models;
2. static validation and semantic comparison;
3. explicit adoption as immutable revisions;
4. a focused Skill Package viewer;
5. an interface-centred Process Model graph;
6. Agent Run start and self-reporting through MCP;
7. Artifact, Handoff, and Assessment management;
8. Human Oversight through Decision Gates;
9. a Run-oriented board;
10. an append-oriented Domain Event Journal;
11. model, effort, and token-usage observations;
12. flow, quality, oversight, and usage analysis;
13. workspace backup and Run audit-bundle export;
14. adapters for Claude Code, Codex, Cursor, Copilot CLI, and VS Code.

v0 excludes a general workflow designer, execution of document order as a workflow, automatic Plugin installation, a Plugin marketplace, multi-tenant cloud operation, multiple writers to one workspace, full event sourcing, Hook-only enforcement, cross-model effort normalization, inferred unreported usage or cost, cryptographically tamper-proof audit, and drag-only domain transitions.

## 5. Architecture

```text
Claude Code ─┐
Codex ───────┤
Cursor ──────┤
Copilot CLI ─┼── MCP / Hooks / Inventory / OTel
VS Code ─────┘
                    │
                    ▼
┌────────────────────────────────────────────┐
│ ALPS Local Runtime                         │
│                                            │
│ Integration                                │
│ ├─ MCP Adapter                             │
│ ├─ Hook Adapter                            │
│ ├─ Host Inventory Adapter                  │
│ └─ Telemetry Import Adapter                │
│                                            │
│ Core                                       │
│ ├─ ALPS Parser / Validator                 │
│ ├─ Revision Resolver                       │
│ ├─ Process Model Resolver                  │
│ ├─ Digest / Manifest                       │
│ └─ Semantic Diff                           │
│                                            │
│ Application                                │
│ ├─ Catalog and Adoption                    │
│ ├─ Run and Artifact                        │
│ ├─ Decision and Assessment                 │
│ ├─ Handoff                                 │
│ └─ Analysis                                │
│                                            │
│ Persistence                                │
│ ├─ SQLite Repositories                     │
│ ├─ Domain Event Journal                    │
│ ├─ Telemetry Outbox                        │
│ └─ Content-addressed Blob Store            │
└──────────────┬───────────────────┬─────────┘
               │ HTTP / SSE        │ CLI
               ▼                   ▼
            Web UI             Administration
```

MCP, HTTP, CLI, and Hook adapters must invoke the same Application Services. Adapters and the frontend must not access storage directly. Domain state must not depend on MCP or browser sessions. One Runtime process is the only writer for one workspace.

## 6. Reference technology stack

### Backend

```text
Language          Go 1.26.x
HTTP / SSE        net/http
MCP               Official MCP Go SDK
Database API      database/sql
Operational DB    SQLite 3.51.3+
SQLite driver     modernc.org/sqlite
Logging           log/slog
Telemetry         OpenTelemetry Go
Static assets     embed.FS
```

The reference implementation uses explicit SQL migrations, repositories, and transactions; it does not use an ORM. Frontend assets are embedded in the single runtime binary. Storage, MCP, Host, Hook, Telemetry, analysis, blob, and frontend-delivery boundaries remain replaceable interfaces.

### Frontend

```text
Framework          Svelte 5
Application        SvelteKit 2
Language           TypeScript
Build              Vite 8
Styling            Tailwind CSS 4 + CSS Custom Properties
Primitives         Bits UI
Server state       TanStack Query
Tables / lists     TanStack Table / TanStack Virtual
Visualization      D3 submodules + Svelte SVG
Testing            Vitest + Playwright
```

SvelteKit builds a static SPA embedded in the Go binary. Production does not require a Node.js server. Design tokens are the visual source of truth. Inline styles, `<style>` elements, and inline event handlers are prohibited in production code.

## 7. Runtime processes

One `alps` binary exposes:

```text
alps serve    Own the workspace and serve API/UI
alps mcp      Provide the Agent Host MCP adapter
alps hook     Normalize Host Hook stdin/stdout
alps scan     Run discovery manually
alps backup   Create a consistent workspace backup
alps export   Export a Run audit bundle
```

`alps mcp` and `alps hook` must not open the database. They connect to `alps serve` over loopback HTTP. If the Runtime is absent, an adapter may acquire the owner lock and start exactly one Runtime.

## 8. Core domain model

```text
Process
  └─ ProcessRevision

SkillPackage
  └─ SkillPackageRevision

Plugin
  └─ PluginRevision
       └─ PluginComponent

ProcessModel
  └─ ProcessModelRevision
       ├─ ProcessMembership
       ├─ InterfaceType
       ├─ ProcessBinding
       └─ HandoffDefinition

Run
  ├─ RunContext
  ├─ RunReport
  ├─ DomainEvent
  ├─ ArtifactRelation
  ├─ DecisionGate
  │    └─ Decision
  ├─ Assessment
  ├─ Handoff
  └─ ModelInvocation
       └─ UsageObservation
```

Common formats are opaque Runtime-generated IDs, RFC 3339 UTC timestamps, `sha256:<hex>` digests, URI references, monotonically increasing state versions, and versioned JSON event payloads.

Required entities include `AssetSource`, `ObservedAsset`, `ProcessRevision`, `SkillPackageRevision`, `PluginRevision`, `PluginComponent`, `ProcessModelRevision`, `HostContext`, `Run`, `RunContext`, `RunReport`, `DomainEvent`, `ArtifactBlob`, `ArtifactRelation`, `DecisionGate`, `Decision`, `Assessment`, `Handoff`, `ModelCatalogSnapshot`, `ModelInvocation`, `UsageObservation`, `CostObservation`, `HostObservation`, and `TelemetryOutbox`.

### Invariants

1. Revisions and Artifacts are immutable.
2. A change creates a new revision or Artifact.
3. Revisions referenced by historical Runs are retained.
4. Decisions are not overwritten.
5. Agent claims and Assessment findings are distinct.
6. Current State, Domain Event, and Telemetry Outbox update in one transaction.
7. Unreported values are never stored as zero.
8. Human Decisions bind to the target revision and expected Run version.

## 9. Process Model Descriptor

A model-aware package may contain:

```text
.alps/process-model.yaml
```

or:

```text
.alps/process-models/<model-id>.yaml
```

Minimum form:

```yaml
apiVersion: alps.dev/process-model/v1alpha1
kind: SkillModel

metadata:
  id: meeting-operations
  name: Meeting Operations
  version: 0.1.0

spec:
  processes:
    - id: consolidate
      ref: ../skills/consolidate/SKILL.md
    - id: review
      ref: ../skills/review/SKILL.md

  interfaces:
    - id: meeting-record
      name: Meeting Record
      kind: information
    - id: meeting-summary
      name: Meeting Summary
      kind: artifact
      mediaTypes: [text/markdown]

  bindings:
    - id: consolidate.output
      process: consolidate
      role: output
      item: Consolidated summary
      interface: meeting-summary
    - id: review.input
      process: review
      role: input
      item: Meeting summary
      interface: meeting-summary

  handoffs:
    - id: summary-for-review
      from: consolidate.output
      to: review.input

  relationships:
    - type: iteration
      processes: [consolidate, review]

  entryPoints:
    - process: consolidate
```

The descriptor contains references, interface types, bindings, handoffs, structural relationships, entry points, and non-normative labels. It must not duplicate Purpose, Outcomes, Activities, or Tasks; store UI coordinates or Run state; or contain model, Hook, analysis, or Host-specific configuration.

A Process Model Revision is derived from the descriptor, referenced Process Revisions, interface schemas, and Handoff criteria.

## 10. Discovery and adoption

Discovery providers normalize common Agent Skills, Agent Plugins, Claude Code, Codex, Cursor, Copilot, VS Code, Host-reported inventory, and configured directories into `ObservedAsset`.

Discovery may read manifests, `SKILL.md`, descriptors, YAML/JSON/frontmatter, file lists, digests, schemas, and static permission metadata. It must not execute Scripts, Hooks, MCP or LSP servers, installers, App authentication, external APIs, or package executables.

Adoption flow:

```text
Discover
→ Validate
→ Show semantic diff and executable surfaces
→ Explicit adoption
→ Content-addressed snapshot
→ Immutable revision
```

External asset state remains multidimensional:

```text
Source:      detected | changed | missing
Validation:  valid | invalid | unsupported | unverified
Host:        installed | enabled | confirmed | unavailable | unknown
ALPS:        external | adopted | retired
```

There is no canonical `loaded` state.

## 11. Run and self-reporting

Run states are:

```text
created
active
waiting_for_decision
waiting_for_input
waiting_for_external_result
waiting_for_resource
completion_requested
completed
failed
cancelled
```

The board is a projection:

| Board lane | Runtime states |
| --- | --- |
| Now | `created`, `active` |
| Waiting | `waiting_*`, `completion_requested` |
| Done | `completed`, `failed`, `cancelled` |

Agent progress sent through MCP is a `RunReport`. A claim that an Outcome is achieved does not itself establish Outcome achievement, Conformance, or Run completion. Those require an Assessment against evidence. Completion requests are accepted only after Exit Criteria, unresolved Gates, required Assessments, required Artifacts, and Handoff state are evaluated.

Every Run mutation requires `expectedVersion`; a mismatch returns HTTP `409 Conflict` or the corresponding MCP error.

## 12. Human Oversight

A Decision Gate records the target Run and revision, expected Run version, proposed effect, reversibility, applicable Controls and Constraints, criteria, evidence, required Authority, and unknown or unverified conditions.

Canonical Decision values are:

```text
continue
hold
change
re-execute
terminate
```

`hold` is non-final and leaves the Gate open. Other Decisions are normally final. The UI uses concrete actions such as `Publish summary`, `Adopt Skill`, `Enable MCP server`, `Return for changes`, `Run verification again`, or `Retire Plugin`; it does not use a generic `Approve` label.

A stale Decision is rejected when the target Run version or revision has changed.

## 13. MCP, Hooks, and Telemetry

v0 targets the stable MCP protocol revision `2025-11-25`; supported older revisions are handled by adapter negotiation. The `2026-07-28` release candidate may be supported only through an experimental adapter or build option until it becomes final and is supported by a stable SDK release. Domain state uses explicit handles such as `run_id`, `gate_id`, and `artifact_id`, never transport-session state.

Required MCP tools are:

```text
alps_catalog_list
alps_asset_get
alps_run_start
alps_run_get
alps_run_report
alps_run_request_completion
alps_artifact_commit
alps_gate_open
alps_gate_get
alps_assessment_record
alps_handoff_create
alps_model_invocation_report
alps_usage_report
```

The standard Agent surface does not expose a Human Decision-finalization tool.

Hooks commonize only a Canonical Hook Binding, Host Capability Profile, and Canonical Event Envelope. Modes are `observe`, `enrich`, `validate`, `gate`, `transform`, and `notify`. Host Hooks provide early observation and supplementary intervention; irreversible effects and external writes are ultimately enforced at Runtime Application Service or ALPS MCP Tool boundaries.

Host Hook, Tool, and Session events are stored as `HostObservation`, not as Domain Events or Assessment results.

The Domain Event Journal is the audit system of record. The Telemetry Outbox feeds OpenTelemetry traces and metrics asynchronously. Default capture is metadata-only; raw prompts, responses, source code, full Tool arguments, and secret values are excluded.

## 14. Model, effort, and token usage

Model usage is recorded per `ModelInvocation`, not once per Run:

```text
Requested Configuration
Effective Configuration
Resolved Model
Usage Observation
Cost / Credit Observation
```

Raw Host values are retained. Model- or provider-specific effort levels are not normalized into a cross-model number.

A Usage Observation records source, Host, adapter version, scope, status, accounting basis, token line items, and inclusion rules. It distinguishes `reported`, `derived`, `estimated`, and `unavailable`; separates provider totals from ALPS-derived totals; and stores tokens, cost, and credits as separate observations. OpenTelemetry attributes are translated through a versioned mapping.

## 15. Persistence

Runtime startup applies:

```sql
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = FULL;
PRAGMA busy_timeout = 5000;
```

There is one write connection (`MaxOpenConns = 1`) and a small read pool. All writes pass through one Write Coordinator:

```text
Command
  ↓
BEGIN IMMEDIATE
  Validate idempotency
  Validate expected version
  Update current state
  Append Domain Event
  Append Telemetry Outbox
COMMIT
  ↓
Publish browser SSE
```

Domain Events contain global and stream sequences, type, Actor, Authority, correlation and causation IDs, payload version, and payload. Stream sequence is unique within a stream.

Blob registration is temporary write → digest → fsync → atomic rename → metadata transaction. Blob path is:

```text
ALPS_WORKSPACE/blobs/sha256/<digest>
```

Backups use SQLite Online Backup or an equivalent consistent snapshot, never a live-file copy. v0 does not automatically archive to Parquet.

## 16. HTTP API and SSE

All mutations accept `Idempotency-Key`; Run mutations also accept `expectedVersion`.

```text
POST /v1/discovery/scan
GET  /v1/catalog
GET  /v1/assets/{id}
GET  /v1/assets/{id}/tree
GET  /v1/assets/{id}/content?path=<path>
POST /v1/assets/{id}/validate
POST /v1/assets/{id}/adopt

GET  /v1/process-models/{revisionId}/graph?mode=structure|live|flow

POST /v1/runs
GET  /v1/runs/{id}
POST /v1/runs/{id}/reports
POST /v1/runs/{id}/completion-requests
POST /v1/runs/{id}/artifacts
POST /v1/runs/{id}/gates

POST /v1/gates/{id}/decisions
POST /v1/assessments
POST /v1/handoffs

POST /v1/model-invocations
POST /v1/usage-observations
POST /v1/cost-observations

GET  /v1/board
GET  /v1/analysis/flow
GET  /v1/analysis/quality
GET  /v1/analysis/oversight
GET  /v1/analysis/usage
GET  /v1/events/stream
```

Browser SSE is an ALPS application API, not an MCP transport. Each message uses the global event sequence as `id`; reconnect resumes from `Last-Event-ID`. The frontend updates only affected entities or queries.

## 17. UI and interaction specification

### Routes

Production routes are:

```text
/atlas
/runs
/runs/:runId
/runs/:runId/gates/:gateId
/library
/library/:assetId
/analysis
```

The standalone reference mock uses equivalent hash routes.

### Global shell

Primary navigation contains only Atlas, Runs, Library, and Analysis. Settings is secondary. `Ctrl/Cmd + K` opens the command palette; `Escape` closes the foremost Dialog, Sheet, or Viewer.

### Information rules

1. Do not initially show information that does not change the next decision or operation.
2. Do not fill the UI with healthy-status badges.
3. Prefer one primary action per surface.
4. Hide digest, revision, compatibility, and telemetry detail until requested.
5. Show a number only with a meaningful definition, unit, or coverage.
6. Do not create a generic dashboard or summary-card wall.
7. Use glass surfaces only to express hierarchy.
8. Keep text and graph edges opaque and readable.

### Library and focused Skill viewer

Library shows icon, name, kind, scope, only action-changing status, and a chevron. It does not initially show digests, revision IDs, Host lists, detailed validation, usage, or history.

The focused viewer follows:

```text
Header
├─ Skill icon
├─ Skill name
├─ Kind / scope
├─ Overflow menu
└─ Close

Body
├─ Package tree
└─ File view

Footer
└─ One contextual primary action
```

For `SKILL.md`, show discovery `Name`, discovery `Description`, and the rendered Skill Description. Other files use a sanitized media-type preview. The contextual action is `Adopt Skill`, `Start Run`, `Compare Changes`, `Reverify`, or `Review Validation` according to state.

Markdown raw HTML is disabled by default. Scripts, inline events, iframes, and external resources are prohibited.

### Atlas

Atlas visualizes an interface-centred directed bipartite graph:

```text
Inner ring: Interface Type
Outer ring: Process / Skill
Process → Interface: produces
Interface → Process: consumes
```

The centre uses the repository-authoritative `assets/icon.svg`. Modes are Structure, Live, and Flow. Selecting a node weakens unrelated nodes and edges and reveals an inspector; there is no permanent inspector. Layout is deterministic and radial. Coordinates are not stored in the descriptor. D3 provides geometry and zoom; Svelte owns the DOM. SVG is the default renderer, with a future Canvas boundary for large models.

### Runs and Run Sheet

Runs has only three lanes: Now, Waiting, and Done. A card shows Skill or Process, Run title, one current-status sentence, Decision presence, reported progress when meaningful, and last update. Revision, token detail, Plugin lists, Timeline, and all Outcomes appear only after opening the Run Sheet.

The Run Sheet shows Decision action when needed, Outcome and Assessment state, Effective Context, model and usage, and Timeline. `Agent Reported` and `Assessed Achieved` are visually distinct.

### Decision Dialog

The Dialog presents proposed effect, target, external effect, reversibility, verified conditions, unknown conditions, evidence, Authority, and concrete actions. After a successful Decision, Runtime records the Domain Event, updates the board projection, publishes SSE, closes the Dialog, and shows a brief toast.

### Analysis

Analysis shows one lens at a time: Flow, Quality, Oversight, or Usage. Each lens contains three measures, one time series, and at most three actionable findings. Structure analysis is integrated into Atlas rather than duplicated as a dashboard.

### Design system and glass surfaces

```text
Design Tokens
  ↓
UI Primitives
  ↓
Domain Components
  ↓
Routes
```

Required primitives include Button, IconButton, Badge, Card, Input, SegmentedControl, Dialog, Sheet, Command, Toast, Progress, Tree, and ScrollArea.

Glass surfaces are limited to navigation, top bar, Skill viewer, Run cards, Dialogs, Sheets, command palette, and Atlas canvas. Implement opaque fallback for browsers without `backdrop-filter`, support `prefers-reduced-transparency` and `prefers-reduced-motion`, and never use glow or gradient as the sole carrier of meaning.

## 18. Analysis definitions

| Metric | Definition |
| --- | --- |
| WIP | Non-terminal Runs at a point in time |
| Throughput | Completed Runs in a period |
| Cycle time | `completed_at - started_at` |
| Waiting time | Sum of `waiting_*` state intervals |
| Gate wait | Final Decision time minus Gate-open time |
| Outcome rate | Achieved Outcomes / Assessed Outcomes |
| Handoff acceptance | Accepted Handoffs / Decided Handoffs |
| Rework rate | Runs containing `change` or `re-execute` / target Runs |
| Token usage | Sum of compatible Usage Observations only |

Every analytical response includes definition, period, population, revision filters, data source, coverage, aggregation, and mapping revision. Incompatible accounting bases or inclusion rules are not combined silently.

## 19. Security

The Runtime binds to loopback by default, uses a random access token, serves UI and API from one origin, validates `Origin`, applies CSP and CSRF controls, restricts workspace and token-file permissions, allowlists discovery roots, canonicalizes paths, warns or rejects root-escaping symlinks, never executes discovery content, stores no secret values, verifies Decision Authority, sanitizes previews, applies request and upload limits, and does not claim tamper-proof audit.

## 20. Repository and workspace layout

Reference repository layout:

```text
cmd/alps/
internal/{core,catalog,discovery,model,run,decision,artifact,assessment,inference,analysis,storage,events,mcp,hooks,telemetry,httpapi}/
schemas/{process-model,api,events,hooks,telemetry}/
migrations/
integrations/{claude-code,codex,cursor,github-copilot-cli,vscode}/
web/src/lib/components/ui/
web/src/lib/features/{atlas,runs,library,analysis}/
web/src/routes/
tests/
```

Workspace layout:

```text
ALPS_WORKSPACE/
├── db/alps.sqlite3
├── blobs/sha256/
├── snapshots/{skills,plugins,process-models}/
├── exports/runs/
├── backups/
└── runtime/{owner.lock,endpoint.json,access.token}
```

## 21. Implementation sequence

1. Runtime foundation: binary, owner lock, migrations, write coordinator, event journal, blob store, HTTP, CLI, backup.
2. Catalog and model: discovery, descriptor, validation, snapshot adoption, semantic diff, graph projection.
3. Run and oversight: state machine, reports, Artifacts, Gates, Decisions, Assessments, Handoffs, MCP, SSE.
4. UI: shell, Library, focused viewer, Atlas, Runs, Run Sheet, Decision Dialog, Analysis, command palette.
5. Inference and telemetry: model invocation, usage, analytical projection, OTel trace/metric, capability profiles.
6. Host integration: Claude Code, Codex, Cursor, Copilot CLI, VS Code, Hook generation, inventory adapters.

## 22. Testing and acceptance

Required test classes are unit, schema/API contract, SQLite and restart integration, backup/restore, owner-lock, blob commit, SSE reconnect, stale-Decision, idempotency, UI route and keyboard interaction, and versioned Host fixtures.

v0 is accepted when it can be distributed as one binary on Windows, macOS, and Linux; enforce one workspace writer; atomically update state/event/outbox; discover without execution; adopt immutable revisions; retain history after source change; render the bipartite model and three Atlas modes; show the focused Skill viewer; accept Agent RunReports while separating Assessment; store content-addressed Artifacts; record and reject stale Human Decisions; update the board through SSE; record requested/effective/resolved models and usage provenance; produce Flow, Quality, Oversight, and Usage analysis; recover state and event sequence after restart; pass MCP and Host fixture tests; and generate a consistent backup and Run audit bundle.

## 23. Final implementation invariants

1. `SKILL.md` is the source of truth for Process meaning.
2. Process Model Descriptor is the source of truth for Process composition.
3. SQLite is the source of truth for operational state.
4. The blob store is the source of truth for Artifact bytes.
5. Domain Event Journal is the source of truth for audit history.
6. Agent self-reporting never substitutes for Assessment.
7. Human Decisions bind to a Run version and revision.
8. Hosts, MCP, Hooks, OpenTelemetry, and the frontend remain replaceable adapters.
9. The UI shows only what is required for the current decision or operation.
10. The ALPS Domain Model does not depend on one Host, vendor, or telemetry schema.
