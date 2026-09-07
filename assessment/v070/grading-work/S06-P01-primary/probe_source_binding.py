"""Disposable component probe only; not a replay of a recorded application.

Test whether a saved prefix can be reused with another state path that has the
same immutable snapshot but an independent untouched quota. All writes stay in
this explicitly assigned grading-work directory. No tranche grants are used.
"""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
assert str(ROOT) == '/workspace/scratch/a75c3a6d9076/alps-v070-assessment/grading-work/S06-P01-primary'
PACKET = Path('/workspace/scratch/a75c3a6d9076/alps-v070-assessment/blind-business/S06-P01')
WORK = ROOT / 'disposable-source-binding'
WORK.mkdir(exist_ok=False)
records = []

def call(label, argv):
    result = subprocess.run([str(x) for x in argv], text=True, capture_output=True, timeout=30, cwd=WORK)
    row = dict(label=label, argv=[str(x) for x in argv], cwd=str(WORK), exit_code=result.returncode,
               stdout=result.stdout, stderr=result.stderr)
    records.append(row)
    (ROOT / 'probe-source-binding-commands-results.json').write_text(json.dumps(records, indent=2)+'\n')
    return result, json.loads(result.stdout)

definitions = [
    ('R17', 'reimbursement-rollup/scripts/rollup.py', '--state'),
    ('R28', 'complete-reimbursement-rollup/scripts/reimbursement_rollup.py', '--source-state'),
    ('R44', 'reimbursement-ledger-rollup/scripts/rollup.py', '--source-state'),
    ('R63', 'reimbursement-rollup/scripts/rollup.py', '--state'),
]
summary = []
for candidate, runner_path, state_flag in definitions:
    local = WORK / candidate
    local.mkdir()
    api = local / 'ledger_api.py'
    runner = local / 'runner.py'
    fixture = local / 'fixture.json'
    sources = [(PACKET/'original-creator-input/ledger_api.py', api),
               (PACKET/candidate/'package'/runner_path, runner),
               (PACKET/'original-consumer-inputs/challenging/fixture.json', fixture)]
    for source, target in sources:
        shutil.copy2(source, target)
        assert source.read_bytes() == target.read_bytes()
    source_a, source_b = local/'state-a.sqlite', local/'state-b.sqlite'
    cp = local/'checkpoint.json'
    for tag, state in [('A',source_a),('B',source_b)]:
        result, body = call(f'{candidate} initialize disposable {tag}', [sys.executable,api,'--state',state,'init','--fixture',fixture])
        assert result.returncode == 0
    def command(state):
        return [sys.executable,runner,'--api',api,state_flag,state,'--checkpoint',cp,
                '--start','2026-06-10','--end','2026-06-18']
    first, first_body = call(f'{candidate} incorporate first tranche from A', command(source_a))
    before = cp.read_bytes()
    (local/'checkpoint-after-a.json').write_bytes(before)
    result_a, meta_a = call(f'{candidate} describe A after first run', [sys.executable,api,'--state',source_a,'describe'])
    assert meta_a['remaining_calls'] == 0 and meta_a['tranche'] == 1
    second, second_body = call(f'{candidate} deliberately substitute B using same checkpoint', command(source_b))
    result_b, meta_b = call(f'{candidate} describe B after substitution', [sys.executable,api,'--state',source_b,'describe'])
    summary.append(dict(candidate=candidate, initial_run_exit=first.returncode, initial_run=first_body,
                        substituted_run_exit=second.returncode, substituted_run=second_body,
                        source_a=meta_a,source_b=meta_b,
                        checkpoint_unchanged=before==cp.read_bytes(),
                        runner_sha256=hashlib.sha256(runner.read_bytes()).hexdigest()))
(ROOT/'probe-source-binding-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
