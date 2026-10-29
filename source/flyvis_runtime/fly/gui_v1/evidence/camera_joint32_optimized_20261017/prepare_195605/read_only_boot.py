# LINE2 当前启动核对：只读；不加载、不复位、不分配、不启动服务
import json,sys,hashlib
from pathlib import Path
from importlib.metadata import version,PackageNotFoundError
from ipykernel.connect import get_connection_file
line2_boot_info=dict(schema='flyvis-current-boot-software-inventory/v1',
    boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
    kernel_file=Path(get_connection_file()).name,python=sys.executable,cwd=str(Path.cwd()),
    existing_owners=[],neural_or_control_listeners=[],kernel_processes=[],image_files=[],
    new_MMIO_reads=0,new_MMIO_writes=0,new_DMA=0,new_loads=0,new_resets=0,new_allocations=0)
try:line2_boot_info['pynq_version_metadata']=version('pynq')
except PackageNotFoundError:line2_boot_info['pynq_version_metadata']='NOT_INSTALLED'
for line2_name,line2_obj in list(globals().items()):
    if line2_name.endswith('_service_instance') and hasattr(line2_obj,'driver'):
        line2_boot_info['existing_owners'].append(dict(name=line2_name,state=getattr(line2_obj,'state',None),
            run_id=getattr(line2_obj,'config',{}).get('run_id'),requests=getattr(line2_obj.driver,'requests',None),
            commits=getattr(line2_obj.driver,'commits',None),pending=getattr(line2_obj.driver,'pending',None) is not None))
for line2_table in ('/proc/net/tcp','/proc/net/tcp6'):
    for line2_row in Path(line2_table).read_text().splitlines()[1:]:
        line2_fields=line2_row.split();line2_port=int(line2_fields[1].split(':')[-1],16)
        if line2_fields[3]=='0A' and line2_port in (5768,5790,5771,5773,5779):
            line2_boot_info['neural_or_control_listeners'].append(dict(port=line2_port,inode=line2_fields[9]))
for line2_proc in Path('/proc').iterdir():
    if not line2_proc.name.isdigit():continue
    try:line2_args=(line2_proc/'cmdline').read_bytes().split(b'\0')
    except (OSError,PermissionError):continue
    if any(b'ipykernel_launcher' in arg for arg in line2_args):
        line2_boot_info['kernel_processes'].append(dict(pid=int(line2_proc.name),
            kernel_files=[Path(arg.decode(errors='replace')).name for arg in line2_args if b'kernel-' in arg and arg.endswith(b'.json')]))
for line2_suffix in ('.bit','.hwh'):
    line2_path=Path('/home/xilinx/jupyter_notebooks/flyvis_t5c67_v1/A3R1_FRESH_READY3_05aa0e5238e14b3aad54bb695882d043/neuron_a'+line2_suffix)
    line2_boot_info['image_files'].append(dict(path=str(line2_path),exists=line2_path.is_file(),
        sha256=hashlib.sha256(line2_path.read_bytes()).hexdigest() if line2_path.is_file() else None))
print('LINE2_CURRENT_BOOT_READ_ONLY '+json.dumps(line2_boot_info,sort_keys=True))
