"""Stateless edge-current gate prototype; requires frozen external spec binding.

No final neural activity is zeroed. Original weights/HH/RH/RR are immutable.
Only selected original HR edge currents can be blocked before R scatter.
"""
import numpy as np
import torch
from r_only import RStepService,RStepResult,InterfaceError

class HRReleaseService(RStepService):
    def init__(self,*args,hr_edge_ids,start_step,mode,**kwargs):
        super().init__(*args,**kwargs)
        if mode not in ('Sham','Ablation'):raise InterfaceError('explicit intervention mode required')
        if type(start_step) is not int or start_step<0:raise InterfaceError('bad intervention step')
        hr=np.asarray(hr_edge_ids)
        if hr.dtype!=np.int64 or hr.ndim!=1 or not len(hr) or not np.all(np.diff(hr)>0):raise InterfaceError('HR original IDs must be ordered unique int64')
        with np.load(args[0]) as p:
            source=p['source_global'];target=p['target_global']
        hmask=np.zeros(self.n_nodes,dtype=bool);hmask[self.h_indices]=True
        actual_hr=np.flatnonzero(hmask[source]&~hmask[target]).astype(np.int64)
        if not np.array_equal(actual_hr,hr):raise InterfaceError('formal HR edge set differs from complete original H->R partition')
        local=np.searchsorted(self.original_edge_ids,hr)
        if not np.array_equal(self.original_edge_ids[local],hr):raise InterfaceError('HR edge missing from R partition')
        self._hr_local=torch.tensor(local,device=self.device,dtype=torch.int64)
        self.start_step,self.mode,self.hr_edge_ids=start_step,mode,hr.copy()
        self.last_gate_evidence=None
        self._original_weight=self._weight.clone()

    @torch.no_grad()
    def step(self,old_full,hex_frame,*,step_id,run_id,condition_id):
        self._check(old_full,self.n_nodes,'old_full')
        if type(step_id) is not int or step_id<0:raise InterfaceError('bad step_id')
        if not run_id or not condition_id:raise InterfaceError('identity required')
        x=self.external_r(hex_frame)
        original=self._weight*torch.relu(old_full.index_select(0,self._source))
        blocked=self.mode=='Ablation' and step_id>=self.start_step
        # Sham and Ablation use the same full-length mask and multiplication.
        gate=torch.ones_like(original)
        if blocked:gate[self._hr_local]=0
        edge_current=original*gate
        hr_before=original.index_select(0,self._hr_local)
        hr_after=edge_current.index_select(0,self._hr_local)
        if blocked and bool(torch.count_nonzero(hr_after)):raise InterfaceError('HR release not blocked')
        current=torch.zeros(self.n_r,dtype=torch.float32,device=self.device)
        current.scatter_add_(0,self._target,edge_current)
        old_r=old_full.index_select(0,self._r)
        velocity=self._inv_tau*(-old_r+self._bias+current+x)
        new_r=old_r+velocity*self.dt
        if not bool(torch.isfinite(new_r).all()):raise InterfaceError('nonfinite R candidate')
        self.last_gate_evidence=dict(step_id=step_id,gate_active=blocked,selected_original_HR_edges=len(self.hr_edge_ids),
            removed_hr_nonzero_terms=int(torch.count_nonzero(hr_before).item()) if blocked else 0,
            hr_before_abs_sum=float(hr_before.abs().sum().item()),hr_after_abs_sum=float(hr_after.abs().sum().item()),
            hr_before_signed_sum=float(hr_before.sum().item()),hr_after_signed_sum=float(hr_after.sum().item()),
            removed_hr_abs_sum=float(hr_before.abs().sum().item()) if blocked else 0.0,
            removed_hr_signed_sum=float(hr_before.sum().item()) if blocked else 0.0,
            selected_HR_gain=0 if blocked else 1,all_other_edge_gain=1,
            hr_after_nonzero_terms=int(torch.count_nonzero(hr_after).item()),
            applied_before_target_scatter=True,H_state_not_zeroed=True,HH_RH_RR_gate=1)
        return RStepResult(self._r.clone(),new_r,step_id,run_id,condition_id,self.candidate_sha256,self.checkpoint_sha256)

    def assert_weights_unchanged(self):
        if not torch.equal(self._weight,self._original_weight):raise InterfaceError('original weights changed')
