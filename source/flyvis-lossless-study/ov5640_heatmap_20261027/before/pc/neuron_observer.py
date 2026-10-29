"""Read-only PC observations from already validated full FPGA state records."""
import hashlib,json
from pathlib import Path
import numpy as np
MAP_SHA='3c8b887e1bcb867f75ed064f5c7f81603d10246e1fe51b2d03922ee5c544ab4f'
class Observer:
    def init__(self,path):
        data=Path(path).read_bytes()
        if hashlib.sha256(data).hexdigest()!=MAP_SHA:raise ValueError('Observer map identity')
        self.map=json.loads(data);self.ids=[np.asarray(r['ids'],dtype=np.intp) for r in self.map['regions']]
        if len(self.ids)!=2 or any(a.shape!=(14,n) or np.any(a<0) or np.any(a>=45669) for a,n in zip(self.ids,[37,721])):raise ValueError('Observer IDs')
    def means(self,bits):
        if len(bits)!=45669*4:raise ValueError('Observer state size')
        state=np.frombuffer(bits,'<f4');out=[]
        for ids in self.ids:
            selected=state[ids]
            if not np.isfinite(selected).all():raise ValueError('Nonfinite observer state')
            out.append(np.mean(selected,axis=1,dtype=np.float64).tolist())
        return out
    def packet(self,bits,reference,reference_sha,state_sha,step):
        return dict(schema='line11-neuron-observer/v2',map_sha256=MAP_SHA,step_id=step,state_sha256=state_sha,
                    means=self.means(bits),reference=reference,reference_step_id=0,reference_state_sha256=reference_sha)
