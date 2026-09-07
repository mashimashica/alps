"""Read-only comparison of the assigned frozen packet; no source API is invoked."""
from pathlib import Path
import ast
import hashlib
import json
import re

BASE=Path('/workspace/scratch/a75c3a6d9076/alps-v070-assessment/blind-business/S06-P02')
OUT=Path(__file__).resolve().parent/'recorded-evidence-review.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
results=[]
for candidate in ('R17','R28','R44','R63'):
    package=BASE/candidate/'package/reimbursement-ledger-rollup'
    for script in (package/'scripts').glob('*.py'):
        ast.parse(script.read_text())
    for variant in ('ordinary','challenging'):
        case=BASE/candidate/variant
        setup=json.loads((case/'setup-observations.json').read_text())
        template=(BASE/'original-consumer-inputs'/variant/'input/request.md').read_text()
        input_dir=str(Path(setup['calls'][0]['argv'][1]).parent)
        expected_request=template.replace('{{STATE_PATH}}',setup['state_path']).replace('{{INPUT_DIR}}',input_dir)
        observed=case/'observed-final-skill/reimbursement-ledger-rollup'
        inventory=lambda p:{str(f.relative_to(p)):{'sha256':sha(f),'mode':f.stat().st_mode&0o777} for f in p.rglob('*') if f.is_file()}
        original_rows=json.loads((BASE/'original-consumer-inputs'/variant/'fixture.json').read_text())['records']
        states={}
        for phase in ('initial','final'):
            path=case/'committed-state'/f'{phase}.sql'
            text=path.read_text()
            rows=[json.loads(m.group(2).replace("''","'")) for m in re.finditer(r'INSERT INTO "records" VALUES\((\d+),\'(.*)\'\);',text)]
            state_line=next(s for s in text.splitlines() if s.startswith('INSERT INTO "source_state"'))
            states[phase]={'state_line':state_line,'record_count':len(rows),'records_match_fixture':rows==original_rows,
                           'sql_hash_matches_metadata':sha(path)==json.loads(path.with_suffix('.json').read_text())['sql_sha256']}
        cp_path=next(p for p in (case/'work-evidence').glob('*.json') if p.name!='continuation-evidence.json')
        cp=json.loads(cp_path.read_text())
        totals=cp.get('totals',cp.get('vendors',cp.get('aggregates')))
        normalized={v:[t.get('charge_cents',t.get('charges')),t.get('credit_cents',t.get('credits')),
                       t.get('entry_count',t.get('count',t.get('qualifying_entry_count')))] for v,t in totals.items()}
        start,end=('2026-04-03','2026-04-09') if variant=='ordinary' else ('2026-06-10','2026-06-18')
        expected={}
        for row in original_rows if variant=='ordinary' else original_rows[:6]:
            if row['status']=='settled' and start<=row['posted_on']<=end:
                t=expected.setdefault(row['vendor_id'],[0,0,0])
                t[0 if row['kind']=='charge' else 1]+=row['amount_cents']
                t[2]+=1
        results.append({'candidate':candidate,'variant':variant,
                        'request_matches':(case/'final-input-state/request.md').read_text()==expected_request,
                        'api_matches_original':sha(case/'final-input-state/ledger_api.py')==sha(BASE/'original-creator-input/ledger_api.py'),
                        'package_bytes_and_modes_match_observed_final':inventory(package)==inventory(observed),
                        'states':states,'checkpoint':str(cp_path),'checkpoint_aggregates_match_expected':normalized==expected,
                        'normalized_charge_credit_count':normalized,
                        'cursor':cp.get('cursor',cp.get('next_cursor')),
                        'resource_observations':json.loads((case/'resource-observations.json').read_text())})
OUT.write_text(json.dumps({'scope':__doc__,'cases':results},indent=2,sort_keys=True)+'\n')
for r in results:
    print(json.dumps({k:r[k] for k in ('candidate','variant','request_matches','api_matches_original',
          'package_bytes_and_modes_match_observed_final','checkpoint_aggregates_match_expected','cursor')},sort_keys=True))
print(str(OUT))
