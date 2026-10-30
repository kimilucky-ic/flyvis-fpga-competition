"""Fresh-process full24 Sham/Ablation; human-window gated, reference after commit."""
import argparse,csv,time,uuid,platform
from common import *
ACTIVE_CONTEXT={}

def main():
    p=argparse.ArgumentParser();p.add_argument('--repeat',required=True,choices=['formal_r1','formal_r2']);p.add_argument('--preflight-only',action='store_true');args=p.parse_args()
    from run_gate import require_launch,require_step_time,verify_frozen_files
    if args.preflight_only:
        identity=verify_frozen_files();manifest_verify(BUNDLE)
        print('PASS_STATIC_PREFLIGHT_ONLY',identity['campaign_id'],'GPU execution=0; neural updates=0');return
    ticket=require_launch()
    out=HERE/'artifacts'/args.repeat
    if out.exists():raise SystemExit('Existing run preserved')
    out.mkdir(parents=True);torch=configure_gpu()
    from gate_service import HRReleaseService
    from bound_adapter import BoundAdapter,make_identity
    from coordinator import Coordinator
    entries=manifest_verify(BUNDLE);reg=load(HERE/'EXECUTION_BINDING.json');spec=load(HERE/'spec_snapshot/spec_config.json')
    initial=np.load(BUNDLE/'initial_state_full.npy');stim=np.load(BUNDLE/'stimulus.npy');clock=np.load(BUNDLE/'time.npy')
    refroot=HERE/'artifacts'/('full_r1' if args.repeat=='formal_r1' else 'full_r2')
    refidentity=load(refroot/'run_identity.json');assert refidentity['campaign_id']==reg['campaign_id']
    refmeta=load(refroot/'result.json');assert refmeta['status']=='PASS_REFERENCE_EXECUTION'
    manifest_verify(refroot);full=np.load(refroot/'activities_full.npy',mmap_mode='r');assert full.shape==(24,485,45669)
    sources=[Path(__file__),HERE/'common.py',HERE/'gate_service.py',HERE/'bound_adapter.py',*(HERE/'dependencies/b_core'/s for s in ['h_step.py','coordinator.py','gpu_adapter.py']),HERE/'dependencies/a_snapshot/r_only.py']
    code={p.relative_to(HERE).as_posix():file_hash(p) for p in sources};start=time.monotonic();allresults=[]
    for name in ['B_T5c','C_T4T5_all_centers']:
        cp=BUNDLE/'candidates'/name;h=HUpdater(cp/'static_boundary_gpu_native.npz');inputs=validate_parameters(h,BUNDLE/'expanded_parameters.npz')
        hr=np.load(HERE/'spec_snapshot'/(name+'_HR_edge_ids.npy'))
        for mode in ['Sham','Ablation']:
            dest=out/name/mode;dest.mkdir(parents=True)
            service=HRReleaseService(BUNDLE/'expanded_parameters.npz',BUNDLE/'identity_manifest.json',cp/'candidate_manifest.json',device='cuda',hr_edge_ids=hr,start_step=200,mode=mode)
            binding=make_identity(name,mode);adapter=BoundAdapter(service,inputs,binding);run=reg['planned_run_ids'][args.repeat][name][mode]
            identity=dict(**binding,run_id=run,repeat=args.repeat,pid=os.getpid(),python=platform.python_version(),torch=torch.__version__,numpy=np.__version__,
                gpu=torch.cuda.get_device_name(0),code_sha256=code,registration_sha256=reg['proposal_sha256'],dt_s=.005,
                command=[sys.executable,*sys.argv],evidence_level='ACTUAL_LIVE_GPU_R_INDEPENDENT_PYTHON_H',Full_source='new_official_GPU_Full_same_campaign',
                Full_source_identity=refidentity,authority_sha256=ticket['authority_sha256'],FPGA_execution=False,recorded_R_production=False,native_H_production_updates=0)
            dump(dest/'run_identity.json',identity)
            trace=np.lib.format.open_memmap(dest/'activities_full.npy',mode='w+',dtype=np.float32,shape=(24,485,45669))
            sham=np.load(out/name/'Sham/activities_full.npy',mmap_mode='r') if mode=='Ablation' else None
            events=(dest/'step_status.jsonl').open('w',encoding='utf-8');envelopes=(dest/'request_bindings.jsonl').open('w',encoding='utf-8');gates=[];cases=[]
            for c,condition in enumerate(spec['fixture']['conditions']):
                case=dest/f'condition_{c:02d}';case.mkdir();h=HUpdater(cp/'static_boundary_gpu_native.npz');co=Coordinator(h,adapter,initial,run,binding['comparison_id'],condition['original_sample'])
                ACTIVE_CONTEXT.update(mode=mode,condition=c,coordinator=co)
                oldh=np.empty((485,len(h.h_ids)),np.float32);raw=np.empty((485,len(h.source_ids)),np.float32);chem=np.empty_like(oldh);xh=np.empty_like(oldh);err=[]
                with native_full_forbidden() as guard:
                    for k in range(485):
                        require_step_time(ticket)
                        x=input_full(stim[c,k,0],inputs);prepared=co.prepare(k,x,'SOURCE_RAW')
                        oldh[k]=prepared.h_request.old_h;raw[k]=prepared.h_request.boundary;chem[k]=prepared.h_result.chemical;xh[k]=prepared.h_request.x_h
                        require_step_time(ticket)
                        actual=co.commit(prepared);trace[c,k]=actual
                        target=full[c,k] if mode=='Sham' else sham[c,k]
                        row=dict(condition=c,step_id=k,state_before_time=float(clock[k]),state_after_time=float(clock[k]+.005))
                        for group,ids in dict(H=h.h_ids,R=service.r_indices,full=np.arange(45669)).items():row.update({group+'_'+key:value for key,value in errors(actual,target,ids).items()})
                        err.append(row)
                        if mode=='Sham':assert row['full_violations']==0
                        elif k<200:assert np.array_equal(actual,sham[c,k])
                        elif k==200:assert np.array_equal(actual[h.h_ids],sham[c,k,h.h_ids])
                        gate=dict(condition=c,**service.last_gate_evidence);gates.append(gate)
                        assert gate['all_other_edge_gain']==1 and gate['selected_HR_gain']==(0 if mode=='Ablation' and k>=200 else 1)
                        if gate['gate_active']:assert gate['hr_after_abs_sum']==0 and gate['hr_after_nonzero_terms']==0
                        for event in co.logs[-2:]:events.write(json.dumps(dict(condition=c,**event))+'\n')
                        envelopes.write(json.dumps(dict(condition=c,**adapter.last_envelope))+'\n')
                        if k in (199,200,201,484):
                            old=prepared.h_request.old_h # full edge diagnostics reconstructed from committed predecessor
                            predecessor=initial if k==0 else trace[c,k-1]
                            with np.load(BUNDLE/'expanded_parameters.npz') as z:
                                w=z['effective_weight'][hr];s=z['source_global'][hr]
                            before=w*np.maximum(predecessor[s],np.float32(0));after=before*np.float32(gate['selected_HR_gain'])
                            np.savez(case/f'HR_edge_current_step_{k:03d}.npz',original_edge_ids=hr,before=before,after=after,gain=np.float32(gate['selected_HR_gain']),step_id=k,old_state_step_id=k)
                    assert guard['forbidden_native_call_count']==0 and h.step_count==co.next_step_id==485
                with (case/'step_differences.csv').open('w',newline='',encoding='utf-8') as f:
                    writer=csv.DictWriter(f,fieldnames=list(err[0]));writer.writeheader();writer.writerows(err)
                np.savez(case/'SOURCE_RAW_step_io.npz',old_H=oldh,boundary_before=raw,x_H=xh,chemical_expected=chem,new_H_expected=trace[c,:,h.h_ids].T,
                    H_global_ids=h.h_ids,source_global_ids=h.source_ids,step_id=np.arange(485),time_label=clock,state_before_time=clock,state_after_time=clock+.005,dt_s=np.float32(.005))
                cases.append(dict(condition=condition,steps=485,native_guard=guard,max_abs={g:max(row[g+'_max_abs'] for row in err) for g in ['H','R','full']},
                    violations=sum(row['full_violations'] for row in err),finite=True,initial_full_digest=array_hash(initial),atomic_commits=485))
                trace.flush();print('FORMAL_CONDITION',args.repeat,name,mode,condition['original_sample'],json.dumps(cases[-1]['max_abs']),flush=True)
            events.close();envelopes.close();trace.flush();service.assert_weights_unchanged();assert adapter.calls==11640
            with (dest/'gate_steps.csv').open('w',newline='',encoding='utf-8') as f:
                writer=csv.DictWriter(f,fieldnames=list(gates[0]));writer.writeheader();writer.writerows(gates)
            result=dict(status='PASS_FORMAL_EXECUTION_CANDIDATE',identity=identity,conditions=cases,R_steps=11640,H_steps=11640,atomic_commits=11640,
                original_weights_unchanged=True,HR_gate_all_steps_checked=True,Full_used_in_production=False,native_H_production_updates=0)
            dump(dest/'result.json',result);seal(dest);allresults.append(result);del trace,adapter,service;torch.cuda.empty_cache()
    assert all(file_hash(BUNDLE/e['path'])==e['sha256'] for e in entries)
    assert all(file_hash(HERE/path)==sha for path,sha in code.items())
    dump(out/'result.json',dict(status='PASS_FORMAL_24_CONDITION_PROCESS',repeat=args.repeat,pid=os.getpid(),condition_runs=96,steps=46560,
        wall_s=time.monotonic()-start,candidate_modes=[dict(candidate=r['identity']['candidate_id'],mode=r['identity']['mode'],run_id=r['identity']['run_id']) for r in allresults],
        software_acceptance='PENDING_NEW_HOOK_FAULTS_AND_REPEAT_AUDIT',FPGA_execution=False))
    seal(out);print('FORMAL_DONE',args.repeat,time.monotonic()-start,flush=True)

if __name__=='__main__':
    try:main()
    except BaseException as exc:
        from failure_record import record
        record(ACTIVE_CONTEXT,exc)
        raise
