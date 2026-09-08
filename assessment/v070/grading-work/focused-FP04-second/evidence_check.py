from pathlib import Path
import ast
import hashlib
import json
import re
import shutil
import sqlite3

PACKET = Path('/workspace/scratch/a75c3a6d9076/alps-v070-assessment/blind-focused/FP04')
WORK = Path('/workspace/scratch/a75c3a6d9076/alps-v070-assessment/grading-work/focused-FP04-second')

def emit(kind, **data):
    print(json.dumps({'kind': kind, **data}, sort_keys=True))

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def aggregate(records, start, end):
    result = {}
    for row in records:
        if row['status'] != 'settled' or not start <= row['posted_on'] <= end:
            continue
        value = result.setdefault(row['vendor_id'], [0, 0, 0, 0])
        value[0 if row['kind'] == 'charge' else 1] += row['amount_cents']
        value[2] = value[0] - value[1]
        value[3] += 1
    return {k: result[k] for k in sorted(result)}

def vendor_rows(rows):
    return {r['vendor_id']: [r.get('settled_charge_cents', r.get('charge_cents')),
                            r.get('settled_credit_cents', r.get('credit_cents')),
                            r['net_cents'], r['qualifying_entry_count']] for r in rows}

fixtures = {kind: json.loads((PACKET/'original-consumer-inputs'/kind/'fixture.json').read_text())['records']
            for kind in ('ordinary', 'challenging')}
api_original = (PACKET/'original-creator-input/ledger_api.py').read_bytes()
expected_cursors = {'ordinary': [None, 'p_de1636bae17d3ae33cda4377d6e42ee3'],
                    'challenging': [None, 'p_824dd208571a05a7d57ff5bd0e4889c0']}
expected_next = {'ordinary': None, 'challenging': 'p_b62d3333e930f1830dd2d61eb80d3bbc'}
expected_snapshot = {'ordinary': 'snap_c22e71aa06b43ab25395e0ce',
                     'challenging': 'snap_fb322d1120ca406ad668bc26'}

for label in ('R17', 'R28', 'R44', 'R63'):
    package = next((PACKET/label/'package').iterdir())
    package_files = [f for f in package.rglob('*') if f.is_file()]
    links = 0
    for f in package_files:
        if f.suffix == '.py':
            ast.parse(f.read_text())
        if f.suffix == '.md':
            for target in re.findall(r'\]\(([^)]+)\)', f.read_text()):
                if '://' not in target:
                    assert (f.parent/target.split('#')[0]).is_file(), (f, target)
                    links += 1
    emit('static_package', label=label, file_count=len(package_files), local_links=links,
         python_ast='pass', no_runner_executed=True)
    for kind in ('ordinary', 'challenging'):
        app = PACKET/label/kind
        prepared = label == 'R63' and kind == 'ordinary'
        copy_root = app/('prepared-skill' if prepared else 'observed-final-skill')/package.name
        assert sorted(str(f.relative_to(copy_root)) for f in copy_root.rglob('*') if f.is_file()) == sorted(str(f.relative_to(package)) for f in package_files)
        assert all((copy_root/f.relative_to(package)).read_bytes() == f.read_bytes() for f in package_files)
        input_dir = app/('prepared-input' if prepared else 'final-input-state')
        assert (input_dir/'ledger_api.py').read_bytes() == api_original
        setup = json.loads((app/'setup-observations.json').read_text())
        request = (input_dir/'request.md').read_text()
        expected_request = (PACKET/'original-consumer-inputs'/kind/'input/request.md').read_text()
        api_path = setup['calls'][0]['argv'][1]
        expected_request = expected_request.replace('{{STATE_PATH}}', setup['state_path']).replace('{{INPUT_DIR}}', str(Path(api_path).parent))
        assert request == expected_request
        emit('resource_comparison', label=label, application=kind,
             package_copy='prepared only' if prepared else 'observed final',
             skill_bytes='equal', api_bytes='equal', request='equal after supplied path substitution')

        all_sql = sorted((app/'committed-state').glob('*.sql')) + sorted((app/'committed-initial-state').glob('*.sql')) + sorted((app/'logical-state-supplement').glob('*.sql'))
        for f in all_sql:
            db = sqlite3.connect(':memory:')
            db.executescript(f.read_text())
            rows = [json.loads(row[0]) for row in db.execute('SELECT payload FROM records ORDER BY position')]
            state = db.execute('SELECT snapshot_id,tranche,calls_used FROM source_state').fetchone()
            db.close()
            assert rows == fixtures[kind]
            assert state[0] == expected_snapshot[kind] and state[1] == 1
            assert state[2] == (2 if 'final' in f.name else 0)
            meta_path = f.with_suffix('.json')
            meta = json.loads(meta_path.read_text()) if meta_path.is_file() else None
            if meta is not None:
                assert meta['sql_sha256'] == digest(f)
            emit('retained_source_sql', path=str(f.relative_to(PACKET)), snapshot=state[0], tranche=state[1],
                 calls_used=state[2], records_match_fixture=True, sha256=digest(f), retained_metadata=meta)

        binding_path = app/'recovery-binding.json'
        binding = json.loads(binding_path.read_text()) if binding_path.is_file() else None
        state_path = binding['restored_state_path'] if binding else setup['state_path']
        if binding:
            assert binding['restored_sql_sha256'] == digest(app/'committed-state/restored-initial.sql')
        start, end = ('2026-04-03', '2026-04-09') if kind == 'ordinary' else ('2026-06-10', '2026-06-18')
        expected_totals = aggregate(fixtures[kind][:6], start, end)
        if prepared:
            note = (app/'recovered-public-text/execution-note.md').read_text()
            output = json.loads(re.findall(r'```json\s*(.*?)\s*```', note, re.S)[0])
            assert output['complete'] is True
            assert output['examined_records'] == output['total_records'] == 6
            assert output['committed_pages'] == 2
            assert output['snapshot_id'] == expected_snapshot[kind]
            assert vendor_rows(output['vendors']) == expected_totals
            matched_source = app/'recovery-provenance/matched-sql-source.sql'
            assert matched_source.read_bytes() == (app/'logical-state-supplement/matched-final-state.sql').read_bytes()
            emit('recovered_stdout_only', label=label, application=kind, arithmetic=expected_totals,
                 checkpoint_available=False, terminal_cursor_independently_inspected=False)
            continue

        if label == 'R17':
            cp = json.loads((app/'work-evidence/request.json').read_text())
            entries, cursors, complete = cp['records'], cp['page_cursors'], cp['exhausted']
            assert cp['state'] == state_path and cp['api'] == api_path
            assert cp['start'] == start and cp['end'] == end
            assert aggregate(entries, start, end) == expected_totals
        elif label == 'R28':
            file = app/('work-evidence/checkpoint/job.json' if kind == 'ordinary' else 'work-evidence/checkpoints/job.json')
            cp = json.loads(file.read_text())
            entries = cp['seen_entry_ids']
            cursors, complete = cp['consumed_cursors'], cp['complete']
            assert cp['source'] == state_path and cp['api'] == api_path
            assert cp['start'] == start and cp['end'] == end
            values = {k: [v['charge_cents'], v['credit_cents'], v['charge_cents']-v['credit_cents'], v['qualifying_entry_count']] for k,v in cp['vendors'].items()}
            assert values == expected_totals
        elif label == 'R44':
            file = next((app/'work-evidence').glob('*.json'))
            cp = json.loads(file.read_text())
            entries, cursors, complete = cp['entries'], cp['cursors'], cp['complete']
            assert cp['request'] == {'api':api_path, 'state':state_path, 'start':start, 'end':end}
            assert aggregate(entries, start, end) == expected_totals
        else:
            original = app/'work-evidence/rollup-checkpoint.sqlite'
            copy = WORK/'R63-challenging-checkpoint-copy.sqlite'
            shutil.copyfile(original, copy)
            db = sqlite3.connect(copy.as_uri()+'?mode=ro', uri=True)
            cp = json.loads(db.execute('SELECT payload FROM state WHERE id=1').fetchone()[0])
            entries = [r[0] for r in db.execute('SELECT entry_id FROM entries ORDER BY rowid')]
            cursors = [json.loads(r[0]) for r in db.execute('SELECT cursor FROM pages ORDER BY rowid')]
            values = {r[0]: [int(r[1]),int(r[2]),int(r[1])-int(r[2]),r[3]] for r in db.execute('SELECT * FROM vendors ORDER BY vendor_id')}
            db.close()
            complete = cp['complete']
            assert cp['source'] == state_path and cp['api'] == api_path
            assert cp['start'] == start and cp['end'] == end
            assert values == expected_totals
            assert original.read_bytes() == copy.read_bytes()
        ids = [r['entry_id'] if isinstance(r,dict) else r for r in entries]
        assert ids == [r['entry_id'] for r in fixtures[kind][:6]]
        if entries and isinstance(entries[0], dict):
            assert entries == fixtures[kind][:6]
        assert cursors == expected_cursors[kind]
        assert cp['next_cursor'] == expected_next[kind]
        assert complete == (kind == 'ordinary')
        assert cp.get('snapshot_id', cp.get('snapshot')) == expected_snapshot[kind]
        assert cp.get('total_records', cp.get('total')) == len(fixtures[kind])
        emit('checkpoint_evidence', label=label, application=kind, source_binding=state_path,
             snapshot=expected_snapshot[kind], interval=[start,end], complete=complete,
             ids=ids, incorporated_cursors=cursors, next_cursor=cp['next_cursor'], arithmetic=expected_totals)
        if label in ('R17','R28'):
            report_file = (app/'work-evidence/result.json') if label == 'R17' else app/('work-evidence/report/report.json' if kind == 'ordinary' else 'work-evidence/reports/report.json')
            result = json.loads(report_file.read_text())
            assert vendor_rows(result.get('vendors', result.get('partial_vendors'))) == expected_totals
            emit('report_arithmetic', path=str(report_file.relative_to(PACKET)), result='match')

emit('finished', result='all retained-evidence assertions passed', source_api_calls=0, runner_invocations=0)
