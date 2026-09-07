"""Create the H03 execution ledger from its twelve prepared assignments."""

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
rows = []
for number in range(1, 13):
    consumer_id = f"D3-U{number:03}"
    assignment = json.loads((ROOT / "consumer-assignments" / f"{consumer_id}.json").read_text())
    rows.append([consumer_id, assignment["creator_id"], assignment["case"],
                 assignment["variant"], assignment["requested_model"],
                 assignment["requested_effort"], "not started", ""])
with (ROOT / "dev3-consumer-list.tsv").open("x", newline="") as stream:
    writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
    writer.writerow(["consumer_id", "creator_id", "case", "variant", "model",
                     "effort", "execution", "agent"])
    writer.writerows(rows)
print("Recorded twelve unstarted H03 assignments")
