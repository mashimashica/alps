"""Package explicit completed cases for independent blinded grading."""

import argparse
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ORDER = {"S01": (4, 1, 3, 2), "S05": (6, 8, 5, 7), "S10": (11, 9, 12, 10)}
CODES = ("K23", "K51", "K14", "K66")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", choices=ORDER)
    args = parser.parse_args()
    target = ROOT / "blind" / args.case
    target.mkdir(parents=True, exist_ok=False)
    shutil.copy2(ROOT / "cases" / args.case / "brief.md", target / "business-brief.md")
    shutil.copy2(ROOT / "oracles" / f"{args.case}.md", target / "business-oracle.md")
    shutil.copy2(ROOT / "grading-guidance.md", target / "grading-guidance.md")
    mapping = {}
    for code, number in zip(CODES, ORDER[args.case]):
        creator_id = f"cal-{number:03}"
        candidate = target / code
        shutil.copytree(ROOT / "trials" / creator_id / "output", candidate / "package", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        consumer_ids = []
        for index, variant in enumerate(("ordinary", "challenging")):
            use_id = f"U{2*(number-1)+index+1:03}"
            source = ROOT / "consumers" / use_id
            destination = candidate / variant
            destination.mkdir()
            for name in ("answer.md", "execution-note.md"):
                shutil.copy2(source / name, destination / name)
            shutil.copytree(source / "input", destination / "final-input-state")
            if any((source / "work").iterdir()):
                shutil.copytree(source / "work", destination / "work-evidence", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            consumer_ids.append(use_id)
        mapping[code] = {"creator": creator_id, "consumers": consumer_ids}
    (ROOT / "blind-mappings").mkdir(exist_ok=True)
    (ROOT / "blind-mappings" / f"{args.case}.json").write_text(json.dumps(mapping, indent=2)+"\n", encoding="utf-8")
    print(f"Prepared four blinded {args.case} artifacts and eight completed consumer applications")


if __name__ == "__main__":
    main()
