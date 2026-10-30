# READ ONLY. Run in the current START_DDR Notebook; do not rerun preparation.
# No PYNQ/MMIO/DMA imports, writes, process stops, resets or hardware calls.
import json
import os
import sys
import urllib.request
from pathlib import Path
from ipykernel.connect import get_connection_file


def line2_read_kernel_processes(proc=Path('/proc')):
    rows = []
    for p in proc.iterdir():
        if not p.name.isdigit():
            continue
        try:
            args = (p / 'cmdline').read_bytes().split(b'\0')
            # Exactly the criterion used by the original admission check.
            if not any(b'ipykernel_launcher' in a for a in args):
                continue
            status = dict(line.split(':', 1) for line in (p / 'status').read_text().splitlines() if ':' in line)
            rows.append(dict(pid=int(p.name),parent_pid=int(status['PPid'].strip()),
                process_name=status['Name'].strip(),state=status['State'].strip(),
                executable_name=Path(args[0].decode(errors='replace')).name,
                is_current=int(p.name) == os.getpid(),
                kernel_files=[a.decode(errors='replace') for a in args if b'kernel-' in a and a.endswith(b'.json')]))
        except (OSError, ValueError, KeyError):
            continue
    return sorted(rows, key=lambda row: row['pid'])


line2_diag_rows = line2_read_kernel_processes()
line2_diag_sessions = []
line2_diag_api = []
# Read metadata from the board's local Jupyter server. Tokens stay in memory
# and are never printed; these are GET requests only, with bounded timeouts.
line2_runtime = Path(get_connection_file()).resolve().parent
line2_server_files = sorted(set(line2_runtime.glob('nbserver-*.json')) | set(line2_runtime.glob('jpserver-*.json')))[:4]
for line2_server_file in line2_server_files:
    try:
        line2_server = json.loads(line2_server_file.read_text())
        line2_port = line2_server['port']
        assert type(line2_port) is int and 0 < line2_port < 65536
        line2_base = line2_server.get('base_url', '/')
        assert line2_base.startswith('/') and '?' not in line2_base and '#' not in line2_base
        line2_url = 'http://127.0.0.1:%d%sapi/sessions' % (line2_port, line2_base.rstrip('/') + '/')
        line2_request = urllib.request.Request(line2_url, method='GET')
        if line2_server.get('token'):
            line2_request.add_header('Authorization', 'token ' + line2_server['token'])
        with urllib.request.urlopen(line2_request, timeout=2) as line2_response:
            line2_sessions = json.loads(line2_response.read(262145))
        assert isinstance(line2_sessions, list)
        for line2_session in line2_sessions:
            line2_kernel = line2_session.get('kernel', {})
            line2_diag_sessions.append(dict(kernel_id=line2_kernel.get('id'),
                notebook=line2_session.get('path') or line2_session.get('notebook', {}).get('path'),
                execution_state_metadata=line2_kernel.get('execution_state'),
                connections_metadata=line2_kernel.get('connections')))
        line2_diag_api.append(dict(port=line2_port,status='READ_OK'))
    except Exception as line2_error:
        line2_diag_api.append(dict(server_file=line2_server_file.name,status='NOT_AVAILABLE',
            error_type=type(line2_error).__name__,http_status=getattr(line2_error, 'code', None)))
for line2_row in line2_diag_rows:
    line2_row['notebooks'] = sorted(set(s['notebook'] for s in line2_diag_sessions if s['notebook']
        and any('kernel-' + str(s['kernel_id']) + '.json' == Path(f).name for f in line2_row['kernel_files'])))
line2_diag_root = globals().get('line2_init_root')
line2_diag = dict(schema='line2-readonly-kernel-diagnostic/v1',current_pid=os.getpid(),
    current_kernel=Path(get_connection_file()).name,python=sys.executable,
    boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
    matched_processes=line2_diag_rows,notebook_sessions=line2_diag_sessions,jupyter_api=line2_diag_api,
    initialization_attempt_exists=(Path(line2_diag_root)/'INITIALIZATION_ATTEMPT.json').exists() if line2_diag_root else None,
    initialized_owner_present='line2_fresh_initialized' in globals(),
    pinned_handles=len(globals()['line2_initializer'].PINNED) if 'line2_initializer' in globals() else None,
    operations='READ_ONLY_NO_PROCESS_SHUTDOWN_NO_HARDWARE',
    note='No notebook mapping or idle metadata proves neither ownership nor permission to stop a process.')
print('LINE2_KERNEL_DIAGNOSTIC ' + json.dumps(line2_diag, ensure_ascii=False, sort_keys=True))
