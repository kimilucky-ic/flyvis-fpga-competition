# Read-only: no PYNQ, MMIO, DMA, socket, signal or process shutdown.
# Run this whole cell in the CURRENT FlyVis Notebook. Do not rerun preparation.
import json
import os
import re
from pathlib import Path


def kernel_process(pid, proc=Path('/proc')):
    root = proc / str(pid)
    try:
        args = (root / 'cmdline').read_bytes().split(b'\0')
        status = dict(line.split(':', 1) for line in (root / 'status').read_text().splitlines() if ':' in line)
        parent = int(status['PPid'].strip())
    except (OSError, ValueError, KeyError):
        return dict(pid=pid, status='ABSENT_OR_CHANGED_READ_ONLY')
    kernel_files = []
    for arg in args:
        match = re.search(rb'kernel-([0-9a-fA-F-]{36})\.json$', arg)
        if match:
            kernel_files.append('kernel-' + match.group(1).decode('ascii') + '.json')
    # The existing gate uses substring matching. Report the actual argv-token
    # distinction, without exposing complete command arguments or credentials.
    exact_launcher = any(arg in (b'ipykernel_launcher', b'ipykernel_launcher.py')
        or arg.endswith(b'/ipykernel_launcher.py') for arg in args)
    try:
        parent_status = dict(line.split(':', 1) for line in (proc / str(parent) / 'status').read_text().splitlines() if ':' in line)
        parent_name = parent_status.get('Name', '').strip()
    except OSError:
        parent_name = None
    return dict(pid=pid, parent_pid=parent, process_name=status.get('Name', '').strip(),
        state=status.get('State', '').strip(), parent_process_name=parent_name,
        kernel_files=kernel_files, gate_substring_match=any(b'ipykernel_launcher' in arg for arg in args),
        exact_launcher_argument=exact_launcher, complete_command_arguments_omitted=True)


def diagnostic(target=18092, proc=Path('/proc'), current=None):
    current = os.getpid() if current is None else current
    return dict(schema='flyvis-readonly-one-kernel-diagnostic/v1',
        current=kernel_process(current, proc), target=kernel_process(target, proc),
        target_is_current=target == current,
        operations='READ_PROC_ONLY_NO_SHUTDOWN_NO_HARDWARE',
        interpretation='Extra PID is not proof of board use. Running shows only its own Jupyter server.')


if __name__ == '__main__':
    print('FLYVIS_KERNEL_CHECK ' + json.dumps(diagnostic(), ensure_ascii=False, sort_keys=True))
