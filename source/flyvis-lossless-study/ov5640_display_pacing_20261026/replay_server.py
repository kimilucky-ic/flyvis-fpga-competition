from pathlib import Path
import json,sys,time,threading,urllib.parse
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
E=Path(__file__).resolve().parent;P=E.parent/'ov5640_live_v261_20261026';sys.path[:0]=[str(P/'pc'),str(P/'bundle')]
from live_server import App
from live_protocol import canonical
R=P/'pc/rounds/604780dd181959f4ad8bb08c94a1f241';app=App(json.loads((R/'session.json').read_text()),R/'records')
servers=[]
def make(mode):
 state={'mode':mode,'start':None,'latest_requests':0,'images':0}
 class Handler(BaseHTTPRequestHandler):
  def log_message(self,*a):pass
  def reply(self,data,mime='application/json'):
   if not isinstance(data,bytes):data=canonical(data)
   self.send_response(200);self.send_header('Content-Type',mime);self.send_header('Content-Length',str(len(data)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(data)
  def do_GET(self):
   u=urllib.parse.urlsplit(self.path);q=urllib.parse.parse_qs(u.query)
   if u.path in ['/latest','/status']:
    if state['start'] is None:state['start']=time.monotonic()
    elapsed=time.monotonic()-state['start'];k=min(218,int(elapsed/.055));status=app.status();status.update(received=k+1,finished=elapsed>=12,next_round_allowed=False,producer_status='OFFLINE_SAVED_RECORD_REPLAY',last_received_unix=time.time(),audit_status='CPU_REPLAY_ONLY',audited_steps=0)
    if u.path=='/status':return self.reply(status)
    state['latest_requests']+=1;after=int(q.get('after',['-1'])[0]);return self.reply(dict(packet=app.packet(k) if k>after else None,status=status))
   if u.path=='/frame.png':
    state['images']+=1;return self.reply(app.frame(int(q['step'][0]),q['state'][0]),'image/png')
   if u.path=='/metrics':return self.reply({**state,'elapsed':time.monotonic()-state['start'] if state['start'] else None})
   paths={'/':'assets/index.html','/ui.js':'assets/ui.js','/fixed_skeleton.js':'assets/fixed_skeleton.js','/projection':'assets/projection.json','/api/competition-live/cache':'assets/projection.bin'}
   if u.path not in paths:self.send_error(404);return
   f=P/paths[u.path]
   if u.path=='/ui.js' and mode=='old':f=E/'before/ui.js'
   raw=f.read_bytes();mime='text/javascript' if u.path.endswith('.js') else 'text/html; charset=utf-8' if u.path=='/' else 'application/octet-stream'
   if u.path=='/':raw=raw.decode().replace('果蝇视觉神经系统','离线保存帧测试 '+mode).replace('完整网络在PL递推','仅回放保存记录，未操作板卡').encode()
   self.reply(raw,mime)
 server=ThreadingHTTPServer(('127.0.0.1',0),Handler);server.daemon_threads=True;threading.Thread(target=server.serve_forever,daemon=True).start();servers.append(server)
 return dict(mode=mode,url='http://127.0.0.1:'+str(server.server_address[1]))
ports=[make('old'),make('new')];(E/'REPLAY_PORTS.json').write_text(json.dumps(ports));print(json.dumps(ports),flush=True)
try:
 while True:time.sleep(1)
except KeyboardInterrupt:pass
finally:
 for s in servers:s.shutdown();s.server_close()
