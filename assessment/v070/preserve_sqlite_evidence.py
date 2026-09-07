"""Preserve explicitly named SQLite evidence as native committed SQL.

For this assessment's plain-UTF-8 checkpoint route only. Original binary files
remain untouched. SQL restores logical state, not byte identity or call history.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re
import sqlite3

ROOT = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+")
    parser.add_argument("--label", required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"[a-z0-9-]+", args.label) or len(set(args.paths)) != len(args.paths):
        raise ValueError("Use a distinct simple label and explicit distinct source paths")
    index_path = ROOT / "sqlite-evidence-index.json"
    index = json.loads(index_path.read_text()) if index_path.exists() else {}
    plans = []
    for relative in args.paths:
        source = ROOT / relative
        if source.resolve() != source or not source.is_relative_to(ROOT):
            raise ValueError(f"Use a regular assessment-root-relative source: {relative}")
        if source.read_bytes()[:16] != b"SQLite format 3\x00":
            raise ValueError(f"Source is not a native SQLite database: {relative}")
        if any(Path(str(source) + suffix).exists() for suffix in ("-wal", "-journal")):
            raise ValueError(f"Active journal needs explicit consistent preservation: {relative}")
        target = ROOT / "sqlite-evidence" / args.label / (relative + ".sql")
        metadata = target.with_suffix(".json")
        if any(p.exists() or p.is_symlink() for p in (target, metadata)):
            raise ValueError(f"Preserve an existing or partial SQL observation: {relative}")
        plans.append((relative, source, target, metadata))
    for relative, source, target, metadata in plans:
        before = digest(source)
        connection = sqlite3.connect(source.as_uri() + "?mode=ro", uri=True)
        try:
            connection.execute("BEGIN")
            if connection.execute("PRAGMA quick_check").fetchall() != [("ok",)]:
                raise ValueError(f"Native database integrity check failed: {relative}")
            sql = "\n".join(connection.iterdump()) + "\n"
        finally:
            connection.close()
        if digest(source) != before:
            raise ValueError(f"Source changed during preservation: {relative}")
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("x", encoding="utf-8") as stream:
            stream.write(sql)
        record = {"source_path": relative, "source_sha256": before,
                  "sql_path": target.relative_to(ROOT).as_posix(),
                  "sql_sha256": digest(target), "sqlite_version": sqlite3.sqlite_version,
                  "representation": "Native SQL from a consistent committed read; logical state only, not binary identity or operation history"}
        with metadata.open("x", encoding="utf-8") as stream:
            json.dump(record, stream, indent=2)
            stream.write("\n")
        index[relative] = {**record, "metadata_path": metadata.relative_to(ROOT).as_posix(),
                           "metadata_sha256": digest(metadata)}
        index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(record))


if __name__ == "__main__":
    main()
