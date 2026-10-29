# This cell reads existing Python objects and filesystem identity only.
# No MMIO, DMA, FPGA programming, reset, new kernel or listener.
import json as _l4_json
import hashlib as _l4_hash
from pathlib import Path as _l4_Path
from ipykernel.connect import get_connection_file as _l4_kernel
_l4_inventory = []
for _l4_name, _l4_object in list(globals().items()):
    if _l4_name.startswith('_l4_'):
        continue
    _l4_fields = getattr(_l4_object, '__dict__', {})
    if not isinstance(_l4_fields, dict) or 'driver' not in _l4_fields or 'config' not in _l4_fields:
        continue
    _l4_config = _l4_fields['config']
    if not isinstance(_l4_config, dict):
        continue
    _l4_driver = _l4_fields['driver']
    _l4_values = getattr(_l4_driver, '__dict__', {})
    _l4_image = _l4_values.get('overlay')
    _l4_bit = _l4_Path(_l4_image.bitfile_name) if _l4_image is not None else None
    _l4_inventory.append(dict(name=_l4_name, run_id=_l4_config.get('run_id'),
        server_session=_l4_config.get('server_session'), state=_l4_fields.get('state'),
        requests=_l4_values.get('requests'), commits=_l4_values.get('commits'),
        pending=_l4_values.get('pending') is not None, poisoned=_l4_values.get('poisoned'),
        service_thread_alive=bool(_l4_fields.get('thread') and _l4_fields['thread'].is_alive()),
        neural_thread_alive=bool(_l4_fields.get('neural_thread') and _l4_fields['neural_thread'].is_alive()),
        bit_path=str(_l4_bit), bit_sha256=_l4_hash.sha256(_l4_bit.read_bytes()).hexdigest() if _l4_bit and _l4_bit.is_file() else None,
        hwh_sha256=_l4_hash.sha256(_l4_bit.with_suffix('.hwh').read_bytes()).hexdigest() if _l4_bit and _l4_bit.with_suffix('.hwh').is_file() else None))
print('LINE4_FRESH_READONLY_IDENTITY ' + _l4_json.dumps(dict(
    kernel=_l4_Path(_l4_kernel()).name,
    boot=_l4_Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
    cwd=str(_l4_Path.cwd()), services=_l4_inventory,
    new_MMIO_reads=0, new_MMIO_writes=0, new_DMA=0, new_loads=0, new_resets=0), ensure_ascii=False))
