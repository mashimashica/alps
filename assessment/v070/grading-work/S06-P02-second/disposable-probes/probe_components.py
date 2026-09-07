"""Independent grader probes on explicitly disposable copied materials only.

No evaluated package is edited. All API state paths and wrapper logs are under
this directory. Operator grants here are validation actions, not consumer work.
"""
from pathlib import Path
import hashlib
import json
import shlex
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
PACKET = Path('/workspace/scratch/a75c3a6d9076/alps-v070-assessment/blind-business/S06-P02')
PYTHON = shutil.which('python3.12')
RESULTS = {'scope': __doc__, 'python': PYTHON, 'cases': []}


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def run(case, argv):
    process = subprocess.run(argv, cwd=case['directory'], text=True, capture_output=True)
    entry = {'argv': [str(x) for x in argv], 'command': shlex.join([str(x) for x in argv]),
             'cwd': case['directory'], 'exit_code': process.returncode,
             'stdout': process.stdout, 'stderr': process.stderr}
    case['commands'].append(entry)
    return entry


def body(entry):
    try:
        return json.loads(entry['stdout'])
    except json.JSONDecodeError:
        return None


def make_case(candidate, label, fixture, lose_first=False):
    folder = ROOT / candidate / label
    folder.mkdir(parents=True, exist_ok=False)
    case = {'candidate': candidate, 'label': label, 'directory': str(folder),
            'disposable': True, 'commands': [], 'observations': []}
    RESULTS['cases'].append(case)
    api = folder / 'api_wrapper.py'
    api.write_text('''# Disposable grader-only API observer; copied API remains unchanged.
from pathlib import Path
import json,subprocess,sys
API = %r
LOG = Path(%r)
LOSE_FIRST = %r
MARKER = Path(%r)
command = [sys.executable, API, *sys.argv[1:]]
r = subprocess.run(command, text=True, capture_output=True)
drop = LOSE_FIRST and 'page' in sys.argv and r.returncode == 0 and not MARKER.exists()
if drop:
    MARKER.write_text('First successful page stdout intentionally withheld by grader.\\n')
with LOG.open('a') as out:
    out.write(json.dumps({'argv':command,'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'stdout_withheld_from_runner':drop},sort_keys=True)+'\\n')
if not drop:
    sys.stdout.write(r.stdout)
sys.stderr.write(r.stderr)
sys.exit(r.returncode)
''' % (str(ROOT/'copied-input/ledger_api.py'), str(folder/'public-api-calls.jsonl'), lose_first, str(folder/'loss.marker')))
    state = folder/'source.sqlite'
    checkpoint = folder/'progress.json'
    case.update({'api':str(api), 'state':str(state), 'checkpoint':str(checkpoint),
                 'fixture':str(fixture), 'fault': 'first successful page stdout discarded after commit' if lose_first else None})
    init = run(case, [PYTHON,str(api),'--state',str(state),'init','--fixture',str(fixture)])
    assert init['exit_code'] == 0, init
    return case


def api_command(case, command, state=None):
    return run(case,[PYTHON,case['api'],'--state',state or case['state'],command])


def runner_command(case, start, end, state=None):
    package=ROOT/'copied-packages'/case['candidate']/'reimbursement-ledger-rollup/scripts'
    args=[PYTHON]
    state=state or case['state']
    if case['candidate']=='R17':
        args += [str(package/'rollup.py'),'--api',case['api'],'--source-state',state,
                 '--from',start,'--to',end,'--checkpoint',case['checkpoint']]
    elif case['candidate']=='R28':
        args += [str(package/'rollup.py'),'--api',case['api'],'--state',state,
                 '--from-date',start,'--through-date',end,'--checkpoint',case['checkpoint']]
    elif case['candidate']=='R44':
        args += [str(package/'rollup.py'),'--api',case['api'],'--state',state,
                 '--from',start,'--to',end,'--checkpoint',case['checkpoint']]
    else:
        args += [str(package/'reimbursement_rollup.py'),'--api',case['api'],'--state',state,
                 '--start-date',start,'--end-date',end,'--progress',case['checkpoint']]
    return run(case,args)


def observe(case,label,result=None):
    checkpoint=Path(case['checkpoint'])
    value={'label':label,'checkpoint_exists':checkpoint.exists()}
    if result is not None:
        value.update({'runner_exit':result['exit_code'],'runner_body':body(result)})
    if checkpoint.exists():
        value['checkpoint']=json.loads(checkpoint.read_text())
    value['describe']=body(api_command(case,'describe'))
    case['observations'].append(value)


(ROOT/'copied-input').mkdir(exist_ok=False)
shutil.copy2(PACKET/'original-creator-input/ledger_api.py',ROOT/'copied-input/ledger_api.py')
shutil.copy2(PACKET/'original-consumer-inputs/challenging/fixture.json',ROOT/'copied-input/challenging.json')
dump(ROOT/'copied-input/empty.json',{'records':[]})
ordinary=json.loads((PACKET/'original-consumer-inputs/ordinary/fixture.json').read_text())
dump(ROOT/'copied-input/singleton.json',{'records':[ordinary['records'][0]]})
for candidate in ('R17','R28','R44','R63'):
    source=PACKET/candidate/'package'
    target=ROOT/'copied-packages'/candidate
    shutil.copytree(source,target,copy_function=shutil.copy2)
    assert all(hashlib.sha256(p.read_bytes()).digest()==hashlib.sha256((target/p.relative_to(source)).read_bytes()).digest()
               for p in source.rglob('*') if p.is_file())
    case=make_case(candidate,'approved-continuation',ROOT/'copied-input/challenging.json')
    observe(case,'initial')
    for tranche in (1,2,3):
        if tranche>1:
            assert api_command(case,'grant-tranche')['exit_code']==0
        result=runner_command(case,'2026-06-10','2026-06-18')
        observe(case,f'after_tranche_{tranche}',result)
    result=runner_command(case,'2026-06-10','2026-06-18')
    observe(case,'completed_checkpoint_rerun',result)

    case=make_case(candidate,'empty-source',ROOT/'copied-input/empty.json')
    result=runner_command(case,'2026-04-03','2026-04-09')
    observe(case,'empty_run',result)

    case=make_case(candidate,'lost-first-response',ROOT/'copied-input/challenging.json',lose_first=True)
    result=runner_command(case,'2026-06-10','2026-06-18')
    observe(case,'after_lost_response',result)
    result=runner_command(case,'2026-06-10','2026-06-18')
    observe(case,'same_command_billable_retry',result)

case=make_case('R44','singleton-source',ROOT/'copied-input/singleton.json')
result=runner_command(case,'2026-04-03','2026-04-09')
observe(case,'singleton_run',result)

case=make_case('R17','different-state-same-snapshot',ROOT/'copied-input/challenging.json')
second=str(Path(case['directory'])/'second-disposable-source.sqlite')
assert run(case,[PYTHON,case['api'],'--state',second,'init','--fixture',case['fixture']])['exit_code']==0
result=runner_command(case,'2026-06-10','2026-06-18')
observe(case,'first_state_paused',result)
result=runner_command(case,'2026-06-10','2026-06-18',state=second)
observe(case,'checkpoint_accepted_on_different_state',result)
case['observations'].append({'label':'second_state_metadata','describe':body(api_command(case,'describe',state=second))})

for case in RESULTS['cases']:
    case['public_api_calls']=[json.loads(s) for s in (Path(case['directory'])/'public-api-calls.jsonl').read_text().splitlines()]
    dump(Path(case['directory'])/'results.json',case)
    print(json.dumps({'candidate':case['candidate'],'case':case['label'],
                      'observations':[{'label':o['label'],'runner_exit':o.get('runner_exit'),
                        'status':(o.get('runner_body') or {}).get('status'),
                        'error':(o.get('runner_body') or {}).get('error'),
                        'checkpoint_exists':o.get('checkpoint_exists'),
                        'tranche':o['describe']['tranche'],'remaining_calls':o['describe']['remaining_calls']}
                        for o in case['observations']]},sort_keys=True))
dump(ROOT/'results.json',RESULTS)
