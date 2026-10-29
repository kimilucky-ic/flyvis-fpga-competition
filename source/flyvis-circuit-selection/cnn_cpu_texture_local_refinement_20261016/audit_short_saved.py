"""Supplementary saved-data audit; no optimization or neural forward."""
from core import *

check();data=load(HERE/'training/DATA.json');m=ref.mapping();initial=np.load(BUNDLE/'initial_state_full.npy')
count=0
for source in data['sources']:
    truth=np.load(source['states'],mmap_mode='r');truth=truth[0] if source['states_batch'] else truth
    x=np.load(source['path']);x=x[0,:,0] if source['inputs_batch'] else x
    for start in [0,196,320] if source['steps']==485 else [0,320,800]:
        out=HERE/'training/short'/(source['id']+'_k'+str(start));r=load(out/'RESULT.json')
        assert r['length']==128 and r['failure'] is None and r['teacher_corrections_during_window']==0
        a=np.load(out/'states.npy',mmap_mode='r');rows=(out/'chain.jsonl').read_text(encoding='utf-8').splitlines();assert len(rows)==128
        previous=digest(initial if start==0 else truth[start-1])
        for j,line in enumerate(rows):
            row=json.loads(line)
            assert row['step']==j and row['old']==previous and row['new']==digest(a[j]) and row['input']==digest(x[start+j])
            assert row['time']==j*.005 and row['next_time']==(j+1)*.005 and row['old_source']=='OWN_LIVE_STATE' and row['native_H_updates']==0
            previous=row['new'];count+=1
result=dict(status='PASS_SAVED_TRAINING_WINDOWS',complete_state_chains_checked=count,windows=30,
    gray_control_extra128_summary_only=True,window_start_uses_teacher_once=True,corrections_within_windows=0,
    new_neural_steps=0,GPU=0,board=0)
dump(HERE/'SHORT_SAVED_AUDIT.json',result);print(json.dumps(result),flush=True)
