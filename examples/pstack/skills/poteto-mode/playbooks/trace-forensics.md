# Trace forensics

## Purpose

Diagnose the cause from a capture that already exists, and hand back a cited diagnosis, with no fix unless asked.

## Outcomes

- The finding comes from the existing artifact, read and not re-run.
- The cause is mapped to file, symbol, and line via the artifact's own symbols, or the reply says plainly that the artifact does not carry them.
- Where a paired capture exists, whether the finding is confirmed rests on a diff of the before and after artifacts. Otherwise the finding is marked as the strongest hypothesis the artifact supports, not a confirmed cause.
- The diagnosis handed back carries no fix unless one was asked for.

## Tasks

The following Tasks are required whenever this playbook runs, each with the conditions it states. Numbers identify the Tasks, and pstack text refers to them as steps. Required order is stated under Constraints.

1. Identify the format and load it with the right tool. Parse large artifacts in a subagent (the **principle-guard-the-context-window** skill) and keep the reduced finding in the main thread. Pick each subagent's reasoning level for the job, per the Subagents section.
2. Transform the raw artifact into a form you can query. Dump the trace or heap snapshot into sqlite, one row per sample, frame, or node. Reach the queryable shape before you read.
3. Narrow to the cause. Query for the frames that hold the most time and walk the call tree to the hot path. For a leak, follow the retainer chain from the leaked object to a GC root. For a spindump, find the thread stuck on-CPU or blocked and its wait reason.
4. Attribute to source. Map the hot frame to file, symbol, and line via the artifact's own symbols. A frame with no source mapping is not yet a diagnosis. Resolve the symbols, or say plainly the artifact does not carry them.
5. If you have a paired capture, diff the before and after artifacts to confirm. Otherwise, mark the finding as the strongest hypothesis the artifact supports, not a confirmed cause.
6. Hand back a cited diagnosis, no fix unless asked. Route to Bug fix or Perf issue once the cause is known. Throughput checkpoint stays one line: `throughput checkpoint: n/a, read-only forensics`.

## Outputs

**Reply:** the artifact and format, the reduced finding, the source location, the artifact paths, and whether a paired capture confirmed it.

## Constraints

**You own the diagnosis from the artifact.**

Distinct from **Runtime forensics**, which instruments the live process. Here the capture already exists. The artifact is a fixed dataset, read it, don't re-run it. Keep tooling generic: a DevTools or trace parser for cpuprofile and `.json.gz`, a text editor for a spindump, your heap tooling for a heapsnapshot.

Unless a Task states otherwise, work the Tasks in the order listed. These dependencies are required.

- Step 2 follows step 1, because it transforms the loaded artifact.
- Step 3 follows step 2, because it queries the form step 2 produces.
- Step 4 follows step 3, because it maps the hot frame step 3 finds.
- Step 5 follows step 4, because it confirms the attributed finding or marks it as a hypothesis.
- Step 6 follows step 5, because the diagnosis it hands back says whether a paired capture confirmed it.
