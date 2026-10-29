"""Audit every raw full-graph row and bind exact new RTL to directed acceptance."""
from pathlib import Path
import csv,json,hashlib,re,numpy as np
P=Path(__file__).resolve().parent;B=P.parent;ROOT=B.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,d):p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def rows(p):
    with p.open(encoding='utf-8',newline='') as f:yield from csv.DictReader(f)
def run_for(kind):
    r=P/load(P/f'LATEST_{kind}.json')['run'];ident=load(r/'RUN_IDENTITY.json');rt=load(r/'RUNTIME.json')
    assert rt['exit_code']==0 and rt['stop_reason'] is None
    log=(r/'xsim.log').read_text(encoding='utf-8',errors='replace')
    assert not re.search(r'Fatal:|FATAL|Error:',log) and log.count('ALL_PASS')==1
    for n,d in ident['source_sha256'].items():assert sha(r/n)==d,n
    for n,d in ident['rom_sha256'].items():assert sha(r/'rom'/n)==d,n
    relevant=['ddr_synapse_core.sv'] if kind in ('math','directed') else ['axi_edge_reader.sv'] if kind=='reader' else list((p.name for p in (P/'rtl').glob('*.sv')))
    for n in relevant:assert sha(r/n)==sha(P/'rtl'/n),(kind,n)
    return r,ident,rt,log
def full(kind):
    r,ident,rt,log=run_for(kind);prep=load(B/'fullscale_20261012/PREPARATION.json')
    for n,v in prep['files'].items():
        assert sha(B/'fullscale_20261012/vectors'/n)==v['sha256']
        if n.endswith('.mem'):assert sha(r/'rom'/n)==v['sha256']
    original=ROOT/'flyvis-fpga/t4t5_scale_20261011/data/incoming_edges_le64.bin'
    assert sha(original)=='208da3b1a8984928bcc338e0f773a664398ef5df1e53a9a889d29e3fed197ff2'
    edges=np.fromfile(original,dtype='<u8');oracle=dict(np.load(B/'fullscale_20261012/vectors/integer_oracle.npz',allow_pickle=False))
    c=prep['contract'];E,H,S,W=c['edge_count'],c['H'],c['source_count'],c['weight_count']
    counts={'source':[0]*S,'target':[0]*H,'dictionary':[0]*W};seen=0;previous=-1;adjacent=0
    for row in rows(r/'edge_trace.csv'):
        assert seen<E
        rec=int(edges[seen]);src=(rec>>21)&32767;t=(rec>>36)&8191;wi=(rec>>49)&1023
        expected=dict(edge_index=seen,global_edge_id=rec&0x1fffff,source_index=src,target=t,dict_index=wi,
            source_q24=int(oracle['source_q24'][src]),term_q24=int(oracle['edge_term_q24'][seen]),partial_sum_q24=int(oracle['partial_chemical_q24'][seen]))
        assert int(row['record_hex'],16)==rec,seen
        for k,v in expected.items():assert int(row[k])==v,(kind,seen,k)
        cycle=int(row['cycle']);assert cycle>previous
        adjacent+=cycle==previous+1;previous=cycle
        counts['source'][src]+=1;counts['target'][t]+=1;counts['dictionary'][wi]+=1;seen+=1
    assert seen==E
    n=0
    for row in rows(r/'candidates.csv'):
        assert n<H and int(row['index'])==n and int(row['candidate_q24'])==int(oracle['candidate_q24'][n]),n
        n+=1
    assert n==H
    coverage={(k,i):v for k,arr in counts.items() for i,v in enumerate(arr)}
    for row in rows(r/'coverage.csv'):
        key=(row['kind'],int(row['index']));assert int(row['count'])==coverage.pop(key)
    assert not coverage and all(all(a) for a in counts.values())
    assert sum(counts['source'][:H])==82793 and sum(counts['source'][H:])==351087
    assert sum(counts['source'][16384:])==2067 and counts['source'][-1]==92
    assert min(counts['target'])==26 and max(counts['target'])==119
    address=int(c['base_addr_hex'],16);remaining=E;bursts=pages=0;prev=-1
    for row in rows(r/'axi_bursts.csv'):
        beats=min(16,remaining,(4096-(address&4095))//8)
        assert remaining>0 and int(row['burst_index'])==bursts and int(row['address_hex'],16)==address and int(row['beats'])==beats
        assert int(row['cycle'])>prev;prev=int(row['cycle']);remaining-=beats;address+=8*beats;bursts+=1;pages+=(address&4095)==0
    assert remaining==0 and bursts==27119 and pages==848
    metrics={}
    for row in rows(r/'summary.csv'):
        assert row['metric'] not in metrics;metrics[row['metric']]=row['value']
    expected=dict(stress=int(kind=='fullstress'),status=0,reader_error=0,edges=E,candidates=H,bursts=27119,page_boundary_ends=848,
        max_fifo_occupancy=129,max_outstanding=4,source_sync_checks=E+2*H,chemical_sync_checks=E+H,
        zero_weight_edges=8790,negative_source_edges=71835,zero_terms=74274,negative_terms=204113,consecutive_edge_retirements=adjacent)
    for k,v in expected.items():assert int(metrics[k])==v,(k,metrics[k],v)
    assert metrics['signature_hex']==c['signature_hex'] and int(metrics['max_reader_wait'])<64 and int(metrics['fifo_stall_cycles'])>0
    cycles=int(metrics['cycles']);assert previous<cycles<8000000
    if kind=='fullpeak':assert cycles<600000 and adjacent>=E-32
    else:assert cycles<2000000 and int(metrics['ar_stall_cycles'])>0 and int(metrics['r_bubble_cycles'])>0
    raw=['edge_trace.csv','candidates.csv','coverage.csv','axi_bursts.csv','summary.csv','xsim.log','xvlog.log','xelab.log','RUN_IDENTITY.json','RUNTIME.json','host_resources.csv']
    result=dict(status='PASS_EXACT_FULLGRAPH_RTL',kind=kind,run=str(r.relative_to(P)),edges=E,candidates=H,integer_mismatches=0,cycles=cycles,metrics=metrics,host_runtime=rt,
        raw_sha256={n:sha(r/n) for n in raw},limitations=['One frozen initial-state request per supply scenario','Mock DDR, not physical HP0 bandwidth','Frequency conversion is conditional until timing/implementation evidence'])
    save(r/'FULL_AUDIT.json',result);save(P/(kind.upper()+'_RESULT.json'),result)
    return result
def main():
    checks={}
    markers={'directed':'DIRECTED_ALL_PASS cases=20','math':'MATH_ALL_PASS multiply=1024 rounding20=1024 rounding24=1024','reader':'READER_ALL_PASS cases=14'}
    for k,m in markers.items():
        r,ident,rt,log=run_for(k);assert m in log
        checks[k]=dict(run=str(r.relative_to(P)),log_sha256=sha(r/'xsim.log'),runtime_sha256=sha(r/'RUNTIME.json'),identity_sha256=sha(r/'RUN_IDENTITY.json'),marker=m)
    for k in ('fullpeak','fullstress'):checks[k]=full(k)
    result=dict(status='PASS_PIPELINE_A_RTL_ACCEPTANCE',rtl_sha256={p.name:sha(p) for p in (P/'rtl').glob('*.sv')},checks=checks,
        validation_scope='20 core directed cases; 14 reader cases; 1024 multiplies; 2048 rounded values; two fullgraph supply scenarios, 867760 edges and11536 candidates exact',
        evidence_level='RTL_SIMULATION_ONLY',old_baseline_cycles=2643658,peak_speedup_cycles=2643658/checks['fullpeak']['cycles'],stress_speedup_cycles=2643658/checks['fullstress']['cycles'])
    save(P/'ACCEPTED.json',result)
    print(json.dumps({k:result[k] for k in ('status','peak_speedup_cycles','stress_speedup_cycles','validation_scope')},indent=2))
if __name__=='__main__':main()
