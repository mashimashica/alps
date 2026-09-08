"""Prepare one of the six fixed focused assessment packets, without grading.

This only copies completed evidence. It does not launch trials, repair sources,
capture live state, or write remotely. Existing/partial outputs are preserved.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat

from prepare_control_consumers import artifact_inventory, checked_path
import prepare_control_grading as control
import prepare_focused as focused
import recovered_control_grading as recovered
from recovery_ledger_binding import record_path, validate_snapshot_identity

ROOT = Path(__file__).resolve().parent
LABELS = ("R17", "R63", "R28", "R44")
VARIANTS = ("ordinary", "challenging")
FIXED_FILES = {
    "focused-grading-allocation.json": "5e0e5ef690576cad8afaa4d35d631a51761734f8d6778730f0ddda3aafc1601b",
    "focused-comparison-plan.md": "848cf7553e643cb549f44fb3070873cb5ade4822eaabfb29c1a9a9514003958e",
    "grading-guidance.md": "35e3fcadda5f885a6ad346961c56e3d15127a6379155ab0de8f4e397958e9afe",
    "control-oracle-hashes.json": "e989aca00c688f58d997377dbf97c7d030aad6ca629cd94bb5835339297456b4",
    "main-case-hashes.json": "142cc29cef88dd33d93b682ff596b68968cf3033d6887eadad509aa8e2cb9fd4",
    "control-consumer-case-hashes.json": control.CASE_MANIFEST_SHA256,
}
# This redundant, closed identity table prevents an allocation/schema change
# from silently introducing another trial or a different blind-label ordering.
FIXED_PACKETS = {
    "FP01": ("S03", ("focus-002", "focus-001", "control-020", "control-019")),
    "FP02": ("S03", ("control-023", "control-024", "focus-003", "focus-004")),
    "FP03": ("S06", ("control-043", "focus-005", "control-044", "focus-006")),
    "FP04": ("S06", ("focus-007", "control-047", "focus-008", "control-048")),
    "FP05": ("S10", ("focus-010", "control-068", "control-067", "focus-009")),
    "FP06": ("S10", ("focus-011", "control-071", "control-072", "focus-012")),
}
REUSED = {
    "control-019": ("S03-P02", "R17"), "control-020": ("S03-P01", "R63"),
    "control-023": ("S03-P02", "R63"), "control-024": ("S03-P01", "R44"),
    "control-043": ("S06-P01", "R28"), "control-044": ("S06-P03", "R44"),
    "control-047": ("S06-P03", "R28"), "control-048": ("S06-P01", "R17"),
}
REUSED_IDENTITIES = {
    "S03-P01": ("45352f2082f52ab635959f40563e13ef06c29cedd11a8eee86718680f56a3e7d",
                 "e441787949a9ecfb3417d8ffc37eb4094aeac126c83379565648cd2b2e8bb39b"),
    "S03-P02": ("05460fb943c7ed9d8102114e2018c0f09155eb4caa957e5ae1174d8dc889a131",
                 "e4e51dbf27ce004e5e028de4f934d83e30025e2643adf329b714708b2be6c24f"),
    "S06-P01": ("4cff1db8f4ad1065f4436eba17b1e7efc55bef2680548ee002485048894bd006",
                 "26d0dc75eed102d42e6625efa4638a20a2bdc108515a348aaff9c58bf52ac6fd"),
    "S06-P03": ("feec9ae1629cf3688bc4206c07ec20b7f158e7496a77c9d56339def33f5e0d32",
                 "c60fe2ac65e96c76432bd803aec8027a337d9b17a5140f86a9c17f788d65b308"),
}
FOCUSED_BOUNDARIES = f"""
## This assessment

Assess all four candidate labels and both applications per candidate. For each
application report requested-task adequacy as adequate / bounded deficiency /
material failure / unconfirmed, with raw evidence. Adequacy requires completing
achievable requested work and reporting faithfully. Report business Outcome and
component correctness separately. Inspect the supplied frozen package even when
the consumer compensated successfully for an instruction defect.

Count each distinct independently evidenced correction to an erroneous or
unusable instruction once per application. Give its instruction, correction,
and evidence. Ordinary interpretation, checks and requested choices do not
count. An unavailable or ungradable public record leaves the count unconfirmed;
absence of observed correction does not establish zero hidden effort.

The two applications share one generated Skill. They are not independent
generators. Keep every assigned slot and all observation limits. Do not infer
experimental identity or consult other packets, reports or grading workspaces.
No release decision or broad acceptance threshold is part of this review.

The optional common authoring aid is available at
{ROOT}/frozen/skill-creator/SKILL.md and its needed resources. This is the only
shared resource outside the assigned packet permitted for this review; do not
enumerate adjacent folders. Public handoffs, where preserved, remain separate
from answer.md and execution-note.md. Runtime
caches are omitted with external bookkeeping; original cache bytes are not
claimed preserved. Raw source paths/style may give identity hints; they have
not been redacted or rewritten. Path restrictions are procedural, not a sandbox.
"""


def identity(path):
    checked_path(path)
    if (not path.is_absolute() or path.resolve() != path or
            not path.is_relative_to(ROOT) or not path.is_file()):
        raise ValueError(f"Expected a regular assessment-owned file: {path}")
    return {"sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "mode": stat.S_IMODE(path.stat().st_mode)}


def observe(path, observations, expected=None):
    value = identity(path)
    if expected is not None and value["sha256"] != expected:
        raise ValueError(f"Fixed source bytes changed: {path}")
    relative = path.relative_to(ROOT).as_posix()
    if relative in observations and observations[relative] != value:
        raise ValueError(f"Source changed during planning: {path}")
    observations[relative] = value
    return value


def read_json(path, observations, expected=None):
    observe(path, observations, expected)
    return json.loads(path.read_text(encoding="utf-8"))


def inventory(folder):
    resources, caches = artifact_inventory(checked_path(folder))
    return {key: identity(folder / key) for key in resources}, {
        key: identity(folder / key) for key in caches}


def observe_tree(folder, trees):
    value = inventory(folder)
    relative = folder.relative_to(ROOT).as_posix()
    if relative in trees and trees[relative] != value:
        raise ValueError(f"Source tree changed during planning: {folder}")
    trees[relative] = value
    return value


def safe_relative(relative):
    path = Path(relative)
    if not relative or path.is_absolute() or ".." in path.parts or path.as_posix() != relative:
        raise ValueError(f"Expected a canonical relative evidence path: {relative}")
    return relative


def add_file(files, source, destination, observations, expected=None):
    safe_relative(destination)
    if destination in files:
        raise ValueError(f"Duplicate packet destination: {destination}")
    files[destination] = {"source": source.relative_to(ROOT).as_posix(),
                          **observe(source, observations, expected)}


def add_tree(files, source, destination, observations, trees):
    resources, _ = observe_tree(source, trees)
    for relative, item in resources.items():
        add_file(files, source / relative, f"{destination}/{relative}", observations, item["sha256"])


def generated_text(generated, destination, text):
    safe_relative(destination)
    if destination in generated:
        raise ValueError(f"Duplicate generated evidence path: {destination}")
    generated[destination] = text


def generated_json(generated, destination, value):
    generated_text(generated, destination, json.dumps(value, indent=2) + "\n")


def refuse_outputs(packet):
    paths = (ROOT / "blind-focused" / packet,
             ROOT / "blind-mappings" / f"focused-{packet}.json",
             ROOT / "blind-mappings" / f"focused-{packet}-provenance.json")
    for path in paths:
        focused.refuse_existing(path)
        if path.resolve() != path or not path.is_relative_to(ROOT):
            raise ValueError(f"Unexpected packet destination: {path}")
    return paths


def fixed_allocation(observations):
    for relative, digest in FIXED_FILES.items():
        observe(ROOT / relative, observations, digest)
    data = read_json(ROOT / "focused-grading-allocation.json", observations)
    if data.get("seed") != 7070 or len(data["packets"]) != 6:
        raise ValueError("Exactly six preallocated packets are required")
    result = {}
    for row in data["packets"]:
        packet = row["packet"]
        if packet not in FIXED_PACKETS or packet in result:
            raise ValueError("Unknown or duplicate focused packet")
        family, creators = FIXED_PACKETS[packet]
        expected = {label: {"creator_id": creator, "arm": "A" if creator.startswith("focus-") else "C"}
                    for label, creator in zip(LABELS, creators)}
        if (row["case"] != family or row["labels"] != expected or
                row["primary"] != f"focused-{packet}-primary.md" or
                row["second"] != f"focused-{packet}-second.md"):
            raise ValueError("Focused label permutation or reviewer slot changed")
        result[packet] = row
    return result


def check_freeze(creator_id, focused_plan, observations, trees):
    is_focused = creator_id.startswith("focus-")
    prefix = "focused" if is_focused else "control"
    manifest = ROOT / f"{prefix}-artifact-freezes" / f"{creator_id}.json"
    freeze = read_json(manifest, observations)
    package = Path(freeze["frozen_path"])
    source = Path(freeze["source_path"])
    if (freeze.get("creator_id") != creator_id or
            package.parent != ROOT / f"frozen/{prefix}-artifacts" / creator_id or
            source != ROOT / "trials" / creator_id / "deliverables/skills" / package.name):
        raise ValueError(f"Frozen package ownership differs: {creator_id}")
    expected = {name: {"sha256": value, "mode": freeze["source_file_modes"][name]}
                for name, value in freeze["file_sha256"].items()}
    if (set(freeze["source_file_modes"]) != set(expected) or "SKILL.md" not in expected or
            observe_tree(package, trees) != (expected, {}) or
            observe_tree(source, trees)[0] != expected):
        raise ValueError(f"Original/frozen package bytes or modes differ: {creator_id}")
    resources, _ = observe_tree(source.parent, trees)
    if resources != {f"{package.name}/{name}": value for name, value in expected.items()}:
        raise ValueError(f"Unknown original Skill-container resources: {creator_id}")
    if freeze.get("case_bank_manifest_sha256") != control.CASE_MANIFEST_SHA256:
        raise ValueError("Frozen Skill does not bind the fixed consumer bank")
    if is_focused:
        row = focused_plan["row"]
        for key in ("file_sha256", "source_file_modes", "public_completion_evidence_sha256"):
            if freeze[key] != focused_plan[key]:
                raise ValueError(f"Focused original evidence differs from its freeze: {creator_id}/{key}")
        if (freeze["paired_control_id"] != row["paired_control_id"] or
                freeze["source_identities_sha256"] != observe(ROOT / "focused-source-identities.json", observations)["sha256"] or
                freeze["schedule_sha256"] != observe(ROOT / "focused-schedule.tsv", observations)["sha256"]):
            raise ValueError("Focused freeze source/assignment identity differs")
        observe(ROOT / "validation/focused-format" / f"{creator_id}.json", observations,
                freeze["physical_validation_sha256"])
        for relative, digest in freeze["public_completion_evidence_sha256"].items():
            safe_relative(relative)
            observe(ROOT / relative, observations, digest)
    elif freeze.get("schedule_sha256") != control.CREATOR_SCHEDULE_SHA256:
        raise ValueError("Control freeze does not bind the fixed creator schedule")
    return manifest, freeze, package


def check_creator(creator_id, row, family, public, observations, trees):
    if row.get("execution") != "completed" or row["case"] != family:
        raise ValueError(f"Explicit creator completion is required: {creator_id}")
    prefix = "focused" if creator_id.startswith("focus-") else "control"
    assignment = read_json(ROOT / f"{prefix}-assignments" / f"{creator_id}.json", observations)
    expected = {"trial_id": creator_id, "stage": row["stage"], "case": family, "arm": row["arm"],
                "repetition": int(row["repetition"]), "requested_model": row["model"],
                "requested_effort": row["effort"], "context": "fresh"}
    original = {name.removeprefix(family + "/"): value for name, value in public.items()
                if name.startswith(family + "/")}
    if (any(assignment.get(key) != value for key, value in expected.items()) or
            assignment["input_sha256"] != {"input/" + name: value for name, value in original.items()}):
        raise ValueError(f"Creator's original assignment differs: {creator_id}")
    trial = ROOT / "trials" / creator_id
    resources, _ = observe_tree(trial / "input", trees)
    if {name: item["sha256"] for name, item in resources.items()} != original:
        raise ValueError(f"Original creator input changed: {creator_id}")
    observe(trial / "prompt.md", observations, assignment["prompt_sha256"])
    observe(trial / "execution-note.md", observations)
    observe_tree(trial / "deliverables", trees)


def check_application(use_id, creator_id, variant, family, row, freeze_path, freeze, package,
                      public, common, observations, trees):
    folder = ROOT / "consumers" / use_id
    assignment = read_json(ROOT / "consumer-assignments" / f"{use_id}.json", observations)
    expected = {"consumer_id": use_id, "creator_id": creator_id, "case": family, "variant": variant,
                "requested_model": "gpt-5.6-sol", "requested_effort": "high", "context": "fresh"}
    if (row.get("execution") != "completed" or any(row.get(key) != expected[key]
            for key in ("consumer_id", "creator_id", "case", "variant")) or
            row.get("model") != expected["requested_model"] or row.get("effort") != "high" or
            any(assignment.get(key) != value for key, value in expected.items()) or
            assignment["artifact_freeze_manifest"] != str(freeze_path) or
            assignment["artifact_freeze_sha256"] != observe(freeze_path, observations)["sha256"] or
            assignment["case_bank_manifest_sha256"] != control.CASE_MANIFEST_SHA256 or
            assignment["common_authoring_aid_sha256"] != common):
        raise ValueError(f"Completed application assignment differs: {use_id}")
    if use_id.startswith("F-"):
        if (assignment.get("stage") != "focused" or assignment.get("paired_consumer_id") != row["paired_consumer_id"] or
                assignment["schedule_sha256"] != observe(ROOT / "focused-consumer-schedule.tsv", observations)["sha256"] or
                assignment["source_identities_sha256"] != observe(ROOT / "focused-source-identities.json", observations)["sha256"]):
            raise ValueError(f"Focused application pairing/source identity differs: {use_id}")
    elif assignment["schedule_sha256"] != control.CREATOR_SCHEDULE_SHA256:
        raise ValueError("Control application does not bind the original schedule")
    request_source = ROOT / "control-consumer-cases" / family / variant / "input/request.md"
    if assignment["request_source"] != str(request_source):
        raise ValueError("Original request source is outside the fixed variant")
    observe(request_source, observations, assignment["request_source_sha256"])
    request = request_source.read_text(encoding="utf-8")
    state = str(folder / "input/state.json")
    if family == "S06":
        state = read_json(ROOT / "consumer-setup" / f"{use_id}.json", observations)["state_path"]
    substitutions = []
    for token, value in (("{{INPUT_DIR}}", str(folder / "input")), ("{{STATE_PATH}}", state),
                         ("{{ENVIRONMENT_PATH}}", str(folder / "input"))):
        count = request.count(token)
        if count:
            substitutions.append({"token": token, "value": value, "occurrences": count})
            request = request.replace(token, value)
    if assignment["request_substitutions"] != substitutions or "{{" in request or "}}" in request:
        raise ValueError(f"Original request substitution differs: {use_id}")
    raw = ROOT / "control-consumer-cases" / family / variant / "input"
    raw_resources, _ = observe_tree(raw, trees)
    initial = {f"input/{key}": item["sha256"] for key, item in raw_resources.items()}
    initial_modes = {f"input/{key}": item["mode"] for key, item in raw_resources.items()}
    initial["input/request.md"] = hashlib.sha256(request.encode()).hexdigest()
    interface = {"S06": "ledger_api.py", "S10": "release_tool.py"}.get(family)
    if interface:
        item = observe(ROOT / "frozen/main-cases" / family / interface, observations, public[f"{family}/{interface}"])
        initial[f"input/{interface}"], initial_modes[f"input/{interface}"] = item["sha256"], item["mode"]
    initial.update({f"skill/{package.name}/{key}": value for key, value in freeze["file_sha256"].items()})
    initial_modes.update({f"skill/{package.name}/{key}": value for key, value in freeze["source_file_modes"].items()})
    if assignment["copied_sha256"] != initial or assignment["copied_file_modes"] != initial_modes:
        raise ValueError(f"Original prepared inputs/Skill bytes or modes differ: {use_id}")
    observe(folder / "prompt.md", observations, assignment["prompt_sha256"])
    if (folder / "prompt.md").read_text(encoding="utf-8") != focused.consumer_prompt(folder, folder / "skill" / package.name):
        raise ValueError(f"Original consumer prompt conditions differ: {use_id}")
    observe_tree(folder, trees)
    return assignment


def state_sources(use_id, variant, assignment, observations, trees):
    initial = assignment["initial_state_evidence_sha256"]
    expected_paths = {f"consumer-setup/{use_id}.json", f"state-snapshots/{use_id}/initial.sql",
                      f"state-snapshots/{use_id}/initial.json"}
    if set(initial) != expected_paths:
        raise ValueError(f"Incomplete native initial evidence identity: {use_id}")
    for relative, digest in initial.items():
        observe(ROOT / relative, observations, digest)
    setup = read_json(ROOT / "consumer-setup" / f"{use_id}.json", observations)
    state = Path(setup["state_path"])
    fixture = ROOT / "control-consumer-cases/S06" / variant / "fixture.json"
    if (setup.get("consumer_id") != use_id or setup.get("setup_verified") is not True or
            setup.get("source_packet") != str(fixture.parent) or
            setup.get("fixture_sha256") != observe(fixture, observations)["sha256"] or
            setup.get("interface_sha256") != assignment["copied_sha256"]["input/ledger_api.py"] or
            not state.is_absolute() or state.parent.parent != ROOT.parent or state.name != "ledger.sqlite" or
            not state.parent.name.startswith(use_id + "-ledger-state-")):
        raise ValueError(f"Native state allocation/setup differs: {use_id}")
    records = json.loads(fixture.read_text(encoding="utf-8"))["records"]
    canonical = json.dumps(records, sort_keys=True, separators=(",", ":"))
    snapshot_id = "snap_" + hashlib.sha256(canonical.encode()).hexdigest()[:24]
    initial_calls = [
        {"state": "ready", "snapshot_id": snapshot_id, "total_records": len(records)},
        {"snapshot_id": snapshot_id, "total_records": len(records), "page_size": 3,
         "calls_per_tranche": 2, "tranche": 1, "remaining_calls": 2},
    ]
    if len(setup["calls"]) != 2 or any(
            call["exit_code"] != 0 or call["stderr"] or json.loads(call["stdout"]) != expected
            for call, expected in zip(setup["calls"], initial_calls)):
        raise ValueError(f"Original native setup observations differ: {use_id}")
    # The historical/native database is deliberately never opened or required.
    snapshot = ROOT / "state-snapshots" / use_id
    resources, _ = observe_tree(snapshot, trees)
    supplemented = use_id in recovered.ASSIGNMENT_SHA256
    labels = ("initial",) if supplemented else ("initial", "final")
    if use_id.startswith("F-") and set(resources) != {f"{label}.{suffix}" for label in labels for suffix in ("json", "sql")}:
        raise ValueError(f"Unknown or missing focused native snapshot: {use_id}")
    for label in labels:
        metadata = read_json(snapshot / f"{label}.json", observations)
        if (metadata.get("consumer_id") != use_id or metadata.get("snapshot") != label or
                metadata["sql_sha256"] != observe(snapshot / f"{label}.sql", observations)["sha256"]):
            raise ValueError(f"Native SQL/metadata identity differs: {use_id}/{label}")
        if use_id.startswith("F-"):
            if metadata.get("state_path") != setup["state_path"] or any(
                    key in metadata for key in ("original_state_path", "recovery_binding_path", "recovery_binding_sha256")):
                raise ValueError(f"Focused native state binding differs: {use_id}")
            if (ROOT / "recovery-bindings" / f"{use_id}.json").exists():
                raise ValueError("Focused native evidence must not borrow a control recovery binding")
        else:
            validate_snapshot_identity(ROOT, use_id, setup, label, metadata)
    return snapshot


def standard_application(files, generated, destination, use_id, family, assignment, observations, trees):
    folder = ROOT / "consumers" / use_id
    for name in ("answer.md", "execution-note.md", "prompt.md"):
        add_file(files, folder / name, f"{destination}/{name}", observations)
    for part, name in (("input", "final-input-state"), ("skill", "observed-final-skill"),
                       ("work", "work-evidence"), ("deliverables", "deliverables-evidence")):
        if (folder / part).exists():
            add_tree(files, folder / part, f"{destination}/{name}", observations, trees)
    final_resources = {f"{part}/{key}": item for part in ("skill", "input") if (folder / part).exists()
                       for key, item in inventory(folder / part)[0].items()}
    changes = []
    for relative, initial in assignment["copied_sha256"].items():
        current = final_resources.get(relative, {})
        mode = assignment["copied_file_modes"][relative]
        if current.get("sha256") != initial or current.get("mode") != mode:
            changes.append({"path": relative, "initial_sha256": initial, "final_sha256": current.get("sha256"),
                            "initial_mode": mode, "final_mode": current.get("mode")})
    # Keep the established control observation schema; full final modes are
    # also retained in the external packet provenance, including added files.
    generated_json(generated, f"{destination}/resource-observations.json", {
        "scope": "Initial and final file bytes/modes; not a complete operation/access trace",
        "changed_originals": changes, "added_resources_sha256": {
            key: item["sha256"] for key, item in final_resources.items() if key not in assignment["copied_sha256"]}})
    for path in sorted(folder.iterdir()):
        if path.name in {"skill", "input", "work", "deliverables", "answer.md", "execution-note.md", "prompt.md", "__pycache__"}:
            continue
        dest = f"{destination}/other-application-files/{path.name}"
        if path.is_dir():
            add_tree(files, path, dest, observations, trees)
        else:
            add_file(files, path, dest, observations)
    if family == "S06":
        snapshot = state_sources(use_id, assignment["variant"], assignment, observations, trees)
        add_tree(files, snapshot, f"{destination}/committed-state", observations, trees)
        add_file(files, ROOT / "consumer-setup" / f"{use_id}.json", f"{destination}/setup-observations.json", observations)
        if use_id.startswith("C-") and record_path(ROOT, use_id).exists():
            add_file(files, record_path(ROOT, use_id), f"{destination}/recovery-binding.json", observations)


def creator_files(files, destination, creator_id, package, observations, trees):
    trial = ROOT / "trials" / creator_id
    add_tree(files, package, f"{destination}/package/{package.name}", observations, trees)
    add_file(files, trial / "execution-note.md", f"{destination}/creator-reported-checks.md", observations)
    for path in sorted((trial / "deliverables").iterdir()):
        if path.name in {"skills", "__pycache__"}:
            continue
        dest = f"{destination}/other-creator-deliverables/{path.name}"
        if path.is_dir():
            add_tree(files, path, dest, observations, trees)
        else:
            add_file(files, path, dest, observations)


def reuse_candidate(files, destination, creator_id, package, apps, observations, trees):
    old_packet, old_label = REUSED[creator_id]
    map_hash, provenance_hash = REUSED_IDENTITIES[old_packet]
    mapping_path = ROOT / "blind-mappings" / f"control-{old_packet}.json"
    provenance_path = ROOT / "blind-mappings" / f"control-{old_packet}-provenance.json"
    mapping = read_json(mapping_path, observations, map_hash)
    provenance = read_json(provenance_path, observations, provenance_hash)
    if mapping[old_label] != {"creator": creator_id, "consumers": [item[0] for item in apps]}:
        raise ValueError("Previously verified candidate/application mapping differs")
    candidate = ROOT / "blind-business" / old_packet / old_label
    expected = {name.removeprefix(old_label + "/"): {"sha256": digest, "mode": provenance["file_modes"][name]}
                for name, digest in provenance["file_sha256"].items() if name.startswith(old_label + "/")}
    if observe_tree(candidate, trees) != (expected, {}):
        raise ValueError("Previously verified candidate bytes/modes changed; no regeneration fallback")
    # Recheck surviving originals against their exact previously packaged role.
    original_files, original_generated = {}, {}
    creator_files(original_files, "candidate", creator_id, package, observations, trees)
    recoveries = {}
    for use_id, variant, family, assignment in apps:
        app_destination = f"candidate/{variant}"
        if use_id in recovered.ASSIGNMENT_SHA256:
            state_sources(use_id, variant, assignment, observations, trees)
            plan = recovered.plan_application(ROOT, use_id, assignment)
            recoveries[use_id] = plan["provenance"]
            for item in plan["files"]:
                add_file(original_files, ROOT / item["source"], f"{app_destination}/{item['destination']}", observations, item["sha256"])
                if original_files[f"{app_destination}/{item['destination']}"]["mode"] != item["observed_copy_source_mode"]:
                    raise ValueError("Recovered original source mode differs")
            generated_text(original_generated, f"{app_destination}/evidence-availability.md", plan["availability"])
            generated_json(original_generated, f"{app_destination}/recovery-provenance.json", plan["provenance"])
            generated_text(original_generated, f"{app_destination}/recovery-provenance/historical-state-observations.md", plan["historical_excerpt"])
        else:
            standard_application(original_files, original_generated, app_destination, use_id, family, assignment, observations, trees)
    if {name.removeprefix("candidate/") for name in (*original_files, *original_generated)} != set(expected):
        raise ValueError("Prior candidate file set differs from preserved original roles")
    for name, item in original_files.items():
        if expected[name.removeprefix("candidate/")] != {key: item[key] for key in ("sha256", "mode")}:
            raise ValueError(f"Prior candidate no longer matches the original source: {name}")
    for name, text in original_generated.items():
        if expected[name.removeprefix("candidate/")]["sha256"] != hashlib.sha256(text.encode()).hexdigest():
            raise ValueError(f"Prior observation/provenance differs from its verified derivation: {name}")
    add_tree(files, candidate, destination, observations, trees)
    return {"source_packet": old_packet, "source_label": old_label,
            "mapping_path": mapping_path.relative_to(ROOT).as_posix(), "mapping_sha256": map_hash,
            "provenance_path": provenance_path.relative_to(ROOT).as_posix(), "provenance_sha256": provenance_hash,
            "recovered_applications": recoveries, "scope": "Exact reuse of every verified candidate file and mode"}


def recovery_creator(files, generated, destination, creator_id, package, observations):
    plan = recovered.plan_creator(ROOT, creator_id, package)
    if plan is None:
        raise ValueError("This creator requires its reviewed recovery layer")
    recovered.verify_creator_plan(ROOT, plan)
    for item in (*plan["candidate_files"], *({**item, "destination": "recovery-provenance/" + item["destination"]}
                                          for item in plan["files"])):
        add_file(files, ROOT / item["source"], f"{destination}/{item['destination']}", observations, item["sha256"])
        if files[f"{destination}/{item['destination']}"]["mode"] != item["observed_copy_source_mode"]:
            raise ValueError("Reviewed creator recovery mode differs")
    # Full coordinator references/identity mappings remain external. The blind
    # candidate retains the exact substantive origin/availability statements.
    creator = plan["provenance"]["creator"]
    generated_text(generated, f"{destination}/recovery-provenance/README.md",
                   "# Recovery provenance\n\n" + creator["content_provenance"] + ".\n\n" + creator["historical_limits"] + "\n\n"
                   "This candidate's canonical freeze and consumer preparation are new recovery observations. "
                   "The format observation concerns physical format at recovery time, not semantic or business grading. "
                   "No missing original file or original-mode attestation is reconstructed.\n")
    return plan


def check_blinding(files, generated):
    # This is a fail-closed label check, not redaction or a quality judgment.
    # Ordinary domain uses of 'model' and substantive original path hints stay.
    explicit = re.compile(r"gpt-(?:6-astra|5[.]6-sol)|requested_(?:model|effort)|^\s*[\"']?(?:arm|repetition)[\"']?\s*[:=]", re.I | re.M)
    for destination, item in files.items():
        source = Path(item["source"])
        if source.parts[0] in {"grades", "grading", "grading-work", "control-assignments", "focused-assignments", "consumer-assignments"}:
            raise ValueError("Experimental metadata or another grade would enter the packet")
        try:
            body = (ROOT / source).read_bytes().decode("utf-8")
        except UnicodeDecodeError:
            continue
        if explicit.search(body):
            raise ValueError(f"Explicit experimental labels require source-preserving review: {destination}")
    for destination, body in generated.items():
        if destination in files or explicit.search(body):
            raise ValueError(f"Generated packet metadata duplicates a file or exposes labels: {destination}")


def build_plan(packet_id):
    destinations = refuse_outputs(packet_id)
    observations, trees, files, generated = {}, {}, {}, {}
    packet = fixed_allocation(observations)[packet_id]
    for name in ("prepare_focused_grading.py", "prepare_focused.py", "prepare_control_grading.py",
                 "prepare_control_consumers.py", "recovered_control_grading.py", "recovery_ledger_binding.py"):
        observe(ROOT / name, observations)
    family = packet["case"]
    creators = control.read_ledger("control-list.tsv", "trial_id")
    consumers = control.read_ledger("control-consumer-list.tsv", "consumer_id")
    control.fixed_schedule("control", "trial_id", control.CREATOR_SCHEDULE_SHA256, creators)
    control.fixed_schedule("control-consumer", "consumer_id", control.CONSUMER_SCHEDULE_SHA256, consumers)
    focused_creators = focused.fixed_ledger("focused", focused.CREATOR_FIELDS, focused.creator_rows())
    focused_consumers = focused.fixed_ledger("focused-consumer", focused.CONSUMER_FIELDS, focused.consumer_rows())
    new_ids = [entry["creator_id"] for entry in packet["labels"].values() if entry["arm"] == "A"]
    fresh_plans, public, sources = focused.completed(new_ids)
    fresh_plans = {plan["row"]["trial_id"]: plan for plan in fresh_plans}
    for name in ("focused-schedule.tsv", "focused-schedule-sha256.txt", "focused-consumer-schedule.tsv",
                 "focused-consumer-schedule-sha256.txt", "control-schedule.tsv", "control-schedule-sha256.txt",
                 "control-consumer-schedule.tsv", "control-consumer-schedule-sha256.txt", "focused-source-identities.json"):
        observe(ROOT / name, observations)
    cases = read_json(ROOT / "control-consumer-case-hashes.json", observations)
    actual_cases, caches = observe_tree(ROOT / "control-consumer-cases", trees)
    if caches or {key: item["sha256"] for key, item in actual_cases.items()} != cases:
        raise ValueError("Frozen original consumer bank changed")
    oracle_hashes = read_json(ROOT / "control-oracle-hashes.json", observations)
    add_file(files, ROOT / "control-oracles" / f"{family}.md", "business-oracle.md", observations, oracle_hashes[f"{family}.md"])
    add_file(files, ROOT / "grading-guidance.md", "grading-guidance.md", observations)
    add_tree(files, ROOT / "frozen/main-cases" / family, "original-creator-input", observations, trees)
    add_tree(files, ROOT / "control-consumer-cases" / family, "original-consumer-inputs", observations, trees)
    # Preserve the verified aid's identity externally and permit its existing
    # read-only path. Duplicating its restored display assets would introduce
    # needless binary files into each durable plain-UTF-8 packet checkpoint.
    observe_tree(ROOT / "frozen/skill-creator", trees)
    generated_text(generated, "judgment-boundaries.md", control.BOUNDARIES + FOCUSED_BOUNDARIES + recovered.BOUNDARY_ADDENDUM)
    mapping, provenance, completion_rows = {}, {}, {}
    creator_recoveries = []
    for label in LABELS:
        selected = packet["labels"][label]
        creator_id, arm = selected["creator_id"], selected["arm"]
        row = (focused_creators if arm == "A" else creators)[creator_id]
        completion_rows[creator_id] = {"ledger": "focused-list.tsv" if arm == "A" else "control-list.tsv",
                                       "key": "trial_id", "row": dict(row)}
        check_creator(creator_id, row, family, public, observations, trees)
        manifest, freeze, package = check_freeze(creator_id, fresh_plans.get(creator_id), observations, trees)
        apps = []
        number = int(creator_id.rsplit("-", 1)[1])
        for index, variant in enumerate(VARIANTS, 1):
            use_id = f"{'F' if arm == 'A' else 'C'}-U{2 * (number - 1) + index:03}"
            use_row = (focused_consumers if arm == "A" else consumers)[use_id]
            completion_rows[use_id] = {"ledger": "focused-consumer-list.tsv" if arm == "A" else "control-consumer-list.tsv",
                                       "key": "consumer_id", "row": dict(use_row)}
            assignment = check_application(use_id, creator_id, variant, family, use_row, manifest, freeze, package,
                                           public, sources["common_authoring_aid_sha256"], observations, trees)
            if family != "S06" and assignment["initial_state_evidence_sha256"]:
                raise ValueError("Unexpected native setup on a non-ledger application")
            apps.append((use_id, variant, family, assignment))
        mapping[label] = {"creator": creator_id, "arm": arm, "case": family, "requested_model": row["model"],
                          "requested_effort": row["effort"], "repetition": row["repetition"],
                          "consumers": [app[0] for app in apps]}
        if creator_id in REUSED:
            provenance[label] = reuse_candidate(files, label, creator_id, package, apps, observations, trees)
            continue
        if creator_id in {"control-071", "control-072"}:
            plan = recovery_creator(files, generated, label, creator_id, package, observations)
            creator_recoveries.append(plan)
            provenance[label] = {"creator_recovery": plan["provenance"]}
        else:
            creator_files(files, label, creator_id, package, observations, trees)
            provenance[label] = {"scope": "Original completed creator/application evidence"}
        if arm == "A":
            add_file(files, ROOT / "focused-public" / creator_id / "final-response.md",
                     f"{label}/creator-public-handoff.md", observations)
            add_file(files, ROOT / "validation/focused-format" / f"{creator_id}.json",
                     f"{label}/creator-format-observation.json", observations, freeze["physical_validation_sha256"])
        for use_id, variant, _, assignment in apps:
            standard_application(files, generated, f"{label}/{variant}", use_id, family, assignment, observations, trees)
            handoff = ROOT / "focused-public" / use_id / "final-response.md"
            # Every newly collected application has a separately preserved
            # public handoff, including the eight newly completed C uses.
            add_file(files, handoff, f"{label}/{variant}/public-handoff.md", observations)
    if len(mapping) != 4 or sum(len(item["consumers"]) for item in mapping.values()) != 8:
        raise ValueError("Exactly four Skills and eight assigned applications are required")
    check_blinding(files, generated)
    return {"packet": packet_id, "destinations": destinations, "files": files, "generated": generated,
            "observations": observations, "trees": trees, "mapping": mapping,
            "candidate_provenance": provenance, "creator_recoveries": creator_recoveries,
            "completion_rows": completion_rows}


def recheck_sources(plan):
    ledgers = {}
    for identity_id, item in plan["completion_rows"].items():
        if item["ledger"] not in ledgers:
            ledgers[item["ledger"]] = control.read_ledger(item["ledger"], item["key"])
        if ledgers[item["ledger"]].get(identity_id) != item["row"]:
            raise ValueError(f"Selected completion record changed after preflight: {identity_id}")
    for relative, item in plan["observations"].items():
        if identity(ROOT / relative) != item:
            raise ValueError(f"Source bytes/mode changed after preflight: {relative}")
    for relative, value in plan["trees"].items():
        if inventory(ROOT / relative) != value:
            raise ValueError(f"Source file set/bytes/modes changed after preflight: {relative}")
    for recovery_plan in plan["creator_recoveries"]:
        recovered.verify_creator_plan(ROOT, recovery_plan)


def write_exclusive(path, body, mode):
    checked_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(body)
        os.fchmod(stream.fileno(), mode)


def prepare(plan):
    target, mapping_path, provenance_path = refuse_outputs(plan["packet"])
    recheck_sources(plan)
    target.mkdir(parents=True, exist_ok=False)
    for destination, item in plan["files"].items():
        source = ROOT / item["source"]
        if identity(source) != {key: item[key] for key in ("sha256", "mode")}:
            raise ValueError(f"Source changed before its copy: {source}")
        path = target / destination
        write_exclusive(path, source.read_bytes(), item["mode"])
        shutil.copystat(source, path, follow_symlinks=False)
        if identity(path) != {key: item[key] for key in ("sha256", "mode")}:
            raise ValueError(f"Evidence copy bytes/mode differs: {destination}")
    for destination, body in plan["generated"].items():
        write_exclusive(target / destination, body.encode("utf-8"), 0o644)
    recheck_sources(plan)
    expected = {name: {key: item[key] for key in ("sha256", "mode")} for name, item in plan["files"].items()}
    expected.update({name: {"sha256": hashlib.sha256(body.encode()).hexdigest(), "mode": 0o644}
                     for name, body in plan["generated"].items()})
    if inventory(target) != (expected, {}):
        raise ValueError("Completed packet file set, bytes or modes differ from preflight")
    provenance = {"packet": plan["packet"], "scope": "Evidence packaging only; no trial, recovery capture or quality judgment",
                  "prepared_with_sha256": identity(Path(__file__).resolve())["sha256"],
                  "file_sha256": {key: item["sha256"] for key, item in expected.items()},
                  "file_modes": {key: item["mode"] for key, item in expected.items()},
                  "copied_files": plan["files"], "generated_files": sorted(plan["generated"]),
                  "source_observations": plan["observations"],
                  "source_tree_observations": {key: {"resources": value[0], "excluded_runtime_caches": value[1]}
                                               for key, value in plan["trees"].items()},
                  "candidate_provenance": plan["candidate_provenance"],
                  "selected_completion_rows": plan["completion_rows"],
                  "limits": "Original source paths may remain. Cache bytes are retained only at source. Native SQL is logical state, not SQLite byte identity or a call trace. Recovery limitations are retained, and absent originals are not synthesized."}
    write_exclusive(mapping_path, (json.dumps(plan["mapping"], indent=2) + "\n").encode(), 0o600)
    write_exclusive(provenance_path, (json.dumps(provenance, indent=2) + "\n").encode(), 0o600)
    if json.loads(mapping_path.read_text()) != plan["mapping"] or json.loads(provenance_path.read_text()) != provenance:
        raise ValueError("External identity/provenance read-back differs")
    print(f"Prepared {plan['packet']}: four frozen packages, eight applications; no quality judgment")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", choices=tuple(FIXED_PACKETS), help="One exact fixed packet identity")
    parser.add_argument("--check-only", action="store_true", help="Read-only complete preflight; create no output")
    args = parser.parse_args()
    plan = build_plan(args.packet)
    if args.check_only:
        recheck_sources(plan)
        print(f"Preflight {args.packet}: four frozen packages, eight completed applications; no files written")
    else:
        prepare(plan)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as error:
        raise SystemExit(str(error)) from error
