# ALPS v0.7.0 assessment protocol

## Objective

Establish whether the two ALPS design Skills help create understandable, applicable and evaluable work descriptions and effective supporting agent work systems. Evaluate generated Skills as tools for fresh consumers, not merely as attractive documents. Deliver justified core improvements, the highest-quality suitable generated exemplar, and release-preparation PRs with evidence and remaining limits.

## Scope lock

The following remain fixed throughout ordinary improvement:

- PF meanings, relationships, normative force, scope, and Markdown/NOTE conventions; optional inclusion does not make the vocabulary's meaning optional.
- Work-system principles' design object, allocation, composition and evaluation meanings.
- The identities and responsibility boundaries of the two design Skills and the central meaning of their Purposes and Outcomes.
- Two distributed Skills, existing native Host support, and separation of development Skills and examples from distribution discovery.
- Minimal descriptions and necessary detail; no runtime, registry, approval institution, new global obligation, compatibility aliases, or legacy negative-contract tests.
- Common authoring assistance, baseline A, business criteria, independent oracles, fair arm comparison and declared evaluation scope.

Allowed changes preserve those meanings: clarity, grouping, navigation, task guidance, explanatory notes, examples, genuine reference corrections, removal of duplication, EN/JA alignment, and bounded design-support processing justified by observed failure. Business scripts belong to the target example, not the design Skill. Example replacement may change its business task and associated code, fixtures, guides and tests as one responsibility. Necessary native distribution and validation plumbing may change.

A proposal to change a fixed meaning is escalated with evidence and impact; it is not slipped into an editorial correction. Calibration may correct defective cases or oracles, with affected arms rerun and those corrections not counted as ALPS improvement. Historical documents and unrelated assets remain untouched.

## Comparison arms and access

| Arm | Authoring assistance |
| --- | --- |
| A | Frozen current-main ALPS plus frozen skill-creator |
| B | Candidate ALPS plus the same frozen skill-creator |
| C | The same skill-creator, without ALPS |

Skill-creator is available in every scenario, including consumer/evaluator work where useful; it is not an obligatory invocation. Record actual use. All arms receive the same raw business material, ordinary Agent Skills format information, authorized tools and environment. Do not assess C against ALPS-specific headings or vocabulary. The estimand is ALPS's added value when skill-creator is available.

Three entrypoints isolate responsibilities: process-description design starts from raw needs; work-system design starts from the same sufficient work description across arms; combined design starts from raw needs and environment, using either responsibility as needed without a mandatory linear sequence.

## Independent evidence

Separate creator, consumer and grader agents. Each creator and consumer is a new conversation and task workspace. Consumers see only the generated Skill and unseen work inputs, not creator conversation or intended answer. They may not repair the frozen artifact unless the assigned task is specifically revision. Blind graders receive anonymized artifacts, observable behavior, and an independently derived oracle, not arm/model labels or improvement intentions. Critical/disputed findings and a random subset receive a second grade. Disagreement is adjudicated against business evidence, not majority vote alone.

The shared filesystem is not an enforced sandbox. Restrict supplied paths and inspect reported access. Do not put consumer inputs or hidden oracles in creator-accessible task folders. Materialize consumer inputs after associated generation ends. Procedural leakage risk remains a stated limitation.

Persist original prompts, raw inputs and hashes, generated Skill versions, requested model/effort and whatever actual configuration is observable, public commands/results, final responses, judgments, interruptions and unperformed checks. No private reasoning traces. A retry is a separate attempt, never replacement evidence. Tool/environment failures are not silently attributed to ALPS or scored as successful work.

## Case families

| ID | Entry | Business concern |
| --- | --- | --- |
| S01 | Description | Minimal bounded candidate selection |
| S02 | Description | One-off workshop operational change |
| S03 | Description | Handover/understanding without a mandatory artifact |
| S04 | Description | Shared requirements/feasibility information, levels and a cross-cutting View |
| S05 | Work system | Purchase/receipt variance with signed corrections and completeness |
| S06 | Work system | All-record aggregation through paginated API |
| S07 | Work system | Existing CLI/SQL sufficient; avoid unnecessary wrappers |
| S08 | Work system | State-changing booking with timeout, partial effects and concurrency |
| S09 | Combined | Intervention assessment: numerical thresholds and comparability |
| S10 | Combined | Approval/order-constrained release with independent preparation |
| S11 | Combined | Changed criteria and scoped revision of related Skills |
| S12 | Combined | Capability change and reallocation preserving work requirements |

Use normal, boundary, incomplete, conflicting, changed-context/version and interaction-failure variants, with review/draft/revision scope where relevant. Synthetic business inputs avoid live effects. No single gold prose or implementation. Final holdout tasks are new work, unavailable during development.

## Assessment layers

1. Description meaning, relationships, boundaries and applicable conditions.
2. Supporting configuration: allocation, information, interfaces and feasibility.
3. Component behavior and required connections, including relevant failure/incompleteness.
4. Fresh consumer work: intended results and conditions supported by actual evidence.
5. Discovery, packaging, EN/JA meaning, native Host resources and human readability.

Score description validity, execution outcomes and satisfaction of requirements separately. A review may correctly identify an unmet condition without satisfying it. Appropriate handling of uncertainty can be good system behavior while the business Outcome remains unachieved. Artifact existence and zero exit status do not prove effectiveness. Quantitative summaries never replace case findings or conceal critical failures.

Calibration fixes rubric anchors, release gates, minimum useful improvement and regression margins before the full comparison. Use paired comparisons by scenario/model/effort/repetition and uncertainty intervals clustered by generated artifact/scenario where appropriate. Do not treat multiple consumer cases from one Skill as independent generated Skills. Show family/configuration results as well as pooled summaries.

## Trial budget

Creators: gpt-5.6-luna, gpt-5.6-sol and gpt-6-astra, each low/high. Reference consumer: gpt-5.6-sol/high. Calibration creator settings: gpt-5.6-luna/low and gpt-5.6-sol/high. Fresh contexts, no seed-based reproducibility claim.

| Stage | Design trials | Consumer trials | Other task trials |
| --- | ---: | ---: | ---: |
| Calibration: 3 tasks × 2 settings × A/C | 12 | 24 | 0 |
| Main: 12 × 6 settings × A/B × 2 repetitions | 288 | 576 | 0 |
| C control: 6 preselected tasks × 6 × 2 | 72 | 144 | 0 |
| Final: 6 new tasks × 6 × A/B × 2 | 144 | 288 | 0 |
| Locale: 3 × 2 source languages × 2 request languages × A/B × 2, one creator | 48 | 96 | 0 |
| Transfer: 24 preselected artifacts × 2 additional consumer configurations × 2 cases | 0 | 96 | 0 |
| Review/revision: 12 requests × A/B × 2 settings | 0 | 0 | 48 |
| Selection: 24 requests × A/B × 2 settings | 0 | 0 | 96 |
| Top-3 exemplar revalidation: 3 × 2 consumers × 2 cases × 2 repeats | 0 | up to 24 | 0 |
| Old/new exemplar influence: 6 tasks × 2 examples × 2 creators; 2 consumer cases | 24 | 48 | 0 |
| Total | 588 | up to 1,296 | 144 |

The base total is up to 2,028 task trials, not including independent grades, double grading, Host sessions or separately recorded development diagnostics. Record measured runtime and available usage data; do not invent monetary costs. At most six child agents run concurrently. An unavailable model/configuration is a recorded limitation, not silently replaced with another under the same label.

Preselected C families: S01, S03, S05, S06, S09, S10. Main repetitions are distinct creator threads. Additional transfer consumers: gpt-5.6-luna/low and gpt-6-astra/high. Locale creator: gpt-5.6-sol/high. Other-task settings: luna/low and sol/high. Transfer artifacts are selected by a fixed balanced rule before inspecting their results.

## Improvement and stopping

Each change begins with a reproduced defect, its cause, target edit and predicted measurable effect. Separate unrelated hypotheses. Run the targeted case and affected cross-business regression. Accept demonstrated quality improvement, or maintained quality with less comprehension/use burden—not fewer lines as an end in itself.

Use at most three development rounds. Stop ordinary exploration when release gates are met and two successive rounds show no practically meaningful improvement. If gates remain unmet at round three, report the concrete failure and needed decision; do not declare convergence or release readiness. Do not tune on the frozen final holdout. If it informs a correction, replace consumed final cases with new ones and record the additional work.

## Exemplar selection and PRs

Choose from all A/B/C results. Eligibility requires a coherent work description, justified judgment/processing split, useful interfaces and information, working bundled processing, independent consumer evidence, correct failure/incomplete behavior, synthetic shareable resources, readability, and illustration of both design responsibilities. Compare quality only after eligibility, not unrelated raw success percentages. Revalidate the top three against unseen cases to reduce lucky-winner selection. A C-arm winner is reported as such; exemplar quality does not establish average ALPS benefit.

Preserve original candidates. EN/JA and distribution adaptation creates a distinct version, re-evaluated before shipment. Keep the old example fixed during core comparison. Then compare old/new-example influence with core fixed. Freeze the complete final package, including the replacement example, before final holdout, locale, Host and release judgment.

Deliver separate English-body PRs for core improvements, exemplar replacement, and release preparation. The example remains outside distributed Skill discovery. Remove superseded example implementation and tests only when no longer needed; retain original assessment evidence outside the Plugin. Do not add a new independent ALPS evaluation schema/runtime or restore deleted repository-layout assertion tests.

## Durability and resumption

The assessment folder is ordinary experiment evidence, not a product contract. Keep trial status and progress in readable files. Snapshot to the dedicated assessment/v070-evidence branch at each completed batch; retain earlier checkpoint commits. Expensive outputs are saved before starting the next batch. All authored Skills and evidence are synced through direct GitHub APIs with DCO and verified tree/commit/ref identity; the evidence branch is not merged into the distribution. The frozen ALPS export is recovered from its identified baseline commit rather than duplicated in that branch. Resumption begins at RESUME.md and retains completed, failed, interrupted and not-run trials distinctly.
