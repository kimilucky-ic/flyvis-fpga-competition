# READ ONLY: no programming, reset, MMIO, DMA, GPU or camera.
import json, os, hashlib
from pathlib import Path
from ipykernel.connect import get_connection_file
from pynq import Device
_joint_pair = Path('/home/xilinx/jupyter_notebooks/flyvis_t5c67_v1/A3R1_FRESH_READY3_05aa0e5238e14b3aad54bb695882d043/neuron_a.bit')
_joint_inventory = {
    'boot_id': Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
    'kernel_file': Path(get_connection_file()).name,
    'pid': os.getpid(), 'cwd': str(Path.cwd()),
    'loaded_bitfile_metadata': str(getattr(Device.active_device, 'bitfile_name', None)),
    'candidate_files': [], 'kernel_processes': [],
    'existing_service_names': [n for n, v in list(globals().items()) if n.endswith('_service_instance')],
}
for _p in (_joint_pair, _joint_pair.with_suffix('.hwh')):
    _joint_inventory['candidate_files'].append({'path': str(_p), 'exists': _p.is_file(), 'sha256': hashlib.sha256(_p.read_bytes()).hexdigest() if _p.is_file() else None})
for _p in Path('/proc').iterdir():
    if _p.name.isdigit():
        try:
            _args = (_p / 'cmdline').read_bytes().split(b'\0')
            if any(b'ipykernel_launcher' in a for a in _args):
                _joint_inventory['kernel_processes'].append({'pid': int(_p.name), 'kernel_files': [a.decode() for a in _args if b'kernel-' in a and a.endswith(b'.json')]})
        except OSError:
            pass
print('LINE2_CURRENT_READONLY ' + json.dumps(_joint_inventory, sort_keys=True))
