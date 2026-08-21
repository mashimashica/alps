# ALPS Local Runtime v0 (experimental review build)

This branch contains the review build of ALPS Local Runtime v0. It is local-first, uses one Runtime process as the only writer for a Workspace, and exposes the same Process, Run, Artifact, Decision, Assessment, Handoff, and Event context to Agent Hosts and the browser UI.

The build is suitable for local evaluation and feedback. It is not intended for production credentials, irreversible external actions, or unattended operation.

## Requirements

To run the committed application:

- Go 1.26.x
- a current desktop browser

Node.js is not required to run the application because the production Svelte assets are embedded in the Go binary. Node.js 24 and npm are required only when rebuilding or testing the frontend.

## Run locally

```console
git fetch origin
git switch feat/local-runtime-v0-conformance
git pull --ff-only

go mod download
go run ./cmd/alps serve \
  --workspace "$PWD/.alps-workspace-local-review" \
  --root "$PWD" \
  --open
```

Open <http://127.0.0.1:8787> when the browser does not open automatically.

The isolated Workspace contains the SQLite database, content-addressed Artifacts, immutable adoption snapshots, backups, exports, the access token, and Runtime ownership metadata. Remove it after evaluation when the data is no longer needed:

```console
rm -rf .alps-workspace-local-review
```

## Review flow

The primary application surfaces are deliberately limited to four routes:

- `/library` discovers and inspects Skills, Plugins, and Process Models. A Skill opens in a focused package viewer and can be adopted as an immutable Revision.
- `/atlas` renders an interface-centric Process Model graph in Structure, Live, and Flow modes.
- `/runs` shows Run instances in Now, Waiting, and Done. Run details distinguish Agent reports from assessed Outcomes and expose Human Decision Gates.
- `/analysis` presents Flow, Quality, Oversight, and Usage lenses with definitions and coverage.

A normal review sequence is:

```text
Library → inspect and adopt a Skill or Process Model
Atlas   → inspect Process / Interface relationships
Runs    → create or observe a Run, report progress, commit an Artifact
Decision→ resolve an open Human Decision Gate
Analysis→ inspect resulting flow, quality, oversight, and usage evidence
```

Use `Ctrl/Cmd + K` to open the command palette.

## Runtime capabilities

The current review build includes:

- non-executing discovery for repository, configured, user, and Host-reported Skill and Plugin roots;
- static validation, executable-surface reporting, semantic file diff, and explicit adoption;
- immutable Process, Skill Package, Plugin, and Process Model Revisions;
- Descriptor-driven Process / Interface graphs with live Run and Handoff overlays;
- Run Context, optimistic versions, completion requests, required Outcomes, and completion blockers;
- Agent Run reports kept distinct from evidence-based Assessments;
- content-addressed Artifacts, Artifact relations, and Handoffs;
- Human Decision Gates with required authority, evidence, criteria, unknowns, and stale-version rejection;
- requested, effective, and resolved Model records; versioned token, cost, and credit observations;
- append-oriented Domain Events and a Telemetry Outbox written with operational state;
- Browser SSE, OpenTelemetry traces and metrics, and metadata-only Host observations;
- the official MCP Go SDK and the complete Agent-facing ALPS MCP tool surface;
- Host capability profiles and fixtures for Claude Code, Codex, Cursor, GitHub Copilot CLI, and Visual Studio Code;
- consistent SQLite backup, integrity checking, and Run audit export.

Human Decision finalization is intentionally not exposed as an Agent MCP tool.

## Useful commands

The Runtime must be running with the same Workspace for `scan`, `mcp`, `hook`, `backup`, and `export`.

```console
go run ./cmd/alps scan --workspace "$PWD/.alps-workspace-local-review"
go run ./cmd/alps mcp --workspace "$PWD/.alps-workspace-local-review"
go run ./cmd/alps backup --workspace "$PWD/.alps-workspace-local-review"
go run ./cmd/alps export \
  --workspace "$PWD/.alps-workspace-local-review" \
  --run <run-id>
```

The access token and active endpoint are stored under:

```text
<workspace>/runtime/access.token
<workspace>/runtime/endpoint.json
```

## MCP configuration

Build one binary:

```console
mkdir -p .tmp
go build -o "$PWD/.tmp/alps" ./cmd/alps
```

Configure an Agent Host to start the following stdio server:

```text
command: <repository>/.tmp/alps
arguments:
  - mcp
  - --workspace
  - <repository>/.alps-workspace-local-review
```

The Runtime must already be running. The MCP adapter reads the endpoint and token from the Workspace and does not open SQLite directly.

## Rebuild the frontend

```console
cd web
npm ci
npm run check
npm test
npm run build
cd ..

rm -rf internal/web/static
mkdir -p internal/web/static/assets
cp -a web/build/. internal/web/static/
cp assets/icon.svg internal/web/static/assets/icon.svg
```

The CI workflow additionally normalizes generated text files and verifies that the committed embedded assets match a clean SvelteKit build.

## Validate locally

Backend and contract checks:

```console
go mod download
go mod tidy
git diff --exit-code -- go.mod go.sum

go test ./...
go test -race ./...
go vet ./...

bash -n scripts/local-runtime-smoke.sh
bash -n scripts/local-runtime-acceptance.sh
bash scripts/local-runtime-smoke.sh
bash scripts/local-runtime-acceptance.sh
```

Frontend checks:

```console
cd web
npm ci
npm run check
npm test
npm run build
npx playwright install chromium
ALPS_E2E_URL=http://127.0.0.1:8787 npm run test:e2e
```

Run the Runtime in another terminal before the Playwright command.

## Security boundary

The Runtime binds to loopback addresses by default, requires a random local access token for API calls, applies same-origin checks to mutations, limits request and preview sizes, canonicalizes package paths, refuses discovery-time execution, and redacts sensitive Host-observation metadata.

Hooks are observations and early guardrails. They are not the final authorization boundary. Irreversible or external writes must be gated at the Runtime or ALPS MCP tool boundary and confirmed through Human Oversight.
