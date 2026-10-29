# Fail-closed review of this exact isolated routed design; no tool/board launch.
from pathlib import Path
import json,hashlib,re,shutil,xml.etree.ElementTree as ET
P=Path(__file__).resolve().parent;B=Path('C:/fpga_work/line11_ring_20261026');R=P.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert (B/'ROUTE_COMPLETED_REVIEW_REQUIRED.txt').is_file()
D=B/'release_routed'
t=(D/'timing_routed.rpt').read_text();u=(D/'utilization_routed.rpt').read_text();d=(D/'drc.rpt').read_text();c=(D/'cdc.rpt').read_text();b=(D/'bus_skew.rpt').read_text();ck=(D/'check_timing.rpt').read_text();route=(D/'route_status.rpt').read_text()
line=re.search(r'WNS\(ns\).*\n[^\n]*\n([^\n]+)',t).group(1).split();assert len(line)==12,line
v=list(map(float,line));assert min(v[0],v[4],v[8])>=0 and v[2]==v[6]==v[10]==0,('TIMING_FAILED',v)
for name in ('no_clock','unconstrained_internal_endpoints','multiple_clock','loops','latch_loops'):assert 'checking '+name+' (0)' in ck
assert not re.search(r'^\|[^\n]*\|\s*(Error|Critical Warning)\s*\|',d,re.M)
assert 'REQP-1839' not in d and not re.search(r'^CDC-\d+\s+Critical',c,re.M)
assert 'VIOLATED' not in b
for name in ('nets with routing errors','unrouted nets','partially routed nets'):
 m=re.search(re.escape(name)+r'\.*\s*:\s*(\d+)',route,re.I)
 if name=='nets with routing errors':assert m,('missing route errors',route)
 if m:assert int(m[1])==0,(name,m[1])
needed=int(re.search(r'# of routable nets\.*\s*:\s*(\d+)',route)[1]);routed=int(re.search(r'# of fully routed nets\.*\s*:\s*(\d+)',route)[1]);assert needed==routed and needed>0
assert 'Number of Failed Nets               = 0' in (B/'route.log').read_text()
for stage in ('migrate3','combine','synth','route'):
 log=(B/(stage+'.log')).read_text(errors='replace')
 assert not re.search(r'^(ERROR:|CRITICAL WARNING: \[Constraints 18-515\])',log,re.M),(stage,'ERROR_OR_SEGMENTATION')
resources={}
for label,name in [('Slice LUTs','LUT'),('Slice Registers','FF'),('Block RAM Tile','BRAM36_equivalent'),('DSPs','DSP')]:
 resources[name]=float(re.search(r'^\| '+label+r'\s*\|\s*([\d.]+)',u,re.M)[1])
base=json.loads((R/'ov5640_official_2026_20261024/RESULT.json').read_text())
baseline_checks={}
for f in (P/'evidence/BASELINE_BUILD_SHA256.json',R/'ddr_ring_20261026/evidence/BASELINE_R3_SHA256.json',R/'ov5640_live_60s_r3_analysis_20261026/SOURCE_SHA256.json'):
 ids=json.loads(f.read_text());assert all(sha(Path(n))==h for n,h in ids.items());baseline_checks[str(f)]=len(ids)
ids=json.loads((R/'ddr_ring_20261026/SOURCE_SHA256.json').read_text());assert all(sha(R/'ddr_ring_20261026'/n)==h for n,h in ids.items())
inputs=json.loads((P/'evidence/BUILD_INPUTS.json').read_text())
for name,row in inputs['relocations'].items():assert sha(B/'neural'/name)==row['build_sha256']
# Clock and routing widths come from generated hardware metadata, not filenames.
hwh=B/'imported3/base/hw_handoff/base.hwh';tree=ET.parse(hwh)
ps=[x for x in tree.iter('MODULE') if x.get('INSTANCE')=='ps7_0'];assert len(ps)==1
params={x.get('NAME'):x.get('VALUE') for x in ps[0].iter('PARAMETER')}
assert float(params['PCW_FPGA0_PERIPHERAL_FREQMHZ'])==100
assert params['PCW_USE_S_AXI_HP0']=='1' and params['PCW_USE_S_AXI_HP1']=='1'
assert params['PCW_S_AXI_HP0_DATA_WIDTH']=='64' and params['PCW_S_AXI_HP1_DATA_WIDTH']=='64'
assert (B/'integration_contract.txt').is_file() and '0x00110005' in (B/'integration_contract.txt').read_text()
structure=(D/'ring_structure.txt').read_text();assert 'clock_period_ns 10' in structure and 'released_count_reg' in structure
rel=P/'release';rel.mkdir(exist_ok=False)
for root in (B/'release',D):
 for f in root.iterdir():
  if f.is_file() and f.suffix in ('.rpt','.xdc','.dcp','.txt'):shutil.copy2(f,rel/f.name)
shutil.copy2(hwh,rel/'base.hwh');shutil.copy2(B/'imported3/base/base.bd',rel/'base.bd')
shutil.copy2(B/'vendor/base.xdc',rel/'pin_constraints.xdc');shutil.copy2(B/'camera_budget.xdc',rel/'camera_budget.xdc')
for f in B.iterdir():
 if f.is_file() and f.suffix in ('.tcl','.jou','.log','.ps1'):shutil.copy2(f,P/'evidence'/f.name)
def slack(name):
 s=(D/name).read_text();m=re.search(r'Slack \(MET\) :\s+([0-9.]+)ns',s);assert m;return float(m[1])
result=dict(status='PASS_FULL_SOC_ROUTED_100MHZ_CONDITIONAL_EXTERNAL_IO',evidence='VIVADO_FULL_SOC_IMPLEMENTATION_NOT_BOARD',tool='Vivado2026.1.1 SW6605303',part='xc7z020clg400-2',top='base_wrapper',build=str(B),
 network=dict(nodes=45669,edges=1513231,input_words=721,numeric='unchanged strict FP32',clock_target_hz=100000000,ring_ABI='0x00110005',neural_state_not_reset_on_wrap=True),resources=resources,baseline_resources=base['resources'],resource_delta={k:resources[k]-base['resources'][k] for k in resources},
 timing=dict(WNS_ns=v[0],WHS_ns=v[4],WPWS_ns=v[8],setup_failing=int(v[2]),hold_failing=int(v[6]),pulse_failing=int(v[10]),setup_endpoints=int(v[3]),hold_endpoints=int(v[7]),unconstrained_internal_endpoints=0,neural_setup_ns=slack('neural_setup.rpt'),neural_hold_ns=slack('neural_hold.rpt'),release_ACK_setup_ns=slack('release_ack_setup.rpt'),release_ACK_hold_ns=slack('release_ack_hold.rpt')),
 drc_summary=[m.groups() for m in re.finditer(r'^\| ([A-Z]+-\d+)\s*\|\s*(\w+)\s*\|[^|]*\|\s*(\d+)\s*\|',d,re.M)],cdc_summary=[m.groups() for m in re.finditer(r'^(CDC-\d+)\s+(Info|Warning|Critical)\s+(\d+)',c,re.M)],bus_skew_met=b.count('(MET)'),
 interfaces=dict(camera='official HP0 64bit',neural_records='HP1 64bit',register_base='0x43c40000',PL_clock_period_ns=10,clock_physical_measurement=False),preservation=baseline_checks,
 earlier_numerical_evidence=str(R/'ddr_ring_20261026/RESULT.json'),numerical_RTL_rerun_this_turn=False,
 limits=['Routed timing passes specified constraints, not physical camera timing signoff','Camera72MHz external timing budget is conditional; official non-CCIO CLOCK_DEDICATED_ROUTE FALSE retained','Existing IIC/LCD missing external delays remain; see check_timing.rpt','DRC/CDC warnings retained and must be distinguished from zero-error timing acceptance','No new bitstream, board actions, cache/ARM ring acceptance, lossless sustained run or speed measurement'],
 routed_dcp_sha256=sha(rel/'combined_routed.dcp'),hwh_sha256=sha(rel/'base.hwh'),board_operations=0,GPU_operations=0,bit_generated=False,next='Generate separate ABI-matched BIT/HWH and CPU-verified operator Notebook only after implementation review; operator controls board')
(P/'RESULT.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
(P/'FINAL_MANIFEST_SHA256.json').write_text(json.dumps({str(f.relative_to(P)):sha(f) for f in P.rglob('*') if f.is_file() and f.name!='FINAL_MANIFEST_SHA256.json'},indent=2))
print(json.dumps(result,indent=2))
