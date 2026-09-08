# Execution note: checkout service release Skill

## Deliverables

- `deliverables/skills/release-checkout-service/SKILL.md`
- `deliverables/skills/release-checkout-service/agents/openai.yaml`

No wrapper script was added. The supplied CLI already provides the required operations, structured JSON, meaningful exit codes, idempotent promotion identity, and request-status recovery. No separate demonstration was requested or added.

## Authoring resources used

- `input/brief.md` supplied the target work, authorization boundary, required success conditions, and available operations.
- `input/release_tool.py` supplied the actual local interface, state transitions, matching rules, outputs, and exit codes.
- `../../common/agent-skills-format.md` supplied the common physical-format orientation.
- `../../frozen/skill-creator/SKILL.md` and `../../frozen/skill-creator/references/openai_yaml.md` guided Skill packaging and host configuration.
- `../../frozen/alps/skills/design-process-description/SKILL.md`, `references/process-framework.md`, and `references/SKILL-template.md` supplied the Process Description form, Outcome rules, Markdown rules, and evaluation distinctions.
- `../../frozen/alps/skills/design-agent-work-system/SKILL.md`, `references/agent-work-system-design.md`, and `references/examples.md` supplied the allocation, interface, state-change recovery, and verification guidance.
- The official Agent Skills specification at `https://agentskills.io/specification` and script guide at `https://agentskills.io/skill-creation/using-scripts` were read on 2026-09-08 for the current format and existing-command guidance.

## Key design choices

- The Skill treats candidate ID plus observed digest as the release identity.
- It preserves an already valid qualification and subsequent matching owner approval because rerunning qualification changes its sequence and makes the older approval stale.
- It assigns interpretation and release judgment to the agent while using the supplied CLI directly for state inspection, qualification, promotion, recovery, and production observations.
- It requires one retained request ID and a `request-status` lookup before any retry after an uncertain promotion response.
- It evaluates promotion, health, and checkout separately and requires both post-promotion production checks to name the expected revision.
- Missing approval blocks only promotion. Authorized inspection, qualification, and preparation of an assessment can continue.
- `agents/openai.yaml` provides a display name, short description, and default prompt. Automatic invocation remains at its default behavior.

## Checks performed

All shell commands below were run from `/workspace/scratch/a75c3a6d9076/alps-v070-assessment/trials/focus-010`. Disposable state files were created under `verification/` from a base candidate `checkout-42`, digest `sha256:abc42`, passed qualification sequence `1`, and matching owner approval sequence `2`.

### Supplied validator

Initial command:

```bash
python3 ../../frozen/skill-creator/scripts/quick_validate.py deliverables/skills/release-checkout-service
```

Observed output:

```text
Unexpected key(s) in SKILL.md frontmatter: compatibility. Allowed properties are: allowed-tools, description, license, metadata, name
```

Exit code: `1`. The Python/environment requirement was moved from `compatibility` frontmatter into the Skill body to remain compatible with the supplied frozen validator.

The same command was run again after the correction. Observed output:

```text
Skill is valid!
```

Exit code: `0`.

### Host configuration and package structure

Command:

```bash
python3 - <<'PY'
from pathlib import Path
import yaml
path = Path("deliverables/skills/release-checkout-service/agents/openai.yaml")
data = yaml.safe_load(path.read_text())
assert set(data) == {"interface"}
assert 25 <= len(data["interface"]["short_description"]) <= 64
assert "$release-checkout-service" in data["interface"]["default_prompt"]
print("openai.yaml parsed; interface fields and lengths valid")
PY
```

Observed output: `openai.yaml parsed; interface fields and lengths valid`. Exit code: `0`.

Command:

```bash
python3 - <<'PY'
from pathlib import Path
root = Path("deliverables/skills/release-checkout-service")
skill = (root / "SKILL.md").read_text()
assert len(skill.splitlines()) < 500
assert not list(root.rglob("README.md"))
print(f"SKILL.md lines={len(skill.splitlines())}; no README or bundled script")
PY
```

Observed output: `SKILL.md lines=93; no README or bundled script`. Exit code: `0`.

Command: `command -v skills-ref`. Observed output: none. Exit code: `1`; the official `skills-ref` executable was unavailable.

Final package command:

```bash
find deliverables -type f -print | sort
test -f execution-note.md
test ! -e verification
```

Observed output:

```text
deliverables/skills/release-checkout-service/SKILL.md
deliverables/skills/release-checkout-service/agents/openai.yaml
```

Exit code: `0`. The two Skill files and execution note were present, and the disposable verification directory had been removed.

### Synthetic CLI component trials

The commands were invoked through a shell helper that ran the command and printed `exit_code=$?` immediately afterward.

Normal promotion and production checks:

```bash
python3 input/release_tool.py --state verification/happy.json inspect
python3 input/release_tool.py --state verification/happy.json promote --candidate checkout-42 --request-id req-happy-42
python3 input/release_tool.py --state verification/happy.json probe
python3 input/release_tool.py --state verification/happy.json checkout
```

Material observed outputs and exit codes:

- `inspect`: candidate `checkout-42` / `sha256:abc42`, passed qualification sequence `1`, matching owner approval sequence `2`, production `checkout-41` / `sha256:old41`; exit `0`.
- `promote`: `{"candidate":"checkout-42","digest":"sha256:abc42","promoted":true}`; exit `0`.
- `probe`: expected production revision and `"ok":true`; exit `0`.
- `checkout`: expected production revision and `"ok":true`; exit `0`.

Timeout recovery with the same request ID:

```bash
python3 input/release_tool.py --state verification/timeout.json promote --candidate checkout-42 --request-id req-timeout-42
python3 input/release_tool.py --state verification/timeout.json request-status --request-id req-timeout-42
python3 input/release_tool.py --state verification/timeout.json probe
python3 input/release_tool.py --state verification/timeout.json checkout
```

Material observed outputs and exit codes:

- `promote`: `{"error":"response timeout; operation effect unconfirmed by this response","request_id":"req-timeout-42"}`; exit `75`.
- `request-status`: recorded `checkout-42` / `sha256:abc42` with `"promoted":true`; exit `0`.
- `probe` and `checkout`: expected revision and `"ok":true`; exits `0` and `0`.

Healthy service with failed checkout:

```bash
python3 input/release_tool.py --state verification/checkout-fail.json promote --candidate checkout-42 --request-id req-checkout-fail-42
python3 input/release_tool.py --state verification/checkout-fail.json probe
python3 input/release_tool.py --state verification/checkout-fail.json checkout
```

Material observed outputs and exit codes:

- `promote`: `"promoted":true`; exit `0`.
- `probe`: expected revision and `"ok":true`; exit `0`.
- `checkout`: expected revision and `"ok":false`; exit `2`.

Requalification and stale approval:

```bash
cp verification/happy.json verification/requalified.json
python3 input/release_tool.py --state verification/requalified.json qualify --candidate checkout-42
python3 input/release_tool.py --state verification/requalified.json inspect
python3 input/release_tool.py --state verification/requalified.json promote --candidate checkout-42 --request-id req-stale-approval-42
```

Material observed outputs and exit codes:

- `qualify`: passed qualification sequence changed to `3`; exit `0`.
- `inspect`: qualification sequence `3`, while approval still cited qualification sequence `1` and had sequence `2`; exit `0`.
- `promote`: `{"error":"qualified candidate and subsequent matching owner approval required"}`; exit `2`.

## Verification limits and missing information

- The supplied validator checks physical form and frontmatter; it does not establish the quality of release decisions.
- The official `skills-ref` validator was not available, so it was not run.
- The CLI trials exercise representative success, uncertain-effect recovery, checkout failure, and stale-approval behavior in local synthetic state only. Candidate-ID mismatch, failed qualification, absent approval, request-ID collision, truncated output, and concurrent state change were not executed as separate trials.
- No independent agent forward test was run because delegation was prohibited for this task. The trials therefore verify the underlying interface and selected invariants, not every possible agent interpretation or prompt.
- No live repository, deployment service, or customer state was accessed. Live deployment behavior and effectiveness remain untested and outside this Skill's scope.
