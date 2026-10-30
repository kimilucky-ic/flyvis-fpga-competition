"""Read-only independent evidence audit of a completed RAM repair OOC run."""
from pathlib import Path
from collections import Counter,defaultdict
from datetime import datetime,timezone,timedelta
import argparse,csv,json,hashlib,re,psutil
B=Path(__file__).resolve().parent
if B.name.startswith('ramfix_'):B=B.parent
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def text(p):return p.read_text(encoding='utf-8',errors='replace')
def save(p,d):p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def rows(p):
    with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def utilization(p):
    s=text(p);out={}
    names={'LUT':'Slice LUTs*','LUT_logic':'LUT as Logic','LUT_memory':'LUT as Memory','FF':'Slice Registers','latches':'Register as Latch','BRAM36_equivalent':'Block RAM Tile','RAMB36':'RAMB36/FIFO*','RAMB18':'RAMB18','DSP':'DSPs'}
    for key,label in names.items():
        m=re.search(r'^\|\s*'+re.escape(label)+r'\s*\|\s*([\d.]+)\s*\|[^\n]+',s,re.M)
        assert m,(p,label)
        out[key]=float(m[1]) if '.' in m[1] else int(m[1])
        cols=[v.strip() for v in m[0].strip('|').split('|')]
        if len(cols)>=6 and cols[4]:
            out[key+'_available']=int(cols[4]);out[key+'_reported_percent']=cols[5]
            out[key+'_percent']=round(100*out[key]/int(cols[4]),4)
    return out
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--directory',required=True);args=ap.parse_args()
    here=(B/args.directory).resolve();assert here.parent==B and here.name.startswith('ramfix_')
    launch=load(here/'LAUNCH_RECORD.json');run=here/launch['run'];ident=load(run/'RUN_IDENTITY.json');runtime=load(run/'RUNTIME.json')
    assert runtime['exit_code']==0 and runtime['stop_reason'] is None
    s=text(run/'vivado.log');assert 'Vivado v2026.1.1' in s and 'SW Build 6605303' in s
    assert 'B433880_OOC_SYNTHESIS_COMPLETE_NO_IMPLEMENTATION' in s and not re.search(r'^ERROR:',s,re.M)
    assert 'Synthesis finished with 0 errors, 0 critical warnings' in s
    assert 'using a maximum of 1 processes' in s
    for key,value in ident['generics'].items():assert re.search(r'Parameter '+key+r' bound to: '+str(value)+r'\b',s),key
    sim=Path(ident['accepted_simulation_directory']);accepted=sim.parent.parent
    assert sha(accepted/'FULL_RTL_RESULT.json')==ident['accepted_result_sha256']
    assert sha(accepted/'MANIFEST_SHA256.json')==ident['accepted_manifest_sha256']
    a=load(accepted/'FULL_RTL_RESULT.json');assert (a['edge_comparisons'],a['candidate_comparisons'],a['exact_integer_mismatches'],a['cycles'])==(433880,5768,0,2643658)
    for name,v in load(accepted/'MANIFEST_SHA256.json')['files'].items():assert sha(accepted/name)==v['sha256'],name
    for name,digest in ident['source_and_rom_sha256'].items():assert sha(run/name)==sha(sim/name)==digest,name
    for key,name in [('new_constraint_sha256','clock.xdc'),('tcl_sha256','synth_fullscale.tcl')]:assert sha(run/name)==ident[key]
    assert sha(run/'PREPARATION.json')==ident['preparation_sha256']
    scopes={name:utilization(run/f'utilization_{name}.rpt') for name in ('top','core','reader','fifo')}
    cells=rows(run/'primitive_cells.tsv');counts=Counter(r['ref_name'] for r in cells)
    assert len({r['cell'] for r in cells})==len(cells)
    for scope,u in scopes.items():
        cc=counts if scope=='top' else Counter(r['ref_name'] for r in cells if r['cell'].startswith(scope+'/'))
        assert u['RAMB36']==cc['RAMB36E1'] and u['RAMB18']==cc['RAMB18E1'] and u['DSP']==cc['DSP48E1'],scope
        assert u['FF']==sum(v for k,v in cc.items() if k.startswith('FD')),scope
        assert u['BRAM36_equivalent']==u['RAMB36']+u['RAMB18']/2,scope
        assert u['latches']==0,scope
    ram=rows(run/'ram_cells.tsv');assert len(ram)==counts['RAMB36E1']+counts['RAMB18E1']
    memory=defaultdict(Counter)
    for r in ram:
        m=re.search(r'/([^/]+?)(?:_reg)?\[',r['cell'])
        label=m[1] if m else r['cell'].split('/')[-1].split('_reg')[0]
        memory[label][r['ref_name']]+=1
    t=text(run/'timing_synth.rpt');lines=t.splitlines();line=next(i for i,l in enumerate(lines) if l.strip().startswith('WNS(ns)'))
    vals=lines[line+2].split();assert len(vals)==12
    keys=('WNS_ns','TNS_ns','setup_failing_endpoints','setup_total_endpoints','WHS_ns','THS_ns','hold_failing_endpoints','hold_total_endpoints','WPWS_ns','TPWS_ns','pulse_failing_endpoints','pulse_total_endpoints')
    timing={k:(float(v) if k.endswith('_ns') else int(v)) for k,v in zip(keys,vals)}
    checks={k:int(v) for k,v in re.findall(r'checking (\w+) \((\d+)\)',text(run/'check_timing.rpt'))};assert len(checks)==12
    stage=dict(l.split('=',1) for l in text(run/'stage_identity.txt').splitlines() if '=' in l)
    assert stage['stage']=='OOC_SYNTHESIS_ONLY' and stage['part']=='xc7z020clg400-2' and stage['general.maxThreads']=='1'
    assert stage['black_box_count']=='0' and text(run/'black_boxes.txt').strip()=='count=0'
    assert (run/'b_fullscale_synthesis.dcp').stat().st_size>0
    alive=[]
    for item in runtime['processes']:
        try:
            p=psutil.Process(item['pid'])
            if abs(p.create_time()-item['created'])<.01:alive.append(item['pid'])
        except psutil.NoSuchProcess:pass
    assert not alive,alive
    top=scopes['top'];fit=all(top[k]<=top[k+'_available'] for k in ('LUT','LUT_memory','FF','BRAM36_equivalent','DSP'))
    required=['b_fullscale_synthesis.dcp','RUN_IDENTITY.json','RUNTIME.json','vivado.log','console.log','primitive_cells.tsv','ram_cells.tsv','ram_properties.tsv','stage_identity.txt','black_boxes.txt']
    raw=list(dict.fromkeys(required+[p.name for p in run.glob('*.rpt')]+['resolved_constraints.xdc','clock.xdc','synth_fullscale.tcl','host_resources.csv']))
    result=dict(status='PASS_OOC_SYNTHESIS_RESOURCE_FIT' if fit else 'OOC_SYNTHESIS_COMPLETE_RESOURCE_OVERFLOW',evidence_level='OOC_SYNTHESIS_NOT_PLACED_OR_ROUTED',audited_at=datetime.now(timezone(timedelta(hours=8))).isoformat(),run=launch['run'],tool='Vivado2026.1.1 SW6605303',device='xc7z020clg400-2',auditor_sha256=sha(Path(__file__)),configuration=ident['generics'],utilization_scopes=scopes,primitive_counts=dict(sorted(counts.items())),ram_mapping={k:dict(v) for k,v in sorted(memory.items())},timing=timing,check_timing=checks,stage_identity=stage,black_boxes=0,resource_fit=fit,timing_met_at_10ns=timing['WNS_ns']>=0 and timing['WHS_ns']>=0,host_runtime=runtime,owned_processes_alive=alive,accepted_full_rtl=dict(directory=str(sim),edges=433880,candidates=5768,integer_mismatches=0,cycles=2643658),dcp_sha256=sha(run/'b_fullscale_synthesis.dcp'),raw_files={name:dict(bytes=(run/name).stat().st_size,sha256=sha(run/name)) for name in raw},warning_counts=dict(Counter(re.findall(r'^WARNING: \[([^\]]+)\]',s,re.M))),limits=['Full B prototype, no PS/AXI interconnect/SoC shells','Synthesis timing uses estimated interconnect, abstract 10ns clk and max2/min0ns IO delays','HD.CLK_SRC is unassigned; no physical clock tree, routed timing or board evidence','Mock DDR RTL is not measured HP0 bandwidth; no GPU shared COMMIT integration','RTL data parity is pre-synthesis; no post-synthesis equivalence or netlist simulation'])
    save(here/'OOC_RESULT.json',result)
    print(json.dumps({k:result[k] for k in ('status','utilization_scopes','ram_mapping','timing','check_timing','warning_counts')},indent=2))
if __name__=='__main__':main()
