"""Loopback-only thin HTTP adapter to the existing offscreen Octarine renderer.

All GPU access stays on one thread. Each reply binds one PNG to one applied
saved frame. There is no autonomous playback clock or model computation here.
"""
from pathlib import Path
import argparse, base64, hashlib, io, json, os, sys, time, uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime, timezone
from scene import ROOT, AnatomyScene, configure_renderer, research_guard
from presentation import verified_identity, describe
import numpy as np
import psutil
import png

class RequestError(ValueError):
    pass

class ResourceYield(RuntimeError):
    pass

class Bridge:
    def init__(self, args):
        self.args = args
        self.identity = verified_identity(args.model)
        self.adapter = configure_renderer(args.renderer)
        self.scene = AnatomyScene(args.model, offscreen=True, size=(args.width,args.height),
                                  max_fps=10 if args.profile=='light' else 60, profile=args.profile)
        self.scene.filter_types('all')
        self.selected = 0
        self.service_id = str(uuid.uuid4())
        self.run = ROOT/'evidence'/args.tag
        self.run.mkdir(parents=True,exist_ok=True)
        self.stopping = False
        self.last_guard = time.monotonic()
        self.last_render_begin = 0.
        self.yield_reason = None
        self.scene.v.screenshot(None,alpha=False)  # Warm the actual GPU pipeline.

    def health(self):
        return dict(status='READY',service_id=self.service_id,pid=os.getpid(),
                    renderer='NAVis/Octarine/pygfx',adapter=self.adapter,identity=self.identity,
                    profile=self.scene.profile,rois_visible=self.scene.rois_visible,
                    background_style=self.scene.background_style,background_geometry=self.scene.background_geometry,
                    background_manifest_sha256=self.scene.background_manifest_sha256,
                    camera_framing=self.scene.projection_info(),
                    viewport=dict(width=self.args.width,height=self.args.height,pixel_ratio=1),
                    display_rate_limit_hz=10 if self.scene.profile=='light' else None,
                    has_playback_clock=False,owned_lifecycle=True)

    def check_resources(self):
        if self.args.renderer!='gpu' or time.monotonic()-self.last_guard < 1:
            return
        self.last_guard = time.monotonic()
        guard = research_guard()
        if guard['busy'] or guard['markers']:
            self.yield_reason = guard
            self.stopping = True
            self.log(dict(event='yield_to_research',guard=guard,action='close_renderer_and_exit_process'))
            raise ResourceYield('RESEARCH_BUSY: releasing the graphics process')

    def validate(self, p):
        for key in ('run_id','activity_sha256'):
            if p.get(key) != self.identity[key]:
                raise RequestError(key+' mismatch; refusing to bind a different experiment')
        for key in ('activity_time_sha256','mapping_sha256'):
            if key in p and p[key] != self.identity[key]:
                raise RequestError(key+' mismatch')
        frame = p.get('frame_index')
        if type(frame) is not int or not 0 <= frame < len(self.scene.time):
            raise RequestError('frame_index must be an in-range integer; no clipping')
        t = p.get('activity_time_s')
        if type(t) not in (int,float) or not np.isfinite(t) or abs(t-float(self.scene.time[frame])) > 1e-9:
            raise RequestError('activity_time_s does not match the exact saved frame')
        rid = p.get('request_id')
        if not isinstance(rid,(str,int)) or isinstance(rid,bool) or len(str(rid))>128:
            raise RequestError('request_id required, up to 128 characters')
        filt = p.get('type_filter','all')
        if filt not in self.identity['filters']:
            raise RequestError('Unknown type_filter')
        profile=p.get('profile',self.scene.profile)
        if profile not in ('light','standard'):
            raise RequestError('profile must be light or standard')
        selected = p.get('selected_type')
        names = [o['type'] for o in self.scene.objects]
        if selected is not None and selected not in names:
            raise RequestError('Unknown selected_type')
        camera = p.get('camera',{})
        if not isinstance(camera,dict) or set(camera)-{'reset','rotate','zoom'}:
            raise RequestError('camera supports reset, rotate and zoom only')
        if 'reset' in camera and camera['reset'] not in ('detail','overview'):
            raise RequestError('camera.reset: detail or overview')
        if 'rotate' in camera:
            r=camera['rotate']
            if not isinstance(r,list) or len(r)!=2 or any(type(v) not in (int,float) or not np.isfinite(v) or abs(v)>0.5 for v in r):
                raise RequestError('camera.rotate: two radians, bounded to +/-0.5 per request')
        if 'zoom' in camera and (type(camera['zoom']) not in (int,float) or not .8 <= camera['zoom'] <= 1.25):
            raise RequestError('camera.zoom: factor .8 to 1.25')
        if 'pick' in p and (not isinstance(p['pick'],list) or len(p['pick'])!=2 or any(type(v) not in (int,float) or not 0<=v<=1 for v in p['pick'])):
            raise RequestError('pick: normalized [x,y] in the returned image')
        return frame, filt, selected, camera, profile

    def render(self,p):
        frame,filt,selected,camera,profile=self.validate(p)  # Validate everything before mutation.
        self.check_resources()
        rate_wait=0.
        if profile=='light':
            rate_wait=max(0.,.1-(time.monotonic()-self.last_render_begin))
            if rate_wait: time.sleep(rate_wait)
        self.check_resources()
        self.last_render_begin=time.monotonic()
        begin=time.perf_counter()
        s=self.scene
        s.set_profile(profile)
        if filt!=s.type_filter: s.filter_types(filt)
        visible=[i for i,o in enumerate(s.objects) if filt in ('all',o['type'],o['type'][:2])]
        if selected is not None and [o['type'] for o in s.objects].index(selected) in visible:
            self.selected=[o['type'] for o in s.objects].index(selected)
        elif self.selected not in visible:
            self.selected=visible[0]
        if camera.get('reset')=='detail': s.detail_view()
        if camera.get('reset')=='overview': s.overview()
        if 'rotate' in camera:
            s.v.controller.rotate(tuple(camera['rotate']),(0,0,self.args.width,self.args.height),animate=False)
        if 'zoom' in camera:
            s.v.camera.width /= camera['zoom']
            s.v.camera.height /= camera['zoom']
        s.set_frame(frame)
        image=np.asarray(s.v.screenshot(None,alpha=False))
        picked=None
        if 'pick' in p:
            x,y=p['pick']
            info=s.v.renderer.get_pick_info((min(x*self.args.width,self.args.width-1),min(y*self.args.height,self.args.height-1)))
            name=getattr(info.get('world_object'),'_object_id',None)
            for i,o in enumerate(s.objects):
                if o['name']==name and i in visible:
                    self.selected=i
                    picked=o['type']
                    break
        buffer=io.BytesIO()
        png.Writer(image.shape[1],image.shape[0],alpha=True,greyscale=False).write(buffer,image.reshape(image.shape[0],-1))
        payload=buffer.getvalue()
        metadata=dict(schema='line10.frame.v1',request_id=p['request_id'],service_id=self.service_id,
                      run_id=self.identity['run_id'],activity_sha256=self.identity['activity_sha256'],
                      activity_time_sha256=self.identity['activity_time_sha256'],mapping_sha256=self.identity['mapping_sha256'],
                      input_time_sha256=self.identity['input_time_sha256'],
                      frame_index=s.frame,activity_time_s=float(s.time[s.frame]),
                      input_time_s=self.identity['input_time_s'][s.frame],
                      type_filter=s.type_filter,visible_types=[s.objects[i]['type'] for i in visible],
                      selected_type=s.objects[self.selected]['type'],picked_type=picked,
                      adapter=self.adapter,renderer='NAVis/Octarine/pygfx',
                      profile=s.profile,rois_visible=s.rois_visible,
                      background_style=s.background_style,background_geometry=s.background_geometry,
                      background_manifest_sha256=s.background_manifest_sha256,camera_framing=s.projection_info(),
                      viewport=dict(width=image.shape[1],height=image.shape[0],pixel_ratio=1),
                      display_rate_limit_hz=10 if profile=='light' else None,
                      rate_limit_wait_ms=rate_wait*1000,
                      image_width=image.shape[1],image_height=image.shape[0],png_sha256=hashlib.sha256(payload).hexdigest(),
                      scale=s.scale,detail=describe(s.objects,s.activity,s.time,s.frame,self.selected),
                      type_states=[dict(type=o['type'],body_id=o['body_id'],value=float(s.activity[s.frame,i]),
                                        color='#'+''.join(f'{round(c*255):02x}' for c in s.colors[i]),visible=i in visible)
                                   for i,o in enumerate(s.objects)],
                      render_and_png_ms=1000*(time.perf_counter()-begin),
                      evidence_level='OFFLINE_SOFTWARE_REPLAY',PL_execution=False)
        self.log(dict(event='render',request_id=p['request_id'],frame_index=s.frame,activity_time_s=metadata['activity_time_s'],
                      type_filter=filt,profile=s.profile,rois_visible=s.rois_visible,
                      png_sha256=metadata['png_sha256'],render_and_png_ms=metadata['render_and_png_ms'],picked_type=picked))
        return dict(metadata=metadata,png_base64=base64.b64encode(payload).decode('ascii'))

    def log(self,data):
        with (self.run/'bridge_events.jsonl').open('a',encoding='utf-8') as f:
            f.write(json.dumps(dict(time_utc=datetime.now(timezone.utc).isoformat(),**data),ensure_ascii=False)+'\n')

class Handler(BaseHTTPRequestHandler):
    def setup(self):
        super().setup()
        self.connection.settimeout(2.)  # A stalled local client must not retain the GPU indefinitely.

    def log_message(self,*args): pass
    def reply(self,status,data):
        payload=json.dumps(data,ensure_ascii=False,allow_nan=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Content-Length',str(len(payload)))
        self.send_header('Cache-Control','no-store')
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        self.reply(200,self.server.bridge.health()) if self.path=='/health' else self.reply(404,dict(error='Unknown endpoint'))

    def do_POST(self):
        bridge=self.server.bridge
        try:
            length=int(self.headers.get('Content-Length','0'))
            if not 0<length<=262144: raise RequestError('JSON body required, maximum 256 KiB')
            p=json.loads(self.rfile.read(length))
            if not isinstance(p,dict): raise RequestError('JSON object required')
            if self.path=='/render': self.reply(200,bridge.render(p))
            elif self.path=='/stop':
                if p.get('owner_token')!=bridge.args.owner_token or p.get('service_id')!=bridge.service_id:
                    self.reply(403,dict(error='Owner token and service_id required'))
                else:
                    bridge.stopping=True
                    self.reply(200,dict(status='STOPPING',service_id=bridge.service_id))
            else: self.reply(404,dict(error='Unknown endpoint'))
        except ResourceYield as e:
            self.reply(503,dict(error=str(e),code='RESEARCH_BUSY',service_id=bridge.service_id,
                                renderer_state='STOPPING',resource_state=bridge.yield_reason))
        except (RequestError,json.JSONDecodeError,ValueError) as e:
            bridge.log(dict(event='reject',reason=str(e)))
            self.reply(409,dict(error=str(e)))
        except (BrokenPipeError,ConnectionResetError):
            pass
        except Exception as e:
            bridge.log(dict(event='error',reason=str(e)))
            self.reply(500,dict(error=type(e).__name__+': '+str(e)))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--model',type=Path,default=ROOT/'model.json')
    ap.add_argument('--port',type=int,default=8877)
    ap.add_argument('--width',type=int)
    ap.add_argument('--height',type=int)
    ap.add_argument('--profile',choices=['light','standard'],default='standard')
    ap.add_argument('--renderer',choices=['gpu','cpu'],default='gpu')
    ap.add_argument('--owner-token',required=True)
    ap.add_argument('--parent-pid',type=int,help='Exit when this owning GUI process ends; never modify it')
    ap.add_argument('--tag',default='bridge_'+datetime.now().strftime('%Y%m%d_%H%M%S'))
    ap.add_argument('--ready-file',type=Path)
    args=ap.parse_args()
    if args.width is None: args.width=800 if args.profile=='light' else 960
    if args.height is None: args.height=500 if args.profile=='light' else 680
    parent = psutil.Process(args.parent_pid) if args.parent_pid else None
    parent_created = parent.create_time() if parent else None
    if not 320<=args.width<=1920 or not 240<=args.height<=1080: ap.error('Bounded viewport: 320..1920 by 240..1080')
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    def offline(event,parameters):
        if event=='socket.connect' and not (isinstance(parameters[1],tuple) and parameters[1][0] in ('127.0.0.1','::1','localhost')):
            raise RuntimeError('Renderer uses local files only; external network denied')
    sys.addaudithook(offline)
    # Bind first and fail on an occupied port; never attach to/stop an unrelated service.
    with HTTPServer(('127.0.0.1',args.port),Handler) as server:
        server.timeout=1.
        bridge=server.bridge=Bridge(args)
        ready=bridge.health()
        ready['url']=f'http://127.0.0.1:{server.server_port}'
        if args.ready_file:
            args.ready_file.parent.mkdir(parents=True,exist_ok=True)
            temp=args.ready_file.with_suffix('.tmp')
            temp.write_text(json.dumps(ready,ensure_ascii=False,indent=2),encoding='utf-8')
            temp.replace(args.ready_file)
        bridge.log(dict(event='ready',pid=os.getpid(),service_id=bridge.service_id,adapter=bridge.adapter))
        print(json.dumps(dict(status='READY',url=ready['url'],pid=os.getpid()),ensure_ascii=False),flush=True)
        try:
            while not bridge.stopping:
                server.handle_request()
                if parent is not None:
                    try:
                        parent_alive = parent.is_running() and parent.create_time()==parent_created
                    except psutil.Error:
                        parent_alive = False
                    if not parent_alive:
                        bridge.log(dict(event='owner_parent_closed',parent_pid=args.parent_pid))
                        break
                try: bridge.check_resources()
                except ResourceYield: break
        finally:
            bridge.scene.v.close()
            bridge.log(dict(event='closed',pid=os.getpid(),service_id=bridge.service_id))

if __name__=='__main__': main()
