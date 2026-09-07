import concurrent.futures
import hashlib
import json
from pathlib import Path
import sqlite3
import subprocess
import sys

ROOT = Path('/workspace/scratch/a75c3a6d9076/alps-v070-assessment/blind-dev1/S08')
WORK = Path(__file__).parent
RAW = ROOT / 'original-creator-input/booking.py'
FIXTURE = ROOT / 'original-creator-input/fixture.json'


def cli(script, args):
    result = subprocess.run([sys.executable, str(script), *map(str, args)], capture_output=True, text=True, timeout=30)
    try:
        value = json.loads(result.stdout)
    except json.JSONDecodeError:
        value = result.stdout
    return {'exit': result.returncode, 'stdout': value, 'stderr': result.stderr.strip()}


def raw(state, *args):
    return cli(RAW, ['--state', state, *args])


def book(candidate, state, record, op, key=None, party='crew-cedar', slot='paper-lab-am', seats=2):
    package = ROOT / candidate / 'package/recoverable-local-workshop-bookings/scripts'
    if candidate == 'R17':
        script = package / 'reconcile_booking.py'
        args = [op, '--state', state, '--journal', record]
    else:
        script = package / 'book.py'
        args = ['--state', state, '--ledger', record, op]
    if key is not None:
        args += ['--request-key', key]
    if op == 'reserve':
        args += ['--party-id', party, '--slot-id', slot, '--seats', str(seats)]
    return cli(script, args)


def scenario(name, initialize=True):
    directory = WORK / name
    directory.mkdir()
    state = directory / 'bookings.sqlite'
    record = directory / 'record.json'
    if initialize:
        assert raw(state, 'init', '--fixture', FIXTURE)['exit'] == 0
    return state, record


def show(label, value):
    print(json.dumps({'probe': label, 'observed': value}, sort_keys=True), flush=True)


# Restore only the copied native snapshots into in-memory databases. All subsequent
# snapshot operations are reads; no path from snapshot metadata is opened.
for candidate in ['R17', 'R63']:
    for case in ['ordinary', 'challenging']:
        snapshots = {}
        for stage in ['initial', 'final']:
            source = ROOT / candidate / case / 'committed-state' / (stage + '.sql')
            metadata = json.loads(source.with_suffix('.json').read_text())
            sql = source.read_bytes()
            assert hashlib.sha256(sql).hexdigest() == metadata['sql_sha256']
            connection = sqlite3.connect(':memory:')
            connection.executescript(sql.decode())
            assert connection.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
            snapshots[stage] = {
                'slots': connection.execute('SELECT slot_id, starts_at, capacity, remaining FROM slots ORDER BY slot_id').fetchall(),
                'operations': {key: {'payload': json.loads(payload), 'receipt': json.loads(receipt)} for key, payload, receipt in connection.execute('SELECT request_key, payload, receipt FROM operations ORDER BY request_key')},
            }
            connection.close()
        before, after = snapshots['initial'], snapshots['final']
        added_keys = sorted(set(after['operations']) - set(before['operations']))
        removed_keys = sorted(set(before['operations']) - set(after['operations']))
        preserved_prior = all(after['operations'].get(key) == receipt for key, receipt in before['operations'].items())
        assert len(added_keys) == 1 and not removed_keys and preserved_prior
        fixture = json.loads((ROOT / 'original-consumer-inputs' / case / 'fixture.json').read_text())
        expected_properties = sorted((slot['slot_id'], slot['starts_at'], slot['capacity']) for slot in fixture['slots'])
        assert [tuple(row[:3]) for row in before['slots']] == expected_properties
        assert [tuple(row[:3]) for row in after['slots']] == expected_properties
        show(candidate + '/' + case + '/snapshots', {
            'all_snapshot_hashes_and_integrity': 'verified',
            'prior_operations_unchanged': preserved_prior,
            'added_operations': {key: after['operations'][key] for key in added_keys},
            'removed_operations': removed_keys,
            'slots_before': before['slots'], 'slots_after': after['slots'],
        })

for candidate in ['R17', 'R63']:
    recover = 'recover' if candidate == 'R17' else 'reconcile'

    state, record = scenario(candidate + '-missing-key')
    result = book(candidate, state, record, 'reserve')
    show(candidate + '/missing-key', {'result': result, 'record_exists': record.exists(), 'record': json.loads(record.read_text()) if record.exists() else None, 'availability': raw(state, 'availability')})

    for fault in ['before-commit', 'after-commit']:
        state, record = scenario(candidate + '-' + fault, initialize=False)
        key = 'probe-' + fault
        # Use the wrapper itself to create the durable request during an actual
        # missing-state access failure. Initialize a new state only after that.
        unavailable = book(candidate, state, record, 'reserve', key)
        assert raw(state, 'init', '--fixture', FIXTURE)['exit'] == 0
        fault_result = raw(state, 'reserve', '--request-key', key, '--party-id', 'crew-cedar', '--slot-id', 'paper-lab-am', '--seats', 2, '--fault', fault)
        assert fault_result['exit'] == 75 and not fault_result['stdout']
        recovery = book(candidate, state, record, recover, key)
        lookup = raw(state, 'lookup', '--request-key', key)
        show(candidate + '/' + fault, {'record_establishment': unavailable, 'fault_call': fault_result, 'recovery': recovery, 'lookup_after_recovery': lookup, 'availability': raw(state, 'availability')})
        if candidate == 'R63' and fault == 'before-commit':
            retry = book(candidate, state, record, 'reserve', key)
            show(candidate + '/' + fault + '/exact-key-reserve-continuation', {'retry': retry, 'lookup': raw(state, 'lookup', '--request-key', key)})

    state, record = scenario(candidate + '-conflict')
    key = 'probe-conflict'
    seed = raw(state, 'reserve', '--request-key', key, '--party-id', 'crew-other', '--slot-id', 'paper-lab-am', '--seats', 1)
    conflict = book(candidate, state, record, 'reserve', key)
    recovery = book(candidate, state, record, recover, key)
    show(candidate + '/server-conflict', {'seed': seed, 'changed_payload_attempt': conflict, 'recovery_after_conflict': recovery, 'record': json.loads(record.read_text()), 'native_lookup': raw(state, 'lookup', '--request-key', key)})

    state, record = scenario(candidate + '-invalid')
    key = 'probe-invalid'
    invalid = book(candidate, state, record, 'reserve', key, seats=0)
    native = raw(state, 'lookup', '--request-key', key)
    corrected = book(candidate, state, record, 'reserve', key, seats=2)
    show(candidate + '/invalid-input', {'invalid': invalid, 'native_lookup': native, 'same_key_valid_input': corrected})

    state, record = scenario(candidate + '-distinct-concurrent')
    def distinct(index):
        key = 'probe-distinct-' + str(index)
        return key, book(candidate, state, record, 'reserve', key, party='party-' + str(index), seats=1)
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
        results = dict(pool.map(distinct, range(12)))
    saved = json.loads(record.read_text())
    missing = sorted(set(results) - set(saved))
    native = {key: raw(state, 'lookup', '--request-key', key) for key in results}
    show(candidate + '/distinct-concurrent', {'results': results, 'ledger_keys': sorted(saved), 'missing_keys': missing, 'native_terminal_count': sum(value['stdout'].get('state') in ['confirmed', 'rejected'] for value in native.values()), 'native_confirmed_count': sum(value['stdout'].get('state') == 'confirmed' for value in native.values()), 'availability': raw(state, 'availability'), 'recovery_of_missing': book(candidate, state, record, recover, missing[0]) if missing else None})

    state, record = scenario(candidate + '-same-concurrent')
    key = 'probe-same'
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(lambda _: book(candidate, state, record, 'reserve', key), range(8)))
    show(candidate + '/same-concurrent', {'results': results, 'native_lookup': raw(state, 'lookup', '--request-key', key), 'availability': raw(state, 'availability')})

