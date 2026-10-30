"""Bounded all-H integer probe, using stored Full states (NOT live GPU feedback).

Uses the prior independent Q24/Q20 vector oracle, checks four first requests
against a new Python arbitrary-precision scalar loop, then runs 8-step H-only
recurrence per condition. No baseline inference is rerun.
"""
import importlib.util,time,json
import numpy as np
from extract_graph import HERE,ROOT,BUNDLE,sha,write_json

def round_shift(x,k):
    return ((x+(1<<(k-1)))>>k) if x>=0 else -(((-x)+(1<<(k-1)))>>k)

def scalar(source,src,dst,w,bias,inv,old,dt):
    sums=[0]*len(old);peak=0
    for si,ti,wi in zip(src,dst,w):
        q=round_shift(max(0,int(source[int(si)]))*int(wi),20)
        assert -(1<<30)<=q<(1<<30)
        sums[int(ti)]+=q;peak=max(peak,abs(sums[int(ti)]));assert -(1<<49)<=sums[int(ti)]<(1<<49)
    out=[]
    for i,c in enumerate(sums):
        assert -(1<<30)<=c<(1<<30)
        drive=-int(old[i])+int(bias[i])+c
        assert -(1<<32)<=drive<(1<<32)
        vel=round_shift(int(inv[i])*drive,24);assert -(1<<30)<=vel<(1<<30)
        delta=round_shift(vel*dt,24);new=int(old[i])+delta;assert -(1<<30)<=new<(1<<30)
        out.append(new)
    return np.array(out,dtype='i8'),np.array(sums,dtype='i8'),peak

def main():
    start=time.perf_counter()
    refpath=ROOT/'flyvis-fpga/phase4_scalable_engine_20261010/scalable_integer_reference.py'
    sp=importlib.util.spec_from_file_location('previous_oracle',refpath);ref=importlib.util.module_from_spec(sp);sp.loader.exec_module(ref)
    d=dict(np.load(HERE/'data/incoming_edges.npz'));par=dict(np.load(HERE/'data/H_parameters.npz'))
    h=d['H'];n=len(h);ids=d['global_edge_id'];src=d['source_cache_index'];dst=d['target_h_index'];weights=d['effective_weight'];source_h=src<n
    sl=np.where(source_h,src,src-n);cache=d['cache_global_ids'];bound=cache[n:]
    assert np.all(np.diff(ids)>0)
    fullpath=ROOT/'flyvis-circuit-selection/phase2_20261010/artifacts/full_gpu_reference_a/activities_full.npy'
    a=np.load(fullpath,mmap_mode='r');a0=np.load(BUNDLE/'initial_state_full.npy'); assert a.shape==(4,485,45669)
    q=lambda x:ref.round_away_float(x,24);wq=ref.round_away_float(weights,20);bias=q(par['bias']);inv=q(par['inverse_tau']);dt=83886;zero=np.zeros(n,dtype='i8')
    rec=[];outputs=[];outputsA=[];peaks={k:0. for k in ['edge_term','chemical','drive','velocity','new_state','scalar_partial_chemical']}
    ranges={'H': [float('inf'),-float('inf')],'cache_sources':[float('inf'),-float('inf')]}
    for c in range(4):
        for k in range(0,485,32):
            chunk=a[c,k:k+32]
            for key,which in [('H',h),('cache_sources',cache)]:
                ar=chunk[:,which];ranges[key][0]=min(ranges[key][0],float(ar.min()));ranges[key][1]=max(ranges[key][1],float(ar.max()))
        for mode,steps in [('single',[0]),('short_recurrence',list(range(198,206)))]:
            previous=None;previousA=None
            for k in steps:
                fullold=a0 if k==0 else a[c,k-1];old=q(fullold[h]) if previous is None else previous;boundary=q(fullold[bound])
                out,chem,terms=ref.fixed_step(old,boundary,zero,bias,inv,source_h,sl,dst,wq,dt)
                if k==0:
                    sc,sc_chem,sc_peak=scalar(np.r_[old,boundary],src,dst,wq,bias,inv,old,dt)
                    assert np.array_equal(sc,out) and np.array_equal(sc_chem,chem)
                    peaks['scalar_partial_chemical']=max(peaks['scalar_partial_chemical'],sc_peak/2**24)
                drive=-old+bias+chem;velocity=ref.round_shift_vector(inv*drive,24)
                for key,val in [('edge_term',terms),('chemical',chem),('drive',drive),('velocity',velocity),('new_state',out)]:
                    peaks[key]=max(peaks[key],float(np.max(np.abs(val)))/2**24)
                # Same source-state semantics; GPU chemical emulated in float32
                # here solely to assess neuron-only fixed-point input quantization.
                oldA=q(fullold[h]) if previousA is None else previousA
                chA=ref.float32_chemical((oldA/2**24).astype('f4'),fullold[bound],source_h,sl,dst,weights)
                cq=q(chA);driveA=-oldA+bias+cq
                velA=ref.round_shift_vector(inv*driveA,24);ref.require_fits(velA,31,'A velocity')
                outA=oldA+ref.round_shift_vector(velA*dt,24);ref.require_fits(outA,31,'A output')
                # Serial float32 original equation on exact stored old state.
                cf=ref.float32_chemical(fullold[h],fullold[bound],source_h,sl,dst,weights)
                drivef=np.add(np.add(-fullold[h],par['bias'],dtype='f4'),cf,dtype='f4')
                ff=np.add(fullold[h],np.multiply(np.multiply(par['inverse_tau'],drivef,dtype='f4'),np.float32(.005),dtype='f4'),dtype='f4')
                result=dict(condition=c,condition_identity=['OFF0','ON0','OFF180','ON180'][c],mode=mode,step=k,
                    B_fixed_vs_saved_Full=ref.metric(a[c,k,h],out/2**24),A_fixed_vs_saved_Full=ref.metric(a[c,k,h],outA/2**24),
                    float32_reconstruction_max_abs=float(np.max(np.abs(ff-a[c,k,h]))))
                rec.append(result);outputs.append(out);outputsA.append(outA);previous=out;previousA=outA
    np.savez(HERE/'data/numeric_probe_outputs.npz',B_q24=np.array(outputs),A_q24=np.array(outputsA),H=h,global_incoming_edge_ids=ids)
    result=dict(status='PASS_BOUNDED_SOFTWARE_PROBE' if all(x['B_fixed_vs_saved_Full']['over_initial_engineering_tolerance']==0 and x['A_fixed_vs_saved_Full']['over_initial_engineering_tolerance']==0 for x in rec) else 'ENGINEERING_TOLERANCE_FAIL',
      evidence_level='SOFTWARE_ONLY',format=dict(state_width=31,state_frac=24,weight_width=24,weight_frac=20,chemical_width=50,drive_width=33,velocity_width=31,dt_code=dt,rounding='nearest_ties_away',overflow='reject_no_saturation'),
      requests=len(rec),H_outputs_per_architecture=len(rec)*n,edges_computed_B=len(rec)*len(ids),scalar_crosschecked_requests=4,scalar_crosschecked_edges=4*len(ids),
      saved_Full_state_range_all_4x485=ranges,observed_fixed_abs_peaks=peaks,
      B_max_abs=max(x['B_fixed_vs_saved_Full']['max_abs'] for x in rec),A_max_abs=max(x['A_fixed_vs_saved_Full']['max_abs'] for x in rec),
      B_over_tolerance=sum(x['B_fixed_vs_saved_Full']['over_initial_engineering_tolerance'] for x in rec),A_over_tolerance=sum(x['A_fixed_vs_saved_Full']['over_initial_engineering_tolerance'] for x in rec),
      float32_reconstruction_max_abs=max(x['float32_reconstruction_max_abs'] for x in rec),
      limitation='R boundary is stored Full replay. No live R feedback, no 5768 RTL, no full 485-step H recurrence, no functional acceptance. Conditions are historical OFF/ON0/180, NOT the new criticality protocol directions.',
      files_sha256={str(f):sha(f) for f in [fullpath,BUNDLE/'initial_state_full.npy',refpath]},elapsed_seconds=time.perf_counter()-start,requests_detail=rec)
    write_json(HERE/'NUMERIC_PROBE.json',result);print(json.dumps({k:v for k,v in result.items() if k!='requests_detail'},indent=2))

if __name__=='__main__':main()
