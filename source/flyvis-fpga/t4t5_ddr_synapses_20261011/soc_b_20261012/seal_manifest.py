"""Seal B sources, accepted evidence, failed attempt records and candidate files."""
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parent
B=P/json.loads((P/'LATEST_BUILD.json').read_text())['build']
files=[]
for f in P.rglob('*'):
    if not f.is_file() or f.name=='MANIFEST_SHA256.json' or '__pycache__' in f.parts:continue
    rel=f.relative_to(P)
    if rel.parts[0]!='work':files.append(f)
for f in B.iterdir():
    if f.is_file() and f.suffix in {'.json','.txt','.rpt','.xdc','.tcl','.bit','.hwh','.dcp'}:files.append(f)
for folder in (B/'source',B/'stages'):
    for f in folder.rglob('*'):
        if f.is_file():files.append(f)
data={str(f.relative_to(P)).replace('\\','/'):dict(bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in sorted(set(files))}
result=dict(scope='B full SoC sources, all stage evidence, routed reports/DCP and BIT/HWH candidate; tool caches and bulk ROM omitted, ROM identities in INPUT_IDENTITY/SYSTEM_AUDIT',
            status=json.loads((P/'SOC_RESULT.json').read_text())['status'],files=data)
(P/'MANIFEST_SHA256.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps(dict(status=result['status'],sealed_files=len(data))))
