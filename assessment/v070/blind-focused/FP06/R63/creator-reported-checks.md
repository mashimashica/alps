# Public execution note

## Deliverables

- `deliverables/skills/checkout-release/SKILL.md`: reusable release workflow and description.
- `deliverables/skills/checkout-release/references/release-interface.md`: command connection, effects, evidence fields, exit codes, and recovery limits.
- `deliverables/skills/checkout-release/assets/release-request.json`: blank application connection and authorization worksheet.

No demonstration was requested or created. This note is outside the Skill.

## Resources actually used

Read the task's `prompt.md`, `input/brief.md`, `input/release_tool.py`, and the supplied common orientation at `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/common/agent-skills-format.md`. The optional frozen skill-creator aid was not used. No external format sources, other tasks, or external business systems were accessed.

## Design decisions

The Skill uses the existing command directly. A duplicate implementation or wrapper adds no needed capability here. The linked reference makes the interface understandable without access to authoring inputs; the application must still supply the existing command and state as specified in the brief.

Configuration has no default candidate, environment, permission, or request identity. The agent resolves the application mapping from the request; the tool itself does not prove which named environment a state file represents.

The workflow binds approval to candidate ID, digest, latest successful qualification sequence, owner identity, and later approval ordering. It preserves usable qualification evidence rather than automatically running qualification again and invalidating existing approval. Missing approval blocks promotion while allowing authorized qualification and assessment. Changed content and newer failed qualifications require re-evaluation.

Recovery preserves promotion request identity, queries recorded effects after uncertainty, and uses exact retries only with matching content and gates. Production verification requires both readiness and checkout for the intended ID/digest. Reports distinguish achieved outcomes, blocked work, failed checks, and unconfirmed effects. No approval or repair mechanism is invented.

## Public commands and observed results

Every shell command used the working directory `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/trials/control-071`.

1. `cat prompt.md` — exit 0; read the task boundaries, output location, permitted resources, and public-note requirement.
2. `cat input/brief.md && rg --files input` — exit 0; read the fictional checkout-release brief and listed exactly `input/brief.md` and `input/release_tool.py`.
3. `cat /workspace/scratch/a75c3a6d9076/alps-v070-assessment/common/agent-skills-format.md` — exit 0; read required Skill frontmatter and supporting-resource guidance.
4. `cat input/release_tool.py` — exit 0; inspected the supplied implementation and its six operations.
5. `sha256sum input/brief.md input/release_tool.py && python3 input/release_tool.py --help` — exit 0; hashes were:

   ```text
   284eab48172c8b996d5eb3218590fb453c1e24f5b532f9d4457bda99fb38485e  input/brief.md
   939931810a40d9f813280ea46c95fec2c4a1ed72368937353bf5c899b8217577  input/release_tool.py
   ```

   Help showed `--state STATE` and operations `inspect`, `probe`, `checkout`, `qualify`, `promote`, and `request-status`. Help did not read or mutate simulation state.
6. The following standard-library check ran as `python3 - <<'PY' ... PY` and exited 0:

   ```python
   import hashlib, json, re
   from pathlib import Path
   root = Path('deliverables/skills/checkout-release')
   skill = root / 'SKILL.md'
   text = skill.read_text()
   assert text.startswith('---\n')
   front, body = text[4:].split('\n---\n', 1)
   fields = dict(line.split(': ', 1) for line in front.splitlines())
   name = fields['name']
   assert name == root.name and len(name) <= 64
   assert re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name)
   assert 0 < len(fields['description']) <= 1024
   links = re.findall(r'\[[^\]]+\]\(([^)]+)\)', body)
   assert links
   for target in links:
       assert (root / target).is_file(), target
   config = json.loads((root / 'assets/release-request.json').read_text())
   assert set(config) == {'environment_path', 'state_path', 'target_environment', 'candidate_id', 'authorized_operations', 'request_id'}
   assert config['authorized_operations'] == []
   assert all(value is None for key, value in config.items() if key != 'authorized_operations')
   for rel, expected in {
       'input/brief.md': '284eab48172c8b996d5eb3218590fb453c1e24f5b532f9d4457bda99fb38485e',
       'input/release_tool.py': '939931810a40d9f813280ea46c95fec2c4a1ed72368937353bf5c899b8217577',
   }.items():
       assert hashlib.sha256(Path(rel).read_bytes()).hexdigest() == expected, rel
   print('PASS: required frontmatter, name, description length, and 2 local links')
   print('PASS: JSON connection worksheet has 6 fields and no preauthorized operations')
   print('PASS: both supplied input hashes unchanged')
   print('Skill files:')
   for path in sorted(root.rglob('*')):
       if path.is_file():
           print(path)
   ```

   Observed output:

   ```text
   PASS: required frontmatter, name, description length, and 2 local links
   PASS: JSON connection worksheet has 6 fields and no preauthorized operations
   PASS: both supplied input hashes unchanged
   Skill files:
   deliverables/skills/checkout-release/SKILL.md
   deliverables/skills/checkout-release/assets/release-request.json
   deliverables/skills/checkout-release/references/release-interface.md
   ```

Authored files were created with `apply_patch`; the tool returned successfully. No commits, uploads, installation, or state-changing release operations were performed.

## Verification limits

The checks establish the simple metadata structure, naming constraints, link existence, JSON validity/configuration defaults, command help, and unchanged inputs. They are not the official reference validator, a complete YAML parser, or a business-behavior execution test. The workflow was reviewed against the supplied implementation, but no application state, actual candidate/environment request, or user-authorized simulation release was supplied. No end-to-end release, consumer-agent run, timeout simulation, approval transition, or production probe/checkout was executed. The deliverable therefore makes no claim that a release occurred or that runtime business behavior was demonstrated.
