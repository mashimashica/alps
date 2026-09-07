"""Prepare the prospectively specified main/control creator tasks.

Requires an explicit frozen B identity after development selection. This helper
only packages assignments; it never executes trials or judges their success.
"""

import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parent
SETTINGS = tuple((model, effort) for model in ("gpt-5.6-luna", "gpt-5.6-sol", "gpt-6-astra")
                 for effort in ("low", "high"))
CONTROL = {"S01", "S03", "S05", "S06", "S09", "S10"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", required=True,
                        help="Selected immutable directory name under frozen/, documented in main-candidate-selection.md")
    args = parser.parse_args()
    if not re.fullmatch(r"candidate-[A-Za-z0-9-]+", args.candidate):
        raise SystemExit("An explicit frozen candidate identity is required")
    if not (ROOT / "main-candidate-selection.md").is_file():
        raise SystemExit("Document the bounded development decision before preparing main")
    ledger = ROOT / "main-list.tsv"
    if ledger.exists() or ledger.is_symlink():
        raise SystemExit("Main assignments already exist; preserve their identities")
    control_ledger = ROOT / "control-list.tsv"
    if control_ledger.exists() or control_ledger.is_symlink():
        raise SystemExit("Independent C assignments already exist; future A/B preparation must preserve those C cells")
    # Either preparation can stop before its ledger is written. Preserve partial
    # owned output too, before creating any new main or duplicate C assignments.
    destinations = [ROOT / name for name in (
        "main-schedule.tsv", "main-schedule-sha256.txt", "main-candidate-hashes.json",
        "control-schedule.tsv", "control-schedule-sha256.txt", "control-assignments")]
    trials = ROOT / "trials"
    if trials.is_symlink() or (trials.exists() and not trials.is_dir()):
        raise SystemExit(f"Unexpected trial directory; preserve it: {trials}")
    for pattern in ("control-[0-9][0-9][0-9]", "main-[0-9][0-9][0-9]"):
        destinations.extend(trials.glob(pattern))
    for path in destinations:
        if path.exists() or path.is_symlink():
            raise SystemExit(f"Assignments or partial preparation already exist; preserve their cells: {path}")
    candidate = ROOT / "frozen" / args.candidate
    for skill in ("design-process-description", "design-agent-work-system"):
        if not (candidate / "skills" / skill / "SKILL.md").is_file():
            raise SystemExit(f"Missing selected frozen source: {skill}")
    bank = ROOT / "frozen/main-cases"
    hashes = json.loads((ROOT / "main-case-hashes.json").read_text())
    for relative, expected in hashes.items():
        if hashlib.sha256((bank / relative).read_bytes()).hexdigest() != expected:
            raise SystemExit(f"Frozen public case changed: {relative}")
    candidate_hashes = {p.relative_to(candidate).as_posix(): hashlib.sha256(
        str(p.readlink()).encode() if p.is_symlink() else p.read_bytes()).hexdigest()
        for p in sorted(candidate.rglob("*")) if p.is_file() or p.is_symlink()}
    rows = []
    for case_index in range(1, 13):
        case = f"S{case_index:02}"
        for configuration, (model, effort) in enumerate(SETTINGS):
            for repetition in (1, 2):
                # Fixed alternation balances adjacent A/B order without inspecting results.
                arms = ("A", "B") if (case_index + configuration + repetition) % 2 == 0 else ("B", "A")
                if case in CONTROL:
                    arms = (*arms, "C")
                for arm in arms:
                    trial_id = f"main-{len(rows)+1:03}"
                    trial = ROOT / "trials" / trial_id
                    trial.mkdir(parents=True, exist_ok=False)
                    inputs = trial / "input"
                    shutil.copytree(bank / case, inputs)
                    deliverables = trial / "deliverables"
                    (deliverables / "skills").mkdir(parents=True)
                    support = f"""The same frozen authoring aid at {ROOT}/frozen/skill-creator/SKILL.md and its resources is available if useful, not obligatory. Use that copy rather than another version; this is not a personal installation request. Read {ROOT}/common/agent-skills-format.md for the common physical-format orientation."""
                    if arm != "C":
                        source = ROOT / "frozen" / ("alps" if arm == "A" else args.candidate)
                        if case_index <= 4:
                            guidance = f"Use {source}/skills/design-process-description/SKILL.md and its required sources. Its linked sibling design Skill and relevant packaged resources are available when needed."
                        elif case_index <= 8:
                            guidance = f"Use {source}/skills/design-agent-work-system/SKILL.md and its required sources. Its linked sibling design Skill and relevant packaged resources are available when needed."
                        else:
                            guidance = f"Use the relevant guidance in {source}/skills/design-process-description/SKILL.md and {source}/skills/design-agent-work-system/SKILL.md, with their required sources, for the requested design subjects."
                        support += " " + guidance
                    prompt = f"""Complete the Agent Skill creation request in {inputs}/brief.md, using the supplied raw material in {inputs}. Write the reusable self-contained Skill folder under {deliverables}/skills, choosing a suitable name. Keep any other expressly requested demonstration or revised work products elsewhere under {deliverables}. Do not add a separate demonstration unless the brief requests it. {support}

Work only on this task. Read only your input folder, supplied authoring resources and needed official Agent Skills format sources. Do not inspect sibling trials, consumer cases, evaluation plans, oracles, audits, other worktrees, GitHub PRs/history or unrelated resources. Do not delegate. This is one fresh authoring task; shared filesystem access does not authorize reading other work.

Use apply_patch for authored files. Available Python standard-library commands, shell, supplied local capabilities and frozen authoring helpers may support authorized local verification in your own folder. Leave all supplied inputs unchanged. External writes, personal installation, live business actions, and sending messages are not authorized. The parent saves your artifact through GitHub; do not commit, push, publish or upload it yourself. Synthetic demonstrations are allowed only to the extent requested by the brief.

Write {trial}/execution-note.md outside the target Skill. Record public commands, observed outputs and exit codes of checks actually performed, supplied authoring resources actually used, key design choices, and missing information or unperformed checks. This is a public handoff, not target Skill content; do not include private reasoning. In your final response identify the generated Skill and other requested outputs, with their verification limits.
"""
                    (trial / "prompt.md").write_text(prompt, encoding="utf-8")
                    input_hashes = {p.relative_to(trial).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                                    for p in sorted(inputs.rglob("*")) if p.is_file()}
                    assignment = {"trial_id": trial_id, "stage": "control" if arm == "C" else "main",
                                  "case": case, "arm": arm, "repetition": repetition,
                                  "requested_model": model, "requested_effort": effort, "context": "fresh",
                                  "input_sha256": input_hashes,
                                  "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest()}
                    (trial / "assignment.json").write_text(json.dumps(assignment, indent=2) + "\n")
                    rows.append([trial_id, assignment["stage"], case, arm, repetition, model, effort, "not started", ""])
    if len(rows) != 360 or sum(row[1] == "main" for row in rows) != 288:
        raise SystemExit("Schedule does not match prospective main/control counts")
    with ledger.open("x", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
        writer.writerow(["trial_id", "stage", "case", "arm", "repetition", "model", "effort", "execution", "agent"])
        writer.writerows(rows)
    # The execution ledger changes status; this independent schedule fixes the
    # prospective denominator and is checkpointed before the first creator.
    schedule = ROOT / "main-schedule.tsv"
    with schedule.open("x", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
        writer.writerow(["trial_id", "stage", "case", "arm", "repetition", "model", "effort"])
        writer.writerows(row[:7] for row in rows)
    (ROOT / "main-schedule-sha256.txt").write_text(hashlib.sha256(schedule.read_bytes()).hexdigest() + "\n")
    (ROOT / "main-candidate-hashes.json").write_text(
        json.dumps({"identity": args.candidate, "files": candidate_hashes}, indent=2) + "\n")
    print("Prepared 288 main and 72 C creator assignments; no trials executed or consumer inputs materialized")


if __name__ == "__main__":
    main()
