# C069 authored-text recovery after environment disconnection

On 2026-09-07, /root/control_make_069 relayed the following text from successful apply_patch calls in its existing conversation. No authoring was rerun. The agent stated: "I have not reread the files or verified their current bytes. No content hashes were recorded."

This is conversation-recovered evidence, separately stored from the original trial artifacts. Compare it with the original files and frozen inventory after reconnection. Do not substitute it for byte-verified originals or infer a missing runtime history. Outer display fences are supplied by the coordinator.

Original path: trials/control-069/deliverables/skills/release-checkout/SKILL.md

~~~~~markdown
---
name: release-checkout
description: Qualify and release an exact checkout-service candidate in the supplied local simulation, verify service-owner approval, recover uncertain promotion effects, and assess production health and checkout. Use for checkout release requests or release-readiness assessments using release_tool.py.
---

# Release checkout

Deliver the requested revision to the requested environment with a ready service and a completed checkout. Qualification, approval, promotion, health, and checkout are distinct evidence requirements. A blocked release is not an achieved release.

## Connect the request

Use [assets/release-request.json](assets/release-request.json) as an optional per-request configuration template. Read its fields as agent inputs; the existing tool does not consume this configuration. Populate values from the user's request and supplied environment, never from guessed defaults. Require the exact candidate ID, desired environment, environment path, and state-file path before operating. Confirm that the supplied state file represents the requested environment: the tool has no environment-selection flag or independent environment attestation. If that mapping is unclear, inspect permitted information and resolve it before mutation.

The environment supplies Python 3 and `release_tool.py`; do not install a connector or copy a second implementation. All operations use this command shape, with quoted arguments:

```text
python3 "<environment-path>/release_tool.py" --state "<state.json>" inspect
python3 "<environment-path>/release_tool.py" --state "<state.json>" qualify --candidate "<candidate-id>"
python3 "<environment-path>/release_tool.py" --state "<state.json>" promote --candidate "<candidate-id>" --request-id "<request-id>"
python3 "<environment-path>/release_tool.py" --state "<state.json>" request-status --request-id "<request-id>"
python3 "<environment-path>/release_tool.py" --state "<state.json>" probe
python3 "<environment-path>/release_tool.py" --state "<state.json>" checkout
```

Substitute literal supplied values safely; do not execute these placeholders. Capture JSON output and exit status for each call. The supplied simulation's precise fields and retry semantics are described in [references/tool-contract.md](references/tool-contract.md); read it before deciding qualification or approval validity or recovering a promotion.

Respect the user's authorized simulation operations. Inspection, probe, checkout, and request-status are read-only in this interface; qualification and promotion write the local state. Existing session authorization is sufficient when it covers the operation. The configuration is not itself permission, and user permission to run the simulation is distinct from service-owner approval in its state. Never edit state directly, manufacture approval, access live services, or substitute another candidate.

## Establish release readiness

1. Inspect the state. Match the requested ID to `candidate.id` and bind this attempt to its exact `digest`. Record current production, qualification, service owner, and approval. If the ID differs, stop candidate mutation and report the mismatch; do not qualify the available candidate instead. Missing identity or evidence fields are unresolved, not successful matches.
2. Determine whether the current recorded qualification passed for this ID and digest. Reuse valid current qualification unless the user requested a fresh run or evidence requires one. Each qualification call creates a new sequence, even for unchanged content, and therefore invalidates approval tied to the previous sequence. If qualification is absent, mismatched, or failed, perform qualification when authorized. A failure blocks promotion. Do not repeatedly rerun a known failing qualification merely to obtain a pass.
3. Inspect again after qualification or any intervening change. Approval must be by the current service owner, name the exact candidate ID and digest, reference the current passed qualification's sequence, and occur later than that qualification. Apply the exact conditions in the tool contract. A changed digest, newer qualification, or latest failed qualification invalidates an older approval. General release permission, candidate-ID-only approval, or a successful historical qualification is insufficient.
4. If valid approval is missing, finish all authorized inspection, qualification, and assessment work. Then report the exact candidate/digest and qualification sequence needing owner approval. There is no approval operation in this interface: the owner or authorized environment provider must supply it. Do not invent a command or change approval fields. Missing owner approval blocks promotion, not the preparatory work.

## Promote and resolve the effect

Immediately before promotion, re-inspect and recheck candidate, qualification, approval, environment mapping, and user authorization. If content changed, reassess that content and require its valid qualification and approval; never silently treat an approval for an old digest as current.

Choose one unique request ID for this exact attempt, or use the request's supplied ID. Record it together with environment/state path, candidate ID, and digest before calling promotion so the same identity survives interruption. Query an existing supplied request ID before using it. If its recorded candidate/digest conflicts, stop and resolve the conflict. Never recycle an ID across candidates, content changes, environments, or unrelated attempts.

Call promotion only when all gates hold. Exit code 0 confirms a command result, not a working release. On timeout, interruption, malformed response, or any uncertain effect, query `request-status` with the same ID and inspect production before deciding whether to retry. Exit code 75 specifically can mean promotion already happened.

- A matching recorded result with `promoted: true` establishes the request's promotion effect; proceed to production checks without another promotion.
- A conflicting recorded result blocks reuse. A missing result does not by itself establish that production is unchanged; compare inspection with the initial state and resolve discrepancies.
- If no result exists, state is consistent with no completed promotion, and the exact candidate and approval gates still hold, an authorized retry may reuse the same ID and arguments. Limit automatic recovery to one exact retry, then inspect status again and report unresolved uncertainty if necessary. Do not use a fresh ID to escape a timeout or tool error.

If the candidate changed while resolving uncertainty, use request-status to recover the prior effect; do not retry against the new candidate. The tool checks the current candidate before recognizing a prior request.

## Verify and assess

After promotion is confirmed, run both `probe` and `checkout`, even if the first fails. Each must report `ok: true` and a production `revision` whose ID and digest match the intended candidate. Health success alone cannot satisfy checkout. Qualification flags and candidate expectations cannot substitute for these post-promotion observations. If the observations identify different revisions or disagree with final inspection, mark the intended release unconfirmed and investigate permitted read-only evidence.

Report the observed promotion effect separately from overall release success. If production is unhealthy or checkout fails, the release objective is unmet even though promotion succeeded. Do not claim automatic rollback, fix state flags, or promote an alternative: this interface supplies no rollback or repair operation. Identify the failed requirement and necessary authorized remediation, then require fresh evidence for any subsequent success claim.

Give a concise release assessment containing:

- Requested environment, candidate ID/digest, and simulation scope.
- Qualification result and sequence; approval owner and binding, or the specific missing gate.
- Request ID, promotion result, and any timeout/recovery evidence.
- Post-promotion health and checkout results with the observed revision for each, or explicitly “not run” and why.
- Requirement status for exact revision, valid qualification, exact owner approval, promotion, ready service, and working checkout; distinguish satisfied, failed, and unconfirmed.
- Overall outcome: achieved only when all requirements hold, otherwise blocked, failed, or unconfirmed, with the next necessary action and responsible party where known.

Support claims with actual outputs. Preserve uncertainty when a command or observation did not establish the result; do not describe a correct permission stop as release completion.
~~~~~

Original path: trials/control-069/deliverables/skills/release-checkout/assets/release-request.json

~~~~~json
{
  "environment": null,
  "environment_path": null,
  "state_path": null,
  "candidate_id": null,
  "request_id": null,
  "authorized_operations": [],
  "authorization_source": null
}
~~~~~

Original path: trials/control-069/deliverables/skills/release-checkout/references/tool-contract.md

~~~~~markdown
# Supplied local release-tool contract

The connection is an environment-provided `release_tool.py` and JSON state file, invoked with Python 3. There is no network connection or credential requirement. The request configuration's `environment` describes the desired target; `environment_path` locates the tool and `state_path` selects the simulation. `candidate_id` identifies the exact candidate. `request_id` can be supplied or generated before an authorized promotion and must be retained for recovery. `authorized_operations` and `authorization_source` summarize actual user authorization; empty or null values confer no permission. Null configuration values are intentionally unbound, not tool arguments.

## Evidence fields

`inspect` returns the state. Relevant fields are:

| Field | Meaning |
| --- | --- |
| `candidate.id`, `candidate.digest` | Current candidate identity and content binding |
| `candidate.qualification_ok` | Simulation input to qualification, not recorded qualification evidence |
| `qualification.candidate`, `.digest`, `.passed`, `.sequence` | Latest recorded qualification |
| `service_owner` | Required approver identity |
| `approval.owner`, `.candidate`, `.digest` | Approval identity and candidate binding |
| `approval.qualification_sequence` | Qualification expressly approved |
| `approval.sequence` | Approval ordering |
| `production.id`, `.digest`, `.healthy`, `.checkout_ok` | Currently promoted revision and simulated behavior |
| `requests` | Recorded promotion effects keyed by request ID |

Require meaningful candidate ID/digest and owner identity rather than treating missing values as equal. A valid promotion basis requires all of:

```text
candidate.id == requested_candidate_id
qualification.candidate == approval.candidate == candidate.id
qualification.digest == approval.digest == candidate.digest
qualification.passed == true
approval.owner == service_owner
approval.qualification_sequence == qualification.sequence
approval.sequence > qualification.sequence
```

`qualify` requires the current candidate ID, increments the global sequence, and overwrites qualification with `{candidate, digest, passed, sequence}`. Failed qualification is still persisted. A fresh qualification supersedes earlier evidence; the interface retains no qualification history. In particular, do not rerun qualification after approval as a harmless check.

## Operations and results

| Operation | Effect and interpretation |
| --- | --- |
| `inspect` | Read-only; exit 0 with state JSON. |
| `qualify --candidate ID` | Writes qualification; exit 0 if passed, 2 if failed or ID mismatched. |
| `promote --candidate ID --request-id ID` | Checks current candidate, then prior request, then qualification/approval gates. On success writes production and request result and increments promotion count. |
| `request-status --request-id ID` | Read-only; exit 0 with `{request_id, result}`. `result: null` means no recorded effect for that ID. |
| `probe` | Read-only; returns `{revision, observation: "probe", ok}`; exit 0 if healthy, otherwise 2. |
| `checkout` | Read-only; returns `{revision, observation: "checkout", ok}`; exit 0 if checkout completed, otherwise 2. |

A successful promotion returns `{candidate, digest, promoted: true}`. A repeated request ID for the same current candidate/digest returns that prior result without another state change. Reusing an ID for different content fails. Prior-result handling occurs before approval checks, so retry success is not new evidence of current approval; use the established approval evidence from the actual promotion attempt.

If `timeout_once_after_promotion` was set, promotion saves production and the request result but returns exit 75 with an error and request ID. Recover via request-status, not a fresh request. Promotion validation failures return exit 2 with `error`. Other process failures may have no JSON; retain diagnostics and inspect state to determine any uncertain effect.

Production checks return the full revision object, not just a Boolean. Compare ID and digest for each observation. The simulator does not support approval creation, rollback, repair, environment discovery, or transactions spanning multiple calls. Report those limits when they prevent establishing the requested result.
~~~~~

Original path: trials/control-069/execution-note.md

~~~~~markdown
# Public execution note

Created `deliverables/skills/release-checkout/` with `SKILL.md`, `assets/release-request.json`, and `references/tool-contract.md`. No demonstration was requested or created. Original inputs were not modified. No external operations, installation, commit, push, or upload were performed.

## Resources used

- Task `prompt.md` and `input/brief.md`.
- Supplied `input/release_tool.py`, read to establish exact qualification, approval, retry, timeout, and observation semantics.
- Supplied `../../common/agent-skills-format.md` physical-format orientation.
- Frozen `../../frozen/skill-creator/SKILL.md`, read in full, and its `scripts/quick_validate.py` validator.

All shell calls used `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/trials/control-069` as the working directory. Authored files were written with `apply_patch`.

## Public commands and observed checks

The read commands were `cat prompt.md`; a call containing `cat input/brief.md`, `cat /workspace/scratch/a75c3a6d9076/alps-v070-assessment/common/agent-skills-format.md`, and `ls input`; `cat input/release_tool.py`; and `cat /workspace/scratch/a75c3a6d9076/alps-v070-assessment/frozen/skill-creator/SKILL.md`. Each returned exit 0 and the requested content. The input listing contained only `brief.md` and `release_tool.py`.

Format check:

```bash
python3 /workspace/scratch/a75c3a6d9076/alps-v070-assessment/frozen/skill-creator/scripts/quick_validate.py deliverables/skills/release-checkout
```

Observed output: `Skill is valid!`; exit 0.

Configuration and resource check:

```bash
python3 - <<'PY'
import json
from pathlib import Path
root = Path('deliverables/skills/release-checkout')
cfg = json.loads((root / 'assets/release-request.json').read_text())
assert set(cfg) == {'environment', 'environment_path', 'state_path', 'candidate_id', 'request_id', 'authorized_operations', 'authorization_source'}
assert cfg['authorized_operations'] == []
assert all(v is None for k, v in cfg.items() if k != 'authorized_operations')
for name in ['assets/release-request.json', 'references/tool-contract.md']:
    assert (root / name).is_file()
    assert f']({name})' in (root / 'SKILL.md').read_text()
print('PASS: configuration parses, defaults confer no authorization, and both supporting resources are linked and present.')
PY
```

Observed output: `PASS: configuration parses, defaults confer no authorization, and both supporting resources are linked and present.`; exit 0.

## Design choices and verification limits

The Skill directly connects to the existing Python command. A wrapper would add no required capability. The supporting JSON is an agent-readable request template, explicitly not a new input format for the command. All identity and authorization fields are unbound by default.

The workflow preserves current valid qualification rather than invalidating approval through an unnecessary new qualification; binds approval to candidate digest and qualification sequence; permits preparatory work when owner approval is missing; and recovers uncertain effects through request-status and a stable request ID. It requires independent post-promotion health and checkout observations on the intended revision. Reporting distinguishes a blocked or failed release from an achieved outcome.

The tool source was reviewed against these instructions. No behavioral forward test or release simulation was performed: the brief supplies no business state, candidate, target environment binding, or per-application authorization and requests no demonstration. Format and resource checks do not prove runtime agent decisions or actual release success. No live service was accessed. The environment's state-to-target mapping must be supplied for each application because the tool has no environment-discovery operation. Saving is handled by the parent.
~~~~~
