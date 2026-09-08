# Public execution note

## Outputs

Created the reusable three-file Skill at `deliverables/skills/checkout-service-release/`:

- `SKILL.md`: applicability description and release decision workflow.
- `assets/release-context.template.json`: per-application input and authorization record.
- `references/interface.md`: existing command connection, state evidence and error/retry semantics.

No separate demonstration was requested or created. This note is outside the Skill. All authored files were created with `apply_patch`. No external writes, repository changes, installations, messages or live operations were performed. Saving is left to the parent as instructed.

## Resources used

Read the task's `prompt.md`, `input/brief.md`, `input/release_tool.py` and the supplied `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/common/agent-skills-format.md`. The optional frozen skill-creator aid was not used. No other authoring resources or external format sources were accessed.

## Design choices

Use the existing Python 3 command directly; it supplies all necessary operations, so a wrapper or duplicate simulator would add no needed capability. The template is explicitly an agent input record, not an extra argument or configuration format supported by the command. Paths and environment binding come from each application request.

Preserve usable existing qualification rather than automatically rerunning it and invalidating approval. Require exact candidate content, owner identity, qualification sequence and approval ordering before a new promotion. Allow permitted inspection and needed qualification even without owner approval. Treat command authorization separately from owner approval.

Record and reuse promotion request IDs, reconcile timeout effects through status and inspection, and account for the implementation's candidate check preceding its idempotent replay path. Require post-promotion production identity, readiness and checkout evidence independently. Report requirement satisfaction and unresolved matters separately from procedural correctness.

## Public commands and observed results

Every shell command used working directory `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/trials/control-072`.

Read/discovery commands, each exit 0:

```bash
cat prompt.md
cat input/brief.md
cat /workspace/scratch/a75c3a6d9076/alps-v070-assessment/common/agent-skills-format.md
rg --files input
cat input/release_tool.py
```

The `cat` commands returned the respective source contents. `rg --files input` returned only `input/release_tool.py` and `input/brief.md`.

Input integrity check, run once before authoring and once after authoring; both exit 0 with identical output:

```bash
sha256sum input/brief.md input/release_tool.py
```

```text
284eab48172c8b996d5eb3218590fb453c1e24f5b532f9d4457bda99fb38485e  input/brief.md
939931810a40d9f813280ea46c95fec2c4a1ed72368937353bf5c899b8217577  input/release_tool.py
```

Static artifact check, exit 0:

```bash
python3 - <<'PY'
import json, re
from pathlib import Path
root = Path('deliverables/skills/checkout-service-release')
text = (root / 'SKILL.md').read_text()
front = text.split('---', 2)[1]
fields = dict(line.split(': ', 1) for line in front.strip().splitlines())
assert set(fields) == {'name', 'description'}
assert fields['name'] == root.name
assert re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', fields['name'])
assert len(fields['name']) <= 64
assert 0 < len(fields['description']) <= 1024
links = re.findall(r'\]\(([^)]+)\)', text)
assert len(links) == 2
for link in links:
    assert (root / link).is_file(), link
config = json.loads((root / 'assets/release-context.template.json').read_text())
assert len(config) == 11
assert config['authorized_operations'] == []
assert config['request_id'] is None
assert config['candidate_id'] == ''
assert config['state_path'] == ''
assert config['environment_path'] == ''
assert len(list(root.rglob('*.*'))) == 3
print('PASS: skill name/frontmatter, description length, 2 resource links, JSON configuration and 3-file package')
print('Description characters:', len(fields['description']))
PY
```

Observed output:

```text
PASS: skill name/frontmatter, description length, 2 resource links, JSON configuration and 3-file package
Description characters: 453
```

CLI help verification, exit 0:

```bash
python3 - <<'PY'
import subprocess
base = ['python3', 'input/release_tool.py']
commands = [base + ['--help']] + [base + ['--state', 'verification-unused-state.json', op, '--help'] for op in ['inspect', 'qualify', 'promote', 'request-status', 'probe', 'checkout']]
for cmd in commands:
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, (cmd, result.stdout, result.stderr)
    assert 'usage:' in result.stdout
    print('PASS exit=0:', ' '.join(cmd))
PY
```

Observed output:

```text
PASS exit=0: python3 input/release_tool.py --help
PASS exit=0: python3 input/release_tool.py --state verification-unused-state.json inspect --help
PASS exit=0: python3 input/release_tool.py --state verification-unused-state.json qualify --help
PASS exit=0: python3 input/release_tool.py --state verification-unused-state.json promote --help
PASS exit=0: python3 input/release_tool.py --state verification-unused-state.json request-status --help
PASS exit=0: python3 input/release_tool.py --state verification-unused-state.json probe --help
PASS exit=0: python3 input/release_tool.py --state verification-unused-state.json checkout --help
```

The unused state path was only an argument to help invocations; no state file was created or read by those invocations.

## Verification limits and missing information

The checks establish basic physical form, resource existence, parseable configuration, CLI help compatibility and unchanged inputs. They are not an official format-validator run or a behavioral consumer evaluation. No qualification, promotion, timeout recovery, probe or checkout scenario was executed. Decisions were authored against the supplied command implementation and brief. No business-application state file, candidate request, environment mapping or operational authorization was supplied for an actual release; those remain per-use inputs. No business outcome is claimed.
