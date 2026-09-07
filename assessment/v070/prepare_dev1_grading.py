"""Copy completed development artifacts into arm/model-blinded review packets.

This is evidence packaging, not an ALPS validator or a success classifier.
Original evaluated packages and observations are retained unchanged.
"""

import argparse
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent
ORDER = {1: {"S10": (3, 1, 4, 2), "S08": (6, 5), "S05": (8, 7)},
         2: {"S05": (5, 1, 6, 2), "S10": (7, 3, 8, 4)},
         3: {"S05": (4, 3), "S10": (5, 1, 6, 2)}}
CODES = ("R17", "R63", "R28", "R44")
IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc")

BOUNDARIES = """# Judgment boundaries

Judge every consumer application as adequate, bounded deficiency, material
failure, or unconfirmed, using the raw request and applicable business evidence.
These labels describe this experiment, not a required Process record. Requested
task adequacy, business Outcome achievement, and the generated package's quality
are different judgments. A consumer can compensate for a defective instruction
and still deliver adequate work; identify that correction separately. An initially
unmet condition may justify a bounded conclusion, but a preventable self-created
blockage is not automatically appropriate handling.

Count distinct evidenced corrections to defective or unusable instructions,
not ordinary interpretation or necessary business checks. Public execution notes
are agent reports, not attested complete transcripts. Do not infer private effort
or unrecorded operations. Flag incomplete or ambiguous evidence explicitly.

The package and public evidence copies are unchanged. Paths in those files may
identify trial workspaces but do not supply experimental arms or model settings.
Treat such paths as evidence; do not follow them to other assessment folders.
Original-consumer-inputs preserve the original fixtures; final-input-state
preserves the state after use. For booking, committed-state contains consistent
native initial/final SQL snapshots, not byte-identical SQLite files. Do not use
the live original states. Component probes, if needed, must use fresh disposable
copies or new temporary databases. Keep their findings distinct from actual
consumer observations. Do not repair a candidate or impose a preferred prose.
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", choices=("S05", "S08", "S10"))
    parser.add_argument("--round", type=int, choices=(1, 2, 3), default=1)
    args = parser.parse_args()
    if args.case not in ORDER[args.round]:
        raise SystemExit("No preregistered creator cells for this round and family")
    order = ORDER[args.round][args.case]
    selection_path = ROOT / "consumer-selected-attempts.json"
    selected = json.loads(selection_path.read_text()) if selection_path.exists() else {}
    stage = f"dev{args.round}"
    target = ROOT / f"blind-{stage}" / args.case
    if target.exists():
        raise SystemExit("Packet already exists; preserve it")
    for number in order:
        for index in range(2):
            use_id = f"D{args.round}-U{2 * (number - 1) + index + 1:03}"
            attempt_id = selected.get(use_id, use_id)
            for name in ("answer.md", "execution-note.md"):
                if not (ROOT / "consumers" / attempt_id / name).is_file():
                    raise SystemExit(f"Completed evidence missing: {attempt_id}/{name}")
            if args.case == "S08" and not (ROOT / "state-snapshots" / use_id / "final.sql").is_file():
                raise SystemExit(f"Final committed state not yet preserved: {use_id}")
    target.mkdir(parents=True)
    first_input = ROOT / "trials" / f"{stage}-{order[0]:03}" / "input"
    shutil.copytree(first_input, target / "original-creator-input", ignore=IGNORE)
    shutil.copy2(ROOT / "development-oracles" / f"{args.case}.md", target / "business-oracle.md")
    shutil.copy2(ROOT / "grading-guidance.md", target / "grading-guidance.md")
    (target / "judgment-boundaries.md").write_text(BOUNDARIES, encoding="utf-8")
    shutil.copytree(ROOT / "development-consumer-cases" / args.case,
                    target / "original-consumer-inputs", ignore=IGNORE)
    mapping = {}
    for code, number in zip(CODES, order):
        creator_id = f"{stage}-{number:03}"
        candidate = target / code
        shutil.copytree(ROOT / "trials" / creator_id / "output", candidate / "package", ignore=IGNORE)
        consumers = []
        for index, variant in enumerate(("ordinary", "challenging")):
            use_id = f"D{args.round}-U{2 * (number - 1) + index + 1:03}"
            attempt_id = selected.get(use_id, use_id)
            source = ROOT / "consumers" / attempt_id
            dest = candidate / variant
            dest.mkdir()
            for name in ("answer.md", "execution-note.md"):
                shutil.copy2(source / name, dest / name)
            shutil.copytree(source / "input", dest / "final-input-state", ignore=IGNORE)
            if any((source / "work").iterdir()):
                shutil.copytree(source / "work", dest / "work-evidence", ignore=IGNORE)
            if attempt_id != use_id:
                if attempt_id != f"{use_id}-R1":
                    raise SystemExit("Only the separately adjudicated first retry is supported")
                shutil.copytree(ROOT / "consumers" / use_id, dest / "interrupted-original", ignore=IGNORE)
                shutil.copy2(ROOT / "audits/consumer-loss-adjudication.md", dest / "observation-validity.md")
                (dest / "attempt-selection.md").write_text(
                    f"Original slot {use_id} was unfinished after recorded runtime loss. "
                    f"The complete answer, note and final state above are from {attempt_id}, "
                    "the single permitted retry and first valid attempt. Judge that completed "
                    "application. The interrupted original is separate partial evidence, not "
                    "a second application in the denominator or an alternative result to select.\n")
            if args.case == "S08":
                shutil.copytree(ROOT / "state-snapshots" / use_id, dest / "committed-state")
            consumers.append(attempt_id)
        mapping[code] = {"creator": creator_id, "consumers": consumers}
    (ROOT / "blind-mappings").mkdir(exist_ok=True)
    (ROOT / "blind-mappings" / f"{stage}-{args.case}.json").write_text(
        json.dumps(mapping, indent=2) + "\n", encoding="utf-8")
    print(f"Prepared {len(mapping)} anonymized packages with two applications each: {args.case}")


if __name__ == "__main__":
    main()
