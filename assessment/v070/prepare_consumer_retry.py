"""Prepare the two independently reviewed lost H02 attempts exactly once.

Original partial observations remain untouched. New attempts start from the
original business fixture, not from partially changed state or an earlier answer.
This is bounded assessment recovery, not a product compatibility mechanism.
"""

import csv
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent
IDS = ("D2-U012", "D2-U014")


def main():
    if not (ROOT / "audits/consumer-loss-adjudication.md").is_file():
        raise SystemExit("Read independent invalidity adjudication before preparing retries")
    ledger = ROOT / "consumer-retry-list.tsv"
    if ledger.exists():
        raise SystemExit("Existing retry identities must be preserved")
    for original in IDS:
        if (ROOT / "consumers" / f"{original}-R1").exists():
            raise SystemExit("Retry folder already exists")
    rows = []
    for original in IDS:
        original_folder = ROOT / "consumers" / original
        metadata = json.loads((ROOT / "consumer-assignments" / f"{original}.json").read_text())
        for relative, digest in metadata["copied_sha256"].items():
            if relative.startswith("skill/") and hashlib.sha256(
                    (original_folder / relative).read_bytes()).hexdigest() != digest:
                raise SystemExit("Original frozen Skill changed")
        attempt = f"{original}-R1"
        folder = ROOT / "consumers" / attempt
        folder.mkdir()
        (folder / "work").mkdir()
        shutil.copytree(original_folder / "skill", folder / "skill",
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        source = ROOT / "development-consumer-cases" / metadata["case"] / metadata["variant"]
        if (source / "input").is_dir():
            source = source / "input"
        shutil.copytree(source, folder / "input")
        if metadata["case"] == "S10":
            shutil.copy2(ROOT / "cases/S10/release_tool.py", folder / "input/release_tool.py")
        request = folder / "input/request.md"
        body = request.read_text()
        for token, value in (("{{INPUT_DIR}}", folder / "input"),
                             ("{{ENVIRONMENT_PATH}}", folder / "input"),
                             ("{{STATE_PATH}}", folder / "input/state.json")):
            body = body.replace(token, str(value))
        if "{{" in body:
            raise SystemExit("Unresolved request token")
        request.write_text(body)
        prompt = (original_folder / "prompt.md").read_text().replace(str(original_folder), str(folder))
        (folder / "prompt.md").write_text(prompt)
        metadata.update(consumer_id=attempt, original_slot=original, attempt=1,
                        recovery_basis="audits/consumer-loss-adjudication.md",
                        copied_sha256={p.relative_to(folder).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                                       for part in ("skill", "input") for p in sorted((folder / part).rglob("*"))
                                       if p.is_file()},
                        prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest())
        (ROOT / "consumer-assignments" / f"{attempt}.json").write_text(json.dumps(metadata, indent=2) + "\n")
        rows.append([attempt, original, metadata["creator_id"], metadata["case"], metadata["variant"],
                     metadata["requested_model"], metadata["requested_effort"], "not started", ""])
    with ledger.open("x", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
        writer.writerow(["consumer_id", "original_slot", "creator_id", "case", "variant", "model", "effort",
                         "execution", "agent"])
        writer.writerows(rows)
    print("Prepared two distinct retries; originals retained, neither trial executed or selected")


if __name__ == "__main__":
    main()
