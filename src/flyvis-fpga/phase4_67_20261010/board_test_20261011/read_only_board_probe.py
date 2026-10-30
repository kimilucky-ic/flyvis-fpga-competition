"""Read Linux files/package metadata only; no PYNQ import, Overlay or MMIO.

Run on the already booted board after the user approves its power/connection
step. This utility never loads a bitstream or changes the boot image.
"""
import argparse
import hashlib
import importlib.metadata as metadata
import json
import os
import platform
from pathlib import Path
import sys
import time


def read_text(path):
    try:
        return Path(path).read_bytes().decode('utf-8', errors='replace').replace('\x00', '\n').strip()
    except (OSError, PermissionError) as exc:
        return {'unavailable': '{}: {}'.format(type(exc).__name__, exc)}


def inspect_board():
    result = {
        'status': 'READ_ONLY_OS_AND_PACKAGE_SNAPSHOT_NO_PL_PROOF',
        'timestamp_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'board_io_operations': 0,
        'scope': 'Linux file reads and package metadata; no Overlay/MMIO/allocation/reset/download',
        'platform': platform.platform(),
        'python': sys.version,
        'python_executable': sys.executable,
        'uid': os.getuid() if hasattr(os, 'getuid') else None,
        'files': {},
        'pynq': {},
    }
    for path in (
        '/etc/os-release', '/proc/version', '/proc/meminfo', '/proc/cmdline',
        '/proc/sys/kernel/random/boot_id', '/proc/uptime', '/proc/iomem',
        '/sys/firmware/devicetree/base/model',
        '/sys/firmware/devicetree/base/compatible',
        '/sys/class/fpga_manager/fpga0/state',
        '/sys/class/fpga_manager/fpga0/name',
    ):
        result['files'][path] = read_text(path)
    try:
        distribution = metadata.distribution('pynq')
        result['pynq']['version'] = distribution.version
        result['pynq']['source_files'] = {}
        for rel in ('pynq/overlay.py', 'pynq/bitstream.py', 'pynq/pl_server/embedded_device.py',
                    'pynq/pl_server/device.py', 'pynq/pl_server/hwh_parser.py', 'pynq/buffer.py'):
            source = Path(distribution.locate_file(rel))
            if source.is_file():
                raw = source.read_bytes()
                result['pynq']['source_files'][rel] = {
                    'path': str(source), 'sha256': hashlib.sha256(raw).hexdigest(),
                    'text': raw.decode('utf-8', errors='replace'),
                }
    except metadata.PackageNotFoundError:
        result['pynq']['version'] = None
        result['pynq']['error'] = 'PYNQ is not registered in this Python environment'
    result['unverified'] = ['physical board/core revision and DDR markings',
                            'current PL configuration identity',
                            'live AXI/HP0 compute functionality']
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    snapshot = inspect_board()
    # Exclusive creation preserves earlier snapshots.
    with args.output.open('x', encoding='utf-8') as stream:
        json.dump(snapshot, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps({k: v for k, v in snapshot.items() if k != 'files' and k != 'pynq'}, indent=2))
    print('PYNQ_VERSION:', snapshot['pynq'].get('version'))
    print('SNAPSHOT:', str(args.output.resolve()))
