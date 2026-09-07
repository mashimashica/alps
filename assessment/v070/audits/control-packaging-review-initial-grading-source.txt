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

ROOT = Path(__file__).resolve().parent
ALLOCATION_SHA256 = "bb463eceeccea6502418daf3263558d386c8fd31f4b1dcfe4f5fba411c577a0f"
CASE_MANIFEST_SHA256 = "f26be07f6cfba54aedc3068a67ae32292877f6ee005f0c190156f5786d1cbdc2"
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
Resource-observations checks recorded original bytes only. Authorized S10 state
changes need behavioral review; additions, removed temporary files, and unrecorded
access are not certified by that check. Do not repair the evaluated Skill.

Judge requested-task adequacy, intended business results, applicable conditions,
and package defects separately. Good handling of initially missing evidence can
be adequate without achieving the business result. An avoidable self-created
block is not automatically appropriate handling. Count only distinct evidenced
corrections to erroneous or unusable instructions; ordinary business choices
and necessary interpretation are not corrections. Do not require ALPS headings,
jargon, a preferred report, or a particular valid implementation.
"""


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_ledger(name, key):
    with (ROOT / name).open(newline="", encoding="utf-8") as stream:
        data = list(csv.DictReader(stream, delimiter="\t"))
    result = {row[key]: row for row in data}
    if len(result) != len(data):
        raise ValueError(f"Duplicate ledger identity: {name}")
    return result


def inventory(folder):
    result = {}
    for path in sorted(folder.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"Review the original symlink before evidence packaging: {path}")
        if path.is_file():
            result[path.relative_to(folder).as_posix()] = sha(path)
    return result


def copy_file(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    if sha(source) != sha(target):
        raise ValueError(f"Evidence copy differs: {source}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", help="Explicit preallocated Sxx-Pxx packet")
    args = parser.parse_args()
    if not re.fullmatch(r"S\d{2}-P\d{2}", args.packet):
        raise ValueError("Use the exact preallocated packet identity")
    allocation_path = ROOT / "control-grading-allocation.json"
    if sha(allocation_path) != ALLOCATION_SHA256:
        raise ValueError("Fixed grading allocation changed")
    allocation = json.loads(allocation_path.read_text())
    matches = [(family, row) for family, packets in allocation["families"].items()
               for row in packets if row["packet"] == args.packet]
    if len(matches) != 1:
        raise ValueError("Exactly one fixed packet must match")
    family, packet = matches[0]
    target = ROOT / "blind-business" / args.packet
    mapping_path = ROOT / "blind-mappings" / f"control-{args.packet}.json"
    for path in (target, mapping_path):
        if path.exists() or path.is_symlink() or path.parent.is_symlink():
            raise ValueError(f"Preserve existing or partial packet: {path}")
    creators = read_ledger("control-list.tsv", "trial_id")
    consumers = read_ledger("control-consumer-list.tsv", "consumer_id")
    case_manifest = ROOT / "control-consumer-case-hashes.json"
    if sha(case_manifest) != CASE_MANIFEST_SHA256:
        raise ValueError("Frozen consumer bank identity changed")
    expected_cases = json.loads(case_manifest.read_text())
    if inventory(ROOT / "control-consumer-cases") != expected_cases:
        raise ValueError("Original consumer bank changed")
    oracle_hashes = json.loads((ROOT / "control-oracle-hashes.json").read_text())
    oracle = ROOT / "control-oracles" / f"{family}.md"
    if sha(oracle) != oracle_hashes[f"{family}.md"]:
        raise ValueError("Frozen business oracle changed")
    public_hashes = json.loads((ROOT / "main-case-hashes.json").read_text())
    original_files = {key.removeprefix(family + "/"): value
                      for key, value in public_hashes.items() if key.startswith(family + "/")}
    for relative, digest in original_files.items():
        if sha(ROOT / "frozen/main-cases" / family / relative) != digest:
            raise ValueError("Original creator business input changed")
    plans = []
    for code, creator_id in zip(("R17", "R63", "R28", "R44"), packet["creators"]):
        if creators[creator_id]["execution"] != "completed":
            raise ValueError(f"Creator is not explicitly complete: {creator_id}")
        freeze_path = ROOT / "control-artifact-freezes" / f"{creator_id}.json"
        freeze = json.loads(freeze_path.read_text())
        package = Path(freeze["frozen_path"])
        if inventory(package) != freeze["file_sha256"]:
            raise ValueError(f"Frozen package changed: {creator_id}")
        applications = []
        number = int(creator_id.rsplit("-", 1)[1])
        for index, variant in enumerate(("ordinary", "challenging")):
            use_id = f"C-U{2 * (number - 1) + index + 1:03}"
            if consumers[use_id]["execution"] != "completed":
                raise ValueError(f"Consumer is not explicitly complete: {use_id}")
            folder = ROOT / "consumers" / use_id
            assignment = json.loads((ROOT / "consumer-assignments" / f"{use_id}.json").read_text())
            if (assignment["creator_id"] != creator_id or assignment["variant"] != variant
                    or assignment["case"] != family or assignment["artifact_freeze_sha256"] != sha(freeze_path)):
                raise ValueError(f"Application identity differs: {use_id}")
            for name in ("answer.md", "execution-note.md", "prompt.md"):
                if not (folder / name).is_file():
                    raise ValueError(f"Completed observation is absent: {use_id}/{name}")
            inventory(folder)
            if family == "S06":
                for label in ("initial", "final"):
                    snapshot = ROOT / "state-snapshots" / use_id
                    metadata = json.loads((snapshot / f"{label}.json").read_text())
                    if sha(snapshot / f"{label}.sql") != metadata["sql_sha256"]:
                        raise ValueError(f"Native state evidence differs: {use_id}/{label}")
            applications.append((variant, use_id, folder, assignment))
        plans.append((code, creator_id, package, applications))
    target.mkdir(parents=True, exist_ok=False)
    copy_file(oracle, target / "business-oracle.md")
    copy_file(ROOT / "grading-guidance.md", target / "grading-guidance.md")
    with (target / "judgment-boundaries.md").open("x", encoding="utf-8") as stream:
        stream.write(BOUNDARIES)
    for relative in original_files:
        copy_file(ROOT / "frozen/main-cases" / family / relative,
                  target / "original-creator-input" / relative)
    shutil.copytree(ROOT / "control-consumer-cases" / family, target / "original-consumer-inputs")
    mapping = {}
    for code, creator_id, package, applications in plans:
        candidate = target / code
        shutil.copytree(package, candidate / "package" / package.name)
        mapping[code] = {"creator": creator_id, "consumers": []}
        for variant, use_id, folder, assignment in applications:
            dest = candidate / variant
            for name in ("answer.md", "execution-note.md", "prompt.md"):
                copy_file(folder / name, dest / name)
            shutil.copytree(folder / "input", dest / "final-input-state")
            # Preserve any observed edits to the supplied Skill for grading.
            changes = []
            for relative, initial in assignment["copied_sha256"].items():
                current = folder / relative
                actual = sha(current) if current.is_file() else None
                if actual != initial:
                    changes.append({"path": relative, "initial_sha256": initial, "final_sha256": actual})
            with (dest / "resource-observations.json").open("x") as stream:
                json.dump({"scope": "Recorded original bytes only; additions and behavior need separate review",
                           "changed_originals": changes}, stream, indent=2)
                stream.write("\n")
            if any(item["path"].startswith("skill/") for item in changes):
                shutil.copytree(folder / "skill", dest / "observed-final-skill")
            if (folder / "work").exists():
                shutil.copytree(folder / "work", dest / "work-evidence")
            if (folder / "deliverables").exists():
                shutil.copytree(folder / "deliverables", dest / "deliverables-evidence")
            if family == "S06":
                shutil.copytree(ROOT / "state-snapshots" / use_id, dest / "committed-state")
            mapping[code]["consumers"].append(use_id)
    mapping_path.parent.mkdir(exist_ok=True)
    with mapping_path.open("x") as stream:
        json.dump(mapping, stream, indent=2)
        stream.write("\n")
    print(f"Prepared {args.packet}: four frozen packages and eight completed observations; no quality judgment")


if __name__ == "__main__":
    main()
