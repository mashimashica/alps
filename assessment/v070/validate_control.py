"""Record pinned physical-format checks for explicit completed C creators.

No heading, ALPS vocabulary, semantic or effectiveness test is added.
Reports are exclusive per creator and never replace an earlier observation.
"""

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

from prepare_control_consumers import completed_creators, refuse_existing, skill_path, write_json

ROOT = Path(__file__).resolve().parent
VALIDATOR = ROOT.parent / "validation-env/bin/skills-ref"
PACKAGES = ROOT.parent / "validation-env/lib/python3.12/site-packages"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("creator_ids", nargs="+")
    args = parser.parse_args()
    completed_creators(args.creator_ids)
    plans = []
    for creator_id in args.creator_ids:
        target = skill_path(creator_id)
        report = ROOT / "validation/control-format" / f"{creator_id}.json"
        refuse_existing(report)
        plans.append((creator_id, target, report))
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(PACKAGES)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    for creator_id, target, report in plans:
        command = [sys.executable, str(VALIDATOR), "validate", str(target)]
        result = subprocess.run(command, capture_output=True, text=True, env=environment, timeout=30)
        write_json(report, {"scope": "Physical Agent Skill format only; not semantics or work effectiveness",
                            "validator_source": "agentskills/agentskills@f130f348f502d9804278a617f86929846896d2e9 skills-ref",
                            "trial": creator_id, "command": command, "exit_code": result.returncode,
                            "stdout": result.stdout, "stderr": result.stderr})
        print(json.dumps({"trial": creator_id, "exit_code": result.returncode, "report": str(report)}))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as error:
        raise SystemExit(str(error)) from error
