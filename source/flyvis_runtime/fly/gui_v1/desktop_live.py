"""Attach the existing WebView2 window to its exact manually launched session.

Never launches GPU/server/camera; the existing demo launcher owns those processes.
"""
import json
from pathlib import Path
import re
import threading
import time
from urllib.request import urlopen
from live_protocol import HERE,load,require,write,utc


class ManagedDesktopBackend:
    def init__(self,record,session_path):
        self.record=record;self.path=Path(session_path).resolve();self.root=self.path.parent
        require(self.root.parent==(HERE/'runtime/live').resolve() and self.path.name=='session.json'
                and re.fullmatch('[a-f0-9]{32}',self.root.name),'DESKTOP_SESSION_SCOPE')
        self.session=load(self.path);require(self.session['session_id']==self.root.name,'DESKTOP_SESSION_IDENTITY')
        self.stop=threading.Event();self.url=None;self.lock=threading.Lock()
        record.write('attaching_live',backend_owned_by_window=False,execution_kind='MANUAL_LIVE_GPU_SESSION',
                     live_session_id=self.session['session_id'],display_host='WINDOWS_DESKTOP_WEBVIEW2')

    def verify(self,body):
        require(body.get('schema')=='flyvis-live-capabilities/v1' and body.get('session_id')==self.session['session_id'],
                'DESKTOP_SERVER_SESSION_MISMATCH')
        return 'http://127.0.0.1:8771/#liveSkeleton' if self.session.get('skeleton_home') else 'http://127.0.0.1:8771/#liveCamera'

    def start(self):
        begin=time.monotonic()
        while not self.stop.is_set():
            require(not (self.root/'STOP_REQUEST.json').exists(),'DESKTOP_SESSION_STOPPED')
            try:
                with urlopen('http://127.0.0.1:8771/api/live',timeout=2) as response:
                    body=json.loads(response.read(262144))
            except OSError:
                require(time.monotonic()-begin<90,'DESKTOP_SERVER_START_TIMEOUT')
                self.stop.wait(.25);continue
            self.url=self.verify(body)
            self.record.write('ready',url=self.url,backend_owned_by_window=False,display_host='WINDOWS_DESKTOP_WEBVIEW2')
            return self.url

    def close(self):
        with self.lock:
            if self.stop.is_set():return
            self.stop.set()
            require(load(self.path)==self.session,'DESKTOP_SESSION_CHANGED')
            write(self.root/'STOP_REQUEST.json',dict(reason='OWNED_DESKTOP_WINDOW_CLOSED',utc=utc()))
            self.record.write('stop_requested',backend_stopped=False,CUDA_release='AWAIT_WORKER_ACK')
