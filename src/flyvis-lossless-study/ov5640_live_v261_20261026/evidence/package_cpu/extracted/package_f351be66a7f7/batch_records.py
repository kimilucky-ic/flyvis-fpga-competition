"""Candidate-only bounded RAM journal. Existing pack worker saves16-step ZIP_STORED
batches, then releases a durable prefix for foreground ARM to ACK; no worker MMIO.
Pending writes are never published; disk failures retain RAM and stop new steps.
"""
import os,time,zipfile
from pathlib import Path
from ram_records import RamRecords

class BatchRecords(RamRecords):
    def __init__(self,root,limit=32*1024*1024,batch_steps=16):
        super().__init__(root,limit)
        if not 1<=batch_steps<=32:raise ValueError('batch bound')
        self.batch_steps=batch_steps;self.persisted_steps=0;self.completed_steps=0
        self.archive_index={};self.batches=[];self.peak_ram_bytes=0
        (self.root/'spool').mkdir(exist_ok=False)
    def put(self,path,data,replace=False):
        with self.lock:
            if self.key(path) in self.archive_index:raise RuntimeError('immutable archived key')
            result=super().put(path,data,replace)
            self.peak_ram_bytes=max(self.peak_ram_bytes,self.bytes);return result
    def get(self,path):
        with self.lock:
            key=self.key(path)
            if self.active and key in self.files:return self.files[key]
            archive=self.archive_index.get(key)
        if archive is not None:
            with zipfile.ZipFile(archive) as z:return z.read(Path(key).as_posix())
        return super().get(path)
    def persist_completed(self,k,force=False):
        if k+1<self.completed_steps:raise RuntimeError('batch sequence regressed')
        self.completed_steps=k+1
        if self.completed_steps==self.persisted_steps:return
        if not force and self.completed_steps-self.persisted_steps<self.batch_steps:return
        if self.completed_steps-self.persisted_steps>self.batch_steps:raise RuntimeError('batch sequence skipped')
        first=self.persisted_steps;last=self.completed_steps
        with self.lock:
            snapshot={}
            for j in range(first,last):
                for rel in ('capture/bound/%06d/PREPARED.bin'%j,'transport/%06d.packet'%j):
                    key=str(Path(rel))
                    if key not in self.files:raise RuntimeError('missing RAM input/packet before batch persistence')
                    snapshot[key]=self.files[key]
        start=time.monotonic();target=self.root/'spool'/('%06d_%06d.zip'%(first,last-1));pending=target.with_suffix('.zip.pending')
        if target.exists() or pending.exists():raise FileExistsError('batch already attempted; no automatic overwrite')
        # One durability barrier for the batch contents, not one per record.
        with pending.open('xb') as f:
            with zipfile.ZipFile(f,'w',compression=zipfile.ZIP_STORED) as z:
                for key,data in snapshot.items():z.writestr(Path(key).as_posix(),data)
            f.flush();os.fsync(f.fileno())
        os.replace(str(pending),str(target))
        if os.name=='posix':
            fd=os.open(str(target.parent),os.O_RDONLY)
            try:os.fsync(fd)
            finally:os.close(fd)
        with self.lock:
            for key,data in snapshot.items():
                if self.files.get(key) is not data:raise RuntimeError('batch RAM changed; retain evidence')
            for key,data in snapshot.items():
                self.archive_index[key]=target;del self.files[key];self.bytes-=len(data)
            self.persisted_steps=last
            self.batches.append(dict(first_step=first,last_step=last-1,files=len(snapshot),bytes=sum(map(len,snapshot.values())),
                persist_ms=(time.monotonic()-start)*1000,archive=str(target.relative_to(self.root))))
    def durable_prefix(self):
        # Updated only after file fsync, atomic rename and directory fsync.
        with self.lock:return self.persisted_steps
    def flush(self):
        if self.completed_steps>self.persisted_steps:self.persist_completed(self.completed_steps-1,force=True)
        result=super().flush()
        result.update(storage='BOUNDED_RAM_WITH_DURABLE_BACKGROUND_BATCHES',batches=self.batches,
            persisted_steps=self.persisted_steps,peak_ram_bytes=self.peak_ram_bytes,
            archives_are_neural_evidence=True,pending_batch_survives_only_in_RAM=True)
        return result
