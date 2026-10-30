"""Bounded software-only comparison of production adapters. No device operation."""
import argparse,copy,hashlib,http.client,importlib.util,json,os,secrets,statistics,sys,threading,time,uuid
from pathlib import Path
from unittest.mock import patch

OUT=Path(__file__).resolve().parent;GUI=OUT.parents[1];sys.path.insert(0,str(GUI))
from live_protocol import load,sha,host_path
from joint_diagnostics import JointDiagnostics
from joint_camera_preparation import PCClockClient,PreparationAuthority,clock_binding
from joint_camera_control import hardware_module

def write(name,value):(OUT/name).write_text(json.dumps(value,indent=2,ensure_ascii=False),encoding='utf8')
def stats(rows):
    a=sorted(r['wall_ms'] for r in rows)
    return dict(count=len(a),p50_ms=statistics.median(a),p95_ms=a[int(.95*(len(a)-1))],max_ms=a[-1])

def files():
    assert os.name=='posix','WSL CPU-only file comparison'
    from hybrid_full485 import Full485Contract
    from live_protocol import Registry
    from joint_camera_controller import source_pins
    from joint_runtime_audit import prepare_runtime_files
    c,reg=Full485Contract(),Registry();root=OUT/('cpu_files_case_'+uuid.uuid4().hex);root.mkdir(exist_ok=False)
    scope=dict(source_sha256=source_pins(),evidence='CPU_ONLY_NONEXECUTABLE')
    session=dict(evidence='CPU_ONLY_NONEXECUTABLE');h=dict(evidence='CPU_ONLY_NO_BOARD')
    for name,v in (('scope.json',scope),('session.json',session),('hardware_handoff.json',h)):
        (root/name).write_text(json.dumps(v),encoding='utf8')
    scope_sha,hsha=sha(root/'scope.json'),sha(root/'hardware_handoff.json')
    guard=prepare_runtime_files(root,scope,scope_sha,session,hsha,c,reg)
    def old():
        assert sha(root/'scope.json')==scope_sha and load(root/'session.json')==session
        assert sha(root/'hardware_handoff.json')==hsha
        for name,expected in scope['source_sha256'].items():
            p=(GUI/name).resolve();assert p.is_relative_to(GUI) and sha(p)==expected
        c.unchanged();reg.unchanged()
    actual=Path.stat;rows=[]
    for iteration in range(6):
        order=('before','after') if iteration%2==0 else ('after','before')
        for mode in order:
            counted=[]
            def stat(path,*a,**kw):counted.append(path);return actual(path,*a,**kw)
            start=time.perf_counter_ns();cpu=time.thread_time_ns()
            with patch.object(Path,'stat',stat):(old if mode=='before' else guard.check)()
            rows.append(dict(mode=mode,iteration=iteration,wall_ms=(time.perf_counter_ns()-start)/1e6,
                thread_cpu_ms=(time.thread_time_ns()-cpu)/1e6,Path_stat_calls=len(counted)))
    proof=guard.final()
    write('CPU_FILE_COMPARE.json',dict(status='PASS_PRODUCTION_AUDIT_CPU_ONLY',summary={m:dict(stats([r for r in rows if r['mode']==m]),
        Path_stat_calls=sorted(set(r['Path_stat_calls'] for r in rows if r['mode']==m))) for m in ('before','after')},
        audit=proof,rows=rows,model_steps=0,torch_imported='torch' in sys.modules,
        limits='Warm-cache file-check slice; excludes clock and GPU, not end-to-end speedup'))
    assert 'torch' not in sys.modules
    print(json.dumps(load(OUT/'CPU_FILE_COMPARE.json')['summary']),flush=True)

def server(host):
    prior=load(GUI/'runtime/joint/34e96b4d227f488bb3214190089569d1/hardware_handoff.json')
    h={k:copy.deepcopy(prior[k]) for k in ('software_package','control_package','software_sha256')}
    scope=dict(run_id='CPU_ONLY_NO_NEURAL_SESSION',server_session='CPU_ONLY',boot_id='NO_BOARD',start_utc='CPU',end_utc='CPU')
    h.update(**scope,listener_id='CPU_ONLY',plan_sha256='0'*64,
        pc_authority_endpoint=dict(host=host,port=18795),control_config=dict(control_key=secrets.token_hex(32)))
    a=PreparationAuthority.__new__(PreparationAuthority);a.helpers=hardware_module(h,'control2')
    a.clock=hardware_module(h,'clock').PCClockAuthority();a.lock=threading.RLock();a.error=None;a.seen=set()
    a.config=h['control_config'];a.binding=clock_binding(h,scope,'0'*64);a.declaration=h
    h['pc_clock_id']=a.clock.id;a.start()
    write('CPU_HTTP_CONFIG_PRIVATE.json',dict(handoff=h,scope=scope))
    print('CPU_PRODUCTION_GUARD_READY '+host,flush=True)
    until=time.monotonic()+110
    try:
        while time.monotonic()<until and not (OUT/'CPU_HTTP_DONE.json').exists():
            if (OUT/'CPU_HTTP_REVOKE.json').exists() and a.error is None:
                a.error='CPU_REVOCATION_INJECTED';write('CPU_HTTP_REVOKED.json',dict(status='CPU_ONLY_REVOKED'))
            time.sleep(.05)
    finally:
        a.close();write('CPU_HTTP_SERVER_CLOSED.json',dict(status='CLOSED',verified_requests=len(a.seen),device_requests=0))

def client():
    p=OUT/'before_sources/joint_camera_preparation.py';spec=importlib.util.spec_from_file_location('before_clock_client_20261017',p)
    old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
    conf=load(OUT/'CPU_HTTP_CONFIG_PRIVATE.json');h,scope=conf['handoff'],conf['scope'];d=JointDiagnostics('CPU_PRODUCTION_CLOCK')
    results={};new=None
    try:
        for mode,cls in (('before',old.PCClockClient),('after',PCClockClient)):
            checker=cls(h,scope,'0'*64,**({'diagnostics':d} if mode=='after' else {}));rows=[]
            for i in range(320):
                start=time.perf_counter_ns();checker.check();rows.append(dict(ordinal=i+1,wall_ms=(time.perf_counter_ns()-start)/1e6));time.sleep(.02)
            results[mode]=dict(summary=stats(rows),rows=rows)
            if mode=='after':new=checker
        write('CPU_HTTP_REVOKE.json',dict(reason='CPU_ONLY_DISCONNECT_TEST'))
        deadline=time.monotonic()+3
        while not (OUT/'CPU_HTTP_REVOKED.json').exists():
            if time.monotonic()>deadline:raise TimeoutError('CPU_REVOKE_TIMEOUT')
            time.sleep(.01)
        failures=[]
        for _ in range(2):
            try:new.check()
            except ValueError as error:failures.append(str(error))
        assert len(failures)==2 and new.failed
        new.close();d.save(OUT/'CPU_CLOCK_PHASES.json','CPU_ONLY','CPU_ONLY')
        names={r['name']:sum(s['name']==r['name'] for s in d.rows) for r in d.rows}
        assert names['clock.connect']==1 and names['clock.verify_response']==320
        write('CPU_HTTP_COMPARE.json',dict(status='PASS_PRODUCTION_REUSED_CLOCK_CPU_ONLY',variants=results,
            phase_counts=names,revocation_errors=failures,automatic_reconnection=False,
            neural_steps=0,board_connections=0,limits='Windows-WSL virtual adapter; does not reproduce the old physical-address stall'))
        print(json.dumps(dict(status='PASS',summary={m:v['summary'] for m,v in results.items()},phase_counts=names)),flush=True)
    finally:
        if new:new.close()
        write('CPU_HTTP_DONE.json',dict(status='CPU_TEST_FINISHED'))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--files',action='store_true');p.add_argument('--server');p.add_argument('--client',action='store_true');a=p.parse_args()
    if a.files:files()
    elif a.server:server(a.server)
    elif a.client:client()
