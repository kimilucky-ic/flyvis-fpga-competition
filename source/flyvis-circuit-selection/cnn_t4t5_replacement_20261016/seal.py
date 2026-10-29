"""Delivery manifest over this completed pilot only; no training/rollouts."""
from common import HERE,dump,sha,check_frozen
check_frozen()
records=[]
for p in sorted(HERE.rglob('*')):
    if not p.is_file() or p.name=='DELIVERY_MANIFEST.json' or any(x in p.parts for x in ['runtime','__pycache__']):continue
    records.append(dict(path=p.relative_to(HERE).as_posix(),bytes=p.stat().st_size,sha256=sha(p)))
dump(HERE/'DELIVERY_MANIFEST.json',dict(files=len(records),bytes=sum(r['bytes'] for r in records),
    excluded=['runtime','__pycache__','DELIVERY_MANIFEST.json'],records=records))
print(dict(files=len(records),bytes=sum(r['bytes'] for r in records),sha256=sha(HERE/'DELIVERY_MANIFEST.json')))
