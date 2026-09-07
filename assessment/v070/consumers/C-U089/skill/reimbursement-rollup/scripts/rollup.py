#!/usr/bin/env python3
"""Exact paginated rollup with durable continuation; see --help and SKILL.md."""
import argparse
import datetime
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


def date(value):
    if datetime.date.fromisoformat(value).isoformat() != value:
        raise ValueError('dates must use YYYY-MM-DD')
    return value


def save(path, value):
    fd, temporary = tempfile.mkstemp(prefix=path.name + '.', dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as stream:
            json.dump(value, stream, sort_keys=True)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def api(args, command):
    proc = subprocess.run([sys.executable, args.api, '--state', args.state, *command],
                          text=True, capture_output=True)
    if proc.returncode == 75:
        return None
    if proc.returncode:
        raise ValueError(f'API exit {proc.returncode}: {proc.stdout.strip()} {proc.stderr.strip()}')
    return json.loads(proc.stdout)


def output(checkpoint, status):
    rows = []
    for vendor, totals in sorted(checkpoint['vendors'].items()):
        charge, credit, count = totals
        rows.append(dict(vendor_id=vendor, settled_charge_cents=charge,
                         settled_credit_cents=credit, net_cents=charge-credit,
                         qualifying_entry_count=count))
    result = dict(status=status, snapshot_id=checkpoint['snapshot_id'],
                  start=checkpoint['request']['start'], end=checkpoint['request']['end'],
                  currency='USD', examined_records=len(checkpoint['seen']),
                  total_records=checkpoint['total_records'])
    result['vendors' if status == 'complete' else 'partial_vendors'] = rows
    print(json.dumps(result, sort_keys=True))


def run(args):
    date(args.start)
    date(args.end)
    if args.start > args.end:
        raise ValueError('start must be no later than end')
    args.api = str(Path(args.api).resolve())
    args.state = str(Path(args.state).resolve())
    path = Path(args.checkpoint).resolve()
    if path in (Path(args.api), Path(args.state)):
        raise ValueError('checkpoint must be separate from API and source state')
    request = dict(api=args.api, state=args.state, start=args.start, end=args.end)
    with open(str(path) + '.lock', 'a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        meta = api(args, ['describe'])
        if meta is None:
            raise ValueError('describe unexpectedly exhausted quota')
        if path.exists():
            cp = json.loads(path.read_text())
            if cp['version'] != 1 or cp['request'] != request:
                raise ValueError('checkpoint request mismatch')
            if (cp['snapshot_id'], cp['total_records']) != (meta['snapshot_id'], meta['total_records']):
                raise ValueError('checkpoint snapshot or record-count mismatch')
        else:
            cp = dict(version=1, request=request, snapshot_id=meta['snapshot_id'],
                      total_records=meta['total_records'], seen=[], cursors=[],
                      next_cursor=None, complete=False, vendors={})
            save(path, cp)
        while not cp['complete']:
            meta = api(args, ['describe'])
            if meta is None or (meta['snapshot_id'], meta['total_records']) != (cp['snapshot_id'], cp['total_records']):
                raise ValueError('source metadata changed')
            if meta['remaining_calls'] == 0:
                output(cp, 'incomplete')
                return 75
            cursor = cp['next_cursor']
            command = ['page', '--snapshot', cp['snapshot_id']]
            if cursor is not None:
                command += ['--cursor', cursor]
            page = api(args, command)
            if page is None:
                output(cp, 'incomplete')
                return 75
            if (page['snapshot_id'], page['total_records']) != (cp['snapshot_id'], cp['total_records']):
                raise ValueError('page snapshot or record-count mismatch')
            following = page['next_cursor']
            if following is not None and (not isinstance(following, str) or not following or following == cursor or following in cp['cursors']):
                raise ValueError('invalid or cycling cursor')
            seen = set(cp['seen'])
            for row in page['items']:
                if set(row) != {'entry_id', 'vendor_id', 'posted_on', 'kind', 'status', 'amount_cents', 'currency'}:
                    raise ValueError('record fields violate contract')
                if any(not isinstance(row[key], str) or not row[key] for key in ('entry_id', 'vendor_id')):
                    raise ValueError('invalid identifier')
                if row['entry_id'] in seen:
                    raise ValueError('duplicate entry in accepted traversal')
                date(row['posted_on'])
                if row['kind'] not in ('charge', 'credit') or row['status'] not in ('settled', 'pending', 'void') or row['currency'] != 'USD' or type(row['amount_cents']) is not int or row['amount_cents'] < 0:
                    raise ValueError('record violates ledger contract')
                seen.add(row['entry_id'])
                if row['status'] == 'settled' and args.start <= row['posted_on'] <= args.end:
                    totals = cp['vendors'].setdefault(row['vendor_id'], [0, 0, 0])
                    totals[0 if row['kind'] == 'charge' else 1] += row['amount_cents']
                    totals[2] += 1
            if len(seen) > cp['total_records'] or (following is None and len(seen) != cp['total_records']):
                raise ValueError('source coverage count mismatch')
            cp['seen'] = sorted(seen)
            cp['cursors'].append(cursor)
            cp['next_cursor'] = following
            cp['complete'] = following is None
            save(path, cp)
        output(cp, 'complete')
        return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--api', required=True, help='path to supplied ledger_api.py')
    parser.add_argument('--state', required=True, help='existing immutable source state')
    parser.add_argument('--start', required=True, help='inclusive YYYY-MM-DD')
    parser.add_argument('--end', required=True, help='inclusive YYYY-MM-DD')
    parser.add_argument('--checkpoint', required=True, help='dedicated durable JSON path; parent must exist')
    args = parser.parse_args()
    try:
        return run(args)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps(dict(status='error', detail=str(error))))
        return 2


if __name__ == '__main__':
    sys.exit(main())
