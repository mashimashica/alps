#!/usr/bin/env python3
"""Verification wrapper: suppress the first successful page response per state."""

from pathlib import Path
import subprocess
import sys


REAL_API = Path(__file__).resolve().parents[1] / "input" / "ledger_api.py"


def main() -> int:
    arguments = sys.argv[1:]
    try:
        state = Path(arguments[arguments.index("--state") + 1]).resolve()
    except (ValueError, IndexError):
        return 2
    marker = Path(str(state) + ".lost-once")
    if "page" in arguments and not marker.exists():
        result = subprocess.run(
            [sys.executable, str(REAL_API), *arguments],
            check=False,
            capture_output=True,
            text=True,
        )
        marker.write_text("response suppressed after the source call\n", encoding="utf-8")
        if result.stderr:
            sys.stderr.write(result.stderr)
        return result.returncode
    return subprocess.run([sys.executable, str(REAL_API), *arguments], check=False).returncode


if __name__ == "__main__":
    sys.exit(main())
