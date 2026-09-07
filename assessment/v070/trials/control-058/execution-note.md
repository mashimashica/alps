# Public execution note

Created `deliverables/skills/operational-intervention-decision/SKILL.md`, a reusable packet-driven Skill, and the requested packet decision in `deliverables/decision.md` with numerical reproduction in `deliverables/reproduce.py`.

Resources used: task `prompt.md`, `input/brief.md`, both input CSVs, both measurement/context Markdown files and the supplied `../../common/agent-skills-format.md`. The optional frozen skill-creator was not used. No external sources, other trials, personal installation or live operations were accessed.

Public commands, all run from this task directory:

- `cat prompt.md` — exit 0; returned task boundaries and output requirements.
- `cat input/brief.md && cat ../../common/agent-skills-format.md && find input -type f` — exit 0; returned brief, physical-format orientation and five input paths.
- `cat input/sources/measurement_notes.md input/sources/decision_context.md input/sources/shipment_cohorts.csv input/sources/shift_operations.csv` — exit 0; read the authorized packet.
- `python deliverables/reproduce.py` — exit 0; assertions passed. Output established East standardized quality 3.2% → 2.0%, West 3.0% → 2.45185%; East pilot recurring hours 234/3,000 orders and projected 93.6 hours/shift; economic net scenarios $12,672, $5,016.89 and $1,448.89.
- `python -c "from pathlib import Path; p=Path('deliverables/skills/operational-intervention-decision/SKILL.md'); s=p.read_text(); f=s.split('---')[1]; fields=dict(x.split(': ',1) for x in f.strip().splitlines()); assert fields['name']==p.parent.name; assert 0<len(fields['description'])<=1024; assert len(fields['name'])<=64; print('Skill frontmatter checks passed'); compile(Path('deliverables/reproduce.py').read_text(), 'reproduce.py', 'exec'); print('Python syntax check passed')"` — exit 0; printed `Skill frontmatter checks passed` and `Python syntax check passed`.

Authored files were created using apply_patch. Design choices: keep reusable instructions separate from the case decision; use a transparent standard-library calculation script; exclude immature cohorts only for delayed quality; do not join line hours onto band rows; distinguish fixed-mix estimates, comparator sensitivities and causality; recommend stopping universal checking because ongoing capacity and dispatch constraints outweigh conditional financial promise. Follow-up has a bounded operating review and a later mature-quality review.

Limits: no observed selective-check workload, no band-specific labor, no independent template effect, no randomized causal estimate and no guaranteed next-period volume/mix. No formal statistical inference, official format-validator execution, live operational test or production action was performed. Script assertions are local data checks, not verification of the fictional records' real-world accuracy.
