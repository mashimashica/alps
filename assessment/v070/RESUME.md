# ALPS v0.7.0 assessment — resume here

## Authorization and delivery

The user authorized execution of the finalized assessment/improvement plan on 2026-09-07, including improvement, exemplar-replacement, and release-preparation pull requests. They explicitly expect recovery after rate limits. This assessment does not by itself authorize merging new PRs, tagging, or publishing a Release. PR descriptions are English. GitHub writes use direct APIs with plain UTF-8 tree contents, not git push, Actions, Base64, or temporary workflows.

## Frozen basis

- Repository: mashimashica/alps.
- Baseline A: main commit `dee3866d35e43db5db480fc9f85166a8dcb1ec3b`, tree `0b64eabaf2d8fc8c5a715e30fa903799387d9f87`, VERSION 0.7.0.
- Improvement worktree: `/workspace/scratch/a75c3a6d9076/alps-assessment-improvements`, branch `assess/v070-skills`.
- Do not modify older worktrees `alps`, `alps-skill-references`, or `alps-validation-review`.
- Baseline common skill-creator: the system authoring Skill at `/root/.codex/skills/.system/skill-creator`, copied and hashed under `frozen/skill-creator`. It is available in every arm, not compulsory. The similarly named personal-skill installation workflow is not the evaluated authoring aid; these are repository experiments, not personal installations.
- Pilot evidence at `../alps-skill-evaluation-57` predates this baseline. Preserve it; do not count its trials as current-main evidence.

## First actions after interruption

1. Read `protocol.md`, this file, and the latest `progress.md`.
2. Check `trial-list.tsv` and each recorded trial's original artifacts, execution note, and independent judgment. Presence of an artifact alone is not completion or success.
3. Inspect live agents before retrying an in-flight trial. Recover their outputs if available. If an attempt is lost or incomplete, record that fact and create a distinct attempt; do not overwrite or erase it.
4. Verify frozen input hashes. Do not update baseline A when main advances. Reconcile the eventual PR with current main separately.
5. Resume the earliest unfinished dependency. Never rerun completed trials just to get better results.
6. Save a durable checkpoint after each generation or consumer batch and before changing phase. Use the separate assessment/v070-evidence GitHub branch, assessment/v070/ prefix, direct APIs and plain UTF-8 content. Verify tree, commit and branch ref. Read checkpoints.md for the last confirmed save; retain previous commits. Do not merge this evidence branch into the product. Restore frozen/alps from the baseline commit and verify frozen-hashes.sha256 before resuming.
7. Volatile orchestration values can disappear with agent/runtime loss. Before each checkpoint mutation, fetch the exact evidence branch ref and its Git commit/tree and reconcile them with the last confirmed receipt. Validate required SHAs before create_tree/create_commit; never allow an absent base tree to turn a delta export into a replacement tree. The API rejected one missing-parent commit attempt after volatile values disappeared; no branch update occurred. Its delta was rebuilt on the verified remote base and saved successfully. Exact ref recovery is required even when a local export cache survives.

## Current phase

All 12 calibration creators and 24 fresh consumers are complete and adjudicated. H01 and H02 are fully reviewed and closed out; neither B1 nor B2 qualifies for progression. H02 yields nine adequate and seven inadequate applications; both B2 release cores substitute assessment or permitted stopping for sufficient achieved-work conditions. This is not proof that every generated defect is caused by the edit. D2-U012 and D2-U014 originals were interrupted by agent loss and retained; independent invalidity review permitted one fresh retry each. consumer-selected-attempts.json selects those first valid attempts and consumer-retry-list.tsv preserves their accounting. Fifty additional tasks were started: 48 complete and two incomplete. H03 reserves 18 tasks (six creators and twelve consumers), leaving four reserve slots. Do not rerun completed trials.

Read development-2-closeout.md, audits/dev2-progression-review.md and development-round-3.md. The product worktree now contains only frozen B3's two-file authoring/review clarification; B1 and B2 remain immutable rejected evidence. All six H03 luna/low creators completed and all six pinned form checks pass; source fidelity and behavioral adequacy are separate pending judgments. Twelve consumers are prepared in dev3-consumer-list.tsv, with D3-U001–005 running at this update; consult that ledger and live agents. Source-fidelity reviewer dev3_source_fidelity is running on the anonymized six-package packet. All original supplied creator input hashes match; audits/dev3-creator-observation-limits.md discloses one added local fixture, own-assignment access, and contradictory reported validation. These were retained without retry. H03 is the final ordinary development round; its prospective progression requirements remain fixed. No product PR or main trial has started.

The twelve reviewed public main cases remain frozen (36 files, main-case-hashes.json). prepare_main.py must not run before documenting a qualifying B selection. It creates a separate immutable schedule and digest before first execution; main-list.tsv is only the mutable execution ledger. Reference consumer remains gpt-5.6-sol/high. The experiment-only compare_main.py implements the predeclared analysis; all 13 numerical/denominator tests pass. Independent initial and follow-up reviews are complete/read, with the reproduced roundoff boundary bug and provenance/grouping gaps addressed. Subgroup planned and unconfirmed counts are reported. Do not treat this calculation as semantic grading or accept a candidate from numeric gates alone.

S08 consumer SQLite states are in dedicated temporary directories outside this evidence folder, identified in consumer-setup/<ID>.json. Initial logical state is durably represented by state-snapshots/<ID>/initial.sql and its hash metadata. After each booking consumer completes, use booking_state.py <ID> --label final to preserve its actual final committed state before checkpointing. Never run setup again over an existing trial. If the SQLite file is lost, restore trusted saved native SQL into a new, nonexisting database and record the new location and restoration; this preserves committed logical state, not byte-identical database identity. Preserve initial and final snapshots and incomplete attempt evidence, and do not manufacture a completed trial from a restoration.

## Important limits

Fresh subagents do not inherit conversation context. They receive only their task-local prompt and permitted files. The host filesystem is shared: path restrictions are procedural, not a security sandbox. Do not disclose held-out cases or independent oracles to creators. Consumer cases are materialized only after the associated creators finish. Keep public prompts/tool observations/artifacts, never private chain-of-thought.

The approved base plan is up to 2,028 task trials, excluding grading, host sessions and bounded development diagnostics. Completed counts must be reported independently of planned counts. Read protocol.md for exact arithmetic and convergence rules.
