#!/usr/bin/env python3
"""Stateless component probe, not a replay of a recorded application.

Use an unchanged disposable helper copy. Model a successful metered page whose
stdout was lost; no real API command or source database is opened or changed.
"""
import contextlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
from unittest.mock import patch

WORK = Path('/workspace/scratch/a75c3a6d9076/alps-v070-assessment/grading-work/S06-P03-primary')
original = Path('/workspace/scratch/a75c3a6d9076/alps-v070-assessment/blind-business/S06-P03/R17/package/reimbursement-ledger-rollup/scripts/rollup.py')
copied = WORK/'DISPOSABLE-COMPONENT-COPY-R17-rollup.py'
shutil.copyfile(original,copied)
namespace = {'__name__':'disposable_probe_target','__file__':str(copied)}
exec(compile(copied.read_text(),str(copied),'exec'),namespace)
checkpoint=WORK/'DISPOSABLE-R17-response-loss-checkpoint.json'
if checkpoint.exists():
    raise RuntimeError('Use a new labelled probe directory; refusing to replace existing probe state')
mocked_calls=[]
description={'snapshot_id':'probe-six-entry-immutable-snapshot','total_records':6,
             'page_size':3,'calls_per_tranche':2,'tranche':1,'remaining_calls':2}

def simulated_run(argv,**kwargs):
    if argv[-1]=='describe':
        result=subprocess.CompletedProcess(argv,0,json.dumps(description),'')
        label='synthetic describe; no database access'
    elif 'page' in argv:
        result=subprocess.CompletedProcess(argv,0,'','')
        label='simulated successful page with lost stdout; one successful call modelled'
    else:
        raise AssertionError('unexpected command')
    mocked_calls.append({'argv':argv,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr,'label':label})
    return result

argv=[str(copied),'--api',str(WORK/'SIMULATED-API-NOT-CREATED.py'),
      '--state',str(WORK/'SIMULATED-SOURCE-NOT-CREATED.sqlite'),
      '--start','2026-04-03','--end','2026-04-09','--checkpoint',str(checkpoint)]
stdout=io.StringIO()
with patch.object(sys,'argv',argv), patch.object(subprocess,'run',simulated_run), contextlib.redirect_stdout(stdout):
    returned=namespace['main']()
result={
    'scope':__doc__,
    'helper_copy_unchanged':copied.read_bytes()==original.read_bytes(),
    'helper_argv':argv,
    'mocked_subprocess_calls':mocked_calls,
    'helper_main_return':returned,
    'helper_stdout':stdout.getvalue(),
    'checkpoint':json.loads(checkpoint.read_text()),
    'simulated_source_database_exists':(WORK/'SIMULATED-SOURCE-NOT-CREATED.sqlite').exists(),
    'actual_api_or_source_operations':0,
}
(WORK/'r17-response-loss-result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
