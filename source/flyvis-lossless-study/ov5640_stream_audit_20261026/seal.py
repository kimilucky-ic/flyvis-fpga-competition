from pathlib import Path
import json,hashlib,ast
P=Path('flyvis-lossless-study/ov5640_live_v261_20261026');E=P.parent/'ov5640_stream_audit_20261026';seal=json.loads((E/'before/FINAL_MANIFEST_SHA256.json').read_text());changed=['pc\\live_server.py','assets\\ui.js'];unchanged=0
for name,digest in seal.items():
 if name not in changed:assert hashlib.sha256((P/name).read_bytes()).hexdigest()==digest,name;unchanged+=1
source=json.loads((P.parent/'ov5640_two_rounds_analysis_20261026/SOURCE_SHA256.json').read_text())
for name,digest in source.items():assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==digest,name
for name in changed+['pc\\stream_audit.py']:seal[name]=hashlib.sha256((P/name).read_bytes()).hexdigest()
(P/'FINAL_MANIFEST_SHA256.json').write_text(json.dumps(seal,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
result=dict(status='PASS_CPU_INCREMENTAL_AUDIT_READY_FOR_OPERATOR_SPEED_CHECK',changed_files=changed,new_files=['pc/stream_audit.py'],unchanged_sealed_files=unchanged,old_evidence_files_unchanged=len(source),board_bundle_notebook_firmware_unchanged=True,board_actions=0,tests={n:json.loads((E/n).read_text()) for n in ['FULL_REPLAY_RESULT.json','NEGATIVE_RESULT.json','HTTP_RESULT.json']},limitations=['No new physical speed measurement','Startup preparation unchanged in this PC-only increment','PC processes share disk/CPU; low priority and slow-receiver yielding reduce but cannot prove zero contention','UI progress write conflicts are advisory; complete evidence write errors fail closed'],rollback='before/live_server.py and before/ui.js plus original manifest; use only with idle completed receiver')
(E/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='tests'}))
