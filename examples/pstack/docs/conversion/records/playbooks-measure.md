# Conversion record: Playbooks: measurement, evaluation, and prototypes

[Conversion guide](../README.md)

## `skills/poteto-mode/playbooks/hillclimb.md`

Title: Hillclimb. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Improve one measurable thing against a target through sustained iteration rather than a one-off fix, with the metric and the experiment's integrity intact.

| Outcome | Basis in the upstream text |
| --- | --- |
| Where a case reproduces the user's complaint, the frozen harness reproduces the symptom on the target case and separates easier cases as expected. | Step 1: "select a case that reproduces the user's complaint". Step 2: "Build the measurement harness, prove its sensitivity, then freeze it" and "Run contrasting realistic workloads and confirm the target case reproduces the symptom while easier cases separate as expected. If the harness cannot distinguish them, revise the workload or metric." Lead line: "You own the metric". The condition is step 1's own alternative: "If no case reproduces it, fix the repro instead of hillclimbing." (profile 15.3). |
| Every change the run keeps has its own before and after measurement on the frozen harness, with the regression gate green. | Lead paragraph 2: "Core discipline: one change, one measurement, keep or revert. Never stack untested changes, and never claim a win from code inspection". Step 5: "Measure before and after with the frozen harness, and run the regression gate." and "Accept only when the metric moves past noise and the gate stays green." Step 6: "keep a simplification that holds the number". The Outcome states only what steps 5 and 6 agree on. The accept criterion itself stays in Tasks 5 and 6 (see findings on their conflict). |
| No change the run keeps breaks behavior. | Step 6: "Correctness and simplicity outrank the number. Revert a win that breaks behavior". Step 2 and step 5: the regression gate ("the tests that must keep passing") is upstream's check, but step 6 states the result itself. |
| Every attempt the run does not keep is reverted in full. | Step 5: "Otherwise revert the change in full. A tweak that \"might help\" is not kept." Lead paragraph 2: "keep or revert". Step 6: "Revert a win that breaks behavior". |
| Where a case reproduces the user's complaint, the decision log has one row per attempt, kept or reverted. | Step 3: "A `decision.tsv`, one row per attempt". Step 5: "Log the row either way, kept or reverted." Reply: "iterations run (kept vs reverted)" and "the `decision.tsv` path". Conditioned on step 1's repro case because the log belongs to the hillclimb that step 1's alternative replaces. |
| Where a case reproduces the user's complaint, the stop predicate is met without being relaxed, or the run stops because the remaining ideas are marginal and not worth their cost while no cheap untried hypothesis remains, or the run is stuck and surfaces that. | Step 7: "Stop when the predicate is met, or when the remaining ideas are marginal and not worth their cost. Don't relax the predicate to meet it, and don't quit while cheap untried hypotheses remain. If you are stuck, surface it instead of spinning." Step 1: "a checkable stop predicate that pairs a target with a floor on attempts". The first two endings are upstream's. Treating "surface it instead of spinning" as a third ending is the converter's reading. "while no cheap untried hypothesis remains" carries step 7's limit on quitting onto the marginal-ideas ending. Conditioned on step 1's repro case (profile 15.3). |
| The accepted fixes are one commit each, stacked in the order they landed. | Step 5: "One commit per accepted fix". Step 8: "Run **Opening a PR** with the accepted commits stacked in the order they landed." README playbook table: "one commit per accepted win". |

Order dependencies stated under Constraints, with the reason for each:

- Step 1 comes before steps 2, 4, and 7. Step 2 measures its metric and case, step 4 uses its architecture model, and step 7 applies its stop predicate. Reason: steps 2, 4, and 7 use results only step 1 produces (the metric and case, the architecture model, the stop predicate).
- Step 2 freezes the harness and records the baseline metric and a green run of the regression gate before any change in step 5. Reason: upstream order word "before any change"; the baseline captures state that step 5 changes, and step 5 measures with the harness step 2 freezes.
- Step 3 opens the decision log before the first attempt in step 5. Reason: upstream order word "before each attempt"; step 5 reads and appends to the log step 3 opens.
- Step 5 repeats, one hypothesis per iteration, until step 7 stops the run. Reason: step 5's "Loop" and step 7's "Stop when"; without this item the listed order could read as steps 5, 6, 7 once each.
- On a stall, step 6 comes before step 7 concludes the hill is climbed, and the run goes on with step 5. Reason: upstream order word "before concluding"; step 7 is where the run concludes, and step 6's further attempts are step 5 iterations.
- Step 8 uses the commits that step 5 accepted. Reason: step 8 uses a result only step 5 produces.

State-changing or external effects the work can have, with the condition upstream states:

- Local commits: "One commit per accepted fix, staging only the files you changed (`git add <files>`, never `-A`)". No approval stated. Condition: only for an accepted fix.
- Reverting working-tree changes: "Otherwise revert the change in full". No approval stated. Condition: the metric did not move past noise or the gate is not green.
- Creating git worktrees for parallel subagents: "each in its own worktree". No approval stated. Condition: several independent hypotheses are live.
- Spawning subagents on the configured hillclimb model (step 5). No approval stated.
- Writing the decision log `decision.tsv`, kept "out of the tree (gitignored)". No approval stated.
- Opening a PR through **Opening a PR** (step 8), which pushes a branch and opens a PR ready for review on the forge. This file states no approval. poteto-mode's Autonomy section governs ("Always pause for irreversible writes").
- For an unattended run, starting the wake mechanism borrowed from the Autonomous run playbook (Cursor's `/loop`, named in that playbook). Condition: "If the run is unattended".

Also: 4 statements moved to the section their function calls for; 9 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/poteto-mode/playbooks/eval.md`

Title: Eval. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Establish whether a variant under test produces the behavior that counts as success, through an experiment whose candidates and judge are blinded, as the basis for a recommendation for whether to promote the variant.

| Outcome | Basis in the upstream text |
| --- | --- |
| Every candidate stays blind, with nothing it sees breaking a non-negotiable for blinding or showing the rubric. | Non-negotiables for blinding, bullets 1 to 5: "No `eval`, `test`, `judge`, `experiment`, `rubric`, `score`, `compare`, `benchmark`, `candidate`, or `arena` in any directory, file, or prompt the candidate sees.", "The candidate prompt looks like an organic user request.", "No chain-eliciting cues.", "Sanitize directory and slug names.", "Don't tell the candidate other candidates exist." Step 1: "Write the rubric (3-6 concrete criteria) for the judge only. Hold it back from candidates." Step 3: "No leakage of what's being measured." |
| The judge sees outputs by sanitized label and the rubric, never a model name. | Non-negotiables bullet 6: "The judge can know it's judging but sees outputs by sanitized label only, never by model name." Step 5: "Judge sees outputs by sanitized label and the rubric, never a model name." |
| Where two variants are compared, one judge scores both sets in a single pass on one scale, blind to which set each came from. | Non-negotiables bullet 7: "Comparing two variants: one judge scores both sets in a single pass on one scale, blind to which set each came from." The condition "Where two variants are compared" is upstream's. |
| Chain-following is graded from the files each candidate actually opened and the shape of its code, never from the candidate's own claims. | Step 6: "Verify the chain from transcripts, not self-report." and "Look at which files each candidate actually opened. Grade chain-following from the files it really read plus the shape of the code, never from the candidate's own claims." Non-negotiables bullet 3: "grade chain-following from code shape, not self-report". |
| The synthesis and the recommendation for whether to promote the variant rest on every candidate output, read end to end by the agent running the playbook and compared with the judge's verdict. | Step 7: "Read every candidate output yourself end to end. Compare to the judge's verdict. Disagreement means a model is biased or the rubric is ambiguous. Synthesize." Reply: "your synthesis, and a recommendation for whether to promote the variant". Lead line: "You own the experiment design." |

Headings whose text changed:

- "**Steps:** (bold label line before the numbered list)" became "## Tasks". Profile section 7 puts the numbered list under `## Tasks`. The governing sentence says pstack text refers to the items as steps. The token screen reports this label as absent for that reason.

Order dependencies stated under Constraints, with the reason for each:

- Step 4 uses the sanitized dirs from step 2 and the prompt from step 3. Reason: step 4 uses results only steps 2 and 3 produce.
- Step 5 gives the judge the rubric from step 1 and the outputs from step 4. Reason: step 5 uses results only steps 1 and 4 produce.
- Step 6 reads the transcripts of the candidates from step 4. Reason: step 6 reads what step 4's candidates leave behind.
- Step 7 compares with the judge's verdict from step 5. Reason: step 7's comparison uses the verdict only step 5's judge produces.

State-changing or external effects the work can have, with the condition upstream states:

- Creating a per-candidate working dir with the variant in place and planted context (step 2). No approval stated. The playbook does not say where the dirs live, so they can be outside the repository.
- Spawning N candidate subagents and one judge subagent (steps 4 and 5). No approval stated.
- Reading candidate transcripts under the active workspace's `agent-transcripts/` directory (step 6). Read only. Prohibition: "Do not glob across `~/.cursor/projects/*/`."
- The playbook recommends whether to promote the variant. It does not promote it, and it has no **Opening a PR** step.

Also: 3 statements moved to the section their function calls for; 7 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/poteto-mode/playbooks/prototype.md`

Title: Prototype. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Make a design decision cheaply, with a throwaway prototype as the instrument. The real build is not part of this work.

| Outcome | Basis in the upstream text |
| --- | --- |
| The decision the prototype exists to make has a recommendation with the alternatives and their tradeoffs, or the work is routed to Feature because there is no decision to make. | Step 1: "Scope the decision the prototype exists to make" and "No decision means no prototype. Route to Feature." Step 6: "Present alternatives, tradeoffs, and a recommendation. The output is the decision plus the throwaway artifact, not shippable code." Reply: "the variants explored", "tradeoffs, your recommendation". Lead line: "You own the design decision, not the code." The second ending is upstream's ("Route to Feature"). |
| The evidence for each variant is an observation on the matching surface, screenshots for a visual decision and the observed output or timing for a behavioral one. | Step 5: "Verify on the matching surface. For a visual decision, screenshot each variant via the control skill and drive the interaction. For a behavioral or timing decision, observe the thing you are deciding by logging the timing, printing the output, or watching the render. The observation is the test here, not an assertion." Reply: "the evidence (screenshots for a visual decision, the observed output or timing for a behavioral one)". |
| The prototype code sits in an isolated scratch dir, separate from production source. | Step 3: "Build throwaway in an isolated scratch dir, separate from production source." Reply: "the scratch path". |
| The prototype is presented as throwaway, not as shippable code. | Reply: "Say plainly that the prototype is throwaway." Step 6: "The output is the decision plus the throwaway artifact, not shippable code." Lead line: "The prototype is a throwaway instrument." |

Order dependencies stated under Constraints, with the reason for each:

- Step 1 scopes the decision before anything is built. Reason: step 1 is the gate for building at all.
- When step 2 applies, the user picks directions before step 3 builds. Reason: upstream order word "before building", under step 2's own condition.
- Step 5 observes the variants that steps 3 and 4 build. Reason: step 5 uses a result only steps 3 and 4 produce.

State-changing or external effects the work can have, with the condition upstream states:

- Writing throwaway code "in an isolated scratch dir, separate from production source" (step 3). The dir can be outside the repository. No approval stated.
- Fetching CDN deps and running "a dev server with hot reload" (step 3). Network use and a local process. No approval stated.
- Driving the prototype and taking screenshots "via the control skill" (step 5). No approval stated.
- Asking the user to pick directions before building (step 2). Condition: "when the design space is open". "Skip when the direction is set."
- Handing the chosen direction to **Feature** (or `architect` for the shape) for the real build (step 6). The playbook produces no shippable code and has no **Opening a PR** step.

Also: 3 statements moved to the section their function calls for; 6 additions other than the Purpose and Outcomes (fixed sentences, pointers).

## `skills/poteto-mode/playbooks/visual-parity.md`

Title: Visual parity. The Purpose and Outcomes below are derived by the conversion.

**Purpose.** Hold pixel-exact equivalence through a migration, so that each migrated component matches its baseline.

| Outcome | Basis in the upstream text |
| --- | --- |
| Every component reported as migrated has a zero image diff against its baseline on the matching surface. | Lead: "You own pixel-exact equivalence." and "Equivalence is verified by image diff, not by eye." Step 1: "No baseline, no parity claim." Step 4: "Verify each component against its baseline via image diff on the matching surface via the control skill. A nonzero diff is a fail. Investigate the pixel delta. `/loop` per component until the diff is zero." Reply: "components migrated, the diff result for each". |
| The baseline every diff runs against is the one established before any migration, untouched by the run. | Step 1: "Establish the baseline first, before any migration". Lead: "The baseline is the spec. You do not touch it." Step 2: "no baseline tampering" and "If the baseline looks wrong, stop and ask, don't edit it." |
| No diff passes because of a harness modification or a component restructuring made to pass it. | Step 2: "no harness modifications, no baseline tampering, no component restructuring to make a diff pass". The Outcome states what both readings of the clause require (see findings). |
| Each component is reported either as migrated, with its diff result, or as part of what is left. | Reply: "components migrated, the diff result for each, the baseline harness location, what's left." |

Order dependencies stated under Constraints, with the reason for each:

- Step 1 establishes the baseline before any migration in step 3. Reason: upstream order words "first, before any migration"; the baseline captures the state that step 3 changes.
- For each component, step 4 verifies it after step 3 migrates it and before step 5 opens its PR. Reason: step 4 verifies what step 3 produces and is the pass or fail verdict ("A nonzero diff is a fail") ahead of step 5's PR. Stated per component because step 3 parallelizes "one owner per component", so the listed order holds within a component and not across components.

State-changing or external effects the work can have, with the condition upstream states:

- Creating the visual regression harness and its baseline screenshots (step 1). No approval stated.
- Editing the harness or the baseline is prohibited (step 2). Condition for a baseline that looks wrong: "stop and ask, don't edit it."
- Migrating components, in parallel git worktrees with one owner per component (step 3). No approval stated.
- Starting Cursor's `/loop` per component until the diff is zero (step 4). No approval stated.
- Opening a PR per component or per safe batch through **Opening a PR** (step 5), which pushes a branch and opens a PR ready for review. This file states no approval. poteto-mode's Autonomy section governs.

Also: 3 statements moved to the section their function calls for; 5 additions other than the Purpose and Outcomes (fixed sentences, pointers).
