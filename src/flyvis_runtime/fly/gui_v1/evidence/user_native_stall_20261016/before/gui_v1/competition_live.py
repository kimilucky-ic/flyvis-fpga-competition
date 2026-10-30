"""Verified stream packets -> line 10's existing skeletons, with no image codec.

This is a graphics consumer of StreamBridge, not another neural coordinator.
Importing it never starts a service or a GPU. Legacy replay is independent.
"""
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import time
import uuid
from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.request import Request

import numpy as np
from competition_renderer import CompetitionRenderer
from data_store import ROOT
from live_protocol import HERE, load, require, sha, write

WIRE = 'json32le+rgba8-v1'
MAX_RAW = 4_000_000
SERVICE_REL = 'live_canvas_cpu_20261015/service.py'
SERVICE_SHA = '235b53a7bdfab805e9d4dd69d25316c1bb62aa0ea5ec708b667d008e24085571'
GUARD_REL = 'live_canvas_cpu_20261015/research_guard.py'
GUARD_SHA = '473018fcebc32ed43d4b2c4a722666f1a78b401870b1971be3abd7a5cf16f595'
FIXED_REL = 'live_canvas_cpu_20261015/fixed_cpu.py'
FIXED_SHA = '7c602ee2c117b20d18325525e6caf8b310221c25a3f33a27597395bc334b3f68'
GUARD_POLICY = 'line10.wsl_readonly_argv.v2'
ENCODING_SHA = '066bde4a6de02bfc3a59c09fd24e8bfc26d82e5c0973762b204e5d62783fdab2'


def verify_source_receipt(value):
    raw=value.get('source_code_sha256',{})
    require(isinstance(raw,dict) and len(raw)<=16,'RAW_SERVICE_SOURCE_PATH')
    pins={}
    for name,digest in raw.items():
        require(isinstance(name,str),'RAW_SERVICE_SOURCE_PATH')
        key=name.replace('\\','/')
        require(':' not in key and all(part not in ('','.','..') for part in key.split('/'))
                and key not in pins,'RAW_SERVICE_SOURCE_PATH')
        pins[key]=digest
    require(pins.get(SERVICE_REL)==SERVICE_SHA and pins.get(GUARD_REL)==GUARD_SHA and pins.get(FIXED_REL)==FIXED_SHA,'RAW_SERVICE_SOURCE_IDENTITY')


def raw_frame(blob):
    require(4 < len(blob) <= MAX_RAW, 'RAW_FRAME_BOUND')
    n = struct.unpack_from('<I', blob)[0]
    require(0 < n <= 100_000 and 4+n < len(blob), 'RAW_HEADER_BOUND')
    r = json.loads(blob[4:4+n]); pixels = blob[4+n:]
    w, h = r['image_width'], r['image_height']
    require(type(w) is int and type(h) is int and 320 <= w <= 1280 and 240 <= h <= 640, 'RAW_DIMENSIONS')
    require(r['wire_format'] == WIRE and r['pixel_format'] == 'RGBA8'
            and r['row_order'] == 'top-down' and r['channel_order'] == 'RGBA'
            and r['row_stride'] == w*4 and r['byte_length'] == len(pixels) == w*h*4, 'RAW_LAYOUT')
    require(hashlib.sha256(pixels).hexdigest() == r['raw_sha256'], 'RAW_PIXELS_SHA')
    return r, pixels


def means_from_packet(bridge, body):
    require(set(body) == {'run_id','session_id','serial','step_id','state_token','request_id'}, 'IDENTITY_ONLY_REQUEST')
    require(type(body['serial']) is int and type(body['step_id']) is int and type(body['state_token']) is int, 'FRAME_INDEX_TYPE')
    require(isinstance(body['request_id'], str) and 0 < len(body['request_id']) <= 128, 'REQUEST_ID')
    with bridge.lock:
        require(bridge.status()['result_valid'], 'STREAM_RESULT_REVOKED')
        p = bridge.packets.get(body['serial'])
        require(p is not None, 'STREAM_PACKET_EXPIRED')
        require(all(p[k] == body[k] for k in ('run_id','session_id','step_id','state_token')), 'RAW_REQUEST_RUN_STEP')
        bridge.validate(p)
        values = np.asarray(p['spatial']['values'], dtype='<f4')
        means = values.reshape(8,721).mean(axis=1, dtype=np.float64).tolist()
    return p, means


class LiveSkeleton(CompetitionRenderer):
    """Uses the original renderer owner's PID checks and cleanup, a new raw API."""
    def init__(self, bridge):
        super().init__(None)
        self.bridge = bridge; self.binding = None; self.folder = None; self.health = None; self.cached = None

    def call(self, path, body=None):
        data = json.dumps(body, allow_nan=False).encode() if body is not None else None
        req = Request(self.ready['url']+path, data=data,
                      headers={'Content-Type':'application/json','X-Line10-Owner':self.token})
        try:
            with self.opener.open(req, timeout=20) as response:
                limit=16_000_000 if path=='/projection_cache' else MAX_RAW
                require(0 < int(response.headers['Content-Length']) <= limit, 'RAW_RESPONSE_BOUND')
                blob = response.read(limit+1)
                if path=='/projection_cache':return blob
                if path == '/render_raw':
                    require(response.headers.get('X-Line10-Wire') == WIRE, 'RAW_WIRE_HEADER')
                    return blob
                return json.loads(blob)
        except HTTPError as e:
            raise ValueError('SKELETON_SERVICE: '+e.read(10000).decode('utf-8', errors='replace')) from e

    def _lease(self):
        # Only explicitly owned instances are exempted by line 10's resource guard.
        import psutil
        a = self.bridge.adapter; active = load(HERE/'runtime/demo_active.json')
        require(active['session_id'] == a.session['session_id'] and active['state'] == 'RUNNING', 'GRAPHICS_SESSION_OWNER')
        parent = psutil.Process(os.getpid()); processes = {}
        for child in active['children']:
            if child['name'] != 'worker':continue
            p = psutil.Process(child['pid'])
            require(p.name().lower() == 'wsl.exe' and p.ppid() == active['pid'], 'OWNED_WSL_REQUIRED')
            for q in [p]+p.children(recursive=True):processes[q.pid] = dict(pid=q.pid,create_time=q.create_time())
        require(processes, 'OWNED_GPU_WORKER_REQUIRED')
        lease = dict(schema='line10.gpu_coordinator.v1',parent_pid=parent.pid,parent_create_time=parent.create_time(),
                     session_id=a.session['session_id'],expires_unix=datetime.fromisoformat(a.session['end_utc']).timestamp(),
                     allowed_processes=list(processes.values()))
        path = self.folder/'coordinator_lease.json'; write(path,lease); return path

    def prepare(self, body):
        require(set(body) == {'renderer'} and body['renderer'] in ('gpu','cpu'), 'EXPLICIT_GRAPHICS_BACKEND')
        require(self.bridge is not None, 'STREAM_NOT_CONNECTED')
        self.bridge.adapter.connected()
        require(self.bridge.adapter.session.get('stream_enabled'), 'STREAM_ENTRY_REQUIRED')
        with self.lock:
            require(not self.closed, 'SKELETON_CLOSED')
            if self.ready:return self.health
            require(self.process is None and self.bridge.control is None, 'PREPARE_BEFORE_STREAM_ONLY')
            studio = ROOT/'flyvis-3d-studio'; base = studio/'activity_replay_20261014'
            source = base/SERVICE_REL
            python = studio/'anatomy_trial_20261013/.venv/Scripts/python.exe'
            require(source.is_file() and python.is_file(), 'LINE10_RAW_SERVICE_NOT_DELIVERED')
            require(sha(source)==SERVICE_SHA, 'LINE10_EXPLICIT_SERVICE_DELIVERY')
            require(sha(base/GUARD_REL)==GUARD_SHA, 'LINE10_EXPLICIT_GUARD_DELIVERY')
            require(sha(base/FIXED_REL)==FIXED_SHA, 'LINE10_EXPLICIT_FIXED_CPU_DELIVERY')
            model = load(base/'model.json'); objects = model['objects']; spatial = self.bridge.spatial
            require([o['type'] for o in objects] == spatial.data['types'], 'TYPE_ORDER')
            require([o['model_node_ids'] for o in objects] == spatial.ids.reshape(8,721).tolist(), 'EXACT_SKELETON_MODEL_NODE_MAP')
            self.folder = self.bridge.adapter.root/'skeleton';self.folder.mkdir(exist_ok=True)
            self.token = uuid.uuid4().hex; self.ready_path = self.folder/'ready.json'
            self.log = (self.folder/'renderer.log').open('w',encoding='utf-8')
            args = [str(python),'-B',str(source),'--renderer',body['renderer'],'--port','0','--width','960','--height','480',
                    '--owner-token',self.token,'--parent-pid',str(os.getpid()),'--ready-file',str(self.ready_path),
                    '--tag','gui_'+self.bridge.adapter.session['session_id']]
            if body['renderer']=='gpu':args += ['--gpu-lease-file',str(self._lease())]
            write(self.folder/'sources.json',dict(service=str(source),service_sha256=sha(source),guard=str(base/GUARD_REL),guard_sha256=GUARD_SHA,model_sha256=sha(base/'model.json'),
                                                  source_kind='ACTUAL_STREAM_GRAPHICS_CONSUMER',PL_execution=False))
            self.process = subprocess.Popen(args,stdout=self.log,stderr=subprocess.STDOUT,
                                           env=dict(os.environ,PYTHONUTF8='1'),creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            try:
                deadline = time.monotonic()+75
                while not self.ready_path.is_file():
                    require(self.process.poll() is None, 'SKELETON_START_FAILED: '+str(self.folder/'renderer.log'))
                    require(time.monotonic()<deadline, 'SKELETON_START_TIMEOUT');time.sleep(.05)
                h = load(self.ready_path); address = urlparse(h['url'])
                verify_source_receipt(h);require(h.get('resource_guard_policy')==GUARD_POLICY,'RAW_GUARD_POLICY')
                if body['renderer']=='cpu':require(h.get('fixed_cpu_projection_sha256') and h.get('fixed_cpu_projection'),'FIXED_CPU_CACHE_REQUIRED')
                require(self.owns_pid(h['pid']) and address.scheme=='http' and address.hostname=='127.0.0.1', 'SKELETON_OWNER_ADDRESS')
                self.ready=h; e=h['expected_binding']; reg=self.bridge.adapter.registry.data
                require(all(e[k]==reg['model'][k] for k in ('model_id','source_commit','checkpoint_sha256','expanded_parameters_sha256')), 'SKELETON_MODEL_IDENTITY')
                mapping = [dict(type=o['type'],body_id=o['body_id'],swc_sha256=o['swc_sha256'],model_node_ids=o['model_node_ids'],mapping=o['mapping']) for o in objects]
                mapping_sha=hashlib.sha256(json.dumps(mapping,sort_keys=True,separators=(',',':')).encode()).hexdigest()
                require(e['mapping_sha256']==mapping_sha and e['node_map_sha256']==reg['pins']['nodes']['sha256'], 'SKELETON_MAP_IDENTITY')
                require(e['types']==spatial.data['types'] and e['counts']==[721]*8 and e['aggregation']=='FP64_MEAN_ALL_NODES_PER_TYPE', 'SKELETON_AGGREGATION')
                require(h['wire_format']==WIRE and h['PL_execution'] is False, 'SKELETON_EVIDENCE')
                import psutil
                require(abs(psutil.Process(h['pid']).create_time()-h['pid_create_time'])<=.00001
                        and h['parent_pid']==os.getpid(), 'SKELETON_PROCESS_INSTANCE')
                require(h['color_encoding']['encoding_sha256']==ENCODING_SHA, 'FIXED_CONTRAST_DELIVERY')
                self.health=h
                if body['renderer']=='cpu':
                    from cached_skeleton import CachedSkeleton
                    blob=self.call('/projection_cache',dict(service_id=h['service_id']))
                    self.cached=CachedSkeleton(blob,h);(self.folder/'projection.cache').write_bytes(blob)
                    h['projection_cache']=dict(schema='flyvis-fixed-cpu-cache/v1',sha256=self.cached.sha256,bytes=len(blob),url='/api/competition-live/cache',upstream_map_sha256=self.bridge.spatial.digest)
                return h
            except BaseException:
                self.release();raise

    def render(self, body):
        with self.lock:
            require(self.ready is not None and not self.closed, 'SKELETON_NOT_PREPARED')
            self.bridge.touch(); p, means = means_from_packet(self.bridge,body)
            if self.binding is None:
                binding = dict(self.health['expected_binding'],session_id=p['session_id'],run_id=p['run_id'],dt_s=.005,
                               input_time_origin_s=0,upstream_map_sha256=p['spatial']['map_sha256'],source_evidence_level=p['evidence_level'])
                self.binding=self.call('/bind',binding);require(self.binding['binding']==binding,'RAW_BINDING_RECEIPT')
                write(self.folder/'binding.json',self.binding)
            b=self.binding['binding']
            command={k:b[k] for k in ('session_id','run_id','model_id','checkpoint_sha256','mapping_sha256','upstream_map_sha256')}
            command.update(bind_id=self.binding['bind_id'],request_id=body['request_id'],step_id=p['step_id'],state_token=p['state_token'],
                           activity_time_s=p['activity_time_s'],means=means,source_sequence=p['source']['sequence'],spatial_values_sha256=p['spatial']['values_sha256'])
            t=time.perf_counter();blob=self.call('/render_raw',command);r,pixels=raw_frame(blob)
            verify_source_receipt(r)
            require(r.get('fixed_cpu_projection_sha256')==self.health.get('fixed_cpu_projection_sha256'),'RAW_FIXED_PROJECTION_IDENTITY')
            require(all(r.get(k)==v for k,v in command.items()), 'RAW_RECEIPT_IDENTITY')
            require(r['service_id']==self.ready['service_id'] and r['color_encoding']==self.health['color_encoding'], 'RAW_SERVICE_ENCODING')
            require(r['source_evidence_level']==p['evidence_level'] and r['evidence_level']=='EXTERNAL_ACTIVITY_RENDER_ONLY'
                    and r['PL_execution'] is False and r['neural_computation_performed'] is False, 'RAW_EVIDENCE_BOUNDARY')
            require([s['value'] for s in r['type_states']]==means and r['types']==b['types'], 'RAW_REAL_MEANS')
            require(r['type_filter']=='all' and r['rois_visible'] and r['background_manifest_sha256']==self.health['background_manifest_sha256'], 'RAW_BACKGROUND_ALL_TYPES')
            # A stopped/revoked stream cannot publish a late image, even if its renderer succeeded.
            with self.bridge.lock:require(self.bridge.status()['result_valid'] and p['run_id']==self.bridge.control['run_id'], 'RAW_REVOKED_DURING_RENDER')
            receipt=dict(r,serial=p['serial'],verified_by='GUI_StreamBridge',windows_render_roundtrip_ms=(time.perf_counter()-t)*1000)
            # Bounded original pixel samples; no codec in the live display path.
            if not (self.folder/'first.rgba').exists():
                (self.folder/'first.rgba').write_bytes(pixels);write(self.folder/'first_receipt.json',receipt)
            for threshold in (500,1000):
                label=f'sample_{threshold}'
                if p['step_id']>=threshold and not (self.folder/(label+'.rgba')).exists():
                    (self.folder/(label+'.rgba')).write_bytes(pixels);write(self.folder/(label+'_receipt.json'),receipt)
            with (self.folder/'frames.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(receipt,allow_nan=False)+'\n')
            header=json.dumps(receipt,ensure_ascii=False,allow_nan=False,separators=(',',':')).encode('utf-8')
            return struct.pack('<I',len(header))+header+pixels

    def status(self):
        return dict(status='READY' if self.ready and self.process and self.process.poll() is None else 'NOT_CONNECTED',
                    prepared=self.health is not None,binding=self.binding,PL_execution=False,FPGA_status='NOT_CONNECTED')

    def cache(self):
        with self.lock:
            require(self.cached is not None and not self.closed,'PROJECTION_CACHE_NOT_PREPARED')
            return self.cached.blob

    def verify_cached_draw(self,body):
        """Recheck browser pixels against the exact committed packet before ACK.

        The expensive HTTP image response is absent. The CPU reference executes
        after the browser's recorded paint; no unverified frame is acknowledged.
        """
        if body.get('skeleton_wire')!='FIXED_CPU_CACHE_V1':return
        with self.lock:
            require(self.cached is not None and not self.closed,'PROJECTION_CACHE_NOT_PREPARED')
            require(body['skeleton_cache_sha256']==self.cached.sha256,'PROJECTION_DRAW_CACHE_IDENTITY')
            with self.bridge.lock:
                p=self.bridge.packets.get(body['serial']);require(p is not None,'STREAM_PACKET_EXPIRED')
                self.bridge.validate(p)
                require(self.bridge.status()['result_valid'],'DRAW_RESULT_REVOKED')
                require(p['run_id']==body['run_id'] and p['step_id']==body['step_id'],'PROJECTION_DRAW_IDENTITY')
                means=np.asarray(p['spatial']['values'],dtype='<f4').reshape(8,721).mean(axis=1,dtype=np.float64).tolist()
            t=time.perf_counter();rgba,states=self.cached.render(means,self.health);pixels=rgba.tobytes()
            pixel_sha=hashlib.sha256(pixels).hexdigest()
            require(pixel_sha==body['skeleton_raw_sha256'],'PROJECTION_DRAW_PIXELS_SHA')
            receipt=dict(schema='line10.live_raw.frame.v1',**{k:p[k] for k in ('run_id','session_id','serial','step_id','state_token','activity_time_s','input_time_s')},
                service_id=self.health['service_id'],request_id=body['skeleton_request_id'],source_sequence=p['source']['sequence'],
                spatial_values_sha256=p['spatial']['values_sha256'],upstream_map_sha256=p['spatial']['map_sha256'],means=means,
                color_encoding=self.health['color_encoding'],type_states=states,types=self.health['expected_binding']['types'],
                source_code_sha256=self.health['source_code_sha256'],fixed_cpu_projection_sha256=self.health['fixed_cpu_projection_sha256'],
                projection_cache_sha256=self.cached.sha256,rendering_method='fixed_SWCs_CPU_projection_composite',
                raw_sha256=pixel_sha,image_width=rgba.shape[1],image_height=rgba.shape[0],PL_execution=False,
                byte_length=len(pixels),color_update_ms=0.,draw_and_readback_ms=0.,draw_performed=False,
                raw_copy_ms=0.,fixed_cpu_compose_ms=(time.perf_counter()-t)*1000,total_render_raw_ms=(time.perf_counter()-t)*1000,
                windows_render_roundtrip_ms=0.,verified_by='GUI_StreamBridge_EXACT_BROWSER_PIXELS_AFTER_DRAW',source_evidence_level=p['evidence_level'],evidence_level='EXTERNAL_ACTIVITY_RENDER_ONLY')
            for label,threshold in [('first',0),('sample_500',500),('sample_1000',1000)]:
                if p['step_id']>=threshold and not (self.folder/(label+'.rgba')).exists():
                    (self.folder/(label+'.rgba')).write_bytes(pixels);write(self.folder/(label+'_receipt.json'),receipt)
            with (self.folder/'frames.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(receipt,allow_nan=False)+'\n')
