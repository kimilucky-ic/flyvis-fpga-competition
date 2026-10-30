"""Read complete-SoC reports; never substitute the accepted core OOC numbers."""
from pathlib import Path
import re,json,hashlib
P=Path(__file__).resolve().parent
B=P/json.loads((P/'LATEST_BUILD.json').read_text())['build']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def text(name):return (B/name).read_text(errors='replace')
def util_value(label,body):
    m=re.search(r'^\|\s*'+re.escape(label)+r'\s*\|\s*([0-9.]+)\s*\|',body,re.M)
    assert m,label
    v=float(m[1]);return int(v) if v.is_integer() else v
util=text('routed_utilization.rpt')
assert 'b_soc_wrapper' in util and 'xc7z020clg400-2' in util and 'Routed' in util
resources={k:util_value(v,util) for k,v in {
 'LUT':'Slice LUTs','FF':'Slice Registers','BRAM_tiles':'Block RAM Tile',
 'RAMB36':'RAMB36/FIFO*','RAMB18':'RAMB18','DSP':'DSPs','latches':'Register as Latch'}.items()}
timing=text('routed_timing.rpt')
pattern=r'^\s+([-0-9.]+)\s+([-0-9.]+)\s+(\d+)\s+(\d+)\s+([-0-9.]+)\s+([-0-9.]+)\s+(\d+)\s+(\d+)\s+([-0-9.]+)\s+([-0-9.]+)\s+(\d+)\s+(\d+)\s*$'
row=re.search(pattern,timing,re.M);assert row,'No timing summary'
keys=['WNS_ns','TNS_ns','setup_failing','setup_total','WHS_ns','THS_ns','hold_failing','hold_total','WPWS_ns','TPWS_ns','pulse_failing','pulse_total']
timings={k:(float(v) if k.endswith('_ns') else int(v)) for k,v in zip(keys,row.groups())}
checks={k:int(v) for k,v in re.findall(r'checking ([a-z_]+) \((\d+)\)',text('check_timing.rpt'))}
route=text('route_status.rpt')
route_counts={}
for key,phrase in [('routable','routable nets'),('fully_routed','fully routed nets'),('routing_errors','nets with routing errors')]:
    m=re.search(r'# of '+phrase+r'\.+\s*:\s*(\d+)',route);assert m,key;route_counts[key]=int(m[1])
drc=text('routed_drc.rpt')
drc_errors=re.findall(r'(?m)^.*\b(?:Error|Critical Warning)\b.*$',drc)
drc_rules={rule:dict(severity=severity.strip(),count=int(count)) for rule,severity,count in
           re.findall(r'^\|\s*([A-Z]+-\d+)\s*\|\s*([^|]+)\|[^|]*\|\s*(\d+)\s*\|',drc,re.M)}
clocks=text('routed_clocks.rpt')
clock_match=re.search(r'^clk_fpga_0\s+(\d+\.\d+)\s+.*FCLKCLK\[0\]',clocks,re.M)
clock_100MHz=bool(clock_match and float(clock_match[1])==10.0)
hp0={}
for kind in ('setup','hold'):
    body=text('routed_hp0_'+kind+'.rpt')
    slack=re.search(r'Slack \(MET\)\s*:\s*([-\d.]+)ns',body)
    assert slack and 'PS7_i/SAXIHP0' in body,'HP0 timing coverage missing'
    hp0[kind+'_slack_ns']=float(slack[1])
xdc=text('routed_constraints.xdc')
false_paths=re.findall(r'^set_false_path.*$',xdc,re.M)
expected_reset_scopes=[
 'b_soc_i/reset/U0/EXT_LPF/ACTIVE_HIGH_AUX.ACT_HI_AUX',
 'b_soc_i/reset/U0/EXT_LPF/ACTIVE_LOW_EXT.ACT_LO_EXT']
reset_only=(len(false_paths)==2 and all(x=='set_false_path -to [get_cells {syncstages_ff_reg[0]}]' for x in false_paths)
            and all(scope in xdc for scope in expected_reset_scopes)
            and not re.search(r'^set_(multicycle_path|input_delay|output_delay|clock_groups)\b',xdc,re.M))
methodology=text('routed_methodology.rpt')
methodology_count=int(re.search(r'Checks found:\s*(\d+)',methodology)[1])
passed=(all(timings[k]>=0 for k in ['WNS_ns','WHS_ns','WPWS_ns']) and
        all(timings[k]==0 for k in ['setup_failing','hold_failing','pulse_failing']) and
        len(checks)>=12 and not any(checks.values()) and route_counts['routing_errors']==0 and
        route_counts['routable']==route_counts['fully_routed'] and not drc_errors and
        clock_100MHz and all(v>=0 for v in hp0.values()) and reset_only and
        resources['latches']==0 and resources['BRAM_tiles']<=140)
files=['routed_utilization.rpt','routed_timing.rpt','check_timing.rpt','routed_drc.rpt',
       'route_status.rpt','routed_clocks.rpt','routed_constraints.xdc','routed_hp0_setup.rpt','routed_hp0_hold.rpt','routed_methodology.rpt']
result=dict(status='PASS_FULL_SOC_ROUTED_REPORTS' if passed else 'FAIL_OR_REVIEW_FULL_SOC_ROUTED_REPORTS',
            design='b_soc_wrapper',part='xc7z020clg400-2',tool='Vivado 2026.1.1 SW6605303',stage='full SoC routed',
            resources=resources,timing=timings,check_timing=checks,route=route_counts,
            clock_100MHz=clock_100MHz,HP0_timing=hp0,DRC_rules=drc_rules,
            native_reset_synchronizer_exceptions_only=reset_only,methodology_violations=methodology_count,
            drc_error_lines=drc_errors,report_sha256={n:sha(B/n) for n in files if (B/n).is_file()},
            bit_hwh={n:dict(sha256=sha(B/n),bytes=(B/n).stat().st_size) for n in ['flyvis_b.bit','flyvis_b.hwh'] if (B/n).is_file()},
            board_execution=False,real_HP0_bandwidth=None)
(B/'IMPLEMENTATION_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
