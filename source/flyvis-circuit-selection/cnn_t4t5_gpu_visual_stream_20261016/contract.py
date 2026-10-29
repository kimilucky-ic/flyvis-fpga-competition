"""CPU-only identities shared by the Windows viewer and WSL GPU worker."""
from pathlib import Path
import json,hashlib,os,re,time,importlib.util
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
FLY=ROOT.parent/'fly'

def path(value):
    s=str(value)
    if os.name!='nt' and re.match(r'^[A-Za-z]:[/\\]',s): s='/mnt/'+s[0].lower()+'/'+s[3:].replace('\\','/')
    return Path(s)
def load(p): return json.loads(path(p).read_text(encoding='utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with path(p).open('rb') as f:
        for b in iter(lambda:f.read(4*1024**2),b''): h.update(b)
    return h.hexdigest()
def write(p,value):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8');os.replace(t,p)
def imported(name,p):
    import sys
    p=path(p);sys.path.insert(0,str(p.parent));s=importlib.util.spec_from_file_location(name,p)
    m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def check():
    p=load(HERE/'PLAN.json');assert sha(HERE/'PLAN.json')==load(HERE/'FREEZE.json')['sha256']
    for name,digest in p['pins'].items(): assert sha(name)==digest,name
    return p
