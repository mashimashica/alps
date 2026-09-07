# Coordinator restoration observations

Observation date: 2026-09-07 UTC. Recovery work adds no creator, consumer or business trial.

The environment reconnected with a filesystem from the older H02 stage. The evidence directory was preserved as `../alps-v070-assessment-restored-h02`; its product-worktree diff is also preserved there. No original user worktree was replaced.

The coordinator fetched only the explicitly authorized evidence branch, shallow and without tags, into `../alps-evidence-recovery-75c0ea9`. The exact commit is `75c0ea9bddf379c5e1803e4c0114ba5b47c871d8`, tree `ecb6cc6d6ba4ebf2c009be8b51b6602749f0939d`, parent `c9c04b94d6b2ae12dd0b9bf8767d89049fe8368f`. The direct API verified commit parent, tree, author, DCO and non-forced branch state; all twelve entries from the latest emergency save were fetched back and matched in full. No PR or unrelated history was investigated.

The committed `assessment/v070` directory was copied to the original evidence-root path. All 5,290 tracked files individually matched their exact Git blob SHA and mode. The only additional root material was the intentionally excluded frozen A checkout, copied from the preserved local directory and checked by the unchanged 77-entry frozen manifest. All six approved helper digests in the independent restoration review matched. Only after this exact comparison did `checkpoint.py mark` recreate the publication cache for the 5,290 published files.

The product worktree was at frozen A with two modified English/Japanese Skill files. Both modified files exactly matched the saved B2 candidate, and the complete diff was preserved before targeted restoration of just those two paths to A. The resulting worktree is clean at `dee3866d35e43db5db480fc9f85166a8dcb1ec3b`.

The independent reviewer inspected the immutable evidence checkout and the source-anchored SQL, prompt and resource identities. Its full report and continuation addendum were read by the coordinator. The review SHA-256 is `b24460ae1ebd8813cd67e378d894e7ef97ed0b427c503f2e80345484eeff7890`. It allows preservation and scoped continuation, while identifying missing originals and required narrow recovery support.

Using explicit original completion notifications, `record_status.py` reconciled C creators 069–072, consumers 084–093, and S06-P02-primary as completed with their original agent identities. No `--event` argument was supplied, so no missing historical start/end time was invented and no existing timestamp was replaced. At this observation the ledgers contain 72 completed creators, 93 completed consumers and 17 completed grading reports. There are 43 prepared but incomplete consumer slots and eight not-yet-recovered preparation slots.

Recovery has not recreated lost completed state, replayed a business operation, granted quota, changed a task prompt or frozen schedule, or resumed an original consumer. C-U094–097 context availability must be verified before continuation. C-U097 and scheduled first-start S09 consumers are independent of the new-path SQLite binding work required for 094–096. Genuine context loss requires independent adjudication before a distinct retry.

Remaining evidence work follows `environment-restoration-review.md`: recover 071/072 text with provenance; independently establish complete final packages before new recovery freezes/preparation; preserve matched historical SQL as supplements, not original final metadata; leave unsupported observations unavailable; review narrow restored-path snapshot/grading and supplemental packaging support. The 1,776 candidate-dependent slots remain blocked under the unchanged scope decision. No product PR, merge, tag or Release was created by recovery.
