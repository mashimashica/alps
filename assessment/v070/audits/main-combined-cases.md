# Main combined-design cases: S09, S11, S12

Prepared as original fictional case packets. This audit describes their construction, interface verification, and limits; it is not a set of target answers or a consumer-grading specification.

## Scope and authorship

Created only `main-cases/S09/`, `main-cases/S11/`, `main-cases/S12/`, and this audit within the assessment tree. All local file creation and edits used `apply_patch`. No target Agent Skills, completed business deliverables, hidden consumer cases, concrete hidden tests, or gold business decisions were authored. No ALPS specification, pilot/current outputs, grades, PR/history, or other worktrees were read. No subagents or external actions were used.

Each brief asks its creator to produce a reusable Agent Skill and a concrete local application from raw business needs and an environment packet. None prescribes ALPS headings or vocabulary, a fixed report, a new runtime, a required new script, or a multiagent architecture. Input baselines are read-only; creation is restricted to a fresh local `deliverables/` area. External operating decisions, notifications, and live-system mutations are explicitly outside permission scope. The parent task will review and persist the resulting case materials.

## S09 — Northbank dispatch verification

Files: one brief, two numerical CSV extracts, one measurement dictionary/context note, and one owner-authorized decision-context note.

The requested result is an operational decision about a second-person package check, with a reproducible numerical basis and a feasible next-period course of action. The measurements intentionally separate shipment-cohort quality outcomes from whole-line labor and dispatch outcomes. Stable downstream observations, changed station-catch capture, incomplete recent cohorts, case-mix movement, a concurrent common template change, a nonrandomized comparison line, one-off training, short-shift observations, costs, forecast volume/mix, and a real hours limit all have distinct roles. This makes an aggregate before/after threshold comparison insufficient, without requiring a specific statistical model or mandating one final recommendation.

Construction checks performed on the public sources:

- Verified 28 unique cohort rows and 14 unique shift rows, matching date/line coverage, and the intended one-to-many relationship that makes repeated labor totals unsafe.
- Verified nonnegative counts, mature orders bounded by shipments, downstream outcomes bounded by mature orders, and station catches bounded by shipments.
- Verified overtime and training are subsets of productive hours and dispatch misses cannot exceed the corresponding shipments.
- Verified four recent cohort rows have no mature observations and that the latest shift is the documented lower-volume shift.

Limits: this is a small observational packet, not a randomized efficacy study. Forecast feasibility requires visible assumptions; a selectively applied check has no observed performance in the packet. The case does not establish one uniquely correct business action, and this audit contains no expected recommendation or computed answer table. It does establish enough numerical and contextual structure to distinguish a supported decision from unsupported causal, maturity, mix, labor, or capacity reasoning.

## S11 — Meridian customer-care revision

Files: one brief, an authorized change memo, one shared baseline policy, one source interface, and four related work descriptions.

The requested result is a scoped, usable document revision, supported by a reusable revision Skill. The change modifies Launch Assist's eligibility timing and authoritative date source, and therefore affects routing evidence and its intake-to-scheduling handoff. Commercial review and historical quality work have independent delivery-based definitions that must keep their meaning. A similar old day-count appears in more than one work context, making indiscriminate substitution unsafe. The approved memo defines authority, effective date, revision identity, excluded changes, unresolved-evidence behavior, and the lack of permission to reopen closed cases.

The source interface provides record identity, authorization evidence, calendar-date semantics, revision selection, and explicit void/conflict handling. It is supplied because changing the date source without its interpretation would leave the revision underspecified. No customer-row dataset or live register is needed for this document task.

Verification: confirmed that all four supplied work descriptions link to the same existing relative policy path. Reviewed the approved change against the baseline to keep the independent rules, ownership boundaries, and safety stop explicit. The revised target bundle itself was not created or graded.

Limits: the packet supports revision of these documents, not organization-wide rollout or operational customer decisions. A creator may choose its change-record format and local support approach. Later evaluation should distinguish meaningful dependency maintenance from superficial text substitution, without requiring byte-for-byte preservation of unaffected prose.

## S12 — Stonewake receiving support after a tool upgrade

Files: one brief, an unchanged receiving policy, former support notes, the new tool interface, a supplied standard-library command, and a three-file nonproduction demonstration packet.

The requested result is a reusable receiving-review Skill, a support setup reassessed against the new capability, and a local demonstration review. Former normalization, joining, signed summation, duplicate manual calculation, and lineage-copying workarounds are tied to specific old capability limits. The revised arrangement must still address whole-piece evidence, source reliability and completeness, quality context, pending or damaged counts, current-date applicability, restricted-part approval, and release authority. These are not delegated to the numerical command merely because it now produces reliable grouped evidence.

`tools/stock_evidence.py` is supplied environment functionality, not a required target implementation. It uses Python 3's standard library, reads two explicitly named local CSVs, and emits JSON evidence. It supports normalized full-identity matching, exact integer-thousandth arithmetic, additive manifest lines, signed posted count changes, pending-event exclusion with lineage, full outer coverage, deterministic grouping, missing-side nulls, and validation failures without partial evidence. It neither processes quality context nor writes inventory or modifies its inputs.

Verification was performed on disposable setup files outside the assessment tree, under `stock-evidence-setup.WwM6uA`, not on a hidden consumer case and not by executing any target Skill. The command's `--version` and `--help` both ran successfully. Disposable probes checked:

- Trimmed/case-normalized complete keys with leading zeros preserved.
- Exact additive and signed arithmetic using deliberately fractional interface-only quantities, plus pending-event exclusion. Those fractional setup values were not represented as valid business release evidence.
- Manifest and event lineage, deterministic repeated output, count-only and manifest-only groups, meaningful zero versus missing-side `null`, and negative-net evidence flags.
- Duplicate event-ID rejection, invalid numeric notation rejection, nonexistent-input failure, correctly headed empty inputs, exit status, standard-output/standard-error separation, and absence of partial evidence.
- Input hashes before and after the probes, confirming no mutation.

All listed probes passed. They are interface smoke checks, not exhaustive software assurance or a business grading suite. The public demonstration packet was structurally inspected but no completed release recommendations were authored here. The tool cannot detect an event never supplied, certify source authenticity, provide an unavailable capability, or replace the receiving and quality owners. Those remaining limits are explicit in the public interface and business policy.

## Remaining review and persistence

The parent should review the three briefs and supplied resources as case-design artifacts before persistence. No solution reports, target Skills, or reusable hidden-test suites accompany them. The disposable setup inputs are not part of the case payload and need not be persisted. Any later consumer or grading design remains independent of this audit.
