from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,socket
import psutil

out=Path(__file__).resolve().parent
gui=out.parents[1]
proof=json.loads((out/'browser_final.json').read_text(encoding='utf-8'))
alive=[]
for path in (gui/'runtime/competition').glob('*/ready.json'):
    data=json.loads(path.read_text(encoding='utf-8'))
    if data.get('service_id')!=proof['service_id']:continue
    try:
        p=psutil.Process(data['pid'])
        if str(path) in p.cmdline():alive.append(p.pid)
    except psutil.Error:pass
s=socket.socket();s.settimeout(1)
try:listening=s.connect_ex(('127.0.0.1',8771))==0
finally:s.close()
files=[gui/n for n in ['competition_policy.py','competition_renderer.py','server.py','test_competition_policy.py','LIGHT_DEMO.md']]
files += [gui.parent/'viewer'/n for n in ['competition.js','competition.css']]
files += [out/n for n in ['actual_light_home.jpg','browser_final.json','idle_check.json','playback.json','policy_tests.log','REPORT.md']]
manifest=[dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size) for p in files]
record=dict(utc=datetime.now(timezone.utc).isoformat(),status='PASS_OWNED_QA_CLOSED' if not alive and not listening else 'NOT_CLOSED',
            owned_renderer_alive=alive,qa_8771_listening=listening,user_desktop_not_operated=True,
            neural_inference_runs=0,board_operations=0,real_GPU_contention_test=False,files=manifest)
(out/'closeout.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in record.items() if k!='files'}))
