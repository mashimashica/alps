#!/usr/bin/env python3.12
import json
from pathlib import Path
import subprocess
import sys
root = Path(__file__).resolve().parent
args = sys.argv[1:]
p = subprocess.run([sys.executable, str(root / "ledger_api.py"), *args], capture_output=True, text=True)
is_page = len(args) >= 3 and args[2] == "page"
drop = is_page and p.returncode == 0 and (root / "drop-first-page-response.enabled").exists() and not (root / "response-dropped.marker").exists()
if drop:
    (root / "response-dropped.marker").write_text("First successful page response deliberately withheld; source call was counted.\n")
with (root / "api-trace.jsonl").open("a") as f:
    f.write(json.dumps(dict(argv=args, returncode=p.returncode, original_stdout=p.stdout, original_stderr=p.stderr, stdout_withheld=drop)) + "\n")
sys.stdout.write("" if drop else p.stdout)
sys.stderr.write(p.stderr)
sys.exit(p.returncode)
