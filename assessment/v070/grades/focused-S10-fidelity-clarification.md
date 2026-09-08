# S10 — Clarification of M1

**M1 should not be counted as an established material source-fidelity defect for the stated brief and supplied CLI contract.** Its omission of an explicit “previous command has finished” or serial-access condition is better classified as a conditional applicability limit, with a bounded clarity concern in the packages' broader incomplete-response wording. The original report's material classification was too strong. This clarification leaves [the original report](focused-S10-fidelity.md) unchanged and qualifies only M1.

**The stated interface supports the generated recovery instructions.** Both [009's brief][b009] and [010's brief][b010] expressly promise that a supported request ID makes an exact retry idempotent and that a timeout can follow a state change. In each supplied implementation ([009][t009], [010][t010]), `operate` first updates production and the request ledger in memory, then returns the timeout result with `changed=True` and code 75. `main` synchronously writes the changed state before printing that response and returning code 75. Thus the specified, completed exit-75 result follows a successful write; it does not report that an original process remains in flight. An exact later replay finds the ledger record and returns it without another promotion.

The generated packages retain the request ID, query status before retrying, accept a matching recorded promotion, and avoid another promotion when that effect is recorded ([009 Skill][g009], “Promote with recoverable request identity”; [009 interface][r009], “Retry boundary”; [010 Skill][g010], “Promote with a recoverable identity,” Tasks 4–5). Those instructions correspond to the promised interface. Neither package directs the agent to overlap mutations.

| Circumstance | Supported judgment |
| --- | --- |
| Completed command returns the specified exit 75 | The write precedes the response. Status-first reconciliation and retained request identity are appropriate; M1 establishes no defect for this case. |
| A completed call's response is missing or truncated | Missing response content does not itself invalidate the sequential idempotency promise. Status lookup can recover a recorded effect; the packages require identity and prerequisite checks before any allowed retry. |
| A runner reports a timeout while the original command continues, or writers overlap | The source supplies no locking or atomic ledger check/update. A current empty ledger cannot establish that no pending write will follow. Applicability of the same recovery recipe is unconfirmed in this execution setting; no such setting or occurrence was established by this review. |

**Why the broader wording matters.** Focus-009 covers a response that “times out, is incomplete, or otherwise leaves its effect uncertain”; focus-010 covers a response that is “missing, truncated, times out, or otherwise leaves the effect uncertain.” Those formulations can be read to include a runner-level timeout that leaves work active, rather than only the specified completed command result. If used in that additional setting, status returning no record plus unchanged prerequisites would not, by itself, establish that the earlier operation has ceased. The packages do not explicitly distinguish these meanings of timeout. That is the limited textual basis for retaining a scope-clarity observation. Broad wording alone does not prove that the packages promise concurrent safety or that their intended runner permits overlapping execution.

**Assumption versus defect.** The brief's exact-retry guarantee is an affirmative design basis, and the implementation supports ordinary sequential use. Lack of locking is a limit of the supplied capability, not a generated departure from that promise. The [work-system principles §§4–5][aws] require relevant conditions and recovery limits to be clear, but they do not justify converting every unexamined runtime possibility into an established defect. The generated guidance would be insufficient if an applicable environment were known to leave the first call running or permit conflicting writers and the guidance nevertheless authorized a retry without resolving that condition. This source review provides no evidence establishing those additional conditions.

**Confidence and scope.** Confidence is high that the specified exit-75 path and sequential exact retry are preserved. Confidence is also high that the source lacks a concurrency guarantee; the significance of the broader wording remains conditional on an unexamined runner/access model. No race, duplicate promotion, consumer failure, or effectiveness result is inferred. No execution, consumer inspection, repair or source change was added. Only this clarification was written.

[b009]: ../trials/focus-009/input/brief.md
[b010]: ../trials/focus-010/input/brief.md
[t009]: ../trials/focus-009/input/release_tool.py
[t010]: ../trials/focus-010/input/release_tool.py
[g009]: ../frozen/focused-artifacts/focus-009/release-checkout-service/SKILL.md
[r009]: ../frozen/focused-artifacts/focus-009/release-checkout-service/references/release-tool.md
[g010]: ../frozen/focused-artifacts/focus-010/release-checkout-service/SKILL.md
[aws]: ../frozen/alps/skills/design-agent-work-system/references/agent-work-system-design.md

