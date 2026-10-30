"""Read-only PC observations from already validated full FPGA state records."""
import hashlib,json
from pathlib import Path
import numpy as np
MAP_SHA='4282f4524df248aa27a313768813fe2062c6d4f3633db4470e5d6c1291360dc8'
class Observer:
    def init__(self,path):
        data=Path(path).read_bytes()
        if hashlib.sha256(data).hexdigest()!=MAP_SHA:raise ValueError('Observer map identity')
        self.map=json.loads(data);self.ids=np.asarray([r['ids'] for r in self.map['regions']],dtype=np.intp)
        if self.ids.shape!=(5,14,37) or np.any(self.ids<0) or np.any(self.ids>=45669):raise ValueError('Observer IDs')
    def means(self,bits):
        if len(bits)!=45669*4:raise ValueError('Observer state size')
        selected=np.frombuffer(bits,'<f4')[self.ids]
        if not np.isfinite(selected).all():raise ValueError('Nonfinite observer state')
        return np.mean(selected,axis=2,dtype=np.float64).tolist()
    def packet(self,bits,reference,reference_sha,state_sha,step):
        return dict(schema='line11-neuron-observer/v1',map_sha256=MAP_SHA,step_id=step,state_sha256=state_sha,
                    means=self.means(bits),reference=reference,reference_step_id=0,reference_state_sha256=reference_sha)
