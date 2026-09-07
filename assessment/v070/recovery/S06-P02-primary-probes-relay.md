# S06-P02 primary probe evidence relay

This recovery preserves text available in the assessment agent's existing conversation after the filesystem became unavailable. It does not report a new probe or a new filesystem read.

## Provenance and completeness

- The component_probes.py block below is the text supplied in the successful apply_patch call that created /workspace/scratch/a75c3a6d9076/alps-v070-assessment/grading-work/S06-P02-primary/component_probes.py.
- The five JSON lines in "Captured probe command output" are the event records actually returned by the successful command python3.12 component_probes.py, whose working directory was /workspace/scratch/a75c3a6d9076/alps-v070-assessment/grading-work/S06-P02-primary.
- The three JSON lines in "Captured non-command events" were actually returned by the later successful read of component-probe-results.json that printed events without an argv field.
- These outputs retain the contents of all eight event objects written by the script to component-probe-results.json. The original complete pretty-printed JSON file was not printed as one block in the retained conversation. This relay therefore preserves the observed event text rather than claiming byte-for-byte recovery of that file's serialization.
- The script establishes the file's event order: R44 setup, R44 empty-source run, R44 describe, R44 checkpoint, R17 setup, R17 completed-checkpoint run, R17 describe, R17 unchanged-checkpoint observation.
- No current filesystem bytes, native SQL dump, file hash, new runtime observation, or additional grading conclusion is supplied. The original report file write failed during the outage; the parent separately preserved the full relayed report.
- The disposable database paths recorded by the original script are /workspace/scratch/a75c3a6d9076/alps-v070-assessment/grading-work/S06-P02-primary/r44-empty-source/source.sqlite and /workspace/scratch/a75c3a6d9076/alps-v070-assessment/grading-work/S06-P02-primary/r17-completed-checkpoint/source.sqlite. Their current bytes and native SQL are not recovered here.

## Original component_probes.py text

~~~python
"""Two bounded checks of unchanged package copies; never open live source paths."""
from pathlib import Path
import json
import shutil
import sqlite3
import subprocess
import sys

PACKET = Path('/workspace/scratch/a75c3a6d9076/alps-v070-assessment/blind-business/S06-P02')
WORK = Path('/workspace/scratch/a75c3a6d9076/alps-v070-assessment/grading-work/S06-P02-primary')
events = []

def run(label, argv):
    proc = subprocess.run(argv, text=True, capture_output=True, cwd=WORK)
    event = {'label': label, 'argv': list(map(str, argv)), 'exit_code': proc.returncode,
             'stdout': proc.stdout, 'stderr': proc.stderr}
    events.append(event)
    print(json.dumps(event, sort_keys=True))
    return proc

empty = WORK / 'r44-empty-source'
empty.mkdir(exist_ok=False)
shutil.copy2(PACKET / 'original-creator-input/ledger_api.py', empty / 'ledger_api.py')
shutil.copy2(PACKET / 'R44/package/reimbursement-ledger-rollup/scripts/rollup.py', empty / 'rollup.py')
(empty / 'fixture.json').write_text('{"records":[]}\n')
run('R44 empty source setup', [sys.executable, str(empty / 'ledger_api.py'), '--state', str(empty / 'source.sqlite'), 'init', '--fixture', str(empty / 'fixture.json')])
run('R44 valid empty source', [sys.executable, str(empty / 'rollup.py'), '--api', str(empty / 'ledger_api.py'), '--state', str(empty / 'source.sqlite'), '--from', '2026-04-03', '--to', '2026-04-09', '--checkpoint', str(empty / 'checkpoint.json')])
run('R44 empty source quota afterward', [sys.executable, str(empty / 'ledger_api.py'), '--state', str(empty / 'source.sqlite'), 'describe'])
events.append({'label': 'R44 empty source checkpoint', 'checkpoint': json.loads((empty / 'checkpoint.json').read_text())})

finished = WORK / 'r17-completed-checkpoint'
finished.mkdir(exist_ok=False)
shutil.copy2(PACKET / 'original-creator-input/ledger_api.py', finished / 'ledger_api.py')
shutil.copy2(PACKET / 'R17/package/reimbursement-ledger-rollup/scripts/rollup.py', finished / 'rollup.py')
shutil.copy2(PACKET / 'R17/ordinary/work-evidence/checkpoint.json', finished / 'checkpoint.json')
with sqlite3.connect(finished / 'source.sqlite') as connection:
    connection.executescript((PACKET / 'R17/ordinary/committed-state/final.sql').read_text())
events.append({'label': 'R17 setup', 'operation': 'Restore preserved ordinary final.sql into a new disposable database; copy its completed checkpoint unchanged.'})
run('R17 completed checkpoint recheck', [sys.executable, str(finished / 'rollup.py'), '--api', str(finished / 'ledger_api.py'), '--source-state', str(finished / 'source.sqlite'), '--from', '2026-04-03', '--to', '2026-04-09', '--checkpoint', str(finished / 'checkpoint.json')])
run('R17 completed checkpoint quota afterward', [sys.executable, str(finished / 'ledger_api.py'), '--state', str(finished / 'source.sqlite'), 'describe'])
events.append({'label': 'R17 checkpoint retained', 'unchanged_bytes': (finished / 'checkpoint.json').read_bytes() == (PACKET / 'R17/ordinary/work-evidence/checkpoint.json').read_bytes()})

(WORK / 'component-probe-results.json').write_text(json.dumps(events, indent=2) + '\n')
~~~

## Captured probe command output

These are the five JSON event lines retained from the successful invocation. The later outer tool response represented stdout as an escaped string; the lines below preserve the command-output JSON text.

~~~jsonl
{"argv": ["/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3.12", "/workspace/scratch/a75c3a6d9076/alps-v070-assessment/grading-work/S06-P02-primary/r44-empty-source/ledger_api.py", "--state", "/workspace/scratch/a75c3a6d9076/alps-v070-assessment/grading-work/S06-P02-primary/r44-empty-source/source.sqlite", "init", "--fixture", "/workspace/scratch/a75c3a6d9076/alps-v070-assessment/grading-work/S06-P02-primary/r44-empty-source/fixture.json"], "exit_code": 0, "label": "R44 empty source setup", "stderr": "", "stdout": "{\"snapshot_id\":\"snap_4f53cda18c2baa0c0354bb5f\",\"state\":\"ready\",\"total_records\":0}\n"}
{"argv": ["/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3.12", "/workspace/scratch/a75c3a6d9076/alps-v070-assessment/grading-work/S06-P02-primary/r44-empty-source/rollup.py", "--api", "/workspace/scratch/a75c3a6d9076/alps-v070-assessment/grading-work/S06-P02-primary/r44-empty-source/ledger_api.py", "--state", "/workspace/scratch/a75c3a6d9076/alps-v070-assessment/grading-work/S06-P02-primary/r44-empty-source/source.sqlite", "--from", "2026-04-03", "--to", "2026-04-09", "--checkpoint", "/workspace/scratch/a75c3a6d9076/alps-v070-assessment/grading-work/S06-P02-primary/r44-empty-source/checkpoint.json"], "exit_code": 2, "label": "R44 valid empty source", "stderr": "", "stdout": "{\"error\":\"page next_cursor did not advance\",\"status\":\"error\"}\n"}
{"argv": ["/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3.12", "/workspace/scratch/a75c3a6d9076/alps-v070-assessment/grading-work/S06-P02-primary/r44-empty-source/ledger_api.py", "--state", "/workspace/scratch/a75c3a6d9076/alps-v070-assessment/grading-work/S06-P02-primary/r44-empty-source/source.sqlite", "describe"], "exit_code": 0, "label": "R44 empty source quota afterward", "stderr": "", "stdout": "{\"calls_per_tranche\":2,\"page_size\":3,\"remaining_calls\":1,\"snapshot_id\":\"snap_4f53cda18c2baa0c0354bb5f\",\"total_records\":0,\"tranche\":1}\n"}
{"argv": ["/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3.12", "/workspace/scratch/a75c3a6d9076/alps-v070-assessment/grading-work/S06-P02-primary/r17-completed-checkpoint/rollup.py", "--api", "/workspace/scratch/a75c3a6d9076/alps-v070-assessment/grading-work/S06-P02-primary/r17-completed-checkpoint/ledger_api.py", "--source-state", "/workspace/scratch/a75c3a6d9076/alps-v070-assessment/grading-work/S06-P02-primary/r17-completed-checkpoint/source.sqlite", "--from", "2026-04-03", "--to", "2026-04-09", "--checkpoint", "/workspace/scratch/a75c3a6d9076/alps-v070-assessment/grading-work/S06-P02-primary/r17-completed-checkpoint/checkpoint.json"], "exit_code": 75, "label": "R17 completed checkpoint recheck", "stderr": "", "stdout": "{\"checkpoint\":\"/workspace/scratch/a75c3a6d9076/alps-v070-assessment/grading-work/S06-P02-primary/r17-completed-checkpoint/checkpoint.json\",\"interval\":{\"from\":\"2026-04-03\",\"to\":\"2026-04-09\"},\"reason\":\"tranche_exhausted\",\"snapshot_id\":\"snap_c22e71aa06b43ab25395e0ce\",\"status\":\"paused\"}\n"}
{"argv": ["/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3.12", "/workspace/scratch/a75c3a6d9076/alps-v070-assessment/grading-work/S06-P02-primary/r17-completed-checkpoint/ledger_api.py", "--state", "/workspace/scratch/a75c3a6d9076/alps-v070-assessment/grading-work/S06-P02-primary/r17-completed-checkpoint/source.sqlite", "describe"], "exit_code": 0, "label": "R17 completed checkpoint quota afterward", "stderr": "", "stdout": "{\"calls_per_tranche\":2,\"page_size\":3,\"remaining_calls\":0,\"snapshot_id\":\"snap_c22e71aa06b43ab25395e0ce\",\"total_records\":6,\"tranche\":1}\n"}
~~~

## Captured non-command events

The later successful read selected the events without argv from the actual saved component-probe-results.json and printed them with json.dumps(event, sort_keys=True). These are the retained lines.

~~~jsonl
{"checkpoint": {"from_date": "2026-04-03", "next_cursor": null, "pages_fetched": 0, "seen_entry_ids": [], "snapshot_id": "snap_4f53cda18c2baa0c0354bb5f", "source_state": "/workspace/scratch/a75c3a6d9076/alps-v070-assessment/grading-work/S06-P02-primary/r44-empty-source/source.sqlite", "to_date": "2026-04-09", "total_records": 0, "totals": {}, "version": 1}, "label": "R44 empty source checkpoint"}
{"label": "R17 setup", "operation": "Restore preserved ordinary final.sql into a new disposable database; copy its completed checkpoint unchanged."}
{"label": "R17 checkpoint retained", "unchanged_bytes": true}
~~~

## Missing items and interpretation limits

The original complete component-probe-results.json serialization and its current file bytes were not directly retained as a single complete read. All eight event objects' contents are retained above. No checksum or native SQL dump of either disposable database was retained in the successful output available to this recovery agent, so none is asserted or reconstructed. This relay does not verify that the pre-outage local files remain available. The parent may attach this immutable recovery blob alongside the already relayed assessment report.
