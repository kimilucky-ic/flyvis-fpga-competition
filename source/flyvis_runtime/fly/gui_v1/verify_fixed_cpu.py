"""Actual CPU graphics protocol/profile using saved real ON60 activity; no inference."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
from urllib.request import Request,build_opener,ProxyHandler
import uuid
import argparse
import numpy as np
from PIL import Image
from competition_live import raw_frame,verify_source_receipt,SERVICE_REL
from live_protocol import HERE,load,require,write


def main(evidence=None):
    root=HERE.parent;studio=root/'flyvis-3d-studio';base=studio/'activity_replay_20261014'
    evidence=Path(evidence) if evidence else HERE/'evidence/fixed_cpu_20261015';evidence.mkdir(parents=True,exist_ok=True)
    ready=evidence/'cpu_ready.json';require(not ready.exists(),'NEW_TEST_DIRECTORY_REQUIRED')
    token=uuid.uuid4().hex;log=(evidence/'cpu_renderer.log').open('ab')
    import os
    args=[str(studio/'anatomy_trial_20261013/.venv/Scripts/python.exe'),'-B',str(base/SERVICE_REL),
          '--renderer','cpu','--width','960','--height','480','--owner-token',token,
          '--parent-pid',str(os.getpid()),'--ready-file',str(ready),'--tag','CPU_SAVED_ACTIVITY_'+uuid.uuid4().hex]
    process=subprocess.Popen(args,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW,
                             env=dict(os.environ,PYTHONUTF8='1'))
    opener=build_opener(ProxyHandler({}));h=None
    def call(path,body):
        request=Request(h['url']+path,data=json.dumps(body,allow_nan=False).encode(),headers={'Content-Type':'application/json','X-Line10-Owner':token})
        with opener.open(request,timeout=15) as response:
            data=response.read(16000001)
            return data if path in ('/render_raw','/projection_cache') else json.loads(data)
    try:
        until=time.monotonic()+90
        while not ready.exists():
            require(process.poll() is None,'CPU_RENDERER_FAILED '+str(evidence/'cpu_renderer.log'))
            require(time.monotonic()<until,'CPU_RENDERER_START_TIMEOUT');time.sleep(.1)
        h=load(ready);verify_source_receipt(h);require(h['adapter']['adapter_type']=='CPU','CPU_GRAPHICS_REQUIRED')
        model=load(base/'model.json');source=Path(next(s['path'] for s in model['sources'] if s['path'].endswith('activities_full.npy')))
        full=np.load(source,mmap_mode='r',allow_pickle=False);ids=np.array([o['model_node_ids'] for o in model['objects']])
        from spatial_state import SpatialRegistry
        spatial=SpatialRegistry();session='CPU_SAVED_ACTIVITY_'+uuid.uuid4().hex
        binding=dict(h['expected_binding'],session_id=session,run_id='2041849d-b1f8-46ad-a059-49b598c19ab2',dt_s=.005,
                     input_time_origin_s=-1.,upstream_map_sha256=spatial.digest,source_evidence_level='OFFLINE_SOFTWARE_REPLAY')
        cache=call('/projection_cache',dict(service_id=h['service_id']));(evidence/'projection.cache').write_bytes(cache)
        h['projection_cache']=dict(sha256=hashlib.sha256(cache).hexdigest(),url='/api/competition-live/cache',upstream_map_sha256=spatial.digest)
        write(evidence/'cache_health.json',h)
        bound=call('/bind',binding);timings=[];receipts=[];packets=[]
        for k in [0,25,50,75,100,125,150,175,200,213,225,250,275,300,325,350,375,400,425,450,475,484]:
            values=np.asarray(full[0,k][ids.reshape(-1)],dtype='<f4');means=values.reshape(8,721).mean(axis=1,dtype=np.float64)
            body={name:binding[name] for name in ('session_id','run_id','model_id','checkpoint_sha256','mapping_sha256','upstream_map_sha256')}
            body.update(bind_id=bound['bind_id'],request_id=uuid.uuid4().hex,step_id=k,state_token=k+1,activity_time_s=-1+k*.005+.005,
                        means=means.tolist(),source_sequence=k,spatial_values_sha256=hashlib.sha256(values.tobytes()).hexdigest())
            begin=time.perf_counter();r,pixels=raw_frame(call('/render_raw',body));timings.append((time.perf_counter()-begin)*1000)
            verify_source_receipt(r);require(r['means']==means.tolist() and not r['draw_performed'],'CACHE_REAL_MEANS_NO_3D_DRAW')
            require(r['fixed_cpu_projection_sha256']==h['fixed_cpu_projection_sha256'],'CACHE_IDENTITY')
            receipts.append(r)
            packets.append(dict(**{name:r[name] for name in ('run_id','session_id','serial','step_id','state_token','activity_time_s','input_time_s') if name in r},serial=k+1,
                source=dict(sequence=k),spatial=dict(values=values.tolist(),map_sha256=spatial.digest,values_sha256=body['spatial_values_sha256']),
                evidence_level='OFFLINE_SOFTWARE_REPLAY'))
            if k in (0,213,484):Image.frombytes('RGBA',(r['image_width'],r['image_height']),pixels).save(evidence/f'actual_saved_state_{k}.png')
        write(evidence/'receipts.json',receipts)
        write(evidence/'packets.json',packets)
        compose=[r['fixed_cpu_compose_ms'] for r in receipts]
        report=dict(status='PASS_ACTUAL_CPU_GRAPHICS_SAVED_REAL_ACTIVITY',frames=len(receipts),actual_new_neural_steps=0,
                    source=str(source),source_run=binding['run_id'],evidence_level='OFFLINE_REPLAY_GRAPHICS_ONLY',
                    full_3D_draws_per_dynamic_frame=0,geometry=h['fixed_cpu_projection'],
                    compose_ms=dict(p50=float(np.median(compose)),p95=float(np.percentile(compose,95))),
                    local_raw_roundtrip_ms=dict(p50=float(np.median(timings)),p95=float(np.percentile(timings,95))),
                    camera_started=False,GPU_neural_started=False,PL_execution=False)
        write(evidence/'cpu_profile.json',report);print(json.dumps({k:report[k] for k in ('status','frames','compose_ms','local_raw_roundtrip_ms')}))
    finally:
        if h:
            try:call('/stop',dict(service_id=h['service_id']))
            except OSError:pass
        try:process.wait(10)
        except subprocess.TimeoutExpired:process.terminate();process.wait(5)
        log.close()


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out');main(parser.parse_args().out)
