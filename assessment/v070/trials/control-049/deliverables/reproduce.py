import csv
from collections import defaultdict
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent / 'input' / 'sources'
def main():
    c=defaultdict(lambda:[0,0,0]); o=defaultdict(lambda:[0,0,0,0])
    with (ROOT/'shipment_cohorts.csv').open(newline='') as f:
        for r in csv.DictReader(f):
            k=(r['period'],r['line']); c[k][0]+=int(r['shipped_orders']); c[k][1]+=int(r['mature_orders']); c[k][2]+=int(r['confirmed_mispack_7d'])
    with (ROOT/'shift_operations.csv').open(newline='') as f:
        for r in csv.DictReader(f):
            k=(r['period'],r['line']); o[k][0]+=int(r['productive_labor_hours']); o[k][2]+=int(r['training_hours']); o[k][3]+=int(r['late_dispatch_orders'])
    for k in sorted(c):
        shipped,mature,errors=c[k]; hours,_,training,late=o[k]
        q=f'{errors/mature:.4%}' if mature else 'NA (immature)'; cut=f'{late/shipped:.4%}' if shipped else 'NA'
        print(f'{k[0]} {k[1]}: shipped={shipped}, mature={mature}, errors={errors}, quality_rate={q}, hours={hours}, training={training}, late={late}, cutoff_rate={cut}')
if __name__=='__main__': main()
