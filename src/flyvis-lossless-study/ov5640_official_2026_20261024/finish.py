"""Collect only this isolated build; fail closed before writing final success."""
from pathlib import Path
import hashlib,json,re,shutil
w=Path(__file__).resolve().parent
r=Path('C:/fpga_work/line11_off26_r2_20261024')
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert (r/'ROUTE_COMPLETED_REVIEW_REQUIRED.txt').is_file()
t=(r/'release_routed/timing_routed.rpt').read_text()
u=(r/'release_routed/utilization_routed.rpt').read_text()
d=(r/'release_routed/drc.rpt').read_text()
c=(r/'release_routed/cdc.rpt').read_text()
b=(r/'release_routed/bus_skew.rpt').read_text()
line=re.search(r'WNS\(ns\).*\n[^\n]*\n([^\n]+)',t).group(1).split()
assert len(line)==12,line
v=list(map(float,line));assert min(v[0],v[4],v[8])>=0 and v[2]==v[6]==v[10]==0
assert 'checking no_clock (0)' in t and 'checking unconstrained_internal_endpoints (0)' in t
assert 'REQP-1839' not in d and '| Error' not in d and '| Critical' not in d
assert not re.search(r'^CDC-\d+\s+Critical',c,re.M)
assert 'VIOLATED' not in b
route=(r/'release_routed/route_status.rpt').read_text()
for key in ['nets with routing errors','unrouted nets','partially routed nets']:
 match=re.search(re.escape(key)+r'\.*\s*:\s*(\d+)',route,re.I)
 if match:assert int(match.group(1))==0,(key,match.group(1))
assert 'Number of Failed Nets               = 0' in (r/'route_resume.log').read_text()
resources={}
for label,name in [('Slice LUTs','LUT'),('Slice Registers','FF'),('Block RAM Tile','BRAM36_equivalent'),('DSPs','DSP')]:
 resources[name]=int(re.search(r'^\| '+label+r'\s*\|\s*(\d+)',u,re.M).group(1))
base=json.loads((w/'BASELINE.json').read_text(encoding='utf-8-sig'))
# Baseline keys are relative to repo cwd, as recorded before this work.
assert all(Path(s).is_file() and h(Path(s))==sha for s,sha in base.items())
assert all(h(p)==h(r/'neural'/p.name) for p in (w/'neural').iterdir() if p.is_file())
assert len(list((w/'neural').iterdir()))==58
sim=(r/'sim/simulate.log').read_text()
assert 'PASS_RESET_R2_STREAM_386560_PIXELS_NOT_VDMA_OR_BOARD' in sim and 'Fatal:' not in sim
rel=w/'release_r2';rel.mkdir(exist_ok=True)
ev=w/'evidence/r2';ev.mkdir(exist_ok=True)
for p in list((r/'release').iterdir())+list((r/'release_routed').iterdir()):
 if p.suffix in ['.rpt','.xdc','.dcp']:shutil.copy2(p,rel/p.name)
for name in ['synth.log','route.log','migrate3.jou','combine.jou','synth.jou','route.jou','route_resume.log','route_resume.jou','route_resume.tcl']:
 shutil.copy2(r/name,ev/name)
shutil.copy2(r/'imported3/base/hw_handoff/base.hwh',rel/'base.hwh')
shutil.copy2(r/'imported3/base/base.bd',rel/'base.bd')
shutil.copy2(r/'vendor/base.xdc',rel/'pin_constraints_r2.xdc')
known={}
for ext,sha in [('bit','ad40c916fe728fbc1272185cf454318dbac8622fc451c62923b4975ec9437031'),('hwh','dcc2df7d5ee8950b081fd77fa392fa1390c73baac0e8b8a3ca791937e6fdbd3a')]:
 q=w.parent/'ov5640_official_20261024'/('ov5640_lcd_7020.'+ext);assert h(q)==sha;known[str(q)]=sha
result=dict(status='PASS_OFFLINE_MIGRATION_RTL_AND_ROUTE_ONLY_EXTERNAL_TIMING_OPEN',
 tool='Vivado 2026.1.1 SW6605303 IP6603865',part='xc7z020clg400-2',design='base_wrapper',stage='Fully Routed',
 network=dict(nodes=45669,edges=1513231,numeric='strict FP32 unchanged RTL',neural_clock_hz=100000000,neural_source_files_unchanged=58,whole_network_numerical_rerun=False),
 resources=resources,timing=dict(WNS_ns=v[0],WHS_ns=v[4],WPWS_ns=v[8],setup_failing=int(v[2]),hold_failing=int(v[6]),pulse_failing=int(v[10]),setup_endpoints=int(v[3]),hold_endpoints=int(v[7]),unconstrained_internal_endpoints=0),
 DRC_summary=[m.groups() for m in re.finditer(r'^\| ([A-Z]+-\d+)\s*\|\s*(\w+)\s*\|[^|]*\|\s*(\d+)\s*\|',d,re.M)],
 CDC_summary=[m.groups() for m in re.finditer(r'^(CDC-\d+)\s+(Info|Warning|Critical)\s+(\d+)',c,re.M)],
 neural_timing=dict(setup_ns=float(re.search(r'Slack \(MET\) :\s+([0-9.]+)ns',(r/'release_routed/neural_setup.rpt').read_text()).group(1)),hold_ns=float(re.search(r'Slack \(MET\) :\s+([0-9.]+)ns',(r/'release_routed/neural_hold.rpt').read_text()).group(1))),
 bus_skew_constraints_met=b.count('(MET)'),
 REQP_1839_after=0,REQP_1839_before=3,simulation_pixels=386560,
 known_good_official_files=known,original_candidate_files_unchanged=len(base),board_operations=0,gpu_operations=0,bitstream_generated=False,
 current_build=str(r),routed_dcp_sha256=h(rel/'combined_routed.dcp'),hwh_sha256=h(rel/'base.hwh'),
 official_path_preserved='Official OV5640 driver/VDMA/video hierarchy retained; IIC2.1 binding only; video-in5.0; minimal capture reset patch',
 major_architecture_change=False,
 limits=['33 DRC Warning plus2 Advisory and5 CDC Warning remain; no Error/Critical, not zero-warning signoff','Camera72MHz falling-edge -0.5..2ns external budget is conditional, not measured','Official non-CCIO camera PCLK dedicated-route exception retained','IIC and unused LCD external delays incomplete: 5 input and29 output ports','Native ARM libiic/video2lcd, cache/VDMA/HP1 and combined full-state board run unverified','No BIT generated; HWH is implementation metadata, not a runnable release'],
 interrupted_route_preserved='evidence/r2/route.log',final_route_log='evidence/r2/route_resume.log',
 next_action='Prepare a separate BIT/HWH offline package and operator-only combined acceptance after final report review')
(w/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
manifest={str(p.relative_to(w)):h(p) for p in w.rglob('*') if p.is_file() and 'build_r1' not in p.parts and p.name!='FINAL_MANIFEST_SHA256.json'}
(w/'FINAL_MANIFEST_SHA256.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(result,indent=2))
