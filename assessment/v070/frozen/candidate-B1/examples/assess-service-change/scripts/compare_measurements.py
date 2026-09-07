"""Compare local request measurements against explicitly supplied pilot limits."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import sys
from pathlib import Path


def nonnegative_number(value: str) -> float:
    number = float(value)
    if not math.isfinite(number) or number < 0:
        raise ValueError("must be finite and nonnegative")
    return number


def summarize(path: Path) -> dict:
    data = path.read_bytes()
    reader = csv.reader(io.StringIO(data.decode("utf-8"), newline=""), strict=True)
    if next(reader, None) != ["request_id", "duration_ms", "status"]:
        raise ValueError(f"{path}: expected header request_id,duration_ms,status")
    identifiers = set()
    durations = []
    errors = 0
    for row in reader:
        location = f"{path}: CSV line {reader.line_num}"
        if len(row) != 3:
            raise ValueError(f"{location}: expected three fields")
        identifier, raw_duration, status = row
        if not identifier.strip() or identifier in identifiers:
            raise ValueError(f"{location}: request_id must be nonempty and unique")
        if status not in ("ok", "error"):
            raise ValueError(f"{location}: status must be ok or error")
        try:
            duration = nonnegative_number(raw_duration)
        except ValueError as error:
            raise ValueError(f"{location}: invalid duration_ms ({error})") from error
        identifiers.add(identifier)
        durations.append(duration)
        errors += status == "error"
    if not durations:
        raise ValueError(f"{path}: at least one measurement is required")
    durations.sort()
    count = len(durations)
    return {
        "path": str(path),
        "sha256": hashlib.sha256(data).hexdigest(),
        "count": count,
        "errors": errors,
        "error_rate": errors / count,
        "p95_ms": durations[math.ceil(0.95 * count) - 1],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", type=Path, help="baseline UTF-8 request CSV")
    parser.add_argument("candidate", type=Path, help="candidate UTF-8 request CSV")
    parser.add_argument("--min-samples", type=int, required=True,
                        help="minimum number of requests in each snapshot")
    parser.add_argument("--max-p95-ms", type=nonnegative_number, required=True,
                        help="maximum candidate nearest-rank p95 duration in ms")
    parser.add_argument("--max-error-rate", type=nonnegative_number, required=True,
                        help="maximum candidate error proportion, between 0 and 1")
    parser.add_argument("--max-p95-increase-ms", type=nonnegative_number, required=True,
                        help="maximum candidate p95 increase over baseline in ms")
    args = parser.parse_args(argv)
    if args.min_samples < 1 or args.max_error_rate > 1:
        parser.error("min-samples must be positive and max-error-rate at most 1")
    try:
        baseline = summarize(args.baseline)
        candidate = summarize(args.candidate)
    except (OSError, UnicodeError, ValueError, csv.Error) as error:
        print(f"measurement error: {error}", file=sys.stderr)
        return 2

    increase = candidate["p95_ms"] - baseline["p95_ms"]
    result = {
        "limits": {
            "min_samples": args.min_samples,
            "max_p95_ms": args.max_p95_ms,
            "max_error_rate": args.max_error_rate,
            "max_p95_increase_ms": args.max_p95_increase_ms,
        },
        "baseline": baseline,
        "candidate": candidate,
        "p95_increase_ms": increase,
        "checks": {
            "baseline_sample_count": baseline["count"] >= args.min_samples,
            "candidate_sample_count": candidate["count"] >= args.min_samples,
            "candidate_p95": candidate["p95_ms"] <= args.max_p95_ms,
            "candidate_error_rate": candidate["error_rate"] <= args.max_error_rate,
            "p95_increase": increase <= args.max_p95_increase_ms,
        },
    }
    print(json.dumps(result, ensure_ascii=False, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
