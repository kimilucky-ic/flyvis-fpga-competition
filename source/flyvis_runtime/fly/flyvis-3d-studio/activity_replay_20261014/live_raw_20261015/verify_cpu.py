"""Bounded real CPU HTTP check with saved ON60 values; never new neural inference."""
from pathlib import Path
import sys,os,json,secrets,subprocess,time,urllib.request,urllib.error,struct,hashlib,socket,io,argparse
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
import numpy as np
from PIL import Image
import psutil

def load(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--tag',default='cpu_protocol_r2');args=parser.parse_args()
    out=HERE/'evidence'/args.tag;out.mkdir(parents=True,exist_ok=True)
    if (out/'acceptance.json').exists():raise RuntimeError('Completed evidence exists')
    ready_path=out/'ready.json'
    require_no_stale=not ready_path.exists()
    if not require_no_stale:raise RuntimeError('Old attempt ready file exists; preserve it and use a new evidence tag')
    token=secrets.token_hex(24)
    command=[sys.executable,'-B',str(HERE/'service.py'),'--renderer','cpu','--port','0','--width','960','--height','480',
             '--owner-token',token,'--parent-pid',str(os.getpid()),'--tag',args.tag,'--ready-file',str(ready_path)]
    def save(name,value):(out/name).write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
    with (out/'stdout.log').open('w',encoding='utf-8') as stdout,(out/'stderr.log').open('w',encoding='utf-8') as stderr:
        process=subprocess.Popen(command,stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW)
        url=None
        try:
            deadline=time.monotonic()+60
            while not ready_path.exists():
                if process.poll() is not None:raise RuntimeError('Owned CPU service exited: '+str(process.returncode))
                if time.monotonic()>deadline:raise RuntimeError('Owned CPU readiness deadline')
                time.sleep(.1)
            ready=load(ready_path);url=ready['url']
            def call(path,body=None,auth=True):
                headers={'Content-Type':'application/json'}
                if auth:headers['X-Line10-Owner']=token
                request=urllib.request.Request(url+path,data=None if body is None else json.dumps(body).encode(),headers=headers)
                start=time.perf_counter()
                try:
                    with urllib.request.urlopen(request,timeout=8) as response:
                        data=response.read();status=response.status;content_type=response.headers.get('Content-Type')
                except urllib.error.HTTPError as error:
                    data=error.read();status=error.code;content_type=error.headers.get('Content-Type')
                return status,data,1000*(time.perf_counter()-start),content_type
            # Windows venv python.exe is a redirector with its own child PID.
            renderer=psutil.Process(ready['pid'])
            assert ready['pid']==process.pid or process.pid in [p.pid for p in renderer.parents()]
            assert ready['pid_create_time']==renderer.create_time() and ready['adapter']['adapter_type']=='CPU'
            model=load(ROOT/'model.json')
            retained=np.load(ROOT/'replay.npz')
            raw_source=next(s for s in model['sources'] if Path(s['path']).name=='activities_full.npy')
            raw=np.load(raw_source['path'],mmap_mode='r')[0]
            nodes=np.concatenate([o['model_node_ids'] for o in model['objects']])
            binding=dict(ready['expected_binding'],session_id='LINE10_CPU_PROTOCOL_FIXTURE_ONLY',
                         run_id=ready['color_encoding']['calibration_run_id'],dt_s=.005,input_time_origin_s=-1.,
                         upstream_map_sha256=hashlib.sha256(nodes.astype('<i8').tobytes()).hexdigest(),
                         source_evidence_level='OFFLINE_SOFTWARE_REPLAY')
            status,data,_,_=call('/bind',binding);assert status==200,(status,data)
            bound=json.loads(data);save('bind.json',bound)
            def packet(k,rid):
                values=raw[k,nodes].astype(np.float32)
                groups=[];offset=0
                for count in binding['counts']:
                    groups.append(float(values[offset:offset+count].mean(dtype=np.float64)));offset+=count
                assert np.array_equal(groups,retained['activity'][k])
                return dict({key:binding[key] for key in ('session_id','run_id','model_id','checkpoint_sha256','mapping_sha256','upstream_map_sha256')},
                            bind_id=bound['bind_id'],request_id=rid,step_id=k,state_token=k+1,activity_time_s=float(retained['time'][k]),
                            means=groups,source_sequence=k,spatial_values_sha256=hashlib.sha256(values.tobytes()).hexdigest())
            samples=[]
            for k in (0,200,212,213,214,484):
                p=packet(k,'cpu_fixture_'+str(k));status,data,wall,ctype=call('/render_raw',p)
                assert status==200 and ctype=='application/octet-stream',(status,data[:200])
                length=struct.unpack('<I',data[:4])[0];receipt=json.loads(data[4:4+length]);rgba=data[4+length:]
                assert receipt['request_id']==p['request_id'] and receipt['step_id']==k and receipt['state_token']==k+1
                assert receipt['means']==p['means'] and receipt['source_evidence_level']=='OFFLINE_SOFTWARE_REPLAY'
                assert receipt['evidence_level']=='EXTERNAL_ACTIVITY_RENDER_ONLY' and receipt['PL_execution'] is False
                assert receipt['byte_length']==len(rgba)==960*480*4 and receipt['row_stride']==960*4
                assert hashlib.sha256(rgba).hexdigest()==receipt['raw_sha256']
                assert receipt['camera_framing']['cropped_node_count']==0
                image=Image.frombytes('RGBA',(960,480),rgba)
                # Saved evidence only; service transport never encodes PNG.
                if k in (0,213):image.save(out/f'actual_raw_{k:04d}.png')
                save(f'receipt_{k:04d}.json',receipt)
                samples.append(dict(step_id=k,request_wall_ms=wall,service_ms=receipt['total_render_raw_ms'],
                                    draw_ms=receipt['draw_and_readback_ms'],raw_bytes=len(rgba),raw_sha256=receipt['raw_sha256']))
            status,data,_,_=call('/render_raw',dict(p,request_id='duplicate_484'))
            length=struct.unpack('<I',data[:4])[0];repeat=json.loads(data[4:4+length])
            assert status==200 and repeat['cache_hit'] and not repeat['draw_performed'] and repeat['raw_sha256']==samples[-1]['raw_sha256']
            invalid=[('wrong_run',dict(p,run_id='wrong')),('wrong_time',dict(p,activity_time_s=99.)),
                     ('nonfinite',dict(p,means=[float('nan')]+p['means'][1:])),
                     ('out_of_order',packet(213,'old_step')),('rewrite_same_step',dict(p,means=[p['means'][0]+.1]+p['means'][1:]))]
            rejection=[]
            for name,bad in invalid:
                status,data,_,_=call('/render_raw',bad);assert status==409,(name,status,data)
                rejection.append(dict(case=name,status=status,response=json.loads(data)))
            status,data,_,_=call('/bind',dict(binding,run_id='other'));assert status==409
            rejection.append(dict(case='rebind_different_run',status=status,response=json.loads(data)))
            status,_,_,_=call('/render_raw',p,auth=False);assert status==403
            status,data,_,_=call('/health');health=json.loads(data);assert health['draw_count']==6 and health['last_step']==484
            status,_,_,_=call('/stop',dict(service_id=ready['service_id']));assert status==200
            process.wait(timeout=10);assert process.returncode==0
            host,port=url.rsplit(':',1);closed=False
            try:
                with socket.create_connection(('127.0.0.1',int(port)),timeout=.5):pass
            except OSError:closed=True
            assert closed
            save('acceptance.json',dict(status='CPU_HTTP_RAW_PASS',samples=samples,rejections=rejection,repeat_receipt=repeat,
                raw_frame_bytes=960*480*4,png_transport=False,base64_transport=False,renderer='CPU / D3D12, 4 logical processors',
                actual_neural_compute=False,PL_execution=False,owned_process_exit=process.returncode,owned_port_closed=closed,
                source_values='exact saved ON60 full state -> FP64 means over all IDs per type',
                service_sha256=sha(HERE/'service.py'),binding=bound,final_health=health,
                scope='Actual loopback protocol and CPU graphics only. Live GPU inference integration is owned by line 2.'))
            print(json.dumps(dict(status='CPU_HTTP_RAW_PASS',raw_bytes=960*480*4,samples=samples,port_closed=closed)),flush=True)
        except BaseException as exc:
            save('failure.json',dict(error=repr(exc),owned_pid=process.pid))
            raise
        finally:
            if process.poll() is None:
                if url:
                    try:call('/stop',dict(service_id=ready['service_id']))
                    except Exception:pass
                try:process.wait(timeout=8)
                except subprocess.TimeoutExpired:
                    process.terminate();process.wait(timeout=5)

if __name__=='__main__':main()
