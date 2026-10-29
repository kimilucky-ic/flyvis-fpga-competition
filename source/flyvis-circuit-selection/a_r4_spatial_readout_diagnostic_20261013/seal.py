"""Hash this completed delivery; no model execution."""
from pathlib import Path
from study import HERE,dump
from video_io import sha

records=[]
for p in sorted(HERE.rglob('*')):
    if not p.is_file() or any(x in p.parts for x in ['__pycache__','runtime']):continue
    if p.name=='DELIVERY_MANIFEST.json':continue
    records.append(dict(path=p.relative_to(HERE).as_posix(),bytes=p.stat().st_size,sha256=sha(p)))
dump(HERE/'DELIVERY_MANIFEST.json',dict(schema='file-sha256/v1',root=str(HERE),files=len(records),
    bytes=sum(r['bytes'] for r in records),excluded=['__pycache__','runtime','DELIVERY_MANIFEST.json'],records=records))
print(dict(files=len(records),bytes=sum(r['bytes'] for r in records),sha256=sha(HERE/'DELIVERY_MANIFEST.json')))
