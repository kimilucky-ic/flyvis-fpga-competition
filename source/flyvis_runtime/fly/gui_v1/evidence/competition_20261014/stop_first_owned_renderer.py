"""One-off cleanup for the first QA renderer that failed venv-PID admission."""
from pathlib import Path
import json
import urllib.request
import psutil

root=Path(__file__).resolve().parents[2]/'runtime/competition'
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
for file in root.glob('*/ready.json'):
    data=json.loads(file.read_text(encoding='utf-8'))
    try:
        process=psutil.Process(data['pid']);args=process.cmdline()
        if str(file) not in args or '--owner-token' not in args:continue
        token=args[args.index('--owner-token')+1]
        req=urllib.request.Request(data['url']+'/stop',data=json.dumps(dict(owner_token=token,service_id=data['service_id'])).encode(),headers={'Content-Type':'application/json'})
        print(opener.open(req,timeout=3).read().decode())
    except (psutil.Error,OSError,ValueError) as error:print(type(error).__name__)
