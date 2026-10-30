"""Owned run identity and source checks; no neural computations on import."""
from pathlib import Path
import base64, hashlib, importlib.util, json, os, re, sys, time
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
GUI=ROOT.parent/'fly/gui_v1'
def path(p):
    s=str(p)
    if os.name!='nt' and re.match(r'^[A-Za-z]:[/\\]',s):s='/mnt/'+s[0].lower()+'/'+s[3:].replace('\\','/')
    return Path(s)
def load(p):return json.loads(path(p).read_text(encoding='utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with path(p).open('rb') as f:
        for b in iter(lambda:f.read(4*1024**2),b''):h.update(b)
    return h.hexdigest()
def write(p,value):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8');os.replace(t,p)
def imported(name,p):
    p=path(p);spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def check():
    freeze=load(HERE/'FREEZE.json');assert sha(HERE/'PLAN.json')==freeze['PLAN_sha256']
    for file,digest in freeze['pins'].items():assert sha(file)==digest,file
    return load(HERE/'PLAN.json')
