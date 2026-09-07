"""Prepare the eight preregistered H01 creator tasks without consumer answers."""

import csv
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CELLS = (("S10", "A", 1), ("S10", "B1", 1),
         ("S10", "B1", 2), ("S10", "A", 2),
         ("S08", "A", 1), ("S08", "B1", 1),
         ("S05", "B1", 1), ("S05", "A", 1))


def main():
    ledger = ROOT / "dev1-list.tsv"
    if ledger.exists():
        raise SystemExit("Already prepared; inspect the existing ledger instead of overwriting trials")
    candidate = ROOT / "frozen/candidate-B1"
    if not (candidate / "skills/design-agent-work-system/SKILL.md").is_file():
        raise SystemExit("Freeze and review candidate-B1 first")
    rows = []
    for index, (case, arm, repetition) in enumerate(CELLS, 1):
        trial_id = f"dev1-{index:03}"
        trial = ROOT / "trials" / trial_id
        trial.mkdir(parents=True, exist_ok=False)
        inputs = trial / "input"
        source = ROOT / ("main-cases" if case == "S08" else "cases") / case
        shutil.copytree(source, inputs)
        (trial / "output").mkdir()
        alps = ROOT / "frozen" / ("alps" if arm == "A" else "candidate-B1")
        prompt = f"""Create the Agent Skill requested in {inputs}/brief.md. Put the self-contained Skill folder under {trial}/output, choosing a suitable name. Supporting local environment files, when supplied, are in {inputs}.

The frozen authoring aid at {ROOT}/frozen/skill-creator/SKILL.md and its resources is available if useful. Use that copy, not another version; this is not a personal installation request. Read {ROOT}/common/agent-skills-format.md for common physical-format orientation. Use {alps}/skills/design-agent-work-system/SKILL.md and its required sources. Its linked sibling design Skill and relevant packaged resources are available when needed.

Work only on this task. Read only your input folder, the supplied authoring resources and required official Agent Skills format sources. Do not inspect sibling trials, evaluation plans, other worktrees, audit reports, expected results, GitHub PRs/history or unrelated resources. Do not delegate. This is one fresh authoring task; shared filesystem access does not authorize reading other tasks.

Use apply_patch for authored files. Python standard library, shell and frozen authoring helpers are available for local verification inside your own folder. Do not modify supplied input. External writes, personal installation, sending business messages and live business actions are not authorized. The parent saves your artifact through GitHub; do not commit, push, publish or upload it yourself.

Write {trial}/execution-note.md outside the target Skill, recording public commands/checks actually performed, supplied authoring resources actually used, key design choices and unperformed checks. This is a handoff, not target Skill content; do not include private reasoning. Do not perform a future business instance beyond verification requested by the brief. In your final response identify the created folder and remaining verification limits.
"""
        (trial / "prompt.md").write_text(prompt, encoding="utf-8")
        hashes = {p.relative_to(trial).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in sorted(inputs.rglob("*")) if p.is_file()}
        assignment = {"trial_id": trial_id, "stage": "development-1", "case": case,
                      "arm": arm, "repetition": repetition, "requested_model": "gpt-5.6-luna",
                      "requested_effort": "low", "context": "fresh", "input_sha256": hashes,
                      "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest()}
        (trial / "assignment.json").write_text(json.dumps(assignment, indent=2) + "\n")
        rows.append([trial_id, case, arm, repetition, "gpt-5.6-luna", "low", "not started", ""])
    with ledger.open("x", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
        writer.writerow(["trial_id", "case", "arm", "repetition", "model", "effort", "execution", "agent"])
        writer.writerows(rows)
    print(f"Prepared {len(rows)} fresh H01 authoring tasks; no consumer fixtures or gold materialized")


if __name__ == "__main__":
    main()
