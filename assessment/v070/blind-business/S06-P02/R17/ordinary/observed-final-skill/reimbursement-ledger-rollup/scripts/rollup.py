#!/usr/bin/env python3
import argparse,datetime,json,os,subprocess,sys
def emit(x): print(json.dumps(x,sort_keys=True,separators=(',',':')))
def main():
 p=argparse.ArgumentParser();p.add_argument('--api',required=True);p.add_argument('--source-state',required=True);p.add_argument('--from',dest='start',required=True);p.add_argument('--to',dest='end',required=True);p.add_argument('--checkpoint',required=True);a=p.parse_args()
 try: start=datetime.date.fromisoformat(a.start);end=datetime.date.fromisoformat(a.end)
 except ValueError: emit({'status':'invalid','error':'invalid_date_interval'});return 2
 if start>end: emit({'status':'invalid','error':'invalid_date_interval'});return 2
 def call(*args):
  r=subprocess.run([sys.executable,a.api,'--state',a.source_state,*args],text=True,capture_output=True)
  try:return r.returncode,json.loads(r.stdout)
  except Exception:return r.returncode,{'error':'invalid_api_response'}
 rc,m=call('describe')
 if rc:emit({'status':'error','error':'describe_failed','detail':m});return rc
 snap=m['snapshot_id'];state={'snapshot_id':snap,'start':a.start,'end':a.end,'cursor':None,'seen_cursors':[],'totals':{}}
 if os.path.exists(a.checkpoint):
  try:state=json.load(open(a.checkpoint))
  except Exception:emit({'status':'error','error':'invalid_checkpoint'});return 2
  if (state.get('snapshot_id'),state.get('start'),state.get('end'))!=(snap,a.start,a.end):emit({'status':'error','error':'checkpoint_mismatch'});return 2
 for _ in range(2):
  q=['page','--snapshot',snap]+([] if state['cursor'] is None else ['--cursor',state['cursor']]);rc,b=call(*q)
  if rc:
   if rc==75:emit({'status':'paused','snapshot_id':snap,'interval':{'from':a.start,'to':a.end},'reason':'tranche_exhausted','checkpoint':a.checkpoint});return 75
   emit({'status':'error','error':'page_failed','detail':b});return rc
  if state['cursor'] in state['seen_cursors']:emit({'status':'error','error':'repeated_cursor'});return 2
  state['seen_cursors'].append(state['cursor']);state['cursor']=b['next_cursor']
  for row in b['items']:
   d=datetime.date.fromisoformat(row['posted_on'])
   if row['status']!='settled' or not(start<=d<=end):continue
   t=state['totals'].setdefault(row['vendor_id'],{'charge_cents':0,'credit_cents':0,'entry_count':0});t['entry_count']+=1;t['charge_cents' if row['kind']=='charge' else 'credit_cents']+=row['amount_cents']
  os.makedirs(os.path.dirname(os.path.abspath(a.checkpoint)),exist_ok=True);json.dump(state,open(a.checkpoint,'w'),sort_keys=True)
  if state['cursor'] is None:
   rows=[{'vendor_id':v,**t,'net_cents':t['charge_cents']-t['credit_cents']} for v,t in sorted(state['totals'].items())];emit({'status':'complete','snapshot_id':snap,'interval':{'from':a.start,'to':a.end},'rows':rows});return 0
 emit({'status':'paused','snapshot_id':snap,'interval':{'from':a.start,'to':a.end},'reason':'tranche_exhausted','checkpoint':a.checkpoint});return 75
if __name__=='__main__':sys.exit(main())
