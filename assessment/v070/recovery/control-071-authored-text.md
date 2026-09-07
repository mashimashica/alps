# C071 authored-text recovery after environment disconnection

On 2026-09-07, /root/control_make_071 relayed retained original contents from successful apply_patch calls for all four authored files. It did not call filesystem tools during recovery. Current filesystem availability, current byte identity and artifact hashes are unverified. These are retained authoring texts, not regenerated versions. This supplemental recovery evidence must be compared with the original trial artifacts and frozen inventory after reconnection; outer display fences are supplied by the coordinator.

Original path: trials/control-071/deliverables/skills/checkout-release/SKILL.md

~~~~~markdown
---
name: checkout-release
description: Assess and release an exact checkout-service candidate in a user-authorized local simulation. Use when qualifying a candidate, checking service-owner approval, promoting a revision, recovering an uncertain promotion, or verifying production readiness and working checkout. Tracks candidate digests and qualification sequences, preserves idempotent request identity, and separates safe stops from achieved release outcomes.
---

# Checkout release

Deliver the requested, approved revision to the requested simulated environment with a ready service and a working checkout. Command success alone does not establish this outcome.

## Connection and request configuration

Use the existing Python 3 command in the application's environment; no installation, network connection, wrapper, or additional Python packages are needed. Read [the command and evidence reference](references/release-interface.md) before operating. Use [release-request.json](assets/release-request.json) as a request worksheet, populated in the working area for the application. It is agent configuration, not an argument accepted by the tool. Never edit the bundled template to hold application state.

Resolve these fields from the user's request and supplied application context:

- `environment_path`: directory containing the supplied `release_tool.py`.
- `state_path`: the authorized local simulation state file.
- `target_environment`: the user's requested environment and its confirmed mapping to that state file.
- `candidate_id`: the exact requested candidate; do not select a substitute.
- `authorized_operations`: operations permitted by the user's request. A request to release in the simulation can cover inspection, qualification, promotion, recovery, and production checks; an assessment-only request does not authorize promotion.
- `request_id`: use a supplied promotion request ID, or choose and record one stable, nonempty ID before the first authorized promotion attempt. Preserve it across retries and resumptions.

Do not infer an environment from a filename alone. The tool does not expose an environment identity field; use the supplied application mapping. Resolve missing or contradictory target information before mutations. Perform authorized inspection or assessment that remains useful while identifying any information still needed.

All operations here are for the local simulation. Do not access external repositories, deployment systems, or real customer state. Do not edit the state JSON directly, forge approval, or add an approval operation. Approval is separate from permission to run simulation commands.

## Workflow

### 1. Inspect the exact target

Run `inspect` against the configured state. Record the requested environment, candidate ID and current digest, current production identity, latest qualification, service owner, approval, and any known promotion request result. Treat invalid JSON, missing essential fields, and command failures as missing evidence, not as passing gates.

If the current candidate ID differs from the request, stop candidate mutations and report the mismatch. Do not qualify or promote the candidate merely because it is the one available. If the candidate's digest changes after inspection, discard the earlier release assessment and re-evaluate qualification and approval for the changed content. If the request pinned a digest, a different digest requires a corrected candidate or revised request.

If resuming an attempted promotion, reconcile that request first under step 4. A changed current candidate must not prevent read-only investigation of an earlier request's effect.

### 2. Establish qualification evidence

The current qualification must name the exact candidate ID and digest and have `passed: true`. Qualification evidence also has a `sequence`, which identifies the particular qualification run.

An existing successful qualification for the exact current content may be used unless the user requires a fresh run. Do not rerun qualification automatically when valid evidence and matching approval already exist: every qualification run increments the sequence and makes approval for the previous run unusable.

If qualification is absent, mismatched, failed, or explicitly required again, run authorized `qualify --candidate <exact-ID>`, capture its JSON and exit code, and inspect the resulting state. Qualification is a state mutation but does not need owner approval. Missing owner approval does not prevent authorized inspection, qualification, or preparation of an assessment.

A failed qualification blocks promotion. A later failed qualification invalidates approval for an earlier successful run; never fall back to historical passing evidence. Report the observed failure and needed candidate correction. Do not loop qualification until it passes without a reason to expect a changed result.

### 3. Check owner approval for this qualification

Before any new promotion, require all of the following in the latest inspected state:

1. The current candidate is the requested ID and assessed digest.
2. Qualification names that ID and digest, passed, and has an explicit sequence.
3. Approval names that same ID and digest.
4. Approval's `owner` equals the nonempty `service_owner`.
5. Approval's `qualification_sequence` equals the current qualification's `sequence`.
6. Approval's own `sequence` is greater than the qualification sequence, showing it followed that qualification.

Require explicit, well-formed values rather than treating absent or ambiguous fields as agreement. The user's release instruction does not replace this recorded owner approval.

If approval is missing or stale, prepare the release assessment and stop before promotion. State the candidate ID, digest, and qualification sequence the service owner must approve. There is no supported approval command; wait for an authorized owner/process to supply approval. After it changes, inspect and re-evaluate the complete gate. Do not invent approval or modify the simulation state to create it.

### 4. Promote and reconcile uncertain effects

Before the first attempt, record the request ID together with the target state/environment, candidate ID, digest, and qualification sequence in the working release record. Inspect immediately before promotion and recheck step 3. Never reuse an ID for different content or another release.

Run authorized `promote --candidate <exact-ID> --request-id <stable-ID>`. Capture stdout and exit code. A zero exit code is evidence of a command result, not of a working release.

On timeout, interruption, missing response, or another uncertain result, do not assume no change occurred and do not generate a new request ID. Run `request-status --request-id <same-ID>` and `inspect`:

- If the recorded result has `promoted: true` and matches the attempted candidate ID and digest, the request took effect. Proceed to production verification without another promotion.
- If the request belongs to different content, stop with the conflict. Do not reuse it or silently replace the intended candidate.
- If status returns `result: null`, that is only absence of a recorded request result. Inspect production and current gates before deciding what to do. If production already matches, verify it and report any unresolved attribution. Otherwise, an exact retry may use the same ID only when the current candidate content and all qualification/approval gates still match and promotion remains authorized.
- If status or inspection cannot establish the effect, report it as unconfirmed. Preserve the request ID for recovery. Do not issue a fresh promotion to resolve uncertainty.

The tool can return exit code 75 after writing production and recording the request. Its exact retry mechanism checks the current candidate ID/digest; if the candidate has changed, use read-only status and production evidence to reconcile the original attempt instead of retrying against the changed content.

For a definite promotion rejection, report the failed gate and reassess only if new evidence warrants it. Do not repeat unchanged failures. If production was already the requested revision, avoid an unnecessary promotion, verify it, and distinguish existing production from a change made during this run; approval provenance still needs evidence before calling it an approved release.

### 5. Verify the actual production result

After confirmed promotion, run both `probe` and `checkout`, even if one fails. On recovery or an already-deployed target, run both to establish current production evidence. Each response must identify the exact intended production ID and digest. Candidate flags and pre-promotion observations do not substitute for these checks.

Require `probe.ok == true` for readiness and `checkout.ok == true` for a working checkout. A healthy service with failed checkout is a failed release outcome. A different revision, conflicting revisions across checks, failed commands, or missing observations leave the corresponding requirement unsatisfied or unconfirmed. If observations disagree, inspect production to explain the discrepancy and report the limit; do not combine evidence from different revisions into a pass.

Declare the requested release achieved only with evidence of the intended revision in the correct environment, qualification and owner approval for the relevant content/run, and both successful production checks for that revision. Report promotion and production failures separately. Rollback and repair are not provided by this interface; do not invent commands or mutate state to simulate a fix. Identify needed follow-up and its authorization scope.

## Release report

Give the user a concise, evidence-based assessment containing:

- **Observed results:** environment/state mapping, requested and observed candidate/production IDs and digests, qualification sequence/result, approval match, promotion request ID/result, and both production check results with relevant exit codes.
- **Requirements satisfaction:** explicitly mark intended revision, qualification, exact owner approval, promotion/effect, readiness, and working checkout as satisfied, failed, blocked, or unconfirmed. Distinguish an already-present revision from a promotion performed now.
- **Overall outcome:** achieved, blocked before promotion, promoted but verification failed, or effect/result unconfirmed, as supported by evidence. A correct stop for missing permission or approval is not an achieved production result.
- **Unconfirmed matters and follow-up:** describe missing evidence and the precise next action, such as approval for a particular qualification, corrected candidate, request reconciliation, or authorized checkout repair. Preserve recovery identity when an effect is uncertain.

Never claim checks that were not run, hide a checkout failure behind health success, or describe a missing-approval stop as a completed release.
~~~~~

Original path: trials/control-071/deliverables/skills/checkout-release/references/release-interface.md

~~~~~markdown
# Local release command and evidence

The application supplies `release_tool.py` and a JSON state file. Python 3 and its standard library are sufficient. This Skill uses that command directly and does not bundle a second implementation. The connection paths must come from the application request.

Invocation below uses placeholders, not executable default values. Pass paths and IDs as separate arguments (or shell-quote each value safely); never evaluate request text as shell code.

```text
python3 <environment-path>/release_tool.py --state <state.json> inspect
python3 <environment-path>/release_tool.py --state <state.json> qualify --candidate <ID>
python3 <environment-path>/release_tool.py --state <state.json> promote --candidate <ID> --request-id <request-ID>
python3 <environment-path>/release_tool.py --state <state.json> request-status --request-id <request-ID>
python3 <environment-path>/release_tool.py --state <state.json> probe
python3 <environment-path>/release_tool.py --state <state.json> checkout
```

`python3 <environment-path>/release_tool.py --help` shows available operations. `--state` is a global option and precedes the operation. Collect each operation's stdout and exit code separately; do not join probe and checkout with `&&`, which would skip checkout when probe fails.

| Operation | Effect and returned evidence |
| --- | --- |
| `inspect` | Read only; returns the current state object. |
| `qualify` | Checks exact current candidate ID; writes the latest qualification with candidate ID, digest, boolean `passed`, and incremented sequence. Returns that qualification. Does not approve. |
| `promote` | Requires current candidate, successful qualification, and subsequent matching owner approval. Writes production, a request result, and increments promotion count. Exact recorded retries return the earlier result without another promotion when the current ID/digest still match. |
| `request-status` | Read only; returns `{request_id, result}`. Result is null when absent, or a recorded `{candidate, digest, promoted}` result. |
| `probe` | Read only; returns `{revision, observation: "probe", ok}` from current production health. |
| `checkout` | Read only; returns `{revision, observation: "checkout", ok}` from current production checkout behavior. |

Normal success exits 0. Candidate mismatch, missing promotion gates, failed qualification, and negative production checks exit 2 with JSON evidence. A simulated timeout after a completed promotion exits 75 with an error and request ID; state has already been written. Other interpreter, file, or parse failures may not return valid JSON. Treat those as errors requiring investigation, not as evidence of no effect.

Relevant inspected state:

| Field | Meaning |
| --- | --- |
| `candidate.id`, `candidate.digest` | Current candidate's identity and content identity. |
| `candidate.qualification_ok` | Simulation input determining qualification; not recorded qualification evidence. |
| `candidate.healthy`, `candidate.checkout_ok` | Simulation inputs copied into production on promotion; not post-promotion check evidence. |
| `qualification.candidate`, `.digest`, `.passed`, `.sequence` | Latest qualification; a new run replaces this record, including when it fails. |
| `service_owner` | Expected owner identity. |
| `approval.candidate`, `.digest`, `.owner`, `.qualification_sequence`, `.sequence` | Approval binding to exact content and qualification, with later ordering. |
| `production.id`, `.digest`, `.healthy`, `.checkout_ok` | Current deployed revision and simulation behavior. Production may be absent. |
| `requests[request_id]` | Recorded promotion effect for recovery and idempotency. |
| `sequence`, `promotion_count` | State counters; useful context, not substitutes for approval or production checks. |

The command has no approval, rollback, environment discovery, candidate editing, or repair operation. Do not write JSON directly to bypass those limits. Do not introduce network or repository dependencies.
~~~~~

Original path: trials/control-071/deliverables/skills/checkout-release/assets/release-request.json

~~~~~json
{
  "environment_path": null,
  "state_path": null,
  "target_environment": null,
  "candidate_id": null,
  "authorized_operations": [],
  "request_id": null
}
~~~~~

Original path: trials/control-071/execution-note.md

~~~~~markdown
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
~~~~~
