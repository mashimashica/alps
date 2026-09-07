# Execution note

## Outputs

- Skill: `deliverables/skills/operational-intervention-decision/SKILL.md`
- Packet decision and arithmetic: `deliverables/northbank-decision/decision.md`
- Reproduction script: `deliverables/northbank-decision/reproduce.py`

## Public checks performed

All commands below were run from the control-051 task directory.

1. `python deliverables/northbank-decision/reproduce.py`
   - Exit code: `0`
   - Observed: mature quality totals were East baseline `132/3000 (4.400%)`, East pilot `45/3000 (1.500%)`, West baseline `120/3000 (4.000%)`, and West pilot `59/3000 (1.967%)`.
   - Observed: ordinary-shift operations were East baseline `207.0` hours and `15/3000` late, East pilot `238.0` hours and `59/3000` late, West baseline `205.0` hours and `17/3000` late, and West pilot `209.0` hours and `22/3000` late.
   - Observed: the planned-mix incremental contrast printed as `-0.652%`, with a 24,000-order scenario of `156.4` avoided orders, `$10,168.89` quality cost, `$5,040.00` added labor cost, and a `93.6` hour linear 1,200-order scenario against the `84.0` hour limit.

2. `python deliverables/northbank-decision/reproduce.py --help`
   - Exit code: `0`
   - Observed: help listed `--shipment` and `--operations` overrides and described the script.

3. `python /workspace/scratch/a75c3a6d9076/alps-v070-assessment/frozen/skill-creator/scripts/quick_validate.py deliverables/skills/operational-intervention-decision`
   - Exit code: `0`
   - Observed: `Skill is valid!`

4. `python -m py_compile deliverables/northbank-decision/reproduce.py`
   - Exit code: `0`.
   - The temporary `__pycache__` produced by this check was removed afterward.

## Supplied resources used

- `input/brief.md`
- `input/sources/measurement_notes.md`
- `input/sources/decision_context.md`
- `input/sources/shipment_cohorts.csv`
- `input/sources/shift_operations.csv`
- `common/agent-skills-format.md`
- Frozen authoring guidance at `frozen/skill-creator/SKILL.md`
- Frozen validator at `frozen/skill-creator/scripts/quick_validate.py`

## Design choices and limits

The Skill separates mature downstream outcomes from process catches, keeps line-date operations from being double-counted across order bands, standardizes by planned mix, and requires capacity, cutoff, cost, and confounding analysis before choosing continue, narrow, expand, or stop. The decision packet recommends ending the all-order East check and offers a five-shift complex-only test with explicit hours, dispatch, maturity, and fallback conditions. The selective variant is unmeasured here; its quality, savings, and capacity are clearly labeled as hypotheses. June 26 is excluded from mature quality and ordinary full-shift capacity comparisons because its observation window is open and its volume is short-shift. No external actions, live changes, or source edits were performed.

No statistical inference beyond descriptive rates, planned-mix standardization, and a cautious concurrent difference was required or performed. The script does not estimate confidence intervals or causal effects. The deliverables do not establish that the checker caused the observed change, and no dollar value was assigned to late dispatches because the packet supplied none.
