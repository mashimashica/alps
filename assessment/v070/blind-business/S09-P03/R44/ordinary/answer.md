# Cedar Quay packing-check decision

## Recommendation: continue at Harbor for the next 20 full shifts

I recommend that Iona **continue Harbor's second-person check on every order for the next 20 full shifts**, with the current 68-productive-hour limit and 1% late-dispatch commitment as hard guardrails. Ridge should keep its usual process during this evidence period as the concurrent comparison. I do not recommend narrowing Harbor, stopping it, or expanding it across all Ridge shifts on this packet alone.

This is a recommendation, not an authorization to change operations, staffing, spending, communications, or records. Iona retains the decision.

## What the observations establish

Only mature cohorts are used for the seven-day customer outcome. The immature July 31 cohorts contribute no customer-outcome denominator. The six ordinary full shifts are used for labor and full-shift dispatch planning; the deliberately short July 31 shift is excluded from that capacity comparison.

| Period and line | Standard mispacks | Complex mispacks | Total mature mispacks | Planned-mix rate |
|---|---:|---:|---:|---:|
| Harbor baseline | 27 / 1,800 (1.500%) | 36 / 600 (6.000%) | 63 / 2,400 | 2.625% |
| Harbor pilot | 12 / 1,800 (0.667%) | 18 / 600 (3.000%) | 30 / 2,400 | 1.250% |
| Ridge baseline | 27 / 1,800 (1.500%) | 36 / 600 (6.000%) | 63 / 2,400 | 2.625% |
| Ridge pilot | 27 / 1,800 (1.500%) | 33 / 600 (5.500%) | 60 / 2,400 | 2.500% |

The observed Harbor change was **-1.375 percentage points**, while Ridge changed by **-0.125 points**. The descriptive difference-in-differences is therefore **-1.250 points**. The observed mix was already 75% standard and 25% complex, so standardizing to the planned mix does not change these aggregate rates.

Harbor's full-shift station catches rose from **13 / 2,400 orders (0.542%)** at baseline to **38 / 2,400 (1.583%)** during the pilot. These were issues corrected before dispatch and are kept separate from customer-confirmed downstream mispacks.

The measurements show that Harbor had fewer mature downstream mispacks while checking was in use, at both order bands. They do not establish that checking caused the entire reduction. Harbor volunteered, assignment was not randomized, there were only three mature pilot full shifts, and dates are clustered. The stable definitions, crews, recording, and Ridge comparison make continuation reasonable, but they do not remove those limits.

## Planned workload, labor, dispatch, and cost

The next period is **16,000 Harbor orders**: 800 orders per shift for 20 shifts, at the observed 75% / 25% mix.

| Planning scenario | Counterfactual mispacks | Expected mispacks at Harbor pilot rate | Expected avoided | Gross avoidable cost | Incremental labor cost | Modeled net advantage |
|---|---:|---:|---:|---:|---:|---:|
| Harbor's own 2.625% baseline | 420 | 200 | 220 | $10,560 | $1,920 | $8,640 |
| 2.500% baseline adjusted by Ridge's common change | 400 | 200 | 200 | $9,600 | $1,920 | $7,680 |

The comparison-adjusted scenario is the more conservative planning case: 2.625% plus Ridge's observed -0.125-point change gives a 2.500% counterfactual. Neither scenario is realized savings or a causal estimate. Both assume the observed rates carry into the next 16,000 orders.

Harbor averaged **62 routine productive hours per full shift at baseline** and **65 during the pilot**, after removing the three one-off training hours on July 20. The implied recurring increase is 3 hours per shift, or **60 hours over the period at $32 = $1,920**. The 65-hour projection fits below the 68-hour cap with 3 hours of headroom. It assumes labor scales proportionally at the same 800-order workload. Harbor also recorded an average of 5 overtime hours per pilot full shift; overtime is already included in productive hours and should not be added again.

Harbor late dispatch was **13 / 2,400 (0.542%)** on the three pilot full shifts, versus 14 / 2,400 (0.583%) at baseline. At the pilot rate, the planning translation is about **87 late orders out of 16,000**, below the period limit of 160. That is an extrapolation from three shifts, and no dollar value is assigned to it. For completeness, the short July 31 shift had 2 / 320 Harbor late orders; it is observable but is not a full-shift capacity test.

## Evidence-period operating scope and guardrails

- **Eligible population and assignment:** check every standard and complex Harbor order on all 20 full shifts. Ridge remains on its usual process for all 20 shifts as a descriptive concurrent comparison. This allocation is not randomized.
- **Staffing:** plan from 65 productive hours per Harbor shift, with no more than 68. Do not count the separately funded introductory training allowance as recurring capacity.
- **Measures:** preserve counts by date, line, and order band for shipped and mature orders, confirmed seven-day mispacks, and station catches; preserve line-date productive, overtime, training, and late-dispatch counts. Keep catches separate from downstream errors and wait seven calendar days before treating a cohort as mature.
- **Immediate guardrails:** do not exceed 68 productive hours on either line. If Harbor reaches the cap before all checks are complete, stop further checking for that shift, record the affected order count, and have Iona review before the next shift. Review cumulative late dispatch after every shift; if Harbor exceeds 1% of shipped orders period-to-date, suspend the check for the next shift and have Iona decide whether to stop or redesign it.
- **Review points:** after shift 10, review hours, overtime, station catches, and dispatch, while treating incomplete seven-day outcomes as immature. Make the final review seven calendar days after shift 20, when the last cohort is mature.
- **Question resolved:** can the all-order Harbor check sustain the planned volume and mix for 20 full shifts within 68 hours and the 1% service commitment, while retaining a comparison-adjusted quality improvement large enough to cover its additional labor cost? This follow-up improves precision and tests operating sustainability; because allocation remains nonrandom, it still will not prove causality or Ridge transferability.

If a guardrail fails, suspend Harbor checking pending Iona's review rather than assume an unmeasured selective variant will work. At the final review, continue beyond the period only if the quality/cost comparison remains favorable and both operating limits hold. A Ridge rollout should follow a separately approved, randomized or staggered Ridge trial; its labor, service, and quality effects are not observed here.

Stopping is weaker because Harbor's mature error count fell from 63 to 30 with no observed dispatch deterioration and with routine labor under the cap. Narrowing to complex orders is weaker because a selective version has not been measured and standard-order outcomes also improved. Full Ridge expansion is weaker because transferability and Ridge's incremental workload have not been observed.

The supplied analyzer's output is in `deliverables/numerical_basis.md`. From this task directory, reproduce it with:

```bash
bash deliverables/reproduce_analysis.sh
```
