"""Independent CPU refinement; accepted source/architecture remain read-only."""
from pathlib import Path
import sys,time,json,hashlib,shutil,csv
HERE=Path(__file__).resolve().parent
OLD=HERE.parent/'cnn_t4t5_replacement_20261016'
sys.path.insert(0,str(OLD))
import common as base
import numpy as np
import torch
from cnn import HexCNN,CNNService,restore
from experiment import OriginalTargets,ClosedLoop
from decoder_cpu import CPUDecoder
dump,load,sha,digest=base.dump,base.load,base.sha,base.digest
BUNDLE,LANE,FLY,TYPES=base.BUNDLE,base.LANE,base.FLY,base.TYPES

def mapping():return dict(np.load(OLD/'mapping.npz'))
def source():return base.source()
def r_service():return base.r_service()
def freezecheck(deep=False):
    p=load(HERE/'PREREGISTRATION.json')
    assert sha(HERE/'PREREGISTRATION.json')==load(HERE/'FREEZE.json')['sha256']
    for path,pin in p['pins'].items():
        q=Path(path)
        assert q.stat().st_size==pin['bytes'] and q.stat().st_mtime_ns==pin['mtime_ns'],path
        if deep:assert sha(q)==pin['sha256'],path
    return p

def fresh_model():
    m=mapping();model=restore(OLD/'training/cnn.pt',m)
    assert sum(p.numel() for p in model.parameters())==31168
    return model

def model_from(path):
    m=mapping();model=HexCNN(m['field_ids'].shape[0],m['offsets'],m['grid_uv'],m['h_channels'])
    model.load_state_dict(torch.load(path,map_location='cpu',weights_only=True));return model.eval()

def train_references():
    p=load(OLD/'PREREGISTRATION.json')
    return {r['condition']:np.load(r['path'],mmap_mode='r')[0] for r in p['training']}

def train_frames():
    root=LANE/'t4t5_criticality_20261011/cpu_preparation_r1'
    return {name:np.load(root/(name+'_stimulus.npy'))[0,:,0] for name in base.TRAIN}

def windows():
    return [dict(id=f'{name}_k{k}',condition=name,start=k,length=128) for name in base.TRAIN for k in [0,196,320]]+[dict(id='GRAY_k0',condition='GRAY',start=0,length=128)]

def short_validation(model,label):
    """Real live R-only+Cnn, single initialization per window; no midwindow truth."""
    start=time.perf_counter();m=mapping();initial=torch.from_numpy(np.load(BUNDLE/'initial_state_full.npy'))
    refs=train_references();frames=train_frames();r=r_service();records=[]
    output=HERE/'short_checks'/label;output.mkdir(parents=True)
    for w in windows():
        k=w['start'];n=w['length'];name=w['condition']
        if name=='GRAY':
            truth=np.load(HERE/'gray_reference.npy',mmap_mode='r');inputs=np.full((n,721),.5,np.float32);a0=initial
        else:
            truth=refs[name][k:k+n];inputs=frames[name][k:k+n]
            a0=initial if k==0 else torch.from_numpy(np.array(refs[name][k-1],copy=True))
        engine=ClosedLoop(r,CNNService(model,m),a0,m,label+'_'+w['id']);rows=[];hs=[];maxabs=0;failure=None
        hsq=rsq=henergy=renergy=0.;subsq=np.zeros(8);subenergy=np.zeros(8)
        with (output/(w['id']+'_chain.jsonl')).open('x',encoding='utf-8') as f:
            for j in range(n):
                try:state,chain=engine.step(torch.from_numpy(inputs[j]),j)
                except (ValueError,RuntimeError) as exc:failure=repr(exc);break
                f.write(json.dumps(chain)+'\n');a=state.numpy();maxabs=max(maxabs,float(abs(a).max()))
                dh=(a[m['H']]-truth[j,m['H']]).astype(np.float64);dr=(a[m['R']]-truth[j,m['R']]).astype(np.float64)
                hsq+=float(dh@dh);rsq+=float(dr@dr)
                ht=truth[j,m['H']].astype(np.float64);rt=truth[j,m['R']].astype(np.float64)
                henergy+=float(ht@ht);renergy+=float(rt@rt)
                subsq+=(dh.reshape(8,721)**2).sum(1);subenergy+=(ht.reshape(8,721)**2).sum(1)
                rows.append(dict(step=j,global_step=k+j,H_RMSE=float(np.sqrt(np.mean(dh**2))),R_RMSE=float(np.sqrt(np.mean(dr**2)))))
                hs.append(a[m['H']].copy())
        complete=len(rows)==n;hrel=float(np.sqrt(hsq/max(henergy,1e-12)));rrel=float(np.sqrt(rsq/max(renergy,1e-12)))
        subtype=np.sqrt(subsq/np.maximum(subenergy,1e-12));hrmse=float(np.sqrt(hsq/max(len(rows)*5768,1)))
        passed=bool(complete and hrel<=.05 and rrel<=.01 and subtype.max()<=.10 and (name!='GRAY' or hrmse<=.002))
        np.save(output/(w['id']+'_H.npy'),np.array(hs));np.save(output/(w['id']+'_final.npy'),engine.state.numpy())
        dump(output/(w['id']+'_errors.json'),rows)
        records.append(dict(**w,complete=complete,H_nRMSE=hrel,R_nRMSE=rrel,subtype_nRMSE=subtype.tolist(),
            H_RMSE=hrmse,max_abs=maxabs,pass_gate=passed,commits=len(rows),failure=failure,native_H_updates=0,teacher_corrections=0))
    result=dict(label=label,pass_gate=all(r['pass_gate'] for r in records),records=records,
        commits=sum(r['commits'] for r in records),wall_s=time.perf_counter()-start)
    dump(output/'RESULT.json',result)
    print(json.dumps(dict(stage='training_short_gate',label=label,passed=result['pass_gate'],
        max_H_nRMSE=max(r['H_nRMSE'] for r in records),max_R_nRMSE=max(r['R_nRMSE'] for r in records),wall_s=result['wall_s'])),flush=True)
    return result
