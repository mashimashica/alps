# ALPS Local Runtime v0 実装仕様

<p align="right">
  <a href="../local-runtime-v0.md">English</a> | <strong>日本語</strong>
</p>

**状態:** 実装開始前の最終案
**対象:** Runtime、Web UI、MCP／Hook／Host Adapter、永続化、適合試験
**動作参照:** [Frosted Minimal UIモック](../prototypes/local-runtime-ui/index.html)

## 1. 目的と位置づけ

ALPS Local Runtimeは、ユーザー、プロジェクトおよびAgent Hostの環境にあるSkills、PluginsおよびProcess Modelsを発見・検証し、選択したRevisionを不変資産として採用する。また、Skillの適用、Artifacts、Decisions、Evidence、AssessmentsおよびModel Usageを、Agentと人間が共有するRunsとして記録する。

ALPSはProcess、Process Description、Skill LifecycleおよびConformanceの意味論を引き続き定義する。本書はInformativeな参照RuntimeおよびEnvironment Bindingを定義し、ALPS自体に特定の言語、データベース、Package Layout、VendorまたはExecution Environmentを追加しない。

情報が矛盾する場合は次の順で優先する。

1. 本実装仕様。
2. Version付きJSON Schema、OpenAPIおよびEvent Schema。
3. Conformance Test。
4. 動作参照モック。
5. その他のInformativeな設計資料。

UIモックは情報階層およびInteraction Intentを示す。サンプルデータとメモリ上の動作は規範要件ではない。

## 2. プロダクト原則

- **Local-first:** State、History、ArtifactsおよびDecisionsをユーザー管理下に置く。
- **Auditable:** Revisions、Actors、Authority、EvidenceおよびDecisionsを追跡可能にする。
- **Agent–human shared runtime:** Agentと人間が同じRuns、Artifacts、DecisionsおよびEventsを扱う。
- **Host-neutral:** Claude Code、Codex、Cursor、GitHub Copilot CLIおよびVisual Studio Codeを同列に扱う。
- **Explicit adoption:** Discoveryだけでは外部Assetを管理対象にしない。
- **Discovery without execution:** Discovery時にScripts、Hooks、MCP Servers、LSP Servers、AppsまたはInstallersを実行しない。
- **Minimal UI:** 現在の判断または操作を変える情報だけを表示する。
- **Adapter isolation:** HostおよびVendor固有の意味をCore Domainへ持ち込まない。

役割は次のように整理する。

> SkillはProcess Workの意味単位、Pluginは能力の配布単位、Process Model DescriptorはSkillsの構成記述、Runは一回の適用記録、Runtimeは実行・判断・Audit Evidenceの正本である。

## 3. 正本

| 対象 | 正本 |
| --- | --- |
| ProcessおよびSkillの意味 | `SKILL.md`およびALPS |
| Process構成 | Process Model Descriptor |
| 採用済みRevision | Runtime Database |
| Runs、DecisionsおよびAssessments | Runtime Database |
| Artifact Bytes | Content-addressed Blob Store |
| Audit History | ALPS Domain Event Journal |
| PluginのInstalled／Enabled状態 | Agent Host |
| 外部Authentication／Authorization | External System |
| Telemetry | Domain EventsおよびObservationsから生成する派生Signal |

OpenTelemetry、Frontend Cache、SSE Message、Analytical ProjectionおよびHost Hook OutputをBusiness StateまたはAudit Historyの唯一の正本にしてはならない。

## 4. v0の範囲

v0は次を提供する。

1. Skills、PluginsおよびProcess ModelsのDiscovery。
2. Static ValidationおよびSemantic Comparison。
3. Immutable RevisionとしてのExplicit Adoption。
4. Focused Skill Package Viewer。
5. Interface中心のProcess Model Graph。
6. MCP経由のAgent Run開始および自己申告。
7. Artifact、HandoffおよびAssessment管理。
8. Decision GateによるHuman Oversight。
9. Run中心のBoard。
10. Append-oriented Domain Event Journal。
11. Model、EffortおよびToken Usage Observation。
12. Flow、Quality、OversightおよびUsage Analysis。
13. Workspace BackupおよびRun Audit Bundle Export。
14. Claude Code、Codex、Cursor、Copilot CLIおよびVS Code向けAdapter。

v0は汎用Workflow Designer、Document OrderのWorkflow実行、自動Plugin Installation、Plugin Marketplace、Multi-tenant Cloud、同一Workspaceへの複数Writer、Full Event Sourcing、HookだけによるEnforcement、Model間のEffort正規化、未報告Usage／Costの推定、Cryptographic Tamper-proof AuditおよびDragだけによるDomain Transitionを対象外とする。

## 5. アーキテクチャ

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

MCP、HTTP、CLIおよびHook Adapterは同じApplication Servicesを呼ぶ。AdapterおよびFrontendはStorageへ直接アクセスしない。Domain StateはMCPまたはBrowser Sessionへ依存させない。一つのWorkspaceでは一つのRuntime ProcessだけがWriteする。

## 6. 参照技術スタック

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

参照実装は明示的なSQL Migration、RepositoryおよびTransactionを使い、ORMを使わない。Frontend Assetを単一Runtime Binaryに埋め込む。Storage、MCP、Host、Hook、Telemetry、Analysis、BlobおよびFrontend Deliveryは交換可能なInterfaceとして保つ。

v0は安定版MCP Protocol Revision `2025-11-25`を対象とする。`2026-07-28` Release Candidateへの対応はExperimental AdapterまたはBuild Optionとして追加してよいが、同RevisionがFinalとなり安定版SDKで対応されるまで、v0の正しさを依存させてはならない。

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

SvelteKitはGo Binaryへ埋め込むStatic SPAを生成し、ProductionではNode.js Serverを必要としない。Design TokenをVisual Source of Truthとし、Production CodeではInline Style、`<style>`要素およびInline Event Handlerを禁止する。

## 7. Runtime Process

単一の`alps` Binaryは次を提供する。

```text
alps serve    Workspaceを所有しAPI/UIを提供する
alps mcp      Agent Host向けMCP Adapterを提供する
alps hook     Host Hook stdin/stdoutを正規化する
alps scan     Discoveryを手動実行する
alps backup   整合したWorkspace Backupを作成する
alps export   Run Audit BundleをExportする
```

`alps mcp`および`alps hook`はDatabaseを開かず、Loopback HTTPで`alps serve`に接続する。Runtimeがない場合、AdapterはOwner Lockを取得し、一つだけRuntimeを起動してよい。

## 8. Core Domain Model

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

共通形式はRuntime生成のOpaque ID、RFC 3339 UTC Timestamp、`sha256:<hex>` Digest、URI Reference、単調増加State VersionおよびVersion付きJSON Event Payloadとする。

必須Entityは`AssetSource`、`ObservedAsset`、`ProcessRevision`、`SkillPackageRevision`、`PluginRevision`、`PluginComponent`、`ProcessModelRevision`、`HostContext`、`Run`、`RunContext`、`RunReport`、`DomainEvent`、`ArtifactBlob`、`ArtifactRelation`、`DecisionGate`、`Decision`、`Assessment`、`Handoff`、`ModelCatalogSnapshot`、`ModelInvocation`、`UsageObservation`、`CostObservation`、`HostObservation`および`TelemetryOutbox`とする。

### 不変条件

1. RevisionおよびArtifactはImmutableとする。
2. 変更は新RevisionまたはArtifactを作る。
3. Historical Runが参照するRevisionを保持する。
4. Decisionを上書きしない。
5. Agent ClaimとAssessment Findingを分離する。
6. Current State、Domain EventおよびTelemetry Outboxを一つのTransactionで更新する。
7. 未報告値をZeroとして保存しない。
8. Human DecisionをTarget RevisionおよびExpected Run Versionに結び付ける。

## 9. Process Model Descriptor

Model-aware Packageは次を含めてよい。

```text
.alps/process-model.yaml
```

または:

```text
.alps/process-models/<model-id>.yaml
```

最小形式:

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

DescriptorはReferences、Interface Types、Bindings、Handoffs、Structural Relationships、Entry PointsおよびNon-normative Labelsを含む。Purpose、Outcomes、ActivitiesまたはTasksの複製、UI Coordinates、Run State、Model、Hook、AnalysisまたはHost固有Configurationを含めない。

Process Model RevisionはDescriptor、参照Process Revisions、Interface SchemasおよびHandoff Criteriaから生成する。

## 10. DiscoveryとAdoption

Discovery ProviderはCommon Agent Skills、Agent Plugins、Claude Code、Codex、Cursor、Copilot、VS Code、Host-reported InventoryおよびConfigured Directoriesを`ObservedAsset`へ正規化する。

DiscoveryはManifest、`SKILL.md`、Descriptor、YAML／JSON／Frontmatter、File List、Digest、SchemaおよびStatic Permission Metadataを読み取ってよい。Scripts、Hooks、MCP／LSP Servers、Installers、App Authentication、External APIまたはPackage Executablesを実行してはならない。

Adoption Flow:

```text
Discover
→ Validate
→ Semantic DiffおよびExecutable Surfaceを表示
→ Explicit Adoption
→ Content-addressed Snapshot
→ Immutable Revision
```

External Asset State:

```text
Source:      detected | changed | missing
Validation:  valid | invalid | unsupported | unverified
Host:        installed | enabled | confirmed | unavailable | unknown
ALPS:        external | adopted | retired
```

Canonicalな`loaded`状態は定義しない。

## 11. Runと自己申告

Run States:

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

BoardはProjectionである。

| Board Lane | Runtime States |
| --- | --- |
| Now | `created`、`active` |
| Waiting | `waiting_*`、`completion_requested` |
| Done | `completed`、`failed`、`cancelled` |

MCP経由のAgent進捗は`RunReport`とする。Outcome達成のClaimだけではOutcome Achievement、ConformanceまたはRun Completionを確立せず、Evidenceに対するAssessmentを必要とする。Completion RequestはExit Criteria、未解決Gate、必要Assessment、必要ArtifactおよびHandoff Stateを評価した後にのみ受理する。

Run Mutationはすべて`expectedVersion`を要求し、不一致はHTTP `409 Conflict`または対応するMCP Errorとする。

## 12. Human Oversight

Decision GateはTarget Run／Revision、Expected Run Version、Proposed Effect、Reversibility、Applicable Controls／Constraints、Criteria、Evidence、Required AuthorityおよびUnknown／Unverified Conditionsを記録する。

Canonical Decision:

```text
continue
hold
change
re-execute
terminate
```

`hold`はNon-finalでGateをOpenのままにする。他のDecisionは原則Finalとする。UIはGenericな`Approve`ではなく、`Publish summary`、`Adopt Skill`、`Enable MCP server`、`Return for changes`、`Run verification again`または`Retire Plugin`などのConcrete Actionを使う。

Target Run VersionまたはRevisionが変わったStale Decisionは拒否する。

## 13. MCP、HooksおよびTelemetry

v0が対象とする安定版MCP Protocol Revisionは`2025-11-25`とし、旧RevisionはAdapter Negotiationで扱う。Domain StateはTransport Sessionではなく`run_id`、`gate_id`および`artifact_id`などのExplicit Handleを使う。

必須MCP Tools:

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

Standard Agent SurfaceにHuman Decision Finalization Toolを公開しない。

HooksではCanonical Hook Binding、Host Capability ProfileおよびCanonical Event Envelopeだけを共通化する。Modeは`observe`、`enrich`、`validate`、`gate`、`transform`および`notify`とする。Host HookはEarly Observationおよび補助的介入に使い、Irreversible EffectおよびExternal WriteはRuntime Application ServiceまたはALPS MCP Tool Boundaryで最終的に強制する。

Host Hook、ToolおよびSession Eventは`HostObservation`として保存し、Domain EventまたはAssessment Resultにしない。

Domain Event JournalをAuditの正本とする。Telemetry OutboxはOpenTelemetry TraceおよびMetricを非同期に供給する。既定CaptureはMetadata-onlyとし、Raw Prompt、Response、Source Code、Full Tool ArgumentおよびSecret Valueを除外する。

## 14. Model、EffortおよびToken Usage

Model UsageはRun単位ではなく`ModelInvocation`単位で記録する。

```text
Requested Configuration
Effective Configuration
Resolved Model
Usage Observation
Cost / Credit Observation
```

HostのRaw Valueを保持し、ModelまたはProvider固有Effort LevelをModel間の数値へ正規化しない。

Usage ObservationはSource、Host、Adapter Version、Scope、Status、Accounting Basis、Token Line ItemおよびInclusion Ruleを記録する。`reported`、`derived`、`estimated`および`unavailable`を区別し、Provider TotalとALPS-derived Totalを分離し、Token、CostおよびCreditを別Observationとする。OpenTelemetry AttributeはVersion付きMappingで変換する。

## 15. 永続化

Runtime起動時:

```sql
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = FULL;
PRAGMA busy_timeout = 5000;
```

一つのWrite Connection（`MaxOpenConns = 1`）と小規模Read Poolを使う。すべてのWriteは一つのWrite Coordinatorを通す。

```text
Command
  ↓
BEGIN IMMEDIATE
  Idempotencyを検証
  Expected Versionを検証
  Current Stateを更新
  Domain Eventを追加
  Telemetry Outboxを追加
COMMIT
  ↓
Browser SSEを発行
```

Domain EventはGlobal／Stream Sequence、Type、Actor、Authority、Correlation／Causation ID、Payload VersionおよびPayloadを持つ。Stream内でStream Sequenceを一意にする。

Blob RegistrationはTemporary Write → Digest → fsync → Atomic Rename → Metadata Transactionとする。Blob Path:

```text
ALPS_WORKSPACE/blobs/sha256/<digest>
```

BackupはSQLite Online Backupまたは同等のConsistent Snapshotを使い、稼働中Fileを単純Copyしない。v0ではParquetへ自動Archiveしない。

## 16. HTTP APIとSSE

全Mutationは`Idempotency-Key`を受け、Run Mutationは`expectedVersion`も受ける。

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

Browser SSEはALPS Application APIでありMCP Transportではない。各MessageはGlobal Event Sequenceを`id`に使い、`Last-Event-ID`から再開する。Frontendは影響するEntityまたはQueryだけを更新する。

## 17. UIおよびInteraction仕様

### Routes

Production Routes:

```text
/atlas
/runs
/runs/:runId
/runs/:runId/gates/:gateId
/library
/library/:assetId
/analysis
```

Standalone Reference Mockは同等のHash Routeを使う。

### Global Shell

Primary NavigationはAtlas、Runs、LibraryおよびAnalysisだけとする。SettingsはSecondaryとする。`Ctrl/Cmd + K`でCommand Paletteを開き、`Escape`で最前面のDialog、SheetまたはViewerを閉じる。

### 情報規則

1. 次の判断または操作を変えない情報を初期表示しない。
2. Healthy Status BadgeでUIを埋めない。
3. 一つのSurfaceではPrimary Actionを一つにする。
4. Digest、Revision、CompatibilityおよびTelemetry Detailを要求時まで隠す。
5. 数値は意味のあるDefinition、UnitまたはCoverageとともに表示する。
6. Generic DashboardまたはSummary Card Wallを作らない。
7. Glass SurfaceはHierarchy表現に限定する。
8. TextおよびGraph Edgeの可読性を保つ。

### LibraryとFocused Skill Viewer

LibraryはIcon、Name、Kind、Scope、次のActionを変えるStatusおよびChevronを表示する。Digest、Revision ID、Host List、Detailed Validation、UsageおよびHistoryは初期表示しない。

Focused Viewer:

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

`SKILL.md`ではDiscovery `Name`、Discovery `Description`およびRendered Skill Descriptionを表示する。他FileはSanitized Media-type Previewを使う。Contextual Actionは状態に応じて`Adopt Skill`、`Start Run`、`Compare Changes`、`Reverify`または`Review Validation`とする。

Markdown Raw HTMLは既定で無効とし、Scripts、Inline Events、iframesおよびExternal Resourcesを禁止する。

### Atlas

AtlasはInterface中心のDirected Bipartite Graphを表示する。

```text
Inner ring: Interface Type
Outer ring: Process / Skill
Process → Interface: produces
Interface → Process: consumes
```

中央にRepository正本の`assets/icon.svg`を置く。ModeはStructure、LiveおよびFlowとする。Node選択時にUnrelated Node／Edgeを弱め、Inspectorを表示する。Permanent Inspectorは置かない。LayoutはDeterministic Radialとし、CoordinatesをDescriptorへ保存しない。D3はGeometryおよびZoomを提供し、DOMはSvelteが所有する。Default RendererはSVGとし、将来のCanvas Boundaryを持つ。

### RunsとRun Sheet

RunsはNow、WaitingおよびDoneの三Laneだけとする。CardはSkill／Process、Run Title、一文のCurrent Status、Decision Presence、意味がある場合のReported ProgressおよびLast Updateを表示する。Revision、Token Detail、Plugin List、Timelineおよび全OutcomeはRun Sheetでのみ表示する。

Run SheetはDecision Action、Outcome／Assessment State、Effective Context、Model／UsageおよびTimelineを表示する。`Agent Reported`と`Assessed Achieved`を視覚的に区別する。

### Decision Dialog

DialogはProposed Effect、Target、External Effect、Reversibility、Verified Conditions、Unknown Conditions、Evidence、AuthorityおよびConcrete Actionsを表示する。Decision成功後、RuntimeはDomain Eventを追加し、Board Projectionを更新し、SSEを発行し、Dialogを閉じ、短いToastを表示する。

### Analysis

一度にFlow、Quality、OversightまたはUsageの一つのLensだけを表示する。各Lensは三つのMeasure、一つのTime Seriesおよび最大三つのActionable Findingを持つ。Structure AnalysisはAtlasへ統合し、Dashboardとして複製しない。

### Design SystemとGlass Surface

```text
Design Tokens
  ↓
UI Primitives
  ↓
Domain Components
  ↓
Routes
```

Required PrimitiveはButton、IconButton、Badge、Card、Input、SegmentedControl、Dialog、Sheet、Command、Toast、Progress、TreeおよびScrollAreaとする。

Glass SurfaceはNavigation、Topbar、Skill Viewer、Run Cards、Dialogs、Sheets、Command PaletteおよびAtlas Canvasに限定する。`backdrop-filter`非対応時のOpaque Fallback、`prefers-reduced-transparency`および`prefers-reduced-motion`を支援し、GlowまたはGradientだけで意味を表現しない。

## 18. Analysis定義

| Metric | 定義 |
| --- | --- |
| WIP | 指定時点のNon-terminal Runs |
| Throughput | 期間内のCompleted Runs |
| Cycle Time | `completed_at - started_at` |
| Waiting Time | `waiting_*` State Intervalの合計 |
| Gate Wait | Final Decision Time - Gate Open Time |
| Outcome Rate | Achieved Outcomes / Assessed Outcomes |
| Handoff Acceptance | Accepted Handoffs / Decided Handoffs |
| Rework Rate | `change`または`re-execute`を含むRun / Target Runs |
| Token Usage | CompatibleなUsage Observationだけの合計 |

Analysis ResponseはDefinition、Period、Population、Revision Filters、Data Source、Coverage、AggregationおよびMapping Revisionを含む。IncompatibleなAccounting BasisまたはInclusion Ruleを暗黙に合算しない。

## 19. Security

Runtimeは既定でLoopbackにBindし、Random Access Tokenを使い、UIとAPIを同一Originから提供し、`Origin` Validation、CSPおよびCSRF Controlを適用する。Workspace／Token File Permissionを制限し、Discovery RootをAllowlistし、PathをCanonicalizeし、Root外SymlinkをRejectまたはWarningする。Discovery Contentを実行せず、Secret Valueを保存せず、Decision Authorityを検証し、PreviewをSanitizeし、Request／Upload Limitを適用し、Tamper-proof Auditを主張しない。

## 20. RepositoryおよびWorkspace Layout

参照Repository Layout:

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

Workspace Layout:

```text
ALPS_WORKSPACE/
├── db/alps.sqlite3
├── blobs/sha256/
├── snapshots/{skills,plugins,process-models}/
├── exports/runs/
├── backups/
└── runtime/{owner.lock,endpoint.json,access.token}
```

## 21. 実装順序

1. Runtime Foundation: Binary、Owner Lock、Migrations、Write Coordinator、Event Journal、Blob Store、HTTP、CLI、Backup。
2. Catalog and Model: Discovery、Descriptor、Validation、Snapshot Adoption、Semantic Diff、Graph Projection。
3. Run and Oversight: State Machine、Reports、Artifacts、Gates、Decisions、Assessments、Handoffs、MCP、SSE。
4. UI: Shell、Library、Focused Viewer、Atlas、Runs、Run Sheet、Decision Dialog、Analysis、Command Palette。
5. Inference and Telemetry: Model Invocation、Usage、Analytical Projection、OTel Trace／Metric、Capability Profile。
6. Host Integration: Claude Code、Codex、Cursor、Copilot CLI、VS Code、Hook Generation、Inventory Adapter。

## 22. Testingおよび受入

必須Test ClassはUnit、Schema／API Contract、SQLite／Restart Integration、Backup／Restore、Owner Lock、Blob Commit、SSE Reconnect、Stale Decision、Idempotency、UI Route／Keyboard InteractionおよびVersion付きHost Fixtureとする。

v0は、Windows、macOSおよびLinux向けに単一Binaryを配布でき、一つのWorkspace Writerを強制し、State／Event／OutboxをAtomicに更新し、実行せずにDiscoveryし、Immutable Revisionを採用し、Source変更後もHistoryを保持し、Bipartite Modelおよび三つのAtlas Modeを表示し、Focused Skill Viewerを提供し、Assessmentと分離したAgent RunReportを受理し、Content-addressed Artifactを保存し、Stale Human Decisionを拒否し、SSEでBoardを更新し、Requested／Effective／Resolved ModelおよびUsage Provenanceを記録し、Flow／Quality／Oversight／Usage Analysisを生成し、Restart後にState／Event Sequenceを復元し、MCP／Host Fixture Testを通過し、Consistent Backup／Run Audit Bundleを生成できたとき受け入れる。

## 23. 最終実装不変条件

1. `SKILL.md`をProcess Meaningの正本とする。
2. Process Model DescriptorをProcess Compositionの正本とする。
3. SQLiteをOperational Stateの正本とする。
4. Blob StoreをArtifact Bytesの正本とする。
5. Domain Event JournalをAudit Historyの正本とする。
6. Agent自己申告をAssessmentの代替にしない。
7. Human DecisionをRun VersionおよびRevisionに結び付ける。
8. Hosts、MCP、Hooks、OpenTelemetryおよびFrontendを交換可能なAdapterとする。
9. UIは現在の判断または操作に必要な情報だけを表示する。
10. ALPS Domain Modelを特定Host、VendorまたはTelemetry Schemaに依存させない。
