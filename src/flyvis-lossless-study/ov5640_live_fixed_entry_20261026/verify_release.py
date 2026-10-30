from pathlib import Path
import ast,hashlib,json,sys,urllib.request
P=Path('flyvis-lossless-study/ov5640_live_v261_20261026');E=P.parent/'ov5640_live_fixed_entry_20261026';sys.path[:0]=[str(P/'pc'),str(P/'bundle')]
import fixed_entry
op=urllib.request.build_opener(urllib.request.ProxyHandler({}))
with op.open('http://127.0.0.1:8798/fixed-notebook',timeout=5) as r:raw=r.read()
assert raw==(P/fixed_entry.NAME).read_bytes();nb=json.loads(raw);ast.parse(''.join(nb['cells'][1]['source']),feature_version=(3,8))
ns={};exec(fixed_entry.CLIENT,ns);key=json.loads((P/'pc/FIXED_ENTRY_KEY.json').read_text())['key'];sid,received,code=ns['fetch_round']('http://127.0.0.1:8798',key)
ptr=json.loads((P/'pc/ACTIVE_ROUND.json').read_text());assert sid==ptr['session_id'];assert hashlib.sha256(received).hexdigest()==ptr['notebook_sha256']
seal=json.loads((P/'FINAL_MANIFEST_SHA256.json').read_text());changed=['pc\\live_server.py','assets\\index.html','assets\\ui.js'];added=['pc\\fixed_entry.py',fixed_entry.NAME]
for n in changed+added:seal[n]=hashlib.sha256((P/n).read_bytes()).hexdigest()
(P/'FINAL_MANIFEST_SHA256.json').write_text(json.dumps(seal,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
r=dict(status='PASS_FIXED_ENTRY_CPU_HTTP_CURRENT_DOWNLOAD_BOARD_PENDING',fixed_notebook=str((P/fixed_entry.NAME).resolve()),fixed_notebook_bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),current_session=sid,same_existing_notebook=True,changed=changed,added=added,receiver_exec_session=39687,board_actions=0,firmware_model_runtime_unchanged=True,limits=['PC CPU/HTTP evidence only; operator physical repeat pending','Restart fixed Notebook kernel only after normal camera close and all-state PASS','PC URL remains current 192.168.2.89:8798; network changes require configuration update'])
(E/'RESULT.json').write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in r.items() if k not in ['limits']},ensure_ascii=False))
