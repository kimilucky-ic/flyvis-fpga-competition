"""CPU-only compact capsule, deferred transfer, local-only and failure tests."""
from pathlib import Path
setup=Path(__file__).with_name('test_live.py').read_text().split('def offline(*a,**k):')[0]
setup=setup.replace("'cpu_'+time.strftime", "'modes_'+time.strftime")
exec(compile(setup,'cpu_fake_setup','exec'),globals())
import capture_binding as cb
from types import SimpleNamespace
summaries={}
for mode in ['after_run','local_only']:
 live_board._RETAINED.clear();receiver=Store(T/(mode+'_receiver'),config);calls=[]
 def send(c,route,data=None):
  assert mode!='local_only','local-only attempted network'
  rt=next(iter(live_board._RETAINED.values()));assert rt.mm.steps==32,'upload during deferred compute'
  calls.append(route)
  if route=='/ingest':return receiver.accept(data)
  if route=='/finish':return receiver.finish(json.loads(data))
  if route=='/camera-close':return receiver.record_camera_close(json.loads(data))
  raise AssertionError(route)
 out=live_board.execute(B,T/mode,dict(config,transfer_mode=mode),authorized=True,boot_id='00000000-0000-0000-0000-000000000004',runtime_factory=Runtime,send=send,upload_wait=10)
 rt=next(iter(live_board._RETAINED.values()));assert rt.mm.steps==32
 total=0;oldtotal=0;sync=[]
 for k in range(32):
  d=out/'capture/bound'/('%06d'%k)
  pre,payload=cb.read_capsule(d/'PREPARED.bin',1152000+2884)
  post,record=cb.read_capsule(d/'COMMITTED.bin',188416)
  m,source,accepted_r=accepted_store.read(k)
  assert payload==source+accepted_r.input_bits
  assert record[128:3012]==accepted_r.input_bits and record[4096:186772]==accepted_r.state_bits
  assert sha(source)==pre['frame_sha256']==post['frame_sha256']
  wire=load_packet(out,k);cm,none,cr=unpack(wire,config);assert none is None and cr.state_bits==accepted_r.state_bits
  assert not (d/'source_frame.bin').exists() and not (d/'actual_state.bin').exists()
  total+=len(wire);oldtotal+=(accepted/'pc/records'/('%06d.packet'%k)).stat().st_size
  profile=json.loads((d/'PACKET_TIMING.json').read_text())['producer_profile']
  sync.append(sum(v['calls'] for name,v in profile.items() if name.startswith('fsync:')))
 assert set(sync)=={3},sync
 if mode=='local_only':
  assert not calls and receiver.final is None
  assert json.loads((out/'TRANSFER.json').read_text())['status']=='LOCAL_ONLY_NOT_SUBMITTED'
 else:assert len(receiver.meta)==32 and receiver.final is not None and receiver.camera_close['status']=='CLOSED'
 summaries[mode]=dict(output=str(out),network_calls=len(calls),wire_bytes=total,old_wire_bytes=oldtotal,reduction_percent=100*(1-total/oldtotal),file_fsync_calls_per_step=3,all32_inputs_sources_states_exact=True)
 ok(mode+' preserves32 inputs/states/raw sources; exactly3 file fsync per step')
# Fail a durable pre/post capsule boundary; never execute next step after uncertainty.
orig=cb.save_capsule
for fail_name,expected_advances in [('PREPARED.bin',0),('COMMITTED.bin',1)]:
 binding=cb.BoundSteps(T/('failure_'+fail_name),2);advances=[]
 m,source,r=accepted_store.read(0);record=(accepted/'pc/records/000000.packet').read_bytes()[-188416:]
 def advance(inputs):advances.append(1);return SimpleNamespace(frame_id=0,sequence=1)
 def injected(path,metadata,payload):
  if Path(path).name==fail_name:raise OSError('CPU injected durability failure')
  return orig(path,metadata,payload)
 cb.save_capsule=injected
 try:
  try:binding.step((0,1,source),lambda _:r.input_bits,advance,lambda _:(r,record))
  except OSError:pass
  else:raise AssertionError('failure ignored')
  assert binding.failed and len(advances)==expected_advances
  try:binding.step((1,2,source),lambda _:r.input_bits,advance,lambda _:(r,record))
  except RuntimeError:pass
  else:raise AssertionError('STEP allowed after failure')
  assert len(advances)==expected_advances
 finally:cb.save_capsule=orig
 ok(fail_name+' failure stops progression without replay')
# Tampered committed payload cannot be uploaded; incomplete PREPARED cannot be loaded.
out=Path(summaries['local_only']['output']);p=out/'capture/bound/000000/COMMITTED.bin';original=p.read_bytes()
try:
 altered=bytearray(original);altered[-1]^=1;p.write_bytes(altered)
 reject(lambda:load_packet(out,0),'corrupt committed capsule rejected')
finally:p.write_bytes(original)
p=out/'capture/bound/000000/PREPARED.bin';original=p.read_bytes()
try:
 p.write_bytes(original[:-1]);reject(lambda:load_packet(out,0),'truncated prepared capsule rejected')
finally:p.write_bytes(original)
result=dict(status='PASS_CPU_R5_MODES_DURABILITY_AND_COMPACT_IDENTITY',tests=results,modes=summaries,board_actions=0,ARM_timing_verified=False)
(T/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');(P/'evidence/latest_modes.txt').write_text(str(T));print(json.dumps(result,indent=2))
