"""Thin isolated localhost viewer; one managed WSL worker, no new scheduler."""
from contract import *
import sys,threading,subprocess,queue,base64,http.server,uuid
import numpy as np
import cv2

cv2.setNumThreads(1)
p=check();a={k:path(v) for k,v in p['assets'].items()};run=p['run_id']
assert not (HERE/'host').exists();(HERE/'host').mkdir()
lock=threading.RLock();acks=queue.Queue(maxsize=2);boot=time.monotonic();started=False;worker_ready_at=None
m=dict(np.load(a['mapping']));sampling=dict(np.load(a['sampler']))
latest=dict(run_id=run,phase='PRELOADING',stage='加载GPU模型',steps=0,frame_id=-1,render_id=0,
            uv=m['grid_uv'].tolist(),FPGA=False,target_steps_per_s=100,source_kind='实际MP4解码；已知受控视频')
events=(HERE/'host/events.jsonl').open('x',encoding='utf-8',buffering=1)
def event(kind,**values):
    with lock:events.write(json.dumps(dict(kind=kind,host_monotonic=time.monotonic(),**values),ensure_ascii=False)+'\n')
def snapshot():
    with lock:return dict(latest)
def setstate(**values):
    with lock:latest.update(values)
command=['wsl.exe','-d','FlyVisCPU','--',p['runtime']['python'],'-B',
         '/mnt/c/Users/hzy72/Documents/ChatGPT/fpga/flyvis-circuit-selection/'+HERE.name+'/worker.py']
stderr=(HERE/'host/worker_stderr.log').open('x',encoding='utf-8')
worker=subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=stderr,text=True,encoding='utf-8',bufsize=1)
write(HERE/'host/PROCESS.json',dict(host_pid=os.getpid(),worker_pid=worker.pid,command=command,run_id=run))

def read_worker():
    global worker_ready_at
    raw=(HERE/'host/worker_stdout.log').open('x',encoding='utf-8')
    try:
        for line in worker.stdout:
            raw.write(line);raw.flush()
            if not line.startswith('FV4 '):continue
            msg=json.loads(line[4:]);kind=msg.pop('event')
            if kind=='STAGE':setstate(stage=msg['text'])
            elif kind=='READY':
                worker_ready_at=time.monotonic();setstate(phase='READY',stage='GPU就绪，等待开始',device=msg['device'],preload_s=msg['preload_s'])
                event('GPU_READY',**msg)
            elif kind=='COMMIT':acks.put(msg)
            elif kind=='COMPLETE':event('GPU_COMPLETE',**msg);setstate(phase='FINISHING',stage='GPU计算完成，释放资源')
            elif kind=='ERROR':event('GPU_ERROR',**msg);setstate(phase='FAILED',stage=msg['error'])
    except BaseException as exc:event('READER_FAILURE',error=repr(exc));setstate(phase='FAILED',stage=repr(exc))
    finally:
        raw.close();code=worker.wait();stderr.close()
        event('WORKER_EXIT',exit_code=code)
        if code==0:setstate(phase='COMPLETED',stage='本次联动已完成；当前为结果回看，GPU已退出')
        else:setstate(phase='FAILED',stage='GPU进程失败，日志已保留')
        write(HERE/'host/EXIT.json',dict(exit_code=code,worker_exited=True,run_id=run))
threading.Thread(target=read_worker,daemon=True).start()

def produce():
    cap=cv2.VideoCapture(str(a['video']));tick=time.monotonic();count=0
    assert cap.isOpened() and abs(cap.get(cv2.CAP_PROP_FPS)-100)<1e-6
    host_inputs=np.empty((1000,721),np.float32)
    try:
        worker.stdin.write(json.dumps(dict(op='START',run_id=run))+'\n');worker.stdin.flush()
        setstate(phase='RUNNING',stage='实际视频输入与GPU计算同步运行');event('VISUAL_STREAM_START')
        for j in range(500):
            if time.monotonic()-tick>90:raise TimeoutError('SOURCE_LOOP_90S_BUDGET')
            delay=tick+j*.02-time.monotonic()
            if delay>0:time.sleep(delay)
            okay,frame=cap.read();assert okay and frame.shape==(224,224,3)
            gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY);xs,ys=sampling['x_pixel'],sampling['y_pixel']
            patch=np.stack([gray[ys+dy,xs+dx] for dy in [-1,0,1] for dx in [-1,0,1]])
            values=patch.mean(0,dtype=np.float64).astype(np.float32)/np.float32(255)
            host_inputs[2*j:2*j+2]=values
            digest=hashlib.sha256(values.tobytes()).hexdigest();sent=time.monotonic()
            worker.stdin.write(json.dumps(dict(op='FRAME',run_id=run,frame_id=j,input_sha=digest,
                pixels_b64=base64.b64encode(values.tobytes()).decode()))+'\n');worker.stdin.flush()
            msg=acks.get(timeout=15);assert msg['frame_id']==j and msg['steps']==2*j+2
            event('FRAME_COMMITTED',frame_id=j,steps=msg['steps'],input_sha=digest,roundtrip_ms=(time.monotonic()-sent)*1000)
            count+=1
            if 'flow_Full' in msg:
                okay,jpeg=cv2.imencode('.jpg',frame,[cv2.IMWRITE_JPEG_QUALITY,90]);assert okay
                rid=(j+1)//5;image=base64.b64encode(jpeg).decode()
                # Persist exactly the data published during running, not future states.
                write(HERE/'host'/f'visual_{rid:03d}.json',dict(**msg,render_id=rid,input_image_b64=image))
                with lock:
                    latest.update(msg,render_id=rid,input_image_b64=image,published_monotonic=time.monotonic(),
                                  elapsed_s=time.monotonic()-tick,achieved_steps_s=msg['steps']/(time.monotonic()-tick))
                event('VISUAL_PUBLISHED',render_id=rid,steps=msg['steps'],phase=snapshot()['phase'])
        np.save(HERE/'host/actual_decoded_inputs.npy',host_inputs)
        write(HERE/'host/SOURCE_RESULT.json',dict(status='ACTUAL_INCREMENTAL_MP4_STREAM_COMPLETE',source_frames=count,
            input_steps=1000,wall_s=time.monotonic()-tick,dt=.005,source_FPS=100,target_model_steps_s=100,
            no_dropped_or_padded_frames=True,precomputed_neural_states_used=False))
        event('SOURCE_COMPLETE',frames=count)
    except BaseException as exc:
        write(HERE/'STOP.json',dict(error=repr(exc)));setstate(phase='FAILED',stage=repr(exc));event('SOURCE_FAILURE',error=repr(exc))
    finally:
        cap.release()
        try:worker.stdin.close()
        except OSError:pass

class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def answer(self,body,kind='application/json'):
        data=body if isinstance(body,bytes) else json.dumps(body,ensure_ascii=False).encode()
        self.send_response(200);self.send_header('Content-Type',kind+'; charset=utf-8');self.send_header('Cache-Control','no-store')
        self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
    def do_GET(self):
        if self.path=='/':self.answer((HERE/'index.html').read_bytes(),'text/html')
        elif self.path=='/api/state':self.answer(snapshot())
        else:self.send_error(404)
    def do_POST(self):
        global started
        body=json.loads(self.rfile.read(int(self.headers.get('Content-Length','0'))))
        if body.get('run_id')!=run:self.send_error(403);return
        if self.path=='/api/start':
            with lock:
                if started or latest['phase']!='READY':self.send_error(409);return
                started=True
            event('BROWSER_START');threading.Thread(target=produce,daemon=True).start();self.answer(dict(started=True))
        elif self.path=='/api/render_ack':
            now=snapshot();rid=body.get('render_id');step=body.get('steps')
            if not isinstance(rid,int) or not 1<=rid<=now['render_id']:self.send_error(400);return
            event('BROWSER_RENDER_ACK',render_id=rid,steps=step,visible=body.get('visible'),
                  phase_when_received=now['phase'],draw_mode='two_animation_frames_after_canvas_draw')
            self.answer(dict(ok=True))
        else:self.send_error(404)

server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler)
url=f'http://127.0.0.1:{server.server_address[1]}/'
write(HERE/'SERVER_READY.json',dict(url=url,run_id=run,pid=os.getpid(),source='LIVE_NEW_GPU_COMPUTATION',FPGA=False))
print('VISUAL_VIEWER_READY '+url,flush=True)
def deadline():
    while time.monotonic()-boot<600:
        if worker_ready_at and not started and time.monotonic()-worker_ready_at>120:
            write(HERE/'STOP.json',dict(reason='NO_VIEWER_START_WITHIN_120S'))
        time.sleep(1)
    server.shutdown()
threading.Thread(target=deadline,daemon=True).start()
server.serve_forever()
