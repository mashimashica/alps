# Fenwick packing-check decision for Nessa Vale

## Decision

**Stop Alder's all-order second-person check for the next 20 full shifts, and do not expand it to Birch.** Keep the August 14 packing-list template and mandatory catch scanning on both lines. Run both lines with their ordinary crews and stations, with no checker training or added hours. Nessa Vale remains the decision owner; this recommendation does not change live operations.

This is a stop decision for the measured all-order process, not a claim that checking can never work. At the planned workload, that process fails the hard hours limit, missed the full-shift dispatch commitment in the pilot, and did not show a quality benefit after accounting for the changed order mix. A selective check is not ready to implement because neither its time nor its outcome has been measured.

## Workload and measurement basis

Each line is planned for 20 × 1,440 = **28,800 orders**: **20,160 standard** and **8,640 complex**. Site volume is 57,600 orders.

The shipment unit is one mutually exclusive date/line/order-band cohort. Its quality denominator is `mature_orders`; the August 28 cohorts have no mature orders and therefore no quality rate. The operations unit is one date/line row. I first summed the two shipment bands to date/line, then joined operations once on `(shipment_date, line)`, so labor and late orders are not duplicated across bands.

The primary outcome is customer-confirmed downstream mispack within seven days. Station catches remain a process measure: recording expanded on August 14 and catches can be resolved before dispatch, so they are not added to mispacks or used as comparable evidence of quality improvement.

## What the mature outcomes support

| Period and line | Observed mispacks | Standard | Complex | Rate standardized to 70% / 30% planned mix |
|---|---:|---:|---:|---:|
| Baseline Alder | 132 / 3,600 = 3.667% | 42 / 2,100 = 2.0% | 90 / 1,500 = 6.0% | 0.70×2.0% + 0.30×6.0% = **3.2%** |
| Baseline Birch | 102 / 3,600 = 2.833% | 42 / 2,100 = 2.0% | 60 / 1,500 = 4.0% | **2.6%** |
| Pilot Alder, all-check | 63 / 3,600 = 1.750% | 33 / 3,300 = 1.0% | 30 / 300 = 10.0% | **3.7%** |
| Pilot Birch, no-check | 51 / 3,600 = 1.417% | 33 / 3,300 = 1.0% | 18 / 300 = 6.0% | **2.5%** |

The attractive raw Alder change, 3.667% to 1.750%, does not survive adjustment for the pilot's unusually simple 91.7% standard / 8.3% complex mix. At the next period's 70% / 30% mix, Alder changes from 3.2% to 3.7%, or **+0.5 percentage point**. Birch changes from 2.6% to 2.5%, or **−0.1 point**. The descriptive difference-in-differences adjustment is therefore:

`(+0.5 point Alder change) − (−0.1 point Birch change) = +0.6 point`.

That adjustment is not causal proof. Alder volunteered, had a worse complex baseline, only 300 mature complex pilot orders were observed per line, the account pause changed mix, and the common template changed at the same time as catch recording. It does show that the packet supplies no defensible quality case for continuing or expanding all-order checking.

## Capacity, labor, cost, and dispatch

On the three ordinary 1,200-order pilot shifts, Alder used 275 productive hours. Five were one-off training, leaving **270 routine productive hours, or 90 per shift**. Overtime was 34 hours, but it is already a subset of productive time and is not added again. Alder's baseline was 246 / 3 = **82 hours per 1,200-order shift**.

Using constant hours per order strictly as a planning scenario:

- all-check Alder: `90 × 1,440 / 1,200 = 108 hours/shift`, **6 hours above** the 102-hour hard cap;
- no-check reference: `82 × 1,440 / 1,200 = 98.4 hours/shift`, 3.6 hours below the cap;
- checking increment: 9.6 hours/shift × $34 = **$326.40/shift**, or **$6,528 over 20 shifts**.

The 98.4- and 108-hour figures are scale scenarios, not measured full-shift capacity at 1,440 orders. Training has separate funding but does not increase the ongoing 102-hour ceiling. Alder is already trained; Birch could use five one-off training hours, but expansion would still fail the ongoing-hours scenario.

Dispatch also fails independently. Alder's ordinary pilot shifts had **42 late orders out of 3,600 = 1.167%**, above the 1% commitment. Holding that rate for planning gives 336 late orders in 28,800, versus a ceiling of 288. Birch remained at 18 / 3,600 = 0.5%. The August 28 result was 0 / 600 on each line, but that short shift had an unusually simple mix and is not evidence of full-shift service or capacity. No dollar value is assigned to lateness.

## Planning scenarios, not forecasts

If Alder's all-check pilot segment rates persisted at the planned mix, the result would be `28,800 × 3.7% = 1,065.6` expected mispacked orders, with an associated expected error cost of **$58,608**.

A descriptive no-check reference preserves Alder's baseline 0.6-point disadvantage to Birch and adds it to Birch's post-template 2.5% rate: `2.5% + 0.6% = 3.1%`. That gives `28,800 × 3.1% = 892.8` mispacks and **$49,104** of error cost. Sensitivity references are 720 mispacks at Birch's 2.5% pilot rate and 921.6 at Alder's 3.2% baseline rate. There is no observed post-template Alder no-check cohort, so 892.8 is a planning estimate rather than a promised result.

Fully attributing the 0.6-point difference-in-differences contrast to checking would imply 172.8 additional mispacks and $9,504 of additional error cost under all-checking. Because allocation and concurrent changes were confounded, that is only a sensitivity calculation. It is **not** a savings claim for stopping. The decision is supported without that attribution because all-checking already violates the hard capacity scenario and observed dispatch constraint.

## Options considered

| Option for the 20 shifts | Quality evidence | Hours, cost, and service | Decision |
|---|---|---|---|
| Continue Alder all-check | 3.7% planned-mix scenario; no supported improvement | 108-hour scenario exceeds cap; $6,528 added labor; observed full-shift late rate 1.167% | **Reject** |
| Expand all-check to Birch | No measured Birch checking outcome | About 108 hours if the observed eight-hour checking increment is carried over and scaled; five training hours do not solve ongoing cap | **Reject** |
| Narrow to a band | No selective quality effect or band-level time was recorded | Cannot establish fit within 102 hours or ≤1% late; any cost estimate would be invented | **Do not implement** |
| Stop Alder all-check; leave Birch unchanged | No-check Alder central planning reference 3.1%, with 2.5%–3.2% sensitivity references | 98.4-hour planning scenario; no checking increment; prior no-check dispatch reference 0.583% on Alder and 0.5% on Birch | **Select** |

## Bounded follow-up while the stop decision runs

Use the 20-shift period to establish the missing post-template Alder no-check reference; do not defer the operating decision while collecting it.

- **Scope:** 20 ordinary full shifts on both Alder and Birch, 1,440 orders per line per shift at the planned 70% / 30% mix. No second-person check on either line.
- **Staffing and budget:** existing line crews and stations; no borrowed workers, added stations, training, or checker hours; maximum 102 productive hours per line per shift; training budget used: zero.
- **Controls held fixed:** packing-list template, order-band definitions, seven-day outcome definition, customer reporting, and mandatory catch scanning.
- **Primary outcome:** `confirmed_mispack_7d / mature_orders`, reported by line and band and standardized to 70% / 30%. Do not pool immature cohorts or catches into this outcome.
- **Process and service measures:** station catches reported separately, productive hours, overtime as a subset, and late dispatches / shipped orders by line.
- **Question:** with the same post-template no-check process and planned mix, does Alder retain a quality disadvantage to Birch beyond the baseline 0.6 point, and does either line meet the hours and ≤1% late conditions?
- **Review:** an interim review once five full-shift cohorts have completed seven calendar days; final review on the eighth calendar day after the twentieth shift, when all cohorts are mature.
- **Escalation triggers:** Nessa reviews immediately if a line reaches or is forecast to exceed 102 productive hours in a shift, its cumulative late rate exceeds 1%, or—after at least five mature shifts—Alder's 70% / 30% standardized mispack rate exceeds both 3.7% and Birch's concurrent rate by more than 0.6 point. A trigger does not automatically restart the infeasible all-order check; it requires a new, capacity-compliant decision.

If the follow-up later supports testing a selective process, it needs a separately scoped trial with measured band-level checking time and a pre-set 102-hour stop rule. The present packet cannot support selective-check savings, capacity, or quality claims.

Arithmetic is reproducible locally with `python3 deliverables/reproduce_decision.py`.
