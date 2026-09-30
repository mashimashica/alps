---
description: Open the ALPS harness's WebUI for this project and show its URL.
argument-hint: "[network|dashboard|instances]"
allowed-tools: mcp__plugin_alps_harness__open_ui
disable-model-invocation: true
---

Call the `open_ui` tool of the ALPS harness's MCP server with `open: true`. The arguments are `$ARGUMENTS`: when they name a screen, `network`, `dashboard`, or `instances`, pass it as `view`; otherwise pass no `view`. Then show the URL that the tool returns.

- The part of the URL after `#` is the access token of this project's harness server. Show the URL only here, to the person who ran this command; do not write it to a file or pass it to another tool.
- When the result has `opened: false`, no browser could be started: say that the URL has to be opened by hand.
- When the tool fails, report its `error.code` and `error.message`. With `no-model`, this project has no `alps-harness.yaml` or `process-model.yaml`; name the files that the error lists. With `server-unreachable`, name the port and `server.json` that the error gives.
