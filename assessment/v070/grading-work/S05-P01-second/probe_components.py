"""Bounded component probes, not fresh consumer or business-review trials."""
import copy
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent
PACKET = Path('/workspace/scratch/a75c3a6d9076/alps-v070-assessment/blind-business/S05-P01')
SCRIPTS = {
    'R17': 'receiving-review/scripts/receiving_review.py',
    'R28': 'monthly-receiving-review/scripts/review.py',
    'R44': 'monthly-receiving-review/scripts/review.py',
    'R63': 'receiving-review/scripts/review_receipts.py',
}

def fixture():
    return {
        'month': '2026-07',
        'orders': [{'order_id': 'P1', 'sku': 'A', 'ordered': 10,
                    'supplier_contact': 'Supplier'}],
        'events': [],
        'coverage': [{'order_id': 'P1', 'sku': 'A', 'month': '2026-07',
                      'complete': True}],
        'responsibilities': {'purchasing_coordinator': 'Coordinator',
                             'warehouse_lead': 'Warehouse',
                             'data_steward': 'Steward'},
    }

def event(event_id, quantity, month='2026-07'):
    return {'event_id': event_id, 'order_id': 'P1', 'sku': 'A',
            'event_month': month, 'quantity': quantity}

def run(candidate, name, data, same_input_output=False):
    directory = ROOT / 'runs' / candidate / name
    directory.mkdir(parents=True)
    source = directory / 'input.json'
    source.write_text(json.dumps(data), encoding='utf-8')
    before = source.read_bytes()
    output = source if same_input_output else directory / 'report.json'
    cmd = ['python3', '-B', str(ROOT / 'copies' / candidate / SCRIPTS[candidate]),
           str(source)]
    if candidate != 'R28':
        cmd += ['--output', str(output)]
    result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    if candidate == 'R28' and result.returncode == 0:
        output.write_text(result.stdout, encoding='utf-8')
    parsed = json.loads(output.read_text()) if result.returncode == 0 else None
    line = None if parsed is None else parsed.get('lines', parsed.get('scope_lines'))[0]
    summary = {
        'candidate': candidate, 'probe': name, 'command': cmd, 'cwd': str(ROOT),
        'exit_code': result.returncode, 'stderr': result.stderr,
        'stdout_bytes': len(result.stdout.encode('utf-8')),
        'input_unchanged': source.read_bytes() == before,
        'line': line,
    }
    (directory / 'capture.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(json.dumps(summary, separators=(',', ':')))
    return summary

def main():
    for candidate in SCRIPTS:
        shutil.copytree(PACKET / candidate / 'package', ROOT / 'copies' / candidate)

    combined = fixture()
    combined['coverage'][0]['complete'] = False
    combined['events'] = [event('CONFLICT', 6), event('CONFLICT', 8), event('CLEAN', 1)]
    results = [run(c, 'same-line-conflict-and-partial', copy.deepcopy(combined))
               for c in SCRIPTS]

    old_conflict = fixture()
    old_conflict['events'] = [event('OLD', 6, '2026-06'), event('OLD', 8, '2026-06'),
                              event('CURRENT', 10)]
    results.append(run('R63', 'prior-month-only-conflict', old_conflict))

    alias = fixture()
    alias['events'] = [event('CURRENT', 10)]
    results.append(run('R63', 'output-is-input', alias, same_input_output=True))
    (ROOT / 'probe-results.json').write_text(json.dumps(results, indent=2), encoding='utf-8')

if __name__ == '__main__':
    main()
