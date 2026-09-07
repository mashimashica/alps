"""Disposable component probes only; no agent application or source edits."""
from pathlib import Path
import copy
import hashlib
import json
import os
import shutil
import subprocess
import sys

PACKET = Path('/workspace/scratch/a75c3a6d9076/alps-v070-assessment/blind-business/S05-P02')
WORK = Path(__file__).resolve().parent
RUN = WORK / 'component-probes'
RUN.mkdir()
source = PACKET / 'original-consumer-inputs/ordinary/input/receiving.json'
original_bytes = source.read_bytes()
base = json.loads(original_bytes)
fixtures = {}
data = copy.deepcopy(base)
del data['responsibilities']['warehouse_lead']
fixtures['missing_warehouse_role'] = data
data = copy.deepcopy(base)
data['events'].append({'event_id': 'PROBE-UNATTRIBUTED', 'sku': 'CARTON-M',
                       'event_month': '2026-06', 'quantity': 7})
fixtures['current_event_missing_order_id'] = data
data = copy.deepcopy(base)
data['events'].append({'order_id': 'PO-R2606-410', 'sku': 'LABEL-60',
                       'event_month': '2026-05', 'quantity': 1})
fixtures['prior_month_event_missing_id'] = data
for name, data in fixtures.items():
    (RUN / f'{name}.json').write_text(json.dumps(data, indent=2) + '\n')

packages = {'R17': ('review-monthly-receiving', 'review_receiving.py'),
            'R28': ('monthly-receiving-review', 'review_receiving.py'),
            'R44': ('monthly-receiving-review', 'review_receiving.py'),
            'R63': ('monthly-receiving-review', 'review.py')}
log = {'python': sys.version, 'probe_scope': 'Three targeted component fixtures derived from the fixed ordinary input; no new agent/business application.', 'runs': []}
for candidate, (folder, script) in packages.items():
    copied = RUN / candidate
    shutil.copytree(PACKET / candidate / 'package' / folder, copied)
    for fixture in fixtures:
        input_path = RUN / f'{fixture}.json'
        output_path = copied / f'{fixture}.report.json'
        argv = [sys.executable, '-B', str(copied / 'scripts' / script)]
        if candidate == 'R63':
            argv.append('--input')
        argv.extend([str(input_path), '--output', str(output_path)])
        before = hashlib.sha256(input_path.read_bytes()).hexdigest()
        result = subprocess.run(argv, cwd=copied, capture_output=True, text=True,
                                env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'), timeout=15)
        record = {'candidate': candidate, 'fixture': fixture, 'argv': argv, 'cwd': str(copied),
                  'exit': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr,
                  'input_bytes_unchanged': before == hashlib.sha256(input_path.read_bytes()).hexdigest(),
                  'report_created': output_path.exists()}
        if output_path.exists():
            report = json.loads(output_path.read_text())
            record['lines'] = []
            for line in report['lines']:
                status = line.get('disposition', line.get('position', line.get('receipt_position', line.get('status'))))
                final = line.get('final_net_received', line.get('final_net'))
                if candidate == 'R17' and line['final_comparison_allowed']:
                    final = line['observed_net_received']
                record['lines'].append({'sku': line['sku'], 'status': status, 'final': final,
                                        'gaps': line.get('evidence_gaps', line.get('evidence_issues', line.get('issue_ids'))),
                                        'actions': line.get('follow_ups', line.get('follow_up', line.get('actions')))})
            record['report_issues'] = report.get('input_issues', report.get('unassigned_issues', report.get('issues', report.get('scope_issues'))))
        log['runs'].append(record)
        print(json.dumps({k: record[k] for k in ('candidate', 'fixture', 'exit', 'stderr', 'input_bytes_unchanged', 'report_created')}))
        if record['report_created']:
            print(json.dumps({'lines': [{k: line[k] for k in ('sku', 'status', 'final', 'gaps')} for line in record['lines']],
                              'report_issues': record['report_issues']}))
assert source.read_bytes() == original_bytes
(RUN / 'probe-log.json').write_text(json.dumps(log, indent=2) + '\n')
print('Probe log:', RUN / 'probe-log.json')
