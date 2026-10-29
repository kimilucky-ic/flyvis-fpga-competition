"""Small read-only HTTP acceptance of the admitted competition UI."""
from pathlib import Path
import hashlib,json,urllib.request,urllib.error

root=Path(__file__).resolve().parent
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
base='http://127.0.0.1:8771'
def get(path):
    with opener.open(base+path,timeout=120) as r:return r.status,r.headers,r.read()
_,_,body=get('/api/competition');meta=json.loads(body)
assert meta['display_kind']=='OFFLINE_REPLAY' and meta['PL_execution'] is False
checks=[]
for name,spec in meta['arrays'].items():
    status,headers,data=get(spec['url'])
    assert status==200 and headers['X-Run-ID']==meta['run_id']
    assert len(data)==spec['bytes'] and hashlib.sha256(data).hexdigest()==spec['sha256']
    checks.append(name+' wire SHA256 and run: PASS')
bad=dict(run_id='another-ON60',activity_sha256=meta['activity_sha256'],frame_index=240,activity_time_s=meta['activity_time_s'][240],type_filter='all',selected_type='T4a',request_id='http-negative')
request=urllib.request.Request(base+'/api/competition/render',data=json.dumps(bad).encode(),headers={'Content-Type':'application/json','Origin':base})
try:opener.open(request,timeout=10);raise AssertionError('Wrong run accepted')
except urllib.error.HTTPError as e:assert e.code==409;checks.append('wrong run rejected before rendering: 409')
status,_,body=get('/api/health');health=json.loads(body)
catalog=json.loads(get('/api/catalog')[2]);count=sum(len(x['conditions']) for x in catalog['datasets'])
assert count==55
record=dict(status='PASS_READ_ONLY_HTTP',run_id=meta['run_id'],conditions=count,checks=checks,
            source_files=meta['source_files'],manifest_sha256=meta['manifest_sha256'],
            PL_execution=False,FPGA_status='NOT_CONNECTED')
(root/'http_acceptance.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(record,ensure_ascii=False))
