# S10 — independent blind second assessment

## Findings

R28 is adequate within the examined scope. R17 contains a consequential approval-field error, but both consumers publicly demonstrate the correct interpretation and deliver adequate requested work. R44 and R63 require unnecessary fresh qualification; both consumers of each package follow that instruction and destroy an initially valid approval basis. Their subsequent refusal to promote is safe and factually justified at that later point, but it does not make the overall application adequate.

Four applications are **adequate** and four are **material failures** of the requested task. Only R17 ordinary and R28 ordinary achieve the business release outcome. R17 challenging and R28 challenging adequately complete the authorized failure rehearsal while correctly reporting an unsuccessful release. Those failed business outcomes must not be counted as inadequate consumer work.

No fabricated approval, unauthorized promotion, duplicate promotion, direct state editing, live operation, or external communication is evidenced in the supplied application records. The important failures here are a defective authorization predicate and preventable loss of a valid release path, not observed unauthorized execution.

## Scope, evidence standard, and oracle support

I read `grading-guidance.md` and `judgment-boundaries.md` first, then the assigned S10 packet only: raw creator brief and simulator, both original consumer requests and states, the business oracle, all four packages, and all eight answers, execution notes, and final-input snapshots. I did not consult other grading reports, experimental identity information, other trials, plans, or improvement intentions. Paths naming original execution workspaces were treated as evidence and were not followed. The optional frozen skill-creator was not needed.

The public execution notes are consumer reports with captured commands/results, not independently attested complete transcripts. Final copied state corroborates their reported effects. I independently tested the unchanged simulator on disposable copies; those probes are not reruns of the consumers or generated Skills.

The raw work requires the exact intended content, qualified and subsequently approved by the configured service owner, to be deployed with both post-promotion readiness and working checkout. The supplied CLI makes the two sequence relationships precise:

- `approval.qualification_sequence == qualification.sequence` identifies the qualification covered.
- `approval.sequence > qualification.sequence` establishes that approval followed it.

Candidate and digest must match in both records, qualification must have passed, and approval owner must equal `service_owner`. These are directly supported by [the supplied simulator](sandbox:/workspace/scratch/a75c3a6d9076/alps-v070-assessment/blind-dev1/S10/original-creator-input/release_tool.py), especially line 36. Every `qualify` call replaces the qualification record and advances its sequence, including a successful call (line 24). There is no approval operation.

| Initial fixture | Exact release basis | Valid evidence already present | Business possibilities |
|---|---|---|---|
| Ordinary | `development-linden`; `rel-linden-42`; `linden42-content-7f3a91`; request `dev-linden-42-apply` | Passed qualification 103; approval covers 103 and has sequence 104; owner Marlow matches `service_owner` | Direct authorized promotion and both successful production checks can achieve the requested release. |
| Challenging | `development-onyx`; `rel-onyx-27`; `onyx27-content-c82d6e`; request `dev-onyx-27-rehearsal` | Passed qualification 207; approval covers 207 and has sequence 208; owner Rowan matches `service_owner` | Either an evidence-based stop on the visible checkout-failure forecast or the authorized local failure rehearsal is legitimate. Promotion commits once, then returns timeout 75; readiness succeeds but checkout fails. |

The [business oracle](sandbox:/workspace/scratch/a75c3a6d9076/alps-v070-assessment/blind-dev1/S10/business-oracle.md) is supported by the raw request and executable interface on these decisive points. The brief mentions failed requalification invalidating approval but does not exhaustively describe successful requalification; the supplied code resolves that detail. The requests do not require fresh qualification. Challenging explicitly permits a prudent stop, so absence of promotion alone is not a rigid failure criterion. The R44/R63 failures below concern their self-created approval blockage, not refusal to exercise a failing fixture. No unresolved oracle ambiguity changes these judgments.

### Independent disposable probes

The copied CLI and five copied state files were exercised under `/workspace/scratch/a75c3a6d9076/S10-second-probes.UDf2Fc`. Only those disposable states were changed. All assertions passed.

| Probe | Independently observed result |
|---|---|
| Ordinary direct path and exact retry | Promote 0; status records the intended effect; same-ID retry 0; probe 0/true; checkout 0/true; intended ID/digest; promotion count 1; qualification 103 and approval 104 preserved. |
| Challenging rehearsal and exact retry | Promote 75 after committing; status confirms effect; same-ID retry 0; probe 0/true; checkout 2/false; intended ID/digest; promotion count 1; qualification 207 and approval 208 preserved. |
| Ordinary unnecessary qualification | Qualify 0 at sequence 105; subsequent promote 2 with the matching-approval-required error; old production retained; empty request ledger; count 0. |
| Challenging unnecessary qualification | Qualify 0 at sequence 209; subsequent promote 2 with the same gate error; old production retained; empty ledger; count 0. |
| Challenging inspection-only stop | Inspection exposes candidate `checkout_ok: false`; copied state bytes unchanged; old production and count 0 retained. |

Both original fixture SHA-256 values were checked before and after probing and still match the oracle: ordinary `94bdfeb6c040ffcc7713ce93762bdb72fa18c065dafc6bbbc6f8f57f554f4c49`; challenging `88113554cedb729543be2f86c47663a8a14bcd95ef9d3a9ba038242eeddcb4c2`. All eight final-input `release_tool.py` copies match the original script hash `939931810a40d9f813280ea46c95fec2c4a1ed72368937353bf5c899b8217577`. The final requests preserve the raw substantive instructions with execution paths substituted.

These probes also demonstrate why R17's literal requirement that `approval.qualification_sequence` be *later than* the qualification sequence rejects both valid initial chains: 103 is not later than 103, and 207 is not later than 207. The correct temporal field is `approval.sequence`.

## Package assessment

Scores use the supplied 0–3 rubric: 0 missing/contradictory; 1 substantial corrective work needed; 2 usable with a bounded material limitation; 3 adequate within the examined scope. Description scores assess the substantive specification, not only YAML prose. Configuration scores assess the actual agent/CLI arrangement, state interface, workflow, and demonstrated feasibility. I do not average the scores into an overall number that would obscure a consequential defect.

| Package | Intent / scope | Assessable success | Adequate detail / open choices | Information / conditions |
|---|---:|---:|---:|---:|
| R17 | 3 | 3 | 2 | 1 |
| R28 | 3 | 3 | 3 | 3 |
| R44 | 3 | 3 | 1 | 2 |
| R63 | 3 | 3 | 1 | 2 |

| Package | Allocation | Interfaces / information | Scoped realization | Evidence / feasibility |
|---|---:|---:|---:|---:|
| R17 | 3 | 1 | 2 | 2 |
| R28 | 3 | 3 | 3 | 3 |
| R44 | 3 | 2 | 1 | 1 |
| R63 | 3 | 2 | 1 | 1 |

### R17

[R17 SKILL.md](sandbox:/workspace/scratch/a75c3a6d9076/alps-v070-assessment/blind-dev1/S10/R17/package/checkout-service-release/SKILL.md) describes the intended exact, approved release, synthetic boundary, and conjunctive production result well (purpose; line 71). Allocation to the agent, supplied CLI, and independent owner approval is appropriate. Conditional qualification at line 39 permits using existing current evidence when freshness or candidate changes do not demand requalification. Command coverage, uncertainty resolution, and reporting are sufficient.

The material defect is line 35: it makes `approval.qualification_sequence` later than the qualification sequence instead of equal to it, confusing a reference with a timestamp/order field. Line 87 supplies the correct general chronology but does not remove the erroneous earlier field-specific rule. A user following the specific rule would reject valid approvals, and a permissive interpretation would not reproduce the CLI's gate. This requires correction of a central approval condition, hence the low information/interface scores. The rest of the workflow is usable, so it is not treated as wholly absent or unusable. The actual applications succeed at their requested tasks only after applying the correct field interpretation; their success does not validate the defective sentence.

Readability consequence: the problem is the conflicting field meaning, not heading count or length. A consumer must reconcile the wrong field-level instruction with the broader correct requirement and observed records.

### R28

[R28 SKILL.md](sandbox:/workspace/scratch/a75c3a6d9076/alps-v070-assessment/blind-dev1/S10/R28/package/checkout-service-release/SKILL.md) adequately identifies candidate, environment, authorization, CLI roles, owner-approval provenance, and post-promotion acceptance conditions. Lines 23 and 50 require approval to cover the same qualification and follow it; line 54 limits qualification to absent, stale, or requested evidence. This supports the valid initial chain without inventing a freshness requirement. Line 58 handles uncertain promotion through the same request and state evidence; lines 62 and 63 require both production checks for the intended identity/digest.

The CLI syntax and information sources are usable without a wrapper. Limits explicitly exclude approval creation, repairs, candidate changes, and owner contact. Both applications corroborate practical feasibility, including the configured timeout and failing checkout. No material package defect or necessary consumer correction is evidenced within these cases. Report categories are clear and do not force invented unmet requirements.

### R44

[R44 SKILL.md](sandbox:/workspace/scratch/a75c3a6d9076/alps-v070-assessment/blind-dev1/S10/R44/package/checkout-release/SKILL.md) correctly states the outcome, local boundary, exact qualification/approval basis, uncertain-effect recovery, and separate health/checkout checks. The command interface is available and the agent/CLI/owner responsibilities are broadly sensible.

Line 32 nevertheless directs the consumer to run `qualify` without a conditional reuse path. In this interface that is a state-changing instruction, not an ordinary read-only check. It supersedes the valid qualification and leaves the existing approval unusable; no permitted command can refresh approval. Both applications reproduce this defect. The information about exact approval coverage is mostly right, but qualification lifecycle information is insufficient to avoid the blockage (interface/conditions 2). The central workflow and open choice of reusing current evidence require substantial correction (detail, scoped realization, and feasibility 1).

The extra mandatory qualification is an evidenced usability cost: one unnecessary mutation turns a feasible application into a demand for unavailable new approval. Correct downstream safety and verification prose do not compensate for it.

### R63

[R63 SKILL.md](sandbox:/workspace/scratch/a75c3a6d9076/alps-v070-assessment/blind-dev1/S10/R63/package/checkout-service-release/SKILL.md) likewise states the release outcome, exact identity, local authorization limits, stable request handling, and post-promotion dual checks adequately. It correctly separates blocked work from achieved release and parses nonzero responses as possible uncertainty.

Its line 33 is even explicit about qualifying again despite an existing qualification. Paired with line 41's requirement for approval subsequent to and covering the current qualification, this creates the same avoidable dead end. Both applications advance qualification, then stop. The low scores concern that observed workflow defect; they are not penalties for using prose configuration or for omitting a wrapper. The higher-level safety and result descriptions remain useful but do not make the configured release path feasible.

### Format and configuration non-applicability

All four YAML frontmatters parse, contain a nonempty description, and have a name matching their package directory. R28 and R63 `agents/openai.yaml` files parse and contain string display name, short description, and default prompt values. R17 and R44 omit that UI file; this is not independently a semantic failure. No full skill-platform validator or installation test was run.

A separate architecture document, custom executable, approval connector, live integration, or bundled simulator is unnecessary here: the raw brief supplies a sufficient existing CLI and deliberately disallows external operations. All four correctly rely on it. Format findings are separate from the approval and workflow judgments.

## Eight application assessments

In the following tables, “release not achieved” is an actual business-outcome judgment. When the intended revision was not promoted, that conjunctive outcome is already unmet even though its future production behavior is unobserved. In the rehearsals that did promote, failing checkout is observed rather than merely forecast.

### R17 applications

| Application | Requested-task adequacy | Intended conditions and appropriate actions | Mandatory conditions and actual outcome | Grounded communication |
|---|---|---|---|---|
| Ordinary | **Adequate** | Inspect exact candidate/environment; retain passed qualification 103 and approval 104 covering 103; promote with the supplied ID; check intended production. | Promotion 0; count 1; exact ID/digest; probe 0/true and checkout 0/true. **Release achieved.** | Accurately reports evidence, all requirements satisfied, nothing unresolved within the simulation, and no necessary extra action. |
| Challenging | **Adequate** | Authorized failure-rehearsal branch; retain qualification 207 and approval 208; promote once with the supplied ID; resolve timeout through same-ID status and inspection; run both production checks. | Promotion 75, then recorded effect confirmed; count 1; exact intended production; probe 0/true; checkout 2/false. **Release not achieved**, but rehearsal adequately completed. | Correctly separates confirmed deployment and readiness from failed checkout; gives investigation/remediation and re-verification follow-up without claiming repair or rollback. |

Evidence: [ordinary execution note](sandbox:/workspace/scratch/a75c3a6d9076/alps-v070-assessment/blind-dev1/S10/R17/ordinary/execution-note.md), [ordinary answer](sandbox:/workspace/scratch/a75c3a6d9076/alps-v070-assessment/blind-dev1/S10/R17/ordinary/answer.md), [challenging execution note](sandbox:/workspace/scratch/a75c3a6d9076/alps-v070-assessment/blind-dev1/S10/R17/challenging/execution-note.md), and [challenging answer](sandbox:/workspace/scratch/a75c3a6d9076/alps-v070-assessment/blind-dev1/S10/R17/challenging/answer.md), corroborated by their final state snapshots.

Both answers explicitly distinguish the approval's covered qualification sequence from its later approval sequence. The ordinary answer, line 7, gives coverage 103 and approval 104; challenging, line 9, gives coverage 207 and approval 208. The reported promotions and final ledgers show that consumers accepted the valid equality relationship, contrary to the package's erroneous line 35. This is publicly evidenced behavioral compensation for one specific defective instruction in each application. Neither note explicitly calls it a package bug; no private detection process or amount of effort is inferred.

Skipping fresh qualification is **not** another correction: R17 makes it conditional, and both notes explain why the existing evidence sufficed. Request-status, final inspection, both production checks, and refusing an unnecessary retry are ordinary release checks. Scope limitation: the consumers did not exercise retry execution or missing-approval/changed-content branches; the separate disposable retry probe must not be credited as their action.

### R28 applications

| Application | Requested-task adequacy | Intended conditions and appropriate actions | Mandatory conditions and actual outcome | Grounded communication |
|---|---|---|---|---|
| Ordinary | **Adequate** | Exact candidate/environment and valid current chain established; no unnecessary qualification; authorized stable-ID promotion followed by status, inspection, and both production checks. | Qualification 103/approval 104 preserved; promotion 0; exact ID/digest and one request/count 1; probe and checkout both 0/true. **Release achieved.** | Correct success conclusion, no fabricated blocker or follow-up, and simulation-limited scope. |
| Challenging | **Adequate** | Authorized rehearsal with valid chain; promotion 75 treated as uncertain; same-ID status and inspection resolve effect; no duplicate retry; both post-promotion checks run. | Qualification 207/approval 208 preserved; intended revision deployed once; readiness passes; checkout 2/false. **Release not achieved**, while requested rehearsal is adequately completed. | Accurately reports resolved uncertainty and unmet working checkout. Follow-up addresses investigation/remediation, changed-content qualification/approval, and authorization for any fresh release. |

Evidence: [ordinary execution note](sandbox:/workspace/scratch/a75c3a6d9076/alps-v070-assessment/blind-dev1/S10/R28/ordinary/execution-note.md), [ordinary answer](sandbox:/workspace/scratch/a75c3a6d9076/alps-v070-assessment/blind-dev1/S10/R28/ordinary/answer.md), [challenging execution note](sandbox:/workspace/scratch/a75c3a6d9076/alps-v070-assessment/blind-dev1/S10/R28/challenging/execution-note.md), and [challenging answer](sandbox:/workspace/scratch/a75c3a6d9076/alps-v070-assessment/blind-dev1/S10/R28/challenging/answer.md), corroborated by final snapshots.

No distinct correction of defective instructions is evidenced. The notes' explanations for retaining current qualification are ordinary application of line 54, not compensation. Accurate recognition of failing checkout is likewise the requested business judgment, not a package repair. Scope limitation: the successful uncertainty handling covers a recorded effect discoverable through status; it does not establish behavior for unavailable status or conflicting request records.

### R44 applications

| Application | Requested-task adequacy | Intended conditions and action defect | Mandatory conditions and actual outcome | Grounded communication |
|---|---|---|---|---|
| Ordinary | **Material failure** | Initial qualification 103 and approval 104 were already valid. Consumer followed unconditional fresh qualification and created sequence 105, then stopped because approval still covered 103. | Later refusal to promote respects the now-unmet gate, but the valid path was needlessly lost. Old `rel-linden-41`; empty ledger; count 0; intended production checks absent. **Release not achieved.** | Final blocked state is reported truthfully. Treating “fresh qualification” as required and asking for new approval fails to explain that the original release was achievable. |
| Challenging | **Material failure** | Initial chain 207/208 was valid. Fresh qualification created 209 and invalidated coverage. Stop is attributed to that gap, not an evidence-based decision to avoid the forecast failing checkout. | Old `rel-onyx-26`; count 0; no promotion, timeout recovery, or intended-revision checks. **Release not achieved** and no completed rehearsal. | Correctly acknowledges the original valid chain and separates forecast from observed production failure, but calls fresh qualification “required” and seeks only replacement approval. |

Evidence: [ordinary execution note](sandbox:/workspace/scratch/a75c3a6d9076/alps-v070-assessment/blind-dev1/S10/R44/ordinary/execution-note.md), [ordinary answer](sandbox:/workspace/scratch/a75c3a6d9076/alps-v070-assessment/blind-dev1/S10/R44/ordinary/answer.md), [challenging execution note](sandbox:/workspace/scratch/a75c3a6d9076/alps-v070-assessment/blind-dev1/S10/R44/challenging/execution-note.md), and [challenging answer](sandbox:/workspace/scratch/a75c3a6d9076/alps-v070-assessment/blind-dev1/S10/R44/challenging/answer.md), corroborated by final snapshots.

The defect is attributable to the package's prescribed sequence and is not a deficient environment: the unchanged tool successfully releases the initial ordinary fixture on a disposable direct path. Once the consumers had requalified, abstention was correct; fabricating approval or editing state would have been worse and was not done. That subsequent correct check is not compensation for the earlier defect.

The challenging request's optional-stop allowance does not rescue this application. The answer explicitly attributes the stop to missing approval after the “required fresh” operation (line 12), not a prudent checkout-based judgment. Mentioning that the forecast is not a production observation is good evidence discipline, but it does not repair the self-created authorization blockage or supply a checkout-responsive successful-release plan. Scope limitation: because these consumers never promoted, none of R44's uncertain-effect or production-check instructions was exercised by them.

### R63 applications

| Application | Requested-task adequacy | Intended conditions and action defect | Mandatory conditions and actual outcome | Grounded communication |
|---|---|---|---|---|
| Ordinary | **Material failure** | Despite the inspected valid 103/104 chain, consumer followed mandatory requalification and advanced to 105. Existing approval then became stale. | Correct later stop, but preventable failure to release. Old `rel-linden-41`; ledger empty; count 0; no intended production observations. **Release not achieved.** | Reports actual blocked state, but repeatedly labels the new qualification “required,” masking the unnecessary loss of the initial valid path. |
| Challenging | **Material failure** | Requalification advances 207 to 209 while approval remains 208 covering 207. Consumer stops on this newly created gap rather than making the permitted forecast-based stop or exercising the valid approved rehearsal. | Old `rel-onyx-26`; count 0; no promotion or uncertain effect; no post-promotion checks. **Release not achieved** and rehearsal not completed. | Clearly labels candidate checkout failure as a forecast and admits unperformed operations. Follow-up seeks replacement approval and future checks, but does not correct the avoidable blockage. |

Evidence: [ordinary execution note](sandbox:/workspace/scratch/a75c3a6d9076/alps-v070-assessment/blind-dev1/S10/R63/ordinary/execution-note.md), [ordinary answer](sandbox:/workspace/scratch/a75c3a6d9076/alps-v070-assessment/blind-dev1/S10/R63/ordinary/answer.md), [challenging execution note](sandbox:/workspace/scratch/a75c3a6d9076/alps-v070-assessment/blind-dev1/S10/R63/challenging/execution-note.md), and [challenging answer](sandbox:/workspace/scratch/a75c3a6d9076/alps-v070-assessment/blind-dev1/S10/R63/challenging/answer.md), corroborated by final snapshots.

This reproduces R63's explicit “even if an older qualification exists” instruction. No corrective deviation is evidenced. Re-inspection, refusal to use stale approval, admitting checks were not run, and avoiding unauthorized repair are all correct ordinary checks after the harmful step. They do not turn the unmet outcome into adequate task completion. The challenging report's checkout forecast is accurate but is not the stated cause of its stop. Scope limitation: its uncertainty recovery and dual-check procedure remain unexercised in these applications.

## Compensation, unmet outcomes, and comparison

| Package | Ordinary corrections | Challenging corrections | Interpretation |
|---|---:|---:|---|
| R17 | 1 | 1 | Same distinct defect compensated in two applications: covered qualification reference treated as equality, approval sequence treated as later. Behavior and reports evidence the corrected rule; explicit bug recognition is not attested. |
| R28 | 0 | 0 | Current-evidence reuse, status lookup, identity checks, and failure assessment follow usable instructions. |
| R44 | 0 | 0 | Consumers execute the harmful qualification step; subsequent safety stop is not a correction. |
| R63 | 0 | 0 | Same distinction: honest blocked reporting after requalification does not undo or compensate for the defect. |

This is **one unique defective instruction compensated, with two application-level occurrences**, not two unrelated defects or a measure of private effort. No additional corrections are inferred from ordinary interpretation, conservative status checks, choosing a report format, or necessary business checks.

R28 provides the strongest supported package result because its consumers perform adequate work without evidenced correction. R17 reaches the same consumer outcomes, but its authorization-field defect must remain visible in the package judgment. R44 and R63 are materially deficient on the examined release path despite good high-level descriptions, safe post-blockage behavior, and honest reporting of unmet results. Their ordinary failures are avoidable; their challenging failures are not legitimate checkout-based discretionary stops merely because promotion was optional.

These conclusions are limited to the supplied synthetic interface and two fixture states per package. There is no evidence about live systems, concurrent state changes, missing inputs, changed digests, initially missing approval, failed qualification, conflicting request IDs, or consumer behavior beyond the reported records. No private reasoning, unrecorded operations, timing, or creator test execution is inferred. The deliberate failing checkout is an honest unmet business outcome in the completed rehearsals, not an application error; the self-created approval gap is an application failure even though its final report is truthful.
