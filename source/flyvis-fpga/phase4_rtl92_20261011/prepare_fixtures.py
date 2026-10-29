"""Freeze original graph and independent arbitrary-precision integer oracle.

The prior software reference is used only for source/identity verification and
an independent vector cross-check. This scalar oracle emits every ordered edge
term and partial chemical sum, not just the final neuron outputs.
"""
from pathlib import Path
import importlib.util
import json
import hashlib
import argparse
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
REF=ROOT/'flyvis-fpga/phase4_scalable_engine_20261010/scalable_integer_reference.py'
spec=importlib.util.spec_from_file_location('prior_reference',REF)
ref=importlib.util.module_from_spec(spec)
spec.loader.exec_module(ref)

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def quant(x,f):
    x=float(x)*2**f
    return int(np.floor(x+0.5) if x>=0 else np.ceil(x-0.5))
def check(v,w,label):
    if not -(1<<(w-1))<=v<(1<<(w-1)): raise OverflowError((label,v,w))
    return v
def rnd(v,s):
    a=(abs(v)+(1<<(s-1)))>>s
    return -a if v<0 else a
def scalar(old,boundary,x,bias,inv,src_h,src,dst,weights,dt):
    chem=[0]*len(old); traces=[]
    for k in range(len(weights)):
        activity=old[src[k]] if src_h[k] else boundary[src[k]]
        term=check(rnd(max(activity,0)*weights[k],20),31,'edge')
        t=dst[k]; chem[t]=check(chem[t]+term,50,'accumulator')
        traces.append((term,chem[t]))
    out=[]
    for h,c in enumerate(chem):
        check(c,31,'chemical/Euler')
        drive=check(-old[h]+bias[h]+c+x[h],33,'drive')
        v=check(rnd(inv[h]*drive,24),31,'velocity')
        delta=check(rnd(v*dt,24),31,'delta')
        out.append(check(old[h]+delta,31,'state'))
    return out,chem,traces
def mem(path,values,width):
    mask=(1<<width)-1
    Path(path).write_text(''.join(f'{int(v)&mask:0{(width+3)//4}x}\n' for v in values),encoding='ascii')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--candidate',default='A_T4c')
    ap.add_argument('--out',default=str(HERE/'fixtures92'))
    ap.add_argument('--window-steps',type=int,default=8)
    args=ap.parse_args(); dest=Path(args.out); dest.mkdir(parents=True,exist_ok=True)
    hazard=args.candidate=='hazard'
    requests=[]; outputs=[]; trace_words=[]; cases=[]; hashes={}
    if hazard:
        n,b=4,8
        # Synthetic unit graph only. Repeated target 0, alternating signed
        # weights and both source classes; not presented as FlyVis topology.
        gids=list(range(100,112)); src_h=[False]*6+[True]*6
        src=[0,1,2,2,1,3,0,1,2,3,0,0]; dst=[0,0,0,0,0,0,0,0,0,1,2,0]
        weights=[1<<20,-(1<<20),1,-1,1<<19,-(1<<19),1<<20,-(1<<20),1<<19,1<<20,1<<20,-(1<<20)]
        bias=[0]*n; inv=[1<<24]*n; dt=83886
        details={'candidate':'SYNTHETIC_BRAM_HAZARD_UNIT','not_original_flyvis_graph':True}
        plans=[('hazard',i) for i in range(6)]
    else:
        details,d=ref.build_candidate(args.candidate,'condition_00')
        n,b=details['n_h'],details['n_boundary']
        gids=d['edge_ids'].tolist(); src_h=d['src_is_h'].tolist()
        src=d['src_local'].tolist(); dst=d['dst_local'].tolist()
        weights=d['weights_q'].tolist(); bias=d['bias_q'].tolist(); inv=d['inv_tau_q'].tolist(); dt=d['dt_q']
        assert weights==[quant(v,20) for v in d['weights']]
        assert bias==[quant(v,24) for v in d['bias']] and inv==[quant(v,24) for v in d['inv_tau']]
        assert dt==83886
        plans=[]
        for c in range(4):
            plans.append((f'condition_{c:02}',0))
            plans.extend((f'condition_{c:02}',k) for k in range(198,198+args.window_steps))
        plans.append(('boundary_perturb',198))
        hashes=details['source_files_sha256']
    hw=(n-1).bit_length(); sw=(max(n,b)-1).bit_length(); mw=21+1+sw+hw+24
    edge_words=[(g<<(1+sw+hw+24))|(int(sh)<<(sw+hw+24))|(s<<(hw+24))|(t<<24)|(w&0xffffff)
        for g,sh,s,t,w in zip(gids,src_h,src,dst,weights)]
    assert all(a<b for a,b in zip(gids,gids[1:]))
    mem(dest/'edges.mem',edge_words,mw)
    mem(dest/'edge_identity.mem',[(g<<hw)|t for g,t in zip(gids,dst)],21+hw)
    mem(dest/'neurons.mem',[(i&((1<<31)-1))<<31 | (bi&((1<<31)-1)) for bi,i in zip(bias,inv)],62)
    if not hazard:
        np.savez(dest/'original_mapping.npz',h_global_ids=d['h_ids'],boundary_global_ids=d['boundary_ids'],
                 original_global_edge_ids=d['edge_ids'],source_is_h=d['src_is_h'],source_local=d['src_local'],
                 target_local=d['dst_local'],weight_q20=d['weights_q'])
    previous_condition=None; previous_step=None; previous_out=None; cache={}
    for label,k in plans:
        if hazard:
            old=[1<<24,-(1<<24),3,-3]; boundary=[1<<24,1<<24,1<<19,-(1<<24),0,0,0,0]
            boundary[0]+=k; x=[0,(k-3)<<20,-(k+1)<<22,0]; sourcefiles={}
        else:
            cond='condition_01' if label=='boundary_perturb' else label
            if cond not in cache: cache[cond]=ref.build_candidate(args.candidate,cond)[1]
            ds=cache[cond]
            io=ds['io']; old=[quant(v,24) for v in io['old_H'][k]]
            if label==previous_condition and k==previous_step+1: old=previous_out[:]
            boundary=[quant(v,24) for v in io['boundary_before'][k]]
            x=[quant(v,24) for v in io['x_H'][k]]
            if label=='boundary_perturb': boundary[0]+=1<<23
            sourcefiles={'step_io':sha(ref.SAVED_RUNS/args.candidate/'Sham'/cond/'SOURCE_RAW_step_io.npz')}
        for v in old+boundary+x: check(v,31,'request')
        out,chem,trace=scalar(old,boundary,x,bias,inv,src_h,src,dst,weights,dt)
        # Prior vector reference is a separate implementation, used per step.
        vo,vc,vt=ref.fixed_step(*(np.asarray(v,dtype=np.int64) for v in (old,boundary,x,bias,inv)),
            np.asarray(src_h,dtype=bool),np.asarray(src,dtype=np.int64),np.asarray(dst,dtype=np.int64),
            np.asarray(weights,dtype=np.int64),dt)
        assert out==vo.tolist() and chem==vc.tolist() and [t[0] for t in trace]==vt.tolist()
        idx=len(cases); requests.extend(boundary+old+x); outputs.extend(out)
        trace_words.extend(((t&((1<<31)-1))<<50)|(s&((1<<50)-1)) for t,s in trace)
        float_err=None
        if not hazard and label!='boundary_perturb':
            saved=np.asarray(io['new_H_expected'][k],dtype=np.float64)
            err=np.abs(np.asarray(out)/2**24-saved)
            float_err={'max_abs':float(err.max()),'engineering_threshold_exceeds':int((err>1e-5+1e-5*np.abs(saved)).sum())}
        cases.append({'index':idx,'label':label,'saved_step':k,'internally_recurrent':not hazard and label==previous_condition and k==previous_step+1,
            'float32_comparison':float_err,'source_sha256':sourcefiles})
        previous_out=out; previous_condition=label; previous_step=k
    mem(dest/'requests.mem',requests,32); mem(dest/'expected.mem',outputs,31); mem(dest/'edge_traces.mem',trace_words,81)
    mem(dest/'recurrent.mem',[int(c['internally_recurrent']) for c in cases],1)
    streak=1; maxstreak=1
    for a,z in zip(dst,dst[1:]):
        streak=streak+1 if a==z else 1; maxstreak=max(maxstreak,streak)
    # One generic TB compiled for each fixture identity and BANKS value.
    defines=f'`define TEST_H {n}\n`define TEST_B {b}\n`define TEST_E {len(gids)}\n`define TEST_STEPS {len(cases)}\n'
    (dest/'fixture_config.svh').write_text(defines,encoding='ascii')
    summary={'candidate':args.candidate,'n_h':n,'n_boundary':b,'n_edges':len(gids),'n_requests':len(cases),
        'state_width':31,'weight_width':24,'state_fraction':24,'weight_fraction':20,'accumulator_width':50,'drive_width':33,'dt_q24':dt,
        'edge_word_bits':mw,'global_edge_order_strict':True,'consecutive_same_target_pairs':sum(a==z for a,z in zip(dst,dst[1:])),
        'max_same_target_streak':maxstreak,'same_bank_pairs':{str(bk):sum(a%bk==z%bk for a,z in zip(dst,dst[1:])) for bk in (1,2,4)},
        'cases':cases,'original_source_details':details,'source_files_sha256':hashes,
        'oracle_sha256':sha(__file__),'prior_reference_sha256':sha(REF),
        'fixture_sha256':{p.name:sha(p) for p in dest.iterdir() if p.suffix in ('.mem','.npz','.svh')},
        'scalar_vector_exact_every_step':True,'overflow_policy':'fail-fast, no clipping/saturation',
        'limits':['Saved external boundary; internal H recurs for each 8-step window. No full hybrid feedback.',
                  'Fixed-point agreement does not imply bitwise float32 dynamics equivalence.']}
    (dest/'manifest.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps({k:summary[k] for k in ('candidate','n_h','n_boundary','n_edges','n_requests','consecutive_same_target_pairs','max_same_target_streak')}))
if __name__=='__main__': main()
