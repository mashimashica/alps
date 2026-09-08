import subprocess,sys,pathlib
r=subprocess.run([sys.executable, '/workspace/scratch/a75c3a6d9076/alps-v070-assessment/trials/focus-008/input/ledger_api.py', *sys.argv[1:]],capture_output=True,text=True)
flag=pathlib.Path('/workspace/scratch/a75c3a6d9076/alps-v070-assessment/trials/focus-008/verification/tmpzqtcyvws/lost')
if 'page' in sys.argv and r.returncode==0 and not flag.exists():
 flag.touch()
 print('lost response')
else:
 print(r.stdout,end='')
sys.exit(r.returncode)
