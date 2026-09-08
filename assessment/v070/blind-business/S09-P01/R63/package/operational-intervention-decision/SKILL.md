---
name: operational-intervention-decision
description: Decide whether to continue, narrow, expand, or stop an operational intervention using a local measurement packet, operating constraints, and planning assumptions. Use when cohort maturity, mix changes, comparison groups, labor, capacity, timing, or cost can materially alter the decision.
---

# Operational intervention decision

Turn the supplied packet into a decision the named owner can use for the stated operating horizon. Treat the packet as the authority for definitions, permissions, limits, and planning assumptions. Do not replace missing local assumptions with web research or take live operational action unless separately authorized.

## Frame the decision

Identify the decision owner, horizon, available options, success criteria, hard constraints, planned volume and mix, authorized costs, and current intervention scope. State which constraints eliminate an option before considering its apparent benefit. Keep hard commitments, objectives, and descriptive metrics distinct.

Map each source before calculating: row grain, numerator, denominator, units, timing or maturity rule, overlapping fields, recording changes, and join keys. Preserve source files. Flag incomplete outcome windows and exclude them from matured outcomes; a zero with an open window is not evidence of no errors. Never add upstream catches to downstream failures unless the packet explicitly defines them as the same outcome. Avoid duplicating line-level measures when joining them to band-level rows.

## Build the numerical basis

Read [references/decision-method.md](references/decision-method.md) for the calculation and interpretation rules. If the packet matches the documented CSV contract, run:

```bash
python3 scripts/analyze_packet.py --help
```

Then invoke it with the packet paths, intervention and comparison lines, decision mix, ordinary-shift dates, horizon, volume, and authorized cost assumptions. Save its JSON output beside the decision work product so another operator can inspect and rerun the arithmetic. If the schema differs, reproduce the same invariants with local tools and document the exact command or calculation.

At minimum, calculate:

- mature outcome counts and rates by period, line, and decision-relevant stratum;
- rates standardized to the next-period mix, alongside raw totals when mix changed;
- within-line changes and a contemporaneous or difference-in-differences contrast when a comparison exists;
- ordinary-shift labor, dispatch performance, training treatment, and planned-volume capacity;
- expected consequence counts and authorized dollars under visible workload and effect assumptions; and
- uncertainty or sensitivity sufficient to show whether the recommendation depends on a fragile point estimate.

Treat non-random comparisons and before/after contrasts as descriptive. A control exposed to common changes can reduce some ambiguity, but it does not make assignment random. Use station or process catches as supporting context when their recording is comparable; do not substitute them for the stated downstream outcome.

## Make the decision

Separate the evidence into three classes:

- **Establishes:** direct arithmetic, maturity, constraint breaches, and observed operating facts supported by the packet.
- **Suggests:** directional or planning estimates that depend on non-random comparison, extrapolation, or assumed unit effort.
- **Unknown:** effects that the design, sample, recording change, or open outcome window cannot resolve.

Compare feasible options on downstream outcome, dispatch, workload, capacity, and authorized costs. Do not invent a dollar value for an unpriced consequence. Do not call an unmeasured selective variant proven or assign it observed savings. Expansion needs evidence that the intervention itself likely helped and that the receiving operation can meet its constraints.

Give one primary recommendation for the stated horizon. Name the scope, what runs in the meantime, and why rejected options fail. A conditional recommendation must use observable gates and say who retains the decision. If follow-up is useful, define its scope, staffing limit, ordinary operating conditions, exposure, outcome maturity date, review point, question, and predeclared action at each result. Do not defer the entire decision to more data.

## Deliver the handoff

Provide a concise decision document with:

1. the recommendation and operating instruction proposed to the decision owner;
2. the decisive evidence and constraint checks;
3. an inspectable comparison table with counts, denominators, rates, and units;
4. cost and capacity assumptions with sensitivity;
5. what the evidence establishes, suggests, and cannot establish;
6. the bounded follow-up and decision gates, if any; and
7. the exact local reproduction command and output path.

Make clear that the document is a recommendation unless the user has authority and explicitly asks to implement it.
