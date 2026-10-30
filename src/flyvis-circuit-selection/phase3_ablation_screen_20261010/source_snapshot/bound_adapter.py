"""Norm-bound request/response envelope around the stateless GPU HR gate.

Array payloads are real old state and frame. Logs keep their hashes; full committed
trajectories plus frozen a0/frames reconstruct every payload without duplication.
"""
from common import *
from gpu_adapter import GPUAdapter
from dataclasses import replace

class BoundAdapter(GPUAdapter):
    def init__(self,service,inputs,identity):
        super().init__(service,inputs);self.identity=dict(identity);self.last_envelope=None
    def request(self,old,x,tag):
        return dict(**self.identity,run_id=tag.run_id,condition_id=tag.condition_id,step_id=tag.step_id,old_state_step_id=tag.step_id,
            old_full=old,hex_frame=x[self.input_ids[0]],old_full_digest=tag.old_full_digest,dt_s=.005,device=str(self.service.device),
            HR_release_gain=0 if self.service.mode=='Ablation' and tag.step_id>=self.service.start_step else 1)
    def check_request(self,q,tag):
        for key,value in self.identity.items():
            if q.get(key)!=value:raise StepError('IDENTITY_MISMATCH',key)
        for key,value in dict(run_id=tag.run_id,condition_id=tag.condition_id,step_id=tag.step_id,old_state_step_id=tag.step_id,
            old_full_digest=tag.old_full_digest,dt_s=.005,device=str(self.service.device),
            HR_release_gain=0 if self.service.mode=='Ablation' and tag.step_id>=self.service.start_step else 1).items():
            if q.get(key)!=value:raise StepError('IDENTITY_MISMATCH',key)
        if array_hash(q['old_full'])!=tag.old_full_digest:raise StepError('STATE_MISMATCH','old state payload')
    def evaluate(self,old,x,tag):
        q=self.request(old,x,tag);self.check_request(q,tag)
        result=super().evaluate(q['old_full'],x,tag)
        response=dict(run_id=tag.run_id,condition_id=tag.condition_id,step_id=tag.step_id,candidate_manifest_sha256=self.service.candidate_sha256,
            spec_sha256=self.identity['spec_sha256'],operator=self.identity['operator'],mode=self.service.mode,HR_release_gain=q['HR_release_gain'],
            global_node_indices=result.r_global_ids,activity=result.new_r,status='CANDIDATE_NOT_COMMITTED')
        self.check_response(response,q)
        self.last_envelope={k:v for k,v in q.items() if k not in ('old_full','hex_frame')}
        self.last_envelope.update(hex_frame_digest=array_hash(q['hex_frame']),candidate_response_activity_digest=array_hash(result.new_r),
            candidate_response_ids_digest=array_hash(result.r_global_ids),candidate_response_status=response['status'])
        return replace(result,evidence=dict(result.evidence,norm_binding=self.last_envelope,gate=dict(self.service.last_gate_evidence)))
    def check_response(self,response,q):
        for key in ['run_id','condition_id','step_id','candidate_manifest_sha256','spec_sha256','operator','mode','HR_release_gain']:
            if response.get(key)!=q[key]:raise StepError('IDENTITY_MISMATCH','response '+key)
        if response['status']!='CANDIDATE_NOT_COMMITTED':raise StepError('IDENTITY_MISMATCH','response status')
        if not np.array_equal(response['global_node_indices'],self.service.r_indices):raise StepError('LAYOUT_MISMATCH','response R order')
        if not np.isfinite(response['activity']).all():raise StepError('NONFINITE','response R')

def make_identity(name,mode):
    reg=load(HERE/'PRE_RUN_REGISTRATION.json');spec=load(HERE/'spec_snapshot/spec_config.json');candidate=spec['candidates'][name]
    return dict(campaign_id=reg['campaign_id'],comparison_id=reg['comparison_ids'][name],candidate_id=name,
        candidate_manifest_sha256=candidate['candidate_manifest']['sha256'],HR_edge_ids_sha256=candidate['HR_edge_ids']['sha256'],
        spec_sha256=reg['spec_sha256'],operator=spec['operator'],mode=mode,activation_step_id=200,
        parameter_profile_sha256=spec['model']['expanded_parameters_sha256'],stimulus_sha256=spec['fixture']['stimulus_sha256'],
        initial_state_sha256=spec['model']['initial_state_sha256'])
