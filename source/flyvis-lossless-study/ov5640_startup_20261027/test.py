from pathlib import Path
import json,sys,time,ast,hashlib,importlib.util
from unittest.mock import patch
O=Path(__file__).resolve().parent;R=O.parent/'ov5640_live_v261_20261026';sys.path.insert(0,str(R/'bundle'))
from ram_records import RamRecords
from batch_records import BatchRecords
E=O/'evidence';E.mkdir(exist_ok=True);root=(E/'paths').resolve();root.mkdir();(root/'transport').mkdir()
def paths(root,n):
 out=[]
 for k in range(n):
  d=root/'capture/bound'/('%06d'%k);out.append(d);out.extend(d/x for x in ('PREPARED.bin','COMMITTED.bin','CYCLE_CHECK.json','PUBLICATION.json','TIMING.json','PACKET_TIMING.json','WORKER_TIMING.json','RETURNED_UNCOMMITTED.bin','IN_DOUBT.json'));out.extend((root/'transport'/('%06d.packet'%k),root/'transport'/('%06d.ack.json'%k)));out.append(root/('CAMERA_BUFFER.json' if k==0 else 'CAMERA_BUFFER_%06d.json'%k))
 return out
old=RamRecords(root);t=time.perf_counter();known=paths(root,4096);old.prevalidate(known);old_ms=(time.perf_counter()-t)*1000
new=RamRecords(root);count=[0];resolve=Path.resolve
def counted(p,*a,**kw):count[0]+=1;return resolve(p,*a,**kw)
t=time.perf_counter()
with patch.object(Path,'resolve',counted):receipt=new.prevalidate_generated_steps(root,4096)
new_ms=(time.perf_counter()-t)*1000
assert new.known_keys==old.known_keys and receipt['paths']==53248 and count[0]<=3
with patch.object(Path,'resolve',side_effect=AssertionError('runtime regression')):
 for p in known:assert new.key(p)==old.known_keys[str(p)]
new.start();p=root/'transport/000000.packet';assert new.put(p,b'exact');assert new.get(p)==b'exact'
def reject(fn):
 try:fn()
 except (ValueError,RuntimeError):return
 raise AssertionError('must reject')
reject(lambda:new.prevalidate_generated_steps(root,1))
for value in [0,4097,True,1.5]:reject(lambda:RamRecords(root).prevalidate_generated_steps(root,value))
(root/'transport/intruder').write_bytes(b'x');reject(lambda:RamRecords(root).prevalidate_generated_steps(root,1))
# Separate fresh roots test existing capture namespace and redirected anchor.
r2=(E/'dirty').resolve();r2.mkdir();(r2/'transport').mkdir();(r2/'capture').mkdir();reject(lambda:RamRecords(r2).prevalidate_generated_steps(r2,1))
r3=(E/'redirect').resolve();r3.mkdir();(r3/'transport').mkdir()
real=Path.resolve
def redirected(p,*a,**kw):return root if p==r3/'transport' else real(p,*a,**kw)
with patch.object(Path,'resolve',redirected):reject(lambda:RamRecords(r3).prevalidate_generated_steps(r3,1))
# Fresh index cannot introduce escape paths: generic unknown-path validation unchanged.
assert RamRecords(root).key(root/'../escape') is None
for f in ['ram_records.py','live_board.py']:ast.parse((R/'bundle'/f).read_text('utf-8'),feature_version=(3,8))
# Read latest accepted run without copying huge timing arrays.
sid=json.loads((R/'pc/ACTIVE_ROUND.json').read_text())['session_id'];D=R/'pc/rounds'/sid/'records';f=json.loads((D/'FINISH.json').read_text());a=json.loads((D/'audit/RESULT.json').read_text());c=json.loads((D/'CAMERA_CLOSE.json').read_text());ph=f['context'];names=['PREPARE','LOAD','CLOCK_HP','FRESH_ABI','ALLOCATE_RESTORE','OFFICIAL_SENSOR_AND_VIDEO_START','BOUNDED_CAPTURE_AND_STEPS'];times={names[i]:(ph['PHASE_'+names[i+1]+'.json']['monotonic_ns']-ph['PHASE_'+names[i]+'.json']['monotonic_ns'])/1e6 for i in range(len(names)-1)}
result=dict(status='PASS_CPU_STARTUP_INDEX',path_count=53248,old_new_keys_identical=True,old_per_file_resolves=53248,new_resolve_calls=count[0],pc_old_ms=old_ms,pc_new_ms=new_ms,timing_scope='THIS_WINDOWS_CPU_ONLY_NOT_ARM',runtime_known_keys_zero_resolves=True,negative_tests=['active','invalid bounds','nonempty transport','existing capture','redirected anchor','escape'],latest_accepted_run=dict(session=sid,steps=a['steps'],elapsed_s=f['duration']['elapsed_seconds'],ms_per_step=f['duration']['elapsed_seconds']*1000/a['steps'],audit=a['status'],mismatch=a['mismatch_words'],close=c['status'],stage_ms=times,pre_PREPARE_timing='NOT_RECORDED_IN_OLD_RUN'),board_actions=0)
(E/'CPU_RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(result,ensure_ascii=False))
# Reuse one integration case, no old control suite rerun.
s=(O.parent/'ov5640_async_persist_20261026/tests/test_ring.py').read_text('utf-8')
s=s.replace("S=P/'bundle'","S=P.parent/'ov5640_live_v261_20261026/bundle'")
a=s.index('# Control and model negatives;');b=s.index('# Fresh CPU runtime',a)
s=s[:a]+"plan=memory_plan(config,'CmaTotal: 131072 kB\\nCmaFree: 3972 kB\\nMemAvailable: 731172 kB\\n')\n"+s[b:]
(O/'tests').mkdir(exist_ok=True);(O/'tests/test_integration.py').write_text(s,encoding='utf-8')
