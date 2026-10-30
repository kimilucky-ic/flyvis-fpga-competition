"""Bridge B's snapshot semantics to A's stateless RStepService.

A code is loaded from a hash-recorded read-only snapshot in this lane.
Each evaluation copies the CURRENT merged state to CUDA; no R trajectory is read.
"""
import numpy as np
import torch
from h_step import StepError, frozen
from coordinator import RResult


class GPUAdapter:
    state_semantics = 'STATELESS_CANDIDATE_ONLY'
    def init__(self, service, input_node_index):
        self.service = service
        self.input_ids = input_node_index
        self.calls = 0
        self.evaluation_tags = []

    def evaluate(self, old_full, x_full, tag):
        frame = np.ascontiguousarray(x_full[self.input_ids[0]], dtype=np.float32)
        if not np.array_equal(x_full[self.input_ids], np.tile(frame, (8, 1))):
            raise StepError('INPUT_MISMATCH', 'photoreceptor rows do not share the signed hex input')
        mask = np.ones(len(x_full), dtype=bool)
        mask[self.input_ids.reshape(-1)] = False
        if np.any(x_full[mask] != 0):
            raise StepError('INPUT_MISMATCH', 'A service supports the canonical visual input only')
        old = torch.tensor(np.array(old_full, copy=True), device=self.service.device, dtype=torch.float32)
        stimulus = torch.tensor(frame, device=self.service.device, dtype=torch.float32)
        response = self.service.step(old, stimulus, step_id=tag.step_id,
            run_id=tag.run_id, condition_id=tag.condition_id)
        if response.status != 'CANDIDATE_NOT_COMMITTED' or response.step_id != tag.step_id or response.run_id != tag.run_id or response.condition_id != tag.condition_id:
            raise StepError('OUT_OF_ORDER', 'A response identity/status mismatch')
        if response.checkpoint_sha256 != self.service.checkpoint_sha256 or response.candidate_sha256 != self.service.candidate_sha256:
            raise StepError('MODEL_MISMATCH', 'A response identity mismatch')
        self.calls += 1
        self.evaluation_tags.append(tag)
        return RResult(tag, frozen(response.activity.detach().cpu().numpy()),
            frozen(response.global_node_indices.detach().cpu().numpy()), 0,
            dict(code_scope='A target-R filtered edge kernel; no native H next state',
                candidate_sha256=response.candidate_sha256, R_edge_count=self.service.n_r_edges,
                backend=str(self.service.device), status=response.status))
