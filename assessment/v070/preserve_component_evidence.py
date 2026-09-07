"""Preserve the two completed S08 independent probe workspaces as text evidence.

Original artifacts are retained. SQLite snapshots represent committed logical
state, not byte-identical databases. This does not execute or grade a probe.
"""

import hashlib
import json
from pathlib import Path
import shutil
import sqlite3

ROOT = Path(__file__).resolve().parent
SOURCES = {
    "dev1-S08-primary": ROOT.parent / "s08-grade-probes-R7GDu8",
    "dev1-S08-second": ROOT.parent / "s08-second-probes-bIw1At",
}

for label, source in SOURCES.items():
    if not source.is_dir() or not (source / "probe.py").is_file():
        raise SystemExit(f"Completed probe source unavailable: {source}")
    target = ROOT / "component-evidence" / label
    if target.exists():
        raise SystemExit(f"Existing preserved evidence must not be overwritten: {label}")
    target.mkdir(parents=True)
    manifest = {"original_workspace": str(source), "role": "Completed independent component probes, not consumer trials",
                "files": {}}
    for path in sorted(source.rglob("*")):
        if not path.is_file() or path.is_symlink() or path.suffix not in {".py", ".json", ".sqlite"}:
            continue
        relative = path.relative_to(source)
        if path.suffix == ".sqlite":
            dest = (target / relative).with_suffix(".sql")
            dest.parent.mkdir(parents=True, exist_ok=True)
            con = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)
            try:
                con.execute("BEGIN")
                if con.execute("PRAGMA quick_check").fetchall() != [("ok",)]:
                    raise SystemExit(f"Probe state integrity failure: {path}")
                data = ("\n".join(con.iterdump()) + "\n").encode("utf-8")
            finally:
                con.close()
            with dest.open("xb") as stream:
                stream.write(data)
            mode = "Native SQL of consistent committed state; not original SQLite bytes"
        else:
            dest = target / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            data = path.read_bytes()
            data.decode("utf-8")
            shutil.copy2(path, dest)
            mode = "Unchanged original text bytes"
        manifest["files"][dest.relative_to(target).as_posix()] = {
            "source": str(path), "representation": mode, "sha256": hashlib.sha256(data).hexdigest()}
    (target / "preservation.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Preserved {label}: {len(manifest['files'])} files; original workspace unchanged")
