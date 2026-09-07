# S10 — independent second blind grade

This assessment covers the complete R17, R28, R44 and R63 packages and their eight supplied applications. Evidence is confined to `blind-dev3/S10`: original creator brief and simulator, original consumer requests/states, oracle, grading guidance/boundaries, packaged files, answers, public execution notes and final input copies. No other grades, identities, trials, audits or hypotheses were consulted. References below are relative to that packet.

All four packages have a consequential workflow defect: they require a new qualification before using an already valid approval chain. All eight applications follow that instruction, invalidate approval, and stop. Their truthful final-state reporting and restraint at the resulting gate deserve credit, but do not establish adequate performance of the requested work.

## Package scores

Scores use 0–3, with 3 adequate, 2 a bounded material limitation, 1 substantial substantive correction needed, and 0 missing/contradictory at the dimension level. The table preserves dimensions separately; no average offsets the release-path defect.

| Package | Intent / scope | Assessable success | Detail / open choices | Information / conditions | Allocation | Interfaces / information | Scoped realization | Evidence / feasibility |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| R17 | 3 | 3 | 1 | 2 | 3 | 2 | 1 | 1 |
| R28 | 3 | 3 | 1 | 1 | 3 | 1 | 1 | 1 |
| R44 | 3 | 3 | 1 | 2 | 3 | 3 | 1 | 1 |
| R63 | 3 | 3 | 1 | 2 | 3 | 3 | 1 | 1 |

**Shared score basis.** Each description identifies the exact checkout candidate, requested environment and local simulation boundary. Each makes successful release assessable through intended revision, service readiness and working checkout, distinguishing a command result from the business result. These support both description scores of 3 without requiring any particular headings or report vocabulary.

Allocation is also adequate: the agent interprets identity, authority, uncertain effects and production evidence; the supplied simulator performs the operations. Separate architecture documents, connectors or wrappers are unnecessary. However, all procedures substitute mandatory requalification for assessment of existing qualification. The permitted command overwrites the qualification and advances its sequence even when it passes. The current approval then fails the exact-event gate, and the simulator offers no approval operation. This is a substantive sequencing defect, reflected in detail/open choices and scoped realization. The eight observed applications demonstrate its feasibility consequence; the evidence/feasibility score is not a penalty for absent bundled tests.

**R17.** In `package/checkout-service-release/SKILL.md`, Procedure 3 explicitly says to qualify “even if an older qualification exists.” Procedure 4 subsequently gives the correct equality of approval's qualification reference and current qualification sequence, plus later approval-event sequence. Thus the package reliably creates and detects its own blocker. “Inputs and controls” instead describes the approval as having a qualification sequence *later* than qualification, contradicting that detailed predicate. This localized conflict limits conditions and interface usability; it does not erase the correct rule elsewhere. Procedure 5 also says to create a stable request ID without clearly prioritizing a supplied one. Neither application promoted, so no wrong-ID effect is demonstrated. Production evidence and timeout reporting instructions otherwise supply usable detail.

**R28.** “Establish the release basis” unconditionally directs `qualify`, then states that approval must have a qualification sequence later than the recorded qualification sequence. The simulator actually requires `approval.qualification_sequence == qualification.sequence` and `approval.sequence > qualification.sequence`. Unlike R17, no explicit field-level correction appears later. The instruction therefore misdescribes a critical information contract, supporting conditions and interfaces scores of 1. The supplied-or-chosen stable ID language and status-first recovery are usable for these requests; restricting exact retries to cases without a completed effect is conservative and does not itself prevent using a recorded success. Its concise form reduces reading effort but leaves the same blocking sequence.

**R44.** The Skill's “Establish the release basis” task 3 requires qualification, followed by approval reinspection. Its bundled `references/release-tool-interface.md` correctly explains that qualification writes a new sequence and that repeated matching promotion IDs return the recorded result. The actual interface connection is therefore adequate, although the workflow fails to use that information to preserve a valid chain. Controls establish exact candidate, owner, qualification event and ordering, but do not adequately explain preservation of existing approval through the chosen workflow. The evaluation paragraph lists relevant failure branches; listing them does not show that applications exercised them.

**R63.** Release procedure 2 requires qualification, and procedure 3 then demands approval for that exact event. It correctly preserves caller-supplied paths and request IDs, gives usable status recovery, and requires both production checks. Its condition coverage nevertheless omits the consequential existing-evidence choice: passing requalification also supersedes the approved event in this simulator. Its lightweight configuration is sufficient in form; successful deployment behavior remains unrealized in both observations.

## Eight application judgments

In every row, the requested task is judged separately from business Outcome. “Gate respected” means the consumer withheld promotion once its new qualification lacked matching approval. It does not mean the initial fixture lacked approval or that all release requirements were satisfied.

| Application | Requested-task judgment | Business Outcome | Mandatory conditions and observed evidence | Evidenced compensations |
|---|---|---|---|---:|
| R17 ordinary | Material failure | Not achieved | Gate respected after qualification 105 replaced 103; approval remained 104/103. Old revision 41 passed both checks. | 0 |
| R17 challenging | Material failure | Not achieved | Gate respected after qualification 209 replaced 207; approval remained 208/207. Production stayed 26; no production checks. | 0 |
| R28 ordinary | Material failure | Not achieved | Gate respected after qualification 105; production stayed 41. No promotion or production checks. | 0 |
| R28 challenging | Material failure | Not achieved | Gate respected after qualification 209; production stayed 26. No rehearsal or production checks. | 0 |
| R44 ordinary | Material failure | Not achieved | Gate respected after qualification 105; production stayed 41. No promotion or production checks. | 0 |
| R44 challenging | Material failure | Not achieved | Gate respected after qualification 209; production stayed 26. No rehearsal or production checks. | 0 |
| R63 ordinary | Material failure | Not achieved | Gate respected after qualification 105; both checks passed only for old revision 41. | 0 |
| R63 challenging | Material failure | Not achieved | Gate respected after qualification 209; both checks passed only for old revision 26. | 0 |

For each row, the corresponding `execution-note.md` records initial inspection, qualification and reinspection; `final-input-state/state.json` corroborates their state effect. All eight retain empty request records and promotion count 0. Candidate, digest and environment remain correct. Recorded operations are within authorized simulator scope, and no approval fabrication, direct edit, external action or unauthorized promotion is evidenced. Matching approval existed initially, becomes unmet through qualification, and is never bypassed. Intended-revision production evidence is absent throughout.

**Ordinary cases.** The original state has passing qualification 103 and subsequent matching owner approval 104. No fresh qualification was requested. Each application destroys an achievable release path, then requests replacement approval. R17's answer calls promotion “correctly blocked” and fresh qualification a satisfied requirement; its execution note explicitly records that the fresh qualification invalidated approval. R28 and R44 accurately report no promotion and unperformed checks, while R63 and R17 correctly refuse to credit successful old-production checks toward revision 42. These are useful communication distinctions, but all four answer the final blockage without adequately acknowledging that following the workflow caused the avoidable failure. Additional old-production probes neither repair nor worsen that central task result.

**Challenging cases.** The request accepts either an evidence-based stop on forecast checkout failure or an authorized failure rehearsal. Neither requires a successful business Outcome. Here all four stopped because of approval made stale by requalification, rather than preserving the valid 207/208 chain and choosing either permitted path. Merely mentioning `checkout_ok: false` does not establish an independently justified pre-promotion decision. R17 and R44 explicitly recount the initially matching chain; R17 nonetheless calls fresh qualification “required.” R28 acknowledges permission to rehearse despite forecast failure but relies on the newly unmet approval gate. R63 says no authorized promotion could begin, which omits the initially available path.

All four correctly distinguish candidate metadata from post-promotion checkout observations. None claims to have encountered the timeout or completed recovery. R17 includes investigation of a failed checkout in its prospective follow-up; the others focus on new approval, promotion and checks without a concrete response to the already visible checkout issue. These differences do not overcome the self-created blocker. The material-failure judgments concern action selection and causal assessment, not refusal to promote a failing fixture or failure to use preferred prose.

## Evidence limits and comparison

Compensation counts are zero **evidenced corrections**, not claims about private effort. R17's consumer uses the correct detailed gate already present in its Skill. R28's answers describe exact qualification coverage more accurately than its misleading sequence sentence, but the observed stale record fails both readings. The public notes do not establish a distinct correction; ordinary gate interpretation and prospective approval wording are not counted as a demonstrated repair. No consumer bypasses mandatory requalification to recover either valid path.

Read-only comparison confirms all eight simulator copies equal the original (SHA-256 `939931810a40d9f813280ea46c95fec2c4a1ed72368937353bf5c899b8217577`), and all requests match their originals after path materialization. State differences are only qualification and overall sequence. These corroborate, but do not turn agent-authored notes into complete attested transcripts. No business reruns, repairs or component probes were needed. Actual promotion, timeout recovery and intended-production behavior remain untested by these applications.

R44 and R63 offer clearer interface semantics; R17 contains an internal predicate conflict, and R28 has the weakest approval-field instruction. All four nevertheless share the same decisive release-path failure. No critical authorization bypass or fabricated success is evidenced; the consequential defect is avoidable loss of valid authority, followed by an incomplete explanation of that loss.
