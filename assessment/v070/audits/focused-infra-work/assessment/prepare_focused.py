"""Prepare the authorized, fixed twelve-cell A versus existing C comparison.

Assessment-only: no trial launch, grading, product edit, or remote write. All
owned outputs are exclusive; partial work and original runtime caches survive.
"""

import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import sqlite3
import stat
import subprocess
import sys
import tempfile

from prepare_control_consumers import (
    CASE_BANK_SHA256, SCHEDULE_SHA256 as CONTROL_SCHEDULE_SHA256,
    artifact_inventory, checked_path, completed_creators as completed_controls,
    creator_input_caches, digest, file_hashes, ignore_runtime_caches,
    refuse_existing, skill_path, verify_bank, write_json,
)
from validate_control import PACKAGES, VALIDATOR

ROOT = Path(__file__).resolve().parent
CONTROL_IDS = tuple(f"control-{number:03}" for number in
                    (19, 20, 23, 24, 43, 44, 47, 48, 67, 68, 71, 72))
PINNED = {
    "frozen-hashes.sha256": "dba1fcdde399d5f0c6a65526ecf2a3ce880ab2bf2b6cd340e90aaed44b5cd32c",
    "main-case-hashes.json": "142cc29cef88dd33d93b682ff596b68968cf3033d6887eadad509aa8e2cb9fd4",
    "common/agent-skills-format.md": "c39f8c9958cf226ae9a0f46c09b680b467968519a726f5ad56463f257ebcd8b0",
}
DISPLAY_ASSETS = {
    "assets/skill-creator-small.svg": "6591bf8ea9bb9435890dbdea299e0d2bd05f3aa893a335d26e4c535e93c8e7fb",
    "assets/skill-creator.png": "a4024b0306ddb05847e1012879d37aaf1e658205199da596f5145ed7a88d9162",
}
# All twelve original C prompts have this identity after replacing only their
# own absolute task-directory path with {{TRIAL}}. No results informed the text.
CONTROL_PROMPT_SHA256 = "5842bdcfd6d0b07fea93987b406c765f0ab31910742f2b046fbd2e87b355fa4d"
CREATOR_FIELDS = ("trial_id", "stage", "case", "arm", "repetition", "model", "effort", "paired_control_id")
CONSUMER_FIELDS = ("consumer_id", "creator_id", "stage", "case", "variant", "model", "effort", "paired_consumer_id")
CACHE_NOTE = ("Regular *.pyc directly inside __pycache__ remain in their original folders; "
              "their hashes are recorded but those bytes are omitted from frozen/copied resources "
              "and durable checkpointing. No non-cache resource is silently discarded.")


def read_json(path):
    return json.loads(checked_path(path).read_text(encoding="utf-8"))


def modes(folder, hashes):
    return {key: stat.S_IMODE(checked_path(folder / key).stat().st_mode) for key in hashes}


def creator_rows():
    return [dict(zip(CREATOR_FIELDS, (f"focus-{index:03}", "focused", case, "A", str(repetition),
                                     model, "high", control)))
            for index, (control, (case, model, repetition)) in enumerate(zip(
                CONTROL_IDS, ((case, model, repetition) for case in ("S03", "S06", "S10")
                              for model in ("gpt-5.6-sol", "gpt-6-astra") for repetition in (1, 2))), 1)]


def consumer_rows():
    result = []
    for row in creator_rows():
        control_number = int(row["paired_control_id"].rsplit("-", 1)[1])
        for index, variant in enumerate(("ordinary", "challenging"), 1):
            result.append(dict(zip(CONSUMER_FIELDS, (
                f"F-U{len(result) + 1:03}", row["trial_id"], "focused", row["case"], variant,
                "gpt-5.6-sol", "high", f"C-U{2 * (control_number - 1) + index:03}"))))
    return result


def table_text(fields, data):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(data)
    return stream.getvalue()


def write_text(path, text):
    with path.open("x", encoding="utf-8", newline="") as stream:
        stream.write(text)


def write_schedule(prefix, fields, data, status):
    body = table_text(fields, data)
    schedule = ROOT / f"{prefix}-schedule.tsv"
    identity = ROOT / f"{prefix}-schedule-sha256.txt"
    write_text(schedule, body)
    write_text(identity, hashlib.sha256(body.encode()).hexdigest() + "\n")
    schedule.chmod(0o444)
    identity.chmod(0o444)
    write_text(ROOT / f"{prefix}-list.tsv", table_text((*fields, "execution", "agent"),
               [{**row, "execution": status, "agent": ""} for row in data]))


def fixed_ledger(prefix, fields, data):
    body = table_text(fields, data)
    schedule = checked_path(ROOT / f"{prefix}-schedule.tsv")
    identity = checked_path(ROOT / f"{prefix}-schedule-sha256.txt")
    if (schedule.read_bytes() != body.encode() or
            identity.read_text().strip() != hashlib.sha256(body.encode()).hexdigest()):
        raise ValueError(f"Fixed focused allocation changed: {prefix}")
    with checked_path(ROOT / f"{prefix}-list.tsv").open(newline="", encoding="utf-8") as stream:
        values = list(csv.DictReader(stream, delimiter="\t"))
    key = fields[0]
    ledger = {row[key]: row for row in values}
    if (len(ledger) != len(values) or set(ledger) != {row[key] for row in data} or
            any(any(ledger[row[key]].get(field) != row[field] for field in fields) for row in data)):
        raise ValueError(f"Mutable ledger differs from the fixed allocation: {prefix}")
    return ledger


def source_identities():
    for relative, expected in PINNED.items():
        if digest(checked_path(ROOT / relative)) != expected:
            raise ValueError(f"Original source identity changed: {relative}")
    public = verify_bank(ROOT / "frozen/main-cases", ROOT / "main-case-hashes.json")
    frozen = dict((relative, value) for value, relative in
                  (line.split("  ", 1) for line in (ROOT / "frozen-hashes.sha256").read_text().splitlines()))
    alps = ROOT / "frozen/alps"
    checked_path(alps)
    alps_actual, alps_modes, links = {}, {}, {}
    for path in sorted(alps.rglob("*")):
        relative = path.relative_to(ROOT).as_posix()
        if path.is_symlink():
            # The original export has exactly these two native Host links.
            if relative not in {"frozen/alps/.agents/skills/design-process-description",
                                "frozen/alps/.agents/skills/design-agent-work-system"}:
                raise ValueError(f"Unexpected frozen ALPS link: {path}")
            checked_path(path.parent)
            links[relative] = str(path.readlink())
            alps_actual[relative] = hashlib.sha256(links[relative].encode()).hexdigest()
        elif path.is_file():
            alps_actual[relative] = digest(checked_path(path))
            alps_modes[relative] = stat.S_IMODE(path.stat().st_mode)
        elif not path.is_dir():
            raise ValueError(f"Unsupported frozen ALPS entry: {path}")
    if alps_actual != {key: value for key, value in frozen.items() if key.startswith("frozen/alps/")}:
        raise ValueError("The complete frozen A file/link set or bytes changed")
    aid = ROOT / "frozen/skill-creator"
    common = file_hashes(aid)
    expected_common = {key.removeprefix("frozen/skill-creator/"): value
                       for key, value in frozen.items() if key.startswith("frozen/skill-creator/")}
    if common != expected_common | DISPLAY_ASSETS:
        raise ValueError("Common frozen authoring aid changed, including restored display assets")
    identities = {"pinned_manifest_sha256": PINNED, "control_schedule_sha256": CONTROL_SCHEDULE_SHA256,
                  "alps_file_or_link_sha256": alps_actual, "alps_file_modes": alps_modes,
                  "alps_symlink_targets": links, "common_authoring_aid_sha256": common,
                  "common_authoring_aid_modes": modes(aid, common),
                  "common_format_mode": stat.S_IMODE((ROOT / "common/agent-skills-format.md").stat().st_mode),
                  "public_input_sha256": public, "public_input_modes": modes(ROOT / "frozen/main-cases", public),
                  "display_asset_provenance": "audits/common-aid-display-restoration.md"}
    return public, identities


def guidance(case):
    base = ROOT / "frozen/alps/skills"
    if case == "S03":
        return f"Use {base}/design-process-description/SKILL.md and its required sources."
    if case == "S06":
        return f"Use {base}/design-agent-work-system/SKILL.md and its required sources."
    return (f"Use the relevant guidance in {base}/design-process-description/SKILL.md and "
            f"{base}/design-agent-work-system/SKILL.md, with their required sources, for the requested design subjects.")


def expected_creator(row, public):
    control_id = row["paired_control_id"]
    original = ROOT / "trials" / control_id
    assignment_path = ROOT / "control-assignments" / f"{control_id}.json"
    assignment = read_json(assignment_path)
    fields = {"trial_id": control_id, "stage": "control", "case": row["case"], "arm": "C",
              "repetition": int(row["repetition"]), "requested_model": row["model"],
              "requested_effort": row["effort"], "context": "fresh"}
    inputs = {key.removeprefix(row["case"] + "/"): value for key, value in public.items()
              if key.startswith(row["case"] + "/")}
    if (any(assignment.get(key) != value for key, value in fields.items()) or
            assignment["input_sha256"] != {"input/" + key: value for key, value in inputs.items()}):
        raise ValueError(f"Paired C assignment differs from its fixed original cell: {control_id}")
    creator_input_caches(original / "input", inputs)
    prompt_path = checked_path(original / "prompt.md")
    original_prompt = prompt_path.read_text(encoding="utf-8")
    normalized = original_prompt.replace(str(original), "{{TRIAL}}")
    if (digest(prompt_path) != assignment["prompt_sha256"] or
            hashlib.sha256(normalized.encode()).hexdigest() != CONTROL_PROMPT_SHA256):
        raise ValueError(f"Original C creator prompt identity changed: {control_id}")
    trial = ROOT / "trials" / row["trial_id"]
    rebound = normalized.replace("{{TRIAL}}", str(trial))
    first, rest = rebound.split("\n\n", 1)
    prompt = first + " " + guidance(row["case"]) + "\n\n" + rest
    metadata = {**fields, "trial_id": row["trial_id"], "stage": "focused", "arm": "A",
                "paired_control_id": control_id, "input_sha256": {"input/" + k: v for k, v in inputs.items()},
                "input_file_modes": {"input/" + k: stat.S_IMODE((ROOT / "frozen/main-cases" / row["case"] / k).stat().st_mode)
                                     for k in inputs},
                "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                "original_control_assignment_sha256": digest(assignment_path),
                "original_control_prompt_sha256": assignment["prompt_sha256"],
                "control_prompt_normalized_sha256": CONTROL_PROMPT_SHA256,
                "added_alps_support": guidance(row["case"])}
    return prompt, inputs, metadata


def paired_controls():
    controls = completed_controls(list(CONTROL_IDS))
    for row in creator_rows():
        original = controls[row["paired_control_id"]]
        if any(original[key] != row[key] for key in ("case", "repetition", "model", "effort")):
            raise ValueError("Fixed C pairing differs from the original schedule")


def prepare_creators():
    destinations = [ROOT / name for name in (
        "focused-assignments", "focused-source-identities.json", "focused-artifact-freezes",
        "frozen/focused-artifacts", "validation/focused-format")]
    for prefix in ("focused", "focused-consumer"):
        destinations += [ROOT / f"{prefix}-{suffix}" for suffix in
                         ("schedule.tsv", "schedule-sha256.txt", "list.tsv")]
    for row in creator_rows():
        destinations.append(ROOT / "trials" / row["trial_id"])
    for row in consumer_rows():
        destinations += consumer_destinations(row["consumer_id"])
    for path in destinations:
        refuse_existing(path)
    paired_controls()
    public, identities = source_identities()
    plans = [(row, *expected_creator(row, public)) for row in creator_rows()]
    # No consumer bank, hidden fixture, or oracle is read or copied here.
    write_json(ROOT / "focused-source-identities.json", identities)
    source_sha = digest(ROOT / "focused-source-identities.json")
    (ROOT / "focused-assignments").mkdir(exist_ok=False)
    for row, prompt, inputs, metadata in plans:
        trial = ROOT / "trials" / row["trial_id"]
        trial.mkdir(parents=True, exist_ok=False)
        shutil.copytree(ROOT / "frozen/main-cases" / row["case"], trial / "input")
        if (file_hashes(trial / "input") != inputs or
                modes(trial / "input", inputs) != {k.removeprefix("input/"): v for k, v in metadata["input_file_modes"].items()}):
            raise ValueError(f"Public input bytes/modes changed while copying: {row['trial_id']}")
        (trial / "deliverables/skills").mkdir(parents=True)
        write_text(trial / "prompt.md", prompt)
        write_json(ROOT / "focused-assignments" / f"{row['trial_id']}.json",
                   {**metadata, "source_identities_sha256": source_sha})
    write_schedule("focused", CREATOR_FIELDS, creator_rows(), "not started")
    write_schedule("focused-consumer", CONSUMER_FIELDS, consumer_rows(), "not prepared")
    print("Prepared focus-001..012 and fixed F-U001..024 metadata; no consumer inputs materialized or trials started")


def completed(creator_ids):
    if not creator_ids or len(set(creator_ids)) != len(creator_ids) or not set(creator_ids) <= {row["trial_id"] for row in creator_rows()}:
        raise ValueError("Use distinct explicit focus-001..012 creator IDs")
    ledger = fixed_ledger("focused", CREATOR_FIELDS, creator_rows())
    fixed_ledger("focused-consumer", CONSUMER_FIELDS, consumer_rows())
    paired_controls()
    public, identities = source_identities()
    if read_json(ROOT / "focused-source-identities.json") != identities:
        raise ValueError("Frozen source bytes, file set, or original modes changed after preparation")
    plans = []
    for creator_id in creator_ids:
        row = ledger[creator_id]
        if row.get("execution") != "completed":
            raise ValueError(f"Coordinator-confirmed creator completion required: {creator_id}")
        prompt, inputs, expected = expected_creator(row, public)
        expected["source_identities_sha256"] = digest(ROOT / "focused-source-identities.json")
        if read_json(ROOT / "focused-assignments" / f"{creator_id}.json") != expected:
            raise ValueError(f"Creator assignment identity changed: {creator_id}")
        trial = ROOT / "trials" / creator_id
        input_caches = creator_input_caches(trial / "input", inputs)
        if ({"input/" + k: v for k, v in modes(trial / "input", inputs).items()} != expected["input_file_modes"] or
                checked_path(trial / "prompt.md").read_bytes() != prompt.encode()):
            raise ValueError(f"Creator input modes or prompt changed: {creator_id}")
        public_evidence = {}
        for path in (trial / "execution-note.md", ROOT / "focused-public" / creator_id / "final-response.md"):
            checked_path(path)
            if not path.is_file() or not path.read_text(encoding="utf-8").strip():
                raise ValueError(f"Preserve the public completion handoff before staging: {path}")
            public_evidence[path.relative_to(ROOT).as_posix()] = digest(path)
        skill = skill_path(creator_id)
        hashes, caches = artifact_inventory(skill)
        plans.append({"row": row, "skill": skill, "file_sha256": hashes, "source_file_modes": modes(skill, hashes),
                      "excluded_runtime_cache_sha256": caches, "creator_input_added_runtime_cache_sha256": input_caches,
                      "public_completion_evidence_sha256": public_evidence})
    return plans, public, identities


def validate(creator_ids):
    plans, _, _ = completed(creator_ids)
    for plan in plans:
        refuse_existing(ROOT / "validation/focused-format" / f"{plan['row']['trial_id']}.json")
    checked_path(VALIDATOR)
    if not VALIDATOR.is_file() or not PACKAGES.is_dir():
        raise ValueError("The original pinned physical-format validator environment is unavailable")
    environment = os.environ.copy()
    environment.update(PYTHONPATH=str(PACKAGES), PYTHONDONTWRITEBYTECODE="1")
    for plan in plans:
        creator_id, target = plan["row"]["trial_id"], plan["skill"]
        command = [sys.executable, str(VALIDATOR), "validate", str(target)]
        result = subprocess.run(command, capture_output=True, text=True, env=environment, timeout=30,
                                cwd=ROOT / "trials" / creator_id)
        if (artifact_inventory(target) != (plan["file_sha256"], plan["excluded_runtime_cache_sha256"]) or
                modes(target, plan["file_sha256"]) != plan["source_file_modes"]):
            raise ValueError(f"Original Skill changed during validation; preserve all evidence: {creator_id}")
        report = ROOT / "validation/focused-format" / f"{creator_id}.json"
        write_json(report, {key: value for key, value in plan.items() if key not in {"row", "skill"}} | {
            "trial": creator_id, "source_path": str(target), "command": command,
            "validator_source": "agentskills/agentskills@f130f348f502d9804278a617f86929846896d2e9 skills-ref",
            "validator_entrypoint_sha256": digest(VALIDATOR), "exit_code": result.returncode,
            "stdout": result.stdout, "stderr": result.stderr,
            "scope": "Physical format only; a failed check remains evidence and does not remove a planned comparison cell"})
        print(f"{creator_id}: format observation exit {result.returncode}; {report}")


def consumer_destinations(consumer_id):
    if any(ROOT.parent.glob(consumer_id + "-ledger-state-*")):
        raise ValueError(f"Preserve existing or partial native state: {consumer_id}")
    return [ROOT / "consumers" / consumer_id, ROOT / "consumer-assignments" / f"{consumer_id}.json",
            ROOT / "consumer-setup" / f"{consumer_id}.json", ROOT / "state-snapshots" / consumer_id]


def snapshot_state(consumer_id, label, setup):
    state = Path(setup["state_path"])
    if (not re.fullmatch(r"F-U\d{3}", consumer_id) or label not in {"initial", "final"} or
            setup.get("consumer_id") != consumer_id or setup.get("setup_verified") is not True or
            state.parent.parent != ROOT.parent or state.name != "ledger.sqlite" or
            not state.parent.name.startswith(consumer_id + "-ledger-state-") or
            state.resolve() != state or not state.is_file()):
        raise ValueError("Native state does not match this focused consumer's verified allocation")
    target = ROOT / "state-snapshots" / consumer_id
    for suffix in ("sql", "json"):
        refuse_existing(target / f"{label}.{suffix}")
    connection = sqlite3.connect(state.as_uri() + "?mode=ro", uri=True)
    try:
        connection.execute("BEGIN")
        if connection.execute("PRAGMA quick_check").fetchall() != [("ok",)]:
            raise ValueError("Native state integrity check failed")
        sql = "\n".join(connection.iterdump()) + "\n"
    finally:
        connection.close()
    target.mkdir(parents=True, exist_ok=True)
    write_text(target / f"{label}.sql", sql)
    write_json(target / f"{label}.json", {"consumer_id": consumer_id, "state_path": str(state),
               "snapshot": label, "sqlite_version": sqlite3.sqlite_version,
               "sql_sha256": hashlib.sha256(sql.encode()).hexdigest(),
               "representation": "Native SQL from a consistent committed read transaction; not byte-identical SQLite"})


def prepare_ledger(folder, source):
    """Same fixed init/describe observations as control_ledger_state, F IDs only."""
    consumer_id = folder.name
    if folder.parent != ROOT / "consumers" or consumer_id not in {row["consumer_id"] for row in consumer_rows() if row["case"] == "S06"}:
        raise ValueError("Expected this focused S06 consumer task folder")
    fixture, api = source / "fixture.json", folder / "input/ledger_api.py"
    records = read_json(fixture)["records"]
    canonical = json.dumps(records, sort_keys=True, separators=(",", ":"))
    expected_snapshot = "snap_" + hashlib.sha256(canonical.encode()).hexdigest()[:24]
    record_path = ROOT / "consumer-setup" / f"{consumer_id}.json"
    refuse_existing(record_path)
    if any(ROOT.parent.glob(consumer_id + "-ledger-state-*")):
        raise ValueError(f"Preserve existing or partial native setup: {consumer_id}")
    state = Path(tempfile.mkdtemp(prefix=consumer_id + "-ledger-state-", dir=ROOT.parent)) / "ledger.sqlite"
    record = {"consumer_id": consumer_id, "state_path": str(state), "source_packet": str(source),
              "fixture_sha256": digest(fixture), "interface_sha256": digest(api), "setup_verified": False, "calls": []}
    write_json(record_path, record)
    for argv, expected in (
        ([sys.executable, str(api), "--state", str(state), "init", "--fixture", str(fixture)],
         {"state": "ready", "snapshot_id": expected_snapshot, "total_records": len(records)}),
        ([sys.executable, str(api), "--state", str(state), "describe"],
         {"snapshot_id": expected_snapshot, "total_records": len(records), "page_size": 3,
          "calls_per_tranche": 2, "tranche": 1, "remaining_calls": 2}),
    ):
        result = subprocess.run(argv, capture_output=True, text=True, timeout=15, cwd=folder)
        record["calls"].append({"argv": argv, "exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr})
        record_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        if result.returncode != 0 or result.stderr or json.loads(result.stdout) != expected:
            raise ValueError(f"Native setup observation mismatch; partial evidence retained: {consumer_id}")
    record["setup_verified"] = True
    record_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    snapshot_state(consumer_id, "initial", record)
    return state


def consumer_prompt(folder, target):
    # Unchanged reviewed C application conditions, with only assigned paths.
    return f"""Use the Skill at {target}/SKILL.md to complete the user's task in {folder}/input/request.md with any accompanying files in that input folder. Write the user-facing answer to {folder}/answer.md using apply_patch. Use {folder}/work for temporary processing and permitted local outputs.

This is an application of the supplied Skill, not a request to redesign, repair, install or publish it. Do not modify the Skill or supplied original inputs. If it cannot support the requested work, report the concrete limitation and perform only independently valid work. Do not change external state or send messages. Synthetic state changes are allowed only when the task explicitly authorizes them, using its supplied interface; do not edit simulation state directly.

You may consult the frozen skill-creator aid at {ROOT}/frozen/skill-creator/SKILL.md if useful. It is available, not required. Read only your supplied Skill and its needed resources, your task input, that common authoring aid and any necessary standard runtime documentation. Use {folder} as your task working directory; do not enumerate the shared workspace. Do not read creator prompts, execution notes, sibling trials, evaluation plans, audits, expected answers or other worktrees. Do not delegate. The parent handles durable saving; do not commit, push, upload or install anything.

Record actual public commands, exit codes, relevant stdout/stderr and files used in {folder}/execution-note.md. Distinguish exact captured observations from summaries and unperformed checks; do not include private reasoning. If no tool is needed, say so. Your final response should give the answer and identify any limitation, not merely say that files were created.
"""


def prepare_consumers(creator_ids):
    plans, public, identities = completed(creator_ids)
    case_manifest = ROOT / "control-consumer-case-hashes.json"
    if digest(checked_path(case_manifest)) != CASE_BANK_SHA256:
        raise ValueError("The independently reviewed consumer bank identity changed")
    verify_bank(ROOT / "control-consumer-cases", case_manifest)
    for plan in plans:
        creator_id = plan["row"]["trial_id"]
        report_path = ROOT / "validation/focused-format" / f"{creator_id}.json"
        report = read_json(report_path)
        if (report.get("trial") != creator_id or report.get("source_path") != str(plan["skill"]) or
                type(report.get("exit_code")) is not int or any(report.get(key) != value
                for key, value in plan.items() if key not in {"row", "skill"})):
            raise ValueError(f"Record unchanged completed format observation before freezing: {creator_id}")
        plan["validation_path"] = report_path
        plan["freeze"] = ROOT / "frozen/focused-artifacts" / creator_id
        plan["manifest"] = ROOT / "focused-artifact-freezes" / f"{creator_id}.json"
        refuse_existing(plan["freeze"])
        refuse_existing(plan["manifest"])
        plan["consumers"] = []
        for row in (value for value in consumer_rows() if value["creator_id"] == creator_id):
            for path in consumer_destinations(row["consumer_id"]):
                refuse_existing(path)
            source = ROOT / "control-consumer-cases" / row["case"] / row["variant"]
            hashes = file_hashes(source / "input")
            request = (source / "input/request.md").read_text(encoding="utf-8")
            for token in ("{{INPUT_DIR}}", "{{STATE_PATH}}", "{{ENVIRONMENT_PATH}}"):
                request = request.replace(token, "resolved-path")
            if "{{" in request or "}}" in request:
                raise ValueError(f"Unrecognized consumer request token: {source}")
            interface = {"S06": "ledger_api.py", "S10": "release_tool.py"}.get(row["case"])
            if interface in hashes:
                raise ValueError(f"Interface must come from the unchanged public source: {source}")
            plan["consumers"].append((row, source, hashes, modes(source / "input", hashes)))
    # Completion, all inventories, and every selected destination pass first.
    for plan in plans:
        creator_id, skill = plan["row"]["trial_id"], plan["skill"]
        plan["freeze"].mkdir(parents=True, exist_ok=False)
        frozen_skill = plan["freeze"] / skill.name
        shutil.copytree(skill, frozen_skill, ignore=ignore_runtime_caches)
        if (artifact_inventory(skill) != (plan["file_sha256"], plan["excluded_runtime_cache_sha256"]) or
                file_hashes(frozen_skill) != plan["file_sha256"] or
                modes(skill, plan["file_sha256"]) != plan["source_file_modes"] or
                modes(frozen_skill, plan["file_sha256"]) != plan["source_file_modes"]):
            raise ValueError(f"Original/frozen Skill bytes or modes changed: {creator_id}")
        write_json(plan["manifest"], {key: plan[key] for key in (
            "file_sha256", "source_file_modes", "excluded_runtime_cache_sha256",
            "creator_input_added_runtime_cache_sha256", "public_completion_evidence_sha256")} | {
            "creator_id": creator_id, "source_path": str(skill), "frozen_path": str(frozen_skill),
            "paired_control_id": plan["row"]["paired_control_id"], "cache_handling": CACHE_NOTE,
            "schedule_sha256": digest(ROOT / "focused-schedule.tsv"), "case_bank_manifest_sha256": CASE_BANK_SHA256,
            "source_identities_sha256": digest(ROOT / "focused-source-identities.json"),
            "physical_validation_sha256": digest(plan["validation_path"]), "scope": "Resource identity; no quality judgment"})
        for row, source, hashes, source_modes in plan["consumers"]:
            consumer_id = row["consumer_id"]
            folder = ROOT / "consumers" / consumer_id
            folder.mkdir(parents=True, exist_ok=False)
            (folder / "work").mkdir()
            target = folder / "skill" / skill.name
            shutil.copytree(frozen_skill, target)
            shutil.copytree(source / "input", folder / "input")
            if (file_hashes(target) != plan["file_sha256"] or modes(target, plan["file_sha256"]) != plan["source_file_modes"] or
                    file_hashes(source / "input") != hashes or file_hashes(folder / "input") != hashes or
                    modes(source / "input", hashes) != source_modes or modes(folder / "input", hashes) != source_modes):
                raise ValueError(f"Consumer source/copy bytes or modes changed: {consumer_id}")
            state = folder / "input/state.json"
            interface = {"S06": "ledger_api.py", "S10": "release_tool.py"}.get(row["case"])
            if interface:
                original = ROOT / "frozen/main-cases" / row["case"] / interface
                shutil.copy2(original, folder / "input" / interface)
                if (digest(folder / "input" / interface) != public[row["case"] + "/" + interface] or
                        stat.S_IMODE((folder / "input" / interface).stat().st_mode) != stat.S_IMODE(original.stat().st_mode)):
                    raise ValueError(f"Public interface changed while copying: {consumer_id}")
            if row["case"] == "S06":
                state = prepare_ledger(folder, source)
            request_source = source / "input/request.md"
            request, substitutions = request_source.read_text(encoding="utf-8"), []
            for token, value in (("{{INPUT_DIR}}", str(folder / "input")), ("{{STATE_PATH}}", str(state)),
                                 ("{{ENVIRONMENT_PATH}}", str(folder / "input"))):
                if token in request:
                    substitutions.append({"token": token, "value": value, "occurrences": request.count(token)})
                    request = request.replace(token, value)
            (folder / "input/request.md").write_text(request, encoding="utf-8")
            prompt = consumer_prompt(folder, target)
            write_text(folder / "prompt.md", prompt)
            copied = {part + "/" + key: value for part in ("skill", "input") for key, value in file_hashes(folder / part).items()}
            state_evidence = {relative: digest(checked_path(ROOT / relative)) for relative in (
                f"consumer-setup/{consumer_id}.json", f"state-snapshots/{consumer_id}/initial.sql",
                f"state-snapshots/{consumer_id}/initial.json")} if row["case"] == "S06" else {}
            write_json(ROOT / "consumer-assignments" / f"{consumer_id}.json", {
                "consumer_id": consumer_id, "creator_id": creator_id, "stage": "focused", "case": row["case"],
                "variant": row["variant"], "paired_consumer_id": row["paired_consumer_id"],
                "requested_model": row["model"], "requested_effort": row["effort"], "context": "fresh",
                "copied_sha256": copied, "copied_file_modes": modes(folder, copied),
                "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                "artifact_freeze_manifest": str(plan["manifest"]), "artifact_freeze_sha256": digest(plan["manifest"]),
                "initial_state_evidence_sha256": state_evidence, "request_source": str(request_source),
                "request_source_sha256": digest(request_source), "request_substitutions": substitutions,
                "case_bank_manifest_sha256": CASE_BANK_SHA256, "schedule_sha256": digest(ROOT / "focused-consumer-schedule.tsv"),
                "common_authoring_aid_sha256": identities["common_authoring_aid_sha256"],
                "source_identities_sha256": digest(ROOT / "focused-source-identities.json")})
            print(f"{consumer_id}: prepared from {creator_id}, {row['variant']}; not started; coordinator records status")


def final_snapshots(consumer_ids):
    ledger = fixed_ledger("focused-consumer", CONSUMER_FIELDS, consumer_rows())
    if not consumer_ids or len(set(consumer_ids)) != len(consumer_ids):
        raise ValueError("Use distinct explicit focused S06 consumer IDs")
    case_manifest = ROOT / "control-consumer-case-hashes.json"
    if digest(checked_path(case_manifest)) != CASE_BANK_SHA256:
        raise ValueError("The independently reviewed consumer bank identity changed")
    case_hashes = verify_bank(ROOT / "control-consumer-cases", case_manifest)
    public, _ = source_identities()
    plans = []
    for consumer_id in consumer_ids:
        row = ledger.get(consumer_id, {})
        if row.get("case") != "S06" or row.get("execution") != "completed":
            raise ValueError(f"Coordinator-confirmed focused S06 consumer completion required: {consumer_id}")
        assignment = read_json(ROOT / "consumer-assignments" / f"{consumer_id}.json")
        expected = {"consumer_id": consumer_id, "creator_id": row["creator_id"], "stage": "focused", "case": "S06",
                    "variant": row["variant"], "paired_consumer_id": row["paired_consumer_id"],
                    "requested_model": row["model"], "requested_effort": row["effort"], "context": "fresh"}
        initial = assignment["initial_state_evidence_sha256"]
        paths = {f"consumer-setup/{consumer_id}.json", f"state-snapshots/{consumer_id}/initial.sql",
                 f"state-snapshots/{consumer_id}/initial.json"}
        if (any(assignment.get(key) != value for key, value in expected.items()) or set(initial) != paths or
                any(digest(checked_path(ROOT / key)) != value for key, value in initial.items())):
            raise ValueError(f"Focused assignment or initial state evidence changed: {consumer_id}")
        setup = read_json(ROOT / "consumer-setup" / f"{consumer_id}.json")
        metadata = read_json(ROOT / "state-snapshots" / consumer_id / "initial.json")
        source = ROOT / "control-consumer-cases/S06" / row["variant"]
        state_bindings = [item for item in assignment["request_substitutions"] if item["token"] == "{{STATE_PATH}}"]
        if (setup.get("consumer_id") != consumer_id or setup.get("setup_verified") is not True or
                setup.get("source_packet") != str(source) or
                setup.get("fixture_sha256") != case_hashes[f"S06/{row['variant']}/fixture.json"] or
                setup.get("interface_sha256") != public["S06/ledger_api.py"] or
                state_bindings != [{"token": "{{STATE_PATH}}", "value": setup["state_path"], "occurrences": 1}] or
                metadata.get("consumer_id") != consumer_id or metadata.get("snapshot") != "initial" or
                metadata.get("state_path") != setup["state_path"] or
                metadata.get("sql_sha256") != initial[f"state-snapshots/{consumer_id}/initial.sql"] or
                setup["interface_sha256"] != assignment["copied_sha256"]["input/ledger_api.py"]):
            raise ValueError(f"Native state evidence is misbound: {consumer_id}")
        records = read_json(source / "fixture.json")["records"]
        canonical = json.dumps(records, sort_keys=True, separators=(",", ":"))
        snapshot_id = "snap_" + hashlib.sha256(canonical.encode()).hexdigest()[:24]
        expected_calls = ({"state": "ready", "snapshot_id": snapshot_id, "total_records": len(records)},
                          {"snapshot_id": snapshot_id, "total_records": len(records), "page_size": 3,
                           "calls_per_tranche": 2, "tranche": 1, "remaining_calls": 2})
        if len(setup["calls"]) != 2 or any(call["exit_code"] != 0 or call["stderr"] or
                json.loads(call["stdout"]) != expected for call, expected in zip(setup["calls"], expected_calls)):
            raise ValueError(f"Original setup observations do not establish the prescribed initial state: {consumer_id}")
        for suffix in ("sql", "json"):
            refuse_existing(ROOT / "state-snapshots" / consumer_id / f"final.{suffix}")
        plans.append((consumer_id, setup))
    for consumer_id, setup in plans:
        snapshot_state(consumer_id, "final", setup)
        print(f"{consumer_id}: preserved final committed SQL; not a business adequacy judgment")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("creators", help="Prepare exactly the fixed twelve A creators; no consumer cases")
    for name in ("validate", "consumers"):
        command = commands.add_parser(name, help="Operate on explicit completed A creators only")
        command.add_argument("creator_ids", nargs="+")
    command = commands.add_parser("snapshot", help="Preserve final native SQL for explicit completed F S06 consumers")
    command.add_argument("consumer_ids", nargs="+")
    args = parser.parse_args()
    if args.command == "creators":
        prepare_creators()
    elif args.command == "validate":
        validate(args.creator_ids)
    elif args.command == "consumers":
        prepare_consumers(args.creator_ids)
    else:
        final_snapshots(args.consumer_ids)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, json.JSONDecodeError, subprocess.SubprocessError) as error:
        raise SystemExit(str(error)) from error
