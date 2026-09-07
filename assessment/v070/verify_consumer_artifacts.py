"""Compare supplied consumer resources with their recorded initial hashes."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main():
    results = []
    for path in sorted((ROOT / "consumer-assignments").glob("*.json")):
        assignment = json.loads(path.read_text())
        folder = ROOT / "consumers" / assignment["consumer_id"]
        changes = []
        permitted_state = []
        for relative, initial in assignment["copied_sha256"].items():
            current = folder / relative
            actual = hashlib.sha256(current.read_bytes()).hexdigest() if current.is_file() else None
            if actual != initial:
                if assignment["case"] == "S10" and relative == "input/state.json":
                    permitted_state.append(relative)
                else:
                    changes.append(relative)
        results.append({"consumer": assignment["consumer_id"], "unexpected_changes": changes, "state_changes_requiring_behavior_review": permitted_state})
    target = ROOT / "validation/consumer-resource-integrity.json"
    target.write_text(json.dumps({"scope": "Recorded original resources only; authorized state changes need separate behavioral review. Does not establish task completion.", "results": results}, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"assignments_checked": len(results), "unexpected_changed_files": sum(len(r["unexpected_changes"]) for r in results), "report": str(target)}))


if __name__ == "__main__":
    main()
