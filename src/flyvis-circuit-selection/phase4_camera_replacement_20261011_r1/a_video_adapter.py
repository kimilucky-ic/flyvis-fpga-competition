"""Forward R-only from current state; camera input is already frozen, no preprocessing."""
from common import *

class BoundRService:
    def init__(self):
        self.slot=require_camera_slot()
        agreement=load(HERE/'A_ACCEPTED_REFERENCE.json')
        assert agreement['status']=='PASS_SAME_CAMERA_MODEL_STATE_INPUT_IDENTITY'
        from r_only import RStepService
        self.service=RStepService(BUNDLE/'expanded_parameters.npz',BUNDLE/'identity_manifest.json',
            BUNDLE/'candidates/B_T5c/candidate_manifest.json',device='cuda')
        self._tensor_names=('_r','_source','_target','_weight','_bias','_tau','_inv_tau','_input_r','_hex_index')
        self._parameter_digests={name:array_hash(getattr(self.service,name).detach().cpu().numpy()) for name in self._tensor_names}
    def __getattr__(self,name):return getattr(self.service,name)
    def assert_weights_unchanged(self):
        for name,digest in self._parameter_digests.items():
            assert array_hash(getattr(self.service,name).detach().cpu().numpy())==digest,name
    def step(self,old,frame,*,step_id,run_id,condition_id):
        require_step_time(self.slot)
        assert condition_id==CONDITION
        expected=np.load(BUNDLE/'stimulus.npy',mmap_mode='r')[0,step_id,0]
        assert np.array_equal(frame.detach().cpu().numpy(),expected)
        return self.service.step(old,frame,step_id=step_id,run_id=run_id,condition_id=condition_id)
