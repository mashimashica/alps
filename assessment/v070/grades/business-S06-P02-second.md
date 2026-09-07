# Independent business assessment: S06-P02, second review

All four ordinary applications delivered the correct complete reimbursement rollup. All four challenging applications made the authorized progress and left adequate, inspectable continuation evidence; their full business result remains incomplete. Those application outcomes do not establish that every package fulfills its wider advertised scope. R44 has a confirmed defect for sources exhausted on their first page. R17 has weaker recovery behavior and documentation, including an unhandled lost-response error. Neither defect was encountered in the eight recorded applications.

## Scope, evidence, and scoring

This review used only the assigned packet at `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/blind-business/S06-P02`, beginning with `judgment-boundaries.md` and `grading-guidance.md`, then the original creator brief/API/fixture, both original consumer requests/fixtures, and `business-oracle.md`. For each candidate I read the package, creator-reported checks, and both applications' prompts, answers, execution notes, setup/resource observations, and work evidence. I compared the observed-final Skill and final inputs with their originals and reviewed the preserved initial/final native SQL and metadata. I did not consult other grades, mappings, plans, original trial directories, or live source states. The optional authoring aid was not needed. No evaluated artifact was repaired.

Scores use the supplied 0–3 scale: 0 missing/contradictory; 1 substantial corrective work needed; 2 usable with a bounded material limitation; 3 adequate within the examined scope. Description scores concern what the Skill communicates. Supporting-system scores concern the allocation of work, interfaces, implementation, and evidence. Correctly stating a business requirement does not prove that the helper implements it. No numerical average is used.

Description dimensions are intent/scope (I), assessable success (S), adequate detail/open choices (D), and information/conditions (C). Supporting dimensions are allocation (A), interfaces/information (I), scoped realization (R), and evidence/feasibility (E). The simple CLI-plus-checkpoint architecture is appropriate for all four candidates; no separate architecture document or additional service is necessary.

| Package | Description I | S | D | C | Support A | I | R | E |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| R17 | 3 | 2 | 2 | 1 | 3 | 2 | 2 | 2 |
| R28 | 3 | 3 | 3 | 2 | 3 | 2 | 3 | 3 |
| R44 | 3 | 3 | 3 | 3 | 3 | 2 | 2 | 2 |
| R63 | 3 | 3 | 3 | 3 | 3 | 2 | 3 | 3 |

A read-only review script and its derived findings are retained at:

- `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/grading-work/S06-P02-second/review_recorded_evidence.py`
- `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/grading-work/S06-P02-second/recorded-evidence-review.json`

The script was run with `python3.12 /workspace/scratch/a75c3a6d9076/alps-v070-assessment/grading-work/S06-P02-second/review_recorded_evidence.py`, exit 0. It invoked no source API. All eight checkpoints' aggregates matched the applicable original fixture or authorized prefix. All eight API files, substituted requests, and observed-final package bytes/modes matched their respective originals. Each preserved SQL hash matched its metadata, and the source records matched the corresponding original fixture.

## Business conditions and recorded state

For the ordinary interval, `2026-04-03` through `2026-04-09`, snapshot `snap_c22e71aa06b43ab25395e0ce`, the complete expected rows are:

| Vendor | Charge cents | Credit cents | Net cents | Qualifying count |
|---|---:|---:|---:|---:|
| apricot | 1234 | 1234 | 0 | 2 |
| juniper | 2501 | 0 | 2501 | 1 |
| willow | 0 | 407 | -407 | 1 |

For the challenging interval, `2026-06-10` through `2026-06-18`, snapshot `snap_fb322d1120ca406ad668bc26`, only the first two pages are authorized. Their four qualifying entries among six examined source records produce:

| Vendor | Charge cents | Credit cents | Net cents | Qualifying count |
|---|---:|---:|---:|---:|
| azure | 5000 | 0 | 5000 | 1 |
| glacier | 700 | 700 | 0 | 2 |
| saffron | 0 | 900 | -900 | 1 |

Every ordinary checkpoint records terminal null cursor and the correct complete aggregates. Every challenging checkpoint records the exact next unprocessed cursor `p_b62d3333e930f1830dd2d61eb80d3bbc` and the correct prefix aggregates. The ordinary case's six records and challenging case's fifteen records are not qualifying counts.

All eight setups preserve an initial tranche 1 with two calls available. The only initial-to-final SQL difference is `source_state.calls_used` changing from 0 to 2; tranche remains 1, snapshot and records remain unchanged. All eight resource observations report no changed originals or added resources. This supports two successful calls within the initial tranche and no recorded source-content change. It does **not** independently attest every operation, rule out temporary edits, or prove that no forbidden read occurred. Execution notes are preserved agent reports, not complete trusted nested-call traces. No prohibited traversal or permission bypass is evidenced.

The application scores below assess requested-task adequacy at the applicable authorization boundary (T), appropriate actions (A), mandatory output/continuation conditions (M), and grounded user-facing communication (G). A challenging T=3 means an adequate authorized pause, not achievement of the complete reimbursement result.

| Application | T | A | M | G | Full business result | Counted corrective compensations |
|---|---:|---:|---:|---:|---|---:|
| R17 ordinary | 3 | 3 | 3 | 3 | Achieved | 0 |
| R17 challenging | 3 | 3 | 3 | 3 | Incomplete; adequate authorized pause | 0 |
| R28 ordinary | 3 | 3 | 3 | 3 | Achieved | 0 |
| R28 challenging | 3 | 3 | 3 | 3 | Incomplete; adequate authorized pause | 0 |
| R44 ordinary | 3 | 3 | 3 | 3 | Achieved | 0 |
| R44 challenging | 3 | 3 | 3 | 3 | Incomplete; adequate authorized pause | 0 |
| R63 ordinary | 3 | 3 | 3 | 3 | Achieved | 0 |
| R63 challenging | 3 | 3 | 3 | 3 | Incomplete; adequate authorized pause | 0 |

The R44 challenging execution note contains a material reporting inaccuracy about a failed third page attempt, discussed below. Its user-facing answer correctly states two **successful** page calls and does not repeat that inaccurate claim. Consequently, this defect is kept separate from the answer-grounding score and from the successful-call authorization judgment.

## R17

### Package judgment

`R17/package/reimbursement-ledger-rollup/SKILL.md` states the right goal, inclusive settled-entry filter, integer amounts, retention of zero/negative nets, two-call invocation limit, and operator ownership of further tranches. The one command identifies all required arguments. The brevity itself is not a defect.

Success and detail score 2 because the instructions leave important output and continuation semantics to code inspection: they do not explicitly give the null-cursor completion criterion, describe the checkpoint's actual contents, or explain how to report an incomplete aggregation. Information/conditions scores 1 because lost responses and interrupted persistence are within the brief, but the Skill supplies no actionable treatment of them. Its creator note says that the source API's lost-response recovery limitation is documented in the Skill; that claim is unsupported by the supplied eight-line file.

The helper correctly reuses `describe` and `page`, filters every fetched record, sums integer cents, and sorts vendor rows. `seen_cursors` and the next cursor define an adequate normal incorporated-page frontier. It can traverse the challenging fixture over three approved tranches and retains the zero-amount quartz entry on eventual completion. These facts support a usable implementation, despite the following limitations:

| Component finding | Evidence and consequence | Status |
|---|---|---|
| Lost first response causes an unhandled exception | `rollup.py` returns an `invalid_api_response` body for non-JSON stdout while preserving exit 0, then accesses `b['next_cursor']`. The disposable loss probe exited 1 with `KeyError: 'next_cursor'`, empty stdout, one call consumed, and no checkpoint. | Confirmed component defect; not encountered by either consumer. |
| Checkpoint writes are not atomic | The script calls `json.dump(state, open(checkpoint, 'w'))` directly. An interruption during replacement can leave a truncated checkpoint; unlike the other packages, there is no previous atomic version guaranteed by the implementation. | Static persistence risk; no write-interruption fault was injected and no actual lost checkpoint is claimed. |
| Source binding relies on retained invocation context | The checkpoint binds snapshot/start/end, not state/API location or observed quota. A disposable continuation accepted a different state with the same snapshot and advanced the checkpoint. | Confirmed missing guard/self-contained binding, not evidence that a documented same-arguments continuation fails or that the original consumer bypassed quota. |
| Completed checkpoints are not recognized before paging | Re-running a completed disposable request fetched the first page again, consumed the last available call, then returned `repeated_cursor`, exit 2. Totals were not doubled. | Confirmed usability/continuation limitation; completed-request rerun is distinct from the observed ordinary application. |

The support interface score is 2 because the checkpoint is usable when retained with its invocation and answer, but cannot alone identify the exact quota-bearing source or observed tranche conditions. Realization scores 2 rather than 3 because lost-response reporting and persistence fall short of the safe-continuation claim. Evidence scores 2: the creator reports only help and one two-page pause, while its claim of documented loss handling is unsupported. The recorded applications and new continuation probe establish substantial normal-path feasibility, not general crash safety.

### Applications

| Case | Evidence and judgment |
|---|---|
| Ordinary | `ordinary/execution-note.md` records one helper invocation, exit 0, with the three correct rows. `work-evidence/checkpoint.json` has the initial cursor and `p_de1636bae17d3ae33cda4377d6e42ee3` in `seen_cursors`, current cursor null, and correct totals. A post-run describe reports tranche 1, remaining 0, total 6. `answer.md` identifies source, snapshot, interval, complete coverage, and exact sorted amounts. Complete business result achieved. |
| Challenging | The helper exits 75 with `paused`; `work-evidence/reimbursement-rollup-checkpoint.json` contains two incorporated page cursors, the exact next cursor, interval, snapshot, and prefix totals. `answer.md` gives the exact source path, full checkpoint contents, observed tranche/quota, six source versus four qualifying records, and the correct provisional rows. It explicitly waits for later operator approval. The answer plus checkpoint forms a usable bound continuation record, although the checkpoint alone lacks the source location. Full business result remains incomplete. |

The challenging answer says no incorporation uncertainty was observed. That is consistent with the helper's successful return and persisted frontier on this clean case; it is not proof of general atomicity. Individual entry IDs are absent, but the oracle permits an unambiguous incorporated-page frontier plus aggregates. I do not impose an entry-ID schema.

Consumer mitigation is visible: the final response supplies source binding and quota information missing from the helper's checkpoint. Under the required narrow counting rule this is ordinary response/evidence assembly, not a demonstrated correction to an erroneous instruction. Neither application encountered a failed helper run, repaired the package, changed the algorithm, or corrected the amounts. Counted corrections: 0 and 0.

## R28

### Package judgment

`R28/package/reimbursement-ledger-rollup/SKILL.md` communicates the business goal, appropriate trigger, exact runner command, dedicated request checkpoint, full-versus-incomplete output, null-cursor completion, operator-approved continuation, and preserved source/request identity clearly. Its warning against presenting partial progress as the answer is reasonably read as a ban on false finality, not a prohibition on the user's expressly permitted saved fetched-record evidence.

The helper binds API path, source path, snapshot, total count and dates; stores canonical records and aggregates atomically; validates dates and records; and uses the descriptor's remaining quota. It checks full record coverage after observing null cursor. Complete reruns return the saved result without another page. The ordinary and challenging cases and disposable completion/empty probes support its arithmetic and normal continuation, including zero and negative nets and the zero-amount vendor.

Information/conditions and supporting interfaces score 2 for a bounded recovery/evidence limitation. The Skill tells the user to rerun after a lost response but does not explicitly explain that the missing response may already have consumed a call. On the disposable lost-first-response probe, the helper correctly returned an error rather than claiming success, but emitted only `{"error":"API returned non-JSON output (exit 0)","status":"error"}` and had not created a checkpoint. That output does not itself preserve the source/request binding or consumed-call uncertainty. Normal checkpoints also omit observed tranche/remaining quota, so a complete boundary report requires another describe observation.

This is not evidence of broken retry arithmetic: rerunning the identical command in the disposable loss case re-described the source, used the remaining one successful call, incorporated the first page once, and paused correctly. Retained command context supplies the initial binding. Therefore scoped realization remains 3 within the tested contract; the deficiency is in self-contained error evidence and explanation. The creator reported multi-tranche completion and invalid-interval checks, and explicitly did not claim exhaustive fault injection. Together with the preserved applications and independent probes, feasibility scores 3.

### Applications

| Case | Evidence and judgment |
|---|---|
| Ordinary | `ordinary/execution-note.md` captures exit 0 with the correct vendor rows and six examined records. `work-evidence/reimbursement-2026-04-03-through-2026-04-09.checkpoint.json` binds the exact API/state/dates/snapshot, contains all six canonical entries, and records `exhausted: true`, `next_cursor: null`. The answer reports complete coverage, exact sorted cents, and post-run tranche 1/remaining 0. Complete business result achieved. |
| Challenging | The helper exits 75, reports six examined records, and preserves all six canonical records, correct aggregates, exact state/API/date/snapshot binding, `exhausted: false`, and the correct next cursor. The answer and `work-evidence/continuation-evidence.json` add observed tranche 1/remaining 0 and an explicit same-checkpoint resume rule after separate approval. The saved record set is sufficient to recover the permitted partial rollup even though no table is displayed. Full business result remains incomplete. |

The challenging consumer calculated the historical second-page request cursor from the supplied API's cursor function. Its execution note and continuation artifact explicitly label this value as **derived**, while the next unprocessed cursor is observed in the checkpoint. That calculation was not used to fetch entries; no prohibited alternate traversal is shown. It adds no independent raw page-response evidence, and was unnecessary for safe continuation. Lack of per-record page grouping is not a business failure: the incorporated set, aggregate, and unambiguous frontier suffice under the oracle.

Neither application corrects a failed workflow or changes its instructions. The extra describe call, decoded fetched records, and separate evidence file are permitted evidence assembly. Counted corrections: 0 and 0.

## R44

### Package judgment

`R44/package/reimbursement-ledger-rollup/SKILL.md` adequately describes the intended task, input contract, completion criterion, provisional rows, exit statuses, lost-response recovery, operator-only tranche control, and empty-result condition. The description dimensions score 3 because these business instructions are clear and correct as requirements. The implementation's failure to realize one requirement is scored separately.

The helper pins state/snapshot/interval/count, stores aggregates and seen entry IDs atomically, verifies returned records, follows the next cursor, and returns sorted exact-cent rows. It reports useful provisional results and a checkpoint path. A successful response with unusable JSON yields `recovery_required` while preserving an initial checkpoint; the disposable loss probe confirms that behavior and a subsequent billable retry's safe progress.

The significant defect is in `add_page`: it rejects `next_cursor == current_cursor` without exempting a terminal null cursor on the first request. Both values are legitimately null for any source exhausted on its first page. The disposable empty and singleton sources each consumed one successful call and then returned exit 2, `{"error":"page next_cursor did not advance","status":"error"}`. No entry from the valid singleton page was incorporated. The checkpoint still described an unstarted request. Thus the explicit empty-source business requirement fails, and inspection shows the same condition applies to valid two- and three-record sources. This is a self-created block, not appropriate handling of an unavailable or invalid source. It must not be obscured by the two successful consumer cases.

Supporting realization and evidence score 2. Multi-page rollups and continuation are feasible and independently demonstrated, but first-page completion is broken. The creator honestly states that it did not construct an empty source; its assertion that the unexercised path is implemented is not successful verification. Supporting interfaces score 2 because quota/tranche observations need supplemental evidence and the runner uses a failed next-page call to discover exhausted quota, rather than stopping immediately after the two successful calls. The supplied API enforces the success limit, so this extra failed call is not an authorization breach.

### Applications

| Case | Evidence and judgment |
|---|---|
| Ordinary | The captured helper output is exit 0, `complete`, `final: true`, two fetched pages, six observed records and all three correct rows. `work-evidence/rollup.json` binds source/snapshot/dates, lists `ord-001` through `ord-006`, and records a terminal null cursor. The answer supplies the interval/snapshot and correct complete table. Complete business result achieved; the first-page-terminal defect does not apply to this two-page source. |
| Challenging | The helper reports exit 75, `incomplete`, `final: false`, two fetched pages, correct provisional rows and the exact next cursor. `work-evidence/rollup-checkpoint.json` binds the source/request and preserves `chg-001` through `chg-006` plus aggregates. A separate describe captures tranche 1/remaining 0. The answer gives that evidence, distinguishes four qualifying from six examined entries, and waits for new approval. Full business result remains incomplete, with usable continuation. |

The challenging execution note's statement “No third page call was attempted” is inconsistent with the delivered runner and its reported output. The runner loops until terminal cursor or an API error; its `call_budget_exhausted` output with `pages_fetched_this_run: 2` is reached after another page attempt returns 75. The unchanged package and captured status therefore support a failed third attempt, and the disposable public-call observer confirms the same code path as exits 0, 0, 75. There is no original nested-call attestation, so that confirmation must not be described as a new observation of the original source. It does establish why the consumer's blanket no-attempt claim is not credible. The oracle expressly permits this failed attempt; it returned no entries and was not a third successful call.

No consumer encountered or compensated for the empty/singleton defect. Post-run describe and evidence formatting are ordinary requested work. Counted corrections: 0 and 0.

## R63

### Package judgment

`R63/package/reimbursement-ledger-rollup/SKILL.md` gives a clear command, dedicated progress-state rule, null-cursor completion condition, exact settled/inclusive aggregation rules, preservation of zero/negative vendors, and explicit operator ownership of further tranches. It distinguishes tranche-boundary and source-budget exhaustion and explicitly warns that retrying after a lost response consumes another call. The explanation is useful detail rather than unnecessary structure.

The helper uses a fixed two-page limit and the supplied API, validates dates before source access, pins state/snapshot/interval/count, and atomically stores entry fingerprints, aggregates, cursor, completion, and recovery status. It creates the initial progress record before fetching. In the disposable lost-first-response case it returned exit 74 with `recovery_required: true`, source/snapshot/request context and a saved initial frontier; a billable retry incorporated the first page once. Complete reruns consume no page calls, and an empty source completes with an empty result. Multi-tranche validation reached the correct five-vendor result including quartz's zero amount/count one. No material arithmetic or traversal defect was demonstrated within the specified immutable, valid-record contract.

Supporting interfaces score 2 because the saved progress record does not preserve observed tranche/remaining quota, although stdout reports a tranche and the missing boundary observation is straightforward to obtain via describe. That observation was supplied in both applications. Supporting realization and evidence score 3 within the examined scope. The creator reported multi-tranche, no-qualifying-result, invalid-interval and completed-rerun checks and clearly listed untested fault classes. This is not a claim of exhaustive crash/concurrency safety. A separate source-total reconciliation check is not mandatory when null-cursor traversal operates against the guaranteed clean API.

The optional initialization sentence in the Skill applies to an explicitly fresh simulator setup, and the Skill otherwise asks for an existing source. Both actual requests expressly supplied initialized states and prohibited initialization. Neither application invoked init; no consumer authorization failure should be inferred from the presence of that setup guidance.

### Applications

| Case | Evidence and judgment |
|---|---|
| Ordinary | In addition to the execution note, `work-evidence/rollup.stdout`, `rollup.stderr`, `rollup.exit-code`, and corresponding describe files preserve the helper's complete output and post-run metadata. The output contains the correct rows, interval/snapshot and two applied pages. `rollup-progress.json` has all six canonical records, exact source binding, terminal null cursor, `complete: true`, and no recovery flag. The answer's cents and dollar representations agree exactly. Complete business result achieved. |
| Challenging | The helper exits 75 with `tranche_boundary`, two applied pages, the exact next cursor and `recovery_required: false`. `work-evidence/rollup-progress.json` binds the exact state/request and contains all six canonical records plus correct aggregates. The answer displays the correct provisional table and gives observed tranche 1/remaining 0, incorporated records, checkpoint location and conditional resume instructions. Full business result remains incomplete. |

The challenging answer loosely says the progress evidence identifies the observed post-run quota, while the JSON itself does not contain those quota fields. The observation is actually preserved in the answer and exact describe result in the execution note. Taken together, the continuation record meets the request; treating the JSON alone as the entire evidence bundle would miss that distinction. This is a minor attribution imprecision, not lost continuation state or false finality.

Neither application repairs instructions or implementation, corrects a failed result, or needs an alternate aggregation. Counted corrections: 0 and 0.

## Independent component probes and exact evidence

All component executions ran only on explicitly labeled disposable copies under:

`/workspace/scratch/a75c3a6d9076/alps-v070-assessment/grading-work/S06-P02-second/disposable-probes`

The executed entry command was:

```sh
python3.12 /workspace/scratch/a75c3a6d9076/alps-v070-assessment/grading-work/S06-P02-second/disposable-probes/probe_components.py
```

It exited 0. The harness copied package files byte-for-byte, copied the supplied API unchanged, and initialized separate new state files. Observer wrappers retained every underlying public API command/response. For loss probes only, the wrapper withheld the first successful page's stdout after the copied API committed the call. The runner did not receive that withheld response. Synthetic empty and singleton fixtures were created only in this disposable directory. The changed-state probe intentionally changed a runner argument; it is a binding/guard check, not a normal same-arguments continuation test.

Exact per-command argv, shell-rendered command, working directory, return code, stdout and stderr, plus checkpoint snapshots and underlying API responses, are retained in `disposable-probes/results.json`, each candidate/case's `results.json`, and each case's `public-api-calls.jsonl`. The harness itself records how each case was constructed. These are independent grader probes, not original consumer executions or creator-reported tests.

| Probe | R17 | R28 | R44 | R63 |
|---|---|---|---|---|
| Fifteen-record ledger across three validation-approved tranches | 75, 75, 0; correct full rows | 75, 75, 0; correct full rows | 75, 75, 0; correct full rows | 75, 75, 0; correct full rows |
| Completed checkpoint rerun | Extra successful initial-page fetch; exit 2 `repeated_cursor` | Exit 0; no page fetch | Exit 0; no page fetch | Exit 0; no page fetch |
| Empty source | Exit 0; empty complete result | Exit 0; empty complete result | Exit 2, false cursor error | Exit 0; empty complete result |
| Lost first successful page response | Exit 1 traceback; no checkpoint | Exit 2 structured error; no checkpoint | Exit 75 recovery-required; initial checkpoint retained | Exit 74 recovery-required; initial checkpoint retained |
| Same-command retry after lost response, using the one remaining successful call | Correct first-page progress, then pause | Correct first-page progress, then pause | Correct first-page progress, then pause | Correct first-page progress, then pause |

The R44 singleton probe also produced the false cursor error. The R17 changed-state probe accepted the checkpoint on a second separately initialized state sharing the snapshot. Validation-only grants in the three-tranche probes were explicit harness operations. No grant occurred on, or was inferred for, any original consumer source. Full results from the disposable probes demonstrate component feasibility only; they do not complete the original challenging requests.

## Compensation counts, alternatives, and limits

The eight counted compensation values are all zero under the stipulated rule: count distinct evidenced corrections to erroneous or unusable instructions. No recorded application corrected a helper failure, changed the Skill, substituted an implementation, or repaired wrong aggregation. Additional describe calls, reading checkpoints, copying known source paths into an answer, and choosing a separate evidence file are normal required business work. They visibly mitigate packaging omissions, especially R17's checkpoint-only binding, but are not automatically eight or more instruction corrections. The unobserved recovery defects must not be assigned hypothetical consumer compensation counts.

Several business judgments warrant explicit qualification:

- The challenging applications are adequate for the approved tranche but do not achieve the requested full-ledger outcome. A report that calls all eight “complete successes” without this distinction would be wrong.
- An aggregate checkpoint with a clear incorporated-page frontier can be valid. Raw response journals, per-page record groupings, entry fingerprints, a particular filename, and ALPS headings are not mandatory. R17's answer plus checkpoint and R28's saved record set satisfy the oracle's accepted alternatives.
- R17's absent state-path guard is reasonably scored as a bounded interface weakness because the Skill tells the user to reuse the same arguments and the consumer retains that binding externally. A stricter package-isolation score could lower its interface dimension, but the changed-argument probe is not grounds to fail its actual same-state applications.
- R28's first-loss behavior admits a slightly different dimension allocation: its retained invocation and quota-aware rerun do recover safely in the probe, so the generic error/no-initial-checkpoint issue can be treated solely as an information limitation. This review does that rather than alleging broken arithmetic or double counting.
- R44's false no-third-attempt statement can justify a lower score for execution-note reliability. It does not justify a successful-call authorization failure or a failure of the correct user-facing provisional result.
- A missing tranche/remaining field in a checkpoint is not itself a failed application when the requested evidence is supplied in a retained answer or execution note. Standalone helper-interface scores remain bounded because that extra context is needed.

No full consumer call trace is supplied, and a final SQL state does not prove source-entry acquisition history by itself. The available commands, unchanged implementations, checkpoint contents and native states consistently support the eight operational outcomes, subject to that provenance limit. No response-loss fault was injected into those original applications. Concurrent writers, persistence interruption, malformed source records and all subprocess-failure boundaries were not comprehensively tested here. The static R17 write-risk observation is therefore a risk analysis, not a claimed observed crash-loss result. Invalid-interval behavior was read in each helper and appears before page traversal, but was not independently rerun in this review; relevant creator claims remain reported checks.

The strongest distinction in this packet is between equal adequacy on the supplied clean applications and unequal package coverage of the broader brief. R28 and R63 have the strongest demonstrated normal continuation behavior; R63 additionally preserves and reports initial lost-response recovery state. R44's first-page-terminal defect is consequential despite correct two-page and longer results. R17 handles the clean business arithmetic but leaves the most recovery interpretation and external context to the user. No experimental identity is inferred from these differences.
