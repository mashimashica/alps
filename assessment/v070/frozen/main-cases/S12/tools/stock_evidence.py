#!/usr/bin/env python3
"""Read-only, exact local matching of manifest and count evidence."""

import argparse
import csv
import json
import re
import sys
from pathlib import Path

TOOL = "stock-evidence"
VERSION = "2.0.0"
KEY_FIELDS = ("site_id", "shipment_id", "sku", "lot_id")
QUANTITY = re.compile(r"[+-]?(?:0|[1-9][0-9]{0,8})(?:\.[0-9]{1,3})?\Z")


def quantity_units(value):
    value = value.strip()
    if not QUANTITY.fullmatch(value):
        raise ValueError("quantity must be a base-10 decimal with <=9 whole and <=3 fractional digits")
    sign = -1 if value.startswith("-") else 1
    whole, _, fraction = value.lstrip("+-").partition(".")
    return sign * (int(whole) * 1000 + int(fraction.ljust(3, "0")))


def decimal_text(units):
    whole, fraction = divmod(abs(units), 1000)
    result = str(whole)
    if fraction:
        result += "." + f"{fraction:03d}".rstrip("0")
    return ("-" if units < 0 else "") + result


def read_rows(path, fields, row_id):
    seen = set()
    rows = []
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, strict=True)
        headers = reader.fieldnames
        if not headers or any(not name.strip() for name in headers) or len(headers) != len(set(headers)):
            raise ValueError(f"{path}: missing, empty, or duplicate header")
        missing = set(fields) - set(headers)
        if missing:
            raise ValueError(f"{path}: missing required columns: {', '.join(sorted(missing))}")
        for row in reader:
            location = f"{path}:{reader.line_num}"
            if None in row:
                raise ValueError(f"{location}: extra unnamed cell")
            for field in fields:
                if row[field] is None or not row[field].strip():
                    raise ValueError(f"{location}: missing {field}")
                row[field] = row[field].strip()
            if row[row_id] in seen:
                raise ValueError(f"{location}: duplicate {row_id}: {row[row_id]}")
            seen.add(row[row_id])
            row["_location"] = location
            rows.append(row)
    return rows


def compare(manifest_path, events_path):
    manifest = read_rows(manifest_path, ("manifest_line_id", *KEY_FIELDS, "expected_qty"), "manifest_line_id")
    events = read_rows(events_path, ("event_id", *KEY_FIELDS, "quantity", "condition", "state"), "event_id")
    grouped = {}

    def group_for(row):
        key = tuple(row[field].upper() for field in KEY_FIELDS)
        if key not in grouped:
            grouped[key] = {
                "manifest_units": 0, "good_units": 0, "damaged_units": 0,
                "manifest_line_ids": [], "posted_event_ids": [], "pending_event_ids": [],
            }
        return grouped[key]

    for row in manifest:
        try:
            units = quantity_units(row["expected_qty"])
        except ValueError as error:
            raise ValueError(f"{row['_location']}: expected_qty: {error}") from error
        if units < 0:
            raise ValueError(f"{row['_location']}: expected_qty cannot be negative")
        group = group_for(row)
        group["manifest_units"] += units
        group["manifest_line_ids"].append(row["manifest_line_id"])

    for row in events:
        try:
            units = quantity_units(row["quantity"])
        except ValueError as error:
            raise ValueError(f"{row['_location']}: quantity: {error}") from error
        condition, state = row["condition"].lower(), row["state"].lower()
        if condition not in ("good", "damaged") or state not in ("posted", "pending"):
            raise ValueError(f"{row['_location']}: unsupported condition or state")
        group = group_for(row)
        if state == "posted":
            group[condition + "_units"] += units
            group["posted_event_ids"].append(row["event_id"])
        else:
            group["pending_event_ids"].append(row["event_id"])

    results = []
    for key, group in sorted(grouped.items()):
        has_manifest = bool(group["manifest_line_ids"])
        has_posted = bool(group["posted_event_ids"])
        flags = []
        if not has_manifest:
            flags.append("missing_manifest")
        if not has_posted:
            flags.append("missing_posted_count")
        if group["pending_event_ids"]:
            flags.append("pending_events")
        if group["good_units"] < 0:
            flags.append("negative_posted_good")
        if group["damaged_units"] < 0:
            flags.append("negative_posted_damaged")
        result = {
            "key": dict(zip(KEY_FIELDS, key)),
            "manifest_qty": decimal_text(group["manifest_units"]) if has_manifest else None,
            "posted_good_qty": decimal_text(group["good_units"]) if has_posted else None,
            "posted_damaged_qty": decimal_text(group["damaged_units"]) if has_posted else None,
            "good_minus_manifest_qty": decimal_text(group["good_units"] - group["manifest_units"])
            if has_manifest and has_posted else None,
            "flags": flags,
        }
        for field in ("manifest_line_ids", "posted_event_ids", "pending_event_ids"):
            result[field] = sorted(group[field])
        results.append(result)
    return {
        "tool": TOOL, "version": VERSION, "key_fields": list(KEY_FIELDS),
        "input_summary": {"manifest_rows": len(manifest), "count_event_rows": len(events)},
        "groups": results,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", action="version", version=f"{TOOL} {VERSION}")
    parser.add_argument("--manifest", required=True, help="manifest CSV path")
    parser.add_argument("--count-events", required=True, help="additive count-events CSV path")
    args = parser.parse_args()
    try:
        result = compare(args.manifest, args.count_events)
    except (OSError, UnicodeError, csv.Error, ValueError) as error:
        print(json.dumps({"tool": TOOL, "version": VERSION, "error": str(error)}), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
