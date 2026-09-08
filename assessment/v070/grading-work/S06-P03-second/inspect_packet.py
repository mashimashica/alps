#!/usr/bin/env python3.12
"""Read packet evidence and inspect a labelled disposable checkpoint copy."""
import ast
import hashlib
import json
from pathlib import Path
import re
import shutil
import sqlite3

ROOT = Path(__file__).resolve().parent
PACKET = ROOT.parents[1] / "blind-business" / "S06-P03"
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def source_rows(path):
    lines=path.read_text().splitlines()
    rows=[]
    for line in lines:
        m=re.fullmatch(r'INSERT INTO "records" VALUES\((\d+),\'(.*)\'\);',line)
        if m: rows.append((int(m[1]),json.loads(m[2].replace("''", "'"))))
    return dict(sha256=sha(path),source_state=[x for x in lines if x.startswith('INSERT INTO "source_state"')],records=[x[1] for x in sorted(rows)])

result={"scope":"Packet read-only observations; no original paths followed; no consumer or original API executed.","packages":{},"applications":{}}
for candidate in ('R17','R28','R44','R63'):
    package=PACKET/candidate/'package'
    files={str(p.relative_to(package)):sha(p) for p in package.rglob('*') if p.is_file()}
    for p in package.rglob('*.py'): ast.parse(p.read_text())
    skill=next(package.glob('*/SKILL.md'))
    fm=skill.read_text().split('---',2)[1]
    result['packages'][candidate]={'file_sha256':files,'python_syntax':'parsed','frontmatter_name_matches_folder':('name: '+skill.parent.name) in fm,'frontmatter_description_present':'description: ' in fm}
    for case in ('ordinary','challenging'):
        folder=PACKET/candidate/case
        expected=json.loads((PACKET/'original-consumer-inputs'/case/'fixture.json').read_text())['records']
        evidence={'resource_comparisons':{},'native_source_sql':{},'recovery_extraction':[]}
        for variant in ('prepared-skill','observed-final-skill'):
            p=folder/variant
            if p.exists(): evidence['resource_comparisons'][variant]={str(x.relative_to(p)):sha(x) for x in p.rglob('*') if x.is_file()}==files
        for p in sorted(folder.glob('committed*/*.sql'))+sorted(folder.glob('logical-state-supplement/*.sql')):
            v=source_rows(p)
            evidence['native_source_sql'][str(p.relative_to(folder))]={k:x for k,x in v.items() if k!='records'}|{'records_match_fixed_fixture':v['records']==expected}
        if (folder/'recovery-provenance.json').exists():
            provenance=json.loads((folder/'recovery-provenance.json').read_text())
            lines=(folder/'recovery-provenance/source-relay.md').read_text().splitlines()
            for entry in provenance['source_entries']:
                span=entry.get('source_body_lines_inclusive')
                if span:
                    kind=entry['role']
                    recovered=folder/('recovered-work-evidence' if kind=='checkpoint-rendering.json' else 'recovered-public-text')/kind
                    relay='\n'.join(lines[span[0]-1:span[1]])
                    evidence['recovery_extraction'].append({'role':kind,'matches_relay_except_terminal_newline':relay.rstrip('\n')==recovered.read_text().rstrip('\n'),'sha256_matches_provenance':sha(recovered)==entry['sha256']})
            evidence['prepared_and_recovered_manifest_matches'] = all(sha(folder/item['destination'])==item['sha256'] for item in provenance['files'])
            evidence['explicit_unavailable']=provenance['unavailable']
        for p in list(folder.glob('work-evidence/*.json'))+list(folder.glob('recovered-work-evidence/*.json')):
            v=json.loads(p.read_text())
            if isinstance(v.get('entries'),dict):
                n=len(v['entries'])
                evidence[str(p.relative_to(folder))]={'entry_count':n,'matches_fixture_prefix':v['entries']=={x['entry_id']:x for x in expected[:n]},'all_fields':v}
            else: evidence[str(p.relative_to(folder))]=v
        result['applications'][candidate+'/'+case]=evidence

folder=ROOT/'disposable-R28-challenging-observation-copy'
folder.mkdir()
(folder/'DISPOSABLE-PROBE.txt').write_text('Byte copy of the recorded workflow checkpoint, inspected read-only; never used to execute the helper or API.\n')
original=PACKET/'R28/challenging/work-evidence/rollup-checkpoint.sqlite'
copy=folder/'disposable-recorded-checkpoint-copy.sqlite'
shutil.copy2(original,copy)
db=sqlite3.connect(copy.as_uri()+'?mode=ro',uri=True)
try:
    db.execute('BEGIN')
    v={'state':json.loads(db.execute('SELECT payload FROM state WHERE id=1').fetchone()[0]),'entries':list(db.execute('SELECT * FROM entries ORDER BY rowid')),'pages':list(db.execute('SELECT * FROM pages ORDER BY rowid')),'vendors':list(db.execute('SELECT * FROM vendors ORDER BY vendor_id'))}
    native='\n'.join(db.iterdump())+'\n'
finally:
    db.rollback()
    db.close()
(folder/'disposable-recorded-checkpoint-copy.native.sql').write_text(native)
result['applications']['R28/challenging']['recorded_checkpoint_disposable_copy']={'original_sha256':sha(original),'copy_sha256':sha(copy),'data':v,'inspection_queries':['SELECT payload FROM state WHERE id=1','SELECT * FROM entries ORDER BY rowid','SELECT * FROM pages ORDER BY rowid','SELECT * FROM vendors ORDER BY vendor_id']}
(ROOT/'packet-inspection.json').write_text(json.dumps(result,indent=2)+'\n')
(ROOT/'DATABASE-WRITES-FINISHED.txt').write_text('All component probe processes have exited. All SQLite connections are closed. No further database writes or copies are planned. Original packet files and original API states were never modified or executed.\n')
print(json.dumps({'status':'completed','packages':len(result['packages']),'applications':len(result['applications']),'recorded_checkpoint_copy':v,'output':str(ROOT/'packet-inspection.json')},sort_keys=True))
