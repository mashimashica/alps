# Analysis method review

Reviewed only `gates.md`, `protocol.md`, `compare_main.py`, and `test_compare_main.py`. No generated Skills, experimental observations, or other assessment files were inspected. Implementation and supplied tests were not edited. Checks ran from disposable `/tmp` with bytecode writes disabled.

This audit concerns the pre-fix helper, SHA-256 `c6fe2adc719a9ec886f17044f886112c1ac35fd521fbb65eb61e14df879275f2`, and tests, SHA-256 `3d937c32ce5fd995f90cd438245894a0fa80cdbb785021b7bcbf8e3ad6b535ce`.

The paired estimator and bootstrap implement the declared method for a complete, balanced supplied schedule. One reproduced numerical bug and two reporting/input-integrity gaps should be resolved before using the helper for the main decision.

## Material findings

1. **An exact 20% burden reduction incorrectly fails.** At helper line 158, `point[3] >= .20` rejects floating-point `0.19999999999999996`. A synthetic fixture with all applications adequate and compensation counts A=5, B=4 has exactly 20% reduction, adequacy interval `[0, 0]`, and a strictly positive burden interval concentrated at 20%, yet `burden_numeric_gate` is false. This changes the predeclared inclusive threshold into a stricter rule for an achievable result. Use an exact comparison or a narrowly documented numerical tolerance, without substantively relaxing the threshold, and retain this regression fixture. The supplied tests do not exercise the exact 20% boundary.

2. **The required substantive case-type report is absent.** Lines 17 and 165–169 report only `ordinary` and `challenging`. These identify the two consumer slots; they do not implement the predeclared positive/incomplete/failure grouping in `gates.md`. The helper has no supplied mapping from slots to those substantive types. A mapping frozen independently of outcomes is needed before final analysis, with the associated denominators and missingness bounds. The test named `test_equal_configuration_weights_and_separate_case_types` verifies slot variants, not the three planned substantive types.

3. **Complete prospective denominators depend on an unchecked input prerequisite.** The balance checks correctly reject unmatched arms and asymmetric omissions, but cannot recognize symmetric truncation. In an independent six-configuration fixture, removing the same configuration from every family and its observations is accepted; reported planned applications shrink from 144 to 120 and the five remaining configurations receive the whole weight. This is not evidence that the actual schedule is incomplete: that file was outside review scope. It shows that balanced shape alone cannot establish the declared main denominator of 12 families × 6 configurations × 2 repetitions × 2 arms × 2 consumers = 576 applications. The CLI needs a verified connection to the complete prospectively frozen schedule, or equivalent external verification documented with each result.

## Numerical verification

All 10 supplied unit tests passed. They cover constant effects, absent observations, evidence/count validation, duplicate/outside observations, unmatched schedules, configuration retention, zero baseline burden, and basic percentile behavior.

An independent nonconstant fixture used families `f=0..2`, configurations `c=0..5`, repetitions `r=0..1`, and consumers `v=0..1`, giving 72 applications per arm. Adequacy indicators were A: `(f+2*c+r+v)%5 > 1`; B: `(2*f+c+2*r+v)%7 > 1`. Compensation counts were A: `(2*f+c+r+v)%4`; B: `(f+2*c+2*r+v)%3`.

I calculated the point estimates using rational arithmetic and independently constructed 10,000 family-then-repetition draws with `random.Random(700)` and direct uniform-index selection. Neither `bootstrap_keys`, `summarize`, nor the helper percentile function was reused for the reference calculation. Every reference draw retained six Skills per configuration and both consumers per selected paired Skill. The independent estimates and linear percentile intervals agreed with the helper within `1e-14`:

| Quantity | Verified result |
| --- | --- |
| A adequacy | 11/18 |
| B adequacy | 17/24 |
| B − A | 7/72 |
| Adequacy 95% interval | −0.0555555555555556 to 0.25 |
| Mean compensation, A / B | 1.5 / 1 |
| Relative reduction | 1/3 |
| Reduction 95% interval | 0.2083333333333333 to 0.4375274122807014 |

Calling the default analysis again returned an identical complete result, confirming the default 10,000 replicates and seed 700. Inspection confirms families are resampled first, repetitions independently within each selected family/configuration block, and the same selected keys carry A, B, and both consumers together. Equal slot averaging implements the fixed family/configuration/repetition weights because `build_cells` requires their balanced shape.

Removing one A and one B observation from the nonconstant fixture retained all 144 planned applications and reported two unconfirmed observations. Conservative/favorable differences were 0.0694444444444444 and 0.0972222222222222; their width was exactly 2/72 within numerical tolerance. Missing compensation disabled the burden route. The supplied all-missing fixture retained its denominator and produced opposing adequacy bounds and gate results.

Two-family fixtures with positive observed A mean verified that zero-A bootstrap draws are retained. With one family having A=B=0 and the other A=2, B=1, the reduction interval was `[0, 0.5]`. Changing the first family to A=0, B=1 produced `[-infinity, 0.5]`. Thus neither unfavorable draws nor all-zero draws are discarded. The supplied tests also verified that actual zero A mean makes the burden route unavailable.

## Scope and outstanding verification

Numerical gates remain separate booleans; the helper does not approve a candidate and explicitly requires semantic, attribution, regression, distribution, and final-package evidence. Unknown compensation is not converted to zero. First-valid-attempt selection, blind adjudication, intervention eligibility, family regression investigation, and semantic acceptance correctly remain external evidence responsibilities; a nonblank evidence reference does not verify their substance.

Actual schedule completeness, substantive case mappings, trial adjudication, and experimental results were not audited. Bootstrap agreement verifies the declared empirical calculation, not population representativeness or semantic validity. The coordinating agent has announced plans to correct threshold comparisons, freeze the case-type mapping, and bind CLI inputs to schedule/mapping hashes; those subsequent changes are outside this unchanged-code review and are not credited as verified here.

## Follow-up verification of narrow fixes

Reviewed helper SHA-256 `3f3703640b6b1c9e8f4ad096766a0a683f7cecdad6099d3be165565a6b6dc847`, tests `0c13caf7aef9e96bc1fbd56e1a48c566dfc140bafbf0b7bc046b269f400ad9fd`, and `prepare_main.py` `c0ee12326c6e9e76b9c8590fb6cc21d505547d4a6b3c0f2bb38a2429d82bf794`. No source or experimental output was changed or inspected beyond the authorized source files.

All 13 supplied tests passed, including the exact A=5, B=4 regression and paired schedule deletion/hash check. The documented absolute `1e-12` tolerance corrects the reproduced 20% rejection and exact five-point cancellation. Values `1e-9` below either threshold remain rejected. Inspection confirms the interval lower-bound comparisons remain strictly greater than zero or −0.05, without that tolerance.

A separate synthetic CLI fixture confirmed that both digest arguments are mandatory, either incorrect digest rejects analysis, and correct inputs produce the exact-20% passing burden route with the default 10,000 replicates/seed 700. Substantive type reporting appears separately from ordinary/challenging slots.

The mapping validator rejects missing, duplicate, unexpected, or invalidly labelled family/variant entries. An independent fixture covering all three types and one missing A observation produced positive-type conservative/favorable differences 0.5/1, with failure/incomplete differences both 1. This verifies mapping use and preservation of missing slots within type bounds. Explicit subgroup application/missing counts are still absent from rendered tables; they should accompany the final report.

I executed schedule preparation only in a fresh temporary directory containing synthetic placeholder inputs. It produced 360 creator assignments, including 288 A/B assignments; `build_cells` recovered 12 families × 6 configurations × 2 paired repetitions, establishing 576 planned A/B applications. The independently calculated schedule digest matched the saved digest exactly. The immutable schedule omitted execution/status fields. Editing the synthetic execution ledger did not alter the schedule or digest; a repeat preparation was rejected. Removing an entire family symmetrically was rejected against the original digest.

The reproduced numerical defect is corrected, and the substantive-type and frozen-input mechanisms are implemented. No new material calculation error was found in these focused checks. Hash comparison establishes identity to the supplied digest, not when or how that digest was approved: complete schedule and mapping hashes still require the stated independently verified prospective checkpoints. Real preparation, checkpoint provenance, actual case classifications, and experimental observations remain unverified here.
