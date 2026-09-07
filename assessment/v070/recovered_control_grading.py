"""Package reviewed C-U084–093 evidence and label four new creator recovery freezes.

Assessment infrastructure only. This module neither grades nor executes a task.
The fixed recovery inputs are deliberately closed to unreviewed additions.
"""

import csv
import hashlib
import json
from pathlib import Path
import stat

from prepare_control_consumers import artifact_inventory, checked_path, file_hashes

SOURCE_COMMIT = "75c0ea9bddf379c5e1803e4c0114ba5b47c871d8"
MANIFEST_PATH = "recovery/consumer-evidence/provenance.json"
MANIFEST_SHA256 = "4a24e1cb17327ea2b05e11b9c8cabcd2324e6b0ec6f9a8f66bbadadd322bf35b"
ASSIGNMENT_SHA256 = {
    "C-U084": "ef173b00d243e4532dd3cd1a0eb970ed925b7c77daa445690a16b8eee84d5e4f",
    "C-U085": "f9a85f38dc1248073afde64d78d2fa539831427b89c5e3137a0b142783a6c988",
    "C-U086": "ee5cd3120cbb59133e8ea25d46df530fb344dd30ebed892c263927a868493cb9",
    "C-U087": "cc7a3b9159e6382e0132b7a3ce477e442c7f4daceafdbc15ef4bff4d09e47f16",
    "C-U088": "ba9f97abd633d8eede957ba63f98f7058dd6e1e413b846ab47d01149006cd222",
    "C-U089": "f09564812bf5bab6fe58f2680708f7dba66b23ef220b4a62ba4dad4cb48a3c6e",
    "C-U090": "2f556d797eabbd97ae59676fa9e9b587552382081f00f65cca064b748ba4a54e",
    "C-U091": "ec70f79f42a91eadcb95fdecfc643fe80f70dab3189542cc24c71096a0e61fce",
    "C-U092": "1e57bff99ac75a751169c51c08cb8b70f6491e65c55e367c3873f37f824ae261",
    "C-U093": "00fab7193f17ebff9cbfa1f0f8b97eff16bbe310750cb7c1cd82aaa499769eb7",
}
ORIGINAL_OBSERVATIONS = {
    "C-U084": {
        "answer.md": "bd965630931d2b407cc6e2471d00321172d11aaa87a6bd61cc150bcd2f82a4ce",
        "execution-note.md": "df1d6f6fdeff1411f1d3e3365b72bbacb7dbe8d9571ee8c12e21946fc1decb87",
        "work/reimbursement-rollup-2026-06-10_2026-06-18.checkpoint.json": "1a72249018b991ee0f1dd70c036d126d8a1f70fa70e6c4b229e2dc3439e5e150",
    },
    "C-U085": {
        "answer.md": "a0a57d77b78a89ee1d728387a806d0f7fe2d665aac94b04aa1370ab6c612ade9",
        "execution-note.md": "7442620a4e99ac001df44fcba75a29c1fb585132cde48eda58f880ec671f5238",
        "work/reimbursement-2026-04-03_2026-04-09.checkpoint.json": "29a3cd1b8aab2b3b35548c14fad40f473472683e84bd1f8343984080b7cfb173",
    },
}
ORIGINAL_RELAYS = {
    "C-U084": ("ae45716269fd9a7fb84945ca8a735c40182d9e1431ad13273eb52d9c35b791e9", "baaa3fabfe615fac7abebbfe165bf67e2681d517"),
    "C-U085": ("c825dcb5a4eb117ee059ac00f61ff3fb1377f2fed1afa2bb7da18a4fa6f08742", "a8bed5c4a45c37e5a74372c2e4edb66d98122813"),
}
CAPTURE_SHA256 = "112e2dc9ab5110e0ef0dd99eb0be53c21a42e5d57978c4626832424fb296c9c4"
WORKFLOW_SHA256 = "0abbc92774a836c30973c9737b3c758d441380122565f54f4e3f401711722006"
REQUEST_PROVENANCE_PATH = "recovery/C-U092-request-hash-match-provenance.json"
REQUEST_PROVENANCE_SHA256 = "1d97138dabefb9389245c0804044cb8733668e75fccd3197328b14917729ee86"
CREATOR_COMPANION_PATH = "recovery/creator-recovery-freezes-001.json"
CREATOR_COMPANION_SHA256 = "03cd21ec820654b6978ea75c903bde1863b1cc625614fe5bbf1859d693f1d402"
RECOVERED_CREATORS = {f"control-{number:03}" for number in range(69, 73)}
COMMITTED_CREATOR_NOTES = {
    "control-069": "358a9face475b70dae4d513206b215fa3495432344b129968a47646d880a4fb6",
    "control-070": "780adc079178f47a0e8945c1c76a48e338122a5fea62962a6948638458202fe9",
}
BOUNDARY_ADDENDUM = """
Some S06 applications include evidence-availability.md and recovery-provenance.json.
Read these before assessing the application. Prepared inputs/Skills are the
assignment-backed resources; no final resource inventory is asserted for them.
Recovered public text and checkpoint renderings retain their separate labels.
Matched SQL is a content-addressed supplement, not a new or reconstructed final
capture. Original per-application final metadata and specified missing artifacts
remain unavailable. The same business criteria and missing-observation rules apply.
"""


def sha_bytes(value):
    return hashlib.sha256(value).hexdigest()


def blob_sha(value):
    return hashlib.sha1(f"blob {len(value)}\0".encode() + value).hexdigest()


def source(root, relative):
    path = root / relative
    if Path(relative).is_absolute() or ".." in Path(relative).parts or not path.is_relative_to(root):
        raise ValueError("Recovery source must stay inside the assessment")
    return checked_path(path)


def checked_bytes(root, relative, expected):
    value = source(root, relative).read_bytes()
    if sha_bytes(value) != expected:
        raise ValueError(f"Preserved recovery evidence changed: {relative}")
    return value


def recovery_manifest(root):
    manifest = json.loads(checked_bytes(root, MANIFEST_PATH, MANIFEST_SHA256))
    expected = {item["path"].removeprefix("recovery/consumer-evidence/"): item["sha256"] for item in manifest["files"]}
    if len(expected) != 32 or len(expected) != len(manifest["files"]):
        raise ValueError("Exactly the reviewed 32 supplemental files are required")
    actual = file_hashes(source(root, "recovery/consumer-evidence"))
    actual.pop("provenance.json", None)
    if actual != expected:
        raise ValueError("Missing, changed or unknown consumer recovery supplement")
    for item in manifest["files"]:
        if item["consumer_id"] not in ASSIGNMENT_SHA256 or item["source_commit"] != SOURCE_COMMIT:
            raise ValueError("Unreviewed recovery identity or source commit")
        if "source_relay" in item:
            relay = checked_bytes(root, item["source_relay"], item["source_sha256"])
            start, end = item["source_body_lines_inclusive"]
            body = b"".join(relay.splitlines(keepends=True)[start - 1:end])
            if blob_sha(relay) != item["source_blob_sha"] or body != source(root, item["path"]).read_bytes():
                raise ValueError("Recovered text no longer matches the retained relay body")
        else:
            original = checked_bytes(root, item["source_path"], item["sha256"])
            if blob_sha(original) != item["source_blob_sha"]:
                raise ValueError("Matched SQL committed source identity differs")
    return manifest


def historical_excerpt(root, consumer_id):
    text = source(root, "RECOVERY-ENVIRONMENT-OFFLINE.md").read_text(encoding="utf-8")
    start = text.index("Actual final native API SQL was captured locally")
    capture = text[start:text.index("\n\n", start)]
    if sha_bytes(capture.encode()) != CAPTURE_SHA256:
        raise ValueError("Historical captured-state digest observation changed")
    parts = [capture]
    if consumer_id == "C-U093":
        start = text.index("A separate consumer-produced workflow checkpoint exists")
        workflow = text[start:text.index("\n\nThe primary S06-P02 grader", start)]
        if sha_bytes(workflow.encode()) != WORKFLOW_SHA256:
            raise ValueError("Historical workflow-checkpoint observation changed")
        parts.append(workflow)
    return ("# Historical state observations\n\n"
            f"Exact selected paragraphs from RECOVERY-ENVIRONMENT-OFFLINE.md at `{SOURCE_COMMIT}`. "
            "The original document's surrounding grades, configuration and progress material is not included. "
            "These outage-time observations are followed by the current availability limits in evidence-availability.md.\n\n"
            + "\n\n".join(parts) + "\n")


def plan_application(root, consumer_id, assignment):
    if consumer_id not in ASSIGNMENT_SHA256:
        raise ValueError("Supplemental packaging is limited to original completed S06 C-U084–093")
    original_assignment = json.loads(checked_bytes(root, f"consumer-assignments/{consumer_id}.json", ASSIGNMENT_SHA256[consumer_id]))
    if assignment != original_assignment or assignment["consumer_id"] != consumer_id or assignment["case"] != "S06":
        raise ValueError("Original supplemental application identity differs")
    with source(root, "control-consumer-list.tsv").open(newline="", encoding="utf-8") as stream:
        rows = [row for row in csv.DictReader(stream, delimiter="\t") if row["consumer_id"] == consumer_id]
    if len(rows) != 1 or rows[0]["execution"] != "completed" or any(
            rows[0][key] != assignment[key] for key in ("creator_id", "case", "variant")):
        raise ValueError("The original supplemental application must be explicitly completed")
    manifest = recovery_manifest(root)
    entries = [item for item in manifest["files"] if item["consumer_id"] == consumer_id]
    folder = source(root, f"consumers/{consumer_id}")
    expected = {**assignment["copied_sha256"], "prompt.md": assignment["prompt_sha256"],
                **ORIGINAL_OBSERVATIONS.get(consumer_id, {})}
    if file_hashes(folder) != expected:
        raise ValueError("Prepared resources or surviving original observations differ; no fallback permitted")
    initial = assignment["initial_state_evidence_sha256"]
    expected_initial = {f"consumer-setup/{consumer_id}.json", f"state-snapshots/{consumer_id}/initial.sql",
                        f"state-snapshots/{consumer_id}/initial.json"}
    if set(initial) != expected_initial:
        raise ValueError("Original initial-state evidence identity differs")
    for relative, value in initial.items():
        checked_bytes(root, relative, value)
    if set(file_hashes(source(root, f"state-snapshots/{consumer_id}"))) != {"initial.sql", "initial.json"}:
        raise ValueError("Unexpected original final/snapshot evidence requires reconciliation")
    if source(root, f"recovery-bindings/{consumer_id}.json").exists():
        raise ValueError("A completed supplemental consumer must not have a restored initial-state binding")
    files = []

    def add(relative, destination, digest, role, mode=None):
        path = source(root, relative)
        checked_bytes(root, relative, digest)
        observed_mode = stat.S_IMODE(path.stat().st_mode)
        if mode is not None and observed_mode != mode:
            raise ValueError(f"Original resource mode differs: {relative}")
        files.append({"source": relative, "destination": destination, "sha256": digest,
                      "observed_copy_source_mode": observed_mode, "role": role})

    add(f"consumers/{consumer_id}/prompt.md", "prompt.md", assignment["prompt_sha256"], "original prepared prompt", 0o644)
    if set(assignment["copied_file_modes"]) != set(assignment["copied_sha256"]):
        raise ValueError("Original copied-resource mode identities incomplete")
    for relative, value in assignment["copied_sha256"].items():
        top, rest = relative.split("/", 1)
        if top not in {"input", "skill"}:
            raise ValueError("Unexpected prepared-resource role")
        add(f"consumers/{consumer_id}/{relative}", f"prepared-{top}/{rest}", value,
            "assignment-backed prepared resource; final inventory unavailable", assignment["copied_file_modes"][relative])
    for relative, value in ORIGINAL_OBSERVATIONS.get(consumer_id, {}).items():
        destination = ("original-work-evidence/" + Path(relative).name if relative.startswith("work/")
                       else "original-public-observations/" + relative)
        add(f"consumers/{consumer_id}/{relative}", destination, value, "surviving original observation", 0o644)
    for relative, value in initial.items():
        destination = ("setup-observations.json" if relative.startswith("consumer-setup/")
                       else "committed-initial-state/" + Path(relative).name)
        add(relative, destination, value, "original assignment-anchored initial observation")
    relay_path = f"recovery/control-use-{consumer_id[-3:]}-relay.md"
    if consumer_id in ORIGINAL_RELAYS:
        relay_digest, relay_blob = ORIGINAL_RELAYS[consumer_id]
    else:
        relay_entry = next(item for item in entries if "source_relay" in item)
        relay_digest, relay_blob = relay_entry["source_sha256"], relay_entry["source_blob_sha"]
    if blob_sha(checked_bytes(root, relay_path, relay_digest)) != relay_blob:
        raise ValueError("Retained source-relay blob identity differs")
    add(relay_path, "recovery-provenance/source-relay.md", relay_digest, "unchanged original recovery relay")
    for item in entries:
        role = item["role"]
        if role in {"answer.md", "execution-note.md"}:
            destination = "recovered-public-text/" + role
        elif role == "checkpoint-rendering.json":
            destination = "recovered-work-evidence/" + role
        elif role == "matched-final-logical-state-supplement":
            destination = "logical-state-supplement/matched-final-state.sql"
            add(item["source_path"], "recovery-provenance/matched-sql-source.sql", item["sha256"],
                "committed byte source of the matching SQL; not this consumer's final capture")
        else:
            raise ValueError("Unknown supplemental evidence role")
        add(item["path"], destination, item["sha256"], item["scope"])
    if consumer_id == "C-U092":
        request_provenance = json.loads(checked_bytes(root, REQUEST_PROVENANCE_PATH, REQUEST_PROVENANCE_SHA256))
        rendering = checked_bytes(root, request_provenance["source"]["path"], request_provenance["source"]["sha256"])
        exact = checked_bytes(root, request_provenance["recovered"]["path"], request_provenance["recovered"]["sha256"])
        review = request_provenance["independent_review"]
        checked_bytes(root, review["path"], review["sha256"])
        if not rendering.endswith(b"\n") or rendering[:-1] != exact or len(exact) != request_provenance["byte_length"]:
            raise ValueError("C-U092 request bytes do not match the reviewed one-LF removal")
        add(request_provenance["recovered"]["path"], "recovered-work-evidence/request-hash-matched.json",
            request_provenance["recovered"]["sha256"], request_provenance["scope"])
        add(REQUEST_PROVENANCE_PATH, "recovery-provenance/request-hash-match.json", REQUEST_PROVENANCE_SHA256,
            "reviewed request-checkpoint byte recovery; not final API state")
    missing = ["Original per-application final API metadata, original SQLite byte identity and complete call history.",
               "A complete post-execution resource inventory; prepared-resource hashes do not establish it.",
               "Uncaptured locks, journals and other absent filesystem observations."]
    if consumer_id == "C-U092":
        missing.append("Final API SQL and its historical captured digest are unavailable. The request/checkpoint rendering and hash-matched request bytes are a different artifact.")
    if consumer_id == "C-U093":
        missing.append("The consumer-produced workflow SQLite checkpoint and its native SQL remain unavailable despite retained historical hashes. The API-state supplement is a different database.")
    if consumer_id == "C-U091":
        missing.append("The checkpoint is a pretty-printed logical rendering; original compact bytes are unavailable.")
    if consumer_id == "C-U089":
        missing.append("The checkpoint rendering retains a display newline; the relay does not establish the original terminal-newline bytes.")
    provenance = {"scope": "Evidence packaging for the same completed original application; no replay or new final capture",
                  "source_commit": SOURCE_COMMIT, "source_manifest": MANIFEST_PATH,
                  "source_manifest_sha256": MANIFEST_SHA256, "source_entries": entries,
                  "source_relay_blob": relay_blob, "files": files, "unavailable": missing,
                  "historical_capture_paragraph_sha256": CAPTURE_SHA256}
    availability = ("# Evidence availability\n\n"
                    "This packet preserves one completed original application. Read the public answer and note in "
                    + ("original-public-observations/. Those files and original-work-evidence/ survive as committed original bytes. "
                       if consumer_id in ORIGINAL_OBSERVATIONS else
                       "recovered-public-text/. These are retained successful-operation text extracts, not a recovered original filesystem attestation. ")
                    + "The unchanged relay is in recovery-provenance/source-relay.md.\n\n"
                    "prepared-input/ and prepared-skill/ match the original assignment's bytes and modes. "
                    "They are supplied for understanding and disposable component checks. No observed-final-skill/, "
                    "final-input-state/ or final resource-inventory claim is supplied for this application.\n\n"
                    "committed-initial-state/ and setup-observations.json are original initial evidence. "
                    "Any logical-state-supplement/ contains committed SQL matching a historically recorded digest; "
                    "it is not original per-trial final metadata or a new final capture. "
                    "Recovered checkpoint renderings remain labelled renderings; any separately named hash-matched request bytes "
                    "retain their exact-byte transformation and historical digest proof. "
                    "Their source/provenance and the selected historical observations are included.\n\n"
                    "Unavailable observations:\n\n" + "".join(f"- {item}\n" for item in missing)
                    + "\nThe original business criteria, denominator and missing-observation rules remain unchanged. "
                    "These packaging labels neither award a grade nor invalidate the application.\n")
    return {"consumer_id": consumer_id, "files": files, "provenance": provenance,
            "availability": availability, "historical_excerpt": historical_excerpt(root, consumer_id)}


def copy_planned_files(root, files, destination, copy_file):
    for item in files:
        original = source(root, item["source"])
        if not original.is_file():
            raise ValueError("Planned recovery source must remain a regular file")
        checked_bytes(root, item["source"], item["sha256"])
        if stat.S_IMODE(original.stat().st_mode) != item["observed_copy_source_mode"]:
            raise ValueError("Recovery source mode changed after preflight")
        target = destination / item["destination"]
        copy_file(original, target)
        if sha_bytes(target.read_bytes()) != item["sha256"] or stat.S_IMODE(target.stat().st_mode) != item["observed_copy_source_mode"]:
            raise ValueError("Recovery evidence copy differs")


def write_application(root, plan, destination, copy_file):
    checked_path(destination)
    if destination.exists() or destination.resolve() != destination or not destination.is_relative_to(root):
        raise ValueError("Preserve existing/partial recovered application packet")
    destination.mkdir(parents=True, exist_ok=False)
    copy_planned_files(root, plan["files"], destination, copy_file)
    generated = {"evidence-availability.md": plan["availability"],
                 "recovery-provenance.json": json.dumps(plan["provenance"], indent=2) + "\n",
                 "recovery-provenance/historical-state-observations.md": plan["historical_excerpt"]}
    for relative, text in generated.items():
        with (destination / relative).open("x", encoding="utf-8") as stream:
            stream.write(text)


def closed_creator_inventory(folder, expected, expected_modes, allow_runtime_caches=False):
    """Verify reviewed files and all directory entries; record only permitted caches."""
    resources, caches = artifact_inventory(checked_path(folder))
    if resources != expected or (caches and not allow_runtime_caches):
        raise ValueError("Closed recovered creator resource inventory differs")
    if {name: stat.S_IMODE((folder / name).stat().st_mode) for name in resources} != expected_modes:
        raise ValueError("Closed recovered creator resource modes differ")
    allowed_directories = set()
    for relative in (*expected, *caches):
        allowed_directories.update(parent.as_posix() for parent in Path(relative).parents if parent != Path("."))
    actual_directories = {path.relative_to(folder).as_posix() for path in folder.rglob("*") if path.is_dir()}
    if actual_directories != allowed_directories:
        raise ValueError("Unknown or missing recovered creator deliverable directory")
    return {name: {"sha256": value, "mode": stat.S_IMODE((folder / name).stat().st_mode)}
            for name, value in caches.items()}


def plan_creator(root, creator_id, package):
    """Attach a filtered new-freeze observation; never rewrite the evaluated Skill."""
    if creator_id not in RECOVERED_CREATORS:
        return None
    companion = json.loads(checked_bytes(root, CREATOR_COMPANION_PATH, CREATOR_COMPANION_SHA256))
    if set(companion["creators"]) != RECOVERED_CREATORS:
        raise ValueError("Exactly the four reviewed creator recovery freezes are required")
    for reference in (*companion["evidence_reviews"], companion["rematerialization"], companion["common_display_recovery"]):
        checked_bytes(root, reference["path"], reference["sha256"])
    entry = companion["creators"][creator_id]
    for reference in (entry["relay"], entry["format_observation"], entry["freeze_manifest"], *entry["consumer_assignments"]):
        checked_bytes(root, reference["path"], reference["sha256"])
    freeze = json.loads(source(root, entry["freeze_manifest"]["path"]).read_text())
    if (freeze["creator_id"] != creator_id or package.parent != root / "frozen/control-artifacts" / creator_id
            or package.name != Path(freeze["frozen_path"]).name
            or freeze["file_sha256"] != entry["frozen_resource_sha256"]
            or freeze["source_file_modes"] != entry["newly_observed_source_file_modes"]
            or file_hashes(checked_path(package)) != entry["frozen_resource_sha256"]
            or {name: stat.S_IMODE((package / name).stat().st_mode) for name in file_hashes(package)}
            != entry["newly_observed_source_file_modes"]):
        raise ValueError("New recovery freeze/resource identity differs")
    for reference in entry["consumer_assignments"]:
        assignment = json.loads(source(root, reference["path"]).read_text())
        if assignment["creator_id"] != creator_id or assignment["artifact_freeze_sha256"] != entry["freeze_manifest"]["sha256"]:
            raise ValueError("Reconstructed preparation does not bind the reviewed recovery freeze")
    rematerialization = json.loads(source(root, companion["rematerialization"]["path"]).read_text())
    selected_placement = [item for item in rematerialization["files"]
                          if item["destination_path"].startswith(f"trials/{creator_id}/")]
    canonical_relative = f"trials/{creator_id}/deliverables"
    canonical_files = {f"skills/{package.name}/{name}": value for name, value in entry["frozen_resource_sha256"].items()}
    canonical_modes = {f"skills/{package.name}/{name}": mode for name, mode in entry["newly_observed_source_file_modes"].items()}
    caches = closed_creator_inventory(source(root, canonical_relative), canonical_files, canonical_modes, True)
    closed_creator_inventory(package, entry["frozen_resource_sha256"], entry["newly_observed_source_file_modes"])
    note_relative = f"trials/{creator_id}/execution-note.md"
    if creator_id in COMMITTED_CREATOR_NOTES:
        if selected_placement:
            raise ValueError("Committed creator note must retain its reviewed original provenance")
        note_sha256, note_mode = COMMITTED_CREATOR_NOTES[creator_id], 0o644
        note_origin = {"source_commit": SOURCE_COMMIT, "corroborating_relay": entry["relay"]}
    else:
        placements = {item["destination_path"]: item for item in selected_placement}
        if len(placements) != len(selected_placement) or set(placements) != {
                note_relative, *(f"{canonical_relative}/{name}" for name in canonical_files)}:
            raise ValueError("The reviewed rematerialization must cover exactly the note and package")
        for name, value in canonical_files.items():
            placement = placements[f"{canonical_relative}/{name}"]
            if placement["sha256"] != value or int(placement["new_placement_mode"], 8) != canonical_modes[name]:
                raise ValueError("Canonical resource disagrees with reviewed rematerialization")
        note_placement = placements[note_relative]
        note_sha256, note_mode = note_placement["sha256"], int(note_placement["new_placement_mode"], 8)
        note_origin = {"rematerialization": companion["rematerialization"], "placement": note_placement}
    note = source(root, note_relative)
    if not note.is_file():
        raise ValueError("Recovered creator public note must be a regular file")
    checked_bytes(root, note_relative, note_sha256)
    if stat.S_IMODE(note.stat().st_mode) != note_mode:
        raise ValueError("Recovered creator public-note mode differs")
    selected_note = {"source": note_relative, "sha256": note_sha256,
                     "observed_copy_source_mode": note_mode, "identity_source": note_origin}
    candidate_files = [{**selected_note, "destination": "creator-reported-checks.md"}]
    for name, value in entry["frozen_resource_sha256"].items():
        candidate_files.append({"source": (package / name).relative_to(root).as_posix(),
                                "destination": f"package/{package.name}/{name}", "sha256": value,
                                "observed_copy_source_mode": entry["newly_observed_source_file_modes"][name]})
    # No whole review, other creator entry, schedule or consumer assignment body
    # enters the blind packet. The preserved relay and format observation contain
    # this candidate's public evidence, without model/effort mappings or grades.
    files = []
    for field, destination in (("relay", "source-relay.md"), ("format_observation", "format-observation.json")):
        reference = entry[field]
        files.append({"source": reference["path"], "destination": destination, "sha256": reference["sha256"],
                      "observed_copy_source_mode": stat.S_IMODE(source(root, reference["path"]).stat().st_mode)})
    provenance = {"source_companion": CREATOR_COMPANION_PATH, "source_companion_sha256": CREATOR_COMPANION_SHA256,
                  "observation_utc": companion["observation_utc"], "scope": companion["scope"],
                  "creator": entry, "evidence_reviews": companion["evidence_reviews"],
                  "rematerialization_source": companion["rematerialization"],
                  "this_creator_rematerialized_files": selected_placement,
                  "canonical_public_note": selected_note,
                  "canonical_deliverable_resource_sha256": canonical_files,
                  "canonical_deliverable_resource_modes": canonical_modes,
                  "excluded_canonical_runtime_caches": caches}
    return {"creator_id": creator_id, "frozen_relative": package.relative_to(root).as_posix(),
            "files": files, "candidate_files": candidate_files, "provenance": provenance}


def verify_creator_plan(root, plan):
    current = plan_creator(root, plan["creator_id"], source(root, plan["frozen_relative"]))
    if current != plan:
        raise ValueError("Recovered creator evidence changed after planning")


def write_creator(root, plan, destination, copy_file):
    checked_path(destination)
    if destination.exists() or destination.resolve() != destination or not destination.is_relative_to(root):
        raise ValueError("Preserve existing/partial creator recovery provenance")
    verify_creator_plan(root, plan)
    destination.mkdir(parents=True, exist_ok=False)
    copy_planned_files(root, plan["files"], destination, copy_file)
    with (destination / "creator-recovery-provenance.json").open("x", encoding="utf-8") as stream:
        json.dump(plan["provenance"], stream, indent=2)
        stream.write("\n")
    with (destination / "README.md").open("x", encoding="utf-8") as stream:
        stream.write("# Recovery provenance\n\n" + plan["provenance"]["creator"]["content_provenance"] + ".\n\n"
                     + plan["provenance"]["creator"]["historical_limits"] + "\n\n"
                     "This candidate's current canonical freeze and consumer preparation are new recovery observations. "
                     "The attached format observation is mechanical validation at recovery time, not semantic or business grading. "
                     "Original task criteria and evaluation rules are unchanged.\n")
    verify_creator_plan(root, plan)


def write_creator_candidate(root, plan, destination, copy_file):
    """Copy only the closed, reviewed candidate version and its public note."""
    checked_path(destination)
    if destination.exists() or destination.resolve() != destination or not destination.is_relative_to(root):
        raise ValueError("Preserve existing/partial recovered creator candidate")
    verify_creator_plan(root, plan)
    destination.mkdir(parents=True, exist_ok=False)
    copy_planned_files(root, plan["candidate_files"], destination, copy_file)
    # This performs a second complete source check before and after attachment,
    # preserving partial output if a canonical or selected file changed mid-copy.
    write_creator(root, plan, destination / "recovery-provenance", copy_file)
