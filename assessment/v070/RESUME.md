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

## Current phase

All 12 calibration creators and 24 fresh consumers are complete, with blind grades, independent second S05/S10 grades, source-fidelity review and root adjudications. All 12 generated packages pass pinned format validation. Main public cases are authored. Gates are fixed after independent operational review. B1 is a NOTE/注記-only candidate in the improvement worktree and frozen/candidate-B1; its exact hashes and patch are preserved and independent semantic/locale review found no blocker. H01's eight fresh creators are complete (8/8 pinned format pass); its sixteen consumers have not started. Independent new consumer-case authors are working on S10, S05 and S08. Read development-round-1.md, dev1-list.tsv, progress.md and calibration-synthesis.md. No improvement is accepted, no new product PR is open, no main trial has begun. The reference consumer remains gpt-5.6-sol/high.

## Important limits

Fresh subagents do not inherit conversation context. They receive only their task-local prompt and permitted files. The host filesystem is shared: path restrictions are procedural, not a security sandbox. Do not disclose held-out cases or independent oracles to creators. Consumer cases are materialized only after the associated creators finish. Keep public prompts/tool observations/artifacts, never private chain-of-thought.

The approved base plan is up to 2,028 task trials, excluding grading, host sessions and bounded development diagnostics. Completed counts must be reported independently of planned counts. Read protocol.md for exact arithmetic and convergence rules.
