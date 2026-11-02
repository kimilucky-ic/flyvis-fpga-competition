"""R6 bounded32-step volatile journal. One authorized session, no board API.
Only paths under the current run are deferred. Power loss loses unflushed data.
"""
import os,threading,time
import step_profile as prof
from pathlib import Path
class RamRecords:
    def __init__(self,root,limit=16*1024*1024):
        self.root=Path(root).resolve();self.limit=limit;self.files={};self.bytes=0
        self.known_keys={};self.active=False;self.lock=threading.RLock();self.flush_ms=None
    def start(self):self.active=True
    def prevalidate(self,paths):
        if self.active:raise RuntimeError('prevalidate before producer starts')
        for path in paths:
            p=Path(path)
            self.known_keys[str(p)]=str(p.resolve().relative_to(self.root))
    def prevalidate_generated_steps(self,root,steps):
        # Closed, fixed filename grammar inside a newly-created empty run.
        # Resolve anchors once; do not resolve 13paths *4096steps individually.
        if self.active or self.known_keys:raise RuntimeError('fresh journal required')
        if type(steps) is not int or not 1<=steps<=4096:raise ValueError('step bound')
        root=Path(root)
        if root.resolve()!=self.root:raise ValueError('run root mismatch')
        allowed={'transport','spool'}
        children=list(self.root.iterdir())
        if {p.name for p in children}-allowed:raise ValueError('run namespace is not fresh')
        if 'transport' not in {p.name for p in children}:raise ValueError('transport missing')
        for p in children:
            if p.is_symlink() or p.resolve()!=self.root/p.name or not p.is_dir():raise ValueError('redirected run directory')
            if next(p.iterdir(),None) is not None:raise ValueError('run directory is not empty')
        names=('PREPARED.bin','COMMITTED.bin','CYCLE_CHECK.json','PUBLICATION.json','TIMING.json','PACKET_TIMING.json','WORKER_TIMING.json','RETURNED_UNCOMMITTED.bin','IN_DOUBT.json')
        keys={};prefix=str(root)
        for k in range(steps):
            d=os.path.join('capture','bound','%06d'%k)
            rels=[d]+[os.path.join(d,n) for n in names]
            rels.extend((os.path.join('transport','%06d.packet'%k),os.path.join('transport','%06d.ack.json'%k)))
            rels.append('CAMERA_BUFFER.json' if k==0 else 'CAMERA_BUFFER_%06d.json'%k)
            for rel in rels:keys[os.path.join(prefix,rel)]=rel
        self.known_keys=keys
        return dict(paths=len(keys),steps=steps,method='FRESH_NAMESPACE_FIXED_GRAMMAR_NO_PER_FILE_RESOLVE')
    def key(self,path):
        t=prof.tick()
        try:
            known=self.known_keys.get(str(path))
            return known if known is not None else str(Path(path).resolve().relative_to(self.root))
        except ValueError:return None
        finally:prof.add('ram_path_resolution',t)
    def put(self,path,data,replace=False):
        with self.lock:
            key=self.key(path)
            if not self.active or key is None:return False
            if key in self.files and not replace:raise FileExistsError(key)
            data=bytes(data);total=self.bytes-len(self.files.get(key,b''))+len(data)
            if total>self.limit or (key not in self.files and len(self.files)>=8192):raise MemoryError('bounded journal full; no next STEP')
            self.files[key]=data;self.bytes=total;return True
    def get(self,path):
        with self.lock:
            key=self.key(path)
            if self.active and key in self.files:return self.files[key]
        return Path(path).read_bytes()
    def retire_duplicate_commit(self,capsule_path,packet_path,record):
        # Packet already contains this exact complete record plus binding metadata.
        # Only retire the duplicate RAM representation, never the input preparation.
        with self.lock:
            if not self.active:return
            c,p=self.key(capsule_path),self.key(packet_path)
            if c not in self.files or p not in self.files:raise RuntimeError('missing committed record or packet')
            if not self.files[c].endswith(record) or not self.files[p].endswith(record):raise RuntimeError('record differs; retain both')
            self.bytes-=len(self.files[c]);del self.files[c]
    def flush(self):
        # End-of-run only. Lock prevents ACK writes racing the snapshot.
        # On error retain ALL RAM bytes and stop finalization; no automatic retry.
        start=time.monotonic()
        with self.lock:
            for key,data in self.files.items():
                path=self.root/key
                if path.resolve().relative_to(self.root)!=Path(key):raise RuntimeError('RAM path changed before flush')
                path.parent.mkdir(parents=True,exist_ok=True)
                with path.open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
            self.active=False;self.flush_ms=(time.monotonic()-start)*1000
        return dict(files=len(self.files),bytes=self.bytes,flush_ms=self.flush_ms,storage='RAM_DURING_STEPS_DISK_AFTER_RUN',raw_images_saved=False)
CURRENT=None

def put(path,data,replace=False):return CURRENT is not None and CURRENT.put(path,data,replace)
def read(path):return CURRENT.get(path) if CURRENT is not None else Path(path).read_bytes()
