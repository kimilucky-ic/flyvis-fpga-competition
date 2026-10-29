"""Private transport wrapper; imports ⑩'s mature renderer without editing its files."""
import argparse
import base64
import hashlib
from http.server import BaseHTTPRequestHandler, HTTPServer
import io
import json
import math
from pathlib import Path
import sys
import time


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--ready',type=Path,required=True)
    parser.add_argument('--token',required=True)
    parser.add_argument('--parent',type=int,required=True)
    args=parser.parse_args()
    studio=Path(__file__).resolve().parents[1]/'flyvis-3d-studio/activity_replay_20261014'
    sys.path.insert(0,str(studio))
    from scene import configure_renderer, AnatomyScene
    import numpy as np
    import psutil
    from PIL import Image
    run='2041849d-b1f8-46ad-a059-49b598c19ab2'
    activity_sha='6c0c41fb9162de306ab5c9bc1cdf0a16da0f354921ed7ecab4462161b3908234'
    def require(ok,why):
        if not ok:raise ValueError(why)
    def sha(p):
        with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
    try:
        model=json.loads((studio/'model.json').read_text(encoding='utf-8'))
        for source in model['sources']:
            require(sha(source['path'])==source['sha256'],'⑩ original source identity changed')
        source={Path(x['path']).name:x for x in model['sources']}
        require(source['activities_full.npy']['sha256']==activity_sha,'Wrong 3D activity source')
        identity=json.loads(Path(source['run_identity.json']['path']).read_text(encoding='utf-8'))
        require(identity['run_id']==run,'Wrong 3D run')
        require(sha(studio/model['activity_file'])==model['replay_sha256'],'3D mean archive changed')
        for item in model['objects']:require(sha(item['swc'])==item['swc_sha256'],'Real skeleton identity changed')
        for item in model['rois']:require(sha(item['path'])==item['sha256'],'Anatomical ROI identity changed')
        adapter=configure_renderer('gpu')
        s=AnatomyScene(offscreen=True,size=(880,520),max_fps=30)
        require(s.activity.shape==(485,8) and len(s.time)==485,'3D shape mismatch')
        limit=float(np.max(np.abs(s.activity))) or 1
        types=[o['type'] for o in s.objects]
        parent=psutil.Process(args.parent)
        born=parent.create_time()
        stopping=False
        class Handler(BaseHTTPRequestHandler):
            def send(self,value,status=200):
                data=json.dumps(value,allow_nan=False).encode('utf-8')
                self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
            def do_POST(self):
                nonlocal stopping
                try:
                    require(self.headers.get('X-Owner-Token')==args.token,'Owner token required')
                    size=int(self.headers.get('Content-Length','0'));require(0<size<=4096,'Bounded JSON required')
                    body=json.loads(self.rfile.read(size))
                    if self.path=='/stop':stopping=True;return self.send({'status':'STOPPING'})
                    require(self.path=='/render','Unknown route')
                    started=time.perf_counter();k=body['frame_index'];flt=body['type_filter']
                    require(type(k) is int and 0<=k<485,'Frame bounds')
                    require(body['run_id']==run and body['activity_sha256']==activity_sha and body['activity_time_s']==float(s.time[k]),'Run/time mismatch')
                    require(flt in ['all','T4','T5']+types,'Filter bounds')
                    view=body.get('view',{});yaw=float(view.get('yaw',0));pitch=float(view.get('pitch',0));zoom=float(view.get('zoom',1))
                    require(all(math.isfinite(v) for v in (yaw,pitch,zoom)) and abs(yaw)<=100000 and abs(pitch)<=70 and .5<=zoom<=2,'View bounds')
                    s.set_frame(k)
                    names=[o['name'] for o in s.objects]
                    s.v.unhide_objects(names)
                    hidden=[o['name'] for o in s.objects if flt!='all' and not o['type'].startswith(flt)]
                    if hidden:s.v.hide_objects(hidden)
                    # GUI legend and shared signed scale: numeric activity, not type identity.
                    vals=s.activity[k]/limit
                    colors={}
                    for o,q in zip(s.objects,vals):
                        zero=np.array([.86,.89,.88]);end=np.array([.84,.27,.18]) if q>=0 else np.array([.16,.39,.74])
                        colors[o['name']]=tuple(zero*(1-abs(q))+end*abs(q))
                    s.v.set_colors(colors)
                    a=math.radians(yaw);p=math.radians(pitch)
                    direction=np.array([math.cos(a)*math.cos(p),-.4+math.sin(p),.5+math.sin(a)*math.cos(p)])
                    center=s.bounds.mean(axis=1);radius=float(np.linalg.norm(s.bounds[:,1]-s.bounds[:,0])/2)
                    s.v.camera.show_object((*center,radius),view_dir=direction,up=(0,-1,0),scale=1.22/zoom)
                    im=Image.fromarray(s.v.screenshot(None,alpha=False)).convert('RGB')
                    out=io.BytesIO();im.save(out,format='PNG',compress_level=1)
                    data=out.getvalue()
                    receipt={key:body[key] for key in ('run_id','activity_sha256','frame_index','activity_time_s','request_id','type_filter')}
                    receipt.update(mapping='type_mean_not_individual_correspondence',means=s.activity[k].tolist(),
                                   skeleton_body_ids=[o['body_id'] for o in s.objects if o['name'] not in hidden],
                                   color_scale={'kind':'shared_signed_fixed','min':-limit,'max':limit,'cross_type_comparable':True},
                                   adapter=adapter,renderer='⑩ NAVis/Octarine scene; GUI transport wrapper',
                                   model_sha256=sha(studio/'model.json'),png_sha256=hashlib.sha256(data).hexdigest(),
                                   render_ms=(time.perf_counter()-started)*1000,view={'yaw':yaw,'pitch':pitch,'zoom':zoom},PL_execution=False,display_kind='OFFLINE_REPLAY')
                    self.send({'receipt':receipt,'png_base64':base64.b64encode(data).decode('ascii')})
                except (ValueError,KeyError,TypeError,OSError) as e:self.send({'error':str(e)},409)
            def log_message(self,*args):pass
        server=HTTPServer(('127.0.0.1',0),Handler);server.timeout=.5
        args.ready.write_text(json.dumps(dict(status='READY',host='127.0.0.1',port=server.server_port,token=args.token,run_id=run,activity_sha256=activity_sha,adapter=adapter)),encoding='utf-8')
        while not stopping and parent.is_running() and parent.create_time()==born:server.handle_request()
        server.server_close();s.v.close()
    except Exception as error:
        args.ready.write_text(json.dumps({'status':'FAILED','error':str(error)}),encoding='utf-8')
        raise


if __name__=='__main__':main()
