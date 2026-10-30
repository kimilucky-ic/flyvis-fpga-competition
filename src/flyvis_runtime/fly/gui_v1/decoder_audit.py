"""Exact original decoder-state audit with one packed device readback per audit.
No decoder forward implementation, layer, mode, value or tolerance is changed.
"""
import numpy as np
from live_protocol import require


class PackedDecoderAudit:
    def init__(self,service,timing):
        self.service=service;self.torch=service.torch;self.timing=timing;self.original=service.assert_weights_unchanged;self.calls=0
        self.keys=list(service.before);self.spec={k:(v.shape,v.dtype) for k,v in service.before.items()}
        self.expected=np.concatenate([v.contiguous().reshape(-1).view(self.torch.uint8).numpy() for v in service.before.values()])
    def install(self):self.service.assert_weights_unchanged=self.check;return self
    def check(self):
        with self.timing.measure('decoder_exact_audit_one_D2H'):
            service=self.service;torch=self.torch
            require(not any(m.training for m in service.decoder.modules()),'DECODER_MODE_CHANGED')
            state=service.decoder.state_dict();require(list(state)==self.keys,'DECODER_STATE_KEYS_CHANGED')
            require(all((state[k].shape,state[k].dtype)==self.spec[k] and state[k].device.type=='cuda' for k in self.keys),'DECODER_STATE_SCHEMA_CHANGED')
            with torch.no_grad():
                packed=torch.cat([state[k].contiguous().reshape(-1).view(torch.uint8) for k in self.keys])
                actual=packed.cpu().numpy()
            require(np.array_equal(actual,self.expected),'DECODER_STATE_MUTATED')
            self.calls+=1
        return True
    def close(self):self.service.assert_weights_unchanged=self.original;self.original()
