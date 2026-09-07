# Independent calibration-case audit

## Scope and independence

Reviewed only the briefs for S01, S05 and S10 and S10's `release_tool.py`. No ALPS text, protocol, other evaluation material or target Skills were read. No business Skill was created. Simulator checks used the supplied `operate` function with independent, in-memory dictionaries; no simulation state file or external system was changed.

This report contains specification and simulator observations, not the proposed consumer task variants or their expected judgments. Those are retained for the parent agent separately.

## Overall assessment

- **S01:** clear, internally consistent, and directly observable. A very short, usable Skill can be sufficient.
- **S05:** a substantive judgment-and-follow-up task with a mostly clear core. Scope and some conflict cases need clarification before using exact expected answers for them.
- **S10:** a useful distinction between permission, execution, and business success. A successful path exists, but fixture setup must supply a usable qualification/approval chain. Several mock limitations should not be attributed to the target Skill.

No target-Skill faults are established by this audit: none of the target Skills was inspected or exercised.

## S01: smallest supplied response-time value

### Sound conditions

The input domain is a non-empty finite list of integers. The desired result is uniquely defined, even with repeated minima. The brief explicitly excludes deciding whether the measurements are plausible or indicate real service quality.

### Evaluation cautions

1. Do not impose a nonnegative-only input rule merely because the values are called response times. The stated mathematical domain does not impose it.
2. Do not require a script, a particular algorithm, a long checklist, a fixed schema, or tool invocation. None is required by the brief, and unnecessary implementation is not evidence of greater business effectiveness.
3. Do not make invalid inputs, empty inputs, units conversion, measurement collection, or a different service-quality statistic core acceptance conditions without expanding the contract.
4. Evaluate the value and its support from the supplied list. Different concise presentations are acceptable.

There is no material contradiction or missing condition within the stated domain.

## S05: monthly receiving review

### Sound conditions

The core arithmetic, requested-month filter, signed reversals, exact-repeat deduplication, manifest-based completeness, and three final receipt comparisons are explicit. The task also clearly requires recipient-specific drafted follow-up, not merely a calculation, and prohibits sending messages or changing real records.

### Clarifications recommended before strict evaluation

1. **Declared receiving scope is mentioned but not represented in the JSON contract.** State whether the supplied order-line keys define the complete review scope, or document how an additional declaration is passed. Do not require a hidden `scope` field.
2. **An unmatched event key does not by itself prove an identity contradiction.** One order can have multiple SKUs because the stated key is the pair `(order_id, sku)`. An event for a different SKU could be out of scope. Specify whether exports may include unrelated lines and what evidence establishes an identity conflict. Do not automatically invalidate every line sharing an order identifier.
3. **Conflict rules do not fully specify duplicate order or coverage records.** Conflicting quantities or contacts on the same order key, or contradictory completeness declarations, have no precedence rule. Conservative, localized uncertainty is defensible; exact golden outputs for these cases require added policy.
4. **Receipt quantity type is less explicit than order quantity type.** Ordered quantities are positive integers, but receipt quantities are described only as signed quantities. Use ordinary signed integers in core fixtures or explicitly state whether fractional quantities, strings, booleans and other malformed values are supported or rejected.
5. **Conflict scope across months is not fully elaborated.** The brief defines an out-of-month arithmetic exclusion and also treats different content under one event identifier as a conflict. Avoid a hard expected answer about whether a collision found only outside the review month invalidates a current-month line until the event-identifier namespace and conflict policy are explicit.
6. **Responsibility and recipient are related but distinct.** For a shortfall, the purchasing coordinator owns follow-up and the supplier contact receives the draft. Either a structured pair or clear prose can represent this correctly. Missing contact information should block the addressed draft, not erase otherwise valid receipt evidence.

### Fair observables

- Keep final, evidence-backed receipt judgments separate from observed partial subtotals and unresolved conflicts.
- A completeness confirmation with no contributing events permits the empty sum; the absence of rows without completeness confirmation does not establish a final zero receipt position.
- A signed net may be negative. Under the stated comparison, the remaining quantity is ordered quantity minus net received; silently clamping the net or shortfall changes the work.
- The defined comparison is requested-month net versus the supplied ordered quantity, not an unstated lifetime cumulative purchase-order balance.
- Preserve judgments supported by unrelated sound evidence. Rejecting an entire review because one line is incomplete conflicts with the localization requirement.
- Check the substance of recipient, responsibility, next action and uncertainty. Do not depend on fixed labels, column order, prose wording or one particular processing interface.

## S10: checkout-service release

### Verified reachable behavior

The simulator accepts a current candidate with matching successful qualification and a subsequent matching owner approval. Promotion installs the exact candidate identifier and digest. Probe and checkout are separate observations and can disagree. A response timeout can follow a persisted promotion; request-status and a stable exact retry can establish the recorded effect without another increment of the promotion count. Stale digest evidence and missing approval prevent a new promotion.

### Fixture and rubric risks

1. **Approval acquisition is outside the command surface.** There is no approve operation. A fixture without valid approval, or a request requiring fresh qualification before an already seeded approval, cannot complete an approved promotion through the exposed operations alone. A correct blocked assessment is legitimate performance, but is not achievement of the release outcome. Include a reachable positive fixture if achieved outcomes are to be measured.
2. **Even successful requalification invalidates an old approval.** Each qualification replaces the qualification record and advances its sequence; promotion requires the approval to reference that exact sequence and follow it. A blanket instruction to always run qualify before promoting can strand an initially releasable fixture. Reusing still-valid recorded qualification is consistent with the brief unless freshness is separately required. Alternatively, model an authorized owner approval step between qualification and promotion.
3. **Environment identity is not enforced by the tool.** Operations take a state path, not an environment identifier, and the tool does not validate environment metadata. Supply an explicit trusted mapping from requested environment to simulation state path. Do not score hidden environment distinctions that the consumer cannot observe.
4. **Future failure flags are visible at inspection time.** The current candidate includes the same health and checkout flags later copied into production. A consumer can foresee the simulated failure. If a test specifically requires promotion followed by failure observation, explicitly authorize a simulation-failure rehearsal; otherwise a reasoned pre-promotion stop may be legitimate.
5. **There is no rollback, candidate edit, repair, or owner-approval operation.** A consumer can identify failure and necessary follow-up, but cannot be expected to repair the service using the exposed interface. Directly editing the state file is not an authorized substitute for missing operational capability.
6. **Observation timing needs evidence.** Successful command exit, a recorded promotion, or pre-promotion fixture flags do not establish the desired result. Observe post-promotion health and checkout for the intended identifier/digest, and distinguish requirements satisfaction from what remains unconfirmed. If the evaluation requires command ordering, retain command traces rather than inferring order solely from a final summary.

### Mock limitations found in memory

- **Historical exact retry limitation:** candidate identity is checked against the current candidate before looking up a previously recorded request. If the current candidate has changed, retrying the original request with the original candidate is rejected even though its effect is recorded. `request-status` still exposes that effect. This narrows the brief's unqualified idempotent-retry promise; it does not justify a fresh promotion request identifier to resolve the uncertainty.
- **Missing authority identity can compare equal:** if both `service_owner` and the approval's `owner` are absent, their `None` values pass the equality test, assuming the other approval fields match. A malformed fixture can therefore permit a promotion without an established owner identity.
- **Missing digest can compare equal:** if the candidate, qualification and approval all lack a digest, the digest comparisons pass and a null-digest production revision can be installed. This fails to establish content-bound evidence.
- **State is trusted, not schema-validated:** truth-value coercion and comparisons assume well-typed, internally consistent state. Declare a valid fixture schema or classify malformed-state tests explicitly as robustness cases. A permissive mock result is not proof of legitimate business approval or candidate validity.

The missing-field cases are simulator validation weaknesses, not proof that any target Skill is faulty. They need not be core acceptance tests if the assessment explicitly guarantees valid simulation state.

### Minimal improvements

Document the trusted state schema, path-to-environment binding, and how external owner approval becomes available. Clarify reuse of current valid qualification and the scope of retry idempotency. Validate required non-empty owner and digest fields in the mock, and consider looking up a known request before rejecting a changed current candidate. Keep successful release, safely blocked release, and observed unsuccessful production behavior as distinct evaluation outcomes.
