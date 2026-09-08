# Decision memo: Alder packing check for the next 20 full shifts

## Recommendation

Nessa should **stop Alder’s all-order second-person packing check for the next 20 full shifts** and leave Birch on its current no-check process. Do not replace it with a standard-only or complex-only check: neither selective variant has measured time, quality, or dispatch performance.

This is the only measured-state recommendation whose planning scenarios stay within 102 productive hours while retaining all 1,440 planned orders per line per shift without adding a station, borrowing workers, or deferring orders. The evidence does not show that Alder’s check improved downstream quality, while the measured all-order process creates both a capacity risk and a dispatch miss at the relevant full-shift pace.

No operational change has been made. This is a recommendation; Nessa retains the decision and spending authority.

## What the measurements support

Only mature cohorts are used for seven-day mispacks. August 28 has 600 shipped orders per line but zero mature orders, so its zero outcomes are excluded. Operations are counted once per date and line; band rows are not used to duplicate labor or dispatch. Station catches are also excluded from the downstream outcome because catch recording changed on August 14 and catches and mispacks are different measures.

| Period and line | Standard mispacks | Complex mispacks | Raw total | Rate at the next-period 70% / 30% mix |
|---|---:|---:|---:|---:|
| Baseline, Alder | 42 / 2,100 = 2.0% | 90 / 1,500 = 6.0% | 132 / 3,600 = 3.667% | 3.2% |
| Baseline, Birch | 42 / 2,100 = 2.0% | 60 / 1,500 = 4.0% | 102 / 3,600 = 2.833% | 2.6% |
| Pilot, Alder, all-order check | 33 / 3,300 = 1.0% | 30 / 300 = 10.0% | 63 / 3,600 = 1.750% | 3.7% |
| Pilot, Birch, no check | 33 / 3,300 = 1.0% | 18 / 300 = 6.0% | 51 / 3,600 = 1.417% | 2.5% |

The raw Alder rate fell from 3.667% to 1.750%, but that comparison is distorted by the shift from 41.7% complex orders at baseline to 8.3% in the mature pilot. At the planned 70% / 30% mix, Alder instead moves from 3.2% to 3.7%. Birch moves from 2.6% to 2.5%. The difference in those changes is **+0.6 percentage points for Alder relative to Birch**, an adverse direction rather than evidence of benefit. Standard performance changed identically on both lines, from 2.0% to 1.0%; complex performance worsened on both and more on Alder.

That comparison is descriptive, not causal. Alder volunteered, started with worse complex performance, the complex account paused, and both lines received a new packing-list template on August 14. The mature pilot also contains only 300 complex orders per line. These facts prevent assigning the observed difference to the checker alone, but they provide no basis for claiming quality savings from continuing it.

## Workload, staffing, dispatch, and budget

The relevant capacity observations are the three ordinary 1,200-order full shifts in each period. August 28 was short and unusually simple, so it is context rather than evidence of full-shift capacity.

| Planning scenario for a 1,440-order full shift | Productive hours | Late dispatch over 20 shifts | Constraint result |
|---|---:|---:|---|
| Alder all-order check, scaled from 90 routine hours per 1,200 orders | 108.0 | 336, from 42 / 3,600 = 1.167% | Fails 102-hour cap; exceeds 288-order maximum |
| Alder no check, scaled from its 82-hour baseline | 98.4 | 168, from 21 / 3,600 = 0.583% | Planning scenario fits both limits |
| Alder no check with Birch’s common +2-hour period change applied | 100.8 | — | Planning scenario fits cap with 1.2 hours of headroom |
| Birch no check, scaled from its 82-hour pilot | 98.4 | 144, from 18 / 3,600 = 0.500% | Planning scenario fits both limits |

Alder’s checker shifts used 275 productive hours in total. The five August 17 training hours are a subset and are removed once, leaving 270 routine hours, or 90 per shift. Overtime remains in productive hours and is not subtracted. Scaling 90 / 1,200 to 1,440 gives 108 hours, six above the hard cap. Separate funding for training cannot repair that ongoing shortfall.

As a rough incremental-labor scenario, Alder rose by eight routine hours per 1,200 orders while no-check Birch rose by two. Treating the remaining six hours as associated with the check gives 7.2 additional hours per planned shift, 144 hours across the period, and **$4,896** at $34 per hour. This is a planning estimate, not an attributed saving.

For quality cost, 28,800 Alder orders at the planned mix produce these transparent scenarios:

- Alder’s mix-adjusted baseline rate of 3.2% implies 921.6 expected mispacks and **$50,688** at $55 each.
- Alder’s mix-adjusted pilot rate of 3.7% implies 1,065.6 expected mispacks and **$58,608**.
- A control-adjusted difference-in-changes scenario of +0.6 percentage points implies 172.8 additional expected mispacks and **$9,504** more cost. Confounding prevents treating this as a causal loss.

There is therefore no supported quality saving to offset the checker’s labor. Missed carrier cutoffs remain unpriced and are enforced directly through the 1% operating commitment.

## Early review and remaining uncertainty

The next workload of 1,440 orders at a 70% / 30% mix was not observed, so even the no-check capacity result is a projection rather than a proven capacity curve. Keep the no-check decision as the interim operating state and review the already-defined productive hours and late-dispatch counts after the first **three full shifts**. The question is whether each line actually remains at or below 102 productive hours and at or below 1% cumulative late dispatches at the new volume and mix. This monitoring adds no station or planned productive hours. If either limit is breached, Nessa should revisit the line workflow immediately; the current packet still does not authorize assuming that a selective check would solve it.

A future reconsideration of checking should require a bounded, pre-specified comparison with assignment within order band and direct minutes by band, plus mature seven-day outcomes and dispatch results. Until such a test has a staffing plan that fits the 102-hour cap, neither selective checking nor expansion to Birch should be treated as an implementable option.

## Reproduce the arithmetic

From the `C-U100` task directory, run:

```bash
python3 work/analyze.py input/sources
```

The script uses only the supplied CSV files and the Python standard library.
