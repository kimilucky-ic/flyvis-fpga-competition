"""One local browser recorder check using production functions; NO devices/inference."""
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import hashlib,json,time

HERE=Path(__file__).parent
source=(HERE.parents[2]/'viewer/competition_joint.js').read_text(encoding='utf8')
helpers=source[source.index(' async function startRecording(){'):source.index(' async function syncClock()')]
html='''<!doctype html><meta charset="utf-8"><title>仅检查录像 · 不启动计算</title>
<h1>仅检查录像；不启动摄像头、GPU或板卡</h1><button id="test">检查录像启动与保存</button>
<p id="result">尚未运行</p><p id="cpJointState"></p><button id="cpJointRecord" disabled></button>
<canvas id="stage" width="1920" height="1080" style="width:960px;height:540px"></canvas>
<script>
const $=id=>document.getElementById(id),fail=(v,m)=>{if(!v)throw Error(m)};
let recorder=null,chunks=[],recordingStream=null,recordingCompletion=null;
const canvas=$('stage'),c=canvas.getContext('2d'),ui={stage:{canvas,c,text:(t,x,y)=>{c.fillStyle='white';c.font='32px sans-serif';c.fillText(t,x,y)}}};
function blank(t){c.fillStyle='#08111b';c.fillRect(0,0,1920,1080);ui.stage.text('CPU录像检查：'+t,60,160);}
'''+helpers+'''
$('test').onclick=async()=>{try{$('test').disabled=true;const begin=performance.now(),ready=await startRecording();
 $('result').textContent='真实MediaRecorder已启动；等待保存（无神经活动）';
 await new Promise(r=>setTimeout(r,1200));blank('录像启动检查完成；这不是神经实验结果');
 const receipt=await finishRecording();const result={status:'PASS_ACTUAL_BROWSER_RECORDER_START_AND_SAVE',ready,receipt,total_ms:performance.now()-begin,neural_steps:0,camera_opened:false};
 const response=await fetch('/result',{method:'POST',body:JSON.stringify(result)});if(!response.ok)throw Error('REPORT_SAVE');
 $('result').textContent=JSON.stringify(result);
 }catch(e){$('result').textContent='FAILED: '+e.message;await fetch('/result',{method:'POST',body:JSON.stringify({status:'FAILED',error:e.message})});}};
</script>'''
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        raw=html.encode('utf8');self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
    def do_POST(self):
        n=int(self.headers.get('Content-Length',0));assert 0<n<10_000_000
        raw=self.rfile.read(n)
        if self.path=='/api/joint-camera/recording':
            assert raw[:4]==bytes.fromhex('1a45dfa3');path=HERE/'CPU_BROWSER_RECORDER_ONLY.webm';path.write_bytes(raw)
            result=dict(path=str(path),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),evidence='CPU_BLANK_CANVAS_NOT_NEURAL_RESULT')
        else:
            assert self.path=='/result';result=json.loads(raw);(HERE/'CPU_BROWSER_RECORDER_RESULT.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf8');self.server.done=True
        body=json.dumps(result).encode();self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
    def log_message(self,*args):pass
server=HTTPServer(('127.0.0.1',18792),Handler);server.timeout=1;server.done=False
print('CPU_RECORDER_CHECK http://127.0.0.1:18792',flush=True)
deadline=time.monotonic()+120
try:
    while not server.done and time.monotonic()<deadline:server.handle_request()
finally:server.server_close()
