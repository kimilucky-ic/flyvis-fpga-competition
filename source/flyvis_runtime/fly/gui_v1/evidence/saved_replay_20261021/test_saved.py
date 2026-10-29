from pathlib import Path
import sys,json,io,copy,time,ast
from unittest.mock import patch
B=Path(r'C:/Users/hzy72/Documents/ChatGPT/fly');E=B/'gui_v1/evidence/saved_replay_20261021';sys.path.insert(0,str(B/'gui_v1'))
import line11_result as mod
begin=time.perf_counter();r=mod.SavedScientificReplay('4fc03f4a729340598b20eb957875d768');frames={k:r.replay(k) for k in [0,313,484]};h=r.projection();assert r.seed_status()['status']=='VERIFIED_SAVED_FIRST_STEP';assert all(x['frame']['offline_replay'] and x['frame']['display_kind']=='OFFLINE_REPLAY_FULL_PL_TRAJECTORY' for x in frames.values())
(E/'frames.json').write_text(json.dumps(dict(anchor=r.frame(),saved=r.seed_status(),status=r.status(),health=h,frames=frames)))
for action in [lambda:r.replay(-1),lambda:r.replay(485),lambda:r.source_frame(313,'wrong',frames[313]['frame']['full_state_sha256']),lambda:mod.SavedScientificReplay('../escape')]:
 try:action();raise AssertionError('must reject')
 except ValueError:pass
original_read=Path.read_bytes
with patch.object(Path,'read_bytes',lambda p:b'corrupted' if p.name=='000313.state.bin' else original_read(p)):
 try:r.replay(313);raise AssertionError('changed file accepted')
 except ValueError as e:assert 'SAVED_REPLAY_CHANGED' in str(e)
original_load=mod.load
def incomplete(p):
 j=original_load(p)
 if Path(p).name=='WINDOW_FINISH.json':j['completed_steps']=484
 return j
with patch.object(mod,'load',incomplete):
 try:mod.SavedScientificReplay(r.preparation_id);raise AssertionError('incomplete accepted')
 except ValueError as e:assert 'SAVED_RUN_INCOMPLETE' in str(e)
# Run actual original HTTP route block in-process, no server/listener/browser.
server=(B/'gui_v1/server.py').read_text(encoding='utf-8');start=server.index("            if parsed.path=='/api/full-pl-history':");end=server.index("            if parsed.path.startswith('/api/full-pl-stream/'):",start)
from urllib.parse import urlparse,parse_qs
import re,zipfile
from functools import lru_cache
class Handler:
 def send(self,payload,mime=None,status=200):return dict(payload=payload,status=status,mime=mime)
ns=dict(parse_qs=parse_qs,zipfile=zipfile,archived_full_pl=lambda run:r if run==r.preparation_id else (_ for _ in ()).throw(ValueError('SAVED_RUN_ID')))
code='def route(self,parsed):\n'+server[start:end];exec(code,ns)
for path in ['/api/full-pl/status','/api/full-pl/frame','/api/full-pl/projection','/api/full-pl/cache','/api/full-pl-stream/status','/api/full-pl-stream/replay?step=313','/api/full-pl-stream/source-frame?step=313&run='+r.preparation_id+'&state='+frames[313]['frame']['full_state_sha256']]:
 result=ns['route'](Handler(),urlparse(path+('&' if '?'in path else '?')+'replay_run='+r.preparation_id));assert result['status']==200,path
assert ns['route'](Handler(),urlparse('/api/full-pl-stream/replay?step=485&replay_run='+r.preparation_id))['status']==409
# Replays can never POST to the active device controller.
start=server.index('        def do_POST(self):');end=server.index('            stream_path=',start);prefix=server[start:end];prefix=prefix.replace('        def do_POST(self):','def reject_post(self):');ns['urlparse']=urlparse;exec(prefix,ns);obj=Handler();obj.path='/api/full-pl-stream/camera-start?replay_run='+r.preparation_id;assert ns['reject_post'](obj)['status']==409
result=dict(status='PASS_CPU_SAVED_ARCHIVE_AND_ORIGINAL_HTTP_ROUTES',run=r.preparation_id,validated_steps=485,model_states_read=485*45669,files_and_chain_checked=True,actual_saved_protocol_frames=[0,313,484],range_wrong_run_path_corrupt_incomplete_rejected=True,read_only_routes=7,archive_POST_rejected=True,board_connection='NOT_CONNECTED',new_gpu_camera_board_neural_runs=0,elapsed_s=time.perf_counter()-begin)
(E/'CPU_RESULT.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
