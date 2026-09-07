#!/usr/bin/env python3
"""Read-only packet inspection; no operational source access or component replay.

The sole SQLite file opened is an explicitly labelled disposable byte copy of
the captured workflow checkpoint. It is opened mode=ro with immutable=1.
"""
import ast
import hashlib
import json
from pathlib import Path
import re
import shutil
import sqlite3

PACKET = Path('/workspace/scratch/a75c3a6d9076/alps-v070-assessment/blind-business/S06-P03')
WORK = Path('/workspace/scratch/a75c3a6d9076/alps-v070-assessment/grading-work/S06-P03-primary')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def aggregate(records, start, end):
    totals = {}
    for row in records:
        if row['status'] != 'settled' or not start <= row['posted_on'] <= end:
            continue
        v = totals.setdefault(row['vendor_id'], dict(charges=0, credits=0, count=0))
        v['charges' if row['kind'] == 'charge' else 'credits'] += row['amount_cents']
        v['count'] += 1
    return [dict(vendor_id=k, **v, net=v['charges']-v['credits']) for k,v in sorted(totals.items())]

out = {'scope': __doc__, 'packages': {}, 'applications': {}, 'recovery_hashes': {}, 'oracle_arithmetic': {}}
original_api = sha(PACKET/'original-creator-input/ledger_api.py')
for candidate in ('R17','R28','R44','R63'):
    package = next((PACKET/candidate/'package').iterdir())
    skill = (package/'SKILL.md').read_text()
    frontmatter = re.match(r'^---\nname: ([^\n]+)\ndescription: ([^\n]+)\n---\n', skill)
    scripts = list((package/'scripts').glob('*.py'))
    for script in scripts:
        ast.parse(script.read_text())
    out['packages'][candidate] = {
        'frontmatter_basic_check': bool(frontmatter and frontmatter[1] == package.name),
        'syntax_ast_parse': 'pass',
        'file_hashes': {str(f.relative_to(package)):sha(f) for f in package.rglob('*') if f.is_file()},
    }
    for case in ('ordinary','challenging'):
        base = PACKET/candidate/case
        resdir = base/('observed-final-skill' if (base/'observed-final-skill').exists() else 'prepared-skill')/package.name
        resource_comparison = {
            str(f.relative_to(package)): {'bytes_equal': f.read_bytes() == (resdir/f.relative_to(package)).read_bytes(),
                                         'modes_equal': (f.stat().st_mode & 0o777) == ((resdir/f.relative_to(package)).stat().st_mode & 0o777)}
            for f in package.rglob('*') if f.is_file()
        }
        input_dir = base/('final-input-state' if (base/'final-input-state').exists() else 'prepared-input')
        setup = json.loads((base/'setup-observations.json').read_text())
        request = (input_dir/'request.md').read_text()
        expected = (PACKET/'original-consumer-inputs'/case/'input/request.md').read_text()
        # Strings from packet metadata are compared only; never followed.
        expected = expected.replace('{{STATE_PATH}}',setup['state_path'])
        prompt = (base/'prompt.md').read_text()
        supplied_api_match = re.search(r'`([^`]+/ledger_api\.py)`', request)
        expected = expected.replace('{{INPUT_DIR}}',supplied_api_match[1].rsplit('/',1)[0])
        initial_dir = base/('committed-state' if (base/'committed-state').exists() else 'committed-initial-state')
        initial = initial_dir/'initial.sql'
        final = base/'committed-state/final.sql'
        kind = 'actual final capture'
        if not final.exists():
            final = base/'logical-state-supplement/matched-final-state.sql'
            kind = 'historical digest matched supplement'
        initial_text = initial.read_text()
        initial_meta = json.loads((initial_dir/'initial.json').read_text())
        app = {
            'resource_class': resdir.parent.name,
            'resource_comparison_to_package': resource_comparison,
            'api_matches_original': sha(input_dir/'ledger_api.py') == original_api,
            'request_matches_fixed_case_after_literal_substitution': request == expected,
            'prompt_read_bytes': len(prompt.encode()),
            'source_binding_from_original_setup': setup['state_path'],
            'setup_calls': setup['calls'],
            'initial_sql_sha256_matches_metadata': sha(initial) == initial_meta['sql_sha256'],
            'initial_state_sql': re.findall(r'INSERT INTO "source_state".*', initial_text),
        }
        if final.exists():
            final_text = final.read_text()
            app.update(final_sql_class=kind, final_sql_sha256=sha(final),
                       final_state_sql=re.findall(r'INSERT INTO "source_state".*', final_text),
                       record_sql_unchanged=re.findall(r'INSERT INTO "records".*', initial_text)==re.findall(r'INSERT INTO "records".*', final_text))
        else:
            app['final_sql_class'] = 'unavailable; no inference from absence'
        if (base/'recovery-binding.json').exists():
            binding=json.loads((base/'recovery-binding.json').read_text())
            app['restored_path_binding']=binding
            app['restored_initial_sql_matches_original']=(initial_text==(base/'committed-state/restored-initial.sql').read_text())
        if (base/'resource-observations.json').exists():
            app['final_resource_observation']=json.loads((base/'resource-observations.json').read_text())
        cp = base/('work-evidence/rollup.json' if candidate=='R17' else 'recovered-work-evidence/checkpoint-rendering.json')
        if cp.exists():
            data=json.loads(cp.read_text())
            app['checkpoint_content']=data
            if 'entries' in data:
                app['checkpoint_recomputed_vendors']=aggregate(data['entries'].values(),data['start'],data['end'])
        if (base/'recovery-provenance.json').exists():
            provenance=json.loads((base/'recovery-provenance.json').read_text())
            out['recovery_hashes'][candidate+'/'+case]={x['destination']:sha(base/x['destination'])==x['sha256'] for x in provenance['files']}
        out['applications'][candidate+'/'+case]=app

for case, dates in [('ordinary',('2026-04-03','2026-04-09')), ('challenging',('2026-06-10','2026-06-18'))]:
    records=json.loads((PACKET/'original-consumer-inputs'/case/'fixture.json').read_text())['records']
    out['oracle_arithmetic'][case]={'full':aggregate(records,*dates),'first_six':aggregate(records[:6],*dates)}

source=PACKET/'R28/challenging/work-evidence/rollup-checkpoint.sqlite'
copied=WORK/'DISPOSABLE-CAPTURE-COPY-R28-challenging-checkpoint.sqlite'
shutil.copyfile(source,copied)
with sqlite3.connect(copied.as_uri()+'?mode=ro&immutable=1',uri=True) as db:
    checkpoint={
        'scope':'Captured workflow checkpoint copy, not source ledger; read-only inspection, no replay',
        'copy_sha256_matches':sha(source)==sha(copied),
        'state':json.loads(db.execute('SELECT payload FROM state WHERE id=1').fetchone()[0]),
        'page_input_cursors':[json.loads(row[0]) for row in db.execute('SELECT cursor FROM pages ORDER BY rowid')],
        'entry_ids':[row[0] for row in db.execute('SELECT entry_id FROM entries ORDER BY rowid')],
        'vendors':list(db.execute('SELECT vendor_id,charges,credits,count FROM vendors ORDER BY vendor_id')),
    }
out['R28_challenging_checkpoint_copy']=checkpoint

matched=PACKET/'R63/challenging/recovered-work-evidence/request-hash-matched.json'
rendering=PACKET/'R63/challenging/recovered-work-evidence/checkpoint-rendering.json'
out['R63_challenging_checkpoint_hash_match']={
    'sha256':sha(matched), 'bytes':matched.stat().st_size,
    'rendering_minus_one_lf':rendering.read_bytes()[:-1]==matched.read_bytes() and rendering.read_bytes().endswith(b'\n'),
    'same_logical_json':json.loads(matched.read_text())==json.loads(rendering.read_text()),
}
(WORK/'inspection-results.json').write_text(json.dumps(out,indent=2)+'\n')
summary={
    'packages':{k:{'frontmatter_basic_check':v['frontmatter_basic_check'],'syntax_ast_parse':v['syntax_ast_parse']} for k,v in out['packages'].items()},
    'applications':{k:{q:v[q] for q in ('resource_class','api_matches_original','request_matches_fixed_case_after_literal_substitution','initial_sql_sha256_matches_metadata','initial_state_sql','final_sql_class','final_state_sql','record_sql_unchanged') if q in v} for k,v in out['applications'].items()},
    'all_compared_skill_bytes_and_modes_equal':all(all(x['bytes_equal'] and x['modes_equal'] for x in a['resource_comparison_to_package'].values()) for a in out['applications'].values()),
    'all_recovery_manifest_file_hashes_match':all(all(x.values()) for x in out['recovery_hashes'].values()),
    'oracle_arithmetic':out['oracle_arithmetic'],
    'R28_challenging_checkpoint_copy':checkpoint,
    'R63_challenging_checkpoint_hash_match':out['R63_challenging_checkpoint_hash_match'],
}
print(json.dumps(summary,indent=2))
