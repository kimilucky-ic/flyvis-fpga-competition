"""Bounded CPU-only checks: pure argv grammar and actual service lease method.

Graphics dependencies are stubbed before importing the new service; construction,
device enumeration, WSL subprocesses, network servers and cameras are never used.
"""
from pathlib import Path
from types import ModuleType, SimpleNamespace
import ast
import hashlib
import importlib.util
import json
import sys
import tempfile
import time
import psutil
import research_guard as guard

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def forbidden(*args, **kwargs):
    raise AssertionError('Graphics or source computation must not be used by this check')


def main():
    evidence = HERE / 'evidence'
    evidence.mkdir(exist_ok=True)
    proc = psutil.Process()
    proc.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    proc.cpu_affinity(proc.cpu_affinity()[:2])
    scene = ModuleType('scene')
    scene.AnatomyScene = scene.configure_renderer = forbidden
    presentation = ModuleType('presentation')
    presentation.verified_identity = presentation.fixed_type_palette = forbidden
    presentation.sha = sha
    sys.modules['scene'] = scene
    sys.modules['presentation'] = presentation
    spec = importlib.util.spec_from_file_location('guarded_live_service', HERE / 'service.py')
    service = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(service)
    assert 'wgpu' not in sys.modules and 'navis' not in sys.modules and 'octarine' not in sys.modules
    query = ['wsl.exe', '-d', 'FlyVisCPU', '--exec', 'nvidia-smi',
             '--query-compute-apps=pid,process_name,used_gpu_memory', '--format=csv,noheader']
    ps = ['C:\\Windows\\System32\\wsl.exe', '--distribution', 'FlyVisCPU', '-e', '/bin/ps', '-eo', 'pid,etime,args']
    shell = ['wsl.exe', '-d', 'FlyVisCPU', '--exec', '/bin/sh', '-c',
             'nvidia-smi --query-compute-apps=pid,process_name,used_gpu_memory --format=csv,noheader; ps -eo pid,etime,args | grep -E "live_worker|render|python" | head -25']
    cases = [
        ('explicit_compute_app_query', query, True),
        ('explicit_process_query', ps, True),
        ('reported_compound_shell_still_unknown', shell, False),
        ('extra_command_arg', query + ['; python live_worker.py'], False),
        ('gpu_mutation_flag', query[:5] + ['--gpu-reset'], False),
        ('output_file_flag', query + ['--filename=output.txt'], False),
        ('worker_command', query[:4] + ['python3', 'live_worker.py'], False),
        ('no_exec_uses_default_shell', ['wsl.exe', '-d', 'FlyVisCPU', 'ps', '-eo', 'pid,etime,args'], False),
        ('interactive_unknown', ['wsl.exe'], False),
        ('missing_command_line', None, False),
    ]
    grammar = []
    for name, argv, expected in cases:
        answer = guard.wsl_diagnostic(argv)
        assert bool(answer) == expected, name
        grammar.append(dict(case=name,diagnostic=answer))
    identity = dict(pid=proc.pid, create_time=proc.create_time())
    def row(argv=query, **kw):
        return dict(identity, name='wsl.exe', cmdline=argv, **kw)
    for bad in (dict(row(), create_time=None), dict(row(), identity_changed=True)):
        kind, value = guard.classify_process(bad)
        assert kind == 'busy' and not guard.same_instance(value, identity)
    assert guard.classify_process(dict(identity,name='vivado.exe',cmdline=['vivado.exe']))[0]=='busy'
    assert guard.classify_process(dict(identity,name='python.exe',cmdline=['python.exe','live_worker.py']))[0]=='busy'
    results = []
    with tempfile.TemporaryDirectory(prefix='guard_fixture_',dir=evidence) as temporary:
        tmp = Path(temporary).resolve()
        assert tmp.is_relative_to(evidence.resolve())
        marker_dir = tmp/'markers'
        marker_dir.mkdir()
        base_lease = dict(schema='line10.gpu_coordinator.v1', parent_pid=proc.pid,
                          parent_create_time=proc.create_time(),session_id='CPU_GUARD_FIXTURE',
                          expires_unix=time.time()+60,allowed_processes=[])
        def check(name, rows=(), marker=None, changes=None, allow=False, expected=None, bind_session='CPU_GUARD_FIXTURE', owner_alive=True):
            lease = dict(base_lease)
            if allow:lease['allowed_processes']=[identity]
            if changes:lease.update(changes)
            path = tmp/'lease.json'
            path.write_text(json.dumps(lease),encoding='utf-8')
            if marker:(marker_dir/marker).write_text('fixture only',encoding='utf-8')
            obj = service.LiveRaw.__new__(service.LiveRaw)
            obj.args = SimpleNamespace(renderer='gpu',parent_pid=proc.pid,gpu_lease_file=path)
            obj.parent = proc if owner_alive else SimpleNamespace(is_running=lambda:False)
            obj.parent_created = proc.create_time()
            obj.binding = dict(session_id=bind_session)
            obj.last_guard=0.; obj.stopping=False; obj.lease=None; obj.guard_state=None; obj.guard_audit_signature=None
            events=[]; obj.log=lambda **v:events.append(v)
            service.research_guard=lambda:guard.research_guard(processes=rows,markers_dir=marker_dir)
            error=None
            try:obj.check_resources(force=True)
            except service.YieldResources as exc:error=str(exc)
            if marker:(marker_dir/marker).unlink()
            assert (error is None) == (expected is None),(name,error,expected)
            if expected:assert expected in error and obj.stopping,(name,error)
            results.append(dict(case=name,passed=True,allowed=error is None,error=error,
                                guard_snapshot=obj.guard_state,audit_events=events))
        check('known_readonly_is_not_busy',rows=[row(),row(ps)])
        check('unknown_wsl_blocks',rows=[row(shell)],expected='EXTERNAL_RESEARCH_BUSY')
        check('same_owned_worker_identity_exempt',rows=[row(['wsl.exe','--exec','python','live_worker.py'])],allow=True)
        check('same_pid_different_snapshot_creation_blocks',rows=[dict(row(shell),create_time=proc.create_time()+1)],allow=True,expected='EXTERNAL_RESEARCH_BUSY')
        check('unreadable_wsl_cannot_receive_exemption',rows=[dict(row(),cmdline=None,create_time=None)],allow=True,expected='EXTERNAL_RESEARCH_BUSY')
        check('marker_blocks_even_known_diagnostic',rows=[row()],marker='EXTERNAL_GPU_BUSY.json',expected='EXTERNAL_RESEARCH_BUSY')
        check('expired_lease_blocks',changes={'expires_unix':time.time()-1},expected='GPU_LEASE_EXPIRED')
        check('session_mismatch_blocks',bind_session='OTHER_SESSION',expected='GPU_LEASE_BOUND_SESSION')
        check('wrong_owner_creation_blocks',changes={'parent_create_time':proc.create_time()+1},expected='GPU_LEASE_OWNER')
        check('reused_allowed_pid_blocks',changes={'allowed_processes':[dict(identity,create_time=proc.create_time()+1)]},expected='GPU_LEASE_PID_REUSED')
        check('owner_exit_blocks',owner_alive=False,expected='OWNER_PARENT_CLOSED')
        # One actual Windows process snapshot, no WSL command or GPU API is executed.
        started=time.perf_counter()
        actual=guard.research_guard()
        actual_ms=(time.perf_counter()-started)*1000
    before=ast.parse((ROOT/'live_raw_20261015/service.py').read_text(encoding='utf-8'))
    after=ast.parse((HERE/'service.py').read_text(encoding='utf-8'))
    def methods(tree):
        return {f'{c.name}.{m.name}':ast.dump(m,include_attributes=False) for c in tree.body
                if isinstance(c,ast.ClassDef) for m in c.body if isinstance(m,ast.FunctionDef)}
    old,new=methods(before),methods(after)
    changed=[name for name in old if old[name]!=new[name]]
    assert changed==['LiveRaw.init__','LiveRaw.check_resources','LiveRaw.health'],changed
    frozen=json.loads((HERE/'preserved_sources.json').read_text(encoding='utf-8'))
    for item in frozen:assert sha(Path(item['path']))==item['sha256'],item['path']
    result=dict(status='PASS_CPU_ONLY_GUARD_AND_LEASE_CHECKS',policy=guard.POLICY,
        grammar_cases=grammar,identity_missing_or_changed_blocks=True,lease_cases=results,
        actual_readonly_windows_snapshot=actual,actual_snapshot_ms=actual_ms,
        changed_service_methods=changed,frozen_sources_unchanged=frozen,
        source_sha256={p.name:sha(p) for p in (HERE/'service.py',HERE/'research_guard.py',Path(__file__))},
        evidence_level='CPU_CLASSIFICATION_AND_LEASE_METHOD_CHECKS',
        graphics_modules_imported=False,renderer_started=False,WSL_command_executed=False,
        GPU_query_executed=False,neural_compute=False,camera_opened=False,PL_execution=False,
        limitation='The observed PID 42460 was not captured with argv/create_time. No causal PID-command identity or live 60-second retest is claimed.')
    (evidence/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(dict(status=result['status'],grammar_cases=len(grammar),lease_cases=len(results),
                         actual_snapshot_ms=actual_ms,source_sha256=result['source_sha256'])))


if __name__=='__main__':main()
