"""Read-only FP04 evidence checks; no target runner or source API execution."""
from pathlib import Path
import ast
import hashlib
import json
import re
import shutil
import sqlite3

ROOT = Path('/workspace/scratch/a75c3a6d9076/alps-v070-assessment/blind-focused/FP04')
WORK = Path(__file__).resolve().parent
NAMES = {'R17': 'rollup-reimbursements', 'R28': 'reimbursement-ledger-rollup',
         'R44': 'reimbursement-rollup', 'R63': 'reimbursement-ledger-rollup'}
out = {'scope': 'Packet bytes and logical evidence only; no application replay or target runtime check',
       'packages': [], 'applications': [], 'sql': []}

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def aggregate(rows, start, end):
    totals = {}
    for row in rows:
        if row['status'] == 'settled' and start <= row['posted_on'] <= end:
            values = totals.setdefault(row['vendor_id'], [0, 0, 0, 0])
            k = 0 if row['kind'] == 'charge' else 1
            values[k] += row['amount_cents']
            values[2] += row['amount_cents'] * (1 if k == 0 else -1)
            values[3] += 1
    return dict(sorted(totals.items()))

api_bytes = (ROOT / 'original-creator-input/ledger_api.py').read_bytes()
for label, name in NAMES.items():
    package = ROOT / label / 'package' / name
    package_files = sorted(p for p in package.rglob('*') if p.is_file())
    for p in package_files:
        if p.suffix == '.py':
            ast.parse(p.read_text())
    out['packages'].append({'label': label, 'python_parse': 'pass',
        'files_read': [str(p.relative_to(ROOT)) for p in package_files]})
    for case in ('ordinary', 'challenging'):
        base = ROOT / label / case
        recovered = label == 'R63' and case == 'ordinary'
        skill = base / ('prepared-skill' if recovered else 'observed-final-skill') / name
        copied = sorted(p for p in skill.rglob('*') if p.is_file())
        assert {p.relative_to(skill) for p in copied} == {p.relative_to(package) for p in package_files}
        differences = [str(p.relative_to(skill)) for p in copied
                       if p.read_bytes() != (package / p.relative_to(skill)).read_bytes()]
        inputs = base / ('prepared-input' if recovered else 'final-input-state')
        assert (inputs / 'ledger_api.py').read_bytes() == api_bytes
        request = (inputs / 'request.md').read_text()
        original = (ROOT / 'original-consumer-inputs' / case / 'input/request.md').read_text()
        state = re.search(r'The initialized source is `([^`]+)`', request).group(1)
        api_path = re.search(r'its supplied API is `([^`]+)`', request).group(1)
        expected = original.replace('{{STATE_PATH}}', state).replace('{{INPUT_DIR}}/ledger_api.py', api_path)
        assert request == expected
        locks = [{ 'path': str(p.relative_to(ROOT)), 'bytes': p.stat().st_size }
                 for p in base.rglob('*.lock')]
        out['applications'].append({'label': label, 'case': case,
            'resource_scope': 'prepared, not final' if recovered else 'observed-final',
            'skill_byte_differences_from_package': differences,
            'api_equals_original': True, 'request_equals_original_after_path_substitution': True,
            'locks': locks})

for sql in sorted(ROOT.rglob('*.sql')):
    body = sql.read_text()
    match = re.search(r'INSERT INTO "source_state" VALUES\(1,\'(snap_[^\']+)\',(\d+),(\d+)\);', body)
    assert match is not None, sql
    records = [(int(pos), json.loads(payload.replace("''", "'")))
               for pos, payload in re.findall(r'INSERT INTO "records" VALUES\((\d+),\'(.*)\'\);', body)]
    records.sort()
    case = 'ordinary' if 'ordinary' in sql.parts else 'challenging'
    fixture = json.loads((ROOT / 'original-consumer-inputs' / case / 'fixture.json').read_text())['records']
    assert [pos for pos, _ in records] == list(range(len(fixture)))
    assert [row for _, row in records] == fixture
    meta = sql.with_suffix('.json')
    metadata_hash_matches = None
    if meta.is_file():
        metadata_hash_matches = json.loads(meta.read_text())['sql_sha256'] == digest(sql)
        assert metadata_hash_matches
    out['sql'].append({'path': str(sql.relative_to(ROOT)), 'sha256': digest(sql),
        'snapshot': match.group(1), 'tranche': int(match.group(2)), 'calls_used': int(match.group(3)),
        'records_equal_original_fixture': True, 'metadata_hash_matches': metadata_hash_matches})

out['arithmetic'] = {}
for case, start, end in [('ordinary','2026-04-03','2026-04-09'),
                         ('challenging','2026-06-10','2026-06-18')]:
    records = json.loads((ROOT / 'original-consumer-inputs' / case / 'fixture.json').read_text())['records']
    out['arithmetic'][case] = {'tuple_order': ['charges', 'credits', 'net', 'count'],
                              'first_six': aggregate(records[:6], start, end),
                              'all_reference_only': aggregate(records, start, end)}

source = ROOT / 'R63/challenging/work-evidence/rollup-checkpoint.sqlite'
copy = WORK / 'R63-challenging-checkpoint-copy.sqlite'
shutil.copyfile(source, copy)
before = digest(source)
db = sqlite3.connect(copy.as_uri() + '?mode=ro&immutable=1', uri=True)
try:
    tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert tables == {'state', 'entries', 'pages', 'vendors'}
    out['r63_challenging_checkpoint'] = {
        'copy_sha256_matches': before == digest(copy),
        'state': json.loads(db.execute('SELECT payload FROM state WHERE id=1').fetchone()[0]),
        'incorporated_ids': [r[0] for r in db.execute('SELECT entry_id FROM entries ORDER BY rowid')],
        'consumed_cursors': [json.loads(r[0]) for r in db.execute('SELECT cursor FROM pages ORDER BY rowid')],
        'vendors': [list(r) for r in db.execute('SELECT * FROM vendors ORDER BY vendor_id')]}
finally:
    db.close()
assert before == digest(source)
out['r63_ordinary_supplement_matches_historical_digest'] = (
    digest(ROOT / 'R63/ordinary/logical-state-supplement/matched-final-state.sql') ==
    '0c59cdc1f01c69cb8dc8899d6565287e22fc0469988613be1a04c379594ca580')
(WORK / 'audit-results.json').write_text(json.dumps(out, indent=2) + '\n')
print(json.dumps(out, indent=2))
