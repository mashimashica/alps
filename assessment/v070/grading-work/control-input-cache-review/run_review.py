"""Disposable assessment-helper checks; no business task is executed."""

import contextlib
import csv
import hashlib
import importlib
import io
import json
import os
from pathlib import Path
import py_compile
import shutil
import stat
import sys
import tempfile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
WORK = Path(__file__).resolve().parent
LOCAL = WORK / ".local"
LOCAL.mkdir(exist_ok=True)
RUN = Path(tempfile.mkdtemp(prefix="run-", dir=LOCAL))
RESULTS = []


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(folder):
    result = {}
    for path in sorted(folder.rglob("*")):
        mode = path.lstat().st_mode
        if stat.S_ISREG(mode):
            value = sha(path)
        elif stat.S_ISLNK(mode):
            value = str(path.readlink())
        else:
            value = None
        result[path.relative_to(folder).as_posix()] = [mode, value]
    return result


def passed(name, detail=None):
    RESULTS.append({"test": name, "result": "PASS", "detail": detail})


def rejected(name, function, folder, text=None):
    before = snapshot(folder)
    try:
        function()
    except ValueError as error:
        if text is not None:
            assert text in str(error), (name, str(error))
        assert snapshot(folder) == before, name + " changed its fixture"
        passed(name, str(error).replace(str(RUN), "<disposable>"))
    else:
        raise AssertionError(name + " was accepted")


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n")


def invoke(module, argument):
    original_argv = sys.argv
    sys.argv = [module.__name__ + ".py", argument]
    output = io.StringIO()
    try:
        with contextlib.redirect_stdout(output):
            module.main()
    finally:
        sys.argv = original_argv
    return output.getvalue()


HELPERS = ("prepare_control_consumers.py", "prepare_control_grading.py",
           "checkpoint.py", "control_ledger_state.py")
EVIDENCE = ("audits/control-061-input-cache-observation.md",
            "control-assignments/control-061.json", "trials/control-061/prompt.md",
            "trials/control-061/execution-note.md")
original_files = [ROOT / name for name in (*HELPERS, *EVIDENCE)]
original_files += sorted((ROOT / "trials/control-061/input").rglob("*"))
original_state = {str(path): [sha(path), stat.S_IMODE(path.stat().st_mode)]
                  for path in original_files if path.is_file()}
original_input_tree = snapshot(ROOT / "trials/control-061/input")
helper_copy = RUN / "helpers"
helper_copy.mkdir()
for name in HELPERS:
    shutil.copy2(ROOT / name, helper_copy / name)
sys.path.insert(0, str(helper_copy))
c = importlib.import_module("prepare_control_consumers")
g = importlib.import_module("prepare_control_grading")
checkpoint = importlib.import_module("checkpoint")
c.ROOT = RUN
assignment = json.loads((ROOT / "control-assignments/control-061.json").read_text())
expected = {name.removeprefix("input/"): digest
            for name, digest in assignment["input_sha256"].items()}
observed_cache = {"__pycache__/release_tool.cpython-312.pyc":
                  "817e07c25329c62c67ad09f7db52c4dde4222c6d3f42733d40a7d0228682b44b"}


def new_input(name):
    folder = RUN / "matrix" / name / "input"
    shutil.copytree(ROOT / "trials/control-061/input", folder)
    return folder


baseline = new_input("baseline")
shutil.copy2(ROOT / "trials/control-061/prompt.md", baseline.parent / "prompt.md")
before = snapshot(baseline.parent)
assert c.creator_input_caches(baseline, expected) == observed_cache
assert sha(baseline.parent / "prompt.md") == assignment["prompt_sha256"]
assert snapshot(baseline.parent) == before
passed("C061 supplied byte identities, prompt identity and sole cache hash", {
    "original_input_sha256": expected, "added_cache_sha256": observed_cache,
    "prompt_sha256": assignment["prompt_sha256"]})

no_cache = new_input("no-cache")
shutil.rmtree(no_cache / "__pycache__")
assert c.creator_input_caches(no_cache, expected) == {}
passed("Unchanged input without a cache remains accepted")

for name, action, message in (
    ("Changed supplied source", lambda p: (p / "release_tool.py").write_bytes(b"changed\n"), "Original creator input"),
    ("Missing supplied source", lambda p: (p / "release_tool.py").unlink(), "Original creator input"),
    ("Renamed supplied source", lambda p: (p / "release_tool.py").rename(p / "renamed.py"), "Original creator input"),
    ("Added ordinary file", lambda p: (p / "extra.md").write_text("extra\n"), "Unexpected added"),
    ("Added pyc outside __pycache__", lambda p: (p / "extra.pyc").write_bytes(b"cache"), "Unexpected added"),
    ("Added non-pyc inside __pycache__", lambda p: (p / "__pycache__/extra.txt").write_text("extra\n"), "Unexpected added"),
    ("Added uppercase PYC", lambda p: (p / "__pycache__/extra.PYC").write_bytes(b"cache"), "Unexpected added"),
):
    folder = new_input(name.lower().replace(" ", "-"))
    action(folder)
    rejected(name, lambda: c.creator_input_caches(folder, expected), folder.parent, message)

folder = new_input("nested-pyc")
(folder / "__pycache__/nested").mkdir()
(folder / "__pycache__/nested/extra.pyc").write_bytes(b"cache")
rejected("Pyc not directly inside __pycache__", lambda: c.creator_input_caches(folder, expected), folder.parent, "Unexpected added")

folder = new_input("original-cache-mutated")
expected_with_cache = expected | observed_cache
(folder / next(iter(observed_cache))).write_bytes(b"changed")
rejected("Previously supplied cache bytes are still pinned", lambda: c.creator_input_caches(folder, expected_with_cache), folder.parent, "Original creator input")

for label, relative, dangling in (
    ("Original source symlink", "release_tool.py", False),
    ("Cache file symlink", next(iter(observed_cache)), False),
    ("Dangling cache symlink", next(iter(observed_cache)), True),
):
    folder = new_input(label.lower().replace(" ", "-"))
    path = folder / relative
    link_target = folder.parent / "link-target"
    if not dangling:
        shutil.copy2(path, link_target)
    path.unlink()
    path.symlink_to(link_target)
    rejected(label, lambda: c.creator_input_caches(folder, expected), folder.parent, "Unexpected symlink")

folder = new_input("cache-directory-symlink")
(folder / "__pycache__").rename(folder.parent / "cache-target")
(folder / "__pycache__").symlink_to(folder.parent / "cache-target", target_is_directory=True)
rejected("Cache directory symlink", lambda: c.creator_input_caches(folder, expected), folder.parent, "Unexpected symlink")

folder = new_input("ancestor-symlink")
alias = folder.parent / "alias"
alias.symlink_to(folder, target_is_directory=True)
rejected("Input directory symlink", lambda: c.creator_input_caches(alias, expected), folder.parent, "Unexpected symlink")

folder = new_input("fifo")
os.mkfifo(folder / "__pycache__/extra.pyc")
rejected("Cache-named FIFO", lambda: c.creator_input_caches(folder, expected), folder.parent, "Unsupported filesystem entry")

folder = new_input("classification-boundaries")
(folder / "__pycache__/opaque.pyc").write_bytes(b"opaque bytes, not validated bytecode")
(folder / "empty-added-directory").mkdir()
assert c.creator_input_caches(folder, expected) == observed_cache | {
    "__pycache__/opaque.pyc": sha(folder / "__pycache__/opaque.pyc")}
passed("Classification limits observed", "Regular files are classified by location/suffix, not bytecode content; empty directories are not inventoried")

# Entirely synthetic packaging inputs; constants below refer only to this fixture.
# The original release tool is copied as data and is never imported or executed.
fixture = RUN / "integration" / "assessment"
fixture.mkdir(parents=True)
c.ROOT = g.ROOT = checkpoint.ROOT = fixture
creator = fixture / "trials/control-061"
shutil.copytree(baseline, creator / "input")
shutil.copy2(baseline.parent / "prompt.md", creator / "prompt.md")
(creator / "execution-note.md").write_text("Synthetic packaging fixture only; no creator/business task was run.\n")
write_json(fixture / "control-assignments/control-061.json", assignment)
skill = creator / "deliverables/skills/fixture-skill"
skill.mkdir(parents=True)
(skill / "SKILL.md").write_text("---\nname: fixture-skill\ndescription: Synthetic packaging fixture.\n---\nNo business execution.\n")
(skill / "probe.py").write_text("VALUE = 7\n")
(skill / "probe.py").chmod(0o755)
py_compile.compile(str(skill / "probe.py"), doraise=True)
skill_before = snapshot(skill)
input_before = snapshot(creator / "input")

bank = fixture / "frozen/main-cases/S10"
bank.mkdir(parents=True)
for relative in expected:
    shutil.copy2(baseline / relative, bank / relative)
write_json(fixture / "main-case-hashes.json", {"S10/" + k: v for k, v in expected.items()})
for variant in ("ordinary", "challenging"):
    source = fixture / "control-consumer-cases/S10" / variant / "input"
    source.mkdir(parents=True)
    (source / "request.md").write_text("Synthetic packaging fixture only. Path: {{INPUT_DIR}}\n")
    (source / "state.json").write_text('{"synthetic_packaging_only": true}\n')
write_json(fixture / "control-consumer-case-hashes.json", c.file_hashes(fixture / "control-consumer-cases"))
c.CASE_BANK_SHA256 = sha(fixture / "control-consumer-case-hashes.json")
aid = fixture / "frozen/skill-creator"
(aid / "assets").mkdir(parents=True)
(aid / "SKILL.md").write_text("Synthetic aid placeholder; not a task instruction.\n")
(aid / "assets/skill-creator.png").write_bytes(b"synthetic-display-placeholder")
(aid / "assets/skill-creator-small.svg").write_text("synthetic-display-placeholder\n")
frozen_identity = {"frozen/skill-creator/SKILL.md": sha(aid / "SKILL.md")}
frozen_identity.update({"frozen/main-cases/S10/" + k: v for k, v in expected.items()})
(fixture / "frozen-hashes.sha256").write_text("".join(f"{v}  {k}\n" for k, v in frozen_identity.items()))


def write_rows(path, rows):
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


schedule = [{"trial_id": f"control-{n:03}", "stage": "control", "case": "S10", "arm": "C",
             "repetition": "1", "model": assignment["requested_model"],
             "effort": assignment["requested_effort"]} for n in range(1, 73)]
write_rows(fixture / "control-schedule.tsv", schedule)
c.SCHEDULE_SHA256 = sha(fixture / "control-schedule.tsv")
(fixture / "control-schedule-sha256.txt").write_text(c.SCHEDULE_SHA256 + "\n")
write_rows(fixture / "control-list.tsv", [row | {"execution": "completed" if row["trial_id"] == "control-061" else "pending"} for row in schedule])

(creator / "input/forbidden-extra.md").write_text("Synthetic refusal case.\n")
rejected("Consumer preflight rejects non-cache input before writes", lambda: invoke(c, "control-061"), fixture, "Unexpected added")
assert not (fixture / "frozen/control-artifacts").exists()
assert not (fixture / "consumers").exists()
(creator / "input/forbidden-extra.md").unlink()
consumer_output = invoke(c, "control-061")
freeze_path = fixture / "control-artifact-freezes/control-061.json"
freeze = json.loads(freeze_path.read_text())
assert freeze["creator_input_added_runtime_cache_sha256"] == observed_cache
assert freeze["excluded_runtime_cache_sha256"] == c.artifact_inventory(skill)[1]
assert snapshot(skill) == skill_before
assert snapshot(creator / "input") == input_before
for use_id in ("C-U121", "C-U122"):
    folder = fixture / "consumers" / use_id
    metadata = json.loads((fixture / "consumer-assignments" / (use_id + ".json")).read_text())
    assert metadata["artifact_freeze_sha256"] == sha(freeze_path)
    assert c.file_hashes(folder / "skill/fixture-skill") == freeze["file_sha256"]
    assert sha(folder / "input/release_tool.py") == expected["release_tool.py"]
    assert not any("__pycache__" in p.parts for p in (folder / "input").rglob("*"))
    assert not list((folder / "skill").rglob("*.pyc"))
    assert stat.S_IMODE((folder / "skill/fixture-skill/probe.py").stat().st_mode) == 0o755
    (folder / "answer.md").write_text("Synthetic packaging placeholder; no consumer was executed.\n")
    (folder / "execution-note.md").write_text("Synthetic packaging placeholder; no consumer was executed.\n")
passed("Synthetic consumer preparation preserves sources and modes, records cache hashes, binds manifest and excludes caches", consumer_output.strip())
rejected("Existing consumer preparation is preserved", lambda: invoke(c, "control-061"), fixture, "already exists")

allocation = {"families": {"S10": [{"packet": "S10-P99", "creators": ["control-061"]}]}}
write_json(fixture / "control-grading-allocation.json", allocation)
g.ALLOCATION_SHA256 = sha(fixture / "control-grading-allocation.json")
g.CASE_MANIFEST_SHA256 = c.CASE_BANK_SHA256
g.CREATOR_SCHEDULE_SHA256 = c.SCHEDULE_SHA256
consumer_schedule = [{"consumer_id": name, "model": "gpt-5.6-sol", "effort": "high"}
                     for name in ("C-U121", "C-U122")]
write_rows(fixture / "control-consumer-schedule.tsv", consumer_schedule)
g.CONSUMER_SCHEDULE_SHA256 = sha(fixture / "control-consumer-schedule.tsv")
(fixture / "control-consumer-schedule-sha256.txt").write_text(g.CONSUMER_SCHEDULE_SHA256 + "\n")
write_rows(fixture / "control-consumer-list.tsv", [row | {"execution": "completed"} for row in consumer_schedule])
(fixture / "control-oracles").mkdir()
(fixture / "control-oracles/S10.md").write_text("Synthetic packaging oracle placeholder; no grading criterion.\n")
write_json(fixture / "control-oracle-hashes.json", {"S10.md": sha(fixture / "control-oracles/S10.md")})
(fixture / "grading-guidance.md").write_text("Synthetic packaging fixture only.\n")
unchanged_freeze_bytes = freeze_path.read_bytes()
tampered = json.loads(unchanged_freeze_bytes)
tampered["creator_input_added_runtime_cache_sha256"] = {next(iter(observed_cache)): "0" * 64}
write_json(freeze_path, tampered)
rejected("Blind preparation rejects tampering with cache evidence bound by assignment", lambda: invoke(g, "S10-P99"), fixture, "Application identity differs")
assert not (fixture / "blind-business").exists()
freeze_path.write_bytes(unchanged_freeze_bytes)
invoke(g, "S10-P99")
packet = fixture / "blind-business/S10-P99"
assert g.inventory(packet / "original-creator-input") == expected
assert g.inventory(packet / "R17/package/fixture-skill") == freeze["file_sha256"]
assert not list(packet.rglob("*.pyc"))
assert stat.S_IMODE((packet / "R17/package/fixture-skill/probe.py").stat().st_mode) == 0o755
assert not (packet / "control-artifact-freezes").exists()
provenance = json.loads((fixture / "blind-mappings/control-S10-P99-provenance.json").read_text())
assert provenance["file_sha256"] == g.inventory(packet)
assert provenance["excluded_source_runtime_cache_sha256"]["trials/control-061/deliverables"]
passed("Synthetic blind preparation accepts unchanged manifest and preserves package/source bytes and modes without cache payloads")

output = io.StringIO()
with contextlib.redirect_stdout(output):
    checkpoint.export()
exported = json.loads(output.getvalue())
export_map = {entry["path"]: entry for entry in exported}
durable_manifest = export_map["assessment/v070/control-artifact-freezes/control-061.json"]["content"]
assert json.loads(durable_manifest)["creator_input_added_runtime_cache_sha256"] == observed_cache
assert not any("__pycache__" in Path(path).parts for path in export_map)
assert export_map["assessment/v070/trials/control-061/input/release_tool.py"]["content"].encode() == (baseline / "release_tool.py").read_bytes()
assert export_map["assessment/v070/frozen/control-artifacts/control-061/fixture-skill/probe.py"]["mode"] == "100755"
assert snapshot(skill) == skill_before
assert snapshot(creator / "input") == input_before
passed("Checkpoint export keeps external cache hashes and original source while omitting raw caches", {"exported_entries": len(exported)})

after_state = {str(path): [sha(path), stat.S_IMODE(path.stat().st_mode)]
               for path in original_files if path.is_file()}
assert after_state == original_state
assert snapshot(ROOT / "trials/control-061/input") == original_input_tree
passed("Read original evidence and helper bytes/modes remain unchanged")
summary = {"python": sys.version.split()[0], "tests_passed": len(RESULTS),
           "disposable_root": str(RUN), "results": RESULTS,
           "limits": "Synthetic S10 packaging fixture with substituted in-memory identity constants and one creator/two consumers. No real schedule/allocation/bank, live preparation, business task, Skill quality, prior validator/refusal, or remote save was exercised. Cache format/origin, modes of original creator inputs, empty directories, and concurrent changes are not attested."}
destination = WORK / "results.json"
with destination.open("x") as stream:
    json.dump(summary, stream, indent=2)
    stream.write("\n")
print(json.dumps({"tests_passed": len(RESULTS), "results": str(destination), "disposable_root": str(RUN)}))
