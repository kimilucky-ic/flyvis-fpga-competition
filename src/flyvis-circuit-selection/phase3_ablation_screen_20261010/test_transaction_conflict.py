"""New-gate conflicting duplicate prepare and wrong payload identity; fail closed."""
import uuid
from common import *

def main():
    out=HERE/'artifacts/formal_conflict_tests'
    if out.exists():raise SystemExit('Preserve existing evidence')
    out.mkdir(parents=True);torch=configure_gpu()
    from gate_service import HRReleaseService
    from bound_adapter import BoundAdapter,make_identity
    from coordinator import Coordinator
    results=[]
    initial=np.load(BUNDLE/'initial_state_full.npy');stim=np.load(BUNDLE/'stimulus.npy')
    for name in ['B_T5c','A_T4c','C_T4T5_all_centers']:
        cp=BUNDLE/'candidates'/name;h=HUpdater(cp/'static_boundary_gpu_native.npz');inp=validate_parameters(h,BUNDLE/'expanded_parameters.npz');hr=np.load(HERE/'spec_snapshot'/(name+'_HR_edge_ids.npy'))
        service=HRReleaseService(BUNDLE/'expanded_parameters.npz',BUNDLE/'identity_manifest.json',cp/'candidate_manifest.json',device='cuda',hr_edge_ids=hr,start_step=200,mode='Ablation')
        adapter=BoundAdapter(service,inp,make_identity(name,'Ablation'));co=Coordinator(h,adapter,initial,str(uuid.uuid4()),adapter.identity['comparison_id'],'0');co.next_step_id=200
        before=array_hash(co.state);x=input_full(stim[0,200,0],inp)
        with native_full_forbidden() as guard:
            first=co.prepare(200,x);conflict=x.copy();conflict[inp.reshape(-1)]=np.float32(.25)
            try:co.prepare(200,conflict);raise AssertionError('conflicting duplicate prepared')
            except StepError as error:assert error.code=='NOT_READY'
            assert co.status=='FAILED' and co.next_step_id==200 and co.pending is None and array_hash(co.state)==before
            try:co.commit(first);raise AssertionError('failed transaction committed')
            except StepError as error:assert error.code=='NOT_READY'
            assert co.next_step_id==200 and array_hash(co.state)==before and adapter.calls==1
        results.append(dict(candidate=name,status='PASS',test='conflicting_same_step_prepare_then_stale_commit',full_state_unchanged=True,R_single_commit=False,actual_GPU_R_calls=1,
            input_first_digest=array_hash(x),input_conflicting_digest=array_hash(conflict),events=co.logs,guard=guard))
        del service,adapter;torch.cuda.empty_cache()
    dump(out/'result.json',dict(status='PASS_FORMAL_CONFLICTING_DUPLICATE_REQUESTS',results=results,code_sha256=file_hash(Path(__file__)),FPGA_execution=False));seal(out)

if __name__=='__main__':main()
