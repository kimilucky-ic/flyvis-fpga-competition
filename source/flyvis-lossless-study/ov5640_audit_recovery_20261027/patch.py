from pathlib import Path
import shutil,hashlib,json
O=Path(__file__).resolve().parent;R=O.parent/'ov5640_live_v261_20261026';B=O/'before';B.mkdir(exist_ok=True)
for rel in ['pc/stream_audit.py','FINAL_MANIFEST_SHA256.json']:
 p=B/rel;p.parent.mkdir(exist_ok=True,parents=True);assert not p.exists();shutil.copy2(R/rel,p)
p=R/'pc/stream_audit.py';s=p.read_text('utf-8')
s=s.replace('def refresh(store):','''def retry_read(operation, sleep=time.sleep):
    # Only transient file permission failures. At most five attempts /0.75s wait.
    for attempt in range(5):
        try:return operation()
        except PermissionError:
            if attempt==4:raise
            sleep(.05*(2**attempt))

def refresh(store):''')
s=s.replace('raw=path.read_bytes();m,_,_=unpack(raw,store.config)','raw=retry_read(path.read_bytes);m,_,_=unpack(raw,store.config)')
s=s.replace('store=Store(records,config);rows=[]','store=retry_read(lambda:Store(records,config));rows=[]')
s=s.replace('m,source,r=store.read(k);error=None','m,source,r=retry_read(lambda:store.read(k));error=None')
p.write_text(s,encoding='utf-8')
seal=json.loads((R/'FINAL_MANIFEST_SHA256.json').read_text('utf-8'))
for k,v in seal.items():
 d=hashlib.sha256((R/Path(k)).read_bytes()).hexdigest()
 if k.replace('\\','/')=='pc/stream_audit.py':seal[k]=d
 else:assert d==v,k
(R/'FINAL_MANIFEST_SHA256.json').write_text(json.dumps(seal,ensure_ascii=False,indent=2),encoding='utf-8')
print('One PC audit file patched;83other sealed files unchanged')
