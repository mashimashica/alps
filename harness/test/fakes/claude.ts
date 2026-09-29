#!/usr/bin/env bun
/* A stand-in for `claude` (Claude Code) in the E2E tests: see agent.ts. */

import { runFake } from "./agent.ts";

await runFake("claude");
