# Decision memo — Cedar Quay packing check

**Recommendation: expand the all-order second-person check to Ridge for a bounded 20-full-shift evidence period, while continuing it at Harbor. Do not narrow the check by order band.** This is a recommendation to Iona, not an operating change: no live action, spending, or communication has been performed.

The evidence is favorable enough to justify monitored expansion. Harbor's confirmed seven-day mispack rate fell materially after checking began, including in both order bands; Ridge showed little contemporaneous change. The observed design is non-randomized and covers only three mature full shifts per period, so it supports an association—not proof that the check caused the entire reduction. Expansion should therefore remain an evidence period rather than be treated as a permanent rollout.

## Observed evidence

Confirmed mispack rates use `confirmed_mispack_7d / mature_orders`:

| Line / band | Baseline, July 6–8 | Pilot, July 20–22 | Change |
|---|---:|---:|---:|
| Harbor — standard | 27 / 1,800 = 1.500% | 12 / 1,800 = 0.667% | −0.833 pp |
| Harbor — complex | 36 / 600 = 6.000% | 18 / 600 = 3.000% | −3.000 pp |
| Harbor — all | 63 / 2,400 = 2.625% | 30 / 2,400 = 1.250% | −1.375 pp |
| Ridge — standard | 27 / 1,800 = 1.500% | 27 / 1,800 = 1.500% | 0.000 pp |
| Ridge — complex | 36 / 600 = 6.000% | 33 / 600 = 5.500% | −0.500 pp |
| Ridge — all | 63 / 2,400 = 2.625% | 60 / 2,400 = 2.500% | −0.125 pp |

The comparison-adjusted change is therefore −1.250 percentage points: Harbor's −1.375 pp change minus Ridge's −0.125 pp contemporaneous change. This is a useful planning contrast, not a causal estimate guaranteed to repeat.

Process observations point in the same direction but are not downstream outcomes: on comparable full shifts, Harbor station catches rose from 13 / 2,400 (0.542%) to 38 / 2,400 (1.583%); Ridge moved from 12 / 2,400 (0.500%) to 14 / 2,400 (0.583%). These catches are kept separate from customer-confirmed mispacks.

July 31 is not used as a full-shift capacity comparison and contributes no customer-outcome rate. Its 640 shipped orders across both lines have zero mature orders because their seven-day window was unavailable at extraction—not because they had zero mispacks. Its dispatch result remains usable because dispatch is immediately observable.

## Workload, hours, and dispatch

The next period is 20 shifts × 800 orders = **16,000 orders per line**, or 32,000 total, at the same observed 75% standard / 25% complex mix.

Harbor averaged 62 productive hours per baseline full shift. Its pilot averaged 66 hours including the three one-off training hours on July 20; removing those expressly nonrecurring hours gives **65 recurring productive hours per shift**, an observed increment of 3 hours and 3 hours of headroom under the 68-hour cap. Overtime rose from 2 to 5 hours per full shift at Harbor, so the hours plan is feasible but tight enough to monitor. Ridge averaged 62 hours; applying Harbor's observed 3-hour recurring increment to Ridge gives a **planning assumption of 65 hours per shift**, also within the cap. Ridge's permitted three one-off training hours should be scheduled before the period with the separate funding described in the packet; it does not expand the recurring 68-hour limit. No extra station or borrowed staff is assumed.

Late dispatch on full shifts was 14 / 2,400 (0.583%) at Harbor before checking and 13 / 2,400 (0.542%) during the pilot. Ridge was also 13 / 2,400 (0.542%) during the pilot. Harbor's July 31 short shift recorded 2 / 320 (0.625%); Ridge recorded 1 / 320 (0.313%). There is no sign of dispatch deterioration in these observations. At the Harbor pilot full-shift rate, the planning projection is about **87 late orders per line out of 16,000**, below the commercial maximum of **160 per line (1%)**. No dollar value is assigned to late dispatch because none was authorized.

## Cost projection

The packet assumes **$48 per avoidable downstream mispacked order** and **$32 per additional productive labor hour**. The following is a projection, not realized or proven savings:

| Planning basis | Per line over 20 shifts | Both lines over 20 shifts |
|---|---:|---:|
| Comparison-adjusted reduction | 200 fewer mispacks | 400 fewer mispacks |
| Avoidable error cost | $9,600 | $19,200 |
| Additional labor | 60 hours | 120 hours |
| Additional labor cost | $1,920 | $3,840 |
| **Projected net benefit** | **$7,680** | **$15,360** |

Arithmetic per line: 16,000 × 1.250% = 200 projected avoided mispacks; 200 × $48 = $9,600; 20 × 3 added hours × $32 = $1,920; net = $7,680. As a sensitivity, Harbor's unadjusted pre/post reduction of 1.375 pp would imply 220 avoided mispacks and an $8,640 net per line. Ridge's actual benefit is unmeasured; extending Harbor's labor and quality response to Ridge is explicitly a planning assumption.

Narrowing to complex orders is not recommended now. Although the complex-band reduction was larger, standard orders also improved, and the packet has no measured selective process or band-specific labor savings. With the all-order version fitting the hours ceiling, narrowing would exchange observed coverage for unquantified capacity savings.

## Operating evidence plan

- **Interim scope:** check every Harbor and Ridge order for all 20 full shifts. Staff each line to a 65-hour planning level without exceeding 68 productive hours; keep training, overtime, and routine hours separately visible.
- **Measurement:** retain date/line/band shipment cohorts; calculate customer outcomes only after the complete seven-day window; log station catches separately; record operations once per date and line so hours are not duplicated across bands.
- **Checkpoint:** after shift 5, review productive hours and late dispatch, plus any cohorts that have matured by then. If Ridge cannot operate within 68 hours or the evidence forecasts more than 160 late orders for the period, Iona should review the Ridge expansion immediately; Harbor should continue meanwhile because its all-order process is the measured configuration.
- **Final review:** seven calendar days after shift 20, when the final cohorts are mature. Decide whether Ridge reproduces a meaningful reduction and whether each line remains within the hours cap and 1% dispatch commitment. That review resolves whether to make both-line checking routine, return Ridge to usual process, or design a separately measured selective version.

## Reproduction

Run from this task directory:

```bash
python3 deliverables/reproduce.py
```

The script reads the two supplied CSV files directly, aggregates shipment cohorts without counting catches as mispacks, aggregates operations at its native date/line grain, exposes immature cohorts, and prints the rates and planning arithmetic above.
