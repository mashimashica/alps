# FP03 — independent focused assessment

All four packages are adequate within the supplied ledger contract. All four ordinary applications support a correct complete rollup; all four challenging applications support an adequate, resumable first-tranche pause while the full business Outcome remains unmet. No material generated-Skill defect or compensating correction is established by this packet. These judgments use the implementations, answers, execution records and checkpoint/state evidence, not completion notices or formatting.

References below are relative to `blind-focused/FP03/`; abbreviated secondary paths in a table row are within that row's package or application folder. I read the original creator brief/API/fixture, both original consumer requests/fixtures, boundaries, oracle, grading guidance, all four packages, all eight application records, creator-reported checks, available handoffs, recovery provenance, and state/work evidence. Embedded original paths were treated only as identity data.

## Package assessment

Scores use the supplied anchors: **0** missing/contradictory; **1** substantial correction required; **2** usable with a bounded material limitation; **3** adequate within examined scope. Description order is **intent/scope; assessable success; needed detail/open choices; information/conditions**. Configuration order is **allocation; interfaces/information; scoped realization; evidence/feasibility**. Configuration applies to all four because each supplies an executable supporting system; no separate architecture document is required.

| Package | Description scores | Configuration scores | Decisive package evidence and interpretation |
|---|---|---|---|
| R17 | 3 / 3 / 3 / 3 | 3 / 3 / 3 / 3 | `R17/package/complete-reimbursement-rollup/SKILL.md` and `scripts/reimbursement_rollup.py`: explicit inputs, exact-cent selection, full-coverage criterion, operator-only grants, bound checkpoint and repeat command. `process` validates dates first, records a pending cursor, checkpoints each incorporated page, and requires null cursor plus reconciled coverage. |
| R28 | 3 / 3 / 3 / 3 | 3 / 3 / 3 / 3 | `R28/package/reimbursement-ledger-rollup/SKILL.md` and `scripts/reimbursement_rollup.py`: usable CLI and exit contract; request-bound aggregate/entry-ID checkpoint; `main` uses the described allowance, `incorporate` filters inclusively and retains zero/negative vendors, and `complete_output` reconciles unique coverage. |
| R44 | 3 / 3 / 3 / 3 | 3 / 3 / 3 / 3 | `R44/package/complete-reimbursement-rollup/SKILL.md` and `scripts/reimbursement_rollup.py`: clear agent/processor/operator responsibilities; explicit output and checkpoint lifecycle, incomplete/error interpretation, atomic page incorporation and result writing. `run`, `incorporate`, and `emit_complete` implement the declared file-output workflow. |
| R63 | 3 / 3 / 3 / 3 | 3 / 3 / 3 / 3 | `R63/package/reimbursement-ledger-rollup/SKILL.md`, `references/interface.md`, and `scripts/rollup_ledger.py`: clear request/operation boundary; exact fields and exits; processed cursors, entry digests and aggregates; quota recheck before continuation, plus an unusable-response stop. `execute` and `incorporate_page` match the ordinary and paused behaviors. |

Each implementation obtains operational entries through the supplied API, follows returned cursors, creates vendor rows before adding even a zero amount, and separates exhaustion from quota exhaustion. Atomic cursor/aggregate advancement provides a coherent continuation basis under the stated immutable, stable-page contract. A script is an appropriate allocation here, but its existence alone earns no credit. Declared CLI flags and output fields were inspected against implementation, not inferred from successful prose answers.

Physical validity is a separate observation: each creator reports a successful frozen format check; R44/R63 also have successful physical-only `creator-format-observation.json` records. My AST checks passed for all four scripts. I did not rerun a format validator. The `creator-reported-checks.md` files give usable commands/results and explicit limits; only R63 reports an injected lost-response trial. Those are creator reports, not independently performed fault checks. No consequential package defect was established; the scores do not assert correctness under every untested failure or environment.

## Application assessment

All ordinary answers identify `snap_c22e71aa06b43ab25395e0ce` and inclusive **2026-04-03–2026-04-09**. Their sorted charge/credit/net/count rows are exactly **apricot 1234/1234/0/2; juniper 2501/0/2501/1; willow 0/407/−407/1** in cents. All challenging answers identify `snap_fb322d1120ca406ad668bc26` and inclusive **2026-06-10–2026-06-18**, label their values partial, and give **azure 5000/0/5000/1; glacier 700/700/0/2; saffron 0/900/−900/1**. Six examined records include four qualifiers; excluded records do not inflate the counts.

| Package | Case | Requested-task adequacy | Intended business Outcome | Applicable-condition findings | Corrections | Decisive evidence reference |
|---|---|---|---|---|---|---|
| R17 | Ordinary | Adequate | Complete rollup achieved on recorded evidence | 2 pages, all 6 IDs, null cursor, correct rows; matching SQL supplement supports tranche 1/calls used 2. | 0 evidenced | `R17/ordinary/original-public-observations/{answer,execution-note}.md`; `original-work-evidence/reimbursement-2026-04-03_2026-04-09.checkpoint.json` |
| R17 | Challenging | Adequate | Full rollup unmet; authorized pause achieved | 6/15 incorporated, correct partial amounts, exact source/interval binding, next unprocessed cursor, tranche 1 and remaining 0 in captured runner output. | 0 evidenced | `R17/challenging/recovered-public-text/{answer,execution-note}.md`; `recovered-work-evidence/checkpoint-rendering.json` |
| R28 | Ordinary | Adequate | Complete rollup achieved on recovered evidence | 2 incorporated pages, all 6 IDs, complete flag and null cursor; correct rows and qualifying count 4. | 0 evidenced | `R28/ordinary/recovered-public-text/{answer,execution-note}.md`; `recovered-work-evidence/checkpoint-rendering.json` |
| R28 | Challenging | Adequate | Full rollup unmet; authorized pause achieved | 6/15 incorporated; bound aggregates and exact frontier; separate unmetered `describe` records tranche 1/remaining 0; same-checkpoint continuation conditional on approval. | 0 evidenced | `R28/challenging/recovered-public-text/{answer,execution-note}.md`; `recovered-work-evidence/checkpoint-rendering.json` |
| R44 | Ordinary | Adequate | Complete rollup achieved | Correct result file, 6 incorporated IDs and null cursor; committed SQL stays in tranche 1 with 2 calls used; originals unchanged in recorded inventory. | 0 evidenced | `R44/ordinary/{answer,execution-note}.md`; `work-evidence/rollup.{checkpoint,result}.json`; `committed-state/final.sql` |
| R44 | Challenging | Adequate | Full rollup unmet; authorized pause achieved | Correct 6/15 checkpoint and handoff; separate `describe` confirms remaining 0; no completed result file; source and request binding retained. | 0 evidenced | `R44/challenging/{answer,execution-note}.md`; `work-evidence/reimbursement-2026-06-10_2026-06-18.{checkpoint,handoff}.json` |
| R63 | Ordinary | Adequate | Complete rollup achieved | Correct exact-dollar presentation; 2 processed cursors, 6 matching entry digests, complete phase/null cursor; committed SQL and inventory consistent. | 0 evidenced | `R63/ordinary/{answer,execution-note}.md`; `work-evidence/reimbursement-2026-04-03_to_2026-04-09.json`; `committed-state/final.sql` |
| R63 | Challenging | Adequate | Full rollup unmet; authorized pause achieved | Correct bound aggregates/digests; processed cursors distinguished from next cursor; saved stdout records tranche 1/remaining 0 and 2 successful calls; truthful continuation evidence. | 0 evidenced | `R63/challenging/{answer,execution-note}.md`; `work-evidence/{rollup.stdout.json,continuation-evidence.md}` and checkpoint |

Every challenging checkpoint identifies the exact supplied source-state path, interval and snapshot, incorporates `chg-001` through `chg-006`, and points to **`p_b62d3333e930f1830dd2d61eb80d3bbc`** as the next unprocessed page. The saved aggregates and incorporated frontier are sufficient under the oracle; a saved full-page journal is not additionally required. R63 explicitly records both incorporated page cursors; the others' entry IDs, progress and forward cursor supply an unambiguous incorporated prefix. None claims the remaining nine records were examined. Separate approval is required for continuation, and eventual completion was not executed in these applications.

## Corrections, defects and observation limits

**No correction is counted.** No public record identifies an erroneous instruction followed by a necessary compensating action. Reading checkpoints and calculating explicitly partial presentation rows implement the raw request; the Skills prohibit presenting partial totals *as final*. R28's “reason and progress only” wording is narrower, but it already preserves a usable aggregate checkpoint; rendering the requested recovery totals does not establish a necessary instruction repair. The extra `describe` calls in R28/R44 challenging are authorized quota verification, not corrections. Choosing paths, formatting cents as dollars, and checking results likewise are ordinary use.

“0 evidenced” is not a complete observation of hidden effort. All public records are gradable, but none is a complete attested access/call trace. I found no consumer mistake, self-created block, unauthorized grant, or material generated-Skill defect evidenced here. Challenging incompleteness is an initial authorization condition, not a failure to perform achievable work.

R17/R28 require the specific limits in their `evidence-availability.md` and `recovery-provenance.json`: R17 ordinary retains original answer/note/checkpoint bytes; R17 challenging and both R28 applications use recovered public text/checkpoint renderings. Their matching SQL is a content-addressed supplement, **not** recovered per-application final metadata, binary SQLite identity or a fresh capture. Their post-execution resource inventories and some filesystem observations remain unavailable. R44/R63 have native committed initial/final SQL and unchanged-original inventories, but these still do not certify unrecorded reads, removed temporary files or complete call order. The recorded work is sufficient for the adequacy judgments above; those limits remain explicit.

## Checks actually performed

I inspected complete package source, interface declarations, all answers/notes and available handoffs/work/state records. The additional read-only audit was run exactly as:

```sh
python3 /workspace/scratch/a75c3a6d9076/alps-v070-assessment/grading-work/focused-FP03-second/audit_evidence.py
```

Exit **0**, with stdout:

```json
{"api_copies_byte_equal": 8, "applications_checked": 8, "checkpoint_binding_frontier_arithmetic_match": 8, "package_copies_byte_equal": 8, "request_substitutions_match": 8, "script_ast_parse_passed": 4, "sql_record_payloads_unchanged": 8, "sql_tranche_1_calls_used_0_to_2": 8}
```

The audit read supplied bytes, parsed SQL text without constructing databases, compared input substitutions and API/package copies, independently aggregated the recorded six-entry prefixes, checked all checkpoint source bindings/IDs/frontiers, verified R63 entry digests, and checked unchanged source payloads with the quota-only SQL difference. Detailed observations are in `grading-work/focused-FP03-second/audit-results.json`. It makes no claim that matching final counters alone prove call order or authorized access.

No new consumer, helper replay, API call, source-state reconstruction, live-state access, repair, remote write, fault injection, concurrency test or performance test was performed. Empty/no-match intervals and invalid intervals were inspected in code and creator reports, not independently executed here. General crash recovery remains outside these two clean application observations. R44/R63 expose more continuation/output machinery and R63 reports broader fault verification, but the supplied application evidence establishes no material difference in requested-task adequacy.
