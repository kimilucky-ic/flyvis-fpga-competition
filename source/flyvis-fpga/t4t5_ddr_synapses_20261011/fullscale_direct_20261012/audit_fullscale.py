"""Audit a single real XSim run against all frozen full-scale integer results.

Never creates simulation evidence. Missing/truncated/duplicate/changed output
is a failure. Run only after the gated runner has written RUNTIME.json.
"""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import argparse,csv,hashlib,json,re
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
PREP=HERE.parent/"fullscale_20261012"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read_json(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def save(p,d):Path(p).write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def need(ok,message):
    if not ok:raise ValueError(message)
def rows(p):
    with Path(p).open(newline='',encoding='utf-8') as f:
        yield from csv.DictReader(f)
def audit(run):
    run=run.resolve();need(run.is_relative_to(HERE/'build'),'Run is outside isolated build directory')
    prep=read_json(PREP/'PREPARATION.json');c=prep['contract'];H,S,E,W=c['H'],c['source_count'],c['edge_count'],c['weight_count']
    need((H,S,E,W)==(5768,16402,433880,645),'Unexpected graph dimensions')
    identity=read_json(run/'RUN_IDENTITY.json');runtime=read_json(run/'RUNTIME.json')
    need(identity['auditor_sha256']==sha(__file__),'Auditor changed after launch')
    need(runtime['exit_code']==0 and not runtime['wall_timeout'] and runtime.get('stop_reason') is None,'Simulator runtime failed or stopped by resource/time guard')
    need(identity['request_count']==1,'More than one request')
    need(sha(PREP/'PREPARATION.json')==identity['preparation_sha256']==sha(run/'PREPARATION.json'),'Preparation changed')
    need(identity['config_sha256']==sha(run/'full_config.svh')==prep['files']['full_config.svh']['sha256'],'Config changed')
    for name,digest in identity['sources'].items():need(sha(run/name)==digest,f'Run source changed: {name}')
    for name,digest in prep['protected_parent_rtl_sha256'].items():
        need(sha(run/name)==sha(HERE.parent/'rtl'/name)==digest,f'Protected RTL changed: {name}')
    for name,v in prep['files'].items():
        need(sha(PREP/'vectors'/name)==v['sha256'],f'Prepared vector changed: {name}')
        if name.endswith('.mem'):need(sha(run/'rom'/name)==v['sha256'],f'Simulator vector changed: {name}')
    for name,v in prep['source_files'].items():need(sha(ROOT/name)==v['sha256'],f'Frozen source changed: {name}')
    gate_path=HERE/identity['gate_path'];gate=read_json(gate_path)
    need(sha(gate_path)==identity['gate_sha256'] and gate['allowed'] and gate['A_release_confirmed'],'Launch lacked valid resource/release gate')
    log=(run/'xsim.log').read_text(encoding='utf-8',errors='replace')
    need(log.count('FULL_ALL_PASS requests=1 ')==1,'Expected exactly one actual XSim PASS marker')
    need(not re.search(r'\b(?:fatal|error):',log,re.I),'XSim log contains a fatal/error')
    records=np.fromfile(ROOT/'flyvis-fpga/t4t5_scale_20261011/data/incoming_edges_le64.bin',dtype='<u8')
    oracle=dict(np.load(PREP/'vectors/integer_oracle.npz',allow_pickle=False))
    weights=np.fromfile(ROOT/'flyvis-fpga/t4t5_scale_20261011/data/weight_dictionary_q20_i32.bin',dtype='<i4')
    source=oracle['source_q24'];candidate=oracle['candidate_q24']
    sources=[0]*S;targets=[0]*H;dictionary=[0]*W;seen=0;previous_cycle=-1
    negative_source_edges=zero_terms=negative_terms=zero_weight_edges=0
    for row in rows(run/'edge_trace.csv'):
        need(seen<E,'Extra edge record')
        rec=int(records[seen]);s=(rec>>21)&32767;t=(rec>>36)&8191;w=(rec>>49)&1023
        expect=dict(edge_index=seen,global_edge_id=rec&0x1fffff,source_index=s,target=t,dict_index=w,
            source_q24=int(source[s]),term_q24=int(oracle['edge_term_q24'][seen]),
            partial_sum_q24=int(oracle['partial_chemical_q24'][seen]))
        need(int(row['record_hex'],16)==rec,f'Original LE64 mismatch at {seen}')
        for key,value in expect.items():need(int(row[key])==value,f'{key} mismatch at edge {seen}')
        cycle=int(row['cycle']);need(cycle>previous_cycle and (seen==0 or cycle-previous_cycle>=6),'Edge cycles repeat or violate serialized lane')
        previous_cycle=cycle;sources[s]+=1;targets[t]+=1;dictionary[w]+=1
        negative_source_edges+=int(source[s])<0;zero_terms+=expect['term_q24']==0
        negative_terms+=expect['term_q24']<0;zero_weight_edges+=int(weights[w])==0;seen+=1
    need(seen==E,'Truncated edge log')
    candidate_count=0
    for row in rows(run/'candidates.csv'):
        need(candidate_count<H,'Extra candidate')
        need(int(row['index'])==candidate_count and int(row['candidate_q24'])==int(candidate[candidate_count]),f'Candidate mismatch at {candidate_count}')
        candidate_count+=1
    need(candidate_count==H,'Truncated candidate log')
    all_coverage={(kind,i):value for kind,hist in [('source',sources),('target',targets),('dictionary',dictionary)] for i,value in enumerate(hist)}
    for row in rows(run/'coverage.csv'):
        key=(row['kind'],int(row['index']))
        need(key in all_coverage and int(row['count'])==all_coverage[key],f'Coverage mismatch or duplicate: {key}')
        del all_coverage[key]
    need(not all_coverage,'Missing source/target/dictionary coverage')
    need(all(sources) and all(targets) and all(dictionary),'Missing source/target/dictionary entry')
    need(min(targets)==c['fanin_min'] and max(targets)==c['fanin_max'],'Fanin changed')
    address=int(c['base_addr_hex'],16);remaining=E;bursts=boundaries=0;last_burst_cycle=-1
    for row in rows(run/'axi_bursts.csv'):
        need(remaining>0,'Extra AXI burst')
        beats=min(16,remaining,(4096-(address&4095))//8)
        need(int(row['burst_index'])==bursts and int(row['address_hex'],16)==address and int(row['beats'])==beats,'Burst length/address/order mismatch')
        burst_cycle=int(row['cycle']);need(burst_cycle>last_burst_cycle,'Burst cycles not increasing')
        last_burst_cycle=burst_cycle;address+=8*beats;remaining-=beats;bursts+=1;boundaries+=(address&4095)==0
    need(remaining==0 and bursts==c['burst_count'] and boundaries==c['page_boundary_ends'],'Incomplete AXI stream')
    metrics={}
    for row in rows(run/'summary.csv'):
        key=row['metric'];need(key not in metrics,f'Duplicate summary metric: {key}');metrics[key]=row['value']
    exact=dict(status=0,reader_error=0,requests=1,edges=E,candidates=H,bursts=bursts,page_boundary_ends=boundaries,
        max_fifo_occupancy=5,source_reads_ge_16384=sum(sources[16384:]),last_source_reads=sources[-1],
        same_target_adjacent=0,synchronous_read_checks=E+H,zero_weight_edges=zero_weight_edges,
        negative_source_edges=negative_source_edges,zero_terms=zero_terms,negative_terms=negative_terms,
        step_timeout=c['step_timeout_cycles'],axi_timeout=c['axi_timeout_cycles'],timeout_events=0,reject_events=0)
    for key,value in exact.items():need(int(metrics[key])==value,f'Summary mismatch: {key}')
    need(metrics['signature_hex'].lower()==c['signature_hex'],'Final signature mismatch')
    cycles=int(metrics['cycles']);need(c['ideal_schedule_cycles_lower_bound']<=cycles<c['step_timeout_cycles'],'Cycles outside proved bounds')
    need(previous_cycle<cycles,'Final edge occurs outside compute interval')
    need(int(metrics['min_same_target_write_read_gap'])>=3,'RAM write/read overlap')
    for key in ('fifo_stall_cycles','ar_stall_cycles','r_bubble_cycles','max_r_backpressure_run'):
        need(int(metrics[key])>0,f'No intended stall coverage: {key}')
    need(int(metrics['max_reader_wait'])<c['axi_timeout_cycles'],'AXI timeout limit reached')
    need((sum(sources[:H]),sum(sources[H:]),zero_weight_edges)==(82793,351087,8790),'HH/RH/zero totals changed')
    evidence_names=['RUN_IDENTITY.json','PREPARATION.json','RUNTIME.json','xvlog.log','xelab.log','xsim.log',
        'console.log','edge_trace.csv','candidates.csv','coverage.csv','axi_bursts.csv','summary.csv','host_resources.csv']
    result=dict(status='PASS_FULLSCALE_RTL_ONE_REQUEST',evidence_level='XSIM_WITH_MOCK_DDR_NOT_BOARD_OR_HP0_MEASUREMENT',
        audited_at=datetime.now(timezone(timedelta(hours=8))).isoformat(),auditor_sha256=sha(__file__),
        run=str(run.relative_to(HERE)),requests=1,edge_comparisons=seen,candidate_comparisons=candidate_count,
        exact_integer_mismatches=0,cycles=cycles,summary=metrics,host_runtime=runtime,
        raw_files={name:dict(bytes=(run/name).stat().st_size,sha256=sha(run/name)) for name in evidence_names},
        limits=['Single initial-state request only','No new full-scale fault injection or adjacent-target case; use separately sealed small directed tests',
            'No GPU/PL COMMIT exchange exercised','Mock DDR timing is not physical AXI HP0 throughput','No synthesis/place/route or board operation'])
    save(run/'FULL_RTL_AUDIT.json',result);save(HERE/'FULL_RTL_RESULT.json',result)
    print(json.dumps({key:result[key] for key in ('status','requests','edge_comparisons','candidate_comparisons','cycles','exact_integer_mismatches')}))
    return result
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',type=Path,required=True);args=ap.parse_args()
    try:audit(args.run)
    except Exception as exc:
        if args.run.resolve().is_relative_to(HERE/'build') and args.run.is_dir():
            save(args.run/'FULL_RTL_AUDIT_FAIL.json',dict(status='FAIL_FULL_RTL_AUDIT',error_type=type(exc).__name__,error=str(exc)))
        raise
if __name__=='__main__':main()
