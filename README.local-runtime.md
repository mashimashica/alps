# ALPS Local Runtime v0 (experimental)

This branch contains a locally runnable vertical slice of the ALPS Runtime. It is intended for evaluation, not irreversible or production use.

## Run locally

Requirements: Go 1.24 or later. The Runtime uses a pure-Go SQLite implementation and does not require a system SQLite installation.

```console
go mod download
go run ./cmd/alps serve --root . --open
```

Open <http://127.0.0.1:8787> when the browser does not open automatically.

The Runtime stores local state under `~/.alps/runtime-v0` by default. To use an isolated workspace:

```console
go run ./cmd/alps serve \
  --workspace /tmp/alps-runtime-v0 \
  --root . \
  --open
```

The current vertical slice provides:

- discovery of repository and user Skills, Plugins, and Process Model descriptors;
- immutable adoption snapshots;
- an Atlas projection of Processes and Interfaces;
- a three-lane Run board;
- Agent progress reports kept separate from assessed Outcomes;
- Human Decision Gates with stale-version protection;
- content-addressed Artifacts;
- model and token usage observations;
- browser updates over SSE;
- a minimal MCP stdio adapter;
- SQLite backup and Run audit export commands.

## Validate locally

The smoke test exercises a Run and Human Decision Gate. The acceptance test additionally checks discovery, adoption, package isolation, Artifacts, usage, Atlas, SSE, MCP, backup, export, restart persistence, authentication, Origin validation, path traversal protection, and stale Decision rejection.

```console
go test ./...
go test -race ./...
go vet ./...
node --check internal/web/static/app.js
bash scripts/local-runtime-smoke.sh
bash scripts/local-runtime-acceptance.sh
```

## Useful commands

```console
go run ./cmd/alps scan
go run ./cmd/alps mcp
go run ./cmd/alps backup
go run ./cmd/alps export --run <run-id>
```

`alps mcp`, `alps scan`, `alps backup`, and `alps export` expect `alps serve` to be running with the same workspace.

## Local MCP configuration

Build the binary first:

```console
go build -o alps ./cmd/alps
```

Then configure an Agent Host to start:

```console
./alps mcp --workspace "$HOME/.alps/runtime-v0"
```

This implementation is experimental. Host Hooks are observations and guardrails, not a complete security boundary.
