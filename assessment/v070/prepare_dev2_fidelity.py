"""Package all completed H02 creator outputs for source-fidelity review.

Do not expose authoring prompts, experimental identity, creator notes or
consumer observations. Preserve the original package text and raw brief.
"""

import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent
ORDER = (7, 2, 4, 5, 8, 1, 3, 6)
CODES = ("F27", "F03", "F61", "F42", "F19", "F80", "F36", "F55")
target = ROOT / "fidelity-dev2"
if target.exists():
    raise SystemExit("Existing fidelity packet must be preserved")
for number in ORDER:
    trial = ROOT / "trials" / f"dev2-{number:03}"
    if not (trial / "execution-note.md").is_file():
        raise SystemExit("Completion evidence missing; coordinator must confirm all creators ended")
target.mkdir()
mapping = {}
for code, number in zip(CODES, ORDER):
    trial_id = f"dev2-{number:03}"
    trial = ROOT / "trials" / trial_id
    shutil.copytree(trial / "output", target / code / "package",
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    shutil.copytree(trial / "input", target / code / "business-input")
    mapping[code] = trial_id
(ROOT / "blind-mappings" / "dev2-fidelity.json").write_text(json.dumps(mapping, indent=2) + "\n")
print("Prepared eight source-fidelity packages without arm/model, creator notes or consumer evidence")
