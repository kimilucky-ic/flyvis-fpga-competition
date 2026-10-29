from pathlib import Path
import json,hashlib,ast,datetime
P=Path('flyvis-lossless-study/ov5640_live_ring_20261026').resolve();S=P.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
counts={}
for f in (P/'evidence/BASELINE_SHA256.json',S/'ddr_ring_20261026/evidence/BASELINE_R3_SHA256.json',S/'ov5640_live_60s_r3_analysis_20261026/SOURCE_SHA256.json'):
 m=json.loads(f.read_text())
 for name,h in m.items():
  assert isinstance(h,str),(name,type(h))
  assert sha(Path(name))==h,name
 counts[str(f)]=len(m)
for f in (P/'bundle').glob('*.py'):ast.parse(f.read_text(encoding='utf-8-sig'),feature_version=(3,8))
result_soc=json.loads((S/'ddr_ring_soc_20261026/RESULT.json').read_text())
release=json.loads((P/'bundle/release_info.json').read_text());delivery=json.loads((P/'DELIVERY.json').read_text())
bitgen=json.loads((P/'evidence/BITGEN.json').read_text());assert bitgen['returncode']==0 and bitgen['stop'] is None
assert sha(Path('C:/fpga_work/line11_ring_release_20261026/source.dcp'))==release['source_routed_dcp_sha256']
assert sha(Path('C:/fpga_work/line11_ring_release_20261026/flyvis_official.bit'))==release['bit_sha256']
checks={}
for name in ('PACKAGE_CPU_RESULT.json','TRANSPORT_CPU_RESULT.json','ALLOCATION_STOP_RESULT.json'):
 data=json.loads((P/'evidence'/name).read_text());assert data['status'].startswith('PASS');checks[name]=data
for key,file in (('CPU_REPLAY','latest_cpu.txt'),('CPU_FAULT','latest_fault.txt')):
 data=json.loads((Path((P/'evidence'/file).read_text())/'RESULT.json').read_text());assert data['status'].startswith('PASS');checks[key]=data
# Original PC full state oracle is unchanged; do not rerun old arithmetic tests.
assert (P/'pc/full_audit.py').read_bytes()==(S/'ov5640_live_60s_20261026/pc/full_audit.py').read_bytes()
commands=dict(python='C:/Users/hzy72/Documents/ChatGPT/fly/.venv/Scripts/python.exe -X utf8 -B',cwd=str(P),commands=['bitgen.py','build_release.py','bundle/offline_check.py','tests/test_ring.py','tests/test_fault_guard.py','tests/test_allocation_stop.py','tests/test_release.py','tests/test_transport.py'],Vivado_command=bitgen['command'],notes=['bitgen only from sealed routed DCP; no synthesis/place-route rerun','First restricted localhost test failed WinError10013; approved localhost-only rerun passed','Transport test uses temporary127.0.0.1 only; server closed','build_release.py repeated with existing session yielded identical Notebook hash'],board_operations=0,GPU_operations=0)
(P/'COMMANDS.json').write_text(json.dumps(commands,indent=2))
r=dict(status='PASS_OFFLINE_RING_BIT_HWH_NOTEBOOK_CPU_RELEASE_BOARD_PENDING',evidence='VIVADO_BIT_GENERATION_AND_CPU_VERIFICATION_NOT_BOARD',tool='Vivado2026.1.1 SW6605303',candidate=str(P),network=dict(nodes=45669,edges=1513231,input_words=721,arithmetic='UNCHANGED_STRICT_FP32',clock_target_hz=100000000),configuration=dict(duration_s=60,ring_slots=64,ring_bytes=12058624,ring_MiB=11.5,queue_capacity=32,prior_queue_capacity=2,minimum_period_s=0,prior_R3_minimum_period_ms=112.5703564727955,batch_steps=16,max_steps_safety_bound=4096,transfer_mode='live_compact'),release=release,delivery=delivery,implementation=dict(source=str(S/'ddr_ring_soc_20261026/RESULT.json'),resources=result_soc['resources'],timing=result_soc['timing'],conditional_external_IO=True),bitgen=bitgen,checks=checks,preservation=counts,board_operations=0,GPU_operations=0,real_board_speed=None,physical_clock_measured=False,core_nominal_ms=21.99975,core_ms_is_not_frame_time=True,limits=['New ring ABI and cache/release behavior not yet verified on ARM/physical board','CPU194-step virtual60s uses saved R3 payloads and expected-state oracle, not new neural compute or speed measurement','Prior full-network5-step RTL evidence reused; no new full RTL run','Conditional external camera timing and prior IIC/LCD delay limitations retained','Official synchronous camera can block;60s is not a hard deadline guarantee','Queue absorbs bounded stalls; sustained slow storage backpressures rather than dropping','Power loss or closing kernel can lose records not yet durably saved','Localhost receiver tests do not prove board Ethernet or rendered browser FPS','2026.1 compatibility has not been tested; release uses2026.1.1'],next='Operator runs dedicated new Notebook once, then inspect all saved states, normal close, released count/occupied slots and whole-loop timings; keep R3 rollback')
(P/'RESULT.json').write_text(json.dumps(r,indent=2))
seal={}
for f in P.rglob('*'):
 if f.is_file() and '__pycache__' not in f.parts and ('evidence' not in f.relative_to(P).parts or f.parent==P/'evidence') and f.name!='FINAL_MANIFEST_SHA256.json':seal[str(f.relative_to(P))]=sha(f)
(P/'FINAL_MANIFEST_SHA256.json').write_text(json.dumps(seal,indent=2))
print(json.dumps(dict(status=r['status'],sealed_files=len(seal),preserved_counts=list(counts.values()),bit_sha256=release['bit_sha256'],notebook_sha256=delivery['notebook_sha256'])))
