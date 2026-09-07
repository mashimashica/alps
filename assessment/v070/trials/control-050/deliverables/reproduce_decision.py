#!/usr/bin/env python3
import csv
from collections import defaultdict
ROOT='input/sources'
def rows(n):
    with open(f'{ROOT}/{n}',newline='') as f:return list(csv.DictReader(f))
a=defaultdict(lambda:defaultdict(float))
for r in rows('shipment_cohorts.csv'):
    k=(r['period'],r['line'])
    for x in ('shipped_orders','mature_orders','confirmed_mispack_7d'):a[k][x]+=float(r[x])
for r in rows('shift_operations.csv'):
    k=(r['period'],r['line'])
    for x in ('productive_labor_hours','training_hours','late_dispatch_orders'):a[k][x]+=float(r[x])
print('period,line,shipped,mature,errors,error_rate,productive_hours,training,late_dispatch')
for k in sorted(a):
    d=a[k];q=d['confirmed_mispack_7d']/d['mature_orders']
    print(*k,int(d['shipped_orders']),int(d['mature_orders']),int(d['confirmed_mispack_7d']),f'{q:.4%}',int(d['productive_labor_hours']),int(d['training_hours']),int(d['late_dispatch_orders']),sep=',')
base=.8*(36/1800)+.2*(96/1200);trial=.8*(27/2700)+.2*(18/300);avoided=24000*(base-trial);extra=((269-4)/3)-(207/3)
print(f'projected baseline errors={24000*base:.1f}; trial scenario errors={24000*trial:.1f}; avoided={avoided:.1f}; gross=${avoided*65:,.0f}; labor=${extra*20*28:,.0f}; residual=${avoided*65-extra*20*28:,.0f}')
