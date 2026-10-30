"""Read-only process classification for the owned live graphics service.

No subprocess, WSL invocation, GPU query, renderer import or process mutation.
Only explicit WSL --exec diagnostic argv are exempt; shell scripts stay unknown.
This is a conservative scheduling heuristic, not a GPU occupancy/security proof.
"""
from pathlib import Path
import hashlib
import json
import math
import re
import psutil

ROOT = Path(__file__).resolve().parent.parent
MARKERS_DIR = ROOT.parents[2] / 'fpga/flyvis-autorunner/runtime'
MARKERS = ('EXTERNAL_GPU_BUSY.json', 'BOARD_RESERVED.json', 'RESOURCE_QUARANTINE.json')
POLICY = 'line10.wsl_readonly_argv.v1'
WORKER_HINTS = ('--worker', 'single_controller.py --execute', 'live_worker.py', 'camera_stream_worker.py')


def finite_time(value):
    return type(value) in (int, float) and math.isfinite(value) and value > 0


def same_instance(row, allowed):
    """Both sampled process creation time and PID must match the coordinator."""
    return (row.get('pid') == allowed.get('pid') and finite_time(row.get('create_time'))
            and finite_time(allowed.get('create_time'))
            and abs(row['create_time'] - allowed['create_time']) <= 1e-5)


def wsl_diagnostic(argv):
    """Recognize a small, complete argv grammar; never parse arbitrary shell text."""
    if not isinstance(argv, (list, tuple)) or not argv or not all(isinstance(v, str) for v in argv):
        return None
    if argv[0].replace('\\', '/').rsplit('/', 1)[-1].lower() != 'wsl.exe':
        return None
    i = 1
    if i < len(argv) and argv[i] in ('-d', '--distribution'):
        if i + 1 >= len(argv) or not re.fullmatch(r'[A-Za-z0-9_.-]{1,128}', argv[i + 1]):
            return None
        i += 2
    if i >= len(argv) or argv[i] not in ('--exec', '-e'):
        return None
    command = argv[i + 1:]
    if not command:
        return None
    executable, arguments = command[0], tuple(command[1:])
    if executable in ('nvidia-smi', '/usr/bin/nvidia-smi', '/usr/lib/wsl/lib/nvidia-smi'):
        if arguments == ('--query-compute-apps=pid,process_name,used_gpu_memory', '--format=csv,noheader'):
            return 'WSL_READONLY_COMPUTE_APPS_QUERY'
    if executable in ('ps', '/bin/ps', '/usr/bin/ps'):
        if arguments in (('-eo', 'pid,etime,args'), ('-eo', 'pid,ppid,etime,args')):
            return 'WSL_READONLY_PROCESS_QUERY'
    return None


def classify_process(row):
    """Return (busy|diagnostic|irrelevant, auditable record) from one snapshot."""
    name = (row.get('name') or '').lower()
    argv = row.get('cmdline')
    argv_valid = isinstance(argv, (list, tuple)) and all(isinstance(v, str) for v in argv)
    cmd = ' '.join(argv) if argv_valid else ''
    record = dict(pid=row['pid'], name=name, create_time=row.get('create_time'))
    record['cmdline_sha256'] = (hashlib.sha256(json.dumps(argv, ensure_ascii=False,
                                  separators=(',', ':')).encode('utf-8')).hexdigest() if argv_valid else None)
    if name == 'wsl.exe':
        diagnostic = wsl_diagnostic(argv)
        if diagnostic and finite_time(record['create_time']) and not row.get('identity_changed'):
            return 'diagnostic', dict(record, reason=diagnostic, diagnostic_argv=list(argv))
        reason = 'WSL_IDENTITY_UNAVAILABLE' if not finite_time(record['create_time']) else 'UNKNOWN_OR_WORK_WSL'
    elif name in ('vivado.exe', 'vitis.exe'):
        reason = 'EDA_RESEARCH_PROCESS'
    elif name.startswith('python') and (not cmd or any(h in cmd for h in WORKER_HINTS)):
        reason = 'UNKNOWN_PYTHON_COMMAND' if not cmd else 'KNOWN_RESEARCH_WORKER'
    else:
        return 'irrelevant', record
    if row.get('identity_changed'):
        reason = 'PROCESS_IDENTITY_CHANGED_DURING_SNAPSHOT'
        record['create_time'] = None  # A stale PID cannot receive a lease exemption.
    return 'busy', dict(record, reason=reason)


def research_guard(*, processes=None, markers_dir=MARKERS_DIR):
    busy, diagnostics = [], []
    if processes is None:
        # Windows command-line inspection is costly; inspect only relevant names.
        processes = psutil.process_iter(['name'])
    for process in processes:
        try:
            if isinstance(process, dict):
                row = process
            else:
                row = dict(process.info, pid=process.pid)
                name = (row.get('name') or '').lower()
                if name not in ('wsl.exe', 'vivado.exe', 'vitis.exe') and not name.startswith('python'):
                    continue
                with process.oneshot():
                    row['create_time'] = process.create_time()
                    row['cmdline'] = process.cmdline()
                # Reject PID reuse during collection; an exited process has no resource to reserve.
                current = psutil.Process(process.pid).create_time()
                row['identity_changed'] = not finite_time(row.get('create_time')) or abs(current - row['create_time']) > 1e-5
            kind, record = classify_process(row)
            if kind == 'busy':
                busy.append(record)
            elif kind == 'diagnostic':
                diagnostics.append(record)
        except psutil.NoSuchProcess:
            continue
        except psutil.AccessDenied:
            name = (process.info.get('name') or '').lower()
            if name in ('wsl.exe', 'vivado.exe', 'vitis.exe') or name.startswith('python'):
                busy.append(dict(pid=process.pid, name=name, create_time=None,
                                 cmdline_sha256=None, reason='PROCESS_INSPECTION_DENIED'))
    markers = [name for name in MARKERS if (Path(markers_dir) / name).exists()]
    return dict(policy=POLICY, busy=busy, markers=markers, readonly_diagnostics=diagnostics,
                free_bytes=psutil.virtual_memory().available)
