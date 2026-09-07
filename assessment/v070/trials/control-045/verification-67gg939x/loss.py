import subprocess,sys
from pathlib import Path
p=subprocess.run([sys.executable,'/workspace/scratch/a75c3a6d9076/alps-v070-assessment/trials/control-045/input/ledger_api.py',*sys.argv[1:]],capture_output=True,text=True)
m=Path('/workspace/scratch/a75c3a6d9076/alps-v070-assessment/trials/control-045/verification-67gg939x/dropped')
if "page" in sys.argv and p.returncode == 0 and not m.exists():
 m.touch()
 sys.exit(9)
print(p.stdout,end="")
sys.exit(p.returncode)
