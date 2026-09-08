# Decision for the next twenty full shifts

**Recommendation to Nessa Vale: stop Alder’s second-person all-order packing check for the full twenty-shift period; keep Birch operating without a checker. Do not expand the process or substitute selective checking.** This is a recommendation only; no operating change has been made.

The all-order check is the only measured variant, and it fails the hard recurring-hours limit under the stated planning scenario. It also did not improve the mix-adjusted downstream mispack result and missed the dispatch commitment on comparable full shifts. Selective checking is not a feasible demonstrated alternative because its time, quality, and dispatch effects were not measured.

## What the outcome evidence supports

`shipment_cohorts.csv` is at date × line × order-band grain. Its key is unique. Mispack rates use confirmed distinct mispacked orders over mature orders with a completed seven-day window. The August 28 cohorts have zero mature orders and are excluded from outcome rates; their zero outcomes are not treated as evidence of zero risk. Counts are aggregated before rates are calculated.

| Line | Baseline standard | Baseline complex | Pilot standard | Pilot complex | Baseline at 70/30 | Pilot at 70/30 | Change |
|---|---:|---:|---:|---:|---:|---:|---:|
| Alder | 42/2,100 = 2.0% | 90/1,500 = 6.0% | 33/3,300 = 1.0% | 30/300 = 10.0% | 3.2% | 3.7% | **+0.5 pp** |
| Birch | 42/2,100 = 2.0% | 60/1,500 = 4.0% | 33/3,300 = 1.0% | 18/300 = 6.0% | 2.6% | 2.5% | **−0.1 pp** |

Alder’s raw rate fell from 132/3,600 (3.667%) to 63/3,600 (1.750%), but that comparison is distorted: complex orders fell from 41.7% of its mature baseline cohort to 8.3% of its mature pilot cohort. At the planned 70% standard / 30% complex mix, Alder instead rises from 3.2% to 3.7%. Birch’s contemporaneous standardized change is −0.1 percentage points, making the nonrandomized difference in changes **+0.6 percentage points against the Alder check**.

This is not causal proof. Alder began with a worse complex-order rate, allocation was voluntary, a complex account paused, and the common packing-list template and mandatory catch recording changed just before the pilot. The mature pilot includes only 300 complex orders per line, versus 8,640 planned complex orders per line, so that stratum is especially uncertain. Station catches are process observations with a changed recording rule; they cannot be combined with customer-confirmed mispacks or used as a consistent before/after outcome.

## Workload, staffing, and dispatch

`shift_operations.csv` is one row per date × line. Hours are counted once at that native grain. The table’s overtime and training fields are subsets of productive hours and were not added again. Alder’s five August 17 training hours were removed only when estimating recurring checker time. August 28 was a short, unusually simple 600-order shift and was kept out of the full-shift capacity comparison.

| Full-shift basis | Recurring minutes/order | Projection at 1,440 orders | Hard cap | Late dispatches on observed full shifts | 20-shift projection |
|---|---:|---:|---:|---:|---:|
| Alder with checker | 4.50 | **108.0 h/shift** | 102 h | 42/3,600 = **1.167%** | 336 late vs 288 maximum |
| Alder without checker, comparator-adjusted planning case | 4.20 | **100.8 h/shift** | 102 h | 0.583% planning rate | 168 late vs 288 maximum |
| Birch, current pilot-period operation | 4.10 | **98.4 h/shift** | 102 h | 18/3,600 = **0.500%** | 144 late vs 288 maximum |

The Alder no-check planning case starts with Alder’s baseline 4.10 minutes/order and adds Birch’s contemporaneous +0.10 minute/order change. Its 100.8-hour forecast fits, but with only 1.2 hours of headroom. The forecast assumes hours scale linearly with orders; labor is not recorded by band, and the planned mix differs materially from the observations, so it does not prove capacity. The checker case is already six hours over the cap under the same assumption. The capacity ceiling is 4.25 minutes/order.

Expanding all-order checking to Birch is therefore unsupported and, if Alder’s measured checker rate transported to Birch, would likewise require 108 recurring hours per shift. Up to five separately funded one-off training hours for a newly participating line would not raise the recurring 102-hour cap.

Alder’s full-shift checker sample also exceeds the commercial limit of 1% late dispatches. Adding the atypical short August 28 shift makes the full recorded pilot exactly 42/4,200 = 1.0%, but that short, simple shift does not establish full-shift delivery. Late dispatches are kept in operating units because no authorized dollar value exists.

## Twenty-shift economics for Alder

All scenarios use 28,800 planned Alder orders, the 70/30 mix, USD 55 per downstream mispack, and USD 34 per additional recurring labor hour. Negative errors avoided means the checker is forecast to create more downstream errors than the named no-check counterfactual.

| No-check counterfactual | No-check mispack rate | Errors avoided by checker | Gross avoidable-error value | Added checker labor cost | Net checker value |
|---|---:|---:|---:|---:|---:|
| Alder own baseline | 3.2% | −144.0 | −$7,920 | $6,528 | **−$14,448** |
| Current Birch | 2.5% | −345.6 | −$19,008 | $6,528 | **−$25,536** |
| Comparator-adjusted | 3.1% | −172.8 | −$9,504 | $4,896 | **−$14,400** |

The comparator-adjusted no-check rate is Alder’s 3.2% baseline plus Birch’s −0.1 percentage-point contemporaneous change. The corresponding labor case is Alder baseline plus Birch’s labor change. Under that case, the checker would need to prevent at least **89.0 errors, or 0.309 percentage points**, merely to cover its $4,896 incremental labor cost. That means a checker rate no higher than about **2.791%**, while the observed 70/30-standardized checker rate was 3.7%.

## Review and decision triggers

Further evidence is not needed to choose the next-period scope: the measured all-order process is infeasible under the hours cap, and no measured narrowing exists. Operate both lines without a second checker for the twenty shifts. Because the no-check Alder forecast has little labor margin, review productive hours and late dispatches after the first five full shifts, and review confirmed mispacks once those five cohorts have completed their seven-day windows. This monitoring asks whether Alder at the realized mix remains within 102 productive hours per shift and 1% late dispatches, and whether its mature mispack rate materially departs from the 3.1% comparator-adjusted planning value. It does not defer the stop decision. If early hours or dispatch breach a limit, keep the checker off because it consumes capacity and had worse full-shift dispatch; the authorized intervention choices cannot repair that broader production-plan shortfall.

Reconsider a redesigned check only if measured evidence at the planned mix shows all three conditions: no more than 4.25 recurring minutes/order, no more than 1% late dispatches, and enough causal quality improvement to cover its incremental labor cost (0.309 percentage points for the comparator-adjusted labor case). Until then, expansion and selective checking remain unsupported.

## Reproducible basis

Run:

```bash
python3 deliverables/reproduce_analysis.py
```

The script reads only `input/sources/shipment_cohorts.csv` and `input/sources/shift_operations.csv`, validates keys, coverage and count ranges, applies the mature-cohort and full-shift rules, and prints the rates, projections, economics, and break-even calculation. A captured run is in `deliverables/analysis_results.txt`.
