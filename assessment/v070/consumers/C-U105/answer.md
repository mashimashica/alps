# Cedar Quay packing-check decision

**Recommendation to Iona Bell:** approve a bounded continuation of Harbor's
second-person check on **all orders for the next 20 full shifts**. Keep Ridge on
its usual process as the concurrent comparison during that period. Do not
expand to Ridge or narrow Harbor by order band yet. This recommendation fits
the observed labor ceiling and dispatch commitment, and the observed quality
change is large enough to justify another bounded period. It is not a permanent
adoption decision or proof that the check caused the improvement.

## Decision basis

The six ordinary full shifts each handled the planned 800 orders per line at
the future 75% standard / 25% complex mix. All outcome rates below use mature
orders only. The July 31 cohorts are excluded from downstream outcomes because
none had completed the seven-day window; they are not counted as zero-error
orders.

| Measure on ordinary full shifts | Harbor baseline | Harbor pilot | Ridge baseline | Ridge pilot |
|---|---:|---:|---:|---:|
| Confirmed 7-day mispacks | 63/2,400 (2.625%) | 30/2,400 (1.250%) | 63/2,400 (2.625%) | 60/2,400 (2.500%) |
| Station catches, kept separate from mispacks | 13/2,400 (0.542%) | 38/2,400 (1.583%) | 12/2,400 (0.500%) | 14/2,400 (0.583%) |
| Productive hours per shift | 62 | 66 including training; **65 recurring** | 62 | 62 |
| Overtime hours per shift, already included above | 2 | 5 | 2 | 2 |
| Late dispatches | 14/2,400 (0.583%) | 13/2,400 (0.542%) | 14/2,400 (0.583%) | 13/2,400 (0.542%) |

Harbor's mix-adjusted mature mispack rate fell 1.375 percentage points, from
2.625% to 1.250%. Ridge fell 0.125 points over the same periods. The descriptive
change-in-changes is therefore:

`(1.250% - 2.625%) - (2.500% - 2.625%) = -1.250 percentage points`.

Both bands moved in Harbor's favor. Standard orders changed from 1.500% to
0.667% at Harbor and stayed at 1.500% at Ridge. Complex orders changed from
6.000% to 3.000% at Harbor and from 6.000% to 5.500% at Ridge. The observed mix
already equals the next period's planned mix, so the raw aggregate and
planned-mix rate are the same.

Harbor's recurring pilot workload was 65 productive hours per full shift after
removing the three introductory training hours on July 20. That is three hours
above Harbor's baseline and three hours below the 68-hour hard limit. The
training was one-off and separately fundable, so it is excluded from the next
period's run rate. Overtime rose from two to five hours per shift; it is a subset
of productive time and has not been added again.

Dispatch did not deteriorate during the full-shift pilot: Harbor's 0.542% late
rate was below the 1% operating-period commitment. On the deliberately short
July 31 shift, Harbor had 2/320 late orders (0.625%); that observation is valid
for dispatch but is not a full-shift capacity test. No dollar value is assigned
to dispatch because the packet supplies none.

## Twenty-shift planning scenario

Use the concurrent-control result as a planning estimate, not realized savings:

| Calculation | Formula | Planning result |
|---|---|---:|
| Harbor orders | 20 shifts × 800 | 16,000 |
| Fewer downstream mispacks | 16,000 × 1.250% descriptive change-in-changes | 200 |
| Avoidable downstream cost | 200 × $48 | $9,600 |
| Additional recurring labor | 20 × (65 − 62) hours | 60 hours |
| Additional labor cost | 60 × $32 | $1,920 |
| Estimated net cost advantage | $9,600 − $1,920 | **$7,680** |

The labor costs $96 per shift. At $48 per downstream mispack, the break-even
improvement is 2 avoided mispacks per 800-order shift, or 0.250 percentage
points. The descriptive control-adjusted improvement is 1.250 points. If
Harbor's pilot dispatch rate merely repeated, about 87 of 16,000 orders would
be late, versus the 160-order maximum implied by 1%; this is a service scenario,
not a guarantee or a monetized benefit.

## Evidence status

**Establishes:** the packet directly supports the counts and rates above;
Harbor performed the all-order process at 65 recurring productive hours per
ordinary shift; full-shift late dispatch was below 1%; and station catches rose
while downstream mispacks fell. The structural checks found all required rows,
matched line/date records, valid count relationships, and no duplicate keys.

**Suggests:** the second-person check may account for a 1.250-point reduction
relative to Ridge, which would produce the planning economics above if it
persists. This is a quasi-experimental estimate. Harbor volunteered, line
assignment was not randomized, and only three mature full-shift pilot dates are
observed. The stable definitions, crews, and absence of reported concurrent
changes make Ridge informative but do not establish causality.

**Unknown:** whether the effect persists for 20 shifts; whether Ridge would
achieve the same effect and workload if expanded; the labor and effectiveness
of any selective check; and the calendar date when the future period's final
cohort matures. The future shift schedule was not supplied.

## Bounded follow-up and guardrails

- **Scope and interim operation:** Harbor checks every standard and complex
  order for 20 full shifts at 800 orders per shift and the planned 75% / 25%
  mix. Ridge remains unchanged. Keep cohort results separate by line, date, and
  band.
- **Staffing:** plan Harbor at the observed 65 recurring productive hours per
  shift. Never exceed 68 productive hours, borrow staff, or add a station. If a
  shift is forecast to exceed 68 hours, stop additional checks before the cap,
  record the affected orders and cause, and have Iona review scope before the
  next shift. Such a shift should be flagged in the analysis rather than treated
  as full adherence.
- **Immediate monitoring:** after each shift, record productive hours,
  overtime, station catches, and late orders. Track Harbor's cumulative late
  rate against the exact 1% commitment. Any cumulative breach triggers review
  before the next shift and blocks expansion.
- **Review points:** conduct an operational review after shift 5 using the
  immediate measures. Review mature outcome cohorts as each complete
  seven-calendar-day window elapses. Conduct the decision review only after the
  final shift's complete seven-day window has elapsed. The exact calendar date
  is final-shift date plus that maturity window and cannot be stated until the
  shift schedule is supplied.
- **Comparison method:** preserve Ridge as the contemporaneous control and use
  the same baseline-to-follow-up change-in-changes, stratified by order band.
  Label the estimate quasi-experimental because allocation remains
  nonrandomized.
- **Question resolved:** did Harbor sustain at least the 0.250-point
  control-adjusted break-even reduction while staying at or below 68 productive
  hours per shift and at or below 1% cumulative late dispatches? If yes, Iona
  has a stronger basis for permanent continuation and for designing a separate
  Ridge expansion test. If no, the next decision should be stop or a separately
  designed selective trial; this packet cannot claim that a narrowed version
  will save labor or preserve the effect.

Stopping now is weaker because it abandons a favorable observed quality,
capacity, service, and cost signal. Narrowing is weaker because both bands
improved and the packet contains no measured selective process or band-specific
labor. Expanding now is weaker because Ridge's checker workload and effect are
untested and losing the concurrent control would reduce the value of the next
20 shifts.

The locally reproducible arithmetic is in
[deliverables/numerical-basis.md](deliverables/numerical-basis.md), with the
exact command and date selection in [deliverables/README.md](deliverables/README.md).
