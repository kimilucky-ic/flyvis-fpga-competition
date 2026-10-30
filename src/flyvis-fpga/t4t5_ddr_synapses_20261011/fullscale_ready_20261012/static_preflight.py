"""Bounded static review; consume frozen preparation, never regenerate it."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import ast,hashlib,json,re
HERE=Path(__file__).resolve().parent;B=HERE.parent;PREP=B/'fullscale_20261012'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def main():
    prep=read(PREP/'PREPARATION.json');c=prep['contract']
    seal=read(PREP/'MANIFEST_SHA256.json')
    for name,v in seal['files'].items():assert sha(PREP/name)==v['sha256'],name
    for name,digest in prep['protected_parent_rtl_sha256'].items():assert sha(B/'rtl'/name)==digest,name
    assert not (PREP/'LAUNCH_RECORD.json').exists() and not (B/'FULLSCALE_LAUNCH_20261012.json').exists()
    tb=(HERE/'tb_fullscale.sv').read_text(encoding='utf-8');top=(B/'rtl/ddr_synapse_top.sv').read_text(encoding='utf-8')
    header=top.split(')(\n',1)[1].split(');',1)[0]
    declarations=re.sub(r'\b(?:input|output|wire|reg|signed|unsigned)\b|\[[^\]]+\]','',header)
    ports=[p.strip() for p in declarations.split(',')]
    connected=re.findall(r'\.(\w+)\(',tb.split('dut(',1)[1].split(');',1)[0])
    assert len(ports)==len(connected)==len(set(connected)) and set(ports)==set(connected)
    for instance,filename in [('core','ddr_synapse_core.sv'),('reader','axi_edge_reader.sv')]:
        identifiers=set(re.findall(r'\b\w+\b',(B/'rtl'/filename).read_text(encoding='utf-8')))
        for identifier in re.findall(r'dut\.'+instance+r'\.(\w+)',tb):assert identifier in identifiers,identifier
    assert sha(HERE/'tb_fullscale.sv')==seal['files']['tb_fullscale.sv']['sha256']
    assert c['source_count']==16402<2**15 and c['H']==5768<2**13
    assert c['source_count']+c['H']==22170<2**16
    lower=6*c['edge_count']+7*c['H']+2
    upper=17*c['edge_count']+16*c['burst_count']+8*c['H']+4096
    assert lower==2643658 and upper==7860104<c['step_timeout_cycles']==8000000
    syntax=[]
    for p in sorted(HERE.glob('*.py')):
        ast.parse(p.read_text(encoding='utf-8'),filename=str(p));syntax.append(p.name)
    assert read(HERE/'LAUNCHER_SYNTAX.json')['status']=='PASS_POWERSHELL_SYNTAX_ONLY'
    monitor=read(HERE/'MONITOR_PRECHECK.json');assert monitor['guard_case_failures']==0 and monitor['unsandboxed_read_only_probe_passed']
    result=dict(status='READY_STATIC_CHECKED_NOT_YET_RTL',at=datetime.now(timezone(timedelta(hours=8))).isoformat(),
        preparation_manifest_sha256=sha(PREP/'MANIFEST_SHA256.json'),frozen_preparation_files_unchanged=len(seal['files']),
        vectors_regenerated=False,integer_oracle_recomputed=False,previous_small_tests_replayed=False,
        full_rtl_launched=False,testbench_byte_identical=True,top_named_port_bindings=len(ports),
        hierarchical_references_resolved=True,source_address_bits=15,highest_source_address=16401,input_address_bits=16,
        ordered_edge_count=433880,candidate_count=5768,dictionary_count=645,zero_weight_edges=8790,
        timeout=dict(ideal_lower_cycles=lower,conservative_upper_cycles=upper,step_limit=8000000,axi_limit=64,wall_seconds=600,
            proof='Per edge <=7 mock response-gap clocks +2 registered R launch/accept +2 FIFO write-to-output +6 lane clocks =17; <=16 clocks per burst control/AR wait; 8H+4096 for clear/neuron/finish. Overlap is ignored. Frozen earlier estimate16E is superseded by this extra FIFO margin.'),
        static_observations=[
            'Core FETCH/CHECK/READ/MUL/ROUND/SUM serializes each chemical RMW; same-target reads cannot overtake prior write',
            'Sync RAM values checked at following negedge; candidate address has a full posedge before readback',
            'AXI payload held under backpressure; FIFO4 RAM slots plus output has total capacity5; no combinational RAM read',
            'Reader AXI timeout counts missing RVALID, not own FIFO RREADY stalls; STEP_TIMEOUT separately bounds local stalls',
            'At most16 beats,8-byte alignment,one outstanding,4KiB split; first burst2 beats at0xff0',
            'Audit checks all original records/terms/partial sums/candidates/counts/coverage; rejects missing,duplicate,extra or malformed values',
            'Mock DDR handshake wait and all output tracing are finite; original order has0 adjacent same-target edges',
            'No full-scale exception injection added; yesterday sealed fault/drain evidence remains separate'],
        resource_policy=dict(minimum_free_MiB=2560,minimum_commit_headroom_MiB=8192,maximum_cpu_percent=50,
            maximum_initial_pages_input_per_second=4096,single_eda=True,wall_seconds=600,
            risk_assessment='Full testbench dominant 4-state arrays conservatively <=32MiB packed/aligned storage; compiler/debug/runtime overhead unmeasured. Reserve1.5GiB tool budget plus1GiB physical floor;8GiB initial commit headroom. This is a guarded attempt, not a guaranteed memory upper bound.',
            source='FLYVIS_20261012_CONSOLIDATE_1528_LIVE_GUI.md section4 allows limited XSim gate relaxation; direct user confirms A resource release',
            stop=['available physical<1024MiB','commit headroom<2048MiB','3seconds available<2048MiB and hard-page input>4096pages/s','monitor delayed>15seconds','wall>=600seconds','monitor API failure'],
            scope='ONE_XSIM_ONLY_NO_SYNTHESIS',counter_limit='PDH hard-page input includes memory-mapped file reads; not all events are swap'),
        python_ast_files=syntax,sv_compiled=False,sources={p.name:sha(p) for p in sorted(HERE.iterdir()) if p.suffix in ('.py','.ps1','.sv')},
        unchanged_core_rtl_sha256=prep['protected_parent_rtl_sha256'])
    (HERE/'STATIC_REVIEW.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('status','frozen_preparation_files_unchanged','testbench_byte_identical','top_named_port_bindings','timeout')},indent=2))
if __name__=='__main__':main()
