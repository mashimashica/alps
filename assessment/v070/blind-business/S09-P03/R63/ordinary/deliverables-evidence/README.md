# Reproducing the numerical basis

Run this command from the `C-U105` task directory:

```bash
python skill/operational-intervention-decision/scripts/analyze_packet.py \
  input/sources \
  --planned-mix standard=0.75,complex=0.25 \
  --intervention-line Harbor \
  --control-line Ridge \
  --baseline-period baseline \
  --trial-period pilot \
  --ordinary-dates 2026-07-06,2026-07-07,2026-07-08,2026-07-20,2026-07-21,2026-07-22 \
  --output deliverables/numerical-basis.md
```

The command reads `input/sources/shipment_cohorts.csv` and
`input/sources/shift_operations.csv`. The six dates passed to
`--ordinary-dates` are the dates identified as ordinary full shifts in
`input/sources/measurement_notes.md`; July 31 is excluded because it was a
deliberately shorter 320-order shift. The planned weights come from
`input/sources/decision_context.md`.

The generated [numerical basis](numerical-basis.md) contains mature downstream
rates by band, planned-mix rates, the concurrent-control change, and ordinary
shift labor and dispatch summaries. The 20-shift cost scenario in the decision
memo applies the stated local cost assumptions to those generated figures.
