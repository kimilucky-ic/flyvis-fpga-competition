"""Small read-only consumer API, no GUI engine, network or compute fallback."""
from common import *


class AnimationResults:
    def init__(self,root=HERE/'gui_bundle'):
        self.root=Path(root);manifest_verify(self.root)
        self.info=load(self.root/'GUI_READONLY_HANDOFF.json')
        self.stimulus=np.load(self.root/'stimulus.npy',mmap_mode='r')
        self.time=np.load(self.root/'time.npy');self.after=np.load(self.root/'activity_time.npy')
        assert self.stimulus.shape==(1,800,1,721) and self.info['steps']==800
        self.arrays={}
        for mode in ['FullGPU','PythonReplacement']:
            identity=load(self.root/mode/'run_identity.json')
            assert identity['comparison_id']==self.info['comparison_id']
            self.arrays[mode]={group:np.load(self.root/mode/('activity_'+group+'.npy'),mmap_mode='r') for group in ['H','central','T4T5']}
            for group,n in [('H',67),('central',65),('T4T5',8)]:
                a=self.arrays[mode][group];assert a.shape==(800,n) and a.dtype==np.float32 and np.isfinite(a).all()

    def read_step(self,k):
        if type(k) is not int or not 0<=k<800:raise StepError('OUT_OF_ORDER','GUI step outside0..799')
        return dict(step_id=k,input_time_s=float(self.time[k]),activity_after_time_s=float(self.after[k]),
            stimulus=self.stimulus[0,k,0].copy(),comparison_id=self.info['comparison_id'],
            FullGPU={g:a[k].copy() for g,a in self.arrays['FullGPU'].items()},
            PythonReplacement={g:a[k].copy() for g,a in self.arrays['PythonReplacement'].items()},
            FPGAReplacement=self.info['mode_status']['FPGAReplacement'],display_mode='offline_replay_of_actual_computation')


if __name__=='__main__':
    obj=AnimationResults();checked=[]
    for k in [0,199,200,400,600,799]:
        step=obj.read_step(k);assert step['input_time_s']==k*.005 and step['activity_after_time_s']==k*.005+.005
        checked.append(k)
    for k in [-1,800,True]:
        try:obj.read_step(k);raise AssertionError('invalid GUI step accepted')
        except StepError as error:assert error.code=='OUT_OF_ORDER'
    dump(HERE/'GUI_READER_TEST.json',dict(status='PASS_READONLY_ARRAY_CONSUMER',steps_checked=checked,
        bad_steps_rejected=[-1,800,'bool'],FPGA_available=False,GUI_browser_verified=False,code_sha256=file_hash(Path(__file__))))
    print('GUI_READONLY_CONSUMER_PASS',checked)
