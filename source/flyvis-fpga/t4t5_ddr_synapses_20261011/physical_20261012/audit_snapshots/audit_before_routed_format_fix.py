"""Read-only OOC physical evidence audit. Timing failures stay failures."""
from pathlib import Path
from collections import Counter
import sys,json,re,csv,hashlib,psutil
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P.parent))
from audit_ramfix_ooc_20261012 import utilization
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return p.read_text(encoding='utf-8',errors='replace')
def save(p,d):p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def timing(p):
    if not p.exists():return None
    lines=read(p).splitlines();idx=next(i for i,l in enumerate(lines) if l.strip().startswith('WNS(ns)'))
    vals=lines[idx+2].split();assert len(vals)==12
    keys=('WNS_ns','TNS_ns','setup_failing_endpoints','setup_total_endpoints','WHS_ns','THS_ns','hold_failing_endpoints','hold_total_endpoints','WPWS_ns','TPWS_ns','pulse_failing_endpoints','pulse_total_endpoints')
    return {k:float(v) if k.endswith('_ns') else int(v) for k,v in zip(keys,vals)}
def violations(p):
    if not p.exists():return None
    with p.open(encoding='utf-8',newline='') as f:rows=list(csv.DictReader(f,delimiter='\t'))
    classes=Counter((r['kind'],r['startpoint_class'],r['endpoint_class']) for r in rows)
    return dict(paths=len(rows),class_counts={'|'.join(k):v for k,v in classes.items()},scope='One worst path per endpoint, negative slack only, cap10000')
def main():
    identity=load(P/'INPUT_IDENTITY.json');gate=load(P/'LATEST_RESOURCE_GATE.json') if (P/'LATEST_RESOURCE_GATE.json').exists() else None
    result=dict(evidence_level='STATIC_PREPARATION',status='READY_AUTHORIZED_PHYSICAL_NOT_RUN' if gate and gate.get('allow_concurrent_vivado') else 'READY_WAITING_A_EDA_RELEASE',new_fullgraph_RTL_runs=0,new_synthesis_runs=0,new_physical_attempts=0,
        previous_OOC_resources=load(P.parent/'pipeline_a_20261012/OOC_RESULT.json')['utilization_scopes']['top'],
        previous_OOC_timing=load(P.parent/'pipeline_a_20261012/OOC_RESULT.json')['timing'],
        clock_context=identity['physical_target'],gate=gate,new_routed_resources=None,new_routed_timing=None,measured_HP0_MBps=None,
        limits=['BUFG site borrowed from a read-only local reference, not B SoC clock proof','All physical IO budgets remain abstract max2/min0','No SoC, BIT, physical board or GPU'])
    if not (P/'LAUNCH_RECORD.json').exists():
        if gate and not gate['allowed']:
            result['status']='READY_BLOCKED_RESOURCE_GATE' if not gate['capacity_allowed'] else 'READY_BLOCKED_PROCESS_OR_SERIAL_GATE'
            result['not_launched_reasons']=gate['reasons']
        save(P/'PHYSICAL_RESULT.json',result);print(json.dumps({k:result[k] for k in ('status','evidence_level','new_physical_attempts')},indent=2));return
    run=P/load(P/'LAUNCH_RECORD.json')['run'];ident=load(run/'RUN_IDENTITY.json');rt=load(run/'RUNTIME.json')
    assert sha(P/'INPUT_IDENTITY.json')==ident['input_identity_sha256']
    assert sha(run/'input_synthesis.dcp')==identity['dcp_sha256']
    for n,k in [('context.xdc','context_sha256'),('implement.tcl','tcl_sha256')]:assert sha(run/n)==ident[k]
    log=read(run/'vivado.log') if (run/'vivado.log').exists() else ''
    tool_identity_verified='SW Build 6605303' in log
    completed=tool_identity_verified and rt['exit_code']==0 and rt['stop_reason'] is None and 'B433880_SINGLE_OOC_PHYSICAL_ATTEMPT_COMPLETE' in log and not re.search(r'^ERROR:',log,re.M)
    stage=dict(l.split('=',1) for l in read(run/'stage_identity.txt').splitlines() if '=' in l) if (run/'stage_identity.txt').exists() else None
    timings={k:timing(run/f'timing_{k}.rpt') for k in ('context','placed','routed')}
    u=utilization(run/'utilization_routed.rpt') if (run/'utilization_routed.rpt').exists() else None
    counts={}
    if (run/'primitive_cells.tsv').exists():
        with (run/'primitive_cells.tsv').open(encoding='utf-8',newline='') as f:rows=list(csv.DictReader(f,delimiter='\t'))
        counts=Counter(r['ref_name'] for r in rows)
        assert u['RAMB36']==counts['RAMB36E1'] and u['RAMB18']==counts['RAMB18E1'] and u['DSP']==counts['DSP48E1']
        assert u['FF']==sum(v for k,v in counts.items() if k.startswith('FD')) and u['latches']==0
    route=read(run/'route_status.rpt') if (run/'route_status.rpt').exists() else ''
    route_metrics={k.strip():int(v) for k,v in re.findall(r'^\s*(.*?)\s*:\s*(\d+)\s*$',route,re.M) if k.strip()}
    drc=read(run/'drc_routed.rpt') if (run/'drc_routed.rpt').exists() else ''
    drc_rules=[]
    for l in drc.splitlines():
        cols=[x.strip() for x in l.strip().strip('|').split('|')]
        if len(cols)>=4 and re.fullmatch(r'[A-Z][A-Z0-9_-]+-\d+',cols[0]) and cols[-1].isdigit():
            drc_rules.append(dict(rule=cols[0],severity=cols[1],count=int(cols[-1])))
    checks={k:int(v) for k,v in re.findall(r'checking (\w+) \((\d+)\)',read(run/'check_routed.rpt'))} if (run/'check_routed.rpt').exists() else {}
    if completed:
        assert stage['stage']=='OOC_PLACED_ROUTED_NO_SOC_NO_BIT' and stage['part']=='xc7z020clg400-2' and stage['HD.CLK_SRC']=='BUFGCTRL_X0Y16'
        assert stage['clock_period_ns']=='10.000' and stage['general.maxThreads']=='1' and stage['black_boxes']=='0'
        assert len(checks)==12
        resolved=read(run/'routed_constraints.xdc')
        for cmd in ('set_false_path','set_multicycle_path','set_clock_groups'):assert not re.search(r'^\s*'+cmd+r'\b',resolved,re.M)
        for cmd in ('set_input_delay','set_output_delay'):
            assert re.search(cmd+r'[^\n]*-max 2(?:\.0+)?\b',resolved) and re.search(cmd+r'[^\n]*-min 0(?:\.0+)?\b',resolved)
    alive=[]
    for rec in rt['processes']:
        try:
            p=psutil.Process(rec['pid'])
            if abs(p.create_time()-rec['created'])<.01:alive.append(rec['pid'])
        except psutil.NoSuchProcess:pass
    assert not alive,alive
    t=timings['routed'];checks_clean=len(checks)==12 and all(v==0 for v in checks.values())
    timing_met=bool(completed and t and t['WNS_ns']>=0 and t['WHS_ns']>=0 and t['pulse_failing_endpoints']==0 and checks_clean)
    status='OOC_ROUTE_COMPLETE_TIMING_MET_CONTEXT_ONLY' if timing_met else 'OOC_ROUTE_COMPLETE_TIMING_FAIL' if completed else 'PHYSICAL_ATTEMPT_FAILED_OR_BOUNDED_STOP'
    result.update(status=status,evidence_level='OOC_PLACED_ROUTED' if completed else 'PARTIAL_PHYSICAL_ATTEMPT',new_physical_attempts=1,
        run=str(run.relative_to(P)),runtime=rt,completed=completed,tool_identity_verified=tool_identity_verified,new_routed_resources=u,new_routed_timing=t,
        timings_by_stage=timings,violation_classes={k:violations(run/f'{k}_violations.tsv') for k in timings},
        route_metrics=route_metrics,drc_rules=drc_rules,check_timing=checks,check_timing_clean=checks_clean,stage_identity=stage,primitive_counts=dict(counts),owned_processes_alive=alive,
        drc_error_count=sum(r['count'] for r in drc_rules if r['severity']=='Error'),
        acceptance_scope='Timing satisfaction is separate from route/DRC completeness; inspect both raw reports before integration',
        timing_met_in_declared_context=timing_met,validated_clock_MHz_in_declared_context=100 if timing_met else None,
        slack_based_period_estimate_ns=10-t['WNS_ns'] if t else None,
        slack_based_frequency_estimate_MHz=1000/(10-t['WNS_ns']) if t and 10-t['WNS_ns']>0 else None,
        actual_Fmax_MHz=None,errors=re.findall(r'^ERROR:[^\n]*',log,re.M),
        frequency_scope='100MHz is the single tested timing target under OOC assumptions; slack-derived estimate is not an Fmax search or board measurement',
        raw_sha256={p.name:sha(p) for p in run.iterdir() if p.is_file() and p.suffix in ('.rpt','.tsv','.log','.json','.xdc','.tcl','.dcp','.csv','.txt')})
    save(P/'PHYSICAL_RESULT.json',result)
    print(json.dumps({k:result[k] for k in ('status','completed','new_routed_resources','new_routed_timing','violation_classes','route_metrics','drc_rules','errors')},indent=2))
if __name__=='__main__':main()
