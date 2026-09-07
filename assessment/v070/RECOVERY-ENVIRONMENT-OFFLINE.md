# Environment-offline recovery checkpoint — 2026-09-07

This document supersedes the execution counts and latest-checkpoint paragraph in the older RESUME.md snapshot until reconciliation is complete. It records observed progress; it does not declare unavailable files lost or durably saved.

The execution server disconnected with: "failed to query exec-server capabilities: exec-server connection attempt failed: environment registry request failed (409 Conflict, environment_offline): Environment is not connected." Both the ordinary execution tool and a read-only Node filesystem attempt failed before process/file access. The parent repeated a bounded pwd check and received the same error. This is an environment connection failure, not a reported model rate-limit error. Direct GitHub API reads still work. No exposed environment reconnection capability was found.

## Last verified full filesystem snapshot

Evidence branch: assessment/v070-evidence, repository mashimashica/alps.

- Commit: bb0b730b49dae994a4869e8002f246e338e9da1f.
- Tree: ebdeb7355d14bf5383b531f3b3a89137b01ebd92.
- Local immutable snapshot: /workspace/scratch/a75c3a6d9076/assessment-checkpoint-zcuYyf.
- 5,268 published files, 217 changed entries.
- Confirmed complete coverage: creators 001–068, consumers 001–083, 136 prepared consumer packets, final native API SQL for 073–083, all six S05 reports and three post-blind addenda, S05 root closeout/adjudication, and the original S06-P02 blind packet.
- Some later artifacts may have been copied while the snapshot was made. Their complete coverage is not inferred from presence of partial files.

The parent re-fetched this exact ref and commit through the direct API after disconnection. Parent, tree, author and DCO were verified. This emergency commit is a text-only descendant of that snapshot, not a new export of inaccessible local files.

## Latest execution observations awaiting reconciliation

| Item | Observed completion before disconnection | Durable coverage / unresolved work |
| --- | --- | --- |
| C creators | All 72 explicitly completed, format-validated and frozen. All 144 consumers prepared locally. | Full snapshot confirms 68 creators and 136 prepared consumers. Reconcile 069–072 and preparation 137–144 against originals and frozen hashes. Do not redo authoring. |
| C consumers | 001–093 explicitly completed. | Full snapshot confirms 001–083. 084–093 artifacts need reconciliation and saving. No completion is inferred solely from a status row. |
| C-U092 | Completion arrived around the outage. | Its ledger still said running, and final native API SQL had not yet been captured. Record completion observation and capture the actual original state after restoration. Do not reinitialize, grant quota or rerun it. |
| C-U094–097 | Spawned with their fixed prompts, but local ledger starts were not recorded. All four reported failure before reading prompt/resources or performing task operations. | Retain the same contexts. They are paused, not completed or newly adjudicated invalid. Parent instructed them to stop repeated tool attempts and wait. |
| C-U098–144 | Not started. | Continue only after recovery and saving reconciled evidence. |
| S06-P02 primary | Full grading completed. Final report write failed during the outage; the grader relayed its finished report through the conversation. | This emergency commit preserves that report at grades/business-S06-P02-primary.md. Its original blind packet is already durable. New component probe files/results and two SQLite databases require recovery; report links to them do not assert remote preservation. |
| C069 authored text | Existing completed agent relayed original successful apply_patch text, with no new authoring. | recovery/control-069-authored-text.md preserves that relay separately. No current byte identity or originally recorded content hash was available in the relay. |

Current agent names are /root/control_use_094, /root/control_use_095, /root/control_use_096 and /root/control_use_097. All retain the same trial identity. C094 and C095/096 cover S06; C097 begins S09. Their original initialization/setup resources must not be regenerated. A fresh business retry is not authorized merely because execution is unavailable. If contexts or original evidence prove lost, apply the preserved independent infrastructure adjudication and first-valid-attempt rules before any distinct retry; retain interrupted originals. Four reserve starts remain under the frozen cap.

The parent read the complete S06-P02 primary report. It grades seven applications adequate and one bounded deficiency (R44 challenging's inaccurate claim that no third attempt was made). All four ordinary business results are complete, and all four challenging applications have the correct permitted prefix and continuation evidence; their full business result remains incomplete. Two broader implementation defects were probed: R44 rejects a valid first terminal page/empty source, and R17 cannot reuse an already complete checkpoint without trying to page again. These are primary findings pending the required additional independent review, not an adjudicated S06 closeout. Consumer correction count is zero in this packet. No new business trial, later authorized tranche, crash injection or general reliability proof is claimed.

## Uncommitted state evidence to recover

Local evidence root: /workspace/scratch/a75c3a6d9076/alps-v070-assessment.

Actual final native API SQL was captured locally for C-U084–091 and C-U093. Captured ordinary SQL hashes match 0c59cdc1f01c69cb8dc8899d6565287e22fc0469988613be1a04c379594ca580; challenging hashes match 071ead7c2855dc57b35546ff0515c79039899eae12b921f60584232f858cb496. These observations do not substitute for original per-trial metadata, binary identity or call histories. C-U092 final API state was not captured; do not infer its hash.

API source databases are outside the evidence folder, at unique paths in consumer-setup/C-Uxxx.json. After explicit completion, control_ledger_state.py captures the actual final state. Do not call init or grant to reconstruct a completed run.

A separate consumer-produced workflow checkpoint exists at consumers/C-U093/work/reimbursement-rollup-2026-04-03_2026-04-09.sqlite. It is not the API source database. The parent explicitly preserved it with observation label consumer-complete:

- Original SQLite SHA-256: 2b35f698076080a15b9df2148535a2955608c6f125c3a5c00504e4050e950359.
- Native SQL: sqlite-evidence/consumer-complete/consumers/C-U093/work/reimbursement-rollup-2026-04-03_2026-04-09.sqlite.sql.
- Native SQL SHA-256: 2f30def62fff9a87c9ebfa3d82235d7c627cb6df9d489a376f35396f4538c87c.
- The preservation completed locally; no subsequent full remote checkpoint succeeded.

The primary S06-P02 grader created and finished using two disposable component databases:

- grading-work/S06-P02-primary/r17-completed-checkpoint/source.sqlite.
- grading-work/S06-P02-primary/r44-empty-source/source.sqlite.

It also wrote and read grading-work/S06-P02-primary/component_probes.py and component-probe-results.json before disconnection. These were not durably exported. The completed grader confirmed no further writes were expected. Preserve their actual native SQL with an explicit new observation label after recovery. Any corresponding blind-packet copies of workflow databases also need representation; do not drop them as runtime cache.

The last normal checkpoint attempts stopped before Git mutation, first on the unrepresented C-U093 workflow database and, after that was preserved, on the grader's unrepresented r17 source.sqlite. They were not successful saves. The verified ref remained bb0b730b49dae994a4869e8002f246e338e9da1f before this emergency update.

## Recovery order

1. Fetch the latest exact evidence ref and commit/tree through the direct Git API. Read this document before the older RESUME counts. This commit and any later emergency text recovery must be preserved when normal whole-folder saving resumes.
2. Reconnect the environment and inspect existing files, immutable snapshots and live agents. Do not replace an original worktree, frozen package, database or attempt merely because its existence was temporarily unverifiable.
3. Reconcile original completed 069–072 creator artifacts and 084–093 consumer artifacts against frozen inventories and captured observations. Conversation-recovered text is supplemental evidence until byte identity is checked. Record any genuinely missing content and its consequences without regenerating it and calling it original.
4. Fetch/merge this emergency RESUME prefix, recovery document and report into the local evidence folder before running checkpoint-direct-api.js. The local .local/published-hashes.json and mutable status files are older than this remote emergency commit. Rebuild/reconcile that cache against the verified remote state; never blindly overwrite the remote recovery files using the stale local export.
5. Reconcile completion notifications with record_status.py, preserving original observation times. Capture C-U092's actual final API state. Preserve all finished unrepresented SQLite sources and verify native SQL/metadata before export.
6. Save the reconciled 72 creators, 144 prepared consumers and 93 completed consumers with a fully verified direct-API checkpoint before adding new work.
7. Resume the existing C-U094–097 contexts where available, then 098–144 under the frozen schedule. Finish S06/S09/S10 primary and required independent second reviews. Grade component faults separately from business applications and distinguish achieved business results from permitted partial work.
8. Read full reports, close out C and produce provisional example eligibility. Apply the separate dependency decision below before any blocked main experiment or final/example selection.

## Scope and release boundary remain unchanged

Calibration and all three permitted ordinary development rounds are complete. B1, B2 and B3 were rejected for progression. The product worktree was verified clean at frozen A, dee3866d35e43db5db480fc9f85166a8dcb1ec3b, before disconnection. No qualifying B exists. No fourth ordinary development round or bypass of the frozen acceptance gates has been authorized.

The independently reviewed dependency plan permits finishing C and version-independent preparation. Main A/B and 1,776 dependent task slots remain pending under scope-decision-required.md. C outcomes cannot substitute for paired acceptance, claim ALPS benefit, close the final example pool or establish release readiness. The three-round cap was intended to bound improvement; any later change needs a concrete scope decision after independent work is exhausted.

No new product PR, merge, tag or Release has occurred in this assessment program. The evidence branch must not be merged into the product. User authorization covers the assessment and supported example/release-preparation PRs, with English PR bodies and direct UTF-8 GitHub API updates. It does not authorize merging those new PRs, tagging or publishing a Release.

## Additional conversation recovery

After the first emergency checkpoint, the original completed C070, C071 and C072 agents also relayed their retained successful apply_patch contents without filesystem access or new authoring. The corresponding recovery/control-070-authored-text.md, control-071-authored-text.md and control-072-authored-text.md preserve each Skill, supporting resources and public execution note separately from the inaccessible originals. Together with C069, all four later creators now have supplemental conversation recovery text. Original package/freeze byte reconciliation and the later consumer artifacts remain pending.

The first emergency commit is 6a0a6dc737ba93df750c449c3ca752d492300053, tree 6b1d4db53f66af3ec70c9c84efe159736a4bd63f, parent bb0b730b49dae994a4869e8002f246e338e9da1f. Its four changed files were fetched back as UTF-8 and compared in full to the submitted text; all four matched. See recovery/checkpoint-receipts.md. Always fetch the latest exact evidence ref before another update.
