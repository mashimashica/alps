"""Preserve six completed H03 packages in a source-fidelity review packet.

Copies original content without experimental identity or consumer observations.
The coordinator confirms completion before running this bookkeeping operation.
"""

import csv
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent
ORDER = (4, 2, 6, 3, 1, 5)
CODES = ("F27", "F03", "F61", "F42", "F19", "F80")
target = ROOT / "fidelity-dev3"
if target.exists():
    raise SystemExit("Existing packet must be preserved")
with (ROOT / "dev3-list.tsv").open() as stream:
    rows = {row["trial_id"]: row for row in csv.DictReader(stream, delimiter="\t")}
for number in ORDER:
    trial_id = f"dev3-{number:03}"
    if rows[trial_id]["execution"] != "completed":
        raise SystemExit(f"Coordinator has not recorded completion: {trial_id}")
    if not (ROOT / "trials" / trial_id / "execution-note.md").is_file():
        raise SystemExit(f"Public handoff missing: {trial_id}")
target.mkdir()
mapping = {}
for code, number in zip(CODES, ORDER):
    trial_id = f"dev3-{number:03}"
    trial = ROOT / "trials" / trial_id
    shutil.copytree(trial / "output", target / code / "package",
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    assignment = json.loads((trial / "assignment.json").read_text())
    for relative, digest in assignment["input_sha256"].items():
        original = trial / relative
        if hashlib.sha256(original.read_bytes()).hexdigest() != digest:
            raise SystemExit(f"Original creator input changed: {trial_id}/{relative}")
        destination = target / code / "business-input" / Path(relative).relative_to("input")
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(original, destination)
    mapping[code] = trial_id
(ROOT / "blind-mappings" / "dev3-fidelity.json").write_text(json.dumps(mapping, indent=2) + "\n")
print("Prepared six source-fidelity packages without arm/model or consumer evidence")
