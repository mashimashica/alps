# Disposable grader-only API observer; copied API remains unchanged.
from pathlib import Path
import json,subprocess,sys
API = '/workspace/scratch/a75c3a6d9076/alps-v070-assessment/grading-work/S06-P02-second/disposable-probes/copied-input/ledger_api.py'
LOG = Path('/workspace/scratch/a75c3a6d9076/alps-v070-assessment/grading-work/S06-P02-second/disposable-probes/R63/lost-first-response/public-api-calls.jsonl')
LOSE_FIRST = True
MARKER = Path('/workspace/scratch/a75c3a6d9076/alps-v070-assessment/grading-work/S06-P02-second/disposable-probes/R63/lost-first-response/loss.marker')
command = [sys.executable, API, *sys.argv[1:]]
r = subprocess.run(command, text=True, capture_output=True)
drop = LOSE_FIRST and 'page' in sys.argv and r.returncode == 0 and not MARKER.exists()
if drop:
    MARKER.write_text('First successful page stdout intentionally withheld by grader.\n')
with LOG.open('a') as out:
    out.write(json.dumps({'argv':command,'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'stdout_withheld_from_runner':drop},sort_keys=True)+'\n')
if not drop:
    sys.stdout.write(r.stdout)
sys.stderr.write(r.stderr)
sys.exit(r.returncode)
