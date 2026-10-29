from pathlib import Path
import sys,json,psutil,time,argparse
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parent/'physical_20261012'))
from gate_policy import terminate_owned
ap=argparse.ArgumentParser();ap.add_argument('stage',choices=['simulate_6','simulate_7']);args=ap.parse_args()
stage=P/'work/soc_20261012_200812_818532/stages'/args.stage
matches=[]
for proc in psutil.process_iter(['name','cmdline']):
    try:
        cmd=' '.join(proc.info['cmdline'] or [])
        if proc.info['name'].lower()=='pwsh.exe' and str(stage).lower() in cmd.lower() and '-Stage simulate' in cmd:
            matches.append(proc)
    except (psutil.NoSuchProcess,psutil.AccessDenied): pass
assert len(matches)==1, 'Only exact B stage launcher may be stopped'
owned=[matches[0]]+matches[0].children(recursive=True)
seen={(p.pid,p.create_time()):{} for p in owned}
result=dict(reason='B_ONLY_DIAGNOSTIC_STOP_GROWING_MEMORY_PRESERVE_PROGRESS',
            stage=str(stage),at=time.time(),owned=[dict(pid=p.pid,created=p.create_time(),name=p.name()) for p in owned],
            actions=terminate_owned(owned,seen))
(stage/'DIAGNOSTIC_STOP.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
