#!/usr/bin/env python3
"""Resumable exact ledger rollup; never grants source tranches."""
import argparse
import datetime
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys


def date(value):
    if datetime.date.fromisoformat(value).isoformat() != value:
        raise ValueError('dates must use YYYY-MM-DD')
    return value


def save(path, value):
    temporary = path.with_name(path.name + '.tmp')
    with temporary.open('w') as stream:
        json.dump(value, stream, sort_keys=True)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)
    descriptor = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def api(args, *command):
    result = subprocess.run([sys.executable, args.api, '--state', args.state, *command],
                            capture_output=True, text=True)
    if result.returncode:
        if result.returncode == 75:
            raise BlockingIOError('source call budget exhausted')
        raise ValueError(f'API exit {result.returncode}: {result.stdout} {result.stderr}')
    return json.loads(result.stdout)


def output(cp):
    result = {k: cp[k] for k in ('snapshot_id', 'start', 'end', 'total_records')}
    result.update(status='complete' if cp['done'] else 'incomplete',
                  examined_records=len(cp['entries']), currency='USD')
    if cp['done']:
        vendors = {}
        for row in cp['entries'].values():
            if row['status'] != 'settled' or not cp['start'] <= row['posted_on'] <= cp['end']:
                continue
            vendor = vendors.setdefault(row['vendor_id'], dict(charge_cents=0, credit_cents=0,
                                                              qualifying_entry_count=0))
            vendor[row['kind'] + '_cents'] += row['amount_cents']
            vendor['qualifying_entry_count'] += 1
        result['vendors'] = [dict(vendor_id=key, **vendors[key],
                                  net_cents=vendors[key]['charge_cents'] - vendors[key]['credit_cents'])
                             for key in sorted(vendors)]
    else:
        result['continuation'] = 'Preserve checkpoint; operator approval may be required before resuming.'
    print(json.dumps(result, sort_keys=True))
    return 0 if cp['done'] else 75


def run(args):
    date(args.start)
    date(args.end)
    if args.start > args.end:
        raise ValueError('start must not exceed end')
    args.api = str(Path(args.api).resolve())
    args.state = str(Path(args.state).resolve())
    path = Path(args.checkpoint).resolve()
    if str(path) in (args.api, args.state):
        raise ValueError('checkpoint must be separate from source and API')
    identity = dict(start=args.start, end=args.end, api=args.api, state=args.state)
    with path.with_name(path.name + '.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        cp = json.loads(path.read_text()) if path.exists() else None
        if cp and (cp['version'] != 1 or any(cp[k] != v for k, v in identity.items())):
            raise ValueError('checkpoint belongs to another request')
        meta = api(args, 'describe')
        if cp is None:
            cp = dict(version=1, **identity, snapshot_id=meta['snapshot_id'],
                      total_records=meta['total_records'], entries={}, cursor=None, done=False,
                      processed_cursors=[])
            save(path, cp)
        if (cp['snapshot_id'], cp['total_records']) != (meta['snapshot_id'], meta['total_records']):
            raise ValueError('source snapshot or record count changed')
        initial_tranche = meta['tranche']
        for _ in range(2):
            if cp['done']:
                break
            meta = api(args, 'describe')
            if meta['snapshot_id'] != cp['snapshot_id'] or meta['total_records'] != cp['total_records']:
                raise ValueError('source identity changed')
            if meta['tranche'] != initial_tranche or meta['remaining_calls'] <= 0:
                break
            command = ['page', '--snapshot', cp['snapshot_id']]
            if cp['cursor'] is not None:
                command += ['--cursor', cp['cursor']]
            try:
                page = api(args, *command)
            except BlockingIOError:
                break
            if page['snapshot_id'] != cp['snapshot_id'] or page['total_records'] != cp['total_records']:
                raise ValueError('page identity mismatch')
            if page['tranche'] != initial_tranche:
                raise ValueError('operator changed tranche during execution; retry checkpoint')
            for row in page['items']:
                date(row['posted_on'])
                if (not isinstance(row['entry_id'], str) or not row['entry_id'] or
                    not isinstance(row['vendor_id'], str) or not row['vendor_id'] or
                    row['kind'] not in ('charge', 'credit') or
                    row['status'] not in ('settled', 'pending', 'void') or
                    row['currency'] != 'USD' or type(row['amount_cents']) is not int or row['amount_cents'] < 0):
                    raise ValueError('invalid source record')
                if row['entry_id'] in cp['entries']:
                    raise ValueError('duplicate entry across disjoint source pages')
                cp['entries'][row['entry_id']] = row
            cp['processed_cursors'].append(cp['cursor'])
            following = page['next_cursor']
            if following is not None and (not isinstance(following, str) or following in cp['processed_cursors']):
                raise ValueError('invalid or cycling cursor')
            cp['cursor'] = following
            cp['done'] = following is None
            if len(cp['entries']) > cp['total_records'] or (cp['done'] and len(cp['entries']) != cp['total_records']):
                raise ValueError('record coverage mismatch')
            save(path, cp)
        return output(cp)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('api', 'state', 'checkpoint', 'start', 'end'):
        parser.add_argument('--' + name, required=True)
    args = parser.parse_args()
    try:
        return run(args)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps(dict(status='error', error=str(error))))
        return 2


if __name__ == '__main__':
    sys.exit(main())
