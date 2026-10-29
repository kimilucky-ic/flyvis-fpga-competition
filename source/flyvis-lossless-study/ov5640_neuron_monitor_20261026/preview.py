from pathlib import Path
import sys,json,urllib.parse
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
O=Path(__file__).resolve().parent;R=O.parent/'ov5640_live_v261_20261026';sys.path[:0]=[str(R/'pc'),str(R/'bundle')]
from live_server import App
from live_protocol import canonical
D=R/'pc/rounds/1f942a59a8515cd6a2e62ddd5fc7bc42';app=App(json.loads((D/'session.json').read_text()),D/'records');packets=json.loads((O/'packets.json').read_text());byid={p['step_id']:p for p in packets}
class H(BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def do_GET(self):
  u=urllib.parse.urlsplit(self.path);q=urllib.parse.parse_qs(u.query);route=u.path;kind='application/json'
  assets={'/':'index.html','/ui.js':'ui.js','/monitor.js':'monitor.js','/fixed_skeleton.js':'fixed_skeleton.js','/monitor-map':'monitor.json','/projection':'projection.json','/api/competition-live/cache':'projection.bin'}
  if route in assets:
   name=assets[route];data=(R/'assets'/name).read_bytes();kind='text/html; charset=utf-8' if name.endswith('.html') else 'application/javascript' if name.endswith('.js') else 'application/octet-stream'
  elif route in ['/latest','/status']:
   s=app.status();s.update(evidence='SAVED_RECORD_PREVIEW',next_round_allowed=False,next_round_reason='离线查看已保存记录，无板端操作')
   if route=='/status':data=canonical(s)
   else:
    after=int(q.get('after',[-1])[0]);p=next((p for p in packets if p['step_id']>after),None);data=canonical(dict(packet=p,status=s))
  elif route=='/frame.png':data=app.frame(int(q['step'][0]),q['state'][0]);kind='image/png'
  else:self.send_error(404);return
  self.send_response(200);self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(data)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(data)
print('READ_ONLY_SAVED_RECORD_PREVIEW http://127.0.0.1:54821/',flush=True)
ThreadingHTTPServer(('127.0.0.1',54821),H).serve_forever()
