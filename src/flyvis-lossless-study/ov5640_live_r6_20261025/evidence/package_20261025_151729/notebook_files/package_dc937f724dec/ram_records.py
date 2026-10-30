"""R6 bounded32-step volatile journal. One authorized session, no board API.
Only paths under the current run are deferred. Power loss loses unflushed data.
"""
import os,threading,time
from pathlib import Path
class RamRecords:
    def init__(self,root,limit=16*1024*1024):
        self.root=Path(root).resolve();self.limit=limit;self.files={};self.bytes=0
        self.active=False;self.lock=threading.RLock();self.flush_ms=None
    def start(self):self.active=True
    def key(self,path):
        try:return str(Path(path).resolve().relative_to(self.root))
        except ValueError:return None
    def put(self,path,data,replace=False):
        with self.lock:
            key=self.key(path)
            if not self.active or key is None:return False
            if key in self.files and not replace:raise FileExistsError(key)
            data=bytes(data);total=self.bytes-len(self.files.get(key,b''))+len(data)
            if total>self.limit or (key not in self.files and len(self.files)>=1024):raise MemoryError('bounded R6 journal full; no next STEP')
            self.files[key]=data;self.bytes=total;return True
    def get(self,path):
        with self.lock:
            key=self.key(path)
            if self.active and key in self.files:return self.files[key]
        return Path(path).read_bytes()
    def flush(self):
        # End-of-run only. Lock prevents ACK writes racing the snapshot.
        # On error retain ALL RAM bytes and stop finalization; no automatic retry.
        start=time.monotonic()
        with self.lock:
            for key,data in self.files.items():
                path=self.root/key;path.parent.mkdir(parents=True,exist_ok=True)
                with path.open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
            self.active=False;self.flush_ms=(time.monotonic()-start)*1000
        return dict(files=len(self.files),bytes=self.bytes,flush_ms=self.flush_ms,storage='RAM_DURING_STEPS_DISK_AFTER_RUN',raw_images_saved=False)
CURRENT=None

def put(path,data,replace=False):return CURRENT is not None and CURRENT.put(path,data,replace)
def read(path):return CURRENT.get(path) if CURRENT is not None else Path(path).read_bytes()
