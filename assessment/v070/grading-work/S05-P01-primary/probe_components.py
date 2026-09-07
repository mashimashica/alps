"""Bounded component probes; not a fresh consumer application."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys

PACKET = Path('/workspace/scratch/a75c3a6d9076/alps-v070-assessment/blind-business/S05-P01')
ROOT = Path(__file__).parent / 'probe-run'
ROOT.mkdir(exist_ok=False)
for candidate in ('R17', 'R63'):
    shutil.copytree(PACKET / candidate / 'package' / 'receiving-review', ROOT / candidate / 'skill')

def fixture():
    return {
        'month': '2026-08',
        'orders': [
            {'order_id': 'P1', 'sku': 'A', 'ordered': 10, 'supplier_contact': 'Supplier A'},
            {'order_id': 'P2', 'sku': 'B', 'ordered': 5, 'supplier_contact': 'Supplier B'}],
        'events': [
            {'event_id': 'E1', 'order_id': 'P1', 'sku': 'A', 'event_month': '2026-08', 'quantity': 10},
            {'event_id': 'E2', 'order_id': 'P2', 'sku': 'B', 'event_month': '2026-08', 'quantity': 5}],
        'coverage': [
            {'order_id': 'P1', 'sku': 'A', 'month': '2026-08', 'complete': True},
            {'order_id': 'P2', 'sku': 'B', 'month': '2026-08', 'complete': True}],
        'responsibilities': {'purchasing_coordinator': 'Coordinator', 'warehouse_lead': 'Warehouse', 'data_steward': 'Steward'}}

results = []

def run(candidate, name, data, same_path=False):
    directory = ROOT / candidate / name
    directory.mkdir()
    source = directory / 'input.json'
    source.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    before = source.read_bytes()
    scriptname = 'receiving_review.py' if candidate == 'R17' else 'review_receipts.py'
    command = [sys.executable, '-B', str(ROOT / candidate / 'skill' / 'scripts' / scriptname), str(source)]
    if same_path:
        command.extend(['--output', str(source)])
    result = subprocess.run(command, cwd=directory, capture_output=True, text=True)
    (directory / 'stdout.txt').write_text(result.stdout, encoding='utf-8')
    (directory / 'stderr.txt').write_text(result.stderr, encoding='utf-8')
    item = {'candidate': candidate, 'probe': name, 'command': command,
            'cwd': str(directory), 'exit': result.returncode, 'stderr': result.stderr.strip(),
            'input_bytes_changed': source.read_bytes() != before}
    report = json.loads(source.read_text()) if same_path and result.returncode == 0 else (json.loads(result.stdout) if result.stdout else None)
    if report is not None:
        lines = report.get('lines', report.get('scope_lines', []))
        item['line_results'] = [{k: line[k] for k in ('order_id', 'sku', 'status', 'observed_subtotal', 'observed_received', 'final_position', 'final_received', 'blocking_conditions', 'issues') if k in line} for line in lines]
        item['warnings'] = report.get('validation_warnings', [])
        item['output_top_level_keys'] = sorted(report)
    results.append(item)

run('R17', 'baseline', fixture())
d = fixture(); del d['events'][0]['event_month']
run('R17', 'missing_event_month', d)
d = fixture(); del d['orders'][0]['supplier_contact']
run('R17', 'missing_supplier_contact', d)
d = fixture(); del d['responsibilities']['warehouse_lead']
run('R17', 'missing_unused_warehouse_role', d)
run('R63', 'baseline', fixture())
d = fixture(); del d['events'][0]['quantity']
run('R63', 'missing_event_quantity', d)
d = fixture()
d['events'].extend([
    {'event_id': 'OLD', 'order_id': 'P1', 'sku': 'A', 'event_month': '2026-07', 'quantity': 1},
    {'event_id': 'OLD', 'order_id': 'P1', 'sku': 'A', 'event_month': '2026-07', 'quantity': 2}])
run('R63', 'prior_month_only_id_conflict', d)
run('R63', 'input_output_same_path', fixture(), same_path=True)
payload = {'runtime': sys.version, 'results': results}
(ROOT / 'results.json').write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
print(json.dumps(payload, indent=2))
