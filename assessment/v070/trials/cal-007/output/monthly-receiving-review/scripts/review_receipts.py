#!/usr/bin/env python3
"""Normalize monthly receipt evidence and expose line-level review facts."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


MONTH_RE = re.compile(r"^(\d{4})-(\d{2})$")
ROLES = ("purchasing_coordinator", "warehouse_lead", "data_steward")


class InterfaceError(ValueError):
    """A fatal document or CLI interface error."""


def valid_month(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    match = MONTH_RE.fullmatch(value)
    return bool(match and 1 <= int(match.group(2)) <= 12)


def nonempty_string(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def is_integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def issue(code: str, message: str, **details: Any) -> dict[str, Any]:
    result = {"code": code, "message": message}
    result.update(details)
    return result


def party(role: str, responsibilities: dict[str, str | None]) -> dict[str, Any]:
    return {"role": role, "recipient": responsibilities.get(role)}


def affected_keys(
    record: dict[str, Any],
    month: str,
    order_ids: dict[str, set[tuple[str, str]]],
    *,
    uncertain_month_affects_order: bool = False,
) -> set[tuple[str, str]]:
    order_id = nonempty_string(record.get("order_id"))
    if order_id not in order_ids:
        return set()
    event_month = record.get("event_month")
    if event_month != month and not (
        uncertain_month_affects_order and not valid_month(event_month)
    ):
        return set()
    sku = nonempty_string(record.get("sku"))
    key = (order_id, sku) if sku is not None else None
    if key in order_ids[order_id]:
        return {key}
    return set(order_ids[order_id])


def parse_document(raw: bytes, source: str) -> dict[str, Any]:
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise InterfaceError(f"input is not valid UTF-8: {exc}") from exc
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise InterfaceError(
            f"input is not valid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc
    if not isinstance(data, dict):
        raise InterfaceError("input root must be a JSON object")
    if not valid_month(data.get("month")):
        raise InterfaceError('field "month" must be a valid string in YYYY-MM form')
    for field in ("orders", "events", "coverage"):
        if not isinstance(data.get(field), list):
            raise InterfaceError(f'field "{field}" must be a JSON array')
    if not isinstance(data.get("responsibilities"), dict):
        raise InterfaceError('field "responsibilities" must be a JSON object')
    data["_input"] = {
        "source": source,
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
    }
    return data


def process(data: dict[str, Any]) -> dict[str, Any]:
    month: str = data["month"]
    scope_issues: list[dict[str, Any]] = []
    evidence_issues: list[dict[str, Any]] = []
    exclusions: list[dict[str, Any]] = []

    responsibilities: dict[str, str | None] = {}
    for role in ROLES:
        responsibilities[role] = nonempty_string(data["responsibilities"].get(role))

    lines: dict[tuple[str, str], dict[str, Any]] = {}
    order_conflicts: defaultdict[tuple[str, str], list[int]] = defaultdict(list)
    exact_order_duplicates: list[dict[str, Any]] = []

    for index, raw_order in enumerate(data["orders"]):
        if not isinstance(raw_order, dict):
            scope_issues.append(issue(
                "invalid_order_record",
                "Supplied order record is not an object and cannot be represented as a line.",
                record_index=index,
            ))
            continue
        order_id = nonempty_string(raw_order.get("order_id"))
        sku = nonempty_string(raw_order.get("sku"))
        ordered = raw_order.get("ordered")
        if order_id is None or sku is None or not is_integer(ordered) or ordered <= 0:
            scope_issues.append(issue(
                "invalid_order_record",
                "Supplied order needs nonempty order_id and sku and a positive integer ordered quantity.",
                record_index=index,
                order_id=order_id,
                sku=sku,
            ))
            continue
        supplier = nonempty_string(raw_order.get("supplier_contact"))
        key = (order_id, sku)
        candidate = {
            "order_id": order_id,
            "sku": sku,
            "ordered": ordered,
            "supplier_contact": supplier,
            "order_record_indexes": [index],
        }
        if key not in lines:
            lines[key] = candidate
        else:
            existing = lines[key]
            if (
                existing["ordered"] == ordered
                and existing["supplier_contact"] == supplier
            ):
                existing["order_record_indexes"].append(index)
                exact_order_duplicates.append({
                    "order_id": order_id,
                    "sku": sku,
                    "record_index": index,
                    "counted_once": True,
                })
            else:
                order_conflicts[key].append(index)
                existing["order_record_indexes"].append(index)

    order_ids: defaultdict[str, set[tuple[str, str]]] = defaultdict(set)
    for key in lines:
        order_ids[key[0]].add(key)

    event_groups: defaultdict[str, list[tuple[int, dict[str, Any]]]] = defaultdict(list)
    anonymous_events: list[tuple[int, Any]] = []
    for index, raw_event in enumerate(data["events"]):
        if not isinstance(raw_event, dict):
            anonymous_events.append((index, raw_event))
            continue
        event_id = nonempty_string(raw_event.get("event_id"))
        if event_id is None:
            anonymous_events.append((index, raw_event))
        else:
            event_groups[event_id].append((index, raw_event))

    line_findings: defaultdict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    line_events: defaultdict[tuple[str, str], list[tuple[str, int]]] = defaultdict(list)
    duplicate_events: list[dict[str, Any]] = []

    for index, raw_event in anonymous_events:
        event_issue = issue(
            "invalid_event_record",
            "Event record needs an event_id and valid object content; it was not included in a subtotal.",
            record_index=index,
        )
        evidence_issues.append(event_issue)
        keys: set[tuple[str, str]] = set()
        if isinstance(raw_event, dict):
            keys = affected_keys(
                raw_event, month, order_ids, uncertain_month_affects_order=True
            )
            raw_order_id = nonempty_string(raw_event.get("order_id"))
            raw_event_month = raw_event.get("event_month")
            if (
                not keys
                and raw_order_id is None
                and (raw_event_month == month or not valid_month(raw_event_month))
            ):
                keys = set(lines)
        else:
            keys = set(lines)
        for key in keys:
            line_findings[key].append(event_issue)

    for event_id, indexed_records in event_groups.items():
        canonical: dict[str, tuple[int, dict[str, Any]]] = {}
        for index, record in indexed_records:
            signature = json.dumps(record, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
            canonical.setdefault(signature, (index, record))
        if len(indexed_records) > len(canonical):
            duplicate_events.append({
                "event_id": event_id,
                "copies_ignored": len(indexed_records) - len(canonical),
            })
        variants = list(canonical.values())
        if len(variants) > 1:
            conflict = issue(
                "conflicting_event_id",
                "The same event_id has different content; all variants were excluded.",
                event_id=event_id,
                record_indexes=[item[0] for item in variants],
            )
            evidence_issues.append(conflict)
            keys: set[tuple[str, str]] = set()
            for _, record in variants:
                keys.update(affected_keys(
                    record, month, order_ids, uncertain_month_affects_order=True
                ))
            for key in keys:
                line_findings[key].append(conflict)
            continue

        index, record = variants[0]
        order_id = nonempty_string(record.get("order_id"))
        sku = nonempty_string(record.get("sku"))
        event_month = record.get("event_month")
        quantity = record.get("quantity")
        valid = (
            order_id is not None
            and sku is not None
            and valid_month(event_month)
            and is_integer(quantity)
        )
        if not valid:
            invalid = issue(
                "invalid_event_record",
                "Event needs nonempty order_id and sku, a valid event_month, and an integer quantity; it was excluded.",
                event_id=event_id,
                record_index=index,
            )
            evidence_issues.append(invalid)
            keys = affected_keys(
                record, month, order_ids, uncertain_month_affects_order=True
            )
            if (
                not keys
                and order_id is None
                and (event_month == month or not valid_month(event_month))
            ):
                keys = set(lines)
            for key in keys:
                line_findings[key].append(invalid)
            continue
        if event_month != month:
            exclusions.append({
                "type": "event_outside_requested_month",
                "event_id": event_id,
                "event_month": event_month,
            })
            continue
        if order_id not in order_ids:
            exclusions.append({
                "type": "event_order_outside_supplied_scope",
                "event_id": event_id,
                "order_id": order_id,
                "sku": sku,
            })
            continue
        key = (order_id, sku)
        if key not in lines:
            mismatch = issue(
                "event_sku_absent_from_order",
                "Current-month event uses an in-scope order with a SKU absent from that order; all lines for the order require identity reconciliation.",
                event_id=event_id,
                order_id=order_id,
                event_sku=sku,
            )
            evidence_issues.append(mismatch)
            for affected in order_ids[order_id]:
                line_findings[affected].append(mismatch)
            continue
        line_events[key].append((event_id, quantity))

    coverage_groups: defaultdict[tuple[str, str], list[tuple[int, Any]]] = defaultdict(list)
    invalid_coverage_by_line: defaultdict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for index, raw_coverage in enumerate(data["coverage"]):
        if not isinstance(raw_coverage, dict):
            evidence_issues.append(issue(
                "invalid_coverage_record",
                "Coverage record is not an object and cannot establish completeness.",
                record_index=index,
            ))
            continue
        order_id = nonempty_string(raw_coverage.get("order_id"))
        sku = nonempty_string(raw_coverage.get("sku"))
        coverage_month = raw_coverage.get("month")
        complete = raw_coverage.get("complete")
        key = (order_id, sku) if order_id is not None and sku is not None else None
        if not valid_month(coverage_month) or not isinstance(complete, bool) or key is None:
            invalid = issue(
                "invalid_coverage_record",
                "Coverage needs nonempty order_id and sku, a valid month, and Boolean complete.",
                record_index=index,
                order_id=order_id,
                sku=sku,
            )
            evidence_issues.append(invalid)
            if key in lines and (coverage_month == month or not valid_month(coverage_month)):
                invalid_coverage_by_line[key].append(invalid)
            continue
        if coverage_month != month:
            exclusions.append({
                "type": "coverage_outside_requested_month",
                "record_index": index,
                "order_id": order_id,
                "sku": sku,
                "month": coverage_month,
            })
            continue
        if key not in lines:
            exclusions.append({
                "type": "coverage_line_outside_supplied_scope",
                "record_index": index,
                "order_id": order_id,
                "sku": sku,
            })
            continue
        coverage_groups[key].append((index, complete))

    results: list[dict[str, Any]] = []
    all_recipient_gaps: set[str] = set()
    for key in sorted(lines):
        base = lines[key]
        findings = list(line_findings[key])
        if key in order_conflicts:
            findings.append(issue(
                "conflicting_order_line",
                "Multiple supplied records identify this line with different order content.",
                record_indexes=base["order_record_indexes"],
            ))

        coverage_records = coverage_groups.get(key, [])
        if invalid_coverage_by_line.get(key):
            coverage_status = "invalid"
            findings.extend(invalid_coverage_by_line[key])
        elif not coverage_records:
            coverage_status = "missing"
            findings.append(issue(
                "missing_coverage",
                "No valid coverage declaration exists for this line and requested month.",
            ))
        elif len({value for _, value in coverage_records}) > 1:
            coverage_status = "conflicting"
            findings.append(issue(
                "conflicting_coverage",
                "Coverage declarations disagree about completeness for this line and month.",
                record_indexes=[index for index, _ in coverage_records],
            ))
        elif coverage_records[0][1]:
            coverage_status = "complete"
        else:
            coverage_status = "incomplete"
            findings.append(issue(
                "incomplete_coverage",
                "Coverage explicitly states that the current-month export is incomplete.",
                record_indexes=[index for index, _ in coverage_records],
            ))

        events = sorted(line_events.get(key, []), key=lambda item: item[0])
        subtotal = sum(quantity for _, quantity in events)
        blocking_codes = {
            "conflicting_order_line",
            "conflicting_event_id",
            "event_sku_absent_from_order",
            "invalid_event_record",
            "invalid_coverage_record",
            "missing_coverage",
            "conflicting_coverage",
            "incomplete_coverage",
        }
        position_is_final = coverage_status == "complete" and not any(
            finding["code"] in blocking_codes for finding in findings
        )

        position = "unconfirmed"
        remaining = None
        excess = None
        if position_is_final:
            if subtotal == base["ordered"]:
                position = "received_as_ordered"
            elif subtotal < base["ordered"]:
                position = "shortfall"
                remaining = base["ordered"] - subtotal
            else:
                position = "excess"
                excess = subtotal - base["ordered"]

        follow_ups: list[dict[str, Any]] = []
        recipient_gaps: set[str] = set()
        identity_codes = {
            "conflicting_order_line",
            "conflicting_event_id",
            "event_sku_absent_from_order",
        }
        identity_findings = [f for f in findings if f["code"] in identity_codes]
        if identity_findings:
            parties = [
                party("purchasing_coordinator", responsibilities),
                party("data_steward", responsibilities),
            ]
            for item in parties:
                if item["recipient"] is None:
                    recipient_gaps.add(f'responsibilities.{item["role"]}')
            follow_ups.append({
                "type": "source_identity_reconciliation",
                "parties": parties,
                "next_action": "Reconcile the identified order and receipt-event source records before any final line comparison.",
                "evidence_codes": sorted({f["code"] for f in identity_findings}),
                "event_ids": sorted({
                    f["event_id"] for f in identity_findings if "event_id" in f
                }),
            })

        export_codes = {
            "invalid_event_record",
            "invalid_coverage_record",
            "missing_coverage",
            "conflicting_coverage",
            "incomplete_coverage",
        }
        export_findings = [f for f in findings if f["code"] in export_codes]
        if export_findings:
            steward = party("data_steward", responsibilities)
            if steward["recipient"] is None:
                recipient_gaps.add("responsibilities.data_steward")
            follow_ups.append({
                "type": "complete_export_confirmation",
                "parties": [steward],
                "next_action": "Provide or confirm a complete, valid current-month export for this line before final comparison.",
                "evidence_codes": sorted({f["code"] for f in export_findings}),
                "event_ids": sorted({
                    f["event_id"] for f in export_findings if "event_id" in f
                }),
            })

        if position == "shortfall":
            coordinator = party("purchasing_coordinator", responsibilities)
            if coordinator["recipient"] is None:
                recipient_gaps.add("responsibilities.purchasing_coordinator")
            if base["supplier_contact"] is None:
                recipient_gaps.add("orders[].supplier_contact")
            follow_ups.append({
                "type": "remaining_receipt_follow_up",
                "sender": coordinator,
                "recipient": base["supplier_contact"],
                "remaining_quantity": remaining,
                "next_action": "Ask the supplied supplier contact to confirm and resolve the remaining receipt quantity.",
            })
        elif position == "excess":
            lead = party("warehouse_lead", responsibilities)
            if lead["recipient"] is None:
                recipient_gaps.add("responsibilities.warehouse_lead")
            follow_ups.append({
                "type": "surplus_reconciliation",
                "parties": [lead],
                "excess_quantity": excess,
                "next_action": "Reconcile the surplus against the purchase order and receiving evidence.",
            })

        all_recipient_gaps.update(recipient_gaps)
        results.append({
            **base,
            "coverage_status": coverage_status,
            "coverage_record_indexes": [index for index, _ in coverage_records],
            "included_event_ids": [event_id for event_id, _ in events],
            "observed_uncontested_net_received": subtotal,
            "evidence_findings": findings,
            "position": position,
            "position_is_final": position_is_final,
            "remaining_quantity": remaining,
            "excess_quantity": excess,
            "follow_ups": follow_ups,
            "recipient_gaps": sorted(recipient_gaps),
        })

    counts = Counter(line["position"] for line in results)
    return {
        "schema_version": "1.0",
        "requested_month": month,
        "input": data["_input"],
        "responsibilities": responsibilities,
        "scope_issues": scope_issues,
        "evidence_issues": evidence_issues,
        "exclusions": exclusions,
        "exact_order_duplicates": exact_order_duplicates,
        "exact_event_duplicates": duplicate_events,
        "lines": results,
        "summary": {
            "supplied_order_records": len(data["orders"]),
            "represented_order_lines": len(results),
            "all_supplied_scope_represented": not scope_issues,
            "all_line_positions_final": all(line["position_is_final"] for line in results),
            "lines_requiring_follow_up": sum(bool(line["follow_ups"]) for line in results),
            "position_counts": {
                "received_as_ordered": counts["received_as_ordered"],
                "shortfall": counts["shortfall"],
                "excess": counts["excess"],
                "unconfirmed": counts["unconfirmed"],
            },
            "recipient_gaps": sorted(all_recipient_gaps),
        },
    }


def read_input(path: str) -> tuple[bytes, str]:
    if path == "-":
        return sys.stdin.buffer.read(), "stdin"
    try:
        return Path(path).read_bytes(), path
    except OSError as exc:
        raise InterfaceError(f"cannot read input {path!r}: {exc}") from exc


def write_output(result: dict[str, Any], path: str) -> None:
    rendered = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if path == "-":
        sys.stdout.write(rendered)
        return
    try:
        Path(path).write_text(rendered, encoding="utf-8")
    except OSError as exc:
        raise InterfaceError(f"cannot write output {path!r}: {exc}") from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate monthly receipt evidence and return line-level JSON facts.",
        epilog=(
            "Exit 0 means processing completed, even when evidence is incomplete. "
            "Exit 2 means no usable result was produced."
        ),
    )
    parser.add_argument("input", help="UTF-8 JSON input path, or - for standard input")
    parser.add_argument(
        "--output", "-o", default="-", help="JSON output path (default: standard output)"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.input != "-" and args.output != "-":
        try:
            if Path(args.input).resolve() == Path(args.output).resolve():
                raise InterfaceError("input and output paths must be different")
        except OSError:
            pass
    try:
        raw, source = read_input(args.input)
        data = parse_document(raw, source)
        result = process(data)
        write_output(result, args.output)
    except InterfaceError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
