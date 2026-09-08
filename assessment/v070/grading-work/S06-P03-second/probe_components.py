#!/usr/bin/env python3.12
"""Independent component probes. Never executes a consumer or an original state."""
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
PACKET = ROOT.parents[1] / "blind-business" / "S06-P03"
results = []

WRAPPER = '''#!/usr/bin/env python3.12
import json
from pathlib import Path
import subprocess
import sys
root = Path(__file__).resolve().parent
args = sys.argv[1:]
p = subprocess.run([sys.executable, str(root / "ledger_api.py"), *args], capture_output=True, text=True)
is_page = len(args) >= 3 and args[2] == "page"
drop = is_page and p.returncode == 0 and (root / "drop-first-page-response.enabled").exists() and not (root / "response-dropped.marker").exists()
if drop:
    (root / "response-dropped.marker").write_text("First successful page response deliberately withheld; source call was counted.\\n")
with (root / "api-trace.jsonl").open("a") as f:
    f.write(json.dumps(dict(argv=args, returncode=p.returncode, original_stdout=p.stdout, original_stderr=p.stderr, stdout_withheld=drop)) + "\\n")
sys.stdout.write("" if drop else p.stdout)
sys.stderr.write(p.stderr)
sys.exit(p.returncode)
'''

def run(label, argv, cwd):
    p = subprocess.run([str(x) for x in argv], cwd=cwd, capture_output=True, text=True)
    observation = dict(label=label, argv=[str(x) for x in argv], cwd=str(cwd), exit_code=p.returncode, stdout=p.stdout, stderr=p.stderr)
    results.append(observation)
    (ROOT / "commands-results.json").write_text(json.dumps(results, indent=2) + "\n")
    return observation

def checkpoint(path):
    if path.suffix == ".sqlite":
        db = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)
        try:
            return {"state": json.loads(db.execute("SELECT payload FROM state WHERE id=1").fetchone()[0]), "entries": list(db.execute("SELECT * FROM entries ORDER BY rowid")), "pages": list(db.execute("SELECT * FROM pages ORDER BY rowid")), "vendors": list(db.execute("SELECT * FROM vendors ORDER BY vendor_id"))}
        finally:
            db.close()
    return json.loads(path.read_text())

def setup(candidate, scenario):
    folder = ROOT / ("disposable-" + candidate + "-" + scenario)
    folder.mkdir()
    (folder / "DISPOSABLE-PROBE.txt").write_text("Grader-created isolated component probe; not recorded consumer evidence and not an original API state.\n")
    shutil.copytree(PACKET / candidate / "package", folder / "unchanged-package-copy")
    shutil.copy2(PACKET / "original-creator-input" / "ledger_api.py", folder / "ledger_api.py")
    shutil.copy2(PACKET / "original-creator-input" / "fixture.json", folder / "fixture.json")
    (folder / "recording_api.py").write_text(WRAPPER)
    if scenario == "counted-response-loss":
        (folder / "drop-first-page-response.enabled").write_text("Drop stdout for first successful page only, preserving exit status.\n")
    copied = next((folder / "unchanged-package-copy").iterdir())
    helper = copied / "scripts" / ("reimbursement_rollup.py" if candidate == "R44" else "rollup.py")
    source = folder / "disposable-source.sqlite"
    cp = folder / ("disposable-checkpoint.sqlite" if candidate == "R28" else "disposable-checkpoint.json")
    source_flag = {"R17": "--state", "R28": "--source", "R44": "--source-state", "R63": "--state"}[candidate]
    command = [sys.executable, helper, "--api", folder / "recording_api.py", source_flag, source, "--checkpoint", cp, "--start", "2026-02-01", "--end", "2026-02-15"]
    api_command = [sys.executable, folder / "recording_api.py", "--state", source]
    run(candidate + "/" + scenario + "/setup-init", [*api_command, "init", "--fixture", folder / "fixture.json"], folder)
    return folder, cp, command, api_command

summary = {}
for candidate in ("R17", "R28", "R44", "R63"):
    candidate_result = {}
    folder, cp, command, api_cmd = setup(candidate, "clean-continuation")
    steps = []
    for tranche in (1, 2, 3):
        if tranche != 1:
            run(f"{candidate}/clean/test-operator-grant-{tranche}", [*api_cmd, "grant-tranche"], folder)
        result = run(f"{candidate}/clean/tranche-{tranche}", command, folder)
        cp_data = checkpoint(cp)
        (folder / f"checkpoint-after-tranche-{tranche}.json").write_text(json.dumps(cp_data, indent=2) + "\n")
        quota = run(f"{candidate}/clean/describe-after-{tranche}", [*api_cmd, "describe"], folder)
        steps.append(dict(exit_code=result["exit_code"], output=json.loads(result["stdout"]), quota=json.loads(quota["stdout"])))
        if tranche == 1:
            run(f"{candidate}/clean/exhausted-repeat", command, folder)
    run(f"{candidate}/clean/final-repeat", command, folder)
    candidate_result["clean"] = steps
    folder, cp, command, api_cmd = setup(candidate, "counted-response-loss")
    loss_steps = []
    for name in ("first-call-output-withheld", "retry-same-checkpoint-with-remaining-quota"):
        result = run(f"{candidate}/loss/{name}", command, folder)
        cp_data = checkpoint(cp)
        (folder / f"checkpoint-{name}.json").write_text(json.dumps(cp_data, indent=2) + "\n")
        quota = run(f"{candidate}/loss/describe-after-{name}", [*api_cmd, "describe"], folder)
        loss_steps.append(dict(exit_code=result["exit_code"], output=json.loads(result["stdout"]), checkpoint=cp_data, quota=json.loads(quota["stdout"])))
    candidate_result["counted_response_loss"] = loss_steps
    summary[candidate] = candidate_result

(ROOT / "probe-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
# All helper/API subprocesses and checkpoint read connections are closed here.
database_manifest = []
for path in sorted(ROOT.glob("disposable-*/*.sqlite")):
    db = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)
    try:
        db.execute("BEGIN")
        native = "\n".join(db.iterdump()) + "\n"
    finally:
        db.rollback()
        db.close()
    native_path = path.with_suffix(path.suffix + ".native.sql")
    native_path.write_text(native)
    database_manifest.append(dict(path=str(path), binary_sha256=hashlib.sha256(path.read_bytes()).hexdigest(), native_sql=str(native_path), native_sql_sha256=hashlib.sha256(native_path.read_bytes()).hexdigest()))
(ROOT / "database-manifest.json").write_text(json.dumps(database_manifest, indent=2) + "\n")
(ROOT / "DATABASE-WRITES-FINISHED.txt").write_text("All component probe processes have exited. All SQLite connections are closed. No further writes are planned. Original packet files and original API states were never modified or executed.\n")
print(json.dumps({"status":"completed", "command_observations":len(results), "preserved_sqlite_files":len(database_manifest), "summary":str(ROOT / "probe-summary.json")}, sort_keys=True))
