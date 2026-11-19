# Conversion record: Playbooks: investigation and diagnosis

[Conversion guide](../README.md)

## `skills/poteto-mode/playbooks/investigation.md`

Title: Investigation. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Answer the user's question about the code with a cited explanation, or with a recommendation where the request is a decision between alternatives, not a code change.

| Outcome | Basis in the upstream text |
| --- | --- |
| The reply answers the question with a cited explanation, or with a recommendation and a tradeoffs table where the request is a decision between alternatives. | Lead paragraph: "They produce a cited explanation or a recommendation, not a code change." Step 3: "Produce the output (Overview / Key Concepts / How It Works / Where Things Live / Gotchas), or a recommendation with a tradeoffs table if the request is a decision between alternatives." Lead line: "You own the answer." |
| What the explanation or recommendation states about the code agrees with a trace of the code the question is about. | Step 1: "Trace the code the question is about." Lead paragraph: "a cited explanation". Lead line: "You own the answer." Worded so that a cited but wrong explanation fails it (review round 1, W10). |
| The code is unchanged by the investigation. | Lead paragraph: "Investigation requests are read-only. They produce a cited explanation or a recommendation, not a code change." Step 2: `throughput checkpoint: n/a, read-only investigation`. Closing paragraph: "No PR, no babysit, no `architect` unless the investigation precedes a code change." |

Order dependencies stated under Constraints, with the reason for each:

- Step 1 before step 3: the output rests on the trace, a result only step 1 produces.
- Step 3 before step 4: unslop is applied to the reply, which is the output step 3 produces.

State-changing or external effects the work can have, with the condition upstream states:

- None permitted by the playbook itself: no code change, no PR, no babysit. Condition upstream states: "Investigation requests are read-only." "No PR, no babysit, no `architect` unless the investigation precedes a code change. If it does, hand back to the user and re-route to Bug fix or Feature."

Also: 4 statements moved to the section their function calls for; 5 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/poteto-mode/playbooks/bug-fix.md`

Title: Bug fix. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Fix the bug at its cause with the smallest change that runtime evidence justifies.

| Outcome | Basis in the upstream text |
| --- | --- |
| On the matching surface, the original repro fails before the fix and passes after it. | Step 1: "Reproduce it yourself on the matching surface via the control skill". Step 4: "Verify on the same surface. The original repro now passes. "Inconclusive" or wrong-surface is not a pass." Reply: "Paste failing-then-passing repro output verbatim." |
| An inconclusive or wrong-surface verification is flagged and not counted as a pass. | Step 4: "\"Inconclusive\" or wrong-surface is not a pass. Flag it." Same form as perf-issue.md (review round 1, F5). |
| Runtime evidence confirms the mechanism of the root cause the reply names. | Step 2: "Don't guess." "Confirm the surviving *mechanism* with runtime evidence before step 3's `architect` or an `interrogate` fan-out." Reply: "root cause". The elimination method ("Form the candidate hypotheses, then rule them out until one survives.") stays in Task 2 (review round 1, W5). |
| The fix addresses the mechanism of the root cause the reply names. | Step 2 hunts the cause and confirms its mechanism before step 3 plans the fix. Reply: "what was broken, root cause, fix". Discipline paragraph: "Belt-and-suspenders that \"might help\" is a hypothesis, not a fix." Moderate confidence: upstream does not state the fix-to-cause relation as a check (review round 1, W7). |
| Every shipped line traces to runtime evidence. | Discipline paragraph: "Every shipped line traces to runtime evidence." "Belt-and-suspenders that \"might help\" is a hypothesis, not a fix. It does not ship." |
| The shipped change is the smallest that the evidence justifies. | Discipline paragraph: "The smallest change the evidence justifies ships, nothing more." "When evidence refutes a hypothesis, revert what it motivated." |
| The fix is open as a PR per **Opening a PR**. | Step 6: "Run **Opening a PR**." Same form as feature.md and refactoring.md (review round 1, F6). |

Order dependencies stated under Constraints, with the reason for each:

- Step 1 before the fix in step 3: step 4 reruns the original repro, so the failing state must be captured before the fix changes it (baseline).
- Step 2's confirmation of the surviving mechanism before step 3's `architect` or an `interrogate` fan-out: upstream says "before".
- Step 3 before step 4: step 4 verifies the fix.
- Step 5 before step 6: the PR carries the staged commits.
- Kept inside their Tasks, not under Constraints: step 1 "only after driving it as far as it goes"; step 2 "Form the candidate hypotheses, then rule them out"; step 3 "`architect` first"; step 5's commit order in git history (an order on a result).

State-changing or external effects the work can have, with the condition upstream states:

- Code changes: instrumentation or logging added during the hunt (step 2) and the fix implemented by a delegated subagent (step 3). Condition upstream states: No approval stated. Limits: "The smallest change the evidence justifies ships, nothing more." "When evidence refutes a hypothesis, revert what it motivated."
- Git commits staged so the failing repro lands before the fix (step 5). Condition upstream states: No approval stated. The skip clause of step 5 is ambiguous (see findings).
- Opening a PR (step 6, through the Opening a PR playbook, which opens PRs ready). Condition upstream states: No approval stated in this playbook. poteto-mode's Autonomy section governs: reversible work and external actions proceed without asking; irreversible writes always pause.

Also: 3 statements moved to the section their function calls for; 7 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/poteto-mode/playbooks/perf-issue.md`

Title: Perf issue. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Fix a perf issue with a one-off fix whose effect is measured against a baseline, not read from source.

| Outcome | Basis in the upstream text |
| --- | --- |
| Every fix is tied to a measurement, with a baseline trace captured before it and a post-fix trace captured after it. | Lead paragraph: "Tie every fix to a measurement, don't read source instead of measuring." Step 1: "Capture a baseline trace via the matching control skill." Step 3: "Capture a post-fix trace." Reply: "baseline number, post-fix number, delta, artifact path". Lead line: "You own the measurement story." |
| No number the reply or the PR reports claims more than its vetting with the **benchmark-checklist** skill supports. | Step 1: "Vet the baseline, and each later number, with the **benchmark-checklist** skill." benchmark-checklist's description: "Vet a perf measurement ... before you report or act on it." Reply: "baseline number, post-fix number, delta". Step 5 cites the measurement in the PR. Worded as the result the vetting secures, not the act of vetting (review round 1, W2). |
| On the matching surface, the post-fix trace of the shipped fix improves on the baseline. | Lead line: "Tie every fix to a measurement". Step 1 captures the baseline "via the matching control skill"; step 4: "wrong-surface is not a pass". Reply: "delta". README row for this playbook: "trace a measured slowness and improve it against a baseline." Moderate confidence: upstream defines neither "the target" nor "pass", so the Outcome requires an improvement and sets no threshold (review round 1, W1). |
| An inconclusive or wrong-surface comparison is flagged and not counted as a pass. | Step 4: "Parse and compare the artifacts (JSON to sqlite, diff). "Inconclusive" or wrong-surface is not a pass. Flag it." |
| The PR cites the measurement. | Step 5: "Cite the measurement in the PR." |

Order dependencies stated under Constraints, with the reason for each:

- Steps 1 and 2 before step 3: step 3 plans the fix from the trace, and the baseline must be captured before the code it measures changes.
- Step 3 before step 4: the comparison needs the post-fix trace.
- Step 4 before step 5: the cited measurement is the compared one.
- Kept inside their Tasks, not under Constraints: step 2 "without running it first", the mantras "in order, cheapest first" and the stop rule "When an earlier mantra meets the target, stop."; step 3 "`architect` first" and "verifying each attempt before trying the next".

State-changing or external effects the work can have, with the condition upstream states:

- Code changes implemented by a delegated subagent (step 3). Condition upstream states: No approval stated. "Review the diff." "Tie every fix to a measurement".
- Opening a PR and citing the measurement in it (steps 5 and 6, through the Opening a PR playbook). Condition upstream states: No approval stated in this playbook. poteto-mode's Autonomy section governs.
- Trace artifacts and a sqlite database written locally (steps 1, 3, 4). Condition upstream states: None stated.

Also: 3 statements moved to the section their function calls for; 6 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/poteto-mode/playbooks/runtime-forensics.md`

Title: Runtime forensics. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Diagnose a live symptom by instrumenting the running process, and deliver a cited diagnosis, not a fix.

| Outcome | Basis in the upstream text |
| --- | --- |
| The diagnosis rests on a real artifact captured from the live process on the matching surface. | Step 1: "Capture the live signal on the matching surface via the control skill ... A real artifact, not a guess." Lead line: "Instrument the live process, don't theorize from source." |
| The mechanism in the diagnosis is proven on the running process. | Step 3: "Prove the mechanism before believing it. Inject instrumentation via CDP eval on the running process, or hotfix the live code without reloading, to confirm the hypothesis cheaply." Reply: "how you proved the mechanism". |
| The finding is mapped to its file, symbol, and the line that allocates or schedules. | Step 4: "Map the finding back to source: file, symbol, the line that allocates or schedules." Reply: "the source location". |
| The deliverable is a cited diagnosis, with no fix unless one was asked for. | Lead paragraph: "The deliverable is a cited diagnosis, not a fix." Reply paragraph: "No fix unless asked." Scoped to the deliverable so that the live hotfix step 3 permits as a proof does not fail it (review round 1, F2 and W3). |

Order dependencies stated under Constraints, with the reason for each:

- Step 1 before step 2: the reduction works on the captured artifact.
- Step 2 before steps 3 and 4: the proof and the source mapping work from the reduced finding.
- Kept inside its Task, not under Constraints: step 3 "Prove the mechanism before believing it" (no second Task is named).

State-changing or external effects the work can have, with the condition upstream states:

- Injecting instrumentation via CDP eval into the running process (step 3). Condition upstream states: No approval stated. Purpose stated by upstream: "to confirm the hypothesis cheaply".
- Hotfixing the live code without reloading (step 3). Condition upstream states: No approval stated. "No fix unless asked." limits the deliverable (Outcome 4), and the hotfix is a proof step.
- Capturing a CPU profile, heap snapshot, or CDP trace from the live process, written as local artifacts (step 1). Condition upstream states: None stated.

Also: 2 statements moved to the section their function calls for; 5 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/poteto-mode/playbooks/trace-forensics.md`

Title: Trace forensics. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Diagnose the cause from a capture that already exists, and hand back a cited diagnosis, with no fix unless asked.

| Outcome | Basis in the upstream text |
| --- | --- |
| The finding comes from the existing artifact, read and not re-run. | Paragraph before step 1: "Here the capture already exists. The artifact is a fixed dataset, read it, don't re-run it." Lead line: "You own the diagnosis from the artifact." |
| The cause is mapped to file, symbol, and line, or the reply says plainly that the artifact does not carry the symbols. | Step 4: "Attribute to source. Map the hot frame to file, symbol, and line via the artifact's own symbols. A frame with no source mapping is not yet a diagnosis. Resolve the symbols, or say plainly the artifact does not carry them." Reply: "the source location". |
| Where a paired capture exists, whether the finding is confirmed rests on a diff of the before and after artifacts. Otherwise the finding is marked as the strongest hypothesis the artifact supports, not a confirmed cause. | Step 5: "If you have a paired capture, diff the before and after artifacts to confirm. Otherwise, mark the finding as the strongest hypothesis the artifact supports, not a confirmed cause." Reply: "whether a paired capture confirmed it". The condition "Where a paired capture exists" keeps step 5's "Otherwise" (review round 1, F1). |
| The diagnosis handed back carries no fix unless one was asked for. | Step 6: "Hand back a cited diagnosis, no fix unless asked." Scoped to the hand-back as step 6 is. |

Order dependencies stated under Constraints, with the reason for each:

- Step 1 before step 2: the transform works on the loaded artifact.
- Step 2 before step 3: upstream says "Reach the queryable shape before you read", and step 3 queries that form.
- Step 3 before step 4: the hot frame must be found before it is mapped.
- Step 4 before step 5: the finding must exist before it is confirmed or marked.
- Step 5 before step 6: the diagnosis handed back says whether a paired capture confirmed it.

State-changing or external effects the work can have, with the condition upstream states:

- A sqlite database written locally from the trace or heap snapshot (step 2). Condition upstream states: None stated. "The artifact is a fixed dataset, read it, don't re-run it."
- No external effect and no fix. Condition upstream states: "Hand back a cited diagnosis, no fix unless asked."

Also: 3 statements moved to the section their function calls for; 8 additions other than the Purpose and Outcomes (fixed sentences, pointers).
