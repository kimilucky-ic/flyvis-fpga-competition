from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,socket
import psutil

out=Path(__file__).resolve().parent
gui=out.parents[1]
alive=[]
for file in (gui/'runtime/competition').glob('*/ready.json'):
    data=json.loads(file.read_text(encoding='utf-8'))
    try:
        p=psutil.Process(data['pid'])
        if str(file) in p.cmdline():alive.append({'pid':p.pid,'ready_file':str(file)})
    except psutil.Error:pass
sock=socket.socket();sock.settimeout(1)
try:listening=sock.connect_ex(('127.0.0.1',8771))==0
finally:sock.close()
record=dict(utc=datetime.now(timezone.utc).isoformat(),owned_renderers_alive=alive,qa_8771_listening=listening,
            status='PASS_OWNED_SERVICES_CLOSED' if not alive and not listening else 'NOT_CLOSED')
(out/'shutdown.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
files=[gui/n for n in ['competition_replay.py','competition_renderer.py','server.py','desktop_runtime.py','COMPETITION_DEMO.md','COMPETITION_3D_CONTRACT.md']]
files += [gui.parent/'viewer'/n for n in ['competition.js','competition.css','index.html','demo_home.js']]
files += [out/n for n in ['actual_home.jpg','browser_final.json','browser_playback.json','http_acceptance.json','bounded_tests.log','REPORT.md','shutdown.json']]
manifest=[dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in files]
(out/'delivery_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(record))
