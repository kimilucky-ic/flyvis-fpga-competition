"""Independently validate the actual unchanged-RTL OOC failure and identities.

Missing utilization/DCP/timing is represented by null, never zero or PASS.
No graph/oracle/RTL replay, Vivado launch or source mutation is performed.
"""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json,re,psutil
HERE=Path(__file__).resolve().parent;B=HERE.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def main():
    launch=load(HERE/'LAUNCH_RECORD.json');run=HERE/launch['run'];identity=load(run/'RUN_IDENTITY.json');runtime=load(run/'RUNTIME.json')
    log=(run/'vivado.log').read_text(encoding='utf-8',errors='replace')
    assert runtime['exit_code']!=0 and runtime['stop_reason'] is None
    assert 'Vivado v2026.1.1' in log and 'SW Build 6605303' in log
    assert 'using a maximum of 1 processes' in log
    assert 'ERROR: [Synth 8-3391]' in log and 'chemical_mem_reg' in log and '288400' in log
    assert 'RTL Elaboration failed' in log
    for name,v in identity['generics'].items():assert re.search(r'Parameter '+name+r' bound to: '+str(v)+r'\b',log),name
    assert log.count('$readmem data file')==2 and log.count('is read successfully')>=2
    verified={}
    for name,digest in identity['source_and_rom_sha256'].items():
        assert sha(run/name)==digest,name
        if name.endswith('.sv'):assert sha(B/'rtl'/name)==digest,name
        verified[name]=digest
    for key,name in [('new_constraint_sha256','clock.xdc'),('tcl_sha256','synth_fullscale.tcl')]:assert sha(run/name)==identity[key],name
    sim=Path(identity['accepted_simulation_directory']);assert sha(sim/'PREPARATION.json')==identity['preparation_sha256']
    accepted_root=B/'fullscale_direct_20261012'
    assert sha(accepted_root/'FULL_RTL_RESULT.json')==identity['accepted_result_sha256']
    assert sha(accepted_root/'MANIFEST_SHA256.json')==identity['accepted_manifest_sha256']
    accepted=load(accepted_root/'FULL_RTL_RESULT.json')
    assert accepted['status']=='PASS_FULLSCALE_RTL_ONE_REQUEST' and accepted['exact_integer_mismatches']==0
    expected_outputs=['b_fullscale_synthesis.dcp','utilization_top.rpt','utilization_core.rpt','utilization_reader.rpt','utilization_fifo.rpt','timing_synth.rpt','check_timing.rpt','primitive_cells.tsv','ram_cells.tsv','black_boxes.txt']
    for name in expected_outputs:assert not (run/name).exists(),name
    alive=[]
    for item in runtime['processes']:
        try:
            p=psutil.Process(item['pid'])
            if abs(p.create_time()-item['created'])<.01:alive.append(item['pid'])
        except psutil.NoSuchProcess:pass
    assert not alive,alive
    fields=dict(LUT=None,FF=None,RAMB36=None,RAMB18=None,BRAM36_equivalent=None,DSP=None)
    timing=dict(WNS_ns=None,TNS_ns=None,WHS_ns=None,THS_ns=None,unconstrained_endpoints=None,black_boxes=None)
    raw_names=['RUN_IDENTITY.json','RUNTIME.json','console.log','vivado.log','vivado.jou','host_resources.csv','clock.xdc','synth_fullscale.tcl']
    result=dict(status='FAIL_OOC_RAM_INFERENCE',evidence_audit='PASS_FAILURE_EVIDENCE_AND_IDENTITIES_VALIDATED',
        audited_at=datetime.now(timezone(timedelta(hours=8))).isoformat(),run=launch['run'],tool='Vivado2026.1.1 SW6605303',device='xc7z020clg400-2',
        attempted_stage='OOC_SYNTHESIS',last_stage='RTL_ELABORATION_FAILED',actual_synthesis_launches=1,threads=1,
        error_id='Synth 8-3391',memory='chemical_mem_reg',logical_memory_bits=288400,
        supported_observation='Original chemical RAM access pattern was not inferable as block/distributed RAM; register dissolution was refused for its size',
        suspected_trigger='Two independent chemical write statements in the same posedge process: CLEAR and SUM/edge_write; no repaired A/B synthesis comparison yet',
        physical_memory_blocker=False,host_runtime=runtime,owned_processes_alive=alive,
        configuration=identity['generics'],original_source_and_rom_sha256=verified,
        utilization_scopes=dict(full_top=fields,core=fields,reader=fields,fifo=fields),timing=timing,
        ram_primitive_mapping=None,dcp_sha256=None,missing_outputs=expected_outputs,
        planning_comparison=dict(previous_core_tile_estimate=55,previous_system_inclusive_tile_estimate=71,
            actual=None,comparison='UNAVAILABLE_NO_SYNTHESIZED_NETLIST; planned tiles remain estimates'),
        constraints=dict(clock_period_ns=10,input_delay_max_ns=2,input_delay_min_ns=0,output_delay_max_ns=2,output_delay_min_ns=0,
            clock_source='Abstract clk only; no HD.CLK_SRC, PS FCLK, package pin, or physical clock tree',constraints_applied_to_netlist=False,
            xdc_sha256=sha(run/'clock.xdc')),
        prior_complete_rtl=dict(requests=1,edges=433880,candidates=5768,mismatches=0,cycles=2643658,still_valid_for_original_RTL=True,replayed=False),
        proposed_patch=dict(path='PROPOSED_CHEMICAL_WRITE_PORT.diff',sha256=sha(HERE/'PROPOSED_CHEMICAL_WRITE_PORT.diff'),applied=False,simulated=False,synthesized=False),
        raw_files={name:dict(bytes=(run/name).stat().st_size,sha256=sha(run/name)) for name in raw_names},
        stopping_point='Preserved unchanged-RTL failed run; no second synthesis, no core source modification, no implementation/bitstream/board/GPU/GUI operation')
    (HERE/'OOC_RESULT.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('status','evidence_audit','last_stage','actual_synthesis_launches','error_id','logical_memory_bits','owned_processes_alive')},indent=2))
if __name__=='__main__':main()
