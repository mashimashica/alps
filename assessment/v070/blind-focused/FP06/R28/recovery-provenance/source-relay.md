# C072 authored-text recovery after environment disconnection

On 2026-09-07, /root/control_make_072 relayed the retained original contents from successful apply_patch calls for all four authored files. It did not access the disconnected workspace. Current filesystem availability, byte identity and authored-file hashes are unverified. No authoring was rerun. This supplemental recovery evidence must be compared with the original trial artifacts and frozen inventory after reconnection; outer display fences are supplied by the coordinator.

Original path: trials/control-072/deliverables/skills/checkout-service-release/SKILL.md

~~~~~markdown
---
name: checkout-service-release
description: Assess and execute an authorized simulated checkout-service release for an exact candidate and environment. Validate qualification and subsequent service-owner approval, reconcile uncertain promotion effects using request IDs, and verify the production revision, service health and checkout result. Use for release requests, readiness assessments, interrupted promotion recovery and post-release verification with the supplied release_tool.py interface.
---

# Checkout service release

The goal is the intended approved revision serving users with both a ready service and a working checkout. A successful promotion command, an approval-blocked stop, or a passing health probe alone does not establish that goal.

This Skill uses an existing Python 3 simulation command. It does not authorize live deployments or supply approvals. Never modify the simulator, its state JSON, qualification, approval, or production fields directly to obtain a desired result.

## Bind the request

Use [assets/release-context.template.json](assets/release-context.template.json) as supporting configuration for each application. Copy it outside this Skill and fill it from the user's request and supplied environment. Empty strings and nulls are unresolved values, never defaults. The file is an agent input record, not a configuration file consumed by `release_tool.py`. See [references/interface.md](references/interface.md) for command syntax, field meanings and retry behavior.

Establish the following before invoking relevant operations:

- The exact requested candidate ID, desired environment, environment path and state-file path. If the request supplies a digest, record it too. Otherwise pin the digest observed at initial inspection.
- Evidence that these paths belong to that desired environment. The simulator has no environment-selection flag or authoritative environment field; do not infer the target from a candidate name or silently use a default state file.
- The operations authorized by the request. Inspection and preparation can proceed within their permitted scope even when owner approval is absent. Qualification and promotion mutate simulation state and need the request's authorization for those operations. A filled configuration entry alone is not evidence of permission.
- For a promotion or recovery, a supported request ID, reused from the interrupted attempt if there was one. For a new release use a caller-supplied ID or, if the environment allows caller-chosen IDs, generate one and record it before sending the command. Never reuse another release's ID.

If an essential input is absent, complete the useful assessment supported by available information, then ask only for the missing input. Do not substitute another candidate or environment. Do not ask again for permissions already given in the request. No approval is required merely to prepare an assessment.

## Inspect and qualify the exact candidate

1. Run `inspect` and record the observed candidate ID and digest, production revision, service owner, qualification, approval and any relevant request record. Bind every later command to the same environment path and state file.
2. Require the current candidate ID to equal the requested ID, and its digest to equal any requested digest. Pin the observed digest for this release. Missing or inconsistent identity evidence blocks promotion. Existing production may be reported but must not be used to silently change the requested release.
3. Examine the current qualification. It is usable only if it names this exact candidate ID and digest and has `passed: true`. Preserve a usable existing qualification, especially one already approved: calling `qualify` creates a new qualification sequence even when content is unchanged.
4. If there is no usable qualification, run `qualify --candidate ...` if authorized, including when approval is missing. Read its JSON and exit code. Record candidate, digest, passed status and sequence. Failed qualification blocks promotion. Do not repeat a failure merely to obtain a different sequence or use older passing evidence.
5. If the user explicitly requests a fresh qualification, perform it when authorized and treat all approval against a prior sequence as stale. New owner approval must follow and cover the new passing qualification.

If candidate content changes after it was pinned, stop the pending promotion and report the mismatch. Do not silently accept the new digest under the old release decision. Once the changed candidate is established as the intended target by the request or user, it requires matching passing qualification and subsequent approval. A newer failed qualification supersedes older passing qualification and approval.

## Validate approval and promote

Use the current inspected state, not a statement that someone approved an earlier version. All of these requirements must hold together:

| Requirement | Evidence |
| --- | --- |
| Candidate identity | Current candidate equals the requested ID and pinned digest |
| Qualified content | `qualification.candidate` and `.digest` match; `.passed` is true |
| Service-owner approval | `approval.owner` equals the non-empty `service_owner` |
| Approved content | `approval.candidate` and `.digest` match the candidate |
| Approved qualification | `approval.qualification_sequence == qualification.sequence` |
| Approval follows qualification | Numeric `approval.sequence > qualification.sequence` |
| Correct target and permission | Request covers promotion in the bound simulation environment |

Missing, malformed, stale or mismatched evidence does not satisfy a requirement. There is no approval-writing command in this interface. If approval is missing or unusable, do not promote or edit the state to approve it. Present the exact candidate ID, digest and passing qualification sequence that the service owner must approve through the application's authorized approval process. Missing owner approval must not prevent permitted inspection, needed qualification or preparation of the release assessment. A valid stop still leaves the production objective unachieved or unconfirmed.

Immediately before a new promotion, inspect again and revalidate candidate, qualification and approval. If qualification changed, reevaluate the whole gate; do not carry forward approval against a different sequence. Use a recorded request ID, then call `promote --candidate ... --request-id ...` once. Interpret its result rather than equating exit code zero with a completed release.

## Reconcile uncertain effects

For an interrupted attempt, recover its original request ID and inspect its status before starting any new promotion. If the ID is unavailable, inspect production and request records for evidence, but do not guess an ID or send a fresh promotion while the previous effect remains unresolved.

- A timeout or exit code 75 can occur **after** promotion has changed state. Call `request-status` with the same ID and inspect current state. Do not immediately use a new ID.
- A status result with `promoted: true` and the exact candidate ID and pinned digest confirms that request's recorded effect. Move to production verification. Historical request success does not prove that revision is still serving.
- A record for another candidate or digest is a conflict, not success and not permission to replace the ID. Stop and resolve the discrepancy.
- A null result means no recorded effect was found in that state at that observation; it is not a successful release. Verify the bound environment, inspect current candidate, production and approval, and check for an in-flight invocation before considering a retry.
- Retry only when the uncertainty is reconciled enough to do so, the environment supports exact idempotent retries, and the intended candidate and digest are unchanged. Reuse the **same** ID and candidate. For an unrecorded request, all qualification, approval and permission gates must still hold. If evidence remains unavailable or contradictory, stop further mutations and report what is unresolved.

This implementation checks the current candidate before returning a recorded request result. A retry can therefore fail after a candidate change even though the first promotion succeeded. Use `request-status` and production observations to resolve that case; do not switch candidates to force the retry to pass.

## Verify production and judge the result

After confirmed promotion, run both `probe` and `checkout` against the same state. Run checkout even if probe fails, when authorized and executable, to obtain both observations. Do not predict production results from candidate flags. These checks occur after promotion; pre-promotion observations cannot establish the result of the new release.

For each observation, record command, exit code, returned revision ID and digest, and `ok`. Require both observations to identify the exact requested ID and pinned digest. If revisions differ between checks or either observes another revision, the release result is inconsistent or incorrect even if both `ok` values are true. Inspect again as useful to explain the discrepancy without claiming stable success.

The full requested result is achieved only with evidence for the intended environment, passing qualification, subsequent matching owner approval, confirmed promotion, matching production identity, successful readiness probe and completed checkout. A checkout failure after a successful promotion and health probe is a deployed but unsuccessful release. Missing checks leave the corresponding requirements unconfirmed. Do not invent a rollback command: this interface has none. Report the failure and necessary remediation; further qualification, promotion or recovery work requires its own applicable authorization and gates.

## Report

Return a concise release assessment with:

- **Target:** environment, candidate ID, pinned digest and promotion request ID, when applicable.
- **Observed results:** qualification sequence and outcome, approval basis, promotion/status evidence, and each production check with exit code and revision.
- **Requirements satisfaction:** mark candidate/environment identity, qualification, owner approval, confirmed promotion, readiness and checkout individually as satisfied, failed, blocked or unconfirmed, citing the observations.
- **Overall outcome:** achieved, not achieved, or unconfirmed. Distinguish a correct procedural stop from the requested production result. If production was already on the desired revision, state that observation separately from whether this requested release was promoted.
- **Unconfirmed matters and follow-up:** exact missing approval or input, failed checkout/readiness, unresolved request effect, or authorized next action. Describe what was not run and why.

Keep approval evidence distinct from the permission to run simulation commands. Do not claim success from an attempted command, candidate metadata, or evidence for a different revision.
~~~~~

Original path: trials/control-072/deliverables/skills/checkout-service-release/assets/release-context.template.json

~~~~~json
{
  "desired_environment": "",
  "environment_path": "",
  "state_path": "",
  "environment_binding_evidence": "",
  "candidate_id": "",
  "requested_digest": null,
  "observed_candidate_digest": null,
  "request_id": null,
  "request_id_origin": null,
  "authorization_evidence": "",
  "authorized_operations": []
}
~~~~~

Original path: trials/control-072/deliverables/skills/checkout-service-release/references/interface.md

~~~~~markdown
# Simulator connection and evidence

Dependency: Python 3 and the application's existing `release_tool.py` plus a supplied JSON state file. No package installation, remote connection, credentials, wrapper or bundled simulator is required. Never replace the application tool or initialize, repair or rewrite its state as part of this workflow.

The context template is a per-request record. `authorized_operations` lists only operations covered by the cited user authorization; an empty list grants none. `request_id_origin` describes whether the ID was supplied, recovered or generated under the application's caller-chosen ID convention. `requested_digest` is optional; `observed_candidate_digest` is pinned from inspect. Record path-to-environment evidence in `environment_binding_evidence`, since this interface cannot independently prove an environment label.

Set shell variables from validated inputs, quote paths and values, and never use `eval`. In the examples, `RELEASE_ENV`, `RELEASE_STATE`, `RELEASE_CANDIDATE` and `RELEASE_REQUEST_ID` must be populated first. Use absolute paths where possible. Commands below are individual workflow steps, not a script to run unconditionally in order.

```bash
python3 "$RELEASE_ENV/release_tool.py" --state "$RELEASE_STATE" inspect
python3 "$RELEASE_ENV/release_tool.py" --state "$RELEASE_STATE" qualify --candidate "$RELEASE_CANDIDATE"
python3 "$RELEASE_ENV/release_tool.py" --state "$RELEASE_STATE" promote --candidate "$RELEASE_CANDIDATE" --request-id "$RELEASE_REQUEST_ID"
python3 "$RELEASE_ENV/release_tool.py" --state "$RELEASE_STATE" request-status --request-id "$RELEASE_REQUEST_ID"
python3 "$RELEASE_ENV/release_tool.py" --state "$RELEASE_STATE" probe
python3 "$RELEASE_ENV/release_tool.py" --state "$RELEASE_STATE" checkout
```

Capture each command's JSON output and process exit code separately. Do not join probe and checkout with `&&`, since a failing probe would suppress checkout. CLI syntax is discoverable with `python3 "$RELEASE_ENV/release_tool.py" --help`; operation help accepts `--state "$RELEASE_STATE" OPERATION --help` without running the operation.

| Operation | State effect | Result and interpretation |
| --- | --- | --- |
| `inspect` | None | Full state: candidate, production, qualification, approval, service_owner, requests and sequence when present. Exit 0 means read completed. |
| `qualify` | Replaces qualification and increments sequence, including on a failed check | `{candidate, digest, passed, sequence}`. Exit 0 for pass, 2 for failure or candidate mismatch. It never creates approval. |
| `promote` | On a new valid request, writes production, request record and promotion count | `{candidate, digest, promoted: true}` with exit 0 on success. Gate rejection returns error and exit 2. An injected response timeout returns error and exit 75 after persisting promotion. |
| `request-status` | None | `{request_id, result}` with exit 0. `result` is null for no recorded request, otherwise the stored promotion result; inspect nested identity and `promoted`. |
| `probe` | None | `{revision, observation: "probe", ok}`. Exit 0 for true, 2 for false. Revision is the production object, or null. |
| `checkout` | None | `{revision, observation: "checkout", ok}`. Exit 0 for true, 2 for false. This is separate from readiness. |

Candidate contains `id`, `digest`, `qualification_ok`, `healthy` and `checkout_ok`. The last three are simulation inputs; use qualification and production commands as evidence rather than reading the flags as completed checks. Production observations return `revision.id` and `revision.digest`, along with its health and checkout flags.

Qualification contains `candidate`, `digest`, `passed`, `sequence`. Approval contains `candidate`, `digest`, `owner`, `qualification_sequence`, `sequence`. Approval must match `service_owner`, the exact candidate content and the current passing qualification; its sequence must be later. The simulator stores only the current qualification, so stale evidence from earlier inspection is insufficient.

For promotion, the implementation first checks the candidate ID against current candidate. It then looks for an existing request ID. A recorded request matching the current candidate and digest returns the prior result without another promotion; a recorded request with differing candidate/digest errors. This retry path does not recheck approval, so a successful replay is historical effect evidence, not fresh proof of current approval. A new request must satisfy the full gate. `request-status` reads the stored record even if the current candidate changed.

The tool reads and rewrites one local JSON file and provides no concurrency lock. Avoid overlapping mutating commands. Fresh inspection reduces stale decisions but is not a transaction lock; contradictory or changing observations require reconciliation. A malformed state file, process interruption, non-JSON output or unexpected exit code is not proof of no effect. Preserve observed evidence, inspect state/status as applicable, and report unresolved matters before further mutation.
~~~~~

Original path: trials/control-072/execution-note.md

~~~~~markdown
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
~~~~~
