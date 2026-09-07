# Public execution note

Created the reusable Skill `deliverables/skills/operational-intervention-decision/SKILL.md` and the expressly requested packet decision in `deliverables/northbank/decision.md`, with `reproduce.py` and its `calculations.json` output. No production action, communication, installation, commit, or upload was performed. Durable saving is left to the parent.

## Resources used

- Task `prompt.md` and `input/brief.md`.
- All four named supplied source files in `input/sources/`: measurement and decision notes and the two CSVs.
- `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/common/agent-skills-format.md` for the physical format orientation.
- The optional frozen skill-creator aid was not read or used. No external sources, sibling trials, or other workspace resources were inspected. No delegation was used.

## Public commands and results

Every shell command used `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/trials/control-059` as its working directory.

| Command / operation | Observed output | Exit status |
|---|---|---|
| `cat prompt.md` | Task boundaries and artifact instructions | 0 |
| `cat input/brief.md /workspace/scratch/a75c3a6d9076/alps-v070-assessment/common/agent-skills-format.md && find input -maxdepth 2 -type f` | Brief, common orientation, and five input file paths | 0 |
| `cat input/sources/measurement_notes.md input/sources/decision_context.md input/sources/shipment_cohorts.csv input/sources/shift_operations.csv` | Supplied notes and full CSV contents | 0 |
| `mkdir -p deliverables/skills/operational-intervention-decision deliverables/northbank` | No stdout | 0 |
| `apply_patch` authoring operations | Successful creation of Skill, script, decision, and this note | Tool success; no shell exit code |
| `python3 deliverables/northbank/reproduce.py --sources input/sources > deliverables/northbank/calculations.json` | No terminal stdout; JSON created with validation status `passed`, 28 cohort rows and 14 shift rows | 0 |
| `cat deliverables/northbank/calculations.json` | Full aggregates and three planning comparisons; adjusted net $5,016.888888888892, East recurring pilot hours 234, next-period cap excess approximately 192 hours | 0 |
| `python3 deliverables/northbank/reproduce.py --help` | Usage with required `--sources` directory and help text | 0 |
| `python3 - <<'PY'` local validation block described below | `PASS: Skill frontmatter/name; 12,000 mature orders; East recurring hours, cap gap, and adjusted financial arithmetic.` | 0 |

The local validation block used only standard-library `json`, `re`, and `pathlib`. It split the Skill frontmatter, checked that its name matches its directory and the lowercase hyphenated format, checked name length ≤64 and nonempty description length ≤1,024, parsed the generated JSON, and asserted the reported source row counts, 12,000 mature orders, 234 East recurring hours, 192-hour planning gap (numeric tolerance 1e-8), and $5,016.888888888889 adjusted net (same tolerance). This was a narrow local format/arithmetic check, not the official validator or an independent statistical analysis.

## Design choices and limits

The Skill is self-contained and keeps packet-specific conclusions in a separate deliverable. Its workflow requires outcome maturity, stratum standardization, cautious attribution, native-grain labor, explicit cost baselines, capacity forecasting, and an actionable decision with interim operations. The demonstration uses a standard-library command with an explicit input path rather than adding dependencies. Sources were read but not edited.

The decision recommends stopping universal East checking for the coming period because observed recurring labor and lateness fail the operating plan, while acknowledging a favorable but uncertain quality/economic signal. Selective checking is treated as an untested candidate conditional on demonstrating staffing feasibility. The fallback includes immediate operational and later mature-outcome reviews.

Missing evidence includes band-specific labor, selective-check performance, validated throughput at 1,200 orders and 80/20 mix, the template's independent effect, credible parallel trends, and mature June 26 outcomes. Forecasts are scenarios and do not establish causal effects or guarantee dispatch. No formal significance test, prospective experiment, invalid-input test suite, official Skill validator, or live-system verification was performed. No claims of those checks are made.
