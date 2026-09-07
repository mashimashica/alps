from pathlib import Path
import ast, hashlib, json, re

PACKET=Path('/workspace/scratch/a75c3a6d9076/alps-v070-assessment/blind-business/S06-P01')
WORK=Path('/workspace/scratch/a75c3a6d9076/alps-v070-assessment/grading-work/S06-P01-second')
result={'scope':'Read-only checks of assigned packet; no database connection, source call or application rerun',
        'packages':{},'applications':{}}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def totals(rows,start,end):
    out={}
    for row in rows:
        if row['status']=='settled' and start<=row['posted_on']<=end:
            v=out.setdefault(row['vendor_id'],[0,0,0])
            v[0 if row['kind']=='charge' else 1]+=row['amount_cents']
            v[2]+=1
    return dict(sorted(out.items()))
api_bytes=(PACKET/'original-creator-input/ledger_api.py').read_bytes()
for candidate in ['R17','R28','R44','R63']:
    package=next((PACKET/candidate/'package').iterdir())
    text=(package/'SKILL.md').read_text()
    front=dict(line.split(': ',1) for line in text.split('---',2)[1].strip().splitlines())
    syntax=[]
    for p in package.rglob('*.py'):
        ast.parse(p.read_text())
        syntax.append(str(p.relative_to(package)))
    links=re.findall(r'\]\(([^)]+)\)',text)
    result['packages'][candidate]={
        'name_matches_folder':front['name']==package.name,
        'name_valid':bool(re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',front['name'])) and len(front['name'])<=64,
        'description_nonempty_within_1024':0<len(front['description'])<=1024,
        'python_ast_pass':syntax,
        'local_skill_links_resolve':all((package/link).is_file() for link in links if '://' not in link),
    }
    for case in ['ordinary','challenging']:
        app=PACKET/candidate/case
        fixture=json.loads((PACKET/'original-consumer-inputs'/case/'fixture.json').read_text())['records']
        start,end=('2026-04-03','2026-04-09') if case=='ordinary' else ('2026-06-10','2026-06-18')
        setup=json.loads((app/'setup-observations.json').read_text())
        inputdir=app/('final-input-state' if (app/'final-input-state').exists() else 'prepared-input')
        expected_request=(PACKET/'original-consumer-inputs'/case/'input/request.md').read_text()
        expected_request=expected_request.replace('{{STATE_PATH}}',setup['state_path']).replace(
            '{{INPUT_DIR}}',setup['calls'][1]['argv'][1].rsplit('/',1)[0])
        resource_dir=app/('observed-final-skill' if (app/'observed-final-skill').exists() else 'prepared-skill')
        observation=dict(
            request_matches_fixed_request_after_path_substitution=(inputdir/'request.md').read_text()==expected_request,
            api_bytes_match=(inputdir/'ledger_api.py').read_bytes()==api_bytes,
            skill_copy_bytes_match=all(p.read_bytes()==(PACKET/candidate/'package'/p.relative_to(resource_dir)).read_bytes()
                for p in resource_dir.rglob('*') if p.is_file()),
            sql=[],
        )
        for p in app.rglob('*.sql'):
            sql=p.read_text()
            rows=re.findall(r'INSERT INTO "?records"? VALUES\((\d+),\'(.*)\'\);',sql)
            data=[json.loads(s.replace("''","'")) for _,s in rows]
            state=[line for line in sql.splitlines() if line.startswith('INSERT INTO "source_state"')]
            observation['sql'].append(dict(path=str(p.relative_to(app)),sha256=sha(p),records_equal_fixture=data==fixture,
                                            source_state_statement=state))
        if (app/'recovery-provenance.json').exists():
            provenance=json.loads((app/'recovery-provenance.json').read_text())
            observation['provenance_digest_checks']=[
                dict(path=item['destination'],sha256_match=sha(app/item['destination'])==item['sha256'])
                for item in provenance['files']]
            relay=(app/'recovery-provenance/source-relay.md').read_text()
            observation['relay_text_checks']=[
                dict(path=str(p.relative_to(app)),text_in_relay=p.read_text().strip() in relay)
                for dirname in ['original-public-observations','recovered-public-text','original-work-evidence','recovered-work-evidence']
                for p in (app/dirname).glob('*') if p.is_file()]
        cps=[p for dirname in ['work-evidence','original-work-evidence','recovered-work-evidence']
             for p in (app/dirname).glob('*.json')]
        assert len(cps)==1, cps
        p=cps[0]
        cp=json.loads(p.read_text())
        if 'entries' in cp:
            rows=list(cp['entries'].values()) if isinstance(cp['entries'],dict) else cp['entries']
            ids=[r['entry_id'] for r in rows]
            aggregation=totals(rows,start,end)
            retained_records_match_fixture=all(row==next(f for f in fixture if f['entry_id']==row['entry_id']) for row in rows)
        else:
            ids=cp.get('seen_entry_ids',cp.get('seen'))
            aggregation={}
            for vendor,values in cp['vendors'].items():
                aggregation[vendor]=values if isinstance(values,list) else [
                    values['settled_charge_cents'],values['settled_credit_cents'],values['qualifying_entry_count']]
            retained_records_match_fixture=None
        expected_ids=[row['entry_id'] for row in fixture[:6]]
        observation['checkpoint']=dict(
            path=str(p.relative_to(app)),
            ids=ids, ids_equal_expected_six=ids==expected_ids,
            retained_records_match_fixture=retained_records_match_fixture,
            next_cursor=cp['next_cursor'],
            status=cp.get('status',cp.get('complete')),
            vendor_charge_credit_count=aggregation,
            aggregates_match_expected=aggregation==totals(fixture[:6],start,end),
            request=cp.get('request'),
        )
        result['applications'][candidate+'/'+case]=observation
(WORK/'packet-readonly-audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result['packages'],indent=2))
for key,value in result['applications'].items():
    print(key,'API/package/request identities:',value['api_bytes_match'],value['skill_copy_bytes_match'],
          value['request_matches_fixed_request_after_path_substitution'],
          'checkpoint six IDs:',value['checkpoint']['ids_equal_expected_six'],
          'aggregate:',value['checkpoint']['aggregates_match_expected'],
          'SQL fixture match:',all(r['records_equal_fixture'] for r in value['sql']))
print('No database writes; all file writes are under the labelled grading-work directory.')

