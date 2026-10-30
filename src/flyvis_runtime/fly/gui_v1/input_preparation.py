"""Owned CPU converter preparation, concurrent with original GPU model loading."""
import os
from pathlib import Path
import subprocess
import sys
import time
from live_protocol import HERE,load,require,utc,validate_scope,write


def preparation_stopped(root):
    return any((root/name).exists() for name in ('STOP_REQUEST.json','GPU_STOP_REQUEST.json',
        'CONVERTER_STOP_REQUEST.json','stream/STOP_REQUEST.json'))


def wait_for_stream_endpoint(root,session,*,timeout_s=180):
    """CPU converter waits for model-ready RPC without acquiring camera input."""
    begin=time.monotonic()
    while True:
        require(not preparation_stopped(root),'INPUT_PREPARATION_STOP_REQUESTED')
        validate_scope(session);require(load(root/'session.json')==session,'INPUT_PREPARATION_SESSION_CHANGED')
        controller=load(root/'controller.json')
        require(controller['session_id']==session['session_id'] and time.time()-controller['unix_time']<15,'INPUT_PREPARATION_CONTROLLER_LOST')
        endpoint=root/'stream_endpoint.json'
        if endpoint.exists():
            data=load(endpoint);require(data['session_id']==session['session_id'],'INPUT_PREPARATION_ENDPOINT_SESSION')
            return data
        require(time.monotonic()-begin<timeout_s,'INPUT_PREPARATION_ENDPOINT_TIMEOUT');time.sleep(.05)


class PreparedConverter:
    def init__(self,root,session):
        self.root=Path(root);self.session=session;self.process=None;self.log=None;self.closed=False;self.attached=False
    def start(self):
        require(self.process is None and not self.closed,'INPUT_PREPARATION_ALREADY_STARTED')
        validate_scope(self.session);require(self.session.get('stream_enabled'),'INPUT_PREPARATION_STREAM_SCOPE')
        self.log=(self.root/'converter.log').open('ab')
        try:
            self.process=subprocess.Popen([sys.executable,'-B',str(HERE/'stream_renderer.py'),'--root',str(self.root)],
                stdout=self.log,stderr=subprocess.STDOUT,env=dict(os.environ,CUDA_VISIBLE_DEVICES='-1'))
            write(self.root/'converter_preparation.json',dict(schema='flyvis-input-preparation/v1',
                session_id=self.session['session_id'],pid=self.process.pid,started_utc=utc(),
                phase='CPU_CONVERTER_PARALLEL_WITH_MODEL',camera_opened=False,published_source_frames=0,neural_updates=0))
        except BaseException:
            if self.process is not None:self.close()
            else:self.log.close();self.log=None
            raise
        return self
    def check(self):
        require(not self.closed and self.process is not None and self.process.poll() is None,
            'INPUT_PREPARATION_EXITED_CHECK_CONVERTER_LOG')
    def attach(self):
        self.check();require(not self.attached,'INPUT_PREPARATION_ALREADY_ATTACHED');self.attached=True
        return self.process,self.log
    def close(self):
        if self.closed:return
        write(self.root/'CONVERTER_STOP_REQUEST.json',dict(session_id=self.session['session_id'],utc=utc()))
        forced=False;exit_code=None
        try:
            if self.process is not None:
                try:exit_code=self.process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    # Exact owned child has CUDA visibility disabled; never a GPU worker.
                    forced=True;self.process.terminate();exit_code=self.process.wait(timeout=5)
        finally:
            if self.log:self.log.close()
            self.closed=True
            write(self.root/'converter_shutdown.json',dict(session_id=self.session['session_id'],
                exit_code=exit_code,forced_owned_CPU_termination=forced,utc=utc(),camera_operations=0))
