"""Bounded browser-test fixture of the original stage and production input plugin.

No production service/controller. Only frozen input routes and existing static
assets are served on a random loopback port. All POST/other API calls refused.
"""
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import json
from pathlib import Path
import re
import time
from urllib.parse import urlparse
import os

from controlled_stimuli28 import ControlledStimuli28,PREFIX

HERE=Path(__file__).resolve().parent
OUT=HERE/'evidence/stimuli28_gpu_fpga_readonly_20261019'
VIEW=HERE.parent/'viewer'


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    stop=OUT/'STOP_DISPLAY_FIXTURE'
    if stop.exists():raise ValueError('Use a new test session; prior stop file exists')
    pack=ControlledStimuli28()
    html=(VIEW/'index.html').read_text(encoding='utf-8')
    html=re.sub(r'\s*<script\b[^>]*>.*?</script>','',html,flags=re.S)
    scripts=['competition_stage.js','competition_explanation.js','competition.js','competition_stimuli28.js','_stimuli_fixture.js']
    html=html.replace('</head>',''.join('<script src="/'+name+'" defer></script>' for name in scripts)+'</head>')
    html=html.replace('id="competitionWorkspace"','id="competitionWorkspace" hidden')
    bootstrap="""document.body.classList.remove('workspace-pending','competition-pending');
document.body.dataset.workspace='competition';
for(const id of ['homeWorkspace','mainWorkspace']){const el=document.getElementById(id);if(el)el.hidden=true;}
document.getElementById('competitionWorkspace').hidden=false;
document.title='FlyVis · 28条件只读显示验收';"""
    requests=[]
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def send(self,value,mime='application/json; charset=utf-8',status=200):
            raw=value if isinstance(value,bytes) else json.dumps(value,ensure_ascii=False,allow_nan=False).encode()
            self.send_response(status);self.send_header('Content-Type',mime);self.send_header('Content-Length',str(len(raw)))
            self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff')
            self.end_headers();self.wfile.write(raw)
        def do_GET(self):
            path=urlparse(self.path).path;requests.append(dict(method='GET',path=path))
            try:
                if path=='/':return self.send(html.encode(),'text/html; charset=utf-8')
                if path=='/_stimuli_fixture.js':return self.send(bootstrap.encode(),'text/javascript; charset=utf-8')
                if path.startswith(PREFIX):
                    value,mime=pack.route(path);return self.send(value,mime)
                if re.fullmatch(r'/[A-Za-z0-9_]+\.(js|css)',path):
                    name=path[1:]
                    if name.endswith('.js') and name not in scripts:return self.send(dict(error='UNRELATED_SCRIPT_DISABLED'),status=403)
                    return self.send((VIEW/name).read_bytes(),'text/javascript; charset=utf-8' if name.endswith('.js') else 'text/css; charset=utf-8')
                if path=='/favicon.ico':return self.send(b'','image/x-icon',204)
                return self.send(dict(status='DISABLED_IN_CPU_INPUT_FIXTURE',neural_state=None,flow=None),status=503)
            except (OSError,ValueError,KeyError) as error:return self.send(dict(status='NOT_AVAILABLE',error=str(error),neural_state=None,flow=None),status=409)
        def do_POST(self):
            requests.append(dict(method='POST_REFUSED',path=self.path));return self.send(dict(error='NO_COMPUTE_IN_CPU_INPUT_FIXTURE'),status=405)
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler);server.timeout=.2
    ready=dict(url='http://127.0.0.1:'+str(server.server_port)+'/',pid=os.getpid(),
        evidence='ISOLATED_CPU_STATIC_DISPLAY_FIXTURE',actual_inputs=True,neural_inference=False,decoder=False,GPU=False,board=False)
    (OUT/'DISPLAY_FIXTURE_READY.json').write_text(json.dumps(ready,indent=2),encoding='utf-8')
    print('CPU_DISPLAY_FIXTURE_READY '+ready['url'],flush=True)
    until=time.monotonic()+600
    try:
        while not stop.exists() and time.monotonic()<until:server.handle_request()
    finally:
        server.server_close()
        (OUT/'DISPLAY_FIXTURE_REQUESTS.json').write_text(json.dumps(requests,ensure_ascii=False,indent=2),encoding='utf-8')
        (OUT/'DISPLAY_FIXTURE_CLOSED.json').write_text(json.dumps(dict(server_closed=True,requests=len(requests),
            compute_post_requests=sum(r['method']=='POST_REFUSED' for r in requests),neural_steps=0,decoder_calls=0)),encoding='utf-8')
        print('CPU_DISPLAY_FIXTURE_CLOSED',flush=True)


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=OUT)
    OUT=parser.parse_args().output
    main()
