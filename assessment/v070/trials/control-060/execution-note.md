# Public execution note

Created a reusable Skill at `deliverables/skills/operational-intervention-decision/SKILL.md` and the expressly requested packet decision at `deliverables/decision.md`, with inspectable reproduction code `deliverables/reproduce.py` and generated `deliverables/calculations.json`.

All shell commands used `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/trials/control-060` as their working directory. Authored text and Python files were created with `apply_patch`; the JSON is generated calculation output. Supplied inputs were read only. No external actions, delegation, installation, commits, or uploads were performed.

## Resources used

- Task `prompt.md` and `input/brief.md`.
- Supplied `../../common/agent-skills-format.md` physical-format orientation.
- Both supplied CSVs and both supplied measurement/context Markdown documents in `input/sources/`.
- Python standard library and local shell. The optional frozen skill-creator resource was not used. No additional Agent Skills sources or browsing were used.

## Commands and observed results

1. `cat prompt.md` — exit 0; returned the scoped authoring and execution-note instructions.
2. A shell invocation containing `cat input/brief.md`, `cat ../../common/agent-skills-format.md`, and `rg --files input` on separate lines — exit 0; returned the brief, common format orientation, and five input file paths.
3. A shell invocation containing `cat input/sources/measurement_notes.md`, `cat input/sources/decision_context.md`, `cat input/sources/shipment_cohorts.csv`, and `cat input/sources/shift_operations.csv` on separate lines — exit 0; returned all four source files.
4. A shell invocation containing `python deliverables/reproduce.py > deliverables/calculations.json` and `python deliverables/reproduce.py --help` on separate lines — exit 0; produced JSON and displayed the usage, source-directory argument, and read-only/deterministic behavior. The subsequent independent subprocess check confirmed reproduction itself exits 0.
5. `cat deliverables/calculations.json` — exit 0; returned the generated observed counts, mature and standardized rates, labor and dispatch measures, and next-period scenarios. Principal results: 45 mature East pilot errors, 59 West; East ongoing pilot labor 234 hours; projected 93.6 East and 83.6 West hours per 1,200 orders; adjusted no-checker East 84.4 hours; site projected late rate 1.35%; illustrative adjusted avoided errors 156.444 and net value $5,016.889.
6. The following local verification command — exit 0. Output: `PASS: Skill frontmatter/name/body checks; deterministic reproduction; 9 numerical spot checks.` Then `Reproduction subprocess exit code: 0` and the four deliverable file paths listed above.

```bash
python - <<'PY'
import json, math, re, subprocess
from pathlib import Path
skill = Path('deliverables/skills/operational-intervention-decision/SKILL.md')
s = skill.read_text()
front = s.split('---', 2)[1]
name = re.search(r'^name: (.+)$', front, re.M).group(1)
description = re.search(r'^description: (.+)$', front, re.M).group(1)
assert name == skill.parent.name and len(name) <= 64
assert re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name)
assert 0 < len(description) <= 1024
assert s.startswith('---\n') and len(s.split('---', 2)[2].strip()) > 0
saved = Path('deliverables/calculations.json').read_text()
run = subprocess.run(['python', 'deliverables/reproduce.py'], capture_output=True, text=True)
assert run.returncode == 0, run.stderr
assert run.stdout == saved, 'Reproduction differs'
r = json.loads(saved)
checks = {'East errors': (r['observed']['East_pilot']['errors'], 45), 'West errors': (r['observed']['West_pilot']['errors'], 59), 'East ongoing hours': (r['observed']['East_pilot']['ongoing_hours'], 234), 'East projected hours': (r['observed']['East_pilot']['hours_for_1200'], 93.6), 'West projected hours': (r['observed']['West_pilot']['hours_for_1200'], 83.6), 'East adjusted no-check hours': (r['planning']['east_adjusted_no_checker_hours_per_shift'], 84.4), 'site late rate': (r['planning']['site_projected_late_rate'], 0.0135), 'avoided errors': (r['planning']['adjusted_avoided_errors'], 156.44444444444444), 'net USD': (r['planning']['adjusted_net_usd'], 5016.888888888889)}
for label, (actual, expected) in checks.items():
    assert math.isclose(actual, expected, rel_tol=1e-10), label
print('PASS: Skill frontmatter/name/body checks; deterministic reproduction; 9 numerical spot checks.')
print('Reproduction subprocess exit code:', run.returncode)
print('Files:', ', '.join(str(p) for p in sorted(Path('deliverables').rglob('*')) if p.is_file()))
PY
```

## Design choices and limits

The reusable Skill is self-contained and contains no Northbank numerical conclusion or dependency on the demonstration. It directs later users to validate units and maturity, standardize mix, expose counterfactual assumptions, and make a feasible decision with bounded review conditions. The demonstration script is deliberately outside the Skill and snapshot-specific, with documented help and clear input failures.

The decision recommends stopping routine East checking for the next period because continuation and expansion lack operational feasibility under the stated cap and promise. It preserves the plausible quality/economic benefit as an uncertainty, discloses that stopping also lacks proven capacity at the new workload, and sets an immediate operating review plus a lagged quality review. A selective check remains unmeasured and is not credited with invented savings.

Performed checks establish physical frontmatter properties, repeatability of the generated JSON, and selected arithmetic. This was not an official validator run or a complete YAML-parser validation. No held-out packet or runtime Skill activation was tested; no external source verification, statistical causal identification, negative-input test suite, or future workload/variant validation was performed. Material missing information includes band-level labor, the template's independent effect, a randomized counterfactual, target-mix full-shift capacity, and selective-check performance. No operational authority was exercised.
