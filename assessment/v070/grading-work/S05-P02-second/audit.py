"""Read only S05-P02; reproduce its supplied processors on disposable copies."""
import ast
import copy
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

PACKET = Path('/workspace/scratch/a75c3a6d9076/alps-v070-assessment/blind-business/S05-P02')
WORK = Path(__file__).resolve().parent
CANDIDATES = {
    'R17': ('review-monthly-receiving', 'review_receiving.py', 'review.json'),
    'R28': ('monthly-receiving-review', 'review_receiving.py', 'review.json'),
    'R44': ('monthly-receiving-review', 'review_receiving.py', 'review.json'),
    'R63': ('monthly-receiving-review', 'review.py', 'receipt-review.json'),
}
# Fixed expectations transcribed from this packet's independent business oracle.
# Tuple: observed usable subtotal, supported final net, supported position.
EXPECTED = {
    'ordinary': {
        'LABEL-60': (120, 120, 'received_as_ordered'),
        'CARTON-M': (42, 42, 'shortfall'),
        'GLOVE-N': (64, 64, 'excess'),
        'FILM-300': (24, 24, 'received_as_ordered'),
        'SEAL-BLUE': (30, None, 'unresolved'),
        'TAPE-48': (0, 0, 'shortfall'),
    },
    'challenging': {
        'BOLT-M8': (90, None, 'unresolved'),
        'WASHER-M8': (200, None, 'unresolved'),
        'PACK-RACK': (20, None, 'unresolved'),
        'STRAP-20': (60, 60, 'received_as_ordered'),
        'SHIELD-CLR': (28, None, 'unresolved'),
        'POUCH-12': (34, None, 'unresolved'),
        'TRAY-L': (9, None, 'unresolved'),
        'BINDER-B': (0, None, 'unresolved'),
        'INSERT-G': (75, 75, 'excess'),
        'WRAP-500': (18, 18, 'shortfall'),
        'CLIP-R': (10, 10, 'received_as_ordered'),
        'PAD-FOAM': (-4, -4, 'shortfall'),
        'CRATE-S': (0, 0, 'shortfall'),
    },
}

def inventory(root):
    result = {}
    for path in sorted(root.rglob('*')):
        assert not path.is_symlink(), str(path)
        if path.is_file():
            result[str(path.relative_to(root))] = {
                'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                'mode': oct(path.stat().st_mode & 0o777),
            }
    return result

def normalize(candidate, report):
    out = {}
    for line in report['lines']:
        if candidate == 'R17':
            observed = line['observed_net_received']
            final = observed if line['final_comparison_allowed'] else None
            status = line['disposition']
        elif candidate == 'R28':
            observed, final, status = (line['observed_subtotal'], line['final_net_received'], line['position'])
        elif candidate == 'R44':
            observed, final, status = (line['observed_net_received'], line['final_net_received'], line['receipt_position'])
        else:
            observed, final, status = (line['valid_event_subtotal'], line['final_net'], line['status'])
        if status in {'indeterminate', 'undetermined', 'incomplete_evidence', 'blocked_evidence'}:
            status = 'unresolved'
        out[line['sku']] = (observed, final, status)
    return out

results = {'python': sys.version.split()[0], 'packages': {}, 'applications': {}, 'commands': []}
for candidate, (folder, script, evidence_name) in CANDIDATES.items():
    package = PACKET / candidate / 'package' / folder
    package_inventory = inventory(package)
    skill_text = (package / 'SKILL.md').read_text()
    front = skill_text.split('---', 2)[1]
    fields = dict(line.split(': ', 1) for line in front.strip().splitlines())
    assert fields['name'] == folder
    assert re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*', fields['name'])
    assert 1 <= len(fields['name']) <= 64 and 0 < len(fields['description']) <= 1024
    links = re.findall(r'\]\(([^)]+)\)', skill_text)
    assert all((package / link).is_file() for link in links)
    for path in package.rglob('*.py'):
        ast.parse(path.read_text(), filename=str(path))
    copied_package = WORK / 'component-copies' / candidate / 'skill' / folder
    shutil.copytree(package, copied_package)
    results['packages'][candidate] = {'files': len(package_inventory), 'selected_format_link_syntax_check': 'pass'}
    for variant in EXPECTED:
        original = PACKET / 'original-consumer-inputs' / variant / 'input'
        final_input = PACKET / candidate / variant / 'final-input-state'
        original_json = original / 'receiving.json'
        final_json = final_input / 'receiving.json'
        source = json.loads(original_json.read_text())
        assert original_json.read_bytes() == final_json.read_bytes()
        assert original_json.stat().st_mode & 0o777 == final_json.stat().st_mode & 0o777
        request = (final_input / 'request.md').read_text()
        normalized_request = re.sub(r'/workspace/[^`\s]+/input/receiving\.json', '{{INPUT_DIR}}/receiving.json', request)
        assert normalized_request == (original / 'request.md').read_text()
        observed_inventory = inventory(PACKET / candidate / variant / 'observed-final-skill' / folder)
        assert package_inventory == observed_inventory
        recorded = json.loads((PACKET / candidate / variant / 'work-evidence' / evidence_name).read_text())
        assert normalize(candidate, recorded) == EXPECTED[variant]
        source_keys = {(line['order_id'], line['sku']) for line in source['orders']}
        assert source_keys == {(line['order_id'], line['sku']) for line in recorded['lines']}
        copied_input = WORK / 'component-copies' / candidate / variant / 'input'
        shutil.copytree(original, copied_input)
        output = copied_input.parent / 'report.json'
        command = ['python3', '-B', 'scripts/' + script]
        if candidate == 'R63':
            command.append('--input')
        command.extend([str(copied_input / 'receiving.json'), '--output', str(output)])
        proc = subprocess.run(command, cwd=copied_package, text=True, capture_output=True)
        results['commands'].append({'candidate': candidate, 'variant': variant, 'cwd': str(copied_package), 'argv': command, 'exit': proc.returncode, 'stdout': proc.stdout, 'stderr': proc.stderr})
        assert proc.returncode == 0, proc.stderr
        reproduced = json.loads(output.read_text())
        assert normalize(candidate, reproduced) == EXPECTED[variant]
        if candidate == 'R63':
            reproduced = copy.deepcopy(reproduced)
            reproduced['source'] = recorded['source']
        assert reproduced == recorded
        assert (copied_input / 'receiving.json').read_bytes() == original_json.read_bytes()
        resource = json.loads((PACKET / candidate / variant / 'resource-observations.json').read_text())
        assert resource['changed_originals'] == [] and resource['added_resources_sha256'] == {}
        results['applications'][candidate + '/' + variant] = {
            'source_json_bytes_modes': 'unchanged',
            'request': 'identical after expected input-path substitution',
            'package_vs_observed_final_bytes_modes': 'identical',
            'line_scope_and_oracle_quantity_status_tuples': 'pass',
            'reproduced_report_equals_recorded': 'pass (source path normalized for R63 only)',
            'normalized_lines': normalize(candidate, recorded),
        }
        print(f'{candidate}/{variant}: copied CLI exit 0; {len(recorded["lines"])} lines match oracle; recorded report reproduced; originals/Skill preserved')

test_cwd = WORK / 'component-copies' / 'R63' / 'skill' / 'monthly-receiving-review'
test_command = ['python3', '-B', '-m', 'unittest', 'discover', '-s', 'tests', '-v']
proc = subprocess.run(test_command, cwd=test_cwd, capture_output=True, text=True)
results['commands'].append({'candidate': 'R63', 'kind': 'supplied component tests', 'cwd': str(test_cwd), 'argv': test_command, 'exit': proc.returncode, 'stdout': proc.stdout, 'stderr': proc.stderr})
assert proc.returncode == 0, proc.stderr
print('R63 copied supplied suite: exit 0; ' + ' / '.join(proc.stderr.strip().splitlines()[-3:]))
print('Selected package format/link/AST checks: 4/4 pass; Python ' + results['python'])
(WORK / 'audit-results.json').write_text(json.dumps(results, indent=2) + '\n')
