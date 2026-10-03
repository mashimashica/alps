#!/usr/bin/env bun
/* A stand-in for `codex` (Codex) in the E2E tests: see agent.ts. */

import { runFake } from "./agent.ts";

await runFake("codex");
