"""Bind the real A video callable to the already accepted B GPUAdapter API."""
import importlib.util
from common import HERE,BUNDLE,load,file_hash,StepError,host_path


def backend(mode):
    acknowledgement=load(HERE/'A_B_STRICT_IDENTITY_CONFIRMATION.json')
    if acknowledgement['status']!='PASS_A_B_STRICT_IDENTITY_CONFIRMED_BY_B':
        raise StepError('MODEL_MISMATCH','A/B exact identities not confirmed')
    path=host_path(acknowledgement['A_backend_path'])
    if file_hash(path)!=acknowledgement['A_backend_sha256']:
        raise StepError('MODEL_MISMATCH','A backend changed since identity confirmation')
    spec=importlib.util.spec_from_file_location('A_single_video_backend',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    obj=module.SingleVideoBackend(host_path(acknowledgement['A_manifest_path']),mode=mode,
        comparison_id=acknowledgement['comparison_id'],device='cuda:0')
    own=load(BUNDLE/'video_manifest.json')
    if obj.comparison_id!=own['comparison_id']:raise StepError('MODEL_MISMATCH','wrong bound comparison')
    for key,field in [('stimulus_sha256','stimulus'),('initial_state_sha256','initial'),
        ('expanded_parameters_sha256','expanded'),('candidate_manifest_sha256','candidate')]:
        if obj.manifest[key]!=own['identity_fingerprint'][field]:raise StepError('MODEL_MISMATCH',key)
    return obj


class BoundRService:
    """No dynamics here; forwards only A r_only mode with frozen frame checks."""
    def init__(self):self.backend=backend('r_only')
    def __getattr__(self,name):return getattr(self.backend.service,name)
    def step(self,old_full,hex_frame,*,step_id,run_id,condition_id):
        return self.backend.step(old_full,hex_frame,step_id=step_id,run_id=run_id,
            condition_id=condition_id,comparison_id=self.backend.comparison_id)
