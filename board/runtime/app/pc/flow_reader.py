"""Official traced/frozen decoder: CPU only, display reads only, no board I/O."""
import os,json,hashlib,threading,time
from pathlib import Path
import numpy as np
class FlowReader:
    def __init__(self,assets):
        os.environ['CUDA_VISIBLE_DEVICES']='-1'
        import torch
        self.torch=torch;torch.set_num_threads(1)
        self.manifest=json.loads((Path(assets)/'official_flow_manifest.json').read_text(encoding='utf-8'))
        model=Path(assets)/'official_flow_cpu.pt'
        if hashlib.sha256(model.read_bytes()).hexdigest()!=self.manifest['artifact_sha256']:raise ValueError('Flow artifact identity')
        if self.manifest['checkpoint_sha256']!='d0e42857e738d0315897c2d50fde9eb3fb1a3fb1f071d55dfc13d53d72bccc3f':raise ValueError('Flow checkpoint identity')
        self.model=torch.jit.load(str(model),map_location='cpu').eval();self.lock=threading.Lock()
        with torch.inference_mode():self.model(torch.zeros(1,1,45669,device='cpu'))
    def packet(self,bits,state_sha,step):
        if len(bits)!=45669*4:raise ValueError('Flow state size')
        if hashlib.sha256(bits).hexdigest()!=state_sha:raise ValueError('Flow state hash')
        a=np.frombuffer(bits,'<f4')
        if not np.isfinite(a).all():raise ValueError('Nonfinite flow input')
        t=time.perf_counter()
        with self.lock,self.torch.inference_mode():
            out=self.model(self.torch.from_numpy(a.copy())[None,None]).numpy()[0,0].copy()
        if out.shape!=(2,721) or not np.isfinite(out).all():raise ValueError('Invalid decoded flow')
        return dict(schema='line11-official-flow/v1',status='READY',step_id=step,state_sha256=state_sha,checkpoint_sha256=self.manifest['checkpoint_sha256'],decoder_sha256=self.manifest['artifact_sha256'],axes=['right_positive','up_positive'],values=out.tolist(),values_sha256=hashlib.sha256(out.astype('<f4').tobytes()).hexdigest(),decode_ms=(time.perf_counter()-t)*1000,evidence='PC_CPU_DECODE_OF_SAVED_FPGA_STATE',velocity_calibrated=False)
