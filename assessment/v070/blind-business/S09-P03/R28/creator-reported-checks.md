# Public execution note

## Commands and observed results

All commands were run from the control-052 task directory. Supplied inputs were read without modification.

| Command/check | Result |
|---|---|
| `cat prompt.md` | Read the task requirements; exit 0. |
| `cat input/brief.md`, `cat ../../common/agent-skills-format.md`, and `find input -maxdepth 2 -type f -print` | Read the brief and common format orientation and confirmed the four supplied source files; exit 0. |
| `cat input/sources/measurement_notes.md`, `cat input/sources/decision_context.md`, and both CSVs | Read the supplied measurement definitions, operating context, and records; exit 0. |
| `cat ../../frozen/skill-creator/SKILL.md` | Used the frozen skill-authoring guidance; exit 0. |
| `python3 -m py_compile deliverables/skills/intervention-decision/scripts/analyze_packet.py` (before a small quoting correction) | Failed with exit 1 on an f-string quoting syntax error. The script was corrected before the final checks. |
| `python3 -m py_compile deliverables/skills/intervention-decision/scripts/analyze_packet.py` followed by the analyzer command in `northbank-decision.md` | Exit 0; printed `wrote deliverables/reproduction/numerical_basis.md`. |
| `python3 ../../frozen/skill-creator/scripts/quick_validate.py deliverables/skills/intervention-decision` | Printed `Skill is valid!`; exit 0. |

The analyzer output was inspected. It reports mature-only cohort rates, line-level operations aggregated once per date, full-shift labor using the 1,000-order cutoff supplied for this packet, and the band-weighted planning calculation. The generated trace includes 156.444 implied avoidable orders and USD 10,168.89 in avoidable-cost sensitivity under the supplied assumptions.

## Files produced

- `deliverables/skills/intervention-decision/SKILL.md` — reusable workflow.
- `deliverables/skills/intervention-decision/scripts/analyze_packet.py` — standard-library numerical trace with schema and value validation and configurable line/period labels.
- `deliverables/northbank-decision.md` — packet-specific operating recommendation and limitations.
- `deliverables/reproduction/numerical_basis.md` — generated inspectable arithmetic basis.

## Design choices and limits

The skill keeps downstream maturity, process-catch recording, line-level labor aggregation, mix changes, concurrent changes, dispatch limits, and capacity limits explicit. The packet recommendation stops the tested all-order East check for the next period because ordinary pilot shifts exceeded the 1% dispatch promise and the observed labor/volume evidence does not establish feasibility at the planned 1,200 orders per shift. A future complex-order-only trial is described only as a separately authorized, bounded evidence option; no savings or capacity for that unmeasured variant is presented as fact.

No browser search, live-system change, staffing change, external contact, spending, commit, push, or upload was performed. No independent agent forward-test was run. The checks above validate file form, script execution on this packet, and arithmetic output; they do not establish causal attribution, sampling uncertainty, or operational feasibility beyond the supplied observations.
