"""Copy one prescribed completed C packet for independent business assessment.

Evidence packaging only: no quality classification, source repair or model run.
Original packages and public observations remain unchanged.
"""

import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import shutil
import stat

from prepare_control_consumers import artifact_inventory, checked_path, ignore_runtime_caches

ROOT = Path(__file__).resolve().parent
ALLOCATION_SHA256 = "bb463eceeccea6502418daf3263558d386c8fd31f4b1dcfe4f5fba411c577a0f"
CASE_MANIFEST_SHA256 = "f26be07f6cfba54aedc3068a67ae32292877f6ee005f0c190156f5786d1cbdc2"
CREATOR_SCHEDULE_SHA256 = "739210b57f1b000dcb3cf6f4e2ee912ca6e911d8e829eacde225bb03ffe91569"
CONSUMER_SCHEDULE_SHA256 = "6321c8bbbfaf1dcd0c3ae6d118b52480c9f5e13897f34196fb1b547d7cd7a6c0"
BOUNDARIES = """# Evidence boundaries

Use only this assigned packet, its original business inputs and oracle, and the
common grading guidance. Experimental configuration mappings and other grades
are not supplied. Original content may retain path or style hints; do not infer
experimental identity or follow paths into other task folders.

Original-consumer-inputs are the independently fixed requests and evidence,
including hidden S06 setup fixtures for review only. Final-input-state is the
actual post-application copy. Committed-state preserves native initial/final SQL
for S06, not byte-identical SQLite or an attested call trace. Do not access live
original states. Probe components only through new disposable copies/databases,
and distinguish those checks from the recorded fresh consumer applications.

Answers and execution notes are preserved agent reports, not guaranteed complete
transcripts. Report unknown observations and unsupported claims explicitly.
Resource-observations compares the recorded original bytes and modes with the
final file inventory. Authorized S10 state changes need behavioral review;
removed temporary files and unrecorded access are not certified by that check.
Creator notes are reported checks, separate from independent observations.
Do not repair the evaluated Skill.

Judge requested-task adequacy, intended business results, applicable conditions,
and package defects separately. Good handling of initially missing evidence can
be adequate without achieving the business result. An avoidable self-created
block is not automatically appropriate handling. Count only distinct evidenced
corrections to erroneous or unusable instructions; ordinary business choices
and necessary interpretation are not corrections. Do not require ALPS headings,
jargon, a preferred report, or a particular valid implementation.
"""


def sha(path):
    return hashlib.sha256(checked_path(path).read_bytes()).hexdigest()


def read_json(path):
    return json.loads(checked_path(path).read_text())


def read_ledger(name, key):
    with checked_path(ROOT / name).open(newline="", encoding="utf-8") as stream:
        data = list(csv.DictReader(stream, delimiter="\t"))
    result = {row[key]: row for row in data}
    if len(result) != len(data):
        raise ValueError(f"Duplicate ledger identity: {name}")
    return result


def inventory(folder):
    return artifact_inventory(folder)[0]


def file_modes(folder):
    return {key: stat.S_IMODE((folder / key).stat().st_mode) for key in inventory(folder)}


def fixed_schedule(name, key, digest, ledger):
    source = ROOT / f"{name}-schedule.tsv"
    if (sha(source) != digest or
            (ROOT / f"{name}-schedule-sha256.txt").read_text().split()[0] != digest):
        raise ValueError(f"Fixed {name} schedule changed")
    planned = read_ledger(f"{name}-schedule.tsv", key)
    if set(planned) != set(ledger) or any(
        any(ledger[identity].get(field) != value for field, value in row.items())
        for identity, row in planned.items()
    ):
        raise ValueError(f"Mutable {name} ledger differs from fixed assignments")
    return planned


def copy_file(source, target):
    checked_path(source)
    checked_path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    if sha(source) != sha(target):
        raise ValueError(f"Evidence copy differs: {source}")


def copy_tree(source, target, excluded):
    resources, caches = artifact_inventory(source)
    modes = file_modes(source)
    checked_path(target)
    shutil.copytree(source, target, ignore=ignore_runtime_caches)
    if inventory(target) != resources or file_modes(target) != modes:
        raise ValueError(f"Evidence tree copy differs: {source}")
    if caches:
        excluded[source.relative_to(ROOT).as_posix()] = caches


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", help="Explicit preallocated Sxx-Pxx packet")
    args = parser.parse_args()
    if not re.fullmatch(r"S\d{2}-P\d{2}", args.packet):
        raise ValueError("Use the exact preallocated packet identity")
    allocation_path = ROOT / "control-grading-allocation.json"
    if sha(allocation_path) != ALLOCATION_SHA256:
        raise ValueError("Fixed grading allocation changed")
    allocation = read_json(allocation_path)
    matches = [(family, row) for family, packets in allocation["families"].items()
               for row in packets if row["packet"] == args.packet]
    if len(matches) != 1:
        raise ValueError("Exactly one fixed packet must match")
    family, packet = matches[0]
    target = ROOT / "blind-business" / args.packet
    mapping_path = ROOT / "blind-mappings" / f"control-{args.packet}.json"
    provenance_path = ROOT / "blind-mappings" / f"control-{args.packet}-provenance.json"
    for path in (target, mapping_path, provenance_path):
        checked_path(path)
        if path.exists() or path.is_symlink() or path.parent.is_symlink():
            raise ValueError(f"Preserve existing or partial packet: {path}")
    creators = read_ledger("control-list.tsv", "trial_id")
    consumers = read_ledger("control-consumer-list.tsv", "consumer_id")
    fixed_schedule("control", "trial_id", CREATOR_SCHEDULE_SHA256, creators)
    fixed_schedule("control-consumer", "consumer_id", CONSUMER_SCHEDULE_SHA256, consumers)
    case_manifest = ROOT / "control-consumer-case-hashes.json"
    if sha(case_manifest) != CASE_MANIFEST_SHA256:
        raise ValueError("Frozen consumer bank identity changed")
    expected_cases = read_json(case_manifest)
    if inventory(ROOT / "control-consumer-cases") != expected_cases:
        raise ValueError("Original consumer bank changed")
    oracle_hashes = read_json(ROOT / "control-oracle-hashes.json")
    oracle = ROOT / "control-oracles" / f"{family}.md"
    if sha(oracle) != oracle_hashes[f"{family}.md"]:
        raise ValueError("Frozen business oracle changed")
    public_hashes = read_json(ROOT / "main-case-hashes.json")
    original_files = {key.removeprefix(family + "/"): value
                      for key, value in public_hashes.items() if key.startswith(family + "/")}
    for relative, digest in original_files.items():
        if sha(ROOT / "frozen/main-cases" / family / relative) != digest:
            raise ValueError("Original creator business input changed")
    plans = []
    for code, creator_id in zip(("R17", "R63", "R28", "R44"), packet["creators"]):
        if creators[creator_id]["execution"] != "completed":
            raise ValueError(f"Creator is not explicitly complete: {creator_id}")
        if not (ROOT / "trials" / creator_id / "execution-note.md").is_file():
            raise ValueError(f"Creator public note is absent: {creator_id}")
        checked_path(ROOT / "trials" / creator_id / "execution-note.md")
        inventory(ROOT / "trials" / creator_id / "deliverables")
        freeze_path = ROOT / "control-artifact-freezes" / f"{creator_id}.json"
        freeze = read_json(freeze_path)
        package = Path(freeze["frozen_path"])
        if (package.parent != ROOT / "frozen/control-artifacts" / creator_id or
                inventory(package) != freeze["file_sha256"] or
                file_modes(package) != freeze["source_file_modes"]):
            raise ValueError(f"Frozen package changed: {creator_id}")
        applications = []
        number = int(creator_id.rsplit("-", 1)[1])
        for index, variant in enumerate(("ordinary", "challenging")):
            use_id = f"C-U{2 * (number - 1) + index + 1:03}"
            if consumers[use_id]["execution"] != "completed":
                raise ValueError(f"Consumer is not explicitly complete: {use_id}")
            folder = ROOT / "consumers" / use_id
            assignment = read_json(ROOT / "consumer-assignments" / f"{use_id}.json")
            if (assignment["creator_id"] != creator_id or assignment["variant"] != variant
                    or assignment["consumer_id"] != use_id or assignment["case"] != family
                    or assignment["requested_model"] != consumers[use_id]["model"]
                    or assignment["requested_effort"] != consumers[use_id]["effort"]
                    or assignment["context"] != "fresh"
                    or assignment["artifact_freeze_sha256"] != sha(freeze_path)):
                raise ValueError(f"Application identity differs: {use_id}")
            for name in ("answer.md", "execution-note.md", "prompt.md"):
                if not (folder / name).is_file():
                    raise ValueError(f"Completed observation is absent: {use_id}/{name}")
            if sha(folder / "prompt.md") != assignment["prompt_sha256"]:
                raise ValueError(f"Original consumer prompt changed: {use_id}")
            if set(assignment["copied_file_modes"]) != set(assignment["copied_sha256"]):
                raise ValueError(f"Original copied mode identities incomplete: {use_id}")
            inventory(folder)
            if family == "S06":
                expected_initial_paths = {f"consumer-setup/{use_id}.json",
                                          f"state-snapshots/{use_id}/initial.sql",
                                          f"state-snapshots/{use_id}/initial.json"}
                initial_identity = assignment["initial_state_evidence_sha256"]
                if set(initial_identity) != expected_initial_paths or any(
                    sha(ROOT / relative) != digest for relative, digest in initial_identity.items()
                ):
                    raise ValueError(f"Original native setup/snapshot evidence changed: {use_id}")
                setup = read_json(ROOT / "consumer-setup" / f"{use_id}.json")
                if (setup.get("consumer_id") != use_id or setup.get("setup_verified") is not True
                        or setup.get("fixture_sha256") != expected_cases[f"S06/{variant}/fixture.json"]
                        or setup.get("interface_sha256") != public_hashes["S06/ledger_api.py"]):
                    raise ValueError(f"Native setup identity differs: {use_id}")
                state = Path(setup["state_path"])
                if (state.parent.parent != ROOT.parent or state.name != "ledger.sqlite" or
                        not state.parent.name.startswith(use_id + "-ledger-state-")):
                    raise ValueError(f"Native allocated state identity differs: {use_id}")
                for label in ("initial", "final"):
                    snapshot = ROOT / "state-snapshots" / use_id
                    metadata = read_json(snapshot / f"{label}.json")
                    if (metadata.get("consumer_id") != use_id or metadata.get("snapshot") != label
                            or metadata.get("state_path") != setup["state_path"]
                            or sha(snapshot / f"{label}.sql") != metadata["sql_sha256"]):
                        raise ValueError(f"Native state evidence differs: {use_id}/{label}")
            applications.append((variant, use_id, folder, assignment))
        plans.append((code, creator_id, package, applications))
    target.mkdir(parents=True, exist_ok=False)
    excluded_caches = {}
    copy_file(oracle, target / "business-oracle.md")
    copy_file(ROOT / "grading-guidance.md", target / "grading-guidance.md")
    with (target / "judgment-boundaries.md").open("x", encoding="utf-8") as stream:
        stream.write(BOUNDARIES)
    for relative in original_files:
        copy_file(ROOT / "frozen/main-cases" / family / relative,
                  target / "original-creator-input" / relative)
    copy_tree(ROOT / "control-consumer-cases" / family, target / "original-consumer-inputs", excluded_caches)
    mapping = {}
    for code, creator_id, package, applications in plans:
        candidate = target / code
        copy_tree(package, candidate / "package" / package.name, excluded_caches)
        creator = ROOT / "trials" / creator_id
        copy_file(creator / "execution-note.md", candidate / "creator-reported-checks.md")
        creator_caches = artifact_inventory(creator / "deliverables")[1]
        if creator_caches:
            excluded_caches[(creator / "deliverables").relative_to(ROOT).as_posix()] = creator_caches
        for path in (creator / "deliverables").iterdir():
            if path.name in {"skills", "__pycache__"}:
                continue
            destination = candidate / "other-creator-deliverables" / path.name
            if path.is_dir():
                copy_tree(path, destination, excluded_caches)
            else:
                copy_file(path, destination)
        mapping[code] = {"creator": creator_id, "consumers": []}
        for variant, use_id, folder, assignment in applications:
            dest = candidate / variant
            application_caches = artifact_inventory(folder)[1]
            if application_caches:
                excluded_caches[folder.relative_to(ROOT).as_posix()] = application_caches
            for name in ("answer.md", "execution-note.md", "prompt.md"):
                copy_file(folder / name, dest / name)
            copy_tree(folder / "input", dest / "final-input-state", excluded_caches)
            # Preserve all final Skill resources, including additions and mode changes.
            copy_tree(folder / "skill", dest / "observed-final-skill", excluded_caches)
            changes = []
            for relative, initial in assignment["copied_sha256"].items():
                current = folder / relative
                actual = sha(current) if current.is_file() else None
                current_mode = stat.S_IMODE(current.stat().st_mode) if current.is_file() else None
                initial_mode = assignment["copied_file_modes"][relative]
                if actual != initial or current_mode != initial_mode:
                    changes.append({"path": relative, "initial_sha256": initial, "final_sha256": actual,
                                    "initial_mode": initial_mode, "final_mode": current_mode})
            final_resources = {part + "/" + key: value for part in ("skill", "input")
                               for key, value in inventory(folder / part).items()}
            additions = {key: value for key, value in final_resources.items()
                         if key not in assignment["copied_sha256"]}
            with (dest / "resource-observations.json").open("x") as stream:
                json.dump({"scope": "Initial and final file bytes/modes; not a complete operation/access trace",
                           "changed_originals": changes, "added_resources_sha256": additions}, stream, indent=2)
                stream.write("\n")
            if (folder / "work").exists():
                copy_tree(folder / "work", dest / "work-evidence", excluded_caches)
            if (folder / "deliverables").exists():
                copy_tree(folder / "deliverables", dest / "deliverables-evidence", excluded_caches)
            for path in folder.iterdir():
                if path.name in {"skill", "input", "work", "deliverables", "answer.md", "execution-note.md", "prompt.md", "__pycache__"}:
                    continue
                destination = dest / "other-application-files" / path.name
                if path.is_dir():
                    copy_tree(path, destination, excluded_caches)
                else:
                    copy_file(path, destination)
            if family == "S06":
                copy_tree(ROOT / "state-snapshots" / use_id, dest / "committed-state", excluded_caches)
                copy_file(ROOT / "consumer-setup" / f"{use_id}.json", dest / "setup-observations.json")
            mapping[code]["consumers"].append(use_id)
    mapping_path.parent.mkdir(exist_ok=True)
    with mapping_path.open("x") as stream:
        json.dump(mapping, stream, indent=2)
        stream.write("\n")
    with provenance_path.open("x") as stream:
        json.dump({"packet": args.packet, "file_sha256": inventory(target),
                   "file_modes": file_modes(target), "excluded_source_runtime_cache_sha256": excluded_caches,
                   "scope": "Copied resource identities; excluded cache originals retained, cache bytes not claimed saved"}, stream, indent=2)
        stream.write("\n")
    print(f"Prepared {args.packet}: four frozen packages and eight completed observations; no quality judgment")


if __name__ == "__main__":
    main()
