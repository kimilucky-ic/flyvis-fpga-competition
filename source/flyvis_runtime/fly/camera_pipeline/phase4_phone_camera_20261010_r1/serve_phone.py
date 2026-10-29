"""Serve only stimulus assets and parameter logs; never serve real recordings."""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import hashlib
import json
from pathlib import Path
import secrets
import threading
import time
from urllib.parse import urlparse
import uuid
try:
    from .config import ROOT,settings_sha,validate_settings,write_new
except ImportError:
    from config import ROOT,settings_sha,validate_settings,write_new

def utc(): return datetime.now(timezone.utc).isoformat()

class StimulusServer(ThreadingHTTPServer):
    daemon_threads=True
    def init__(self,address,logs,validation_only=False):
        self.token=secrets.token_urlsafe(24);self.logs=Path(logs).resolve();self.validation_only=validation_only
        self.logs.mkdir(parents=True,exist_ok=True);self.sessions={};self.guard=threading.Lock()
        super().init__(address,Handler)

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args): pass
    def respond(self,status,value):
        body=json.dumps(value,ensure_ascii=False).encode()
        self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Content-Length',str(len(body)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(body)
    def do_GET(self):
        path=urlparse(self.path).path
        if path not in ('/','/phone.html','/player.js','/style.css'):
            return self.respond(404,{'error':'Only stimulus assets are served; recordings are never exposed'})
        name='phone.html' if path=='/' else path[1:]
        data=(ROOT/'web'/name).read_bytes()
        self.send_response(200);self.send_header('Content-Type',{'html':'text/html; charset=utf-8','js':'text/javascript; charset=utf-8','css':'text/css; charset=utf-8'}[name.split('.')[-1]])
        self.send_header('Content-Length',str(len(data)));self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff');self.end_headers();self.wfile.write(data)
    def do_POST(self):
        if self.headers.get('X-Stimulus-Token')!=self.server.token: return self.respond(403,{'error':'Use the startup URL containing its token'})
        try:
            size=int(self.headers.get('Content-Length','0'))
            if not 0<size<=65536: raise ValueError('Body size outside bounds')
            data=json.loads(self.rfile.read(size));json.dumps(data,allow_nan=False)
            if not isinstance(data,dict):raise ValueError('JSON object required')
            path=urlparse(self.path).path
            with self.server.guard:
                if path=='/api/arm':
                    settings=validate_settings(data['settings']);session_id=uuid.uuid4().hex
                    folder=self.server.logs/session_id;folder.mkdir(exist_ok=False)
                    assets={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'web').iterdir() if p.is_file()}
                    spec={'schema':'flyvis-phone-presentation-session-v1','phone_stimulus_session_id':session_id,
                          'state':'armed','presentation_id':'phone_'+session_id,'created_utc':utc(),'settings':settings,'settings_sha256':settings_sha(settings),
                          'source_kind':'interactive_browser_stimulus','physical_phone_verified':False,
                          'validation_only':self.server.validation_only,'comparison_id':None,
                          'logical_resolution':[640,640],'source_assets_sha256':assets,
                          'client_declared':data.get('client',{}),'clock_semantics':'client performance clock and server receipt clock are different; no optical alignment inferred',
                          'camera_capture':False,'neural_inference':False}
                    write_new(folder/'presentation.json',spec);self.server.sessions[session_id]=spec
                    return self.respond(200,{'session_id':session_id,'settings_sha256':spec['settings_sha256'],
                                            'presentation_path':str(folder/'presentation.json'),'validation_only':self.server.validation_only})
                if path!='/api/events': return self.respond(404,{'error':'Unknown endpoint'})
                session_id=data.get('session_id');spec=self.server.sessions.get(session_id)
                if spec is None: raise ValueError('Unknown session')
                events=data.get('events')
                if not isinstance(events,list) or not 1<=len(events)<=180: raise ValueError('Event batch outside bounds')
                # Validate the whole batch before writing any part of it.
                for event in events:
                    if not isinstance(event,dict) or event.get('kind') not in ('standby','start','frame','touch','resize','stop','complete','visibility','fullscreen'):
                        raise ValueError('Invalid event kind')
                    import math
                    stamp=event.get('client_performance_ms')
                    if isinstance(stamp,bool) or not isinstance(stamp,(int,float)) or not math.isfinite(stamp) or stamp<0:
                        raise ValueError('Invalid client performance timestamp')
                folder=self.server.logs/session_id
                with (folder/'events.jsonl').open('a',encoding='utf-8') as stream:
                    for event in events:
                        stream.write(json.dumps({'server_received_utc':utc(),'server_received_monotonic_ns':time.perf_counter_ns(),
                                                'client_event':event},ensure_ascii=False)+'\n')
                        if event['kind']=='start': spec['state']='playing'
                        if event['kind'] in ('stop','complete'): spec['state']=event['kind']
                # Replace only this server-owned mutable presentation status, not source/video input.
                temporary=folder/'presentation.tmp';temporary.write_text(json.dumps(spec,ensure_ascii=False,indent=2),encoding='utf-8')
                temporary.replace(folder/'presentation.json')
                return self.respond(200,{'state':spec['state'],'events_received':len(events)})
        except (ValueError,TypeError,KeyError,json.JSONDecodeError) as error:
            return self.respond(400,{'error':str(error)})

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--bind',default='127.0.0.1');parser.add_argument('--port',type=int,default=8766)
    parser.add_argument('--logs',type=Path,default=ROOT/'phone_sessions');parser.add_argument('--validation-only',action='store_true')
    args=parser.parse_args();server=StimulusServer((args.bind,args.port),args.logs,args.validation_only)
    print(json.dumps({'url':f'http://127.0.0.1:{server.server_port}/?token={server.token}',
                      'phone_url_template':f'http://PC_IPV4:{server.server_port}/?token={server.token}',
                      'bind':args.bind,'logs':str(server.logs),'camera_opened':False,'validation_only':args.validation_only}),flush=True)
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()
if __name__=='__main__':main()
