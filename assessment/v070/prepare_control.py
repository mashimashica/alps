"""Prepare the original independent C-control creator assignments.

This assessment-only helper preserves the preselected control allocation and
common C authoring conditions. It never executes trials or materializes consumer
inputs, and it does not satisfy the qualifying-B prerequisite for main A/B.
"""

import argparse
import csv
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent
CASES = ("S01", "S03", "S05", "S06", "S09", "S10")
SETTINGS = tuple((model, effort) for model in ("gpt-5.6-luna", "gpt-5.6-sol", "gpt-6-astra")
                 for effort in ("low", "high"))
SCHEDULE_FIELDS = ("trial_id", "stage", "case", "arm", "repetition", "model", "effort")


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    ledger = ROOT / "control-list.tsv"
    schedule = ROOT / "control-schedule.tsv"
    digest = ROOT / "control-schedule-sha256.txt"
    assignments = ROOT / "control-assignments"
    rows = []
    for case in CASES:
        for model, effort in SETTINGS:
            for repetition in (1, 2):
                trial_id = f"control-{len(rows)+1:03}"
                rows.append([trial_id, "control", case, "C", repetition, model, effort])
    if len(rows) != 72:
        raise SystemExit("Schedule does not match the prospective 72 C creators")

    # The original main helper also assigns C cells. Preserve either preparation
    # and any partial output; reconciliation must not silently assign them twice.
    destinations = [ledger, schedule, digest, assignments,
                    ROOT / "main-list.tsv", ROOT / "main-schedule.tsv"]
    destinations.extend(ROOT / "trials" / row[0] for row in rows)
    for path in destinations:
        if path.exists() or path.is_symlink():
            raise SystemExit(f"Assignments or preparation already exist; preserve them: {path}")

    bank = ROOT / "frozen/main-cases"
    hashes = json.loads((ROOT / "main-case-hashes.json").read_text(encoding="utf-8"))
    if not bank.is_dir():
        raise SystemExit("Missing frozen public case bank")
    bank_paths = tuple(bank.rglob("*"))
    if any(path.is_symlink() for path in bank_paths):
        raise SystemExit("Frozen public case bank contains an unexpected symlink")
    actual_files = {path.relative_to(bank).as_posix() for path in bank_paths if path.is_file()}
    if actual_files != set(hashes):
        raise SystemExit("Frozen public case file set differs from main-case-hashes.json")
    for relative, expected in hashes.items():
        if hashlib.sha256((bank / relative).read_bytes()).hexdigest() != expected:
            raise SystemExit(f"Frozen public case changed: {relative}")
    for resource in (ROOT / "frozen/skill-creator/SKILL.md",
                     ROOT / "common/agent-skills-format.md"):
        if not resource.is_file():
            raise SystemExit(f"Missing common authoring resource: {resource}")

    assignments.mkdir(exist_ok=False)
    for row in rows:
        trial_id, stage, case, arm, repetition, model, effort = row
        trial = ROOT / "trials" / trial_id
        trial.mkdir(parents=True, exist_ok=False)
        inputs = trial / "input"
        shutil.copytree(bank / case, inputs)
        deliverables = trial / "deliverables"
        (deliverables / "skills").mkdir(parents=True)
        support = f"""The same frozen authoring aid at {ROOT}/frozen/skill-creator/SKILL.md and its resources is available if useful, not obligatory. Use that copy rather than another version; this is not a personal installation request. Read {ROOT}/common/agent-skills-format.md for the common physical-format orientation."""
        prompt = f"""Complete the Agent Skill creation request in {inputs}/brief.md, using the supplied raw material in {inputs}. Write the reusable self-contained Skill folder under {deliverables}/skills, choosing a suitable name. Keep any other expressly requested demonstration or revised work products elsewhere under {deliverables}. Do not add a separate demonstration unless the brief requests it. {support}

Work only on this task. Use {trial} as the working directory for every shell command, and keep authored files and disposable verification state inside this task directory. Read only your input folder, supplied authoring resources and needed official Agent Skills format sources. Do not enumerate the workspace or parent directories. Do not inspect sibling trials, consumer cases, evaluation plans, oracles, audits, other worktrees, GitHub PRs/history or unrelated resources. Do not delegate. This is one fresh authoring task; shared filesystem access does not authorize reading other work.

Use apply_patch for authored files. Available Python standard-library commands, shell, supplied local capabilities and frozen authoring helpers may support authorized local verification in your own folder. Leave all supplied inputs unchanged. External writes, personal installation, live business actions, and sending messages are not authorized. The parent saves your artifact through GitHub; do not commit, push, publish or upload it yourself. Synthetic demonstrations are allowed only to the extent requested by the brief.

Write {trial}/execution-note.md outside the target Skill. Record public commands, observed outputs and exit codes of checks actually performed, supplied authoring resources actually used, key design choices, and missing information or unperformed checks. This is a public handoff, not target Skill content; do not include private reasoning. In your final response identify the generated Skill and other requested outputs, with their verification limits.
"""
        with (trial / "prompt.md").open("x", encoding="utf-8") as stream:
            stream.write(prompt)
        input_hashes = {path.relative_to(trial).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                        for path in sorted(inputs.rglob("*")) if path.is_file()}
        expected_inputs = {"input/" + relative.removeprefix(case + "/"): expected
                           for relative, expected in hashes.items() if relative.startswith(case + "/")}
        if input_hashes != expected_inputs:
            raise SystemExit(f"Copied public input differs from the frozen bank: {trial_id}")
        assignment = {"trial_id": trial_id, "stage": stage, "case": case, "arm": arm,
                      "repetition": repetition, "requested_model": model,
                      "requested_effort": effort, "context": "fresh",
                      "input_sha256": input_hashes,
                      "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest()}
        # Coordinator metadata is not part of the creator's task context.
        with (assignments / f"{trial_id}.json").open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(assignment, indent=2) + "\n")

    # The immutable schedule fixes the denominator independently of status edits.
    with schedule.open("x", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
        writer.writerow(SCHEDULE_FIELDS)
        writer.writerows(rows)
    with digest.open("x", encoding="utf-8") as stream:
        stream.write(hashlib.sha256(schedule.read_bytes()).hexdigest() + "\n")
    schedule.chmod(0o444)
    digest.chmod(0o444)
    with ledger.open("x", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
        writer.writerow((*SCHEDULE_FIELDS, "execution", "agent"))
        writer.writerows([*row, "not started", ""] for row in rows)
    print("Prepared 72 independent C creator assignments; no trials executed or consumer inputs materialized")


if __name__ == "__main__":
    main()
