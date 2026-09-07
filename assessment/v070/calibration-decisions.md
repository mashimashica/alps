# Calibration decisions before consumer testing

## Case corrections and limits

An independent case author inspected only the three business briefs and simulation, not ALPS or any generated Skills. Their public audit is in audits/calibration-case-audit.md. Concrete consumer inputs and expected results were returned to the coordinator without disk materialization. The original creation task and the future consumer task remain distinct.

Before S05 creation began, the coordinator clarified that all supplied order lines/month define scope, coverage does not exclude lines, current-month known-order/unknown-SKU events require order identity reconciliation, and unknown orders are out of scope. This is a case correction, not an ALPS improvement. Trial-local briefs already contain it. Calibration does not rigidly score undefined policies for contradictory order/coverage duplicates, cross-month identifier collisions, or malformed quantity types.

S10 calibration supplies well-formed local state with an exact valid qualification/approval chain and a trusted mapping from environment name to state path. No new owner approval can be generated with the provided simulator. Reusing still-valid existing qualification is permissible; unconditional requalification can invalidate the available approval. Missing owner/digest robustness and historical retry after candidate replacement are mock limitations outside these two calibration fixtures, not target-Skill defects. Future tests needing those conditions must first define and verify the environment contract. The negative production case explicitly authorizes a local failure rehearsal because the mock exposes prospective health flags.

## Observation and completion

Creator completion means the agent delivered the requested artifact and an execution note; it is not a quality pass. The parent records successful agent starts and final messages. An unsuccessful spawn due to capacity is not an executed trial. The platform exposes requested model/effort settings but no separately attested actual serving model or price per trial; do not invent them.

Commands and checks are evidenced by task-local logs/notes and produced files where available. If exact stdout, stderr or command timing was not captured, label the evidence as the creator's report rather than an independently verified trace. Independent component and consumer tests provide separate corroboration. Do not count a summary as proof of unobserved operations.

## Calibration rubric anchors

Each relevant dimension is assessed with evidence: 0 = absent or contradictory; 1 = substantial corrective work needed; 2 = usable with a bounded material limitation; 3 = adequate for the examined task. Not-applicable dimensions require a reason tied to the business task, not missing evidence. Different prose and implementations can earn the same judgment.

| Layer | Assessed dimensions |
| --- | --- |
| Description | Intent and scope preserved; observable success conditions; necessary work/detail and open choices; information/reference/condition meaning |
| Supporting configuration | Responsibilities and judgment/processing allocation; interfaces and information; implementation/connections within scope; evidence and feasibility limits |
| Consumer work | Each intended result supported or explicitly unmet/unconfirmed; appropriate requested action/follow-up; mandatory conditions respected; user-usable answer grounded in observations |
| Packaging and usability | Physical format; usable required references; comprehensible discovery; unnecessary effort to understand/use the Skill |

Business-Outcomes achievement and quality of response to an unmet or unconfirmed condition are separate columns. The denominator for achievable positive work is not silently mixed with deliberately impossible or failure cases. No-ALPS controls are not judged against ALPS-only headings. Source-specific Markdown fidelity is examined separately after the blind business assessment. A line count can describe an artifact but cannot decide whether its detail is needed.

The final numeric release gates, minimum useful differences and regression margins remain pending calibration. They must be fixed before main A/B scoring, with the chosen basis recorded here. Calibration results are exploratory, not evidence from the later untouched holdout.

## Calibration closeout — 2026-09-07

The preceding pending status is superseded by gates.md, fixed after the completed calibration and independent gate review, before any B1 or main creator outputs. It defines the 5-point useful-gain target, strict positive interval for effectiveness acceptance, 5-point non-regression margin for the separately measured burden route, 20% compensation-reduction target, and 10-point family-review trigger. These are prospective practical decision policies, not power estimates derived from calibration. The original draft and its independent critique remain in checkpoint history; the accepted logic, missing-observation handling, candidate identity, budget and stopping definitions are explicit in gates.md.

Primary task adequacy pools predeclared case types with fixed weights because it measures appropriate requested work, not positive business Outcome achievement. Positive Outcome denominators and failure/incomplete strata remain separate. All calibration trials are complete and the consequential S05/S10 findings have independent second assessments; see calibration-synthesis.md for root adjudications.
