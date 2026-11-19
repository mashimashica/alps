# Opening a PR

## Purpose

Put the change up for review as a ready PR.

## Outcomes

- Every PR the run opens is open and ready, not a draft.
- Each such PR's commits are small and landable.
- The worktree each such PR comes from holds no unrelated work.
- Each such PR's title follows the title format under Controls.
- Each such PR's body is a one-minute briefing that follows the body format under Controls.
- Where there are follow-ups, they are stacked by base branch.

## Tasks

The following Tasks are required whenever this playbook runs, each with the conditions it states. Numbers identify the Tasks and set no order.

1. Work from a git worktree off trunk, and keep unrelated work out of it.
2. Rebase into small, landable commits.
3. Run `/deslop` from `cursor-team-kit` over the diff before commit.
4. Stack follow-ups by base branch.
5. Open PRs ready, through the run's PR tool with `draft: false`. Without one, use `gh pr create` without `--draft`, or `origin pr create --status open` when Origin's CLI resolves the repository.

## Controls

Title: `type(scope): subject`, naming a real symbol when one carries the change. Body: a one-minute briefing under 40 lines with these `##` headings in order, dropping empty ones: `## Why`, `## What changed`, `## Scope`, `## Tradeoffs` (only rejected alternatives a reviewer would otherwise ask about), `## Blast Radius`, `## Verification`.

## Constraints

This playbook is invoked at the end of every other playbook. Opening a PR does not start a babysit.
