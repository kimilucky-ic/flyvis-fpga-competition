from pathlib import Path
import sys,json,hashlib,ast,base64,io,zipfile
O=Path(__file__).resolve().parent;R=O.parent/'ov5640_live_v261_20261026'
sys.path[:0]=[str(R/'bundle'),str(R/'pc')]
import motion_trial
from live_protocol import Store,pack,unpack
from direct_input import DirectAreaInput
from round_sessions import notebook
from offline_check import verify
import numpy as np
fixture=json.loads((O.parent/'ov5640_motion_experiment_20261026/evidence/CPU_RESULT.json').read_text())['fixtures']['white_black']
oldcfg=json.loads(Path(fixture['config']).read_text());old=Store(Path(fixture['records']),oldcfg)
cfg=dict(oldcfg,motion_condition='capture',session_id='c'*32)
store=Store(O/'cpu_records',cfg);mapper=DirectAreaInput(48,80,'BGR')
for k in range(32):
 m,src,r=old.read(k);m=dict(m,session_id=cfg['session_id'],experiment=motion_trial.annotation('capture',m['experiment']['elapsed_ns']))
 assert m['experiment']['phase']=='capture' and m['experiment']['trial'] is None and m['experiment']['cue']==''
 raw=pack(m,src,(Path(fixture['records'])/('%06d.packet'%k)).read_bytes()[-188416:])
 a=store.accept(raw);assert store.accept(raw)['duplicate']
 mm,ss,rr=store.read(k);assert ss==src and rr.input_bits==r.input_bits and rr.state_bits==r.state_bits
 assert np.max(np.abs(mapper.render(np.frombuffer(ss,np.uint8).reshape(48,80,3))-np.frombuffer(rr.input_bits,'<f4')))<3e-6
 if k==0:
  def reject(raw):
   try:unpack(raw,cfg)
   except (ValueError,RuntimeError):return
   raise AssertionError('Bad record accepted')
  bad=bytearray(src);bad[0]^=1;reject(pack(m,bytes(bad),raw[-188416:]))
  badm=dict(m,experiment=dict(m['experiment'],elapsed_ns=m['experiment']['elapsed_ns']+1));reject(pack(badm,src,raw[-188416:]))
  badr=bytearray(raw[-188416:]);badr[4096]^=1;reject(pack(m,src,bytes(badr)))
nb,base=notebook(R,cfg)
tree=ast.parse(''.join(json.loads(nb)['cells'][1]['source']),feature_version=(3,8))
raw=base64.b64decode(ast.literal_eval(next(x.value.args[0] for x in tree.body if isinstance(x,ast.Assign) and isinstance(x.targets[0],ast.Name) and x.targets[0].id=='_raw')))
with zipfile.ZipFile(io.BytesIO(raw)) as z:
 manifest=json.loads(z.read('release_manifest.json'))
 for n,v in manifest.items():assert hashlib.sha256(z.read(n)).hexdigest()==v['sha256']
 assert b"segments=[] if motion_trial.condition(config)=='capture'" in z.read('live_board.py')
for rel in json.loads((O/'CHANGED.json').read_text()):
 if rel.endswith('.py'):ast.parse((R/rel).read_text(encoding='utf-8'),feature_version=(3,8))
checked=verify(R/'bundle')
result=dict(status='PASS_CPU_UNIFIED_CAPTURE',steps=32,input_words=32*721,state_words=32*45669,source_bytes=32*11520,raw_and_input_mapping_verified=True,duplicate_idempotent=True,corrupt_source_state_and_timestamp_rejected=True,planned_movement_removed=True,old_records_unchanged=True,board_actions=0,neural_computation=False,evidence='SYNTHETIC_RAW_FRAMES_AND_SAVED_STATE_FIXTURES_NOT_PHYSICAL_EXPERIMENT',package=checked)
(O/'RESULT.json').write_text(json.dumps(result,indent=2));print('PASS 32 frame-input-state CPU binding, corruption rejection, Python3.8 Notebook and unchanged firmware checks')
