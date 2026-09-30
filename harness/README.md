# ALPS harness development

The harness is the TypeScript program in this directory. Bun runs its source as it is: there is no build step and no bundled output, and the WebUI's TSX is bundled in memory when the server starts. What the harness does and how to use it is in the [Harness section of the repository README](../README.md#harness).

## Setup

The harness needs [Bun](https://bun.sh/) 1.3.11 or later. Its dependencies are installed in two steps:

```console
bun install                        # at the repository root: the runtime dependencies
cd harness
bun install                        # the development tools
bunx playwright install chromium   # the browser that E8 and E10 drive
```

The runtime dependencies (the MCP server SDK, zod, Preact, and marked) are in the root `package.json` and `bun.lock`. They are all that the Plugin's fetch-time install reads: Claude Code runs `bun install --frozen-lockfile --ignore-scripts` at the Plugin root. The development tools (TypeScript, oxlint, oxfmt, Playwright, the MCP client SDK, and Bun's types) are in this directory's `package.json` and `bun.lock`, outside that install. This directory's `bunfig.toml` installs them with Bun's isolated linker, so that only the tools themselves appear in `harness/node_modules` and the harness's imports resolve to the root's install, as they do for users.

Add a dependency that the harness needs at run time to the root `package.json`, and a development tool to `harness/package.json`. Keep `bunfig.toml` out of the repository root: Claude Code skips the fetch-time install when one is beside the Bun lockfile.

## Commands

Run them in `harness/`.

| Purpose           | Command                                                                                                                                             |
| ----------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| Develop the WebUI | `bun --watch src/cli.ts serve ../examples/service-change --dev`                                                                                     |
| Type-check        | `bun run check` (`tsc --noEmit`)                                                                                                                    |
| Lint              | `bun run lint` (oxlint with its default rules)                                                                                                      |
| Format            | `bun run fmt`, or `bunx oxfmt --check` to check only                                                                                                |
| Test              | `bun test`, one file with `bun test test/e2e/e5-dashboard.test.ts`, and without the browser's E10 with `bun test --path-ignore-patterns='**/e10-*'` |

`--dev` uses Bun's development server: the WebUI is bundled on each request and reloads when its source changes. Its page and assets bypass the server's Host check and security headers, so use it only while developing the WebUI.

The [validation workflow](../.github/workflows/validate.yml) runs the type check, lint, format check, and tests on macOS and Linux. E10 runs in a job of its own, which retries a failed test once. On Windows the same tests run without being required to pass.

## Layout

| Path            | Content                                                                                                                                                                       |
| --------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `src/cli.ts`    | The command line: `serve`, `stop`, `mcp`, `wake`, and `assess`.                                                                                                               |
| `src/shared/`   | `types.ts`, the shapes of the records, which only this file defines; `schema.ts`, their zod schemas; `strings.ts`, what the harness says, in English and Japanese; `cron.ts`. |
| `src/model/`    | Reading `process-model.yaml` and `alps-harness.yaml`, finding Skills, and scanning the Artifact locations.                                                                    |
| `src/harness/`  | Instances, runs, provenance, evaluations, staleness, the prompts, the demo agent, and the conversion of old records.                                                          |
| `src/agents/`   | The agents' command lines and the reading of their output.                                                                                                                    |
| `src/assess.ts` | The dashboard's statistics and the findings.                                                                                                                                  |
| `src/mcp.ts`    | The MCP server: the tools, the resources, and what they say about themselves.                                                                                                 |
| `src/server/`   | The HTTP server and its safety checks, the UI's bundle, SSE, the daemon, idle exit, and the schedules.                                                                        |
| `src/ui/`       | The WebUI in Preact: the network, the dashboard, the instances, and `strings.ts` with its English and Japanese texts.                                                         |
| `test/`         | `e2e/`, `unit/`, `helpers/`, `fakes/` (the fake agents), and `fixtures/`.                                                                                                     |

## Tests

The E2E tests drive the harness's four external interfaces as real processes: the command line, HTTP and SSE, MCP over stdio, and the browser. They never call its functions. Each test copies `examples/service-change` to a temporary workspace with a daemon of its own on port 0. The agents are fakes (`test/fakes/`) that read the arguments they are given and print fixed stream-json or JSON Lines from `test/fixtures/agents/`. Those fixtures were recorded from the real agents (Claude Code 2.1.96 and codex-cli 0.158.0), with the machine's paths, ids, and file contents made placeholders.

| Test | What it checks                                                                                                                                                                                                                                                                                                                      |
| ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| E1   | `serve --daemon` writes `server.json`, answers `/api/health`, and exits when idle; `stop`; a second `mcp` process uses the running daemon.                                                                                                                                                                                          |
| E2   | Over MCP and HTTP: `instantiate`, `run` with the demo agent, and `get_run` with `wait`, with the outputs in provenance; the error codes; the five resources; `wake`; `server-unreachable`.                                                                                                                                          |
| E3   | The fake Claude Code and Codex: events, usage, and reports; failures; the prompt on standard input; a Claude Code agent and its version check without the marks of a Claude Code session; `cancel_run` stopping the process group; runs interrupted when the server stops; two runs at the same time that keep their outputs apart. |
| E4   | Self runs: the prompt, the output changes at `finish_run`, self judgments per MCP session, and interruption when the connection closes.                                                                                                                                                                                             |
| E5   | Stale evidence by SHA-256 of the inputs and the `SKILL.md`, and the same numbers from `get_assessment`, `/api/stats`, and `assess`.                                                                                                                                                                                                 |
| E6   | Wakes: the agent started with the harness's MCP server and no other, `started[]`, skips, `wake` from the command line, and no idle exit while schedules are configured.                                                                                                                                                             |
| E7   | The conversion of an unversioned `state.json`.                                                                                                                                                                                                                                                                                      |
| E8   | Safety: the Host check, the token, `Sec-Fetch-Site`, framing, JSON bodies, 127.0.0.1 only, paths outside the workspace, and the page that `--open` and `open_ui` open.                                                                                                                                                              |
| E9   | The language of the prompts; what the harness itself writes in a run (its events, the demo's, and the run's error) in English with its key and arguments over MCP and HTTP; the MCP server's sentences and run log in the workspace's language.                                                                                     |
| E10  | The WebUI in Chromium: the bundle made at startup, the token kept in sessionStorage, the ring and the focus view, the marks that follow runs through SSE, and the language switch, which also says the harness's own lines of a run in Japanese.                                                                                    |
| E11  | A fresh clone installs only the runtime dependencies within 60 seconds, and its `mcp` answers `initialize`.                                                                                                                                                                                                                         |

The unit tests (`test/unit/`) cover pure functions only: location patterns, statistics and findings, the network's layout, cron expressions, digests, staleness, provenance (runs at the same time included), the conversion of old records, the environment and the output of agents, and the sanitizing of Markdown. What an E2E test shows is not repeated in a unit test.

In whole-suite runs, the Chromium that Playwright starts from Bun has at times stopped answering during E10, and cleanup hooks have run past Bun's default five seconds under load; the cause of the first is not identified. The tests bound what they wait for: closing a browser takes at most 10 seconds before its process group is killed, HTTP requests time out after 20 seconds and MCP requests after 80, and each file's `beforeAll` and `afterAll` may take up to 60 seconds (`HOOK_TIMEOUT_MS`).

## Conventions

- The shapes of the records are defined only in `src/shared/types.ts`. The API, the MCP server, and the WebUI refer to them.
- Bun's own APIs (`Bun.serve`, `Bun.YAML`, `Bun.spawn`, `Bun.build`, and HTML imports) stay in `src/server/` and `src/cli.ts`.
- The WebUI's layout computations are pure functions that do not touch the DOM, and unit tests check them.
- What the server says, in failures and in the events it writes, is a key and arguments of `src/shared/strings.ts`, which each client says in its own language. English is the source and Japanese its translation, as `localization.yaml` lists.
- A test is named after the behavior it checks, with its scenario number (`E5 …`). Change the test first when the behavior changes.
- Identifiers and comments are in English.
