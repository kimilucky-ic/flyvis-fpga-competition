"""Approved full ON60 experiment profile. Reuses original GPU/R/Coordinator/PL ABI."""
from datetime import datetime,timezone
import numpy as np
from hybrid_v2 import V2Contract
from live_protocol import HERE,Registry,require,canonical,sha,load,host_path

SOURCE_NAMES=['hybrid_full485.py','hybrid_full485_run.py','hybrid_joint_run.py','hybrid_joint.py','hybrid_joint_evidence.py',
              'hybrid_a3.py','hybrid_gpu.py','hybrid_v2.py','hybrid_joint_registry.json','board_actual_registry.json']
def source_pins():return {n:sha(HERE/n) for n in SOURCE_NAMES}

class Full485Contract(V2Contract):
    def init__(self):
        super().init__();self.reg=Registry()
        self.raw=np.load(self.reg.path_for('initial'),allow_pickle=False)
        require(self.raw.shape==(45669,) and self.raw.dtype==np.float32 and np.isfinite(self.raw).all(),'FROZEN_A0')
        self.raw.flags.writeable=False
    def initial(self):
        raw=self.raw.copy();words=self.wire.encode_activity(raw[self.h]);mixed=raw.copy();mixed[self.h]=self.decode(words)
        return mixed,words,raw

def validate_full_scope(s,c,acceptance,now=None):
    now=now or datetime.now(timezone.utc)
    require(s.get('schema')=='flyvis-approved-joint-full485/v1' and s.get('status')=='APPROVED_BY_HUMAN'
        and bool(s.get('human_authorization_reference')),'FULL485_NOT_AUTHORIZED')
    require(s.get('condition')=='ON60' and s.get('model_steps')==list(range(485))
        and s.get('max_requests')==s.get('max_commits')==485 and s.get('automatic_retry') is False,'EXACT_485_SCOPE')
    require(s.get('new_loads')==s.get('new_resets')==s.get('new_allocations')==0,'NO_LOAD_RESET_ALLOCATION')
    require(s.get('board_acceptance_sha256')==canonical(acceptance)
        and acceptance.get('status')=='PASS_INDEPENDENT_SAVED_BOARD_REPLAY','BOARD_ACCEPTANCE_REQUIRED')
    require(type(c) is Full485Contract and s.get('model')==c.registry['model']
        and s.get('bit_sha256')==c.wire.BIT_SHA and s.get('hwh_sha256')==c.wire.HWH_SHA
        and s.get('mapping_sha256')==c.mapping_sha and s.get('tolerance')==c.tolerance,'EXACT_FULL485_PROFILE')
    require(s.get('initial_file_sha256')==c.reg.data['model']['initial_state_sha256']
        and s.get('initial_kind')=='FROZEN_GRAY_ADAPTED_A0_QUANTIZE_H_ONCE','FROZEN_INITIAL_IDENTITY')
    require(s.get('endpoint')=={'host':'192.168.2.99','port':5768} and s.get('expected_boot_id')
        and s.get('expected_server_session') not in (None,'',acceptance['old_server_session'],'f6f0fc75d3304655adc9c9879be0249b'),'FRESH_FULL485_SESSION')
    begin=datetime.fromisoformat(s['start_utc']);end=datetime.fromisoformat(s['end_utc'])
    require(begin.tzinfo and end.tzinfo and 0<(end-begin).total_seconds()<=2700 and begin<=now<end,'FULL485_SCOPE_EXPIRED')
    require(s.get('max_worker_seconds')==2700 and s.get('max_compute_seconds')==2400
        and s.get('input_sha256')==c.reg.pins['stimulus_ON60']['sha256']
        and s.get('gpu_lease_id') and s.get('run_id') and s.get('comparison_id'),'RUN_INPUT_LIMITS')

class OriginalCPUCheck:
    """Independent same-old validation using the original R service and edge order.

    CPU results are never published as production neural activity.
    """
    def init__(self,reg,c,torch,timing):
        from live_worker import import_file
        self.torch=torch;self.timing=timing;self.c=c;self.frames=np.array(reg.input('ON60')[0,:,0],copy=True)
        R=import_file('gui_full485_cpu_original_R',reg.path_for('r_only')).RStepService
        self.r=R(reg.path_for('parameters'),reg.path_for('identity'),c.paths['R5768_manifest'],device='cpu')
        with np.load(reg.path_for('parameters'),allow_pickle=False) as z:
            mask=np.isin(z['target_global'],c.h);local=np.full(45669,-1,dtype=np.int64);local[c.h]=np.arange(5768)
            self.src=z['source_global'][mask].copy();self.dst=local[z['target_global'][mask]];self.weight=z['effective_weight'][mask].copy()
            self.input_ids=z['input_node_index'].copy()
        self.calls=0;self.max_r=0.;self.max_chemical=0.
    def check(self,old,output,k):
        torch=self.torch;frame=self.frames[k]
        with self.timing.measure('independent_CPU_same_old_check'):
            rr=self.r.step(torch.from_numpy(old.copy()),torch.from_numpy(frame.copy()),step_id=k,run_id='independent_reference',condition_id='ON60')
            r=rr.activity.numpy();chemical=np.zeros(5768,dtype=np.float32)
            np.add.at(chemical,self.dst,self.weight*np.maximum(old[self.src],np.float32(0)))
            x=np.zeros(45669,dtype=np.float32);x[self.input_ids]=frame
            require(np.array_equal(output['r_ids'],self.c.r) and np.array_equal(output['x_full'],x),'CURRENT_GPU_INPUT_MAP')
            er=float(np.max(np.abs(r-output['new_R'])));ec=float(np.max(np.abs(chemical-output['chemical_H'])))
            require(np.allclose(r,output['new_R'],atol=1e-5,rtol=1e-5),'R_CPU_COMPARISON_FAILED')
            require(np.allclose(chemical,output['chemical_H'],atol=1e-5,rtol=1e-5),'CHEMICAL_CPU_COMPARISON_FAILED')
        self.calls+=1;self.max_r=max(self.max_r,er);self.max_chemical=max(self.max_chemical,ec)
        return dict(status='PASS_ORIGINAL_CPU_SAME_OLD_REFERENCE',R_max_abs=er,chemical_max_abs=ec,atol=1e-5,rtol=1e-5,
                    neural_output_source='CURRENT_GPU_AND_PL_ONLY_NOT_THIS_REFERENCE')
