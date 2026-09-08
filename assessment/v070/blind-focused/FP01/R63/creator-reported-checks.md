# Execution note

## Deliverable

Created the reusable Agent Skill at `deliverables/skills/confirm-handover-understanding/SKILL.md`. No demonstration or revised handover work product was created because the brief requests the Skill design only.

## Authoring resources used

- `input/brief.md`
- `prompt.md`
- `../../common/agent-skills-format.md`
- `../../frozen/skill-creator/SKILL.md`
- `../../frozen/skill-creator/scripts/quick_validate.py`
- `../../frozen/alps/skills/design-process-description/SKILL.md`
- `../../frozen/alps/skills/design-process-description/references/process-framework.md`
- `../../frozen/alps/skills/design-process-description/references/SKILL-template.md`
- `../../frozen/alps/skills/design-process-description/references/examples.md`, especially the cases for work without a fixed artifact, shared information, missing references, and Outputs that do not establish Outcomes
- The official Agent Skills specification at `https://agentskills.io/specification`, consulted on 2026-09-08 for the required folder, frontmatter, naming, description, and body rules

## Key design choices

- Used one self-contained `SKILL.md`; the workflow needs no deterministic helper, bundled asset, or substantial conditional reference.
- Defined observable Outcomes separately from the conversational Outputs, so a polished summary or read-back cannot be mistaken for shared understanding.
- Used evidence states that distinguish statements, accepted commitments, read-backs awaiting confirmation, confirmations, open or disputed items, and superseded statements.
- Kept work ownership, question ownership, approval authority, and evidence of completion separate.
- Made unresolved items a valid bounded result when no reply is available: the Skill must expose pending questions and their effects rather than manufacture closure.
- Required later corrections to revise affected conclusions and dependent judgments.
- Preserved a conversational interface; the Skill does not require a form, external messaging, audio processing, or task-system integration.

## Verification performed

All shell commands were run from `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/trials/focus-001`.

### Frozen format validator

Command:

```sh
python /workspace/scratch/a75c3a6d9076/alps-v070-assessment/frozen/skill-creator/scripts/quick_validate.py deliverables/skills/confirm-handover-understanding
```

Observed output:

```text
Skill is valid!
```

Exit code: `0`.

### Focused invariant check

Command:

```sh
python - <<'PY'
from pathlib import Path
p=Path('deliverables/skills/confirm-handover-understanding/SKILL.md')
s=p.read_text()
checks={
 'name_matches_folder': 'name: '+p.parent.name in s,
 'purpose_present': '\n## Purpose\n' in s,
 'outcomes_present': '\n## Outcomes\n' in s,
 'unknown_values_explicit': 'with missing values explicit' in s,
 'authority_distinguished': 'authority' in s.lower() and 'approval' in s.lower(),
 'readback_not_confirmation': 'read-back alone' in s,
 'silence_not_confirmation': 'from silence' in s,
 'later_corrections_reopen': 'reconsider dependent owners' in s,
 'no_scaffold_markers': not any(x in s for x in ('<lowercase-hyphen-name>', '<Why the work', 'TODO', 'TBD')),
}
for k,v in checks.items(): print(f'{k}={str(v).lower()}')
raise SystemExit(0 if all(checks.values()) else 1)
PY
```

Observed output:

```text
name_matches_folder=true
purpose_present=true
outcomes_present=true
unknown_values_explicit=true
authority_distinguished=true
readback_not_confirmation=true
silence_not_confirmation=true
later_corrections_reopen=true
no_scaffold_markers=true
```

Exit code: `0`.

### Size check

Command:

```sh
wc -l -w -c deliverables/skills/confirm-handover-understanding/SKILL.md
```

Observed output:

```text
83 1011 7035 deliverables/skills/confirm-handover-understanding/SKILL.md
```

Exit code: `0`.

### Official reference validator availability

Command:

```sh
if command -v skills-ref >/dev/null 2>&1; then skills-ref validate deliverables/skills/confirm-handover-understanding; else printf 'skills-ref: not installed\n'; exit 127; fi
```

Observed output:

```text
skills-ref: not installed
```

Exit code: `127`.

## Verification limits

- The supplied quick validator checks physical format, frontmatter, naming, and unfinished scaffold markers; it does not establish behavioral quality or successful handover outcomes.
- The official `skills-ref` executable was unavailable, so that validator was not run.
- No synthetic handover demonstration or forward behavioral trial was performed because the brief requests design only and does not request a demonstration. The invariant check therefore confirms selected instruction coverage, not how a future assistant will apply the Skill in every conversation.
- No live communication, operational work, task-system update, installation, upload, or other external action was performed.
