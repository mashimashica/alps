"""Test-only adapter: lose the first successful page response after quota charge."""
from pathlib import Path
import subprocess
import sys

api = Path(__file__).resolve().parents[1] / "input" / "ledger_api.py"
result = subprocess.run([sys.executable, str(api), *sys.argv[1:]], capture_output=True, text=True)
source = Path(sys.argv[sys.argv.index("--state") + 1])
marker = source.with_suffix(".lost")
if "page" in sys.argv and result.returncode == 0 and not marker.exists():
    marker.touch()
    sys.exit(1)
print(result.stdout, end="")
print(result.stderr, end="", file=sys.stderr)
sys.exit(result.returncode)
