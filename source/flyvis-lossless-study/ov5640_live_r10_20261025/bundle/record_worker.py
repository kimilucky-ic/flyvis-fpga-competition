"""Bounded ordered packaging of already admitted immutable records. No MMIO.
Queue exhaustion applies backpressure, never drops audit work. Failed and pending
jobs remain reachable in retained worker; finish requires an explicit drain.
"""
from queue import Queue,Full,Empty
from types import SimpleNamespace
import threading,time,json
import step_profile as prof
import ram_records
from capture_binding import save_json
from live_protocol import packet_from_committed,atomic,sha

class RecordWorker:
    def init__(self,out,config,context,packets,capacity=2,uploader=None):
        if type(capacity) is not int or not 1<=capacity<=32:raise ValueError('bounded worker capacity')
        self.out,self.config,self.context,self.packets=out,dict(config),dict(context),packets
        self.uploader=uploader
        self.queue=Queue(maxsize=capacity);self.error=None;self.failed_job=None
        self.finished=threading.Event();self.submitted=0;self.done=0;self.timings={}
        self.thread=threading.Thread(target=self._run,name='line11-record-pack',daemon=True)
        self.thread.start()
    def check(self):
        if self.error is not None:raise RuntimeError('record worker failed; retain all records: '+repr(self.error))
    def submit(self,bridge,k,previous,timing,producer_profile):
        self.check()
        if self.finished.is_set():raise RuntimeError('worker already draining')
        if k!=self.submitted:raise ValueError('worker input sequence')
        # Capture current validated bytes NOW. Never let worker read mutable bridge state.
        commit=bridge.binding.last_committed
        if bridge.failed or bridge.binding.failed or bridge.binding.next!=k+1 or not commit:
            raise ValueError('no validated commit')
        snapshot=SimpleNamespace(failed=False,last_record_bytes=bridge.last_record_bytes,
            binding=SimpleNamespace(failed=False,next=k+1,last_committed=(commit[0],commit[1],dict(commit[2]),dict(commit[3]))))
        if not isinstance(snapshot.last_record_bytes,bytes):raise TypeError('immutable record required')
        job=(snapshot,k,previous,dict(timing),producer_profile,time.monotonic())
        while True:
            self.check()
            try:self.queue.put(job,timeout=.05);break
            except Full:pass
        self.submitted+=1
        self.check()
    def _run(self):
        while not self.finished.is_set() or not self.queue.empty():
            try:job=self.queue.get(timeout=.02)
            except Empty:continue
            try:
                snapshot,k,previous,timing,producer_profile,queued=job
                if k!=self.done:raise ValueError('worker output sequence')
                started=time.monotonic();prof.begin()
                raw=packet_from_committed(snapshot,k,self.config,self.context,previous,timing)
                packed=time.monotonic();digest=sha(raw);hashed=time.monotonic()
                if self.uploader is not None:self.uploader.digests[k]=digest
                atomic(self.out/'transport'/('%06d.packet'%k),raw)
                if ram_records.CURRENT is not None:
                    ram_records.CURRENT.retire_duplicate_commit(self.out/'capture/bound'/('%06d'%k)/'COMMITTED.bin',self.out/'transport'/('%06d.packet'%k),snapshot.last_record_bytes)
                self.timings['%06d'%k]=dict(queue_wait_ms=(started-queued)*1000,pack_ms=(packed-started)*1000,wire_hash_ms=(hashed-packed)*1000,store_and_retire_ms=(time.monotonic()-hashed)*1000,total_worker_ms=(time.monotonic()-started)*1000)
                self.packets.append(digest);self.done+=1
                if self.uploader is not None:self.uploader.wake.set()
            except BaseException as exc:
                self.failed_job=job;self.error=exc;return
            finally:self.queue.task_done()
    def drain(self,timeout=10):
        self.finished.set();self.thread.join(timeout)
        if self.thread.is_alive():raise RuntimeError('record worker still active; retain RAM, no flush or close')
        self.check()
        if self.done!=self.submitted:raise RuntimeError('record queue incomplete')
