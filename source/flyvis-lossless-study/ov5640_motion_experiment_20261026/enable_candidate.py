from pathlib import Path
import sys,json,hashlib,shutil
P=Path('flyvis-lossless-study/ov5640_motion_experiment_20261026').resolve();R=P.parent/'ov5640_live_v261_20261026'
seal=json.loads((R/'FINAL_MANIFEST_SHA256.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert all(sha(R/n)==v for n,v in seal.items()),'release changed'
a=json.loads((R/'pc/ACTIVE_ROUND.json').read_text());assert a['session_id']=='1f942a59a8515cd6a2e62ddd5fc7bc42'
d=R/'pc/rounds'/a['session_id'];c=json.loads((d/'records/CAMERA_CLOSE.json').read_text());audit=json.loads((d/'records/audit/RESULT.json').read_text())
assert c['status']=='CLOSED' and audit['status']=='PASS_ALL_SAVED_STATES' and audit['steps']==1081 and audit['mismatch_words']==0
assert json.loads((P/'evidence/FINAL_PACKAGE_RESULT.json').read_text())['status']=='PASS_FINAL_CPU_PACKAGE'
changed=[];added=[]
for folder in ('bundle','pc','assets'):
 for f in (P/folder).iterdir():
  if not f.is_file() or (folder=='pc' and f.suffix!='.py'):continue
  rel=f.relative_to(P);dest=R/rel
  if dest.exists() and dest.read_bytes()==f.read_bytes():continue
  if dest.exists():
   backup=P/'before'/rel;backup.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(dest,backup);changed.append(str(rel))
  else:added.append(str(rel))
  shutil.copyfile(f,dest)
shutil.copyfile(R/'FINAL_MANIFEST_SHA256.json',P/'before/FINAL_MANIFEST_SHA256.json')
shutil.copyfile(R/'LINE11_START_60S.ipynb',P/'before/LINE11_START_60S.ipynb')
for rel in changed+added:
 key=next((k for k in seal if Path(k)==Path(rel)),rel)
 seal[key]=sha(R/rel)
(R/'FINAL_MANIFEST_SHA256.json').write_text(json.dumps(seal,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
assert all(sha(R/n)==v for n,v in seal.items())
(P/'evidence/INSTALL_RESULT.json').write_text(json.dumps(dict(status='CPU_VALIDATED_SOURCES_INSTALLED',changed=changed,added=added,active_round=a['session_id'],active_round_unchanged=True,board_actions=0,receiver_restart_pending=True),indent=2))
print('Changed',changed,'Added',added)
