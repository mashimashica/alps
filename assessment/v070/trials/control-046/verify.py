import json
from pathlib import Path
import subprocess
import sys

root = Path(__file__).parent.resolve()
work = root / 'verification'
work.mkdir(exist_ok=True)
api = root / 'input/ledger_api.py'
helper = root / 'deliverables/skills/reimbursement-rollup/scripts/rollup.py'


def command(argv, expected=0):
    result = subprocess.run([sys.executable, *map(str, argv)], capture_output=True, text=True)
    assert result.returncode == expected, (argv, result.returncode, result.stdout, result.stderr)
    return json.loads(result.stdout)


def control(state, *args):
    return command([api, '--state', state, *args])


def roll(state, checkpoint, start='2026-02-01', end='2026-02-15', expected=0):
    return command([helper, '--api', api, '--state', state, '--checkpoint', checkpoint,
                    '--start', start, '--end', end], expected)


state = work / 'main.sqlite'
cp = work / 'main.json'
control(state, 'init', '--fixture', root / 'input/fixture.json')
assert roll(state, cp, start='2026-02-30', expected=2)['status'] == 'error'
assert roll(state, cp, start='2026-03-01', expected=2)['status'] == 'error'
assert control(state, 'describe')['remaining_calls'] == 2
assert not cp.exists()
assert roll(state, cp, expected=75)['examined_records'] == 6
assert roll(state, cp, expected=75)['examined_records'] == 6
control(state, 'grant-tranche')  # Test harness represents operator, never helper.
assert roll(state, cp, expected=75)['examined_records'] == 12
control(state, 'grant-tranche')
final = roll(state, cp)
records = json.loads((root / 'input/fixture.json').read_text())['records']
expected = {}
for row in records:
    if row['status'] == 'settled' and '2026-02-01' <= row['posted_on'] <= '2026-02-15':
        totals = expected.setdefault(row['vendor_id'], [0, 0, 0])
        totals[row['kind'] == 'credit'] += row['amount_cents']
        totals[2] += 1
assert final['examined_records'] == 17
assert final['vendors'] == [dict(vendor_id=k, charge_cents=v[0], credit_cents=v[1],
                                net_cents=v[0]-v[1], qualifying_entry_count=v[2])
                             for k, v in sorted(expected.items())]
assert roll(state, cp) == final
assert roll(state, cp, end='2026-02-16', expected=2)['status'] == 'error'
print('PASS: invalid dates, three tranches, exhausted resume, oracle totals, final repeat, request binding')

lost = work / 'lost.sqlite'
control(lost, 'init', '--fixture', root / 'input/fixture.json')
snapshot = control(lost, 'describe')['snapshot_id']
control(lost, 'page', '--snapshot', snapshot)  # Simulate counted response lost before persistence.
assert roll(lost, work / 'lost.json', expected=75)['examined_records'] == 3
for _ in range(3):
    control(lost, 'grant-tranche')
    result = roll(lost, work / 'lost.json', expected=75 if _ < 2 else 0)
assert result['vendors'] == final['vendors']
print('PASS: counted lost response retries within remaining quota without duplicate totals')

for name, rows, start, end in [('empty', [], '2026-02-01', '2026-02-15'),
                               ('no-match', records[:3], '2030-01-01', '2030-01-02')]:
    fixture = work / (name + '.json')
    fixture.write_text(json.dumps({'records': rows}))
    source = work / (name + '.sqlite')
    control(source, 'init', '--fixture', fixture)
    result = roll(source, work / (name + '-checkpoint.json'), start, end)
    assert result['status'] == 'complete' and result['vendors'] == []
print('PASS: empty source and no qualifying entries')
