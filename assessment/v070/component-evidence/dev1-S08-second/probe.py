#!/usr/bin/env python3.12
"""Independent bounded CLI probes. Only new states under this directory mutate."""
import concurrent.futures
import hashlib
import json
from pathlib import Path
import sqlite3
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
BASE = Path('/workspace/scratch/a75c3a6d9076/alps-v070-assessment/blind-dev1/S08')
RAW = BASE / 'original-creator-input/booking.py'
FIXTURE = BASE / 'original-creator-input/fixture.json'
PYTHON = sys.executable
LOG = []


def run(argv, tag):
    p = subprocess.run([str(v) for v in argv], text=True, capture_output=True, timeout=20)
    row = {'tag': tag, 'argv': [str(v) for v in argv], 'exit': p.returncode,
           'stdout': p.stdout, 'stderr': p.stderr}
    LOG.append(row)
    try:
        return json.loads(p.stdout), p.returncode
    except ValueError:
        return None, p.returncode


def raw(state, args, tag):
    return run([PYTHON, RAW, '--state', state, *args], tag)


def new_case(name, initialized=True):
    directory = ROOT / name
    directory.mkdir()
    state = directory / 'state.sqlite'
    ledger = directory / 'recovery.json'
    if initialized:
        raw(state, ['init', '--fixture', FIXTURE], name + ':init')
    return state, ledger


def wrapper_argv(candidate, state, ledger, mode, key=None, party='crew-cedar', slot='paper-lab-am', seats=2):
    package = BASE / candidate / 'package/recoverable-local-workshop-bookings/scripts'
    if candidate == 'R17':
        args = [PYTHON, package / 'reconcile_booking.py', mode, '--state', state, '--journal', ledger]
    else:
        args = [PYTHON, package / 'book.py', '--state', state, '--ledger', ledger,
                'reconcile' if mode == 'recover' else mode]
    if key is not None:
        args += ['--request-key', key]
    if mode == 'reserve':
        args += ['--party-id', party, '--slot-id', slot, '--seats', str(seats)]
    return args


def wrap(candidate, state, ledger, mode, tag, **kw):
    return run(wrapper_argv(candidate, state, ledger, mode, **kw), tag)


def inspect_case(state, ledger, keys, tag):
    availability, _ = raw(state, ['availability'], tag + ':availability')
    receipts = {k: raw(state, ['lookup', '--request-key', k], tag + ':lookup:' + k)[0] for k in keys}
    records = json.loads(ledger.read_text()) if ledger.exists() else None
    return {'availability': availability, 'receipts': receipts, 'ledger': records}


def parallel_calls(calls):
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(calls)) as pool:
        return list(pool.map(lambda item: run(*item), calls))


def snapshot_comparisons():
    results = {}
    for candidate in ('R17', 'R63'):
        for case in ('ordinary', 'challenging'):
            restored = {}
            for version in ('initial', 'final'):
                directory = BASE / candidate / case / 'committed-state'
                sql = (directory / (version + '.sql')).read_text()
                meta = json.loads((directory / (version + '.json')).read_text())
                assert hashlib.sha256(sql.encode()).hexdigest() == meta['sql_sha256']
                db = sqlite3.connect(':memory:')
                db.executescript(sql)
                db.execute('PRAGMA query_only = ON')
                restored[version] = {
                    'slots': db.execute('SELECT * FROM slots ORDER BY slot_id').fetchall(),
                    'operations': db.execute('SELECT * FROM operations ORDER BY request_key').fetchall(),
                }
                db.close()
            initial, final = restored['initial'], restored['final']
            before = {row[0]: row for row in initial['operations']}
            after = {row[0]: row for row in final['operations']}
            added = sorted(after.keys() - before.keys())
            assert len(added) == 1 and all(after[k] == v for k, v in before.items())
            initial_slots = {row[0]: row for row in initial['slots']}
            final_slots = {row[0]: row for row in final['slots']}
            assert initial_slots.keys() == final_slots.keys()
            assert all(initial_slots[k][:3] == final_slots[k][:3] for k in initial_slots)
            deltas = {k: final_slots[k][3] - initial_slots[k][3] for k in initial_slots}
            receipt = json.loads(after[added[0]][2])
            if case == 'ordinary':
                assert added == ['iris-screenprint-20261116-01']
                assert receipt == {'booking_id': 'booking:iris-screenprint-20261116-01',
                                   'party_id': 'team-iris', 'request_key': added[0], 'seats': 3,
                                   'slot_id': 'screenprint-mon-am', 'state': 'confirmed'}
                assert deltas == {'paper-marbling-tue': 0, 'risograph-mon-pm': 0, 'screenprint-mon-am': -3}
            else:
                assert added == ['orchid-linocut-20261122-01']
                assert receipt == {'party_id': 'crew-orchid', 'reason': 'insufficient_capacity',
                                   'request_key': added[0], 'seats': 3, 'slot_id': 'linocut-sun-am',
                                   'state': 'rejected'}
                assert all(v == 0 for v in deltas.values())
            results[candidate + '/' + case] = {'sql_hashes_valid': True, 'exact_expected_target': receipt,
                                              'capacity_deltas': deltas, 'other_receipts_unchanged': True,
                                              'initial_receipt_count': len(before), 'final_receipt_count': len(after)}
    return results


def probe_candidate(c):
    results = {}
    # Normal reserve, replay, local conflict, business rejections and syntax.
    s, l = new_case(c + '-basic')
    for tag, kw in [
        ('normal', {'key': 'normal'}),
        ('replay', {'key': 'normal'}),
        ('local-conflict', {'key': 'normal', 'party': 'changed-party'}),
        ('unknown-slot', {'key': 'unknown', 'slot': 'missing-slot'}),
        ('insufficient', {'key': 'too-many', 'seats': 7}),
        ('invalid-seats', {'key': 'invalid', 'seats': 0}),
    ]:
        out, rc = wrap(c, s, l, 'reserve', c + ':' + tag, **kw)
        results[tag] = {'out': out, 'exit': rc}
    results['basic-final'] = inspect_case(s, l, ['normal', 'unknown', 'too-many', 'invalid'], c + ':basic-final')

    # Server-side conflict with another valid payload already retained.
    s, l = new_case(c + '-server-conflict')
    raw(s, ['reserve', '--request-key', 'conflict', '--party-id', 'original-party',
            '--slot-id', 'paper-lab-am', '--seats', '2'], c + ':conflict-setup')
    out, rc = wrap(c, s, l, 'reserve', c + ':server-conflict', key='conflict', party='different-party', seats=3)
    results['server-conflict'] = {'out': out, 'exit': rc}
    out, rc = wrap(c, s, l, 'recover', c + ':conflict-recover', key='conflict')
    results['conflict-recover'] = {'out': out, 'exit': rc}
    results['conflict-final'] = inspect_case(s, l, ['conflict'], c + ':conflict-final')

    # Missing key, with a process-ended unavailable attempt and durable generated key.
    s, l = new_case(c + '-missing-key', initialized=False)
    out, rc = wrap(c, s, l, 'reserve', c + ':missing-key')
    results['missing-key'] = {'out': out, 'exit': rc, 'ledger': json.loads(l.read_text()) if l.exists() else None}
    raw(s, ['init', '--fixture', FIXTURE], c + ':missing-key-later-init')
    if l.exists():
        keys = list(json.loads(l.read_text()))
        assert len(keys) == 1
        key = keys[0]
        out, rc = wrap(c, s, l, 'recover', c + ':generated-key-recover', key=key)
        results['generated-key-recover'] = {'out': out, 'exit': rc}
        out, rc = wrap(c, s, l, 'reserve', c + ':generated-key-exact-retry', key=key)
        results['generated-key-exact-retry'] = {'out': out, 'exit': rc}
        results['missing-key-final'] = inspect_case(s, l, keys, c + ':missing-key-final')

    # Establish a ledger through a real wrapper attempt to an unavailable, nonexistent state.
    # Then initialize that NEW state and create the two legal ambiguous outcomes via public faults.
    # Each invocation ends before the next starts; recovery runs without a fault flag.
    for fault in ('before-commit', 'after-commit'):
        s, l = new_case(c + '-' + fault, initialized=False)
        first, first_rc = wrap(c, s, l, 'reserve', c + ':' + fault + ':ledger-create', key='durable')
        raw(s, ['init', '--fixture', FIXTURE], c + ':' + fault + ':init')
        fault_out, fault_rc = raw(s, ['reserve', '--request-key', 'durable', '--party-id', 'crew-cedar',
                                    '--slot-id', 'paper-lab-am', '--seats', '2', '--fault', fault],
                                  c + ':' + fault + ':uncertain-attempt')
        assert fault_out is None and fault_rc == 75
        out, rc = wrap(c, s, l, 'recover', c + ':' + fault + ':recover-1', key='durable')
        second, second_rc = wrap(c, s, l, 'recover', c + ':' + fault + ':recover-2', key='durable')
        before_retry = inspect_case(s, l, ['durable'], c + ':' + fault + ':before-manual-retry')
        retry, retry_rc = wrap(c, s, l, 'reserve', c + ':' + fault + ':exact-retry', key='durable')
        results[fault] = {'ledger_create': {'out': first, 'exit': first_rc},
                          'recover_1': {'out': out, 'exit': rc}, 'recover_2': {'out': second, 'exit': second_rc},
                          'before_manual_retry': before_retry,
                          'exact_retry': {'out': retry, 'exit': retry_rc},
                          'final': inspect_case(s, l, ['durable'], c + ':' + fault + ':final')}

    # Two independent coordinators competing for the same remaining capacity, separate ledgers.
    s, l = new_case(c + '-capacity-race')
    calls = [(wrapper_argv(c, s, l.with_name('ledger-' + str(i) + '.json'), 'reserve',
                           key='race-' + str(i), party='party-' + str(i), seats=4), c + ':capacity-race:' + str(i))
             for i in range(2)]
    results['capacity-race'] = {'calls': parallel_calls(calls),
                                'final': inspect_case(s, l, ['race-0', 'race-1'], c + ':capacity-race:final')}

    # Two continuations after the original process ended, same key/payload and shared ledger.
    s, l = new_case(c + '-same-key-race', initialized=False)
    wrap(c, s, l, 'reserve', c + ':same-key-race:ledger-create', key='same-key')
    raw(s, ['init', '--fixture', FIXTURE], c + ':same-key-race:init')
    calls = [(wrapper_argv(c, s, l, 'reserve', key='same-key'), c + ':same-key-race:' + str(i)) for i in range(2)]
    results['same-key-race'] = {'calls': parallel_calls(calls),
                               'final': inspect_case(s, l, ['same-key'], c + ':same-key-race:final')}

    # Multiple new logical requests using the same state and multi-entry recovery file.
    s, l = new_case(c + '-shared-ledger-race')
    keys = ['shared-' + str(i) for i in range(12)]
    calls = [(wrapper_argv(c, s, l, 'reserve', key=k, party='party-' + str(i), seats=1),
              c + ':shared-ledger-race:' + str(i)) for i, k in enumerate(keys)]
    outputs = parallel_calls(calls)
    final = inspect_case(s, l, keys, c + ':shared-ledger-race:final')
    missing = sorted(set(keys) - set(final['ledger'] or {}))
    recovery = None
    if missing:
        out, rc = wrap(c, s, l, 'recover', c + ':shared-ledger-race:missing-recovery', key=missing[0])
        recovery = {'key': missing[0], 'out': out, 'exit': rc}
    results['shared-ledger-race'] = {'calls': outputs, 'final': final, 'missing_keys': missing,
                                    'missing_key_recovery': recovery}

    if c == 'R63':
        s, l = new_case(c + '-generated-ledger-race')
        calls = [(wrapper_argv(c, s, l, 'reserve', party='party-' + str(i), seats=1),
                  c + ':generated-ledger-race:' + str(i)) for i in range(12)]
        outputs = parallel_calls(calls)
        keys = [out['request_key'] for out, rc in outputs]
        final = inspect_case(s, l, keys, c + ':generated-ledger-race:final')
        missing = sorted(set(keys) - set(final['ledger'] or {}))
        results['generated-ledger-race'] = {'calls': outputs, 'final': final, 'missing_keys': missing}
    return results


def main():
    summary = {'python': sys.version, 'probe_root': str(ROOT), 'snapshots': snapshot_comparisons()}
    summary['R17'] = probe_candidate('R17')
    summary['R63'] = probe_candidate('R63')
    print(json.dumps({'summary': summary, 'exact_calls': LOG}, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
