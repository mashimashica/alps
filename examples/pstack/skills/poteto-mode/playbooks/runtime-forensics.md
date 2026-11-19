# Runtime forensics

## Purpose

Diagnose a live symptom by instrumenting the running process, and deliver a cited diagnosis, not a fix.

## Outcomes

- The diagnosis rests on a real artifact captured from the live process on the matching surface.
- The mechanism in the diagnosis is proven on the running process.
- The finding is mapped to its file, symbol, and the line that allocates or schedules.
- The deliverable is a cited diagnosis, with no fix unless one was asked for.

## Tasks

The following Tasks are required whenever this playbook runs, each with the conditions it states. Numbers identify the Tasks, and pstack text refers to them as steps. Required order is stated under Constraints.

1. Capture the live signal on the matching surface via the control skill: a CPU profile for a spinning process, a heap snapshot for a leak, a CDP trace for a visual glitch. A real artifact, not a guess.
2. Reduce the artifact to the smoking gun: the function on the hot path, the retainer chain from the leaked object to a GC root, the loop firing without input. Parse large artifacts in a subagent (the **guard-the-context-window** principle skill), keep the reduced finding in the main thread. Pick each subagent's reasoning level for the job, per the Subagents section.
3. Prove the mechanism before believing it. Inject instrumentation via CDP eval on the running process, or hotfix the live code without reloading, to confirm the hypothesis cheaply.
4. Map the finding back to source: file, symbol, the line that allocates or schedules.
5. Throughput checkpoint stays one line: `throughput checkpoint: n/a, read-only forensics`.

## Outputs

**Reply:** the signal captured, the reduced finding, how you proved the mechanism, the source location, artifact paths. No fix unless asked. Hand back to Bug fix or Perf once the cause is known.

## Constraints

**You own the diagnosis. Instrument the live process, don't theorize from source.** The deliverable is a cited diagnosis, not a fix.

Unless a Task states otherwise, work the Tasks in the order listed. These dependencies are required.

- Step 2 follows step 1, because it reduces the captured artifact.
- Steps 3 and 4 follow step 2, because they work from the reduced finding.
