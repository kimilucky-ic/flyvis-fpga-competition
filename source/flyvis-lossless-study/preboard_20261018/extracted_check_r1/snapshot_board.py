"""Read current PYNQ metadata, PS clock and process/socket occupancy only.

No Overlay construction/download, reset, PL register reads, writes or DMA.
Clocks.fclk0_mhz reads a non-clearing PS clock-control register.
"""
from pathlib import Path
from datetime import datetime
import hashlib,json,os,time
from pynq import PL
from pynq.ps import Clocks

def text(path):
    try:return Path(path).read_text(errors='replace').strip()
    except OSError:return None
def sha(path):
    p=Path(path)
    if not p.is_file():return None
    h=hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(1048576),b''):h.update(block)
    return h.hexdigest()
def attempt(fn):
    try:return dict(ok=True,value=fn())
    except Exception as exc:return dict(ok=False,error=type(exc).__name__+': '+str(exc))

bit=attempt(lambda:PL.bitfile_name)
filename=bit.get('value')
current=dict(bitfile=bit,timestamp=attempt(lambda:PL.timestamp),
    ip_metadata=attempt(lambda:[dict(name=name,type=item.get('type'),
        phys_addr=item.get('phys_addr'),addr_range=item.get('addr_range'))
        for name,item in PL.ip_dict.items()]),fclk0_mhz=attempt(lambda:float(Clocks.fclk0_mhz)))
if filename:
    current['bitfile_sha256']=sha(filename)
    current['hwh_sha256']=sha(str(Path(filename).with_suffix('.hwh')))

tcp={}
for name in ['tcp','tcp6']:
    for line in (text('/proc/net/'+name) or '').splitlines()[1:]:
        fields=line.split()
        if len(fields)>9 and fields[3]=='0A':tcp[fields[9]]=int(fields[1].rsplit(':',1)[1],16)
processes=[]
for directory in Path('/proc').iterdir():
    if not directory.name.isdigit():continue
    try:
        command=(directory/'cmdline').read_bytes().replace(b'\0',b' ').decode('utf-8','replace').lower()
        markers=[x for x in ['ipykernel','jupyter','flyvis','a3r1'] if x in command]
        if not markers:continue
        ports=[]
        for fd in (directory/'fd').iterdir():
            try:
                target=os.readlink(str(fd))
                if target.startswith('socket:[') and target[8:-1] in tcp:ports.append(tcp[target[8:-1]])
            except OSError:pass
        processes.append(dict(pid=int(directory.name),comm=text(directory/'comm'),
            markers=markers,listener_ports=sorted(set(ports))))
    except OSError:pass

print(json.dumps(dict(status='READ_ONLY_BOARD_IDENTITY_AND_OCCUPANCY_SNAPSHOT',
    observed_at_board_UTC=datetime.utcnow().isoformat()+'Z',monotonic=time.monotonic(),
    boot_id=text('/proc/sys/kernel/random/boot_id'),own_pid=os.getpid(),current=current,
    listening_TCP_ports=sorted(set(tcp.values())),relevant_processes=processes,
    PL_busy='NOT_READ_NO_CLEAR_ON_READ_RISK',
    operations=dict(program=0,reset=0,PL_register_reads=0,register_writes=0,DMA=0)),indent=2))
