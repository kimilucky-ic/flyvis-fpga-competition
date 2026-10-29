"""Owned loopback adapter: externally verified activity -> existing Octarine -> RGBA8.

This process performs graphics only. Source computation is verified by line 2.
No changes to frozen offline scene/bridge/presentation or the admitted frame pack.
"""
from pathlib import Path
from http.server import BaseHTTPRequestHandler,HTTPServer
from datetime import datetime,timezone
import argparse,hashlib,json,math,os,secrets,struct,sys,time,uuid
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
sys.path.insert(0,str(ROOT))
from scene import AnatomyScene,configure_renderer
from research_guard import research_guard, same_instance, POLICY
from fixed_cpu import FixedCPU
from presentation import verified_identity,sha,fixed_type_palette
import numpy as np
import psutil

WIRE='json32le+rgba8-v1'
SOURCE_LEVELS=('OFFLINE_SOFTWARE_REPLAY','ACTUAL_CONTINUOUS_FULL_GPU_STATE')

def canonical(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf-8')

def digest(value):return hashlib.sha256(canonical(value)).hexdigest()

class Rejected(ValueError):pass
class YieldResources(RuntimeError):pass

def require(value,message):
    if not value:raise Rejected(message)

def valid_sha(value):
    return isinstance(value,str) and len(value)==64 and all(c in '0123456789abcdef' for c in value)

def identifier(value):return isinstance(value,str) and 0<len(value)<=128
def number(value):return type(value) in (int,float) and math.isfinite(value)

def frame_wire(receipt,pixels):
    header=canonical(receipt)
    return struct.pack('<I',len(header))+header+pixels

class LiveRaw:
    def init__(self,args):
        self.args=args
        self.service_id=str(uuid.uuid4())
        self.identity=verified_identity(args.model)
        model=json.loads(args.model.read_text(encoding='utf-8'))
        node_source=next(s for s in model['sources'] if Path(s['path']).name=='nodes_full.csv')
        self.expected=dict(model_id=model['model']['model_id'],checkpoint_sha256=model['model']['checkpoint_sha256'],
                           source_commit=model['model']['source_commit'],expanded_parameters_sha256=model['model']['expanded_parameters_sha256'],
                           node_map_sha256=node_source['sha256'],mapping_sha256=self.identity['mapping_sha256'],
                           types=[o['type'] for o in model['objects']],counts=[o['count'] for o in model['objects']],
                           aggregation='FP64_MEAN_ALL_NODES_PER_TYPE')
        self.parent=psutil.Process(args.parent_pid) if args.parent_pid else None
        self.parent_created=self.parent.create_time() if self.parent else None
        self.binding=None
        self.bind_id=None
        self.last_step=-1
        self.last_signature=None
        self.last_receipt=None
        self.last_pixels=None
        self.draw_count=0
        self.cache_hits=0
        self.stopping=False
        self.last_guard=0.
        self.lease=None
        self.guard_state=None
        self.guard_audit_signature=None
        self.run=HERE/'evidence'/args.tag
        self.run.mkdir(parents=True,exist_ok=True)
        self.check_resources(force=True)
        if args.renderer=='gpu':
            # Only this explicit coordinator lease permits same-session CUDA + graphics.
            # Unlisted research processes and shared busy markers still block it.
            import wgpu
            from wgpu.utils import preconfigure_default_device
            adapters=wgpu.gpu.enumerate_adapters_sync()
            adapter=next((a for kind in ('DiscreteGPU','IntegratedGPU') for a in adapters
                          if a.info['adapter_type']==kind and a.info['backend_type']=='D3D12'),None)
            require(adapter is not None,'GPU_ADAPTER_UNAVAILABLE')
            preconfigure_default_device('line10 coordinated graphics only',adapter=adapter)
            self.adapter=dict(adapter.info)
        else:self.adapter=configure_renderer('cpu')
        self.scene=AnatomyScene(args.model,offscreen=True,size=(args.width,args.height),profile='light',max_fps=60)
        s=self.scene
        self.camera_state=self.camera_signature()
        limit=float(np.max(np.abs(s.activity)))
        require(limit>0 and math.isfinite(limit),'CALIBRATION_DOMAIN')
        self.encoding=dict(mode='fixed_type_hue_abs_gamma_v1',palette=fixed_type_palette(s.objects),
            intensity_domain=[0.,limit],brightness_floor=.25,gamma=.45,brightness_max=1.,
            formula='b=0.25+0.75*clip(abs(mean)/M,0,1)^0.45; rendered_sRGB=b*identity_sRGB',
            calibration_run_id=self.identity['run_id'],calibration_activity_sha256=self.identity['activity_sha256'],
            calibration_replay_sha256=self.identity['replay_sha256'],units='original_model_units',
            normalization='fixed shared domain for the entire bound session; no per-frame/per-type rescaling',
            sign_semantics='Sign retained in raw signed values and main GUI zero-baseline plots; brightness means absolute magnitude',
            perceptual_note='Gamma contrast enhancement is for display, not a changed neuron equation or calibrated luminance')
        self.encoding['encoding_sha256']=digest(self.encoding)
        self.fixed=FixedCPU(s,self.run/'fixed_projection') if args.renderer=='cpu' else None
        self.code={str(p.relative_to(ROOT)):sha(p) for p in (Path(__file__),HERE/'research_guard.py',HERE/'fixed_cpu.py',ROOT/'scene.py',ROOT/'presentation.py')}
        # Warm only the renderer; this saved-state image is never published as live.
        np.asarray(s.v.canvas.draw())
        self.last_guard=0.
        self.log(event='ready',adapter=self.adapter,source_code_sha256=self.code,graphics_warmup_published=False)

    def log(self,**value):
        with (self.run/'events.jsonl').open('a',encoding='utf-8') as f:
            f.write(json.dumps(dict(utc=datetime.now(timezone.utc).isoformat(),service_id=self.service_id,**value),ensure_ascii=False,allow_nan=False)+'\n')

    def camera_signature(self):
        return json.dumps(self.scene.v.camera.get_state(),sort_keys=True,default=lambda v:v.tolist())

    def check_resources(self,force=False):
        if self.parent is not None:
            try:alive=self.parent.is_running() and self.parent.create_time()==self.parent_created
            except psutil.Error:alive=False
            if not alive:
                self.stopping=True
                raise YieldResources('OWNER_PARENT_CLOSED')
        if self.args.renderer!='gpu':return
        if not force and time.monotonic()-self.last_guard<1:return
        self.last_guard=time.monotonic()
        try:
            require(self.parent is not None and self.args.gpu_lease_file is not None,'GPU_COORDINATOR_REQUIRED')
            lease=json.loads(self.args.gpu_lease_file.read_text(encoding='utf-8'))
            require(lease.get('schema')=='line10.gpu_coordinator.v1','GPU_LEASE_SCHEMA')
            require(type(lease.get('parent_pid')) is int and lease['parent_pid']==self.args.parent_pid
                    and number(lease.get('parent_create_time'))
                    and abs(lease['parent_create_time']-self.parent_created)<=1e-5,'GPU_LEASE_OWNER')
            require(identifier(lease.get('session_id')),'GPU_LEASE_SESSION')
            require(number(lease.get('expires_unix')) and time.time()<lease['expires_unix']<=time.time()+3600,'GPU_LEASE_EXPIRED')
            if self.binding:require(lease['session_id']==self.binding['session_id'],'GPU_LEASE_BOUND_SESSION')
            allowed=lease.get('allowed_processes')
            require(isinstance(allowed,list) and len(allowed)<=64,'GPU_LEASE_PROCESS_LIST')
            allowed_instances=[]
            for item in allowed:
                require(isinstance(item,dict) and type(item.get('pid')) is int and item['pid']>0
                        and number(item.get('create_time')),'GPU_LEASE_PROCESS_IDENTITY')
                try:
                    process=psutil.Process(item['pid'])
                    require(abs(process.create_time()-item['create_time'])<=1e-5,'GPU_LEASE_PID_REUSED')
                    allowed_instances.append(dict(pid=item['pid'],create_time=process.create_time()))
                except psutil.NoSuchProcess:pass  # Finished members cannot exempt a new reused PID.
            state=research_guard()
            self.guard_state=state
            signature=digest(dict(policy=POLICY,session_id=lease['session_id'],busy=state['busy'],markers=state['markers'],readonly_diagnostics=state['readonly_diagnostics']))
            if signature!=self.guard_audit_signature:
                self.log(event='resource_guard',session_id=lease['session_id'],policy=POLICY,
                         busy=state['busy'],markers=state['markers'],readonly_diagnostics=state['readonly_diagnostics'])
                self.guard_audit_signature=signature
            remaining=[p for p in state['busy'] if not any(same_instance(p,item) for item in allowed_instances)]
            require(not remaining and not state['markers'],'EXTERNAL_RESEARCH_BUSY: '+json.dumps(dict(busy=remaining,markers=state['markers'])))
            self.lease=lease
        except (OSError,ValueError,KeyError,TypeError,psutil.Error) as exc:
            self.stopping=True
            raise YieldResources(str(exc)) from exc

    def health(self):
        return dict(schema='line10.live_raw.health.v1',status='BOUND' if self.binding else 'READY_TO_BIND',
                    service_id=self.service_id,pid=os.getpid(),pid_create_time=psutil.Process().create_time(),
                    parent_pid=self.args.parent_pid,parent_create_time=self.parent_created,
                    adapter=self.adapter,expected_binding=self.expected,
                    viewport=dict(width=self.args.width,height=self.args.height,pixel_ratio=1),
                    wire_format=WIRE,color_encoding=self.encoding,background_style='simplified_mesh',
                    background_manifest_sha256=self.scene.background_manifest_sha256,
                    camera_framing=self.scene.projection_info(),source_code_sha256=self.code,
                    bind_id=self.bind_id,binding=self.binding,last_step=self.last_step,draw_count=self.draw_count,cache_hits=self.cache_hits,
                    geometry_rebuilt_per_frame=False,autonomous_playback=False,renderer_computes_neurons=False,
                    PL_execution=False,lease_session=self.lease['session_id'] if self.lease else None,
                    resource_guard_policy=POLICY,resource_guard_snapshot=self.guard_state,
                    fixed_cpu_projection=self.fixed.identity if self.fixed else None,
                    fixed_cpu_projection_sha256=self.fixed.digest if self.fixed else None)

    def bind(self,body):
        self.check_resources(force=True)
        require(isinstance(body,dict),'BIND_OBJECT')
        extra={'session_id','run_id','dt_s','input_time_origin_s','upstream_map_sha256','source_evidence_level'}
        require(set(body)==set(self.expected)|extra,'BIND_FIELDS')
        for k,v in self.expected.items():require(body[k]==v,'BIND_IDENTITY_'+k)
        require(identifier(body['session_id']) and identifier(body['run_id']),'BIND_RUN_SESSION')
        require(number(body['dt_s']) and abs(body['dt_s']-.005)<1e-12,'BIND_MODEL_DT')
        require(number(body['input_time_origin_s']),'BIND_TIME_ORIGIN')
        require(valid_sha(body['upstream_map_sha256']),'BIND_UPSTREAM_MAP')
        require(body['source_evidence_level'] in SOURCE_LEVELS,'BIND_SOURCE_EVIDENCE')
        if self.lease:require(body['session_id']==self.lease['session_id'],'BIND_LEASE_SESSION')
        contract=dict(body)
        candidate=digest(dict(binding=contract,color_encoding_sha256=self.encoding['encoding_sha256'],
                              background_manifest_sha256=self.scene.background_manifest_sha256,
                              viewport=[self.args.width,self.args.height],source_code_sha256=self.code))
        if self.binding is not None:
            require(candidate==self.bind_id,'ALREADY_BOUND_TO_ANOTHER_SESSION')
        else:
            self.binding=contract
            self.bind_id=candidate
            self.log(event='bind',bind_id=candidate,binding=contract,color_encoding=self.encoding)
        return dict(status='BOUND',service_id=self.service_id,bind_id=self.bind_id,binding=self.binding,
                    color_encoding=self.encoding,wire_format=WIRE)

    def validate_frame(self,body):
        require(self.binding is not None,'NOT_BOUND')
        fields={'session_id','run_id','model_id','checkpoint_sha256','mapping_sha256','upstream_map_sha256',
                'bind_id','request_id','step_id','state_token','activity_time_s','means','source_sequence','spatial_values_sha256'}
        require(isinstance(body,dict) and set(body)==fields,'FRAME_FIELDS')
        for key in ('session_id','run_id','model_id','checkpoint_sha256','mapping_sha256','upstream_map_sha256'):
            require(body[key]==self.binding[key],'FRAME_IDENTITY_'+key)
        require(body['bind_id']==self.bind_id,'FRAME_BIND_ID')
        require(identifier(body['request_id']),'FRAME_REQUEST_ID')
        k=body['step_id']
        require(type(k) is int and 0<=k<=100000000,'FRAME_STEP')
        require(type(body['state_token']) is int and body['state_token']==k+1,'FRAME_STATE_TOKEN')
        expected=self.binding['input_time_origin_s']+k*self.binding['dt_s']+self.binding['dt_s']
        require(number(body['activity_time_s']) and abs(body['activity_time_s']-expected)<=1e-9,'FRAME_EULER_TIME')
        require(type(body['source_sequence']) is int and body['source_sequence']>=0,'FRAME_SOURCE_SEQUENCE')
        if self.last_receipt:require(body['source_sequence']>=self.last_receipt['source_sequence'],'SOURCE_SEQUENCE_REVERSED')
        require(valid_sha(body['spatial_values_sha256']),'FRAME_SPATIAL_VALUES_SHA')
        values=body['means']
        require(isinstance(values,list) and len(values)==len(self.expected['types'])
                and all(number(v) for v in values),'FRAME_MEANS_FINITE')
        with np.errstate(over='ignore'):
            require(np.isfinite(np.asarray(values,dtype=np.float64)/self.encoding['intensity_domain'][1]).all(),
                    'FRAME_MEANS_NORMALIZATION_OVERFLOW')
        signature=digest({k:v for k,v in body.items() if k!='request_id'})
        require(k>=self.last_step,'OUT_OF_ORDER')
        if k==self.last_step:require(signature==self.last_signature,'COMMITTED_STATE_REWRITE')
        return np.asarray(values,dtype=np.float64),signature

    def render_raw(self,body):
        begin=time.perf_counter()
        values,signature=self.validate_frame(body)  # No mutation on rejected identity/order/time.
        self.check_resources()
        s=self.scene
        require(s.type_filter=='all' and s.profile=='light' and self.camera_signature()==self.camera_state,'FIXED_VIEW_CHANGED')
        duplicate=body['step_id']==self.last_step
        if duplicate:
            receipt=dict(self.last_receipt,request_id=body['request_id'],cache_hit=True,draw_performed=False,
                         draw_and_readback_ms=0.,color_update_ms=0.,raw_copy_ms=0.,total_render_raw_ms=1000*(time.perf_counter()-begin))
            self.cache_hits+=1
            return receipt,self.last_pixels
        update_start=time.perf_counter()
        magnitude=np.abs(values)
        normalized=magnitude/self.encoding['intensity_domain'][1]
        brightness=.25+.75*np.clip(normalized,0,1)**.45
        bases=np.array([[int(self.encoding['palette'][o['type']][i:i+2],16)/255 for i in (1,3,5)] for o in s.objects])
        colors=bases*brightness[:,None]
        if not self.fixed:
            s.v.set_colors({o['name']:tuple(color) for o,color in zip(s.objects,colors)})
            s.v.canvas.request_draw()
        update_ms=1000*(time.perf_counter()-update_start)
        draw_start=time.perf_counter()
        image=self.fixed.compose(colors) if self.fixed else np.asarray(s.v.canvas.draw())
        draw_ms=1000*(time.perf_counter()-draw_start)
        require(image.shape==(self.args.height,self.args.width,4) and image.dtype==np.uint8,'RAW_RGBA_SHAPE')
        copy_start=time.perf_counter()
        pixels=image.tobytes(order='C')
        raw_sha=hashlib.sha256(pixels).hexdigest()
        copy_ms=1000*(time.perf_counter()-copy_start)
        states=[dict(type=o['type'],body_id=o['body_id'],model_node_count=o['count'],activity_signed=float(value),
                     value=float(value),identity_color=self.encoding['palette'][o['type']],brightness_factor=float(b),
                     intensity_abs=float(abs(value)),normalized_intensity=float(norm),saturated=bool(norm>1),
                     polarity='positive' if value>0 else 'negative' if value<0 else 'zero',
                     color='#'+''.join(f'{round(c*255):02x}' for c in color))
                for o,value,b,norm,color in zip(s.objects,values,brightness,normalized,colors)]
        receipt=dict(schema='line10.live_raw.frame.v1',service_id=self.service_id,**body,
            input_time_s=self.binding['input_time_origin_s']+body['step_id']*self.binding['dt_s'],
            node_map_sha256=self.expected['node_map_sha256'],types=self.expected['types'],counts=self.expected['counts'],
            aggregation=self.expected['aggregation'],type_states=states,color_encoding=self.encoding,
            means_f64le_sha256=hashlib.sha256(values.astype('<f8').tobytes()).hexdigest(),
            raw_sha256=raw_sha,byte_length=len(pixels),row_stride=self.args.width*4,pixel_format='RGBA8',
            row_order='top-down',channel_order='RGBA',alpha_mode='straight',wire_format=WIRE,
            image_width=self.args.width,image_height=self.args.height,adapter=self.adapter,
            profile='light',type_filter='all',rois_visible=s.rois_visible,background_style=s.background_style,
            background_manifest_sha256=s.background_manifest_sha256,camera_framing=s.projection_info(),
            source_code_sha256=self.code,draw_performed=not bool(self.fixed),cache_hit=False,color_update_ms=update_ms,
            draw_and_readback_ms=0. if self.fixed else draw_ms,fixed_cpu_compose_ms=draw_ms if self.fixed else None,
            fixed_cpu_projection_sha256=self.fixed.digest if self.fixed else None,
            rendering_method='fixed_SWCs_CPU_projection_composite' if self.fixed else 'full_scene_WGPU_draw',
            raw_copy_ms=copy_ms,source_evidence_level=self.binding['source_evidence_level'],
            evidence_level='EXTERNAL_ACTIVITY_RENDER_ONLY',source_verification_owner='line2 upstream stream verifier',
            scientific_boundary='True morphology with type-level model means; not individual biological measurement or FPGA result',
            neural_computation_performed=False,PL_execution=False,total_render_raw_ms=1000*(time.perf_counter()-begin))
        self.last_step=body['step_id'];self.last_signature=signature;self.last_receipt=receipt;self.last_pixels=pixels
        self.draw_count+=1
        self.log(event='render_raw',step_id=self.last_step,state_token=body['state_token'],activity_time_s=body['activity_time_s'],
                 source_sequence=body['source_sequence'],request_id=body['request_id'],raw_sha256=raw_sha,
                 means_f64le_sha256=receipt['means_f64le_sha256'],draw_and_readback_ms=draw_ms,total_render_raw_ms=receipt['total_render_raw_ms'])
        return receipt,pixels

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def setup(self):
        super().setup();self.connection.settimeout(3.)
    def reply(self,status,data,raw=False):
        payload=data if raw else canonical(data)
        self.send_response(status)
        self.send_header('Content-Type','application/octet-stream' if raw else 'application/json; charset=utf-8')
        self.send_header('Content-Length',str(len(payload)))
        self.send_header('Cache-Control','no-store')
        if raw:self.send_header('X-Line10-Wire',WIRE)
        self.end_headers();self.wfile.write(payload)
    def do_GET(self):
        self.reply(200,self.server.live.health()) if self.path=='/health' else self.reply(404,dict(error='Unknown endpoint'))
    def do_POST(self):
        live=self.server.live
        if not secrets.compare_digest(self.headers.get('X-Line10-Owner',''),live.args.owner_token):
            self.reply(403,dict(error='OWNER_TOKEN_REQUIRED'));return
        try:
            length=int(self.headers.get('Content-Length','0'))
            require(0<length<=65536,'BODY_LENGTH')
            body=json.loads(self.rfile.read(length))
            require(isinstance(body,dict),'BODY_OBJECT')
            if self.path=='/projection_cache':
                require(live.fixed is not None and body.get('service_id')==live.service_id,'FIXED_CACHE_OWNER')
                self.reply(200,live.fixed.cache_wire(),raw=True)
            elif self.path=='/bind':self.reply(200,live.bind(body))
            elif self.path=='/render_raw':self.reply(200,frame_wire(*live.render_raw(body)),raw=True)
            elif self.path=='/stop':
                require(body.get('service_id')==live.service_id,'STOP_SERVICE_ID')
                live.stopping=True;self.reply(200,dict(status='STOPPING',service_id=live.service_id))
            else:self.reply(404,dict(error='Unknown endpoint'))
        except YieldResources as exc:
            live.log(event='yield_to_coordinator_or_research',error=str(exc))
            self.reply(503,dict(code='RESEARCH_BUSY',renderer_state='STOPPING',error=str(exc)))
        except (Rejected,ValueError,TypeError,KeyError) as exc:
            live.log(event='reject',error=str(exc));self.reply(409,dict(error=str(exc),code='REQUEST_REJECTED'))
        except (BrokenPipeError,ConnectionResetError,TimeoutError):pass
        except Exception as exc:
            live.stopping=True;live.log(event='fatal_render_error',error=repr(exc))
            self.reply(500,dict(error=repr(exc),renderer_state='STOPPING'))

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--model',type=Path,default=ROOT/'model.json')
    parser.add_argument('--renderer',choices=['cpu','gpu'],default='cpu')
    parser.add_argument('--port',type=int,default=0)
    parser.add_argument('--width',type=int,default=960);parser.add_argument('--height',type=int,default=480)
    parser.add_argument('--owner-token',required=True);parser.add_argument('--parent-pid',type=int)
    parser.add_argument('--gpu-lease-file',type=Path);parser.add_argument('--ready-file',type=Path,required=True)
    parser.add_argument('--tag',default='session_'+datetime.now().strftime('%Y%m%d_%H%M%S'))
    args=parser.parse_args()
    require(320<=args.width<=1280 and 240<=args.height<=640,'VIEWPORT_BOUND')
    require(len(args.owner_token)>=16 and len(args.owner_token)<=256,'OWNER_TOKEN_LENGTH')
    require(args.tag and Path(args.tag).name==args.tag and args.tag not in ('.','..'),'EVIDENCE_TAG')
    proc=psutil.Process();proc.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    if args.renderer=='cpu':proc.cpu_affinity(proc.cpu_affinity()[:4])
    def offline(event,parameters):
        if event=='socket.connect' and not (isinstance(parameters[1],tuple) and parameters[1][0] in ('127.0.0.1','localhost','::1')):
            raise RuntimeError('Local-file renderer: external connections denied')
    sys.addaudithook(offline)
    with HTTPServer(('127.0.0.1',args.port),Handler) as server:
        server.timeout=.5
        live=None
        try:
            live=server.live=LiveRaw(args)
            ready=dict(live.health(),url=f'http://127.0.0.1:{server.server_port}')
            args.ready_file.parent.mkdir(parents=True,exist_ok=True)
            temp=args.ready_file.with_suffix('.tmp');temp.write_text(json.dumps(ready,ensure_ascii=False,indent=2),encoding='utf-8');temp.replace(args.ready_file)
            print(json.dumps(dict(status='READY_TO_BIND',url=ready['url'],pid=os.getpid())),flush=True)
            while not live.stopping:
                server.handle_request()
                try:live.check_resources()
                except YieldResources as exc:
                    live.log(event='yield_or_parent_closed',error=str(exc));break
        finally:
            if live is not None:
                live.scene.v.close();live.log(event='closed',pid=os.getpid())

if __name__=='__main__':main()
