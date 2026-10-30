"""GUI-owned lifecycle adapter around ⑩'s existing NAVis/Octarine scene.

No network/model implementation. The private helper renders already saved values.
"""
import base64
import json
import os
from pathlib import Path
import subprocess
import threading
import time
import uuid
import hashlib
import ctypes
from ctypes import wintypes
from urllib.parse import urlparse
from urllib.request import Request, build_opener, ProxyHandler
from urllib.error import HTTPError
from data_store import ROOT
from competition_replay import RUN, ACTIVITY_SHA
from scientific_pilot import require
from competition_policy import busy_reasons, presentation_policy


class CompetitionRenderer:
    def init__(self, replay):
        self.replay = replay
        self.lock = threading.RLock()
        self.process = None
        self.ready = None
        self.log = None
        self.closed = False
        self.config = None
        self.priority_reason = None
        self.monitor_stop = threading.Event()
        self.monitor = None
        self.policy_checked_at = -1e9
        self.policy_reasons = []
        self.opener = build_opener(ProxyHandler({}))

    def policy(self,profile):
        now=time.monotonic()
        if now-self.policy_checked_at>=1:
            self.policy_reasons=busy_reasons(ROOT);self.policy_checked_at=now
        reasons=self.policy_reasons
        compute=self.priority_reason or any('wsl.exe' in r or 'marker:' in r for r in reasons)
        config=presentation_policy(profile,bool(compute))
        if reasons and not compute and config['renderer']=='gpu':
            config=presentation_policy('light');config.update(degraded=True,reason='RESEARCH_RESOURCE_GUARD')
        config['resource_reasons']=reasons+([self.priority_reason] if self.priority_reason else [])
        return config

    def yield_for_compute(self):
        with self.lock:
            self.priority_reason='GPU_COMPUTE_REQUESTED; graphics yields until this GUI closes'
            if self.process:self.release()

    def watch_gpu(self):
        while not self.monitor_stop.wait(1):
            with self.lock:
                if self.closed:return
                if self.config and self.config['renderer']=='gpu' and busy_reasons(ROOT):
                    self.priority_reason='EXTERNAL_COMPUTE_OR_RESEARCH_RESOURCE_DETECTED'
                    self.release()

    def owns_pid(self,pid):
        if self.process.poll() is not None:return False
        if pid==self.process.pid:return True
        if os.name!='nt':return False
        # Windows venv python.exe redirects to an owned child; no extra package.
        class Entry(ctypes.Structure):
            _fields_=[('dwSize',wintypes.DWORD),('cntUsage',wintypes.DWORD),('pid',wintypes.DWORD),
                      ('heap',ctypes.c_size_t),('module',wintypes.DWORD),('threads',wintypes.DWORD),
                      ('parent',wintypes.DWORD),('priority',wintypes.LONG),('flags',wintypes.DWORD),('exe',wintypes.WCHAR*260)]
        kernel=ctypes.WinDLL('kernel32',use_last_error=True)
        kernel.CreateToolhelp32Snapshot.restype=wintypes.HANDLE
        kernel.Process32FirstW.argtypes=[wintypes.HANDLE,ctypes.POINTER(Entry)]
        kernel.Process32NextW.argtypes=[wintypes.HANDLE,ctypes.POINTER(Entry)]
        kernel.CloseHandle.argtypes=[wintypes.HANDLE]
        handle=kernel.CreateToolhelp32Snapshot(2,0)
        if handle==ctypes.c_void_p(-1).value:return False
        parents={};row=Entry();row.dwSize=ctypes.sizeof(row)
        try:
            ok=kernel.Process32FirstW(handle,ctypes.byref(row))
            while ok:
                parents[int(row.pid)]=int(row.parent)
                ok=kernel.Process32NextW(handle,ctypes.byref(row))
        finally:kernel.CloseHandle(handle)
        seen=set()
        while pid in parents and pid not in seen:
            seen.add(pid);pid=parents[pid]
            if pid==self.process.pid:return True
        return False

    def terminate_child(self,pid):
        if not self.owns_pid(pid):return
        kernel=ctypes.WinDLL('kernel32',use_last_error=True)
        kernel.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD]
        kernel.OpenProcess.restype=wintypes.HANDLE
        kernel.TerminateProcess.argtypes=[wintypes.HANDLE,wintypes.UINT]
        kernel.CloseHandle.argtypes=[wintypes.HANDLE]
        handle=kernel.OpenProcess(1,False,pid)
        if handle:
            try:kernel.TerminateProcess(handle,1)
            finally:kernel.CloseHandle(handle)

    def start(self,config):
        require(not self.closed, 'Renderer owner closed')
        if self.process:
            require(self.process.poll() is None, '3D renderer exited; reopen the application to retry')
            return
        studio = ROOT/'flyvis-3d-studio'
        python = studio/'anatomy_trial_20261013/.venv/Scripts/python.exe'
        scene = studio/'activity_replay_20261014/bridge.py'
        require(python.is_file() and scene.is_file(), '⑩ formal Octarine bridge unavailable')
        self.replay.get().unchanged()
        folder = ROOT/'gui_v1/runtime/competition'/uuid.uuid4().hex
        folder.mkdir(parents=True)
        self.token = uuid.uuid4().hex
        self.ready_path = folder/'ready.json'
        self.log = (folder/'renderer.log').open('w', encoding='utf-8')
        renderer=config['renderer']
        args = [str(python),'-B',str(scene),'--port','0','--width',str(config['width']),'--height',str(config['height']),
                '--renderer',renderer,'--profile',config['profile'],'--owner-token',self.token,'--ready-file',str(self.ready_path),
                '--tag','competition_'+folder.name,'--parent-pid',str(os.getpid())]
        environment=dict(os.environ,PYTHONUTF8='1')
        self.process = subprocess.Popen(args, stdout=self.log, stderr=subprocess.STDOUT,env=environment,
                                        creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        deadline = time.monotonic()+75
        while time.monotonic()<deadline:
            if self.ready_path.is_file():
                value = json.loads(self.ready_path.read_text(encoding='utf-8'))
                if value.get('status') != 'READY':raise ValueError(value.get('error','Renderer startup failed'))
                identity=value['identity']
                require(identity['run_id']==RUN and identity['activity_sha256']==ACTIVITY_SHA and self.owns_pid(value['pid']),
                        'Renderer startup identity mismatch')
                address=urlparse(value['url'])
                require(address.scheme=='http' and address.hostname=='127.0.0.1' and 1<=address.port<=65535,'Renderer loopback required')
                require(identity['activity_time_s']==self.replay.get().pilot.activity_time.tolist(),'Renderer full timeline mismatch')
                require(identity['model']==self.replay.get().pilot.identity['model'],'Renderer model mismatch')
                manifest=studio/'activity_replay_20261014/roi_lod_20261015/manifest.json'
                require(value['background_manifest_sha256']==hashlib.sha256(manifest.read_bytes()).hexdigest(),
                        'Renderer simplified-background manifest mismatch')
                self.ready=value
                self.config=config
                if renderer=='gpu' and self.monitor is None:
                    self.monitor=threading.Thread(target=self.watch_gpu,daemon=True,name='FlyVis graphics resource watcher');self.monitor.start()
                return
            if self.process.poll() is not None:
                self.log.flush()
                reason=(folder/'renderer.log').read_text(encoding='utf-8',errors='replace')
                if renderer=='gpu' and '科研任务正在使用资源' in reason:
                    self.log.close();self.process=None
                    self.priority_reason='RESOURCE_GUARD_DURING_GPU_START'
                    return self.start(presentation_policy('light',True))
                raise ValueError('3D renderer exited; see '+str(folder/'renderer.log'))
            time.sleep(.05)
        raise ValueError('3D renderer startup timed out; see '+str(folder/'renderer.log'))

    def call(self, path, body):
        payload=json.dumps(body,allow_nan=False).encode('utf-8')
        req=Request(self.ready['url']+path,data=payload,
                    headers={'Content-Type':'application/json','X-Owner-Token':self.token},method='POST')
        with self.opener.open(req,timeout=20) as response:
            require(int(response.headers['Content-Length'])<=8_000_000,'Bounded renderer response required')
            return json.loads(response.read(8_000_001))

    def render(self, body):
        with self.lock:
            replay=self.replay.get()
            replay.unchanged()
            k=body.get('frame_index')
            require(type(k) is int and 0<=k<485,'Frame outside admitted run')
            require(body.get('run_id')==RUN and body.get('activity_sha256')==ACTIVITY_SHA and
                    body.get('activity_time_s')==float(replay.pilot.activity_time[k]),'Render run/time mismatch')
            require(body.get('type_filter') in ['all','T4','T5']+list(replay.spatial.data['types']),'Unknown type filter')
            require(body.get('selected_type') in replay.spatial.data['types'],'Unknown selected type')
            require(isinstance(body.get('request_id'),str) and len(body['request_id'])<=64,'Request identity required')
            profile=body.get('presentation_profile','light')
            require(profile in ('light','standard'),'Unknown presentation profile')
            config=self.policy(profile)
            signature=lambda c:tuple(c[k] for k in ('renderer','profile','width','height'))
            if self.process and (self.process.poll() is not None or self.config is None or signature(config)!=signature(self.config)):self.release()
            self.start(config)
            body=dict(body,profile=self.config['profile'])
            try:value=self.call('/render',body)
            except HTTPError as error:
                detail=error.read(4096).decode('utf-8',errors='replace')
                if self.config['renderer']!='gpu' or 'RESEARCH_BUSY' not in detail:raise ValueError('3D renderer: '+detail) from error
                self.priority_reason='RESEARCH_BUSY; GPU graphics released'
                self.release();self.start(presentation_policy('light',True))
                body['profile']='light';value=self.call('/render',body)
            r=value['metadata']
            for key in ('run_id','activity_sha256','frame_index','activity_time_s','request_id','type_filter'):
                require(r[key]==body[key],'Renderer receipt mismatch: '+key)
            require(r['service_id']==self.ready['service_id'] and r['mapping_sha256']==self.ready['identity']['mapping_sha256'],'Renderer mapping/service mismatch')
            require([x['type'] for x in r['type_states']]==replay.spatial.data['types'],'Renderer type order mismatch')
            require([x['value'] for x in r['type_states']]==replay.means[k].tolist(),'Renderer activity differs from original run')
            require(r['PL_execution'] is False and r['evidence_level']=='OFFLINE_SOFTWARE_REPLAY','Renderer evidence mismatch')
            expected_types=[t for t in replay.spatial.data['types'] if body['type_filter']=='all' or t.startswith(body['type_filter'])]
            require(r['visible_types']==expected_types,'Renderer visible type set differs from requested group')
            require(r['profile']==self.config['profile'] and r['rois_visible']==self.config['background_rois'] and
                    r['background_style']==self.config['background_style'],'Presentation/background identity mismatch')
            require(r['background_manifest_sha256']==self.ready['background_manifest_sha256'],
                    'Renderer background manifest changed during session')
            from competition_frames import validate_encoding
            validate_encoding(r['color_encoding'], replay.means)
            image=base64.b64decode(value['png_base64'],validate=True)
            require(image.startswith(b'\x89PNG\r\n\x1a\n') and len(image)<=5_000_000,'Bounded PNG required')
            require(hashlib.sha256(image).hexdigest()==r['png_sha256'],'Renderer PNG identity mismatch')
            r['color_scale']=r['scale']
            r['presentation_policy']=dict(self.config)
            r['requested_profile']=profile
            return dict(status='VERIFIED',receipt=r,image_url='data:image/png;base64,'+value['png_base64'])

    def release(self):
        with self.lock:
            if self.process and self.process.poll() is None:
                if self.ready:
                    try:self.call('/stop',{'owner_token':self.token,'service_id':self.ready['service_id']})
                    except (OSError,ValueError):pass
                try:self.process.wait(timeout=8)
                except subprocess.TimeoutExpired:
                    # Only this GUI's child, never an existing standalone ⑩ viewer.
                    # Windows venv launcher can own the actual Python child PID.
                    if self.ready and self.owns_pid(self.ready['pid']):
                        self.terminate_child(self.ready['pid'])
                    self.process.terminate()
                    self.process.wait(timeout=5)
            if self.log:self.log.close()
            self.process=None;self.ready=None;self.config=None;self.log=None

    def close(self):
        with self.lock:
            if self.closed:return
            self.closed=True;self.monitor_stop.set();self.release()
