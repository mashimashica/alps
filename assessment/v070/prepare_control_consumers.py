"""Package the two prescribed fresh consumers for explicitly completed C creators.

Assessment bookkeeping only. Source identity and copied bytes are checked, not
Skill quality. Partial preparation is retained for explicit reconciliation.
"""

import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import shutil
import stat

from control_ledger_state import prepare as prepare_ledger

ROOT = Path(__file__).resolve().parent
SCHEDULE_SHA256 = "739210b57f1b000dcb3cf6f4e2ee912ca6e911d8e829eacde225bb03ffe91569"
CASE_BANK_SHA256 = "f26be07f6cfba54aedc3068a67ae32292877f6ee005f0c190156f5786d1cbdc2"
FIELDS = ("trial_id", "stage", "case", "arm", "repetition", "model", "effort")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checked_path(path):
    """Reject symlinks, including dangling links in any owned path component."""
    for part in (path, *path.parents):
        if part.is_symlink():
            raise ValueError(f"Unexpected symlink; preserve it: {part}")
        if part == ROOT:
            break
    return path


def file_hashes(folder):
    checked_path(folder)
    if not folder.is_dir():
        raise ValueError(f"Missing regular directory: {folder}")
    result = {}
    for path in sorted(folder.rglob("*")):
        checked_path(path)
        if path.is_file():
            result[path.relative_to(folder).as_posix()] = digest(path)
        elif not path.is_dir():
            raise ValueError(f"Unsupported filesystem entry: {path}")
    return result


def verify_bank(folder, manifest):
    checked_path(manifest)
    expected = json.loads(manifest.read_text(encoding="utf-8"))
    if file_hashes(folder) != expected:
        raise ValueError(f"Frozen file set or bytes changed: {folder}")
    return expected


def rows(path):
    checked_path(path)
    with path.open(newline="", encoding="utf-8") as stream:
        data = list(csv.DictReader(stream, delimiter="\t"))
    if len({row["trial_id"] for row in data}) != len(data):
        raise ValueError(f"Duplicate trial ID: {path}")
    return {row["trial_id"]: row for row in data}


def completed_creators(creator_ids):
    if len(set(creator_ids)) != len(creator_ids) or not all(
        re.fullmatch(r"control-\d{3}", value) for value in creator_ids
    ):
        raise ValueError("Use distinct explicit control-NNN creator IDs")
    schedule = ROOT / "control-schedule.tsv"
    schedule_digest = ROOT / "control-schedule-sha256.txt"
    checked_path(schedule)
    checked_path(schedule_digest)
    if digest(schedule) != SCHEDULE_SHA256 or schedule_digest.read_text().strip() != SCHEDULE_SHA256:
        raise ValueError("The fixed 72-cell C schedule identity changed")
    scheduled = rows(schedule)
    ledger = rows(ROOT / "control-list.tsv")
    if len(scheduled) != 72 or set(ledger) != set(scheduled):
        raise ValueError("Creator ledger no longer covers the fixed 72 cells")
    if any(any(ledger[key].get(field) != row[field] for field in FIELDS)
           for key, row in scheduled.items()):
        raise ValueError("Creator ledger assignment differs from the fixed schedule")
    for creator_id in creator_ids:
        if creator_id not in ledger or ledger[creator_id].get("execution") != "completed":
            raise ValueError(f"Creator completion is not explicitly recorded: {creator_id}")
    return {key: scheduled[key] for key in creator_ids}


def skill_path(creator_id):
    container = checked_path(ROOT / "trials" / creator_id / "deliverables/skills")
    if not container.is_dir():
        raise ValueError(f"Missing generated Skill directory: {creator_id}")
    targets = []
    for path in container.iterdir():
        checked_path(path)
        if path.is_dir() and (path / "SKILL.md").is_file():
            checked_path(path / "SKILL.md")
            targets.append(path)
    if len(targets) != 1:
        raise ValueError(f"Expected exactly one supplied Skill: {creator_id}")
    return targets[0]


def artifact_inventory(skill):
    resources, caches = {}, {}
    for relative, value in file_hashes(skill).items():
        path = Path(relative)
        stored_parts = (skill.name, *path.parts)
        if any(part in {".git", ".local"} for part in stored_parts):
            raise ValueError(f"Checkpoint would omit a resource at this path; preserve and reconcile it: {skill / relative}")
        if path.parent.name == "__pycache__" and path.suffix == ".pyc":
            caches[relative] = value
        elif "__pycache__" in stored_parts:
            raise ValueError(f"Checkpoint would omit a non-cache resource; preserve and reconcile it: {skill / relative}")
        else:
            resources[relative] = value
    return resources, caches


def ignore_runtime_caches(directory, names):
    if Path(directory).name != "__pycache__":
        return []
    return [name for name in names if Path(name).suffix == ".pyc" and (Path(directory) / name).is_file()]


def refuse_existing(path):
    checked_path(path)
    if path.exists():
        raise ValueError(f"Complete or partial preparation already exists; preserve it: {path}")
    for parent in path.parents:
        if parent.exists() and not parent.is_dir():
            raise ValueError(f"Unexpected parent entry; preserve it: {parent}")
        if parent == ROOT:
            break


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("creator_ids", nargs="+")
    args = parser.parse_args()
    scheduled = completed_creators(args.creator_ids)
    public_hashes = verify_bank(ROOT / "frozen/main-cases", ROOT / "main-case-hashes.json")
    case_manifest = ROOT / "control-consumer-case-hashes.json"
    checked_path(case_manifest)
    if digest(case_manifest) != CASE_BANK_SHA256:
        raise ValueError("The independently reviewed consumer bank identity changed")
    verify_bank(ROOT / "control-consumer-cases", case_manifest)
    checked_path(ROOT / "frozen-hashes.sha256")
    common_hashes = {}
    for line in (ROOT / "frozen-hashes.sha256").read_text().splitlines():
        expected, relative = line.split("  ", 1)
        if relative.startswith("frozen/skill-creator/"):
            common_hashes[relative.removeprefix("frozen/skill-creator/")] = expected
    common_actual = file_hashes(ROOT / "frozen/skill-creator")
    display_assets = {"assets/skill-creator.png", "assets/skill-creator-small.svg"}
    if ("SKILL.md" not in common_hashes or set(common_actual) != set(common_hashes) | display_assets
            or any(common_actual.get(key) != value for key, value in common_hashes.items())):
        raise ValueError("The common frozen authoring aid file set or recorded bytes changed")

    plans = []
    for creator_id, row in scheduled.items():
        creator = ROOT / "trials" / creator_id
        assignment_path = checked_path(ROOT / "control-assignments" / f"{creator_id}.json")
        assignment = json.loads(assignment_path.read_text())
        expected_fields = {"trial_id": creator_id, "stage": "control", "case": row["case"],
                           "arm": "C", "repetition": int(row["repetition"]),
                           "requested_model": row["model"], "requested_effort": row["effort"],
                           "context": "fresh"}
        if any(assignment.get(key) != value for key, value in expected_fields.items()):
            raise ValueError(f"Creator metadata differs from the fixed schedule: {creator_id}")
        original_inputs = {relative.removeprefix(row["case"] + "/"): expected
                           for relative, expected in public_hashes.items()
                           if relative.startswith(row["case"] + "/")}
        if assignment["input_sha256"] != {"input/" + key: value for key, value in original_inputs.items()}:
            raise ValueError(f"Creator input identity differs from the frozen public bank: {creator_id}")
        if file_hashes(creator / "input") != original_inputs:
            raise ValueError(f"Original creator inputs changed: {creator_id}")
        checked_path(creator / "prompt.md")
        if digest(creator / "prompt.md") != assignment["prompt_sha256"]:
            raise ValueError(f"Original creator prompt changed: {creator_id}")
        skill = skill_path(creator_id)
        hashes, caches = artifact_inventory(skill)
        freeze = ROOT / "frozen/control-artifacts" / creator_id
        manifest = ROOT / "control-artifact-freezes" / f"{creator_id}.json"
        refuse_existing(freeze)
        refuse_existing(manifest)
        consumers = []
        number = int(creator_id.rsplit("-", 1)[1])
        for index, variant in enumerate(("ordinary", "challenging")):
            use_id = f"C-U{2 * (number - 1) + index + 1:03}"
            folder = ROOT / "consumers" / use_id
            for destination in (folder, ROOT / "consumer-assignments" / f"{use_id}.json",
                                ROOT / "consumer-setup" / f"{use_id}.json",
                                ROOT / "state-snapshots" / use_id):
                refuse_existing(destination)
            if any(ROOT.parent.glob(use_id + "-ledger-state-*")):
                raise ValueError(f"An existing or partial native state must be reconciled: {use_id}")
            source = ROOT / "control-consumer-cases" / row["case"] / variant
            source_hashes = file_hashes(source / "input")
            if "request.md" not in source_hashes:
                raise ValueError(f"Missing reviewed consumer request: {source}")
            request = (source / "input/request.md").read_text(encoding="utf-8")
            tokens = set(re.findall(r"\{\{[^{}]*\}\}", request))
            if tokens - {"{{INPUT_DIR}}", "{{STATE_PATH}}", "{{ENVIRONMENT_PATH}}"}:
                raise ValueError(f"Unrecognized request substitution: {source}")
            for token in tokens:
                request = request.replace(token, "resolved-path")
            if "{{" in request or "}}" in request:
                raise ValueError(f"Unresolved request token: {source}")
            if row["case"] == "S06" and "ledger_api.py" in source_hashes:
                raise ValueError("S06 interface must be supplied from the unchanged frozen public source")
            if row["case"] == "S10" and "release_tool.py" in source_hashes:
                raise ValueError("S10 interface must be supplied from the unchanged frozen public source")
            consumers.append((use_id, variant, folder, source, source_hashes))
        plans.append((creator_id, row, skill, hashes, caches, freeze, manifest, consumers))

    # All selected creators and owned destinations pass preflight before writes.
    # Any later failure retains its files; no automated overwrite or retry occurs.
    for creator_id, row, skill, hashes, caches, freeze, manifest, consumers in plans:
        freeze.mkdir(parents=True, exist_ok=False)
        frozen_skill = freeze / skill.name
        shutil.copytree(skill, frozen_skill, ignore=ignore_runtime_caches)
        if artifact_inventory(skill) != (hashes, caches) or file_hashes(frozen_skill) != hashes:
            raise ValueError(f"Artifact changed while freezing: {creator_id}")
        write_json(manifest, {"creator_id": creator_id, "source_path": str(skill),
                             "frozen_path": str(frozen_skill), "file_sha256": hashes,
                             "source_file_modes": {key: stat.S_IMODE((skill / key).stat().st_mode)
                                                   for key in hashes},
                             "excluded_runtime_cache_sha256": caches,
                             "cache_handling": "Regular *.pyc directly inside __pycache__ are retained in the original creator folder but omitted from the frozen/copy resources and durable checkpoint; their bytes are not claimed preserved",
                             "schedule_sha256": SCHEDULE_SHA256,
                             "case_bank_manifest_sha256": digest(case_manifest),
                             "scope": "Supplied Skill resources and bytes, with explicitly recorded Python runtime-cache exclusions; no quality judgment"})
        for use_id, variant, folder, source, source_hashes in consumers:
            folder.mkdir(parents=True, exist_ok=False)
            (folder / "work").mkdir()
            target = folder / "skill" / skill.name
            shutil.copytree(frozen_skill, target)
            if file_hashes(target) != hashes:
                raise ValueError(f"Consumer Skill copy differs from its frozen original: {use_id}")
            shutil.copytree(source / "input", folder / "input")
            if file_hashes(source / "input") != source_hashes or file_hashes(folder / "input") != source_hashes:
                raise ValueError(f"Reviewed input changed while copying: {use_id}")
            state = folder / "input/state.json"
            if row["case"] == "S06":
                shutil.copy2(ROOT / "frozen/main-cases/S06/ledger_api.py", folder / "input/ledger_api.py")
                if digest(folder / "input/ledger_api.py") != public_hashes["S06/ledger_api.py"]:
                    raise ValueError(f"S06 interface changed while copying: {use_id}")
                state = prepare_ledger(folder, source)
            elif row["case"] == "S10":
                shutil.copy2(ROOT / "frozen/main-cases/S10/release_tool.py", folder / "input/release_tool.py")
                if digest(folder / "input/release_tool.py") != public_hashes["S10/release_tool.py"]:
                    raise ValueError(f"S10 interface changed while copying: {use_id}")
            original_request = source / "input/request.md"
            body = original_request.read_text(encoding="utf-8")
            substitutions = []
            for token, value in (("{{INPUT_DIR}}", str(folder / "input")),
                                 ("{{STATE_PATH}}", str(state)),
                                 ("{{ENVIRONMENT_PATH}}", str(folder / "input"))):
                count = body.count(token)
                if count:
                    substitutions.append({"token": token, "value": value, "occurrences": count})
                    body = body.replace(token, value)
            if "{{" in body or "}}" in body:
                raise ValueError(f"Unresolved request path token: {use_id}")
            (folder / "input/request.md").write_text(body, encoding="utf-8")
            prompt = f"""Use the Skill at {target}/SKILL.md to complete the user's task in {folder}/input/request.md with any accompanying files in that input folder. Write the user-facing answer to {folder}/answer.md using apply_patch. Use {folder}/work for temporary processing and permitted local outputs.

This is an application of the supplied Skill, not a request to redesign, repair, install or publish it. Do not modify the Skill or supplied original inputs. If it cannot support the requested work, report the concrete limitation and perform only independently valid work. Do not change external state or send messages. Synthetic state changes are allowed only when the task explicitly authorizes them, using its supplied interface; do not edit simulation state directly.

You may consult the frozen skill-creator aid at {ROOT}/frozen/skill-creator/SKILL.md if useful. It is available, not required. Read only your supplied Skill and its needed resources, your task input, that common authoring aid and any necessary standard runtime documentation. Use {folder} as your task working directory; do not enumerate the shared workspace. Do not read creator prompts, execution notes, sibling trials, evaluation plans, audits, expected answers or other worktrees. Do not delegate. The parent handles durable saving; do not commit, push, upload or install anything.

Record actual public commands, exit codes, relevant stdout/stderr and files used in {folder}/execution-note.md. Distinguish exact captured observations from summaries and unperformed checks; do not include private reasoning. If no tool is needed, say so. Your final response should give the answer and identify any limitation, not merely say that files were created.
"""
            with (folder / "prompt.md").open("x", encoding="utf-8") as stream:
                stream.write(prompt)
            copied = {part + "/" + key: value for part in ("skill", "input")
                      for key, value in file_hashes(folder / part).items()}
            copied_modes = {key: stat.S_IMODE((folder / key).stat().st_mode) for key in copied}
            initial_state_evidence = {}
            if row["case"] == "S06":
                for relative in (f"consumer-setup/{use_id}.json",
                                 f"state-snapshots/{use_id}/initial.sql",
                                 f"state-snapshots/{use_id}/initial.json"):
                    initial_state_evidence[relative] = digest(checked_path(ROOT / relative))
            metadata = {"consumer_id": use_id, "creator_id": creator_id, "case": row["case"],
                        "variant": variant, "requested_model": "gpt-5.6-sol",
                        "requested_effort": "high", "context": "fresh",
                        "copied_sha256": copied, "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                        "copied_file_modes": copied_modes,
                        "initial_state_evidence_sha256": initial_state_evidence,
                        "artifact_freeze_manifest": str(manifest), "artifact_freeze_sha256": digest(manifest),
                        "case_bank_manifest_sha256": digest(case_manifest),
                        "request_source": str(original_request), "request_source_sha256": digest(original_request),
                        "request_substitutions": substitutions,
                        "common_authoring_aid_sha256": common_actual,
                        "common_aid_unrecorded_original_display_assets": sorted(display_assets),
                        "schedule_sha256": SCHEDULE_SHA256}
            write_json(ROOT / "consumer-assignments" / f"{use_id}.json", metadata)
            print(f"{use_id}: prepared from {creator_id}, {variant}; not started")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as error:
        raise SystemExit(str(error)) from error
