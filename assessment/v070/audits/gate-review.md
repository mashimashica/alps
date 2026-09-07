# Independent acceptance-criteria review

## Scope and disposition

Reviewed only `protocol.md`, `gates.md`, `calibration-decisions.md`, and `calibration-synthesis.md`. This is a review of the experiment's decision rules, not a product assessment. No other evidence, historical PRs, or source artifacts were inspected; the four inputs were not edited.

**Disposition: substantively sound, but not yet a fully operational acceptance rule set.** Resolve the decision-logic, budget, missing-observation, and version/stopping ambiguities before candidate B outputs exist. The remaining findings require short prospective definitions, not a new evaluation framework or any change to fixed PF/work-system meanings.

The strongest existing safeguards should be preserved: identical skill-creator availability; fresh creators and consumers; separation of requested-task adequacy from business Outcome achievement; independent business-grounded grading; artifact-level clustering; no automatic inference from one generated defect to source defect; and eligibility plus unseen revalidation for the example. The calibration adjudications correctly distinguish an explicit required owner from an oracle-added preference and an avoidable blockage from an unsupported authorization allegation. These are appropriate anti-goalpost precedents.

## Findings

### 1. Acceptance has two incompatible readings; settle them before B

**Decision-critical.** `gates.md`, lines 17–25, says all rules apply, but rule 4 is an alternative to rule 3. Rule 3 permits a +5-point estimate with a confidence interval crossing zero, provided its lower bound exceeds −5 points. The subsequent instruction to preserve A for “inconclusive intervals,” and `protocol.md`, line 97, requiring demonstrated quality improvement, do not establish whether that candidate is accepted. For example, a +6-point estimate with interval [−4, +16] can currently be accepted or rejected by defensible readings. A quality-neutral candidate with 25% less measured burden similarly passes the stated alternative but fails a literal conjunction of all rules.

**Recommended adjudication:** write the logic as mandatory semantic/mechanism/safety gates AND either the effectiveness route OR the burden route. I recommend the conservative effectiveness route: estimate at least +5 points **and** lower 95% bound above zero. The burden route retains its stated −5-point quality margin and independently measured 20% burden reduction, once finding 4 is resolved. Otherwise retain A. An interval crossing zero is not evidence of ineffectiveness; it is insufficient for this recommended effectiveness acceptance rule. Even a positive interval does not establish that the true gain is at least five points.

This recommendation is a prospective tightening, not a claim that non-inferiority is intrinsically an invalid deployment policy. If the intended policy instead permits +5-point estimates with a lower bound between −5 and zero, explicitly choose that weaker rule now, define “inconclusive” against its required non-regression bound, and describe accepted results as estimated improvement with demonstrated bounded non-regression—not demonstrated positive superiority. Do not switch interpretations after seeing B.

### 2. “Base total” allows off-budget trials despite the authorized ceiling

**Decision-critical.** The table in `protocol.md`, lines 77–91, correctly totals up to 2,028 task trials. But line 91 excludes development diagnostics, while line 99 permits replacement holdout work and line 40 preserves retries as separate attempts. Those provisions can exceed the user-approved task-trial ceiling. The table already uses the full ceiling when all 24 exemplar revalidation trials run; it contains no explicit development/retry reserve.

**Recommended adjudication:** treat 2,028 as a hard ceiling on executed creator, consumer, revision, and selection task trials, including diagnostic, retry, and replacement task executions. Independent grading or mechanical checks are not automatically task trials, but a fresh creator/consumer assignment cannot be exempted merely by calling it a diagnostic or Host check. Failed starts are not executed trials, consistently with calibration. Maintain an executed/reserved/remaining ledger. Prospectively reconcile the stage allocations with required diagnostics and revalidation; do not silently cancel required stages to create headroom. If the remaining work cannot fit, report the affected stages as blocked and request a budget/scope decision before exceeding the cap.

### 3. The primary denominator does not yet operationalize “unconfirmed”

**Decision-critical.** `gates.md`, lines 9–13, retains missing observations without saying how they enter the per-Skill adequacy fraction or matched-pair analysis. Excluding them can bias arm comparisons; treating every missing observation as an ordinary failure can attribute infrastructure loss to ALPS. `calibration-decisions.md`, line 28, also warns against mixing positive-work and deliberately failing-case denominators, whereas the later primary measure pools appropriate task handling.

**Recommended adjudication:** the primary measure may pool predeclared case types because it measures requested-task adequacy, not business Outcome achievement. Report case-type strata and keep positive business Outcome denominators separate. A faithful, appropriate response to insufficient business evidence may be **adequate with an unconfirmed Outcome**; lack of evidence about whether the consumer actually performed the requested work is an **unconfirmed task observation**. These are different states.

Freeze planned case slots and weights. For unresolved task observations, report observed classifications, completeness, and best-/worst-case adequacy bounds rather than silently dropping slots or labeling them failures. Do not declare a required gate passed if admissible missing-outcome assignments reverse that judgment. Define an arm-blind infrastructure-invalidity rule and a fixed retry rule, using the first valid retry rather than the best attempt. Product-caused failure remains an observed outcome, not a reason for an infrastructure exclusion.

### 4. The burden alternative is not measurable as currently specified

**Important before collection.** `gates.md`, line 22, gives a useful 20% threshold, but “corrective interventions or avoidable tool interactions in affected tasks” leaves the metric, denominator, affected subset, and choice between the two measures unspecified. This permits selecting whichever metric or subset improves after results are known. Consumer compensation in S10 and explicit-Python invocation in calibration illustrate why faithful final answers alone do not measure artifact use burden.

**Action:** prospectively choose the burden endpoint or a fixed combination; define the counted unit, who independently identifies avoidability, the affected task set, exposure denominator, and the zero-baseline case. Apply the same observation procedure to A/B, retain paired artifact clustering, and report its uncertainty. Count compensating work rather than erasing it because the final answer succeeded; do not count necessary business work as avoidable. Specify whether “without a required correction” concerns correction of the delivered answer, consumer compensation for the Skill, or both. Keep final-task adequacy, artifact defects, and compensating effort separate. Until this is frozen and actually measured, the alternative route remains unavailable, as the existing gate already says.

### 5. Freeze candidate identity and the development/confirmation sequence

**Decision-critical.** `protocol.md`, lines 97–105, and `gates.md`, lines 31–37, combine up to three development rounds, two successive no-useful-improvement rounds, complete-package freezing, and correction/replacement after a consumed holdout. They do not say whether main A/B output can drive another B revision or which B version the full comparison then estimates. Nor do they say how two plateau rounds interact with a useful change in round three or with release gates that can only be assessed after final freezing.

**Action:** record a stage order and immutable candidate IDs. A full-comparison estimate must identify one B version; do not pool changing candidates under one label. If main results inform a subsequent edit, label that evidence developmental and identify which unchanged or new trials support the new version. Adaptively selected main results are not independent confirmation. Final holdout claims belong to the frozen complete package, including the chosen example; they do not isolate the core edit alone.

Define the reference, hypotheses, examined cases, and useful-improvement rule for each round. Two rounds without supported improvement justify only a bounded plateau among the examined changes, not proof that no useful improvement exists. Wide intervals, unperformed diagnostics, or simply rereading the same evidence do not establish convergence. If round three improves the candidate but leaves fewer than two successive plateau rounds, stop at the cap and report “round limit reached; convergence not established.” Any post-holdout correction is another development round and another version, within both the three-round and task-trial limits; otherwise escalate. A consumed holdout cannot be reused as fresh confirmation.

### 6. Clustering is sound in principle, but the fixed design must survive resampling

**Important before analysis.** `gates.md`, lines 11–13, properly keeps both consumer cases together and resamples families. However, resampling all matched artifact pairs within a family can change the proportions of the six deliberately fixed creator configurations. Weighting, bootstrap details, and the target population remain unspecified. There are only 12 main and six final task-family clusters; synthetic selected families do not establish representativeness of general business work.

**Action:** freeze family/configuration weights and pair IDs before scoring. Preserve the intended configuration mixture, for example by resampling matched repetitions within each family/configuration block while retaining both consumer cases. Record bootstrap interval construction and replicate count. Report per-family/configuration results, leave-one-family-out sensitivity, missingness sensitivity, and the limited-cluster caveat already required. A random seed can make the analysis rerunnable without claiming reproducible model generations. Treat family/configuration inspection and the −10-point trigger as diagnostic, not a collection of unadjusted significance claims. Confidence intervals describe the declared empirical sampling model, not automatic generalization beyond these synthetic tasks and tested settings.

### 7. Specify attribution evidence without making generation defects disappear

**Important before defect adjudication.** `gates.md`, lines 19–25, correctly distinguishes shipped-source defects from individual generated-package defects. Nevertheless, “reproduced,” “reproducible,” and “caused by the candidate” have no operational evidentiary standard. Replaying the same generated buggy script reproduces a package fault, not its source-level cause. Conversely, an unreplicated consequential observation must not vanish from consumer adequacy simply because it does not establish ALPS causality.

**Action:** retain separate judgments for (a) observed task/package defect, (b) valid business/environment contract, (c) replication of the behavior, and (d) attribution to a source rule or candidate edit. Record the proposed mechanism and independent check. If attribution depends on generation behavior, require fresh matched A/B diagnostic evidence with the relevant contract fixed; replaying one frozen package is insufficient. A direct independently verified material contradiction in shipped source can establish a source defect without waiting for many stochastic generations. Preserve unresolved attribution explicitly. Do not count an oracle/environment correction as candidate improvement, and rerun affected arms symmetrically. The S05/S10 calibration distinctions should remain precedents, not be generalized into new universal product obligations.

### 8. Example ranking and blocked release gates need explicit consequences

**Important before selection/final judgment.** `protocol.md`, lines 103–105, and `gates.md`, lines 29–33, provide good eligibility and revalidation requirements, but leave “top three” ranking, tie-breaking, failed-candidate replacement, and the effect of blocked stages open. Merely documenting an unperformed mandatory check cannot satisfy that check. Selecting among several unrelated business tasks is also not justified by comparing raw success percentages.

**Action:** freeze an eligibility-first quality ranking and tie-break rule before examining revalidation outcomes. Revalidate up to the top three eligible candidates independently on unseen, contract-validated cases; choose the highest-ranked candidate that meets every required check. If none qualifies, report that result rather than repeatedly fishing for a passing winner. Any repair or EN/JA adaptation is a distinct version with appropriately independent rechecks, charged to the trial ceiling. Describe the result as the best eligible example in the assessed pool, not a globally best example or evidence of average ALPS benefit.

Declare which blocked stages prevent an overall release-readiness recommendation and which only limit a specific support claim. Required final/semantic/example checks that remain unconfirmed cannot be reported as passed. Native support cannot be inferred from successful local package use. Keep “candidate eligible,” “required verification complete,” and “convergence established” distinct rather than treating any one as all three.

## Freeze-record correction

`calibration-decisions.md`, line 30, still says the numeric gates are pending and promises their basis will be recorded there; `gates.md`, line 3, says they are fixed before B or main outputs. The stricter timing is preferable: resolve these findings and create a dated, immutable freeze record **before any B/main outputs**, not merely before scoring. Record the practical rationale for the 5-point gain, 5-point non-regression margin, 20% burden reduction, and 10-point family-review trigger; do not imply the tiny calibration established their power. Explicitly supersede the stale pending status without rewriting historical decisions. `calibration-synthesis.md`, line 10, still has an S05 second grade pending: either close that adjudication or identify the bounded unresolved issue and do not treat it as settled calibration evidence.

No finding warrants changing PF or work-system semantic scope, removing the C arm's fair assistance, relaxing failure-case truthfulness, exceeding the authorized trial/round limits, or attributing a generated defect to ALPS without supporting evidence.

## Follow-up disposition: revised prospective gates

Reviewed only the updated `gates.md` and this review. Reviewed gate-file SHA-256: `3424136cf47f70abce9265dc0572d10215815446e378fac64a950413078b96a0`. The coordinator reports that no B1/main creator has started; this follow-up does not independently audit trial execution or the source proposal.

**Disposition: the substantive decision-rule ambiguities are resolved sufficiently to proceed with bounded development.** Two narrow pre-acceptance details remain below; this is not a product-quality or release-readiness finding.

**Budget correction:** withdraw finding 2's claim that 2,028 was an all-inclusive user ceiling. That premise came from the initial review assignment and was incorrect. The protocol's base-trial exclusion is now explicitly adjudicated, with a separate shared cap of 72 additional executions across diagnostics, retries and replacement confirmation—not 72 per round—and at most three development rounds. Required base stages cannot be silently sacrificed. This is finite accounting of up to 2,028 base plus 72 additional task executions, with escalation when either limit cannot accommodate required work.

Confirmed in the revised gates:

- Rules 1, 2 and 5 are mandatory, with rule 3 OR rule 4. Effectiveness requires a gain of at least five points AND a positive 95% lower bound. Read the inconclusiveness fallback subject to this explicit logic: an inconclusive effectiveness route does not veto an independently passing burden route.
- The compensation endpoint, deduplication unit, full main-task population, fixed weights, dual blind review and zero-observed-baseline exclusion are declared. Adequate delivered work can coexist with a defective artifact and compensating effort.
- Planned slots survive missingness; business uncertainty differs from unobserved task performance; gate-reversing bounds make the gate unconfirmed. Infrastructure invalidity is arm-blind, with at most one retry and no best-attempt selection.
- Bootstrap configuration weights, paired repetitions, consumer clustering, replicate count, percentile construction, analysis seed and limited-generalization cautions are fixed.
- Candidate versions and stage order prohibit mixing B revisions or treating consumed comparison data as fresh confirmation. Attribution retains valid-contract failures without turning package replay into proof of source causality.
- Eligibility-first ranking, deterministic ties, one top-three revalidation pass, failed-pool reporting, blocked-check consequences and Host-specific limitations are explicit. Plateau is bounded to examined changes and remains separate from final verification; round exhaustion cannot be relabeled convergence.

Two narrow follow-ups:

1. Restore the original explicit requirement to review the **full task-owned diff** before a release-readiness recommendation. The revised blocked-check paragraph names format/version/link/whitespace checks but no longer carries that existing review requirement.
2. Before invoking the burden route, freeze the count-analysis edge cases. An observed positive A mean can still produce bootstrap replicates with A equal to zero; a relative-reduction interval then needs a declared convention. One clean option is a paired interval for the absolute count reduction, using the relative reduction only for the 20% point threshold. Also specify defensible bounds for missing compensation counts, or leave the route unconfirmed while they remain unresolved: binary adequacy bounds cannot automatically bound a count. Do not discard undefined replicates or impute unknown compensation as zero.

These follow-ups do not require changing the declared effectiveness threshold, widening semantic scope, adding development rounds, or delaying otherwise valid bounded diagnostic work.
