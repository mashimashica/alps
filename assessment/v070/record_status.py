"""Record coordinator-confirmed execution status; never infer task success.

This assessment-only helper updates an existing explicit ledger. Timestamps
record this notification, not unobserved historical execution timing.
"""

import argparse
import csv
from datetime import datetime, timezone
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", help="Existing assessment-root TSV filename")
    parser.add_argument("ids", nargs="+")
    parser.add_argument("--status", required=True, help="Explicit coordinator observation; not a quality judgment")
    parser.add_argument("--agent")
    parser.add_argument("--event", choices=("start", "end"))
    args = parser.parse_args()
    if not re.fullmatch(r"[a-z0-9-]+\.tsv", args.ledger):
        raise SystemExit("Use an explicit root ledger filename")
    path = ROOT / args.ledger
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        fields = list(reader.fieldnames or [])
        rows = list(reader)
    key = fields[0]
    requested = set(args.ids)
    matches = [row for row in rows if row[key] in requested]
    if len(matches) != len(requested) or {row[key] for row in matches} != requested:
        raise SystemExit("Every requested ID must occur exactly once in the existing ledger")
    if "execution" not in fields or "agent" not in fields:
        raise SystemExit("Expected explicit execution and agent columns")
    event_field = None
    if args.event:
        event_field = "start_recorded_utc" if args.event == "start" else "end_recorded_utc"
        if event_field not in fields:
            fields.append(event_field)
        if any(row.get(event_field) for row in matches):
            raise SystemExit("Existing event timestamp must be preserved; use a distinct attempt for retries")
    now = datetime.now(timezone.utc).isoformat()
    for row in matches:
        row["execution"] = args.status
        if args.agent:
            row["agent"] = args.agent
        if event_field:
            row[event_field] = now
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"Recorded {len(matches)} explicit statuses in {args.ledger}; no success judgment made")


if __name__ == "__main__":
    main()
