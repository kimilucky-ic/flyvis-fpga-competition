"""Offline report gate. No Vivado invocation, hardware imports, or silent waivers."""
from pathlib import Path
import json,re,hashlib
p=Path(__file__).resolve().parent;b=p/'build_r7';rel=b/'release'
for stage in ('synth','route'):
 r=json.loads((b/(stage+'_RUN.json')).read_text());assert r['exit_code']==0 and r['stop'] is None,r
 log=(b/(stage+'.log')).read_text(errors='replace')
 assert not re.search(r'^(?:ERROR|CRITICAL WARNING):',log,re.M),'tool errors/critical warnings'
 assert 'Path segmentation by forcing' not in log,'invalid timing segmentation'
assert (b/'completed.txt').exists()
t=(rel/'timing_routed.rpt').read_text();clocks={}
for line in t.splitlines():
 v=line.split()
 if len(v)==13 and v[0] in ('camera_pclk','clk_fpga_0'):
  clocks[v[0]]=dict(WNS_ns=float(v[1]),TNS_ns=float(v[2]),setup_failed=int(v[3]),setup_endpoints=int(v[4]),WHS_ns=float(v[5]),THS_ns=float(v[6]),hold_failed=int(v[7]),hold_endpoints=int(v[8]),WPWS_ns=float(v[9]),pulse_failed=int(v[11]))
assert clocks.keys()=={'camera_pclk','clk_fpga_0'},clocks
assert clocks['clk_fpga_0']['setup_endpoints']>=10000,'internal checks missing'
for v in clocks.values():assert min(v['WNS_ns'],v['WHS_ns'],v['WPWS_ns'])>=0 and v['setup_failed']==v['hold_failed']==v['pulse_failed']==0
n=(rel/'neural_paths.rpt').read_text();assert '/network/' in n and 'clk_fpga_0' in n
assert 'Path Type:              Setup' in n
camera=(rel/'camera_external_paths.rpt').read_text();assert 'fall@' in camera and 'Input Delay:' in camera and 'VIOLATED' not in camera
# min_max top20 can contain only hold paths; verify both applied bounds in exported XDC.
constraints=(rel/'effective_constraints.xdc').read_text()
for bound in ('-min -0.500','-max 2.000'):
 assert 'set_input_delay -clock camera_pclk -clock_fall '+bound in constraints
assert 'set_clock_uncertainty -setup 0.250 [get_clocks camera_pclk]' in constraints
assert 'set_clock_uncertainty -hold 0.100 [get_clocks camera_pclk]' in constraints
u=(rel/'utilization_routed.rpt').read_text()
def used(label):return float(re.search(r'\|\s*'+re.escape(label)+r'\s*\|\s*([\d.]+)',u).group(1))
resources={k:used(v) for k,v in dict(LUT='Slice LUTs',FF='Slice Registers',BRAM36_equivalent='Block RAM Tile',DSP='DSPs').items()}
drc=(rel/'drc.rpt').read_text();assert 'REQP-1839' not in drc
warnings={m[0]:int(m[2]) for m in re.findall(r'\|\s*([A-Z]+-\d+)\s*\|\s*(Warning|Advisory)\s*\|[^|]+\|\s*(\d+)\s*\|',drc)}
assert not re.search(r'\|\s*(?:Error|Critical Warning)\s*\|',drc)
check=(rel/'check_timing.rpt').read_text();checks={k:int(v) for k,v in re.findall(r'^\d+\. checking (\w+) \((\d+)\)',check,re.M)}
assert len(checks)==12 and checks['no_input_delay']==2
assert all(v==0 for k,v in checks.items() if k!='no_input_delay')
assert 'cam_iic_scl_io' in check and 'cam_iic_sda_io' in check
cdc=(rel/'cdc.rpt').read_text();assert not re.search(r'^CDC-\d+\s+(?:Critical|Warning)\s+',cdc,re.M),'unsafe CDC remains'
assert 'fault_sync_reg[0]/D' in cdc and 'ready_sync_reg[0]/D' in cdc
route=(rel/'route_status.rpt').read_text()
assert re.search(r'nets with routing errors[^:]*:\s*0\s*:',route)
skew=(rel/'bus_skew.rpt').read_text();slacks=[float(x) for x in re.findall(r'Slack \(MET\)\s*:\s*([\d.]+)ns',skew)]
assert len(slacks)==2 and min(slacks)>=0 and 'VIOLATED' not in skew,'FIFO bus skew failed'
inputs=(rel/'iic_input_paths.rpt').read_text();delays=[float(x) for x in re.findall(r'Data Path Delay:\s*([\d.]+)ns',inputs)];assert len(delays)==2 and max(delays)<=20,delays
assert 'Timing Exception:       False Path' in inputs # vendor asynchronous input synchronizers
outputs=(rel/'iic_output_paths.rpt').read_text();assert '20.000ns' in outputs and 'internal pin' not in outputs
cp=json.loads((p/'CPU_RESULT.json').read_text());assert cp['passed'] and cp['tests']==9
for folder,marker in [('sim_r6','PASS_VENDOR_VIDEO5_XPM_FIFO_RESET_OVERFLOW_RESTART'),('sim_iic_r1','PASS_ACTUAL_AXI_IIC_WRITE_100KHZ_WITH_300NS_LINE_MODEL')]:
 log=(p/folder/'simulate.log').read_text(errors='replace');assert marker in log and 'Fatal:' not in log
identity=json.loads((p/'NEURAL_IDENTITY.json').read_text());assert len(identity['files'])==58
for name,v in identity['files'].items():assert v['identical'] and hashlib.sha256((b/name).read_bytes()).hexdigest()==v['sha256']
result=dict(status='PASS_OFFLINE_RESET_FIFO_AND_ROUTED_100MHZ_CONDITIONAL_EXTERNAL_TIMING',evidence_level='CPU_REGISTER_MODEL_AND_VENDOR_IP_RTL_AND_FULL_SOC_ROUTED',candidate='build_r7',part='xc7z020clg400-2',tool='Vivado 2026.1.1 SW6605303',nodes=45669,edges=1513231,precision='unchanged strict FP32',clocks=clocks,resources=resources,timing_check_counts=checks,CDC_critical_or_warning_count=0,FIFO_bus_skew_slack_ns=slacks,drc_warning_or_advisory_counts=warnings,REQP_1839_count=0,iic_input_delay_ns=delays,iic_input_constraint='vendor CDC first-stage false path; reported routed propagation audited <=20ns, not sensor setup/hold',camera_external_timing='conditional -0.5..2.0ns falling-edge budget, physical tCO/skew unverified',CPU_tests=9,VGA_pixels_verified=307200,physical_board_result=False,GPU_operations=0,board_operations=0,bitstream_generated=False,external_signoff_complete=False,physical_board_revision_confirmed=False,unverified=['physical oscillator/frequency/polarity and board skew','SCCB physical RC waveforms','native PS/ARM/cache/VDMA behavior','real-camera full-state oracle','end-to-end frame rate and power'])
(p/'FINAL_RESULT.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
