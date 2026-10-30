"""Original CUDA chemical + existing R-only. No H velocity/update or transport.

The original target_sum currently materializes all target currents. This bounded
correctness-first adapter extracts H after that reduction; RStepService separately
evaluates its original R edges. Redundant synaptic work is measured, not hidden.
"""
from contextlib import contextmanager
import numpy as np
from live_protocol import require
from live_worker import import_file


@contextmanager
def forbid_native_H(oracle):
    originals=[];count={'forbidden_calls':0}
    def reject(*args,**kwargs):
        count['forbidden_calls']+=1
        raise ValueError('NATIVE_H_UPDATE_FORBIDDEN_IN_HYBRID')
    for obj,name in ((oracle,'step'),(oracle.net,'_next_state'),(oracle.net.dynamics,'write_state_velocity')):
        originals.append((obj,name,getattr(obj,name)));setattr(obj,name,reject)
    try:yield count
    finally:
        for obj,name,method in reversed(originals):setattr(obj,name,method)


class GPUCandidates:
    def init__(self,registry,contract,oracle,torch,timing):
        self.reg=registry;self.c=contract;self.oracle=oracle;self.torch=torch;self.timing=timing
        R=import_file('gui_hybrid_original_r',registry.path_for('r_only')).RStepService
        self.r=R(registry.path_for('parameters'),registry.path_for('identity'),contract.paths['R5768_manifest'],device='cuda')
        require(np.array_equal(self.r.h_indices,contract.h) and np.array_equal(self.r.r_indices,contract.r),'GPU_PARTITION_ORDER')
        require(oracle.device.type=='cuda' and not oracle.net._state_hooks,'ORIGINAL_CUDA_REQUIRED')
        self.h=torch.as_tensor(contract.h.copy(),dtype=torch.int64,device=oracle.device)
        self.calls=0;self.native_H_update_count=0
        self.r_identity=self.r_digest()

    def r_digest(self):
        import hashlib
        digest=hashlib.sha256()
        for name,value in sorted(vars(self.r).items()):
            if isinstance(value,self.torch.Tensor):
                digest.update(name.encode()+str(value.dtype).encode()+value.detach().cpu().contiguous().numpy().tobytes())
        return digest.hexdigest()

    def produce(self,old_full,hex_frame,*,run_id,step_id,condition_id='ON60'):
        torch=self.torch;o=self.oracle;net=o.net
        self.r._check(old_full,45669,'old_full');self.r._check(hex_frame,721,'hex_frame')
        require(not bool(((hex_frame<0)|(hex_frame>1)).any()),'INPUT_RANGE')
        old_version=old_full._version;input_version=hex_frame._version
        with torch.no_grad(),forbid_native_H(o) as guard:
            with self.timing.measure('original_chemical_host_with_sync'):
                state=net._state_api(o.AutoDeref(nodes=o.AutoDeref(activity=old_full.reshape(1,-1)),edges=o.AutoDeref()))
                # These exact original functions contain no neuron integration.
                chemical=net.target_sum(net.dynamics.currents(state,o.params))[0].index_select(0,self.h)
                torch.cuda.synchronize()
            with self.timing.measure('original_R_only_host_with_sync'):
                result=self.r.step(old_full,hex_frame,step_id=step_id,run_id=run_id,condition_id=condition_id)
                torch.cuda.synchronize()
            net.stimulus.buffer.zero_();net.stimulus.add_input(hex_frame.reshape(1,1,1,721))
            x=net.stimulus()[:,0][0]
            with self.timing.measure('candidate_D2H'):
                arrays=dict(chemical_H=chemical.detach().cpu().numpy().copy(),new_R=result.activity.detach().cpu().numpy().copy(),
                    r_ids=result.global_node_indices.cpu().numpy().copy(),x_full=x.detach().cpu().numpy().copy())
        require(old_full._version==old_version and hex_frame._version==input_version,'OLD_STATE_OR_INPUT_MUTATED')
        require(result.status=='CANDIDATE_NOT_COMMITTED' and result.run_id==run_id and result.step_id==step_id
            and result.condition_id==condition_id and result.candidate_sha256==self.r.candidate_sha256,'R_RESULT_IDENTITY')
        require(all(np.isfinite(v).all() for v in arrays.values()),'NONFINITE_GPU_CANDIDATE')
        require(guard['forbidden_calls']==0,'NATIVE_H_EXECUTED')
        self.calls+=1
        return arrays

    def check_unchanged(self):
        self.oracle.assert_weights_unchanged()
        require(self.r_digest()==self.r_identity,'R_PARAMETERS_CHANGED')
