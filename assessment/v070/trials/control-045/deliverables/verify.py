"""Local verification only: operator grants and fixture reads are test setup."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
API = ROOT / 'input/ledger_api.py'
RUNNER = ROOT / 'deliverables/skills/reimbursement-rollup/scripts/rollup.py'


def call(*args, expected=0):
    p = subprocess.run([sys.executable, *map(str, args)], capture_output=True, text=True)
    assert p.returncode == expected, (p.returncode, p.stdout, p.stderr)
    return json.loads(p.stdout)


with tempfile.TemporaryDirectory(dir=ROOT, prefix='verification-') as temporary:
    work = Path(temporary)
    state = work / 'source.sqlite'
    fixture = ROOT / 'input/fixture.json'
    call(API, '--state', state, 'init', '--fixture', fixture)
    def invoke(cp='checkpoint.json', start='2026-02-01', end='2026-02-15', expected=0, source=state, api=API):
        return call(RUNNER, '--api', api, '--state', source, '--checkpoint', work/cp,
                    '--start', start, '--end', end, expected=expected)
    for start, end in [('2026-02-30', '2026-03-01'), ('2026-02-15', '2026-02-01'), ('20260201', '2026-02-15')]:
        assert invoke(start=start, end=end, expected=2)['status'] == 'error'
    assert call(API, '--state', state, 'describe')['remaining_calls'] == 2
    first = invoke(expected=75)
    assert first['examined_records'] == 6 and first['status'] == 'incomplete'
    assert invoke(expected=75) == first
    call(API, '--state', state, 'grant-tranche')
    assert invoke(expected=75)['examined_records'] == 12
    call(API, '--state', state, 'grant-tranche')
    final = invoke()
    assert final['examined_records'] == final['total_records'] == 17
    expected = {}
    for r in json.loads(fixture.read_text())['records']:
        if r['status'] == 'settled' and '2026-02-01' <= r['posted_on'] <= '2026-02-15':
            v = expected.setdefault(r['vendor_id'], dict(vendor_id=r['vendor_id'], settled_charge_cents=0,
                settled_credit_cents=0, net_cents=0, qualifying_entry_count=0))
            v['settled_' + r['kind'] + '_cents'] += r['amount_cents']
            v['net_cents'] += r['amount_cents'] * (1 if r['kind'] == 'charge' else -1)
            v['qualifying_entry_count'] += 1
    assert final['vendors'] == [expected[k] for k in sorted(expected)]
    before = call(API, '--state', state, 'describe')
    assert invoke() == final
    assert call(API, '--state', state, 'describe') == before
    assert invoke(start='2026-02-02', expected=2)['status'] == 'error'
    print('PASS invalid intervals consume no calls; 6/12/17 coverage; paused and complete retries; exact fixture oracle; interval binding')

    empty = work / 'empty.json'
    empty.write_text('{"records":[]}')
    empty_state = work / 'empty.sqlite'
    call(API, '--state', empty_state, 'init', '--fixture', empty)
    assert invoke(cp='empty-cp.json', source=empty_state)['vendors'] == []
    no_match = work / 'no-match.sqlite'
    call(API, '--state', no_match, 'init', '--fixture', fixture)
    for _ in range(2):
        assert invoke(cp='no-match-cp.json', source=no_match, start='2025-01-01', end='2025-01-02', expected=75)['partial_vendors'] == []
        call(API, '--state', no_match, 'grant-tranche')
    assert invoke(cp='no-match-cp.json', source=no_match, start='2025-01-01', end='2025-01-02')['vendors'] == []
    print('PASS empty ledger and exhaustive no-match interval')

    lost_state = work / 'lost.sqlite'
    call(API, '--state', lost_state, 'init', '--fixture', fixture)
    wrapper = work / 'loss.py'
    marker = work / 'dropped'
    wrapper.write_text('import subprocess,sys\nfrom pathlib import Path\n'
        + f'p=subprocess.run([sys.executable,{str(API)!r},*sys.argv[1:]],capture_output=True,text=True)\n'
        + f'm=Path({str(marker)!r})\n'
        + 'if "page" in sys.argv and p.returncode == 0 and not m.exists():\n'
        + ' m.touch()\n sys.exit(9)\n'
        + 'print(p.stdout,end="")\nsys.exit(p.returncode)\n')
    invoke(cp='lost-cp.json', source=lost_state, api=wrapper, expected=2)
    assert call(API, '--state', lost_state, 'describe')['remaining_calls'] == 1
    assert invoke(cp='lost-cp.json', source=lost_state, api=wrapper, expected=75)['examined_records'] == 3
    call(API, '--state', lost_state, 'grant-tranche')
    assert invoke(cp='lost-cp.json', source=lost_state, api=wrapper, expected=75)['examined_records'] == 9
    call(API, '--state', lost_state, 'grant-tranche')
    assert invoke(cp='lost-cp.json', source=lost_state, api=wrapper, expected=75)['examined_records'] == 15
    call(API, '--state', lost_state, 'grant-tranche')
    assert invoke(cp='lost-cp.json', source=lost_state, api=wrapper) == final
    print('PASS lost response consumes quota, retries same cursor, and completes without duplicate counting')
