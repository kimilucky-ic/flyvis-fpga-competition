"""Finite CPU-only acceptance for additive light profile; no new neural run."""
from pathlib import Path
import base64, hashlib, json, os, subprocess, time, uuid
import urllib.request, urllib.error

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'evidence/competition_light_r1'
OUT.mkdir(parents=True,exist_ok=True)
python=ROOT.parent/'anatomy_trial_20261013/.venv/Scripts/python.exe'
ready_path=OUT/('ready_'+uuid.uuid4().hex+'.json')
token=uuid.uuid4().hex
log=(OUT/'stdio.log').open('w',encoding='utf-8')
process=subprocess.Popen([str(python),'-B',str(ROOT/'bridge.py'),'--port','0','--renderer','cpu',
                          '--profile','light','--owner-token',token,'--tag',OUT.name,
                          '--ready-file',str(ready_path),'--parent-pid',str(os.getpid())],
                         stdout=log,stderr=subprocess.STDOUT,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
deadline=time.monotonic()+60
while not ready_path.exists():
    if process.poll() is not None: raise RuntimeError('Renderer startup failed: '+str(OUT/'stdio.log'))
    if time.monotonic()>deadline: raise TimeoutError('Renderer ready timeout')
    time.sleep(.2)
ready=json.loads(ready_path.read_text(encoding='utf-8'))
client=urllib.request.build_opener(urllib.request.ProxyHandler({}))
def call(path,body=None):
    req=urllib.request.Request(ready['url']+path,data=json.dumps(body).encode() if body is not None else None,
                               headers={'Content-Type':'application/json'})
    with client.open(req,timeout=30) as r: return json.load(r)
health=call('/health')
assert health['service_id']==ready['service_id'] and health['pid']==ready['pid']
assert health['adapter']['adapter_type']=='CPU'
assert health['profile']=='light' and health['rois_visible'] is False
assert health['viewport']==dict(width=800,height=500,pixel_ratio=1)
identity=health['identity']
observed=[]
try:
    for n,(frame,profile) in enumerate([(213,'light'),(214,'light'),(213,'standard'),(213,'light')]):
        body=dict(request_id=f'light-{n}',run_id=identity['run_id'],activity_sha256=identity['activity_sha256'],
                  frame_index=frame,activity_time_s=identity['activity_time_s'][frame],
                  type_filter='T4a',selected_type='T4a',profile=profile)
        response=call('/render',body)
        meta=response['metadata'];image=base64.b64decode(response['png_base64'])
        assert meta['profile']==profile and meta['rois_visible']==(profile=='standard')
        assert meta['frame_index']==frame and meta['activity_time_s']==body['activity_time_s']
        assert meta['viewport']==health['viewport'] and meta['mapping_sha256']==identity['mapping_sha256']
        assert meta['png_sha256']==hashlib.sha256(image).hexdigest()
        assert meta['scale']==identity['scale'] and meta['adapter']['adapter_type']=='CPU'
        (OUT/f'{n}_{profile}_{frame}.png').write_bytes(image)
        (OUT/f'{n}_{profile}_{frame}.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
        observed.append(dict(profile=profile,rois_visible=meta['rois_visible'],frame=frame,
                             png_sha256=meta['png_sha256'],render_and_png_ms=meta['render_and_png_ms'],
                             rate_limit_wait_ms=meta['rate_limit_wait_ms']))
    assert observed[0]['png_sha256']!=observed[2]['png_sha256']
    assert observed[0]['png_sha256']==observed[3]['png_sha256']  # Same camera and saved values after ROI roundtrip.
    assert observed[1]['rate_limit_wait_ms']>0
    before=(OUT/'bridge_events.jsonl').read_text(encoding='utf-8').count('"event": "render"')
    time.sleep(.35)
    call('/health')
    after=(OUT/'bridge_events.jsonl').read_text(encoding='utf-8').count('"event": "render"')
    assert before==after  # Idle health/lifecycle polling does not render another frame.
    try: call('/render',{**body,'profile':'unknown'})
    except urllib.error.HTTPError as e:
        assert e.code==409
    else: raise AssertionError('Invalid profile accepted')
    assert call('/health')['profile']=='light'
    result=dict(status='PASS',adapter=health['adapter'],viewport=health['viewport'],
                renders=observed,idle_extra_renders=after-before,invalid_profile_refused=True,
                geometry_and_camera_preserved_on_profile_roundtrip=True,
                scientific_identity_unchanged=True,no_GPU_test=True,no_neural_inference=True,PL_execution=False)
finally:
    call('/stop',dict(owner_token=token,service_id=health['service_id']))
    process.wait(timeout=10)
    log.close()
try: call('/health')
except (OSError,urllib.error.URLError): result['owned_stop_port_closed']=True
else: raise AssertionError('Owned listener remains open')
(OUT/'acceptance.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result))
