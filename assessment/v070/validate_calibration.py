"""Run the pinned physical-format validator on an explicitly completed trial group."""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VALIDATOR = ROOT.parent / "validation-env/bin/skills-ref"
PACKAGES = ROOT.parent / "validation-env/lib/python3.12/site-packages"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prefix", choices=("cal", "dev1"), default="cal")
    args = parser.parse_args()
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(PACKAGES)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    results = []
    for trial in sorted((ROOT / "trials").glob(args.prefix + "-*")):
        targets = list((trial / "output").glob("*/SKILL.md"))
        if len(targets) != 1:
            raise SystemExit(f"Exactly one completed artifact expected for {trial.name}")
        command = [sys.executable, str(VALIDATOR), "validate", str(targets[0].parent)]
        completed = subprocess.run(command, capture_output=True, text=True, env=environment, timeout=30)
        results.append({"trial": trial.name, "command": command, "exit_code": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr})
    report = "calibration-format.json" if args.prefix == "cal" else "development-1-format.json"
    target = ROOT / "validation" / report
    target.write_text(json.dumps({"scope": "Physical Agent Skill format only; not semantics or work effectiveness", "validator_source": "agentskills/agentskills@f130f348f502d9804278a617f86929846896d2e9 skills-ref", "results": results}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"checked": len(results), "passed": sum(r["exit_code"] == 0 for r in results), "report": str(target)}))


if __name__ == "__main__":
    main()
