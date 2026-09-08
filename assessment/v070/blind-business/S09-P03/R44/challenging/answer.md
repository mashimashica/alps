# Decision for Fenwick's next 20 full shifts

## Recommendation

**Stop Alder's all-order second-person packing check for the next 20 full shifts and do not expand it to Birch.** Nessa Vale retains the operating decision. This recommendation does not authorize a staffing, production, spending, communication, or record change.

The measured all-order process misses two hard operating conditions when carried into the planned workload, and the quality results do not offset that problem:

- **Capacity:** Alder's three ordinary pilot shifts used 90 routine productive hours per 1,200 orders after removing the five one-off training hours. Proportional scaling to 1,440 orders gives **108 hours per shift**, which is **6 hours above the 102-hour hard cap**. Alder's baseline scales to 98.4 hours, leaving 3.6 hours of headroom.
- **Dispatch:** On Alder's ordinary pilot shifts, **42 of 3,600 orders were late (1.167%)**, above the 1% commitment. Alder's baseline was 21 of 3,600 (0.583%); concurrent Birch remained at 18 of 3,600 (0.500%) in both periods. If the observed pilot rate carried into the next 28,800 orders, it would imply 336 late orders, versus a maximum of 288. This is a rate-transfer scenario, not a guarantee.
- **Quality:** At the planned 70% standard / 30% complex mix, Alder's mature seven-day mispack rate standardizes to **3.7% in the pilot**, compared with **3.2% in its own baseline**. Birch changed from 2.6% to 2.5%; applying that common change to Alder gives a second counterfactual of **3.1%**. The descriptive difference-in-differences is therefore **+0.6 percentage points**, unfavorable to Alder's pilot.
- **Cost:** At 28,800 orders per line, transferring the standardized rates gives 1,065.6 expected pilot mispacks, versus 921.6 under Alder's own baseline or 892.8 under the common-change counterfactual. That is **144.0 to 172.8 additional mispacks**, or **$7,920 to $9,504 in additional avoidable-error cost** at $55 each. Proportional scaling also adds 192 labor hours over the period versus baseline, costing **$6,528** at $34 per hour. Combined, the all-order pilot is **$14,448 to $16,032 unfavorable** in these planning scenarios. Missed carrier cutoffs have no authorized dollar value and are kept outside this calculation.

## What the measurements establish

The delayed quality calculation uses only mature cohorts. August 28 contributes no seven-day outcome evidence because all 1,200 orders across both lines were immature. The mature counts are:

| Period | Line | Standard | Complex | Total |
|---|---|---|---|---|
| Baseline | Alder | 42 / 2,100 (2.0%) | 90 / 1,500 (6.0%) | 132 / 3,600 (3.667%) |
| Pilot | Alder | 33 / 3,300 (1.0%) | 30 / 300 (10.0%) | 63 / 3,600 (1.750%) |
| Baseline | Birch | 42 / 2,100 (2.0%) | 60 / 1,500 (4.0%) | 102 / 3,600 (2.833%) |
| Pilot | Birch | 33 / 3,300 (1.0%) | 18 / 300 (6.0%) | 51 / 3,600 (1.417%) |

The crude total rates fell on both lines, but the pilot contained only 8.3% complex orders among mature shipments, while the next period is planned at 30%. The planned-mix standardization therefore gives the more relevant planning comparison:

| Line | Baseline | Pilot | Change |
|---|---:|---:|---:|
| Alder | 3.2% | 3.7% | +0.5 pp |
| Birch | 2.6% | 2.5% | -0.1 pp |

Station catches are not combined with downstream errors. Their recording changed on August 14, so before/after catch counts are not comparable evidence of benefit.

## Limits on interpretation

The pilot does not establish that the checker caused the observed quality or dispatch changes. Alder volunteered, assignment was not random, Alder began with worse complex-order quality, complex volume changed sharply, and a packing-list template changed on both lines at the same time as mandatory catch recording. The pilot's complex stratum is only 300 mature orders on three clustered dates per line. The standardized rates, common-change counterfactual, and difference-in-differences are descriptive planning evidence.

The labor forecast assumes hours scale directly with orders. It is not a validated capacity curve, but it is the only supported projection and it fails the cap by a material margin. August 28 is excluded from full-shift capacity because it was a short, unusually simple 600-order shift. Overtime is already included in productive hours and cannot be treated as extra capacity. The five training hours are one-off and excluded from ongoing Alder pilot workload.

## Scope and rejected alternatives

- **Continue all-order checking at Alder:** rejected because projected workload exceeds the hard cap, observed dispatch misses the service commitment, and the planned-mix quality scenarios are unfavorable.
- **Expand to Birch:** rejected because the only measured variant is the infeasible all-order process and there is no measured quality benefit to justify adding it. Birch's permitted five training hours would not raise its ongoing 102-hour cap.
- **Narrow to selected orders:** not recommended for this operating period. A simple proportional calculation suggests Alder has room for about 540 checks per shift, but the records contain no check time by band and no measured quality or dispatch effect for selective checking. That figure is capacity arithmetic, not an observed or validated operating design.

No further evidence is needed to decide the next 20 shifts: the measured all-order variant should stop. Before any later selective-check proposal, Fenwick would need a separately authorized, bounded study that establishes per-band check time, randomized or otherwise balanced assignment, mature seven-day mispacks by band, late dispatches, and compliance with the 102-hour and 1% guardrails. Until such evidence is reviewed, the operating recommendation remains no second-person check on either line.

## Reproduce the arithmetic

The supplied analyzer was run against the authoritative local packet. Its full output is in `deliverables/analyzer-report.md`.

```bash
python skill/operational-intervention-decision/scripts/analyze_packet.py \
  --shipments input/sources/shipment_cohorts.csv \
  --operations input/sources/shift_operations.csv \
  --baseline-label baseline \
  --pilot-label pilot \
  --treated-line Alder \
  --comparison-line Birch \
  --full-shift-dates 2026-08-03,2026-08-04,2026-08-05,2026-08-17,2026-08-18,2026-08-19 \
  --planned-mix standard=0.7,complex=0.3 \
  --planned-orders-per-shift 1440 \
  --planned-shifts 20 \
  --productive-hour-cap 102 \
  --hourly-cost 34 \
  --avoidable-event-cost 55
```

**Compact basis:** stop Alder all-order checking and do not expand; planned-mix pilot quality 3.7% versus 3.2% own-baseline and 3.1% common-change counterfactual; projected 108 hours per shift versus the 102-hour cap; observed pilot late dispatch 1.167% versus the 1% commitment; modeled total disadvantage $14,448 to $16,032 over 20 shifts.
