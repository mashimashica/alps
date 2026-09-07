"""Prepare task-local creator briefs, not consumer inputs or grading oracles."""

import csv
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SETTINGS = (("gpt-5.6-luna", "low"), ("gpt-5.6-sol", "high"))


def main():
    rows = []
    for case in ("S01", "S05", "S10"):
        for model, effort in SETTINGS:
            for arm in ("A", "C"):
                trial_id = f"cal-{len(rows)+1:03}"
                trial = ROOT / "trials" / trial_id
                trial.mkdir(parents=True, exist_ok=False)
                inputs = trial / "input"
                shutil.copytree(ROOT / "cases" / case, inputs)
                (trial / "output").mkdir()
                creator = ROOT / "frozen/skill-creator"
                format_doc = ROOT / "common/agent-skills-format.md"
                support = f"The frozen authoring aid at {creator}/SKILL.md and its resources is available if useful. Use that copy, not another version. It is not a personal installation request. Read {format_doc} for the common format orientation."
                if arm == "A":
                    selected = "design-process-description" if case == "S01" else "design-agent-work-system"
                    support += f" Use the relevant design guidance at {ROOT}/frozen/alps/skills/{selected}/SKILL.md and follow its required sources. Its linked sibling design Skill and other relevant packaged resources are available when needed."
                prompt = f"""Create the Agent Skill requested in {inputs}/brief.md. Put the self-contained Skill folder under {trial}/output, choosing a suitable name. Supporting local environment files, when supplied, are in {inputs}. {support}

Work only on this task. Read only your input folder, the supplied common/frozen authoring resources and required official Agent Skills format sources. Do not inspect sibling trials, evaluation plans, other worktrees, audit reports, hidden expected results, GitHub PRs/history or unrelated resources. Do not delegate; complete this as one fresh authoring task. Filesystem isolation here is a task boundary, not permission to access other task artifacts.

Use apply_patch for authored files. You may use the available Python standard library, shell and frozen authoring helpers for local verification within your own folder. External writes, personal installation, sending business messages and live business actions are not authorized. Do not modify supplied sources. The parent will save the generated artifact to the assessment evidence branch; do not commit, push, publish or upload it yourself.

Outside the Skill folder, write {trial}/execution-note.md recording the public commands/checks actually performed, which supplied authoring resources you used, key design decisions, and any unperformed checks or missing information. This note is an execution handoff, not part of the target Skill. Do not include private chain-of-thought. In your final response identify the created folder and what remains unverified. Do not perform a specific future business application not requested by the brief.
"""
                (trial / "prompt.md").write_text(prompt, encoding="utf-8")
                hashes = {str(p.relative_to(trial)): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs.rglob("*") if p.is_file()}
                metadata = {"trial_id": trial_id, "case": case, "arm": arm, "requested_model": model, "requested_effort": effort, "context": "fresh", "input_sha256": hashes, "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest()}
                (trial / "assignment.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
                rows.append([trial_id, "calibration", "creator", case, arm, model, effort, "not started", ""])
    with (ROOT / "trial-list.tsv").open("x", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t")
        writer.writerow(["trial_id", "stage", "role", "case", "arm", "model", "effort", "execution", "agent"])
        writer.writerows(rows)
    print(f"Prepared {len(rows)} creator tasks; no consumer case or oracle materialized")


if __name__ == "__main__":
    main()
