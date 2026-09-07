from pathlib import Path
import hashlib, json, shutil, subprocess, sys

PACKET = Path('/workspace/scratch/a75c3a6d9076/alps-v070-assessment/blind-business/S06-P01')
WORK = Path('/workspace/scratch/a75c3a6d9076/alps-v070-assessment/grading-work/S06-P01-second')
PROBE = WORK / 'disposable-r44-source-binding'
PROBE.mkdir(parents=True, exist_ok=False)
(PROBE / 'SCOPE.txt').write_text(
    'Independent component probe only, not a recorded consumer application.\n'
    'All API source writes are confined to disposable copies in this directory.\n'
    'Tests checkpoint acceptance after switching between separately initialized same-snapshot states.\n'
    'No grants, no original source-state paths, no evaluated artifact edits.\n')
sources = {
    'ledger_api.py': PACKET/'original-creator-input/ledger_api.py',
    'fixture.json': PACKET/'original-consumer-inputs/challenging/fixture.json',
    'rollup.py': PACKET/'R44/package/reimbursement-ledger-rollup/scripts/rollup.py',
}
copies = []
for name, source in sources.items():
    destination = PROBE / name
    shutil.copy2(source, destination)
    copies.append(dict(source=str(source), destination=str(destination),
                       sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                       identical=source.read_bytes()==destination.read_bytes()))
records = []
def call(*arguments):
    argv = [sys.executable, *map(str, arguments)]
    result = subprocess.run(argv, cwd=PROBE, text=True, capture_output=True, timeout=30)
    record = dict(argv=argv, cwd=str(PROBE), exit_code=result.returncode,
                  stdout=result.stdout, stderr=result.stderr)
    records.append(record)
    (PROBE/'commands-results.json').write_text(json.dumps(dict(
        label='Independent disposable component probe; not historical consumer evidence',
        copies=copies, commands=records), indent=2)+'\n')
    return result

api = PROBE/'ledger_api.py'
runner = PROBE/'rollup.py'
fixture = PROBE/'fixture.json'
state_a = PROBE/'source-a.sqlite'
state_b = PROBE/'source-b.sqlite'
checkpoint = PROBE/'request.json'
for state in [state_a, state_b]:
    assert call(api,'--state',state,'init','--fixture',fixture).returncode == 0
    assert call(api,'--state',state,'describe').returncode == 0

def run(state):
    return call(runner,'--api',api,'--source-state',state,
                '--checkpoint',checkpoint,'--start','2026-06-10','--end','2026-06-18')

first = run(state_a)
shutil.copy2(checkpoint,PROBE/'checkpoint-after-source-a.json')
second = run(state_b)
shutil.copy2(checkpoint,PROBE/'checkpoint-after-source-b.json')
for state in [state_a,state_b]:
    assert call(api,'--state',state,'describe').returncode == 0
first_body=json.loads(first.stdout)
second_body=json.loads(second.stdout)
summary=dict(
    label='Independent disposable component probe; not historical consumer evidence',
    interpreter=sys.executable,
    python_version=sys.version,
    first_exit=first.returncode,
    first_result=first_body,
    after_source_change_exit=second.returncode,
    after_source_change_result=second_body,
    request_change_rejected=second_body.get('status')=='error',
    source_inputs_unchanged=all(
        hashlib.sha256(source.read_bytes()).hexdigest()==copies[i]['sha256']
        for i,source in enumerate(sources.values())),
)
(PROBE/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
print('All disposable database writes for this assessment are finished.')

