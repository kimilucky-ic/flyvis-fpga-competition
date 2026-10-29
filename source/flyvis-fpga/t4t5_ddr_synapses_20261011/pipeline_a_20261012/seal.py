"""Verify historical sealed evidence and seal this isolated milestone."""
from pathlib import Path
import hashlib,json,psutil
P=Path(__file__).resolve().parent;B=P.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main():
    packages={}
    manifests=[B/'MANIFEST_SHA256.json']+sorted(p for p in B.glob('*/MANIFEST_SHA256.json') if p.parent!=P)
    for manifest in manifests:
        files=load(manifest)['files']
        for name,item in files.items():
            digest=item if isinstance(item,str) else item['sha256']
            assert sha(manifest.parent/name)==digest,str(manifest.parent/name)
        packages[str(manifest.parent.relative_to(B))]=dict(files=len(files),manifest_sha256=sha(manifest))
    alive=[];runs=[]
    for r in sorted((P/'build').glob('*/RUNTIME.json')):
        rt=load(r);runs.append(dict(run=str(r.parent.relative_to(P)),exit_code=rt['exit_code'],stop_reason=rt['stop_reason']))
        for item in rt['processes']:
            try:
                proc=psutil.Process(item['pid'])
                if abs(proc.create_time()-item['created'])<.01:alive.append(item['pid'])
            except psutil.NoSuchProcess:pass
    assert not alive,alive
    preserved=dict(status='PASS_PRIOR_SEALED_FILES_UNCHANGED_OWNED_PROCESSES_EXITED',packages=packages,owned_processes_alive=alive,runs=runs,
        scope='Every file in earlier hardware B manifests; no claim about files edited externally in other lanes')
    save(P/'PRESERVATION_VERIFICATION.json',preserved)
    keep={'.py','.ps1','.sv','.svh','.mem','.json','.md','.tcl','.xdc','.rpt','.csv','.tsv','.log','.jou','.dcp','.txt'}
    files={}
    for p in sorted(P.rglob('*')):
        rel=p.relative_to(P)
        if not p.is_file() or p.suffix.lower() not in keep or p==P/'MANIFEST_SHA256.json':continue
        if any(n in {'tmp','xsim.dir','.Xil','__pycache__'} for n in rel.parts):continue
        files[rel.as_posix()]=dict(bytes=p.stat().st_size,sha256=sha(p))
    result=dict(algorithm='SHA256',scope='Pipeline A source, tests, all run identities/logs, complete accepted raw rows, OOC reports/checkpoint; failed attempts preserved; vendor caches excluded',files=files)
    save(P/'MANIFEST_SHA256.json',result)
    for name,item in files.items():assert sha(P/name)==item['sha256']
    print(json.dumps(dict(status='PASS_SEALED',historical_files=sum(x['files'] for x in packages.values()),new_files=len(files),manifest_sha256=sha(P/'MANIFEST_SHA256.json')),indent=2))
if __name__=='__main__':main()
