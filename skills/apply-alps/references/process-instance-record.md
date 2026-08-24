# Process Instance Record

This informative binding supports a readable record for a Process Instance. The record can be created before invocation and completed in the same file after execution. Use it only when the quality risk, applicable Controls, review, handoff, or a Conformance claim justifies the detail.

This is an optional Environment Binding. Its file format, fields, and checker rules are binding-specific, not ALPS requirements. Headings are for readers and may be renamed or reordered. The visible ``- `key`: value`` fields and the `kind` value make a generated record machine-readable.

## Contents

- [Binding rules](#binding-rules)
- [Core record](#core-record)
- [Conditional blocks](#conditional-blocks)
- [Generator and checker](#generator-and-checker)

## Binding rules

- Keep one field on one line. Repeat a field such as `evidence` when several values are needed.
- Do not repeat a single-valued field. Contradictory duplicate values make the binding ambiguous and are rejected by the checker.
- Keep binding fields in visible ordinary Markdown. Fenced or indented code is not binding data; raw HTML and HTML comments are rejected because their visibility is renderer-dependent.
- Do not invent missing values. Leave a value blank while the record is being prepared, then complete or remove it as appropriate.
- Identify the managed source. Add the exact applicable `source_statement` when the record must remain reviewable without reopening that source; a source reference alone may be proportionate in lower-risk use.
- Use `instance_statement` only to state the application-specific expression. Its presence alone does not establish Tailoring.
- Add a `criterion` when an Instance-specific success condition is needed. Record `result` and `assessment` after execution; add `evidence` and `limitations` as justified by risk.
- If meaning, normative strength, or applicability is changed, add a `tailoring` block and apply the management Process. Do not use this format to make Tailoring implicit.
- Add handoff and Conformance blocks only when they apply. A Conformance block records a claim; the format and checker do not prove the claim.

## Core record

The following is a representative layout, not a required heading set or order.

```markdown
# <record title>

## Application basis
- `kind`: application
- `record_format`: process-instance-record/1
- `source`: <managed Process Description and version, including its providing Skill when applicable>
- `context`: <application situation and need>
- `scope`: <application scope, including relevant exclusions or an explicit statement that none apply>

## Intended Outcome
- `kind`: outcome
- `source_statement`: <exact applicable Outcome statement>
- `instance_statement`: <application-specific expression, when useful>
- `criterion`: <Instance-specific success condition, when needed>
- `result`:
- `assessment`:
- `evidence`:
- `limitations`:

## Task
- `kind`: task
- `source_statement`: <exact applicable Task statement>
- `instance_statement`: <application-specific expression, when useful>
- `criterion`:
- `result`:
- `assessment`:
- `evidence`:
- `limitations`:
```

Use additional blocks with core `kind` values such as `activity`, `purpose`, `input`, `output`, `entry_criterion`, `exit_criterion`, `control`, `constraint`, `enabler`, `exchange`, or `decision` when they are material. Prefix a local extension kind with `x_`, for example `x_review_note`; this makes a misspelled core kind distinguishable from an intentional extension. The checker ignores prose sections that have no `kind` field and does not impose a complete Process Description on every Process Instance.

## Conditional blocks

Use a handoff block for a material Output/Input correspondence. At completion, record its status.

```markdown
## Handoff
- `kind`: handoff
- `provider`: <providing Process or Process Instance>
- `output`: <Output>
- `receiver`: <receiving Process or Process Instance>
- `input`: <Input>
- `correspondence`: <meaning, scope, and quality conditions>
- `status`:
```

Use a Tailoring block only when an element is added, changed, or excluded through managed Tailoring. This binding's checker requires values for `basis`, `candidate_evaluation`, `decision`, `affected_party_input`, and `controls_constraints`. Recording `scope` and `rationale` is recommended, but the checker treats them as optional. `before`, `after`, `assumptions_criteria`, and `performance_assessment` are also optional according to the application situation. These field names and their one-line representation are binding-specific and do not establish the validity of the Tailoring decision.

```markdown
## Tailoring
- `kind`: tailoring
- `scope`: <recommended: affected elements and application scope>
- `before`: <optional: managed statement before the change>
- `after`: <optional: approved statement after the change>
- `basis`: <risks, requirements, complexity, available capabilities and resources, and relevant standards>
- `candidate_evaluation`: <evaluation of candidate Processes or lifecycle models against application conditions, expertise and experience, stakeholder expectations and requirements, and risk tolerance>
- `rationale`: <recommended: decision rationale>
- `decision`: <management decision and, when applicable, its resolvable reference>
- `affected_party_input`: <affected parties and the Input obtained, or an explicit statement that none were identified>
- `controls_constraints`: <applicable Controls and Constraints, or an explicit statement that none apply>
- `assumptions_criteria`: <optional: assumptions and decision criteria>
- `performance_assessment`: <optional: how the tailored application will be monitored or assessed>
```

Use a Conformance block only when making a claim.

```markdown
## Conformance
- `kind`: conformance
- `subject`: <claim subject>
- `scope`: <claim scope>
- `basis`: <Outcomes, Tasks, or both>
- `claim`: <Full or Tailored>
- `tailoring_decision`: <managed Tailoring decision reference when the Tailoring details are not restated locally>
- `remaining_requirements`: <for Tailored Conformance, every Outcome and Activity/Task requirement remaining in scope>
- `evidence`: <evidence supporting the claim>
```

For Tailored Conformance, use `subject`, `scope`, and `remaining_requirements` in the Conformance block to identify the tailored Process, the claim scope, and every Outcome and Activity/Task requirement that remains within that scope. The providing Skill may also be identified when applicable. Also include either a local `tailoring` block or a `tailoring_decision` reference through which the details can be resolved. A `tailoring_decision` reference does not replace `scope` or `remaining_requirements` in the Conformance block. For an ALPS claim, the evidence must demonstrate satisfaction of those remaining Outcomes and requirements; the checker verifies only that the evidence field is present.

## Generator and checker

The generator transcribes only the values supplied on the command line. It does not read a Process Description to infer its Purpose, Outcomes, Tasks, normative attributes, or Tailoring. It prepares the complete content before atomically placing it at the output path, so a failed replacement does not truncate the existing record.

```bash
python3 scripts/process_instance_record.py new \
  --title "Contract review" \
  --source "contract-review SKILL.md, managed version 2026-08-15" \
  --context "Review contract A before internal approval" \
  --scope "Contract body and supplied appendices" \
  --outcome "Material contractual issues are identified." \
  --task "Review the applicable contract terms." \
  --output contract-review.md

python3 scripts/process_instance_record.py check --at instantiation contract-review.md
python3 scripts/process_instance_record.py check --at completion contract-review.md
```

The instantiation check requires exactly one `application` block with `record_format: process-instance-record/1`, the source, context, application scope, and at least one intended Outcome or success criterion. The completion check additionally requires a result and assessment for each Outcome, included Task, standalone success criterion, and any other block that declares a `criterion`. Evidence is required by the checker only for a Conformance claim, and `claim` accepts only `Full` or `Tailored`. A Tailored claim requires `scope` and `remaining_requirements` together with either a local Tailoring block or a `tailoring_decision` reference. Conditional blocks are otherwise checked only when present. These checks establish only conformity to this binding, not truth, Outcome achievement, Tailoring validity, or ALPS Conformance.
