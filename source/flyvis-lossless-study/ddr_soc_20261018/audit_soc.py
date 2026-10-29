"""Read-only source/report audit; writes results only in this new candidate."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

P=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def text(p):return p.read_text(encoding='utf-8',errors='replace')
def load(p):return json.loads(text(p))
def save(p,value):p.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
def row(t,label):
    for line in t.splitlines():
        f=[x.strip() for x in line.split('|')[1:-1]]
        if f and f[0].rstrip('*')==label:return f
    raise AssertionError(label)
def timing(p):
    m=re.search(r'^\s*(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(\d+)\s+(\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(\d+)\s+(\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(\d+)\s+(\d+)\s*$',text(p),re.M)
    assert m,'Missing timing summary'
    keys=['wns_ns','tns_ns','setup_failing','setup_total','whs_ns','ths_ns','hold_failing','hold_total','wpws_ns','tpws_ns','pulse_failing','pulse_total']
    return {k:float(v) if i%4<2 else int(v) for i,(k,v) in enumerate(zip(keys,m.groups()))}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--tag',required=True);a=ap.parse_args()
    run=P/a.tag;release=run/'release'
    baselines={}
    for name,original in load(P/'BASELINE_BEFORE.json').items():
        root=P.parent/name;manifest=root/'FINAL_MANIFEST_SHA256.json'
        assert sha(manifest)==original['manifest_sha256']
        records=load(manifest);assert len(records)==original['files']
        for name,item in records.items():
            f=root/name;assert f.stat().st_size==item['bytes'] and sha(f)==item['sha256'],str(f)
        baselines[root.name]=dict(files=len(records),manifest_sha256=sha(manifest),unchanged=True)
    save(P/'BASELINE_AFTER.json',baselines)
    identities=load(P/'control_r1/IDENTITY.json')
    for path,h in identities.items():assert sha(Path(path))==h,path
    for name,h in load(run/'INPUT_SNAPSHOT.json').items():assert sha(run/name)==h,name
    for name in ('fp32_rne.sv','banked_state_mem.sv','sync_mem.sv','compact_edge_gen.sv','flyvis_lane.sv'):
        assert sha(run/name)==sha(P/'rtl'/name)==sha(P.parent/'hole_pipeline_20261016'/name),name
    for name in ('snapshot_axi_writer.sv','flyvis_ddr_snapshot_top.sv'):
        assert sha(run/name)==sha(P/'rtl'/name)==sha(P.parent/'ddr_snapshot_20261018/rtl'/name),name
    assert sha(P/'rtl/host_reference.cpp')==sha(P.parent/'ddr_snapshot_20261018/rtl/host_reference.cpp')
    assert sha(P/'rtl/host_reference.cpp')==sha(P.parent/'hole_pipeline_20261016/host_reference.cpp')
    assert sha(run/'flyvis_ddr_soc_ip.sv')==identities[str(P/'rtl/flyvis_ddr_soc_ip.sv')]
    cpu=load(P/'control_r1/summary.json');assert cpu['completed_steps']==3 and cpu['state_mismatches']==0
    contract=load(P/'CPU_CONTROL_RESULT.json');assert contract['status']=='PASS_CPU_PS_CONTRACT_ONLY'
    for name,h in contract['inputs'].items():assert sha(P/name)==h,name
    for stage in ('synth','route'):
        result=load(run/('RESULT_'+stage+'.json'))
        assert result['returncode']==0 and result['status']=='PASS_'+stage.upper()+'_COMMANDS',stage
        for name,item in result['reports'].items():assert sha(release/name)==item['sha256'],name
    assert not list(run.rglob('*.bit')),'No bitstream requested'
    util=text(release/'utilization_routed.rpt')
    labels=dict(lut='Slice LUTs',ff='Slice Registers',dsp='DSPs',bram36_equivalent='Block RAM Tile',latches='Register as Latch',lutram='LUT as Memory')
    resources={k:float(row(util,v)[1]) for k,v in labels.items()}
    limits=dict(lut=53200,ff=106400,dsp=220,bram36_equivalent=140)
    assert all(resources[k]<=limit for k,limit in limits.items()) and resources['latches']==0
    t=timing(release/'timing_routed.rpt')
    assert all(t[k]>=0 for k in ('wns_ns','whs_ns','wpws_ns'))
    assert all(t[k]==0 for k in ('setup_failing','hold_failing','pulse_failing'))
    assert re.search(r'clk_fpga_0\s+\{0.000 5.000\}\s+10.000\s+100.000',text(release/'timing_routed.rpt'))
    checks=dict(re.findall(r'\d+\. checking (\w+) \((\d+)\)',text(release/'check_timing.rpt')))
    assert len(checks)==12 and all(v=='0' for v in checks.values()),checks
    route={label:int(re.search(r'# of '+re.escape(label)+r'\.+\s*:\s*(\d+)',text(release/'route_status.rpt'))[1]) for label in ('routable nets','fully routed nets','nets with routing errors')}
    assert route['routable nets']==route['fully routed nets'] and route['nets with routing errors']==0
    assert not re.search(r'\|\s*[^|]+\|\s*(Error|Critical Warning)\s*\|',text(release/'drc.rpt'))
    drc_warnings={rule:int(count) for rule,count in re.findall(r'^\|\s*([A-Z0-9-]+)\s*\|\s*Warning\s*\|[^|]*\|\s*(\d+)\s*\|',text(release/'drc.rpt'),re.M)}
    tree=ET.parse(release/'flyvis_ddr.hwh');modules={x.get('INSTANCE'):x for x in tree.findall('.//MODULE')}
    def params(n):return {x.get('NAME'):x.get('VALUE') for x in modules[n].findall('./PARAMETERS/PARAMETER')}
    ps=params('ps7');rst=params('reset')
    assert float(ps['PCW_ACT_FPGA0_PERIPHERAL_FREQMHZ'])==100 and ps['PCW_USE_M_AXI_GP0']=='1'
    assert ps['PCW_USE_S_AXI_HP0']=='1' and ps['PCW_S_AXI_HP0_DATA_WIDTH']=='64'
    assert ps['PCW_CRYSTAL_PERIPHERAL_FREQMHZ']=='33.333333' and rst['C_EXT_RESET_HIGH']=='0'
    ports={x.get('NAME'):x.attrib for x in modules['network'].findall('./PORTS/PORT')}
    assert ports['aclk']['CLKFREQUENCY']=='100000000' and ports['aresetn']['SIGNAME']=='reset_peripheral_aresetn'
    ranges=[x.attrib for x in tree.findall('.//MEMRANGE')]
    reg=[x for x in ranges if x.get('INSTANCE')=='network'];assert len(reg)==1
    assert int(reg[0]['BASEVALUE'],16)==0x43c40000 and int(reg[0]['HIGHVALUE'],16)==0x43c40fff
    hp=[x for x in ranges if x.get('SLAVEBUSINTERFACE')=='S_AXI_HP0'];assert len(hp)==1
    assert int(hp[0]['BASEVALUE'],16)==0 and int(hp[0]['HIGHVALUE'],16)==0x3fffffff
    generated=text(run/'bd/flyvis_ddr/synth/flyvis_ddr.v')
    for channel in ('AWID','WID'):
        assert '.S_AXI_HP0_'+channel+"({1'b0,1'b0,memory_bus_M00_AXI_"+channel+'})' in generated
    assert 'assign m_axi_awid=0;' in text(run/'flyvis_ddr_soc_ip.sv')
    reused=load(run/'REUSED_SYNTH.json') if (run/'REUSED_SYNTH.json').exists() else None
    synth_origin=Path(reused['source']) if reused else run
    if reused:
        assert sha(synth_origin/'RESULT_synth.json')==reused['source_result_sha256']
        assert sha(release/'ddr_soc_synth.dcp')==sha(synth_origin/'release/ddr_soc_synth.dcp')==reused['checkpoint_sha256']
        assert sha(run/'bd/flyvis_ddr/synth/flyvis_ddr.v')==sha(synth_origin/'bd/flyvis_ddr/synth/flyvis_ddr.v')
    logs={'synth':synth_origin/'synth_console.log','route':run/'route_console.log'}
    critical={stage:re.findall(r'^CRITICAL WARNING:.*$',text(path),re.M) for stage,path in logs.items()}
    errors={stage:re.findall(r'^ERROR:.*$',text(path),re.M) for stage,path in logs.items()}
    assert not any(errors.values()),errors
    assert all('[BD 41-737]' in line and 'C_EXT_RESET_HIGH' in line for lines in critical.values() for line in lines),critical
    baseline=load(P.parent/'hole_pipeline_20261016/AUDIT_soc_r2.json')['resources']
    core_cycles=[int.from_bytes((P/'control_r1/ddr_records.bin').read_bytes()[i*188416+32:i*188416+36],'little') for i in range(3)]
    assert all(c==2199975 for c in core_cycles),core_cycles
    result=dict(status='PASS_FULL_DDR_SOC_100MHZ_LOCAL_IMPLEMENTATION_ONLY',candidate=a.tag,
        design='flyvis_ddr_wrapper',device='xc7z020clg400-2',tool_version=text(run/'tool_version.txt').strip(),
        nodes=45669,edges=1513231,arithmetic='Unchanged strict binary32 RNE add13/mul8; no FMA or FTZ',
        clock_MHz=100,resources=resources,resource_limits=limits,timing=t,check_timing=checks,route=route,
        resource_delta_from_accepted_MMIO={k:resources[k]-baseline[k] for k in limits},
        DRC=dict(errors=0,critical_warnings=0,ordinary_warnings=drc_warnings,total_ordinary_warnings=sum(drc_warnings.values()),
            review='5 existing DSP pipeline advisories; 2 vendor AXI conversion FIFO unused-LUT-input checks; 1 no-routable-load warning for22 vendor FIFO nets. None waived or downgraded. Gate-level/native PS7/board validation not run.'),
        worst_setup_path='PS reset peripheral_aresetn to current_ram BRAM WEA; fanout4791; 95.925% of9.300ns data path is routing',
        cycle_counter=dict(record_values=core_cycles,core_phase_ms_at_nominal100MHz=core_cycles[0]/1e5,
            excludes=['721-word internal input feed','final DDR/header response and publication','ARM input MMIO','cache/readback/validation/transport/rendering'],
            is_measured_physical_step_time=False,unchanged_reference_MMIO_core_cycles=2201418),
        control_base='0x43c40000',control_ABI='0x00110004',DDR_interface='HP0 AXI3/64bit through generated AXI4-to-AXI3 converter',
        ID_width_review='Only ID0 is issued. Generated AWID/WID explicitly zero-pad 4 to6 bits; returned BID is narrowed to4. No valid issued ID aliases; native PS7 fault injection not run.',
        cpu_rtl=cpu,cpu_contract=contract,baseline_seals=baselines,configuration_critical_warnings=critical,
        synthesized_in=str(synth_origin),checkpoint_reuse=reused,
        evidence_limits=['Behavioral RTL uses CPU DDR responder, not PS7 native VIP or routed-netlist numerical equivalence',
            'No physical-board execution, DDR allocation/cache-visibility validation or end-to-end frame-rate measurement',
            'Finite append-only journal stops before capacity exhaustion can drop a neural step; no automatic wrap',
            'Display reads/copies/rendering are outside the producer; physical DDR backpressure can still stall state output'],
        board_operations=0,GPU_operations=0,bitstream='NOT_REQUESTED_NOT_GENERATED')
    save(P/'AUDIT.json',result)
    print(json.dumps({k:v for k,v in result.items() if k in ('status','candidate','resources','timing','route')},indent=2))

if __name__=='__main__':main()
