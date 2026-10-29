"""Bind pipeline simulation acceptance to real OOC primitives and timing."""
from pathlib import Path
from collections import Counter,defaultdict
from datetime import datetime,timezone,timedelta
import sys,re,json,psutil
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parent))
from audit_ramfix_ooc_20261012 import load,sha,text,save,rows,utilization

def main():
    run=P/load(P/'LATEST_ooc.json')['run'];ident=load(run/'RUN_IDENTITY.json');rt=load(run/'RUNTIME.json')
    assert rt['exit_code']==0 and rt['stop_reason'] is None
    log=text(run/'vivado.log')
    assert 'Vivado v2026.1.1' in log and 'SW Build 6605303' in log
    assert 'B433880_OOC_SYNTHESIS_COMPLETE_NO_IMPLEMENTATION' in log and not re.search(r'^ERROR:',log,re.M)
    assert 'Synthesis finished with 0 errors, 0 critical warnings' in log
    assert 'using a maximum of 1 processes' in log
    for key,value in ident['generics'].items():
        if key=='reader_outstanding':
            # Vivado only logs overridden generics, not this module default.
            assert re.search(r'OUTSTANDING\s*=\s*'+str(value)+r'\b',text(run/'axi_edge_reader.sv'))
            assert 'OUTSTANDING' not in text(run/'ddr_synapse_top.sv')
        else:assert re.search(r'Parameter '+key+r' bound to: '+str(value)+r'\b',log),key
    assert sha(P/'ACCEPTED.json')==ident['accepted_sha256']
    accepted=load(P/'ACCEPTED.json');assert accepted['status']=='PASS_PIPELINE_A_RTL_ACCEPTANCE'
    for name,digest in accepted['rtl_sha256'].items():
        assert sha(P/'rtl'/name)==sha(run/name)==ident['source_sha256'][name]==digest
    for kind in ('fullpeak','fullstress'):
        a=accepted['checks'][kind];assert (a['edges'],a['candidates'],a['integer_mismatches'])==(433880,5768,0)
        for name,digest in a['raw_sha256'].items():assert sha(P/a['run']/name)==digest,(kind,name)
    for name,digest in ident['rom_sha256'].items():assert sha(run/'rom'/name)==digest
    for n,k in [('clock.xdc','xdc_sha256'),('synth_pipeline.tcl','tcl_sha256')]:assert sha(run/n)==ident[k]
    assert sha(run/'PREPARATION.json')==sha(P.parent/'fullscale_20261012/PREPARATION.json')
    scopes={name:utilization(run/f'utilization_{name}.rpt') for name in ('top','core','reader','fifo')}
    cells=rows(run/'primitive_cells.tsv');counts=Counter(r['ref_name'] for r in cells)
    assert len({r['cell'] for r in cells})==len(cells)
    for scope,u in scopes.items():
        cc=counts if scope=='top' else Counter(r['ref_name'] for r in cells if r['cell'].startswith(scope+'/'))
        assert u['RAMB36']==cc['RAMB36E1'] and u['RAMB18']==cc['RAMB18E1'] and u['DSP']==cc['DSP48E1']
        assert u['FF']==sum(v for k,v in cc.items() if k.startswith('FD'))
        assert u['BRAM36_equivalent']==u['RAMB36']+u['RAMB18']/2 and u['latches']==0
    ram=rows(run/'ram_cells.tsv');assert len(ram)==counts['RAMB36E1']+counts['RAMB18E1']
    memory=defaultdict(Counter)
    for r in ram:
        m=re.search(r'/([^/]+?)(?:_reg)?\[',r['cell'])
        label=m[1] if m else r['cell'].split('/')[-1].split('_reg')[0]
        memory[label][r['ref_name']]+=1
    lines=text(run/'timing_synth.rpt').splitlines();line=next(i for i,l in enumerate(lines) if l.strip().startswith('WNS(ns)'))
    vals=lines[line+2].split();assert len(vals)==12
    keys=('WNS_ns','TNS_ns','setup_failing_endpoints','setup_total_endpoints','WHS_ns','THS_ns','hold_failing_endpoints','hold_total_endpoints','WPWS_ns','TPWS_ns','pulse_failing_endpoints','pulse_total_endpoints')
    timing={k:(float(v) if k.endswith('_ns') else int(v)) for k,v in zip(keys,vals)}
    checks={k:int(v) for k,v in re.findall(r'checking (\w+) \((\d+)\)',text(run/'check_timing.rpt'))};assert len(checks)==12
    method=re.search(r'\| SYNTH-6\s*\| Warning\s*\|[^\n]+\|\s*(\d+)\s*\|',text(run/'methodology.rpt'))
    assert method and int(method[1])==len(ram)
    stage=dict(l.split('=',1) for l in text(run/'stage_identity.txt').splitlines() if '=' in l)
    assert stage['stage']=='OOC_SYNTHESIS_ONLY' and stage['part']=='xc7z020clg400-2' and stage['general.maxThreads']=='1'
    assert stage['black_box_count']=='0' and text(run/'black_boxes.txt').strip()=='count=0'
    assert (run/'b_fullscale_synthesis.dcp').stat().st_size>0
    alive=[]
    for item in rt['processes']:
        try:
            p=psutil.Process(item['pid'])
            if abs(p.create_time()-item['created'])<.01:alive.append(item['pid'])
        except psutil.NoSuchProcess:pass
    assert not alive,alive
    top=scopes['top'];fit=all(top[k]<=top[k+'_available'] for k in ('LUT','LUT_memory','FF','BRAM36_equivalent','DSP'))
    required=['b_fullscale_synthesis.dcp','RUN_IDENTITY.json','RUNTIME.json','vivado.log','console.log','primitive_cells.tsv','ram_cells.tsv','ram_properties.tsv','stage_identity.txt','black_boxes.txt']
    raw=list(dict.fromkeys(required+[p.name for p in run.glob('*.rpt')]+['resolved_constraints.xdc','clock.xdc','synth_pipeline.tcl','host_resources.csv']))
    result=dict(status='PASS_OOC_SYNTHESIS_RESOURCE_FIT' if fit else 'OOC_SYNTHESIS_COMPLETE_RESOURCE_OVERFLOW',evidence_level='OOC_SYNTHESIS_NOT_PLACED_OR_ROUTED',
        audited_at=datetime.now(timezone(timedelta(hours=8))).isoformat(),run=str(run.relative_to(P)),tool='Vivado2026.1.1 SW6605303',device='xc7z020clg400-2',
        auditor_sha256=sha(Path(__file__)),shared_parser_sha256=sha(P.parent/'audit_ramfix_ooc_20261012.py'),configuration=ident['generics'],
        utilization_scopes=scopes,primitive_counts=dict(sorted(counts.items())),ram_mapping={k:dict(v) for k,v in sorted(memory.items())},
        timing=timing,check_timing=checks,methodology_warnings={'SYNTH-6_RAM_output_register_not_merged':int(method[1])},stage_identity=stage,black_boxes=0,resource_fit=fit,timing_met_at_10ns=timing['WNS_ns']>=0 and timing['WHS_ns']>=0,
        host_runtime=rt,owned_processes_alive=alive,accepted_rtl_sha256=sha(P/'ACCEPTED.json'),dcp_sha256=sha(run/'b_fullscale_synthesis.dcp'),
        raw_files={name:dict(bytes=(run/name).stat().st_size,sha256=sha(run/name)) for name in raw},warning_counts=dict(Counter(re.findall(r'^WARNING: \[([^\]]+)\]',log,re.M))),
        limits=['B prototype only; no PS/interconnect/SoC','Synthesis timing has estimated interconnect, abstract 10ns clock and max2/min0ns IO delays',
                'HD.CLK_SRC unassigned; no physical clock tree or routed timing','Mock DDR, no measured HP0 or GPU COMMIT integration',
                'Exact RTL parity is pre-synthesis; no gate-level simulation or formal equivalence'])
    save(P/'OOC_RESULT.json',result)
    print(json.dumps({k:result[k] for k in ('status','utilization_scopes','ram_mapping','timing','check_timing','warning_counts')},indent=2))
if __name__=='__main__':main()
