# Execution note: `release-checkout-service`

## Delivered files

- `deliverables/skills/release-checkout-service/SKILL.md`
- `deliverables/skills/release-checkout-service/references/release-tool.md`
- `deliverables/skills/release-checkout-service/agents/openai.yaml`

Disposable simulator states used by the checks remain under `verification/`; they are not part of the Skill or a demonstration deliverable. Supplied files under `input/` were not changed.

## Supplied authoring resources used

- `input/brief.md` was the source for the requested release purpose, exact candidate and environment scope, qualification and approval ordering, production checks, authorization boundary, uncertain-effect recovery, and reporting requirements.
- `input/release_tool.py` was inspected as the source for the simulator's arguments, state changes, JSON results, approval comparisons, request-id behavior, and exit codes.
- `../../common/agent-skills-format.md` supplied the common physical-format orientation.
- `../../frozen/skill-creator/SKILL.md` supplied the frozen authoring guidance. Its `references/openai_yaml.md` and `scripts/quick_validate.py` were used for host configuration and validation.
- `../../frozen/alps/skills/design-process-description/SKILL.md`, `references/process-framework.md`, `references/examples.md` (especially Production Release), and `references/SKILL-template.md` were used to state the Purpose, independent Outcomes, ordering constraints, evidence distinctions, and reporting conditions.
- `../../frozen/alps/skills/design-agent-work-system/SKILL.md`, `references/agent-work-system-design.md`, `references/examples.md`, and `../../frozen/alps/examples/README.md` were used to allocate contextual judgment to the agent, use the existing CLI directly, document its interface, and define incomplete-effect handling and evaluation limits.
- The official Agent Skills specification at `https://agentskills.io/specification` and script guide at `https://agentskills.io/skill-creation/using-scripts` were read on 2026-09-08. They confirmed the required frontmatter, relative references, progressive disclosure, optional directories, and that an existing command can be used directly without a bundled script.

Source reads were performed with `cat` and targeted `rg` commands from the task working directory. The used reads exited `0`. One initial case-sensitive heading search returned exit `1` with no output; a case-insensitive targeted search found the Production Release section and exited `0`. A `rg --files input` inventory exited `0` and returned only `input/brief.md` and `input/release_tool.py`.

## Key design choices

- The Skill defines success as the approved exact revision being in production, a healthy post-promotion probe for that revision, and a completed post-promotion checkout for that revision. Command completion is treated as evidence rather than success by itself.
- The agent retains contextual responsibility for request interpretation, authorization, exact candidate and environment identity, approval validity, result judgment, and reporting. The existing local Python CLI retains deterministic state processing and request recording.
- No wrapper or bundled script was added. The supplied CLI already exposes every required operation, including request status and idempotent retry. A wrapper would duplicate that interface without adding a needed capability.
- The detailed CLI contract is in one linked reference that the Skill requires before invocation. This keeps the main Process Description focused while preserving exit codes, state effects, exact approval fields, and retry conditions.
- Owner approval and user authorization are separate conditions. An existing passing qualification and valid subsequent approval are reused; unnecessary requalification is prohibited because it would invalidate the earlier approval basis.
- One request ID is retained across uncertain promotion responses. Status lookup precedes retry, and no second request ID is used to bypass uncertainty.
- `agents/openai.yaml` provides only requested-useful interface metadata. It declares no MCP dependency because the capability is a supplied local command, and it leaves implicit invocation at the default.

## Verification commands and observations

All shell commands below ran with `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/trials/focus-009` as the working directory.

### Physical-format validation

```console
$ python3 ../../frozen/skill-creator/scripts/quick_validate.py deliverables/skills/release-checkout-service
Skill is valid!
```

Exit code: `0`.

A final presence check ran:

```console
$ rg --files deliverables/skills/release-checkout-service && test -f execution-note.md
deliverables/skills/release-checkout-service/SKILL.md
deliverables/skills/release-checkout-service/agents/openai.yaml
deliverables/skills/release-checkout-service/references/release-tool.md
```

Exit code: `0`. The frozen validator was also rerun after the note was authored and again returned `Skill is valid!` with exit code `0`.

An earlier attempt to query that validator with `--help` was interpreted as a skill path:

```console
$ python3 ../../frozen/skill-creator/scripts/quick_validate.py --help
SKILL.md not found
```

Exit code: `1`. This was interface discovery, not a validation failure for the delivered Skill.

### Packaged-file and relative-link check

The inline standard-library Python check recursively listed the Skill's files and resolved local Markdown link targets relative to their source files:

```console
$ python3 - <<'PY'
from pathlib import Path
import re
root = Path('deliverables/skills/release-checkout-service')
files = sorted(p for p in root.rglob('*') if p.is_file())
missing = []
for source in files:
    if source.suffix != '.md':
        continue
    for target in re.findall(r'\[[^]]+\]\(([^)]+)\)', source.read_text(encoding='utf-8')):
        target = target.split('#', 1)[0]
        if target and '://' not in target and not (source.parent / target).exists():
            missing.append(f'{source}: {target}')
print('files:', ', '.join(str(p.relative_to(root)) for p in files))
print('relative markdown links:', 'OK' if not missing else '; '.join(missing))
raise SystemExit(bool(missing))
PY
files: SKILL.md, agents/openai.yaml, references/release-tool.md
relative markdown links: OK
```

Exit code: `0`.

### Timeout, status recovery, idempotency, and production evidence

The first promotion used a valid synthetic qualification and subsequent owner approval, with the simulator configured to time out once after changing state:

```console
$ python3 input/release_tool.py --state verification/timeout-state.json promote --candidate candidate-009 --request-id request-009
{"error": "response timeout; operation effect unconfirmed by this response", "request_id": "request-009"}
```

Exit code: `75`.

Status lookup with the same request ID established the effect:

```console
$ python3 input/release_tool.py --state verification/timeout-state.json request-status --request-id request-009
{"request_id": "request-009", "result": {"candidate": "candidate-009", "digest": "sha256:009", "promoted": true}}
```

Exit code: `0`.

The two post-promotion observations remained distinct:

```console
$ python3 input/release_tool.py --state verification/timeout-state.json probe
{"revision": {"id": "candidate-009", "digest": "sha256:009", "healthy": true, "checkout_ok": false}, "observation": "probe", "ok": true}
$ python3 input/release_tool.py --state verification/timeout-state.json checkout
{"revision": {"id": "candidate-009", "digest": "sha256:009", "healthy": true, "checkout_ok": false}, "observation": "checkout", "ok": false}
```

Exit codes: `0` for `probe`; `2` for `checkout`. This supports a healthy production judgment and an unmet checkout Outcome, not overall release success.

An exact retry with the same request ID returned the recorded success:

```console
$ python3 input/release_tool.py --state verification/timeout-state.json promote --candidate candidate-009 --request-id request-009
{"candidate": "candidate-009", "digest": "sha256:009", "promoted": true}
```

Exit code: `0`. A following `inspect` exited `0` and reported `promotion_count: 1`, showing that the retry did not duplicate the promotion.

### Requalification invalidates the older approval basis

The second synthetic state began with qualification sequence `1` and an approval for that sequence. Requalification created sequence `3`:

```console
$ python3 input/release_tool.py --state verification/requalification-state.json qualify --candidate candidate-009
{"candidate": "candidate-009", "digest": "sha256:009", "passed": true, "sequence": 3}
```

Exit code: `0`.

Promotion with the older approval was rejected:

```console
$ python3 input/release_tool.py --state verification/requalification-state.json promote --candidate candidate-009 --request-id requalify-request-009
{"error": "qualified candidate and subsequent matching owner approval required"}
```

Exit code: `2`.

## Verification limits and unperformed checks

- The supplied frozen validator checks physical form and frontmatter; it does not establish the quality of the release decisions an agent will make.
- The link check establishes that local target files exist. It does not validate Markdown rendering or host navigation to anchors.
- The simulator checks covered timeout-after-effect recovery, same-ID idempotency, separate health and checkout evidence, and invalidation by requalification. They used authored disposable states, not a supplied business application state, and do not cover every malformed-input or filesystem failure.
- No candidate, target environment mapping, user authorization, or service-owner action for an actual release instance was supplied. No actual release result was attempted or claimed.
- No live repository, deployment service, customer state, personal installation, external write, or message was accessed.
- The Skill was not loaded through a host UI, so `agents/openai.yaml` display behavior remains unconfirmed.
- No independent agent-mediated forward test was performed because delegation was explicitly prohibited for this task. Whole-system effectiveness beyond the examined simulator behaviors remains unconfirmed.
- The official `skills-ref` validator was not run; validation used the supplied frozen `quick_validate.py` and direct comparison with the official format requirements.
