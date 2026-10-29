"""Bounded CPU audit/official decoder for received LIVE PL states, never a producer."""
import json
import os
from pathlib import Path
import queue
import subprocess
import sys
import threading
import numpy as np
from line11_ddr_flow import CPUDecoder, FlowConsumer, archive_frame, send, receive, read_exact, digest

HERE=Path(__file__).resolve().parent
STUDY=HERE.parent.parent/'fpga/flyvis-lossless-study'
INITIAL='d276601573420bf787a81ffa8c81f2da3499a20df2bb858f6082c2e449ff564f'


def reference_engine():
    pins={'engine.py':'74f88a84563bac1e20b851b7d505db0fab107527f7d57fb44aa8de68d256a29f',
          'codec.py':'e675b4eb7f594467518c9faf725b7706e45237d2b6a9afe0e94a5de6640fef64'}
    for name,pin in pins.items():
        if digest((STUDY/name).read_bytes())!=pin:raise ValueError('LIVE_CPU_REFERENCE_SOURCE_CHANGED')
    sys.path.insert(0,str(STUDY))
    from codec import read_template
    from engine import Engine
    template=STUDY/'runs/acceptance800_20261013/flyvis_template.bin'
    if digest(template.read_bytes())!='1d52e7dea2d244f69398cff81e14c120626f3f9a61694b84ad0259839acfd574':raise ValueError('LIVE_TEMPLATE_CHANGED')
    engine=Engine(read_template(template))
    if digest(engine.activity.tobytes())!=INITIAL:raise ValueError('LIVE_INITIAL_STATE_CHANGED')
    return engine


def audit_bits(engine,inp,state):
    expected=np.asarray(engine.advance(np.frombuffer(inp,dtype='<f4')),dtype='<f4').tobytes()
    if expected!=state:raise ValueError('LIVE_COMPLETE_45669_STATE_BIT_MISMATCH')


def worker(root):
    from contextlib import redirect_stdout
    wire=sys.stdout.buffer
    with redirect_stdout(sys.stderr):
        decoder=CPUDecoder(root/'cache');engine=reference_engine()
    send(wire,dict(status='CPU_DECODER_READY',identity=decoder.identity))
    k=0
    while True:
        meta=receive(sys.stdin.buffer)
        if meta.get('stop'):return
        inp=read_exact(sys.stdin.buffer,2884);bits=read_exact(sys.stdin.buffer,182676)
        if meta['frame_id']!=k or digest(inp)!=meta['input_sha256'] or digest(bits)!=meta['full_state_sha256']:raise ValueError('LIVE_AUDIT_PIPE_IDENTITY')
        with redirect_stdout(sys.stderr):
            audit_bits(engine,inp,bits)
            values=decoder.decode(np.frombuffer(bits,dtype='<f4').reshape(1,45669))[0]
        flow=values.astype('<f4',copy=False).tobytes()
        send(wire,dict(meta,**decoder.identity,flow_sha256=digest(flow),numerical_audit='FULL_STATE_BIT_EXACT'),flow)
        k+=1


class LiveCPUConsumer(FlowConsumer):
    """Reuse existing decoder/protocol/archive; bounded queue and variable stop."""
    def init__(self,output,callback):
        super().init__(output,callback)
        self.queue=queue.Queue(maxsize=32);self.final_count=None;self.ready=threading.Event()

    def finish_input(self):self.final_count=self.accepted

    def submit(self,snapshot):
        if self.error or self.stop.is_set():raise ValueError(self.error or 'LIVE_AUDITOR_CLOSED')
        try:self.queue.put_nowait(snapshot);self.accepted+=1
        except queue.Full:
            self.error='LIVE_AUDIT_QUEUE_FULL';self.state='FAILED';raise ValueError(self.error)

    def _run(self):
        try:
            with (self.output/'CPU_DECODER.log').open('xb') as log:
                env=dict(os.environ,CUDA_VISIBLE_DEVICES='-1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',NUMBA_NUM_THREADS='1')
                self.process=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'--worker',str(self.output)],
                    stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=log,env=env,cwd=str(HERE.parent),
                    creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
                hello=receive(self.process.stdout)
                if hello['status']!='CPU_DECODER_READY':raise ValueError('LIVE_CPU_NOT_READY')
                self.state='READY';self.ready.set()
                while not self.stop.is_set():
                    if self.final_count is not None and self.completed==self.final_count:break
                    try:snapshot=self.queue.get(timeout=.1)
                    except queue.Empty:continue
                    m,inp,bits,received,_=snapshot
                    binding=dict(run_id=m['run_id'],session_id=m['session_id'],frame_id=m['frame_id'],
                                 full_state_sha256=m['state_sha256'],input_sha256=digest(inp))
                    if binding['frame_id']!=self.completed:raise ValueError('LIVE_AUDIT_ORDER')
                    send(self.process.stdin,binding,inp+bits)
                    result=receive(self.process.stdout);flow=read_exact(self.process.stdout,5768)
                    if any(result.get(n)!=v for n,v in binding.items()) or digest(flow)!=result['flow_sha256'] or result['numerical_audit']!='FULL_STATE_BIT_EXACT':raise ValueError('LIVE_AUDIT_RETURN_IDENTITY')
                    archive_frame(self.output,snapshot,result,flow)
                    self.last_binding=binding;self.completed+=1
                    self.callback(snapshot,dict(values=np.frombuffer(flow,dtype='<f4').reshape(2,721).tolist(),
                                               sha256=digest(flow),binding=result))
                if self.stop.is_set():return
                send(self.process.stdin,{'stop':True})
                if self.process.wait(timeout=10):raise ValueError('LIVE_CPU_CHILD_FAILED')
                (self.output/'COMPLETE.json').write_text(json.dumps(dict(status='ALL_RECEIVED_STATES_AUDITED_AND_DECODED',
                    frames=self.completed,identity=hello['identity']))+'\n',encoding='utf-8')
                self.state='COMPLETE'
        except Exception as error:
            self.error=type(error).__name__+': '+str(error);self.state='FAILED';self.ready.set()
            try:
                (self.output/'FAILED.json').write_text(json.dumps(dict(status='FAILED_NUMERICAL_AUDIT_OR_DECODER',
                    error=self.error,accepted=self.accepted,completed=self.completed))+'\n',encoding='utf-8')
            except OSError:pass
        finally:
            if self.process and self.process.poll() is None:
                self.process.terminate()
                try:self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:self.process.kill();self.process.wait()


if __name__=='__main__':
    if len(sys.argv)!=3 or sys.argv[1]!='--worker':raise SystemExit('Explicit CPU audit/decoder worker only')
    worker(Path(sys.argv[2]))
