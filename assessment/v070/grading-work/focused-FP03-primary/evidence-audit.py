"""Read-only packet checks; never follow original embedded source paths."""
import ast
import hashlib
import json
from pathlib import Path
import re

ROOT = Path('/workspace/scratch/a75c3a6d9076/alps-v070-assessment/blind-focused/FP03')
OUT = Path('/workspace/scratch/a75c3a6d9076/alps-v070-assessment/grading-work/focused-FP03-primary/evidence-audit.json')

def readj(path):
    return json.loads(path.read_text())

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def totals(rows, start, end):
    result = {}
    for row in rows:
        if row['status'] == 'settled' and start <= row['posted_on'] <= end:
            a = result.setdefault(row['vendor_id'], [0, 0, 0, 0])
            a[row['kind'] == 'credit'] += row['amount_cents']
            a[3] += 1
    for a in result.values():
        a[2] = a[0] - a[1]
    return dict(sorted(result.items()))

cases = {
    'ordinary': ('2026-04-03', '2026-04-09', 'snap_c22e71aa06b43ab25395e0ce'),
    'challenging': ('2026-06-10', '2026-06-18', 'snap_fb322d1120ca406ad668bc26'),
}
records = {case: readj(ROOT / 'original-consumer-inputs' / case / 'fixture.json')['records'] for case in cases}
report = {'scope': 'Packet-only static and arithmetic checks; no source API or target helper executed.', 'applications': [], 'packages': []}
for label in ['R17', 'R28', 'R44', 'R63']:
    package = next((ROOT / label / 'package').iterdir())
    package_files = [p for p in package.rglob('*') if p.is_file()]
    for p in package_files:
        if p.suffix == '.py':
            ast.parse(p.read_text())
    report['packages'].append({'label': label, 'files': len(package_files), 'python_ast_parse': 'pass'})
    for case, (start, end, snapshot) in cases.items():
        base = ROOT / label / case
        recovery = label in ['R17', 'R28']
        skillbase = base / ('prepared-skill' if recovery else 'observed-final-skill') / package.name
        skill_equal = all((skillbase / p.relative_to(package)).read_bytes() == p.read_bytes() for p in package_files)
        assert skill_equal
        inputbase = base / ('prepared-input' if recovery else 'final-input-state')
        assert (inputbase / 'ledger_api.py').read_bytes() == (ROOT / 'original-creator-input/ledger_api.py').read_bytes()
        setup = readj(base / 'setup-observations.json')
        desc = json.loads(setup['calls'][1]['stdout'])
        assert desc == {'calls_per_tranche': 2, 'page_size': 3, 'remaining_calls': 2, 'snapshot_id': snapshot, 'total_records': len(records[case]), 'tranche': 1}
        inputdir = str(Path(setup['calls'][0]['argv'][1]).parent)
        expected_request = (ROOT / 'original-consumer-inputs' / case / 'input/request.md').read_text().replace('{{STATE_PATH}}', setup['state_path']).replace('{{INPUT_DIR}}', inputdir)
        assert (inputbase / 'request.md').read_text() == expected_request
        statedir = base / ('committed-initial-state' if recovery else 'committed-state')
        initial_meta = readj(statedir / 'initial.json')
        initial = (statedir / 'initial.sql').read_text()
        assert sha(statedir / 'initial.sql') == initial_meta['sql_sha256']
        finalpath = base / ('logical-state-supplement/matched-final-state.sql' if recovery else 'committed-state/final.sql')
        final = finalpath.read_text()
        initial_state = re.findall(r'INSERT INTO "source_state" VALUES\((.*)\);', initial)
        final_state = re.findall(r'INSERT INTO "source_state" VALUES\((.*)\);', final)
        assert initial_state == [f"1,'{snapshot}',1,0"]
        assert final_state == [f"1,'{snapshot}',1,2"]
        assert initial.replace(initial_state[0], final_state[0]) == final
        sql_rows = re.findall(r'INSERT INTO "records" VALUES\(\d+,\'(.*)\'\);', final)
        assert [json.loads(s.replace("''", "'")) for s in sql_rows] == records[case]
        if recovery:
            provenance = readj(base / 'recovery-provenance.json')
            for item in provenance['files']:
                local = base / item['destination']
                assert local.is_relative_to(base)
                assert sha(local) == item['sha256']
            assert (base / 'recovery-provenance/matched-sql-source.sql').read_bytes() == finalpath.read_bytes()
            work = base / ('original-work-evidence' if label == 'R17' and case == 'ordinary' else 'recovered-work-evidence')
            cp_path = next(work.glob('*.json'))
            resource = 'final inventory unavailable'
        else:
            finalmeta = readj(base / 'committed-state/final.json')
            assert sha(finalpath) == finalmeta['sql_sha256']
            observations = readj(base / 'resource-observations.json')
            assert observations['changed_originals'] == [] and observations['added_resources_sha256'] == {}
            work = base / 'work-evidence'
            cp_path = next(p for p in work.glob('*.json') if 'checkpoint' in p.name or (label == 'R63' and case == 'ordinary'))
            resource = 'recorded originals unchanged'
        cp = readj(cp_path)
        assert cp['request']['source_state'] == setup['state_path']
        assert cp['request']['api'] == inputdir + '/ledger_api.py'
        assert cp['request'].get('start', cp['request'].get('start_date')) == start
        assert cp['request'].get('end', cp['request'].get('end_date')) == end
        if label == 'R17':
            ids = cp['seen_entry_ids']; cursor = cp['next_cursor']; complete = cp['status'] == 'complete'
            assert cp['snapshot_id'] == snapshot and cp['pages_processed'] == 2
            agg = {v: [a['settled_charge_cents'], a['settled_credit_cents'], a['settled_charge_cents']-a['settled_credit_cents'], a['qualifying_entry_count']] for v, a in cp['vendors'].items()}
        elif label == 'R28':
            ids = cp['seen_entry_ids']; cursor = cp['next_cursor']; complete = cp['complete']
            assert cp['request']['snapshot_id'] == snapshot and cp['pages_incorporated'] == 2
            agg = {v: [a['charges'], a['credits'], a['charges']-a['credits'], a['count']] for v, a in cp['aggregates'].items()}
        elif label == 'R44':
            ids = cp['progress']['seen_entry_ids']; cursor = cp['progress']['next_cursor']; complete = cp['progress']['complete']
            assert cp['source']['snapshot_id'] == snapshot and cp['progress']['last_tranche'] == 1
            agg = {v: [a['charge'], a['credit'], a['charge']-a['credit'], a['count']] for v, a in cp['aggregates'].items()}
        else:
            ids = list(cp['entries']); cursor = cp['cursor']; complete = cp['phase'] == 'complete'
            assert cp['snapshot_id'] == snapshot and cp['pages_processed'] == 2
            for row in records[case][:6]:
                digest = hashlib.sha256(json.dumps(row, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
                assert cp['entries'][row['entry_id']] == digest
            agg = {v: [a['settled_charge_cents'], a['settled_credit_cents'], a['settled_charge_cents']-a['settled_credit_cents'], a['qualifying_entry_count']] for v, a in cp['aggregates'].items()}
        assert ids == [r['entry_id'] for r in records[case][:6]]
        assert complete == (case == 'ordinary')
        assert cursor == (None if case == 'ordinary' else 'p_b62d3333e930f1830dd2d61eb80d3bbc')
        assert agg == totals(records[case][:6], start, end)
        report['applications'].append({'label': label, 'case': case, 'request_and_api_match': True, 'skill_copy_match': True, 'initial': {'tranche': 1, 'calls_used': 0}, 'final_logical': {'tranche': 1, 'calls_used': 2, 'unchanged_records': True, 'supplement_only': recovery}, 'resource_observation': resource, 'checkpoint': str(cp_path.relative_to(ROOT)), 'complete': complete, 'incorporated_records': len(ids), 'next_cursor': cursor, 'aggregate_matches_independent_prefix_arithmetic': True, 'aggregates_charge_credit_net_count': agg})
OUT.write_text(json.dumps(report, indent=2) + '\n')
print('PASS: 4 package Python parses; 8 assignment/API/Skill-copy, setup, SQL, checkpoint identity/frontier/arithmetic checks; 4 recovery provenance destination hashes; 4 recorded unchanged-resource observations.')
print('No target helper, source API, original live state, or embedded external path was executed or accessed.')
