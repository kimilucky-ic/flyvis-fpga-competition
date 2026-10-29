"""Official all-node Full24 reference. Launch requires ratified human GPU window."""
import argparse,csv,os,platform,time
from common import *
from run_gate import require_launch,require_step_time,verify_frozen_files
ACTIVE_CONTEXT={}

def main():
    p=argparse.ArgumentParser();p.add_argument('--repeat',required=True,choices=['full_r1','full_r2'])
    p.add_argument('--preflight-only',action='store_true');args=p.parse_args()
    if args.preflight_only:
        identity=verify_frozen_files();manifest_verify(BUNDLE)
        print('PASS_STATIC_FULL_PREFLIGHT_ONLY',identity['campaign_id'],'GPU execution=0; neural updates=0');return
    ticket=require_launch()
    ACTIVE_CONTEXT.update(mode='Full',reference_repeat=args.repeat)
    out=HERE/'artifacts'/args.repeat
    if out.exists():raise SystemExit('Existing reference preserved; choose a new reviewed attempt')
    torch=configure_gpu()
    # Full oracle exists only here; replacement never imports this module.
    from full_oracle import FullNetworkOracle
    out.mkdir(parents=True)
    manifest_verify(BUNDLE);binding=load(HERE/'EXECUTION_BINDING.json')
    initial=np.load(BUNDLE/'initial_state_full.npy');stim=np.load(BUNDLE/'stimulus.npy',mmap_mode='r');clock=np.load(BUNDLE/'time.npy')
    assert initial.dtype==stim.dtype==np.float32 and stim.shape==(24,485,1,721)
    oracle=FullNetworkOracle(BUNDLE/'identity_manifest.json',device='cuda')
    identity=dict(run_id=binding['planned_Full_run_ids'][args.repeat],campaign_id=binding['campaign_id'],mode='Full',
        reference_repeat=args.repeat,pid=os.getpid(),proposal_sha256=binding['proposal_sha256'],
        checkpoint_sha256=binding['checkpoint_sha256'],expanded_parameters_sha256=binding['expanded_parameters_sha256'],
        initial_state_sha256=binding['initial_state_sha256'],stimulus_sha256=binding['stimulus_sha256'],time_sha256=binding['time_sha256'],
        dt_s=.005,shape=[24,485,45669],state_semantics='saved[k]=a[k+1], input[k] original time labels',
        python=platform.python_version(),torch=torch.__version__,numpy=np.__version__,gpu=torch.cuda.get_device_name(0),
        code_sha256={f:file_hash(HERE/f) for f in ['run_full.py','common.py','run_gate.py','dependencies/a_snapshot/full_oracle.py']},
        authority_sha256=ticket['authority_sha256'],command=[sys.executable,*sys.argv],
        evidence_level='ACTUAL_ORIGINAL_GPU_FULL_REFERENCE',FPGA_execution=False)
    dump(out/'run_identity.json',identity)
    trace=np.lib.format.open_memmap(out/'activities_full.npy',mode='w+',dtype=np.float32,shape=(24,485,45669))
    first=None
    if args.repeat=='full_r2':
        ref=HERE/'artifacts/full_r1';manifest_verify(ref)
        assert load(ref/'result.json')['status']=='PASS_REFERENCE_EXECUTION'
        assert load(ref/'run_identity.json')['campaign_id']==binding['campaign_id']
        first=np.load(ref/'activities_full.npy',mmap_mode='r')
    start=time.monotonic();steps=0;max_error=0.;violations=0;rows=[]
    torch.cuda.reset_peak_memory_stats()
    for c in range(24):
        ACTIVE_CONTEXT['condition']=c
        state=torch.tensor(initial,device='cuda',dtype=torch.float32)
        for k in range(485):
            require_step_time(ticket)
            candidate=oracle.step(state,torch.tensor(stim[c,k,0].copy(),device='cuda',dtype=torch.float32))
            require_step_time(ticket)
            state=candidate;actual=state.cpu().numpy();trace[c,k]=actual;steps+=1
            assert np.isfinite(actual).all()
            if first is not None:
                err=errors(actual,first[c,k],np.arange(45669))
                max_error=max(max_error,err['max_abs']);violations+=err['violations']
                rows.append(dict(condition=c,step_id=k,**err))
                assert err['violations']==0
        trace.flush();print('FULL_CONDITION',args.repeat,c,flush=True)
    oracle.assert_weights_unchanged();trace.flush()
    if rows:
        with (out/'repeat_step_errors.csv').open('w',newline='',encoding='utf-8') as f:
            writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    dump(out/'result.json',dict(status='PASS_REFERENCE_EXECUTION',identity=identity,conditions=24,steps=steps,
        all_finite=True,checkpoint_weights_unchanged=True,independent_reference_max_abs=max_error if first is not None else None,
        independent_reference_violations=violations if first is not None else None,
        wall_s=time.monotonic()-start,GPU_peak_allocated_bytes=torch.cuda.max_memory_allocated(),
        GPU_peak_reserved_bytes=torch.cuda.max_memory_reserved(),FPGA_execution=False,
        software_ablation_acceptance='NOT_EVALUATED_HERE'))
    seal(out)

if __name__=='__main__':
    try:main()
    except BaseException as exc:
        from failure_record import record
        record(ACTIVE_CONTEXT,exc)
        raise
