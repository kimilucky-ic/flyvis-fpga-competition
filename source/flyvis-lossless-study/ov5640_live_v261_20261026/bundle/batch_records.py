"""Bounded asynchronous persistence of immutable input/state batches.
Only the foreground releases DDR, using the prefix published after all barriers.
A writer failure is sticky: keep RAM/queued jobs, never retry or acknowledge it.
"""
import os,time,zipfile,threading
from queue import Queue,Full,Empty
from pathlib import Path
from ram_records import RamRecords

class BatchRecords(RamRecords):
    def init__(self,root,limit=32*1024*1024,batch_steps=16,pending_batches=2,wait_timeout=10):
        super().init__(root,limit)
        if not 1<=batch_steps<=32:raise ValueError('batch bound')
        if type(pending_batches) is not int or not 1<=pending_batches<=2:raise ValueError('writer queue bound')
        if not 0<wait_timeout<=10:raise ValueError('writer wait bound')
        self.batch_steps=batch_steps;self.persisted_steps=0;self.completed_steps=0;self.scheduled_steps=0
        self.archive_index={};self.batches=[];self.peak_ram_bytes=0;self.pending_keys=set()
        self.queue=Queue(maxsize=pending_batches);self.wait_timeout=wait_timeout
        self.error=None;self.failed_job=None;self.finished=threading.Event();self.peak_pending_batches=0
        self.thread=None;self.draining=False;self.drain_ms=0
        (self.root/'spool').mkdir(exist_ok=False)
    def check(self):
        if self.error is not None:raise RuntimeError('batch writer failed; retain RAM and DDR: '+repr(self.error))
    def _fail(self,exc):
        with self.lock:
            if self.error is None:self.error=exc
        self.finished.set()
    def put(self,path,data,replace=False):
        with self.lock:
            key=self.key(path)
            if key in self.archive_index or key in self.pending_keys:raise RuntimeError('immutable scheduled/archived key')
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
        self.check()
        if self.draining:raise RuntimeError('batch writer already draining')
        if k+1<self.completed_steps or k+1>self.completed_steps+1:raise RuntimeError('batch completion sequence')
        self.completed_steps=k+1
        count=self.completed_steps-self.scheduled_steps
        if count==0 or (not force and count<self.batch_steps):return
        if count>self.batch_steps:raise RuntimeError('batch sequence skipped')
        first=self.scheduled_steps;last=self.completed_steps
        with self.lock:
            snapshot={}
            for j in range(first,last):
                for rel in ('capture/bound/%06d/PREPARED.bin'%j,'transport/%06d.packet'%j):
                    key=str(Path(rel))
                    if key not in self.files:raise RuntimeError('missing RAM input/packet before persistence')
                    snapshot[key]=self.files[key]
            self.pending_keys.update(snapshot)
        # Queue stores references to immutable bytes already counted in RAM, not copies.
        queued=time.monotonic();job=(first,last,snapshot,queued)
        if self.thread is None:
            self.thread=threading.Thread(target=self._run,name='line11-batch-save',daemon=True);self.thread.start()
        try:
            while True:
                self.check()
                remaining=self.wait_timeout-(time.monotonic()-queued)
                if remaining<=0:raise TimeoutError('batch queue stalled; preserve RAM and DDR')
                try:self.queue.put(job,timeout=min(.05,remaining));break
                except Full:pass
            self.scheduled_steps=last
            self.peak_pending_batches=max(self.peak_pending_batches,self.queue.qsize())
            self.check()
        except BaseException as exc:
            self.failed_job=job;self._fail(exc);raise
    def _run(self):
        while not self.finished.is_set() or not self.queue.empty():
            try:job=self.queue.get(timeout=.02)
            except Empty:continue
            try:
                self.check();self._persist(job)
            except BaseException as exc:
                self.failed_job=job;self._fail(exc);return
            finally:self.queue.task_done()
    def _sync_directory(self,directory):
        if os.name=='posix':
            fd=os.open(str(directory),os.O_RDONLY)
            try:os.fsync(fd)
            finally:os.close(fd)
    def _persist(self,job):
        first,last,snapshot,queued=job
        if first!=self.persisted_steps:raise RuntimeError('writer prefix discontinuity')
        start=time.monotonic();target=self.root/'spool'/('%06d_%06d.zip'%(first,last-1));pending=target.with_suffix('.zip.pending')
        if target.exists() or pending.exists():raise FileExistsError('batch already attempted; no automatic overwrite')
        with pending.open('xb') as f:
            with zipfile.ZipFile(f,'w',compression=zipfile.ZIP_STORED) as z:
                for key,data in snapshot.items():z.writestr(Path(key).as_posix(),data)
            f.flush();os.fsync(f.fileno())
        synced=time.monotonic();os.replace(str(pending),str(target));self._sync_directory(target.parent)
        durable=time.monotonic()
        with self.lock:
            self.check()
            for key,data in snapshot.items():
                if self.files.get(key) is not data:raise RuntimeError('batch RAM changed; retain evidence')
            for key,data in snapshot.items():
                self.archive_index[key]=target;del self.files[key];self.bytes-=len(data)
            self.pending_keys.difference_update(snapshot)
            self.batches.append(dict(first_step=first,last_step=last-1,files=len(snapshot),bytes=sum(map(len,snapshot.values())),
                persist_ms=(durable-start)*1000,queue_wait_ms=(start-queued)*1000,
                write_and_file_sync_ms=(synced-start)*1000,rename_and_directory_sync_ms=(durable-synced)*1000,
                archive=str(target.relative_to(self.root))))
            self.persisted_steps=last
    def durable_prefix(self):
        with self.lock:
            self.check();return self.persisted_steps
    def drain(self):
        start=time.monotonic();self.check()
        if not self.draining:
            if self.completed_steps>self.scheduled_steps:self.persist_completed(self.completed_steps-1,force=True)
            self.draining=True;self.finished.set()
        if self.thread is not None:self.thread.join(max(0,self.wait_timeout-(time.monotonic()-start)))
        if self.thread is not None and self.thread.is_alive():
            exc=TimeoutError('batch writer active; keep kernel/RAM/DDR; no flush or close');self._fail(exc);raise exc
        self.check()
        if self.persisted_steps!=self.completed_steps:raise RuntimeError('writer incomplete; retain DDR')
        self.drain_ms+=(time.monotonic()-start)*1000
    def flush(self):
        self.drain()
        result=super().flush()
        result.update(storage='BOUNDED_RAM_WITH_INDEPENDENT_DURABLE_WRITER',batches=self.batches,
            persisted_steps=self.persisted_steps,scheduled_steps=self.scheduled_steps,peak_ram_bytes=self.peak_ram_bytes,
            pending_batch_capacity=self.queue.maxsize,peak_pending_batches=self.peak_pending_batches,writer_drain_ms=self.drain_ms,
            archives_are_neural_evidence=True,pending_batch_survives_only_in_RAM=True)
        return result
