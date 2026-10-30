"""CPU fail-stop check; use accepted fake runtime setup, no HTTP server or board."""
from pathlib import Path
s=Path(__file__).with_name('test_live.py').read_text()
s=s[:s.index('rt=next(iter(live_board._RETAINED.values()))')]
s=s.replace("'cpu_'+time.strftime", "'cpu_failure_'+time.strftime")
s=s.replace(' native_calls.append(raw)',' native_calls.append(raw);raise RuntimeError("CPU injected decode failure")')
s=s.replace('assert progress==[8,16,24,32],progress','assert progress==[],progress')
exec(compile(s,'CPU_failure_setup','exec'),globals())
rt=next(iter(live_board._RETAINED.values()))
assert rt.mm.steps==1 and rt.video.k==1 and rt.owner['bridge'].failed
assert events.count('close')==0 and rt.owner['bridge'].binding.next==0
assert not rt.owner['gc_trace'].active and rt.owner['gc_trace'].callback not in __import__('gc').callbacks
assert (out/'IN_DOUBT.json').exists()
assert (out/'capture/bound/000000/RETURNED_UNCOMMITTED.bin').stat().st_size==188416
f=json.loads((out/'FINISH.json').read_text());assert f['status']=='STOPPED_KEEP_KERNEL_AND_BUFFERS'
assert f['context']['GC_EVENTS.json']['collector_policy_before']==f['context']['GC_EVENTS.json']['collector_policy_after']
r=dict(status='PASS_CPU_FAILURE_STOP_AND_DIAGNOSTIC_DETACH',fake_steps=1,committed_steps=0,no_retry=True,no_camera_close=True,returned_record_retained=True,gc_callback_removed=True,board_operations=0)
(T/'RESULT.json').write_text(json.dumps(r,indent=2)+'\n');(P/'evidence/latest_failure.txt').write_text(str(T));print(json.dumps(r,indent=2))
