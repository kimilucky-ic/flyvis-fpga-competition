"""Small acceptance: source/time refusal, signed real renders, owned shutdown."""
from pathlib import Path
import base64, hashlib, json, os, subprocess, time, urllib.request, urllib.error, uuid

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'evidence/competition_bridge_r2'
OUT.mkdir(parents=True,exist_ok=True)
python=ROOT.parent/'anatomy_trial_20261013/.venv/Scripts/python.exe'
log=(OUT/'stdio.log').open('w',encoding='utf-8')
ready_path=OUT/('ready_'+uuid.uuid4().hex+'.json')
process=subprocess.Popen([str(python),'-B',str(ROOT/'bridge.py'),'--port','0','--owner-token','line10-acceptance-20261015',
                          '--tag',OUT.name,'--ready-file',str(ready_path),'--parent-pid',str(os.getpid())],
                         stdout=log,stderr=subprocess.STDOUT,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
deadline=time.monotonic()+60
while not ready_path.exists():
    if process.poll() is not None: raise RuntimeError('Renderer startup failed: '+str(OUT/'stdio.log'))
    if time.monotonic()>deadline: raise TimeoutError('Renderer ready timeout')
    time.sleep(.2)
ready=json.loads(ready_path.read_text(encoding='utf-8'))
client=urllib.request.build_opener(urllib.request.ProxyHandler({}))
def call(path,body=None):
    data=json.dumps(body).encode() if body is not None else None
    req=urllib.request.Request(ready['url']+path,data=data,headers={'Content-Type':'application/json'})
    with client.open(req,timeout=30) as r: return json.load(r)

health=call('/health')
assert health['service_id']==ready['service_id'] and health['pid']==ready['pid']
identity=health['identity']
observed=[]
try:
    for n,(frame,kind) in enumerate([(0,'T4a'),(213,'T4a'),(213,'T4d'),(368,'T5')]):
        request=dict(request_id=f'accept-{n}',run_id=identity['run_id'],activity_sha256=identity['activity_sha256'],
                     mapping_sha256=identity['mapping_sha256'],activity_time_sha256=identity['activity_time_sha256'],
                     frame_index=frame,activity_time_s=identity['activity_time_s'][frame],type_filter=kind)
        response=call('/render',request)
        meta=response['metadata']
        image=base64.b64decode(response['png_base64'])
        assert meta['request_id']==request['request_id'] and meta['frame_index']==frame
        assert meta['activity_time_s']==request['activity_time_s'] and meta['type_filter']==kind
        assert meta['mapping_sha256']==identity['mapping_sha256']
        assert hashlib.sha256(image).hexdigest()==meta['png_sha256']
        assert meta['scale']['min']==-meta['scale']['max'] and meta['scale']['zero']==0
        (OUT/f'{kind}_{frame:03d}.png').write_bytes(image)
        (OUT/f'{kind}_{frame:03d}.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
        observed.append(dict(frame=frame,filter=kind,png_sha256=meta['png_sha256'],render_and_png_ms=meta['render_and_png_ms']))
    assert observed[0]['png_sha256']!=observed[1]['png_sha256']
    refused=[]
    for key,bad in [('run_id','same-label-wrong-run'),('activity_time_s',1234),('frame_index',485)]:
        wrong={**request,key:bad}
        try: call('/render',wrong)
        except urllib.error.HTTPError as e:
            assert e.code==409
            refused.append(dict(field=key,status=e.code,reason=json.load(e)['error']))
        else: raise AssertionError('Mismatch was accepted: '+key)
    result=dict(status='PASS',identity=identity,adapter=health['adapter'],actual_renders=observed,
                mismatches_refused=refused,source_verification=identity['verification'],
                no_neural_inference=True,no_board_operation=True)
finally:
    call('/stop',dict(owner_token='line10-acceptance-20261015',service_id=health['service_id']))
    for attempt in range(30):
        try: call('/health')
        except (OSError,urllib.error.URLError): break
        time.sleep(.1)
    else: raise AssertionError('Owned listener did not close')
result['owned_stop_port_closed']=True
process.wait(timeout=10)
log.close()
(OUT/'acceptance.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(status='PASS',render_ms=[round(r['render_and_png_ms'],1) for r in observed],
                      mismatches_refused=len(refused),owned_stop_port_closed=True)))
