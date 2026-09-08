# Decision memo — Fenwick Audio Renewal packing check

**To:** Nessa Vale, site manager  
**Decision horizon:** the next 20 full shifts  
**Recommendation:** **Stop Alder's all-order second-person packing check for all 20 shifts. Keep Birch's current no-check process. Do not expand the check or substitute a selective check during this period.** This is an analysis and recommendation; Nessa retains the operating decision.

## Why this is the defensible scope

The pilot does not establish a quality benefit, and continuing it fails both hard operating tests under the stated planning assumptions.

The raw mature pilot rate looks better than baseline because the mature pilot was 91.7% standard orders, while the next period is planned at 70% standard / 30% complex. The relevant mix-adjusted result reverses that impression:

| Mature downstream outcome | Alder baseline | Alder pilot | Birch baseline | Birch pilot |
|---|---:|---:|---:|---:|
| Standard | 42/2,100 = 2.0% | 33/3,300 = 1.0% | 42/2,100 = 2.0% | 33/3,300 = 1.0% |
| Complex | 90/1,500 = 6.0% | 30/300 = 10.0% | 60/1,500 = 4.0% | 18/300 = 6.0% |
| Raw all-band rate | 132/3,600 = 3.667% | 63/3,600 = 1.750% | 102/3,600 = 2.833% | 51/3,600 = 1.417% |
| **70/30 adjusted rate** | **3.2%** | **3.7%** | **2.6%** | **2.5%** |

The adjusted calculation is `0.70 × standard rate + 0.30 × complex rate`. Alder changed by `3.7% − 3.2% = +0.5 percentage points`; Birch changed by `2.5% − 2.6% = −0.1 points`. The change-in-changes is therefore `+0.5 − (−0.1) = +0.6 percentage points`, adverse to checking. This is a **quasi-experimental estimate**, not a causal finding: allocation was voluntary, Alder began with worse complex-order performance, the customer mix changed, and both lines received the new packing-list template and catch-recording rule.

On the three ordinary 1,200-order pilot shifts, Alder used 91.67 productive hours per shift, or **90.0 ongoing hours after removing only the five one-off training hours**. Its immediately observable late-dispatch rate was `42/3,600 = 1.167%`. Birch used 82.0 hours and had `18/3,600 = 0.500%` late dispatches. Productive hours already include overtime and training, so neither subset is added again.

## Next-period planning scenarios

There will be `1,440 × 20 = 28,800` orders per line. Labor projections assume constant hours per order from the ordinary 1,200-order shifts; that is a planning scenario, not a validated capacity curve.

| Scenario | Productive hours per full shift | Position vs 102-hour cap | Late dispatch projection | Position vs 1% commitment |
|---|---:|---:|---:|---:|
| Alder continues all-order check | `90.0 × 1.2 = 108.0` | **6.0 hours over** | `1.167% × 28,800 = 336` | **48 over the maximum 288** |
| Alder stops, control-trend labor case | `(82 + 82 − 80) × 1.2 = 100.8` | 1.2 hours under | `0.583% × 28,800 = 168` | 120 under |
| Alder stops, baseline-only labor case | `82 × 1.2 = 98.4` | 3.6 hours under | same 168 baseline-rate case | 120 under |
| Birch remains without check | `82 × 1.2 = 98.4` | 3.6 hours under | `0.500% × 28,800 = 144` | 144 under |

The Alder stop labor scenario uses its baseline 82 hours plus Birch's contemporaneous two-hour increase, then scales by `1,440/1,200 = 1.2`. The stop dispatch scenario uses Alder's baseline 0.583% because Birch's ordinary-shift rate remained at 0.500%. These projections support planning but do not prove that the unobserved 1,440-order workload will perform this way. No new training hours are needed for the stop scope.

For an expected-cost comparison, the control-trend no-check quality counterfactual is `3.2% + (2.5% − 2.6%) = 3.1%`. Holding the planned mix and observed band rates constant:

| Twenty-shift Alder scenario | Expected mispacks | Expected mispack cost | Incremental check labor vs stop | Incremental labor cost |
|---|---:|---:|---:|---:|
| Continue all-order check | `3.7% × 28,800 = 1,065.6` | **$58,608** | **144.0 hours** | **$4,896** |
| Stop, control-trend counterfactual | `3.1% × 28,800 = 892.8` | **$49,104** | 0 | $0 |

The modeled continue-minus-stop difference is 172.8 additional mispacks (`$9,504`) plus 144 incremental labor hours (`$4,896`), or **$14,400 more expected cost**. The labor increment comes from the ordinary-shift change-in-changes: `[(90 − 82) − (82 − 80)] × 1.2 × 20 = 144 hours`. This dollar comparison depends on the nonrandom control-trend attribution and constant-rate scaling. Dispatch remains a separate constraint because no dollar value for missed cutoffs was authorized.

No separate dollar spending ceiling was supplied. The enforceable budget condition in the packet is the 102 productive-hour maximum per line per full shift; one-off training has separate funding, but the recommended stop scope requires none.

## Operating scope and review

- **Alder:** no second-person all-order check on the next 20 full shifts.
- **Birch:** continue without a checker. Do not expand the pilot.
- **Both lines:** retain the centrally required packing-list template and mandatory catch recording. Track station catches separately from downstream mispacks.
- **Workload and staffing:** plan 1,440 orders per line per shift at 70% standard / 30% complex, with no more than 102 productive hours on either line in any shift. Do not rely on borrowed labor, another station, deferred orders, or added staffing.
- **Near-term review:** at the end of shift 5, Nessa should review whether every shift stayed at or below 102 hours and whether cumulative late dispatch is at or below 1% on each line (no more than 72 of 7,200 planned orders). This resolves whether the thin modeled Alder headroom is holding at the new workload. A miss triggers reassessment of the feasible operating plan; it is not evidence in favor of restoring the checker.
- **Outcome review:** review downstream mispacks only after each cohort's complete seven-calendar-day window has elapsed. The final quality review is seven calendar days after shift 20's shipment date; the packet does not provide the future shift dates needed to state a calendar date.

Continuing is weaker because it projects above the hours cap and dispatch commitment and shows no measured quality gain. Expansion is weaker because Birch has no check experience, and adding the estimated six check hours per 1,200 orders to Birch's current run rate gives `(82 + 6) × 1.2 = 105.6` projected hours, also above the cap. Narrowing is not presently supportable: selective-check labor, quality, and dispatch effects are all unmeasured, and the records cannot recover time by order band. Under the conservative stop forecast, Alder has only 1.2 modeled hours of headroom per shift, so a selective process cannot be assumed to fit.

## What the packet establishes, suggests, and leaves unknown

**Establishes:** mature band counts and rates; the six ordinary shifts' hours and dispatch results; Alder's five one-off training hours; the hard 102-hour cap; the 1% dispatch commitment; and that the August 28 cohorts are immature rather than error-free. Structural checks found 28 cohort rows and 14 operation rows, unique keys, valid nonnegative integer counts, valid numerator/denominator relationships, both bands for every date-line, and matching date-line coverage across the two CSVs.

**Suggests:** the all-order check did not improve quality and may have worsened it relative to Birch; approximately six additional ongoing hours per 1,200 orders are attributable to checking; and stopping should fit the next workload with limited headroom. These are constrained by nonrandom assignment, concurrent changes, small complex-order pilot samples, and scaling from 1,200 to 1,440 orders.

**Unknown:** the independent effect of the template, the causal effect of checking, any selective variant's time or effectiveness, labor by order band, performance at 1,440 orders, and the final calendar maturity date. Station catches cannot fill these gaps: capture changed on August 14, and catches are upstream issues rather than downstream mispacks.

## Reproduce the arithmetic

From this task directory, run:

```bash
python deliverables/reproduce_decision.py
```

The script reads only the two supplied CSVs, runs structural checks, excludes immature cohorts from outcome rates, counts line-level labor once, and prints the calculations above. Its captured output is in `deliverables/reproduced_results.txt`. The supplied analyzer's independent basis is in `work/measurement_basis.md`.
