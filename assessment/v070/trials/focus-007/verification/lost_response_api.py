"""Verification-only adapter: consume a page, then lose its first response."""
import pathlib
import subprocess
import sys

api = pathlib.Path(__file__).resolve().parents[1] / "input/ledger_api.py"
state = pathlib.Path(sys.argv[sys.argv.index("--state") + 1])
marker = state.with_suffix(".lost")
response = subprocess.run([sys.executable, str(api), *sys.argv[1:]], capture_output=True)
if "page" in sys.argv and response.returncode == 0 and not marker.exists():
    marker.touch()
    print("lost response")
    sys.exit(0)
sys.stdout.buffer.write(response.stdout)
sys.stderr.buffer.write(response.stderr)
sys.exit(response.returncode)
