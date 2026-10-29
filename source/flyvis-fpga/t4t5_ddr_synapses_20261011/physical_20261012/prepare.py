"""Light CPU/static preparation only. No graph, oracle, simulation or EDA run."""
from pathlib import Path
import json,hashlib,re,csv,xml.etree.ElementTree as ET
P=Path(__file__).resolve().parent;B=P.parent;ROOT=B.parents[1];A=B/'pipeline_a_20261012'
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def main():
    accepted=load(A/'ACCEPTED.json');ooc=load(A/'OOC_RESULT.json');run=A/ooc['run']
    assert accepted['status']=='PASS_PIPELINE_A_RTL_ACCEPTANCE' and ooc['resource_fit']
    assert sha(A/'ACCEPTED.json')==ooc['accepted_rtl_sha256']
    for n,d in accepted['rtl_sha256'].items():assert sha(A/'rtl'/n)==sha(run/n)==d,n
    dcp=run/'b_fullscale_synthesis.dcp';assert sha(dcp)==ooc['dcp_sha256']
    hwh=ROOT/'flyvis-fpga/phase4_67_20261010/build/v1_bankfix_20261011_153525/flyvis_t5c_source_raw_v1.hwh'
    timing=hwh.parent/'implementation_timing_summary.rpt'
    tree=ET.parse(hwh).getroot();ps=next(x for x in tree.iter('MODULE') if x.attrib.get('INSTANCE')=='ps7')
    names={'PCW_FPGA0_PERIPHERAL_FREQMHZ','PCW_S_AXI_HP0_DATA_WIDTH','PCW_USE_S_AXI_HP0','PCW_UIPARAM_DDR_BUS_WIDTH','PCW_UIPARAM_DDR_FREQ_MHZ','PCW_UIPARAM_DDR_PARTNO'}
    params={x.attrib['NAME']:x.attrib['VALUE'] for x in ps.iter('PARAMETER') if x.attrib.get('NAME') in names}
    assert params['PCW_FPGA0_PERIPHERAL_FREQMHZ']=='100' and params['PCW_S_AXI_HP0_DATA_WIDTH']=='64'
    sites=set(re.findall(r'(BUFGCTRL_X\d+Y\d+)\s+BUFG[^\n]*buffer_fclk_clk_0',timing.read_text(encoding='utf-8')))
    assert sites=={'BUFGCTRL_X0Y16'},sites
    context=(P/'context.xdc').read_text(encoding='utf-8');tcl=(P/'implement.tcl').read_text(encoding='utf-8')
    active='\n'.join(l for l in (context+'\n'+tcl).splitlines() if not l.lstrip().startswith('#'))
    banned=['set_false_path','set_multicycle_path','set_clock_groups','set_clock_latency','set_input_delay','set_output_delay','create_clock','synth_design','write_bitstream']
    assert not any(re.search(r'\b'+x+r'\b',active) for x in banned)
    assert tcl.count('\nroute_design\n')==1 and tcl.count('\nplace_design\n')==1
    clock=(run/'clock.xdc').read_text(encoding='utf-8');assert '-period 10.000' in clock
    for key in ('set_input_delay','set_output_delay'):
        assert re.search(key+r'[^\n]*-max 2.000',clock) and re.search(key+r'[^\n]*-min 0.000',clock)
    identity=dict(accepted_path=str(A.relative_to(ROOT)),accepted_sha256=sha(A/'ACCEPTED.json'),ooc_result_sha256=sha(A/'OOC_RESULT.json'),
        pipeline_manifest_sha256=sha(A/'MANIFEST_SHA256.json'),dcp_path=str(dcp.relative_to(ROOT)),dcp_sha256=sha(dcp),
        rtl_sha256=accepted['rtl_sha256'],clock_xdc_sha256=sha(run/'clock.xdc'),
        reference_only_clock_source=dict(hwh=str(hwh.relative_to(ROOT)),hwh_sha256=sha(hwh),routed_report=str(timing.relative_to(ROOT)),routed_report_sha256=sha(timing),
            params=params,bufg_site='BUFGCTRL_X0Y16',scope='Read-only 67-node local build reference; not B integration or board observation'),
        physical_target=dict(part='xc7z020clg400-2',tool='Vivado2026.1.1 SW6605303',clock_ns=10,HD_CLK_SRC='BUFGCTRL_X0Y16',input_max_ns=2,input_min_ns=0,output_max_ns=2,output_min_ns=0),
        constraints_policy='Retain accepted clock and all IO constraints; add only explicit reference BUFG context; no timing exceptions or relaxed delays')
    save(P/'INPUT_IDENTITY.json',identity)
    E,H,S=433880,5768,16402;edge_bytes=8*E;input_bytes=4*(S+H);output_bytes=4*H;state_bytes=input_bytes+output_bytes
    frequency=100e6;nonedge=451207-E;load_cycles=S+H+H
    samples=[]
    for mbps in (400,500,600,650,694.208,700,750,800,900,1000,1200):
        cap=min(mbps*1e6,8*frequency)
        samples.append(dict(assumed_HP0_MBps=mbps,edge_supply_floor_ms=edge_bytes/(mbps*1e6)*1000,
            compute_or_supply_lower_bound_ms=max(451207/frequency,edge_bytes/(mbps*1e6))*1000,
            no_prefill_service_model_core_ms=(edge_bytes/cap+nonedge/frequency)*1000,
            no_prefill_plus_existing_state_port_cycles_ms=(edge_bytes/cap+(nonedge+load_cycles)/frequency)*1000))
    budget=dict(evidence_level='CPU_ARITHMETIC_AND_DOCUMENT_REVIEW_NOT_BANDWIDTH_MEASUREMENT',
        edges=E,edge_bytes=edge_bytes,state_input_bytes=input_bytes,candidate_output_bytes=output_bytes,roundtrip_state_bytes=state_bytes,
        edge_bandwidth_at_200steps_MBps=edge_bytes*200/1e6,roundtrip_state_at_200steps_MBps=state_bytes*200/1e6,
        edge_plus_state_at_200steps_MBps=(edge_bytes+state_bytes)*200/1e6,
        bus_raw_MBps={'64bit_100MHz':800,'64bit_150MHz':1200},
        ideal_core_cycles=451207,nonedge_cycles=nonedge,state_port_cycles_min=load_cycles,
        ideal_core_ms_at_100MHz=4.51207,core_plus_one_word_per_cycle_state_ports_ms=4.51207+load_cycles/frequency*1000,
        peak_core_average_edge_MBps=edge_bytes/(451207/frequency)/1e6,
        required_sustained_during_edges_MBps_for_5ms_no_prefill=edge_bytes/(.005-nonedge/frequency)/1e6,
        required_sustained_MBps_for_5ms_with_state_port_cycles=edge_bytes/(.005-(nonedge+load_cycles)/frequency)/1e6,
        FIFO128_plus_output_max_mask_us=129/frequency*1e6,four_16beat_bursts_bytes=512,
        latency_window_us_for_4bursts_at_800MBps=512/800e6*1e6,AXI_timeout_64_at_100MHz_us=.64,
        configured_reference_DDR_peak_MBps=32/8*2*float(params['PCW_UIPARAM_DDR_FREQ_MHZ']),
        ideal_1GbE_state_roundtrip_ms=state_bytes*8/1e9*1000,
        unoverlapped_ideal_core_plus_1GbE_payload_ms=4.51207+state_bytes*8/1e9*1000,
        actual_B_HP0_clock_MHz=None,actual_DDR_frequency_MHz=None,measured_HP0_MBps=None,measured_step_ms=None,
        samples=samples,limits=['Existing state ports are pins, not implemented DMA/AXI load paths','Supply models omit prefill/latency distributions and are not an RTL replay',
            'No current board DDR/FCLK configuration observed','Edge table remains resident in PS DDR; do not send 3.47MB from PC per step','1GbE value is serialization only; no protocol or Linux cost'],
        sources=[dict(title='AMD UG585 PS-PL interfaces',url='https://docs.amd.com/r/en-US/ug585-zynq-7000-SoC-TRM/PS-PL-Interfaces'),
            dict(title='AMD UG585 PL clocks',url='https://docs.amd.com/r/en-US/ug585-zynq-7000-SoC-TRM/PL-Clocks'),
            dict(title='AMD UG946 OOC clock context',url='https://docs.amd.com/api/khub/documents/jEbBRZSUd9Rf0GNfAMS6dw/content'),
            dict(title='AMD UG1145 DDR contention',url='https://docs.amd.com/r/2024.2-English/ug1145-sdk-system-performance/Evaluating-High-Performance-Ports'),
            dict(title='AMD XAPP792 150MHz registered HP interface example',url='https://docs.amd.com/api/khub/documents/ASiLExM7IeFBcSm9PQJ9bw/content')])
    save(P/'DDR_HP0_BUDGET.json',budget)
    with (P/'DDR_HP0_SCENARIOS.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(samples[0]));w.writeheader();w.writerows(samples)
    static=dict(status='READY_EXPLICIT_CONCURRENT_VIVADO_AUTHORIZED',no_new_RTL_or_fullgraph_runs=True,
        checks=dict(accepted_input_identity=True,same_10ns_clock=True,same_IO_max2_min0=True,only_HD_CLK_SRC_added=True,no_timing_exceptions=True,
            single_place_and_route=True,existing_DCP_reused=True,reference_BUFG_proven_in_local_routed_report=True),
        input_identity_sha256=sha(P/'INPUT_IDENTITY.json'),prepared_files_sha256={n:sha(P/n) for n in ('context.xdc','implement.tcl','launch.ps1')},
        helper_sha256={n:sha(P/n) for n in ('run.py','gate_policy.py','policy_checks.py','audit_physical.py','prepare.py')},
        concurrency_authorization_sha256=sha(P/'CONCURRENCY_AUTHORIZATION.json'),
        pending=['Bounded resource and actual process-tree gate; optional explicit concurrent override','Vendor Tcl execution and actual placed/routed timing'],
        board_GPU_GUI_operations=0,previous_875_hold_endpoints='Cause classification pending context report and physical route; synthesis top10 are input-to-BRAM only')
    save(P/'STATIC_REVIEW.json',static)
    print(json.dumps(dict(status=static['status'],budget={k:budget[k] for k in ('edge_bandwidth_at_200steps_MBps','peak_core_average_edge_MBps','required_sustained_MBps_for_5ms_with_state_port_cycles','unoverlapped_ideal_core_plus_1GbE_payload_ms')},input_dcp_sha256=identity['dcp_sha256']),indent=2))
if __name__=='__main__':main()
