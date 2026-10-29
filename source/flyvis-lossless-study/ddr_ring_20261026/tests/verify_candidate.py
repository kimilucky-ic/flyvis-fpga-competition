"""Read-only preservation/source verification; writes only this candidate's evidence."""
from pathlib import Path
import ast,json,hashlib,sys
P=Path(__file__).resolve().parents[1];root=P.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checked={}
for source in (P/'evidence/BASELINE_R3_SHA256.json',root/'ov5640_live_60s_r3_analysis_20261026/SOURCE_SHA256.json'):
 data=json.loads(source.read_text());assert all(Path(p).is_file() and sha(Path(p))==h for p,h in data.items()),source
 checked[str(source)]=len(data)
core=('fp32_rne.sv','flyvis_lane.sv','compact_edge_gen.sv','banked_state_mem.sv','sync_mem.sv')
frozen={}
for n in core:
 a=P/'rtl'/n;b=root/'ov5640_official_2026_20261024/neural'/n
 assert a.read_bytes()==b.read_bytes();frozen[n]=sha(a)
for n in ('meta.hex','map.hex','rows.hex','initial.hex'):
 f=root/'hole_pipeline_20261016/images'/n;frozen[str(f)]=sha(f)
for n in ('direct_input.py','capture_binding.py','cycle_contract.py','payload_check.c','arm_barrier.c'):
 a=P/'software'/n;b=root/'ov5640_live_60s_r3_20261026/bundle'/n
 assert a.read_bytes()==b.read_bytes();frozen[n]=sha(a)
for stage in ('rtl_full_r1','rtl_unit_r1'):
 ids=json.loads((P/stage/'IDENTITY.json').read_text())
 assert all(sha(Path(f))==h for f,h in ids.items()),stage
for f in (P/'software').glob('*.py'):ast.parse(f.read_text(encoding='utf-8'),feature_version=(3,8))
sys.path.insert(0,str(P/'software'));import live_board
from unittest.mock import patch
with patch('offline_check.verify',return_value={}):
 for slots in (0,16,65):
  try:live_board.execute(P/'software',P/'evidence',dict(max_steps=4096,duration_s=60.,ring_slots=slots),authorized=True,runtime_factory=lambda *a:(_ for _ in ()).throw(AssertionError('must not create runtime')))
  except ValueError:pass
  else:raise AssertionError('invalid ring admitted')
assert not list(P.glob('*.ipynb')) and not list((P/'software').glob('*.bit'))
result=dict(status='PASS_BASELINE_AND_CORE_PRESERVATION_PY38_CPU_GUARDS',baseline_counts=checked,frozen=frozen,rtl_test_source_identities_match=True,python38_syntax_files=len(list((P/'software').glob('*.py'))),hardware_operations=0)
(P/'evidence/PRESERVATION.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in result.items() if k!='frozen'},indent=2))
