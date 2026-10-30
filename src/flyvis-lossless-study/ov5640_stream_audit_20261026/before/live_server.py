"""Isolated entry reusing original renderer. PC serves no board-control endpoint."""
import argparse,hmac,io,json,os,sys,threading,time,urllib.parse,webbrowser
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from pathlib import Path
from collections import OrderedDict
P=Path(__file__).resolve().parents[1];sys.path.insert(0,str(P/'bundle'))
import numpy as np
from PIL import Image,ImageDraw
from ps_input import receptor_centers
from live_protocol import Store,MAX_PACKET,atomic,canonical,sha
from full_audit import audit
from round_sessions import Rounds,admission
import fixed_entry

class App:
    def init__(self,config,records):
        self.config=config;self.store=Store(records,config);self.started=time.time();self.last_received=None
        self.audit_result=None;self.audit_running=False;self.audit_lock=threading.Lock()
        self.display_cache=OrderedDict();self.display_lock=threading.Lock();self.display_builds=0
        self.spatial=json.loads((P/'assets/spatial.json').read_text());self.audit_if_ready()
    def audit_if_ready(self):
        with self.audit_lock:
            if self.audit_running or self.audit_result or self.store.final is None or not self.store.meta:return
            existing=self.store.path/'audit/RESULT.json'
            if existing.exists():self.audit_result=json.loads(existing.read_text());return
            self.audit_running=True
            def work():
                try:
                    dest=self.store.path/'audit'
                    if dest.exists():dest=self.store.path/('audit_resume_'+str(time.time_ns()))
                    self.audit_result=audit(self.store,P/'bundle',dest)
                    if dest.name!='audit':atomic(existing,canonical(self.audit_result))
                except Exception as exc:
                    self.audit_result=dict(status='AUDIT_ERROR',error=repr(exc));atomic(self.store.path/'AUDIT_ERROR.json',canonical(self.audit_result))
                finally:self.audit_running=False
            threading.Thread(target=work,name='line11-offline-audit',daemon=True).start()
    def status(self):
        with self.store.lock:
            allowed,reason=admission(self)
            return dict(application='line11-live-v261',next_round_allowed=allowed,next_round_reason=reason,round_label=self.config['session_id'][:8],received=len(self.store.meta),max_steps=self.config['max_steps'],session_id=self.config['session_id'],
                        finished=self.store.final is not None,camera_close_status=self.store.camera_close['status'] if self.store.camera_close else 'NOT_CONFIRMED',producer_status=self.store.final['status'] if self.store.final else None,
                        audit_status=self.audit_result['status'] if self.audit_result else ('AUDITING' if self.audit_running else 'PENDING'),
                        mismatch_words=self.audit_result.get('mismatch_words') if self.audit_result else None,
                        last_received_unix=self.last_received,board_controls=False)
    def display(self,k):
        # A two-entry immutable cache; no Store/ingest lock held while rendering.
        with self.display_lock:
            if k in self.display_cache:
                self.display_cache.move_to_end(k);return self.display_cache[k]
            m,source,r=self.store.read(k)
            vals=np.frombuffer(r.state_bits,'<f4')[self.spatial['ids']].astype('<f4')
            packet=dict(run_id=m['run_id'],session_id=m['session_id'],serial=k+1,step_id=k,state_token=m['state_sha256'],
                        activity_time_s=(k+1)*.005,input_time_s=k*.005,source=dict(sequence=k),
                        evidence_level=m['evidence'],spatial=dict(values=vals.tolist(),map_sha256=self.spatial['map_sha256'],values_sha256=sha(vals.tobytes())),
                        timing=m['timing'],source_sha256=m['source_sha256'])
            buf=io.BytesIO()
            if source is None:
                img=Image.new('RGB',(417,417),(35,35,35));draw=ImageDraw.Draw(img)
                values=np.frombuffer(r.input_bits,'<f4')
                for (row,col),value in zip(receptor_centers(),values):
                    gray=int(np.clip(value,0,1)*255+.5);draw.ellipse((int(col)-5,int(row)-5,int(col)+5,int(row)+5),fill=(gray,gray,gray))
                packet['input_721']=values.tolist();packet['source_display']='721 actual inputs; not original camera image'
            else:
                a=np.frombuffer(source,np.uint8).reshape(480,800,3);img=Image.fromarray(a[:,:,::-1],'RGB')
            img.save(buf,format='PNG')
            entry=(canonical(packet),buf.getvalue(),m['state_sha256']);self.display_cache[k]=entry
            while len(self.display_cache)>2:self.display_cache.popitem(last=False)
            self.display_builds+=1;return entry
    def packet(self,k):return json.loads(self.display(k)[0])
    def latest(self,after=-1):
        with self.store.lock:k=len(self.store.meta)-1
        # No file read, state checksum, PNG encoding or activity serialization if unchanged.
        if k<0 or after>=k:return canonical(dict(packet=None,status=self.status()))
        encoded=self.display(k)[0]
        return b'{"packet":'+encoded+b',"status":'+canonical(self.status())+b'}'
    def frame(self,k,state):
        entry=self.display(k)
        if state!=entry[2]:raise ValueError('frame-state binding')
        return entry[1]

def make_server(app,host='127.0.0.1',port=0,rounds=None):
    initial_app=app
    fixed_root=rounds.root if rounds else P
    fixed_key=fixed_entry.prepare(fixed_root) if rounds else None
    class Handler(BaseHTTPRequestHandler):
        protocol_version='HTTP/1.0'
        def log_message(self,*a):pass
        def reply(self,status,data,kind='application/json'):
            if isinstance(data,(dict,list)):data=canonical(data)
            self.send_response(status);self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(data)))
            self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.end_headers();self.wfile.write(data)
        def auth(self,app):return hmac.compare_digest(self.headers.get('Authorization',''),'Bearer '+app.config['token'])
        def local(self):return self.client_address[0] in ('127.0.0.1','::1')
        def do_GET(self):
            app=rounds.current if rounds else initial_app
            self.connection.settimeout(5)
            try:
                u=urllib.parse.urlsplit(self.path);route=u.path
                if route=='/runner':
                    if fixed_key is None or not hmac.compare_digest(self.headers.get('Authorization',''),'Bearer '+fixed_key):return self.reply(403,{'error':'authorization'})
                    nonce=urllib.parse.parse_qs(u.query).get('nonce',[''])[0]
                    return self.reply(200,fixed_entry.response(rounds,fixed_key,nonce))
                if route=='/hello':
                    if not self.auth(app):return self.reply(403,{'error':'authorization'})
                    return self.reply(200,app.status())
                if not self.local():return self.reply(403,{'error':'display is PC-local only'})
                if route=='/fixed-notebook' and fixed_key is not None:
                    return self.reply(200,(fixed_root/fixed_entry.NAME).read_bytes(),'application/x-ipynb+json')
                if route=='/notebook':
                    file=rounds.notebook_path(app) if rounds else P/'LINE11_OFFICIAL_LIVE_V261_60S.ipynb'
                    return self.reply(200,file.read_bytes(),'application/x-ipynb+json')
                static={'/':('assets/index.html','text/html; charset=utf-8'),'/ui.js':('assets/ui.js','text/javascript'),
                        '/fixed_skeleton.js':('assets/fixed_skeleton.js','text/javascript'),'/projection':('assets/projection.json','application/json'),
                        '/api/competition-live/cache':('assets/projection.bin','application/octet-stream'),
                        '/notebook':('LINE11_OFFICIAL_LIVE_V261_60S.ipynb','application/x-ipynb+json')}
                if route in static:
                    f,mime=static[route];return self.reply(200,(P/f).read_bytes(),mime)
                if route=='/status':return self.reply(200,app.status())
                if route=='/latest':
                    q=urllib.parse.parse_qs(u.query);after=int(q.get('after',['-1'])[0])
                    return self.reply(200,app.latest(after))
                if route=='/frame.png':
                    q=urllib.parse.parse_qs(u.query);k=int(q['step'][0])
                    return self.reply(200,app.frame(k,q['state'][0]),'image/png')
                return self.reply(404,{'error':'no such endpoint; no board commands'})
            except (ValueError,KeyError,IndexError,FileNotFoundError) as exc:self.reply(400,{'error':str(exc)})
            except (BrokenPipeError,ConnectionResetError,TimeoutError):pass
        def do_POST(self):
            app=rounds.current if rounds else initial_app
            self.connection.settimeout(5)
            try:
                route=urllib.parse.urlsplit(self.path).path
                if route=='/next-round':
                    if not self.local() or self.headers.get('X-Line11-UI')!='1' or self.headers.get('Content-Type')!='application/json':return self.reply(403,{'error':'PC-local UI only'})
                    origin=self.headers.get('Origin')
                    if origin and origin!='http://'+self.headers.get('Host',''):return self.reply(403,{'error':'origin'})
                    if rounds is None:return self.reply(409,{'error':'请重新启动电脑接收窗口'})
                    n=int(self.headers.get('Content-Length','0'))
                    if not 0<n<=1024:return self.reply(413,{'error':'body bound'})
                    data=self.rfile.read(n)
                    if len(data)!=n:raise ValueError('truncated request')
                    return self.reply(200,rounds.advance(json.loads(data)['session_id']))
                if route not in ('/ingest','/finish','/camera-close'):return self.reply(404,{'error':'no board commands'})
                if not self.auth(app):return self.reply(403,{'error':'authorization'})
                n=int(self.headers.get('Content-Length','0'));limit=MAX_PACKET if route=='/ingest' else 16*1024*1024
                if not 0<n<=limit:return self.reply(413,{'error':'body bound'})
                start=time.monotonic();data=self.rfile.read(n)
                if len(data)!=n:raise ValueError('truncated request')
                if route=='/ingest':
                    result=app.store.accept(data)
                    if not result['duplicate']:app.last_received=time.time()
                    if not result['duplicate']:atomic(app.store.path/('%06d_receive.json'%result['step_id']),canonical(dict(result,receive_to_commit_ms=(time.monotonic()-start)*1000)))
                elif route=='/camera-close':result=app.store.record_camera_close(json.loads(data))
                else:result=app.store.finish(json.loads(data));app.audit_if_ready()
                self.reply(200,result)
            except (ValueError,KeyError,TypeError) as exc:self.reply(409,{'error':str(exc)})
            except (BrokenPipeError,ConnectionResetError,TimeoutError):pass
            except OSError as exc:self.reply(503,{'error':'storage/network failure; resend same record only'})
    server=ThreadingHTTPServer((host,port),Handler);server.daemon_threads=True;return server

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--no-browser',action='store_true');args=parser.parse_args()
    from offline_check import verify
    verify(P/'bundle')
    rounds=Rounds(P,App);app=rounds.current;c=app.config
    server=make_server(app,'0.0.0.0',c['port'],rounds=rounds)
    print('LINE11 official camera display: http://127.0.0.1:%s'%c['port'],flush=True)
    print('Notebook receiver address: '+c['pc_url'],flush=True)
    print('Records: '+str(app.store.path)+' | no board/GPU operations by this PC program',flush=True)
    if not args.no_browser:webbrowser.open('http://127.0.0.1:%s'%c['port'])
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
if __name__=='__main__':main()
