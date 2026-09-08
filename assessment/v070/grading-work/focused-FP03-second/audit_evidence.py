from pathlib import Path
import ast
import hashlib
import json
import re

BASE = Path('/workspace/scratch/a75c3a6d9076/alps-v070-assessment/blind-focused/FP03')
WORK = Path('/workspace/scratch/a75c3a6d9076/alps-v070-assessment/grading-work/focused-FP03-second')
LABELS = {'R17': 'complete-reimbursement-rollup', 'R28': 'reimbursement-ledger-rollup', 'R44': 'complete-reimbursement-rollup', 'R63': 'reimbursement-ledger-rollup'}
observations = []
for label, skill_name in LABELS.items():
    package = BASE / label / 'package' / skill_name
    package_files = sorted(p for p in package.rglob('*') if p.is_file())
    for p in package_files:
        if p.suffix == '.py':
            ast.parse(p.read_text())
    for case in ('ordinary', 'challenging'):
        app = BASE / label / case
        recovered = label in ('R17', 'R28')
        skill_copy = app / ('prepared-skill' if recovered else 'observed-final-skill') / skill_name
        assert {p.relative_to(package) for p in package_files} == {p.relative_to(skill_copy) for p in skill_copy.rglob('*') if p.is_file()}
        for p in package_files:
            q = skill_copy / p.relative_to(package)
            assert p.read_bytes() == q.read_bytes(), (label, case, p)
        input_dir = app / ('prepared-input' if recovered else 'final-input-state')
        assert (input_dir / 'ledger_api.py').read_bytes() == (BASE / 'original-creator-input/ledger_api.py').read_bytes()
        setup = json.loads((app / 'setup-observations.json').read_text())
        req = (input_dir / 'request.md').read_text()
        api_original_path = setup['calls'][0]['argv'][1]
        expected_req = (BASE / 'original-consumer-inputs' / case / 'input/request.md').read_text().replace('{{STATE_PATH}}', setup['state_path']).replace('{{INPUT_DIR}}', str(Path(api_original_path).parent))
        assert req == expected_req
        if recovered:
            initial = app / 'committed-initial-state/initial.sql'
            final = app / 'logical-state-supplement/matched-final-state.sql'
            assert final.read_bytes() == (app / 'recovery-provenance/matched-sql-source.sql').read_bytes()
        else:
            initial = app / 'committed-state/initial.sql'
            final = app / 'committed-state/final.sql'
        before = initial.read_text()
        after = final.read_text()
        state_pattern = r'INSERT INTO "source_state" VALUES\(1,\'(snap_[a-f0-9]+)\',(\d+),(\d+)\);'
        si = re.search(state_pattern, before)
        sf = re.search(state_pattern, after)
        assert si and sf
        assert si.group(1) == sf.group(1)
        assert si.groups()[1:] == ('1', '0') and sf.groups()[1:] == ('1', '2')
        assert re.sub(state_pattern, '', before) == re.sub(state_pattern, '', after)
        records = [json.loads(m.group(1)) for m in re.finditer(r'INSERT INTO "records" VALUES\(\d+,\'(.*)\'\);', before)]
        fixture = json.loads((BASE / 'original-consumer-inputs' / case / 'fixture.json').read_text())['records']
        assert records == fixture
        meta_dir = 'committed-initial-state' if recovered else 'committed-state'
        im = json.loads((app / meta_dir / 'initial.json').read_text())
        assert hashlib.sha256(initial.read_bytes()).hexdigest() == im['sql_sha256']
        if not recovered:
            fm = json.loads((app / 'committed-state/final.json').read_text())
            assert hashlib.sha256(final.read_bytes()).hexdigest() == fm['sql_sha256']
        if label == 'R17':
            cp = app / ('original-work-evidence/reimbursement-2026-04-03_2026-04-09.checkpoint.json' if case == 'ordinary' else 'recovered-work-evidence/checkpoint-rendering.json')
        elif label == 'R28':
            cp = app / 'recovered-work-evidence/checkpoint-rendering.json'
        else:
            cps = list((app / 'work-evidence').glob('*checkpoint.json')) if label == 'R44' or case == 'challenging' else list((app / 'work-evidence').glob('*.json'))
            assert len(cps) == 1
            cp = cps[0]
        checkpoint = json.loads(cp.read_text())
        identity = checkpoint['request']
        assert identity['source_state'] == setup['state_path']
        assert identity['api'] == api_original_path
        start, end = ('2026-04-03', '2026-04-09') if case == 'ordinary' else ('2026-06-10', '2026-06-18')
        assert identity.get('start', identity.get('start_date')) == start
        assert identity.get('end', identity.get('end_date')) == end
        expected = {}
        incorporated = fixture[:6]
        for item in incorporated:
            if item['status'] == 'settled' and start <= item['posted_on'] <= end:
                row = expected.setdefault(item['vendor_id'], [0, 0, 0])
                row[0 if item['kind'] == 'charge' else 1] += item['amount_cents']
                row[2] += 1
        if label == 'R17':
            rows = checkpoint['vendors']
            actual = {v: [a['settled_charge_cents'], a['settled_credit_cents'], a['qualifying_entry_count']] for v, a in rows.items()}
            ids = checkpoint['seen_entry_ids']
            cursor = checkpoint['next_cursor']
            complete = checkpoint['status'] == 'complete'
            snapshot = checkpoint['snapshot_id']
            assert checkpoint['pages_processed'] == 2 and checkpoint['records_examined'] == 6
        elif label == 'R28':
            actual = {v: [a['charges'], a['credits'], a['count']] for v, a in checkpoint['aggregates'].items()}
            ids = checkpoint['seen_entry_ids']
            cursor = checkpoint['next_cursor']
            complete = checkpoint['complete']
            snapshot = identity['snapshot_id']
            assert checkpoint['pages_incorporated'] == 2
        elif label == 'R44':
            actual = {v: [a['charge'], a['credit'], a['count']] for v, a in checkpoint['aggregates'].items()}
            ids = checkpoint['progress']['seen_entry_ids']
            cursor = checkpoint['progress']['next_cursor']
            complete = checkpoint['progress']['complete']
            snapshot = checkpoint['source']['snapshot_id']
            assert checkpoint['progress']['processed_records'] == 6
        else:
            actual = {v: [a['settled_charge_cents'], a['settled_credit_cents'], a['qualifying_entry_count']] for v, a in checkpoint['aggregates'].items()}
            ids = sorted(checkpoint['entries'])
            cursor = checkpoint['cursor']
            complete = checkpoint['phase'] == 'complete'
            snapshot = checkpoint['snapshot_id']
            assert checkpoint['pages_processed'] == 2
            expected_second_cursor = 'p_de1636bae17d3ae33cda4377d6e42ee3' if case == 'ordinary' else 'p_824dd208571a05a7d57ff5bd0e4889c0'
            assert checkpoint['processed_cursors'] == [None, expected_second_cursor]
            for item in incorporated:
                digest = hashlib.sha256(json.dumps(item, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
                assert checkpoint['entries'][item['entry_id']] == digest
        assert actual == expected
        assert ids == [item['entry_id'] for item in incorporated]
        assert snapshot == si.group(1)
        assert complete == (case == 'ordinary')
        assert cursor == (None if case == 'ordinary' else 'p_b62d3333e930f1830dd2d61eb80d3bbc')
        observations.append({'package': label, 'case': case, 'package_copy_byte_equal': True, 'api_byte_equal': True, 'request_matches_original_substitution': True, 'record_payloads_unchanged': True, 'tranche': 1, 'calls_used_before': 0, 'calls_used_after': 2, 'checkpoint_source_binding': True, 'checkpoint_ids': ids, 'checkpoint_cursor': cursor, 'checkpoint_aggregates_match_incorporated_fixture_prefix': True, 'evidence_kind': 'recovered/original evidence plus matched SQL supplement' if recovered else 'committed final evidence'})

result = {'scope': 'Read-only packet verification; no API calls, consumer replay, source-state reconstruction, or live-state access.', 'script_ast_parse': 'all four passed', 'applications': observations}
(WORK / 'audit-results.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'applications_checked': len(observations), 'package_copies_byte_equal': 8, 'api_copies_byte_equal': 8, 'request_substitutions_match': 8, 'sql_record_payloads_unchanged': 8, 'sql_tranche_1_calls_used_0_to_2': 8, 'checkpoint_binding_frontier_arithmetic_match': 8, 'script_ast_parse_passed': 4}, sort_keys=True))
