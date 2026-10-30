"""Accept only current-source XSim runs; independently recheck raw CSV.

This script recomputes integer arithmetic with divmod instead of the vector
generator's shift oracle, and checks raw trace/output lengths and every value.
Failed and superseded runs stay on disk and are listed separately.
"""
from pathlib import Path
import hashlib,json,csv,re,ctypes,subprocess
from datetime import datetime,timezone,timedelta

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def signed(v,n):return v-(1<<n) if v>=(1<<(n-1)) else v
def readmem(p):return [int(v,16) for v in Path(p).read_text().split()]
def rounding(v,n):
    q,rem=divmod(abs(v),2**n)
    if rem>=2**(n-1):q+=1
    return -q if v<0 else q
def reference(request,edges,weights,neurons,h,s):
    chem=[0]*h;trace=[]
    for r in edges:
        gid=r&0x1fffff;src=(r>>21)&0x7fff;t=(r>>36)&0x1fff;w=(r>>49)&0x3ff
        assert r>>59==0 and src<s and t<h and w<len(weights)
        term=rounding(max(0,request[src])*weights[w],20);chem[t]+=term
        assert -(1<<30)<=term<(1<<30) and -(1<<49)<=chem[t]<(1<<49)
        trace.append((gid,t,term,chem[t]))
    out=[]
    for i,v in enumerate(neurons):
        bias=signed(v&((1<<31)-1),31);inv=signed(v>>31,31)
        drive=-request[i]+bias+chem[i]+request[s+i]
        vel=rounding(drive*inv,24);delta=rounding(vel*83886,24)
        out.append(request[i]+delta)
    return trace,out
def audit(run):
    identity=json.loads((run/'RUN_IDENTITY.json').read_text(encoding='utf-8-sig'))
    name=identity['fixture'];fixture=HERE/'fixtures'/name
    for source in identity['sources']:
        assert sha(HERE/'rtl'/source['name'])==sha(run/source['name'])==source['sha256']
    assert sha(run/'manifest.json')==sha(fixture/'manifest.json')==identity['fixture_manifest_sha256']
    m=json.loads((run/'manifest.json').read_text());h=m['H'];s=m['source_count'];e=m['edge_count'];words=h+s
    for f,v in m['files'].items():assert sha(run/('fixture_config.svh' if f=='fixture_config.svh' else 'rom/'+f))==sha(fixture/f)==v
    for f,v in m['source_hashes'].items():assert sha(ROOT/f)==v
    log=(run/'xsim.log').read_text(errors='replace')
    assert 'ALL_PASS' in log and not re.search(r'Fatal:|FATAL|Error:',log)
    assert '2026.1.1' in log
    rows=list(csv.reader((run/'summary.csv').open()))
    good=[list(map(int,r[1:])) for r in rows if r[0]=='PASS']
    failures=[list(map(int,r[1:])) for r in rows if r[0]=='FAULT_PASS']
    expected_count=m['requests']+(name=='mini')
    assert len(good)==expected_count
    assert [r[0] for r in good]==list(range(m['requests']))+([0] if name=='mini' else [])
    if name=='mini':
        assert [r[0] for r in failures]==list(range(1,26))
        assert sum(r[0]=='DRAIN_PASS' for r in rows)==2
    else:assert not failures
    edges=readmem(run/'rom/edges.mem');weights=[signed(v,24) for v in readmem(run/'rom/weights.mem')]
    req=[signed(v,32) for v in readmem(run/'rom/requests.mem')];neurons=readmem(run/'rom/neurons.mem')
    assert len(edges)==e and len(weights)==m['weight_count'] and len(req)==words*m['requests'] and len(neurons)==h
    traces=list(csv.DictReader((run/'edge_trace.csv').open()));states=list(csv.DictReader((run/'states.csv').open()))
    assert len(traces)==e*len(good) and len(states)==h*len(good)
    repeated=zero_terms=negative_terms=0;handoffs=0;previous_out=None
    for block,row in enumerate(good):
        idx,cy,applied,received,stalls,maxfifo,bursts,arstall,bubbles=row
        assert applied==received==e and maxfifo<=5 and bursts>=2
        reference_trace,reference_out=reference(req[idx*words:(idx+1)*words],edges,weights,neurons,h,s)
        if m['prior_cases'] and m['prior_cases'][idx]['internally_recurrent']:
            assert req[idx*words:idx*words+h]==previous_out
            handoffs+=1
        for k,(gid,t,term,partial) in enumerate(reference_trace):
            actual=traces[block*e+k]
            assert tuple(int(actual[f]) for f in ('request','edge_index','global_edge_id','target','term','partial_sum'))==(idx,k,gid,t,term,partial)
            zero_terms+=term==0;negative_terms+=term<0
            if k and reference_trace[k-1][1]==t:repeated+=1
        for i,v in enumerate(reference_out):
            actual=states[block*h+i]
            assert tuple(int(actual[f]) for f in ('request','index','candidate_q24'))==(idx,i,v)
        previous_out=reference_out
    assert any(r[4]>0 for r in good) and max(r[5] for r in good)==5
    if name in ('92','298'):assert any(r[7]>0 and r[8]>0 for r in good)
    artifacts=['RUN_IDENTITY.json','manifest.json','xvlog.log','xelab.log','xsim.log','summary.csv','edge_trace.csv','states.csv']
    return dict(fixture=name,path=str(run.relative_to(HERE)),evidence_level='RTL_SIM_XSIM_2026_1_1',
        requests=len(good),edges=len(traces),states=len(states),fault_checks=len(failures),
        cycle_counts=[r[1] for r in good],fifo_stall_cycles=[r[4] for r in good],
        maximum_fifo_occupancy=max(r[5] for r in good),ar_stall_cycles=sum(r[7] for r in good),ddr_bubbles=sum(r[8] for r in good),
        consecutive_same_target_comparisons=repeated,zero_term_comparisons=zero_terms,negative_term_comparisons=negative_terms,
        recurrent_old_state_handoffs=handoffs,exact_mismatches=0,files={f:dict(bytes=(run/f).stat().st_size,sha256=sha(run/f)) for f in artifacts})
class MemoryStatus(ctypes.Structure):
    _fields_=[('length',ctypes.c_ulong),('load',ctypes.c_ulong)]+[(n,ctypes.c_ulonglong) for n in (
        'total_phys','avail_phys','total_page','avail_page','total_virtual','avail_virtual','avail_extended')]
def main():
    accepted={};excluded=[]
    for run in sorted((HERE/'build').iterdir()):
        try:r=audit(run);accepted[r['fixture']]=r
        except (AssertionError,FileNotFoundError,KeyError,ValueError) as exc:
            excluded.append(dict(path=str(run.relative_to(HERE)),reason=type(exc).__name__,clean_ALL_PASS=False))
    assert set(accepted)=={'mini','addr15','92','298'}
    inherited=json.loads((HERE/'stage2_format/INHERITED_IDENTITY.json').read_text())
    for p,v in inherited['files'].items():assert sha(ROOT/p)==v['sha256'] and (ROOT/p).stat().st_size==v['bytes']
    inherited_weight=next(v for p,v in inherited['files'].items() if Path(p).name=='weight_dictionary_q20_i32.bin')
    assert sha(HERE/'stage2_format/weight_dictionary_q20_i32.bin')==inherited_weight['sha256']
    result=dict(status='PASS_FIRST_MILESTONE_RTL_SIM',date_local=datetime.now(timezone(timedelta(hours=8))).isoformat(),
        tool='Vivado Simulator 2026.1.1, SW 6605303',target_intended='xc7z020clg400-2',
        evidence_level='RTL_SIM_ONLY',clock='10 ns testbench clock; not timing closure',
        current_rtl_sha256={p.name:sha(p) for p in sorted((HERE/'rtl').glob('*.sv'))},
        positive_requests=sum(r['requests'] for r in accepted.values()),ordered_edge_comparisons=sum(r['edges'] for r in accepted.values()),
        state_comparisons=sum(r['states'] for r in accepted.values()),fault_checks=sum(r['fault_checks'] for r in accepted.values()),
        integer_mismatches=0,recurrent_old_state_handoffs=sum(r['recurrent_old_state_handoffs'] for r in accepted.values()),
        simulations=list(accepted.values()),excluded_runs=excluded,
        inherited_full_identity_verified=True,full_433880_edge_rtl=False,synthesis=False,routed=False,board_io=0,
        limits=['No PS/HP0 hardware or DDR throughput measurement','No full-H graph RTL simulation',
            'No AXI-Lite/DMA/candidate DDR writeback','old_state_tag is an echo, not hardware SHA256',
            'Ordered rotate-XOR signature is not cryptographic authentication',
            'GPU-R/PL unified old-state and COMMIT coordinator not connected',
            'Arithmetic faults 16-20 include deliberate local ROM/RAM injections, not original FlyVis stimuli'])
    out=HERE/'RTL_STREAM_SMALL_PASS.json';out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    mem=MemoryStatus();mem.length=ctypes.sizeof(mem)
    ok=ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(mem))
    processes=subprocess.run(['pwsh','-NoProfile','-Command',"Get-Process -Name vivado,xsim,xelab,xvlog,vitis_hls -ErrorAction SilentlyContinue | Select-Object ProcessName,Id | ConvertTo-Json -Compress"],capture_output=True,text=True)
    p=json.loads(processes.stdout) if processes.stdout.strip() else []
    gate=dict(date_local=datetime.now(timezone(timedelta(hours=8))).isoformat(),available_MiB=round(mem.avail_phys/2**20,2) if ok else None,
        total_MiB=round(mem.total_phys/2**20,2) if ok else None,eda_processes=p,cpu_percent=None,
        threshold_MiB=4096,threshold_source='workstream conservative policy, not vendor minimum',
        status='NOT_REQUESTED_FIRST_MILESTONE_STOP',synthesis_started=False,
        future_gate='Refresh memory/CPU and confirm staggered EDA slot with A before OOC')
    (HERE/'RESOURCE_SNAPSHOT.json').write_text(json.dumps(gate,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('status','positive_requests','ordered_edge_comparisons','state_comparisons','fault_checks','integer_mismatches')}))
    print(json.dumps(gate))
if __name__=='__main__':main()
