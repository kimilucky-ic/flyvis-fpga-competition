"""Python3.8/stdlib display callback for the EXISTING FrameStepper.

No imports of PYNQ/FlyVis, neural math, board commands or retry. The human's
existing board loop supplies/validates retained state, then calls advance().
One persistent HTTP connection sends bytes; it never waits for GUI painting.
"""
import hashlib
import http.client
import json
import struct
from urllib.parse import urlparse


class Line11DisplayClient:
    def init__(self, connection):
        if connection['schema']!='flyvis-line11-gui-connection/v1':raise ValueError('Connection schema')
        self.config=dict(connection)
        target=urlparse(connection['url'])
        if target.scheme!='http' or target.username or target.password or target.path not in ('','/'):
            raise ValueError('Direct GUI HTTP origin required')
        self.http=http.client.HTTPConnection(target.hostname,target.port or 80,timeout=5)
        self.bound=False;self.failed=False;self.count=0;self.finished=False
        self.previous=connection['seed_state_sha256']

    def bind_retained_state(self, state_bits, completed_steps, boot_id):
        if self.bound or self.failed:raise RuntimeError('Display client already bound or failed')
        if (len(state_bits)!=182676 or hashlib.sha256(state_bits).hexdigest()!=self.previous
                or completed_steps!=1 or boot_id!=self.config['boot_id']):
            self.failed=True
            raise RuntimeError('Retained full PL state does not match accepted first step; no reset or retry')
        self.bound=True

    def _post(self, route, payload, mime):
        if self.failed or self.finished:raise RuntimeError('Display transport closed; no automatic retry')
        try:
            self.http.request('POST',route,body=payload,headers={'Authorization':'Bearer '+self.config['token'],'Content-Type':mime})
            reply=self.http.getresponse();data=reply.read(16385)
            if reply.status!=200 or len(data)>16384:raise RuntimeError('GUI rejected state: HTTP '+str(reply.status))
            return json.loads(data)
        except Exception:
            self.failed=True;self.http.close();raise

    def __call__(self, frame):
        if not self.bound or self.failed or self.finished:raise RuntimeError('Bind accepted retained state before advancing')
        try:
            k=self.config['first_frame_id']+self.count
            if self.count>=self.config['max_new_frames'] or frame.frame_id!=k or frame.completed_steps!=k+1:
                raise RuntimeError('Frame order/window mismatch; stop without retry')
            inp,state=bytes(frame.input_bits),bytes(frame.state_bits)
            if len(inp)!=2884 or len(state)!=182676:raise ValueError('Complete input and state required')
            state_sha=hashlib.sha256(state).hexdigest()
            meta=dict(schema='flyvis-line11-state-stream/v1',session_id=self.config['session_id'],run_id=self.config['run_id'],
                boot_id=self.config['boot_id'],frame_id=k,completed_steps=frame.completed_steps,
                previous_state_sha256=self.previous,input_sha256=hashlib.sha256(inp).hexdigest(),state_sha256=state_sha,
                compute_cycles=frame.compute_cycles,clock_hz=self.config['clock_hz'],faults=0,elapsed_seconds=frame.elapsed_seconds)
            header=json.dumps(meta,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
            receipt=self._post('/api/full-pl-stream/frame',struct.pack('<I',len(header))+header+inp+state,'application/octet-stream')
            if (receipt['status']!='RECEIVED_FOR_DISPLAY' or receipt['session_id']!=self.config['session_id']
                    or receipt['run_id']!=self.config['run_id'] or receipt['frame_id']!=k or receipt['full_state_sha256']!=state_sha):
                raise RuntimeError('Display receipt identity mismatch; this is NOT a neural COMMIT')
            self.previous=state_sha;self.count+=1
        except Exception:
            self.failed=True;self.http.close();raise

    def finish(self):
        body=dict(session_id=self.config['session_id'],run_id=self.config['run_id'],received_steps=self.count,
                  last_frame_id=self.config['first_frame_id']+self.count-1,full_state_sha256=self.previous)
        result=self._post('/api/full-pl-stream/finish',json.dumps(body).encode(),'application/json')
        if result['status']!='FINISHED_PRODUCER_REPORTED':self.failed=True;raise RuntimeError('Finish mismatch')
        self.finished=True;self.http.close()
        return result

    def close(self):
        self.http.close()
