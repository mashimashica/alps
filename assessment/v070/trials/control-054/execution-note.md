# Execution note

## Outputs

- `deliverables/skills/operational-intervention-decision/`: reusable Skill with a deterministic CSV analysis script.
- `deliverables/decision.md`: packet-specific recommendation.
- `deliverables/decision-basis.md`: inspectable calculations, assumptions, exclusions, and reproduction command.

## Supplied resources used

- `input/brief.md`
- `input/sources/measurement_notes.md`
- `input/sources/decision_context.md`
- `input/sources/shipment_cohorts.csv`
- `input/sources/shift_operations.csv`
- `../../common/agent-skills-format.md`
- `../../frozen/skill-creator/SKILL.md`
- `../../frozen/skill-creator/scripts/quick_validate.py`

No external sources were used.

## Key design choices

- The Skill separates established descriptive measurements from suggestive nonrandomized contrasts and unknown performance of untested variants.
- The analyzer standardizes downstream rates to a supplied planned mix, excludes immature orders from downstream denominators, keeps line-level labor at line grain, separates training from ongoing hours, and labels difference-in-differences and proportional scaling as descriptive sensitivities.
- June 26 remains in shipped and maturity accounting but is excluded from the operations comparison through an explicit command option because the supplied context identifies it as a short low-volume shift rather than an ordinary full shift.
- The decision narrows the check to a bounded complex-order measurement period only behind the 84-hour staffing gate. It does not treat that untested scope as proven, and it makes dispatch and capacity stop conditions explicit.

## Checks performed

1. `python3 ../../frozen/skill-creator/scripts/quick_validate.py deliverables/skills/operational-intervention-decision`
   - Output: `Skill is valid!`
   - Exit code: 0
2. `python3 -m py_compile deliverables/skills/operational-intervention-decision/scripts/analyze_packet.py`
   - Output: none
   - Exit code: 0
3. `python3 deliverables/skills/operational-intervention-decision/scripts/analyze_packet.py --help`
   - Output: usage text listing positional files and all analysis options.
   - Exit code: 0
4. `python3 deliverables/skills/operational-intervention-decision/scripts/analyze_packet.py input/sources/shipment_cohorts.csv input/sources/shift_operations.csv --intervention-line East --control-line West --planned-mix standard=0.8,complex=0.2 --planned-orders-per-shift 1200 --shifts 20 --hour-cap 84 --avoidable-cost 65 --hour-cost 28 --exclude-operations-date 2026-06-26`
   - Output: the tables and sensitivities transcribed in `deliverables/decision-basis.md`, including 3.20% to 2.00% East standardized quality, a -0.65 percentage-point descriptive difference-in-differences, 1.97% East late dispatch on comparable pilot shifts, 12.82 observed versus 14.29 required orders/hour, and a 93.6-hour proportional sensitivity.
   - Exit code: 0
5. Invalid-input check using `--planned-mix standard=0.7,complex=0.2` with the remaining required arguments.
   - Output: `analyze_packet.py: error: argument --planned-mix: mix shares must be nonnegative and sum to 1`
   - Exit code: 2

## Limits and unperformed checks

- The physical Skill validator does not validate decision quality.
- No causal or statistical-significance claim was tested; the packet is nonrandomized and has concurrent changes.
- Future labor scaling and complex-only checker effort are unmeasured, so the report does not claim their capacity or savings as fact.
- No live operational change, external action, installation, commit, upload, or message was performed.
