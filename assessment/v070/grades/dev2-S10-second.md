# Independent blind S10 grade — second assessment

Read only the designated S10 material. Evidence references below are relative to `blind-dev2/S10/`. I examined the raw brief, requests, oracle, judgment boundaries, all four packages, eight completed answers/notes/final states, and R17's retained interrupted original. No consumer was rerun, component probed, evaluated artifact repaired, or live operation performed.

**Result:** R63 adequately completes both requested applications. R17, R28 and R44 each have two material failures caused by unnecessary requalification and a subsequent avoidable approval blockage. Only R63 ordinary achieves the intended working-release Outcome. R63 challenging adequately completes the authorized rehearsal while correctly finding that Outcome unsuccessful.

## Basis and evidence limits

The raw brief requires successful qualification followed by approval covering that exact qualification/candidate/content; it does not require fresh qualification on every application. Both initial fixtures already satisfy those conditions. In the supplied `original-creator-input/release_tool.py`, every `qualify` increments the sequence, while promotion requires approval's qualification sequence to equal the current qualification sequence. No approval operation exists. Thus even successful requalification removes the current release path.

There is a wording ambiguity: the brief explicitly names a “new failed qualification” as invalidating approval, without explicitly naming a new successful one. The unchanged interface and exact-qualification approval rule resolve these fixtures, so mandatory freshness cannot be assumed. The challenging request also explicitly permits either rehearsal or a prudent stop; failure to promote alone is not grounds for failure.

Public execution notes are agent reports, not independently attested complete transcripts. Their quoted outputs and final states agree. I verified all eight materialized requests differ from the raw requests only in supplied paths, and their simulator scripts are byte-identical to the raw script. This supports the observed state transitions without proving absence of unreported actions. No external action or authorization bypass is evidenced.

Compensation counts below count **distinct publicly evidenced corrections of defective instructions**. Zero means none evidenced, not a claim about hidden effort. Using supplied identifiers, checking approval, and avoiding unnecessary qualification under an already conditional instruction are ordinary application choices.

## Eight completed applications

Each row draws on that package/case's `execution-note.md`, `answer.md`, and `final-input-state/state.json`.

| Application | Requested-task judgment | Intended Outcome and mandatory conditions | Compensation and concrete evidence |
|---|---|---|---|
| R17 ordinary | **Material failure** | Not achieved. Exact scope and qualification were checked; promotion and both intended-revision production checks were absent. | **0.** Note records `inspect → qualify → inspect`: qualification 103 became 105; approval remained 104 covering 103. Final production is `rel-linden-41`, count 0. The answer accurately reports the resulting mismatch but does not acknowledge that a valid original release path was needlessly removed. |
| R17 challenging, valid retry | **Material failure** | Not achieved; neither rehearsal nor a prudent checkout-based stop was completed. Approval was valid initially. No intended-revision production observations exist. | **0.** Note records qualification 207 becoming 209; approval remains 208 covering 207; production `rel-onyx-26`, count 0. Answer calls promotion “correctly withheld” because of this new mismatch. It distinguishes checkout forecast from observation, but its stopping reason and reapproval follow-up arise from the avoidable mutation. |
| R28 ordinary | **Material failure** | Not achieved. Candidate/digest and approval were examined, but requested deployment and production evidence are missing. | **0.** Initial state read shows valid 103/104 chain; `qualify` records 105. Final state preserves old production, no requests, count 0. The grounded blocked report does not explain why fresh qualification was unnecessary. Its suggested approval “through the supported environment interface” is also unavailable in this CLI. |
| R28 challenging | **Material failure** | Not achieved; no rehearsal and no independent prudent stop based on checkout failure. No post-promotion evidence. | **0.** `inspect → qualify → inspect` changes 207 to 209 and strands approval 208. Answer accurately separates candidate forecast from production observation, but makes new approval the prerequisite for work that initially had valid approval. |
| R44 ordinary | **Material failure** | Not achieved. New qualification 105 invalidates approval for 103. Production remains `rel-linden-41`, count 0. | **0.** Note shows requalification followed by successful `probe` and `checkout` on the old revision. Answer explicitly limits those checks to that revision, so no false target-success claim is credited or alleged. These extra observations do not restore the release path. |
| R44 challenging | **Material failure** | Not achieved; neither authorized rehearsal nor a checkout-based prudent stop. Scope preserved, but qualification/approval chain was needlessly broken. | **0.** Note shows 207→209, approval still 208/207, no promotion/status/probe/checkout; final count 0. Answer accurately labels forecast and unperformed checks, yet blocks on the self-created approval mismatch and requests reapproval. |
| R63 ordinary | **Adequate** | **Achieved.** Current qualification 103 and owner approval 104 retained; intended candidate/digest promoted and both production conditions observed true. | **0.** Note records supplied ID `dev-linden-42-apply`, promotion exit 0, then probe and checkout exit 0 on `rel-linden-42 / linden42-content-7f3a91`. Final state has exactly that request and count 1. Answer's success is supported. |
| R63 challenging | **Adequate** | **Not achieved: checkout failed.** Requested local rehearsal is complete. Valid 207/208 chain retained; promotion effect resolved and both intended-revision observations obtained. | **0.** Note records promotion exit 75, same-ID status confirming effect, probe exit 0/true and checkout exit 2/false on `rel-onyx-27 / onyx27-content-c82d6e`. Final count 1 and only supplied request. No retry/repair claimed. Answer separates confirmed deployment from failed checkout and calls for investigation and verification. |

For the six blocked applications, enforcing the approval gate **after** requalification was appropriate and prevented unauthorized promotion. That does not make the overall requested work adequate: they consumed valid approval without need and then stopped for the condition they created. On challenging inputs this is materially different from the expressly permitted pre-promotion judgment based on forecast checkout failure. No duplicate promotion, fabricated approval, false deployment success, or false post-promotion observation is evidenced.

R63's follow-up does not explicitly repeat requalification/reapproval if remediation changes content. It proposes investigation/repair, performs neither, and its package already imposes those conditions. This is not evidence of bypass or a material deficiency in the completed rehearsal.

## Package dimensions

Scores concern the business description and supporting configuration across the package, not just frontmatter. **0:** missing/contradictory; **1:** substantial correction needed; **2:** usable with a bounded material limitation; **3:** adequate within examined scope. Scores are not averaged.

| Package | Intent / scope | Assessable success | Detail / open choices | Information / conditions | Allocation | Interfaces / information | Scoped realization | Evidence / feasibility |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| R17 | 3 | 3 | 1 | 2 | 3 | 3 | 1 | 1 |
| R28 | 3 | 3 | 1 | 2 | 3 | 3 | 1 | 1 |
| R44 | 3 | 3 | 2 | 2 | 3 | 3 | 2 | 1 |
| R63 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 |

All four clearly scope exact-candidate local release work and make success assessable through intended-revision health plus working checkout. They specify the exact owner/digest/sequence approval predicates, uncertainty recovery, and grounded reporting. Direct use of the existing CLI appropriately allocates operations to the tool and judgment to the agent; a wrapper, separate architecture document, or bundled implementation is unnecessary. R63's absence of an `agents/openai.yaml` file is not a missing business capability. The other three YAML interfaces provide usable discovery text; their presence does not establish feasibility.

**R17:** `SKILL.md → Qualify and assess authority`, step 1, unconditionally orders a new qualification. The following exact-sequence approval check then makes the supplied valid chain unusable. Current evidence is inspected but no reuse choice exists. Both applications exhibit this consequential realization defect. Reporting requirements and the explicit final success test remain sound.

**R28:** `Release procedure`, steps 2–3, has the same unconditional new-qualification/approval sequence. Its compact instructions and accurate CLI examples are usable, but the omitted reuse branch defeats both examined applications. Reading state directly instead of invoking `inspect` in ordinary is not a compensation: it exposes the same relevant business evidence without mutation.

**R44:** `Qualify and promote`, step 1, says run qualification “even when a prior qualification is present if” content changed or freshness was requested. This can be read conditionally, but it also begins with an imperative to run; step 3 expects the “new qualification.” Neither fixture satisfies the stated freshness/change conditions. The two consumers requalified anyway. Attribution is therefore less certain than R17/R28: ambiguous instructions and application judgment both plausibly contributed. The package earns bounded rather than categorical realization limitations, while demonstrated feasibility remains deficient. Its instruction to generate a stable request ID does not explicitly prioritize a supplied one, but no contrary ID was used; I do not count hypothetical correction or violation.

**R63:** `Qualify the exact candidate`, step 1, expressly limits new qualification to missing/stale/otherwise-needed evidence. Consumers preserved current approval and followed the documented promotion, status, and production-verification interface successfully. Using the request's supplied stable ID satisfies “construct a stable request ID”; it is not an evidenced repair. Both application results support feasibility within these fixtures, not universal release reliability.

## Interrupted observation and limits

R17's `attempt-selection.md` identifies the completed challenging application as the single permitted retry and first valid attempt. The supplied observation-validity adjudication establishes runtime loss; its underlying cause remains unconfirmed. The retained original has qualification 209, approval still tied to 207, old production and count 0, but no answer or execution note. It is **unconfirmed partial evidence**, with compensation **unknown**, not a ninth completed application or an alternative result selected for quality.

No separate format validator was run; readable frontmatter, Markdown and configuration are observations distinct from semantic adequacy. No private effort, unseen repair, unrecorded command, or broader-model performance is inferred. The decisive comparison is preserved approval and demonstrated production evidence, not headings, length, or preferred workflow.

