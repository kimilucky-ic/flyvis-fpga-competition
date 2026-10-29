"""Bounded stream evidence. No model, device, socket or worker starts on import.

The neural host reserves a journal slot before computing. A checked candidate
can advance private state, but public COMMIT is the fsync-confirmed watermark.
Large source/snapshot writes have their own bounded queue and cannot consume a
step slot. Power loss/storage failure is never promoted to a complete result.
"""
import base64
from contextlib import contextmanager
import json
import os
import queue
import threading
import time
import numpy as np
from live_protocol import checked_commit,require,write
from realtime_timing import Timings

STORAGE_LIMIT_BYTES=512*1048576


class CommitJournal:
    def init__(self,path,batch_steps=10):
        require(type(batch_steps) is int and 1<=batch_steps<=32,'JOURNAL_BATCH_BOUND')
        self.file=path.open('xb',buffering=0);self.capacity=batch_steps
        self.slots=[None]*batch_steps;self.pending=0;self.ticket=None
        self.accepted_steps=0;self.durable_steps=0;self.durable_bytes=0;self.error=None;self.closed=False
        self.timing=Timings()

    def prepare(self,row):
        require(not self.closed and self.error is None,'JOURNAL_UNAVAILABLE')
        require(self.ticket is None and self.pending<self.capacity,'JOURNAL_RESERVATION_REQUIRED_BEFORE_COMPUTE')
        k=self.accepted_steps
        require(row['step_id']==k and row['state_token']==k+1 and row['status']=='COMMITTED','JOURNAL_STEP_ORDER')
        encoded=(json.dumps(row,separators=(',',':'),allow_nan=False)+'\n').encode('utf-8')
        require(len(encoded)<=4096,'JOURNAL_RECORD_BOUND')
        self.ticket=(object(),encoded)
        return self.ticket

    def accept(self,ticket,candidate,gate,commit):
        require(ticket is self.ticket and ticket is not None and self.pending<self.capacity,'JOURNAL_TICKET')
        # All validation/encoding/capacity checks preceded computation/commit.
        state=checked_commit(candidate,gate,commit)
        self.slots[self.pending]=ticket[1];self.pending+=1;self.accepted_steps+=1;self.ticket=None
        return state

    def cancel(self,ticket):
        if ticket is self.ticket:self.ticket=None

    def flush(self):
        require(not self.closed and self.error is None,'JOURNAL_WRITE_FAILED '+str(self.error))
        if not self.pending:return self.durable_steps
        try:
            data=b''.join(self.slots[:self.pending]);view=memoryview(data)
            with self.timing.measure('journal_write'):
                while view:
                    count=self.file.write(view)
                    require(count is not None and 0<count<=len(view),'JOURNAL_SHORT_WRITE')
                    view=view[count:]
            with self.timing.measure('journal_fsync'):os.fsync(self.file.fileno())
            # Never acknowledge rows solely because write()/flush() returned.
            self.durable_bytes+=len(data);self.durable_steps=self.accepted_steps
            for i in range(self.pending):self.slots[i]=None
            self.pending=0
            return self.durable_steps
        except BaseException as error:
            self.error=repr(error)
            raise

    def info(self):
        return dict(schema='flyvis-durable-commit/v1',accepted_private_steps=self.accepted_steps,
            durable_steps=self.durable_steps,durable_bytes=self.durable_bytes,pending_steps=self.pending,
            max_pending_steps=self.capacity,error=self.error,stages=self.timing.summary(),
            semantics='Public COMMIT requires fsync; unacknowledged suffix is not committed evidence')

    def close(self):
        if self.closed:return
        try:self.flush()
        finally:self.closed=True;self.file.close()


class EvidenceWriter:
    """Assets only: reservations count queued AND in-flight writes, not GPU steps."""
    def init__(self,root,capacity=128):
        self.root=root;self.queue=queue.Queue(capacity);self.available=threading.BoundedSemaphore(capacity)
        self.capacity=capacity;self.lock=threading.RLock();self.error=None;self.bytes=0;self.peak=0;self.outstanding=0
        self.tickets=set();self.accepted=0;self.saved=0;self.closed=False;self.timing=Timings()
        self.thread=threading.Thread(target=self.loop,daemon=True,name='FlyVis source and snapshot evidence');self.thread.start()

    def reserve(self,kind,timeout=.1):
        require(kind in ('source','snapshot'),'ASSET_KIND')
        with self.lock:require(not self.closed and self.error is None,'EVIDENCE_WRITE_FAILED '+str(self.error))
        start=time.perf_counter();available=self.available.acquire(timeout=timeout)
        with self.lock:
            self.timing.add('asset_reservation_wait',time.perf_counter()-start)
            require(available,'EVIDENCE_BACKPRESSURE_BEFORE_COMPUTE')
            if self.closed or self.error is not None:
                self.available.release();raise ValueError('EVIDENCE_WRITE_FAILED '+str(self.error))
            ticket=(object(),kind);self.tickets.add(ticket);self.outstanding+=1;self.peak=max(self.peak,self.outstanding)
            return ticket

    def cancel(self,ticket):
        with self.lock:
            if ticket in self.tickets:
                self.tickets.remove(ticket);self.outstanding-=1;self.available.release()

    def submit(self,ticket,value):
        with self.lock:
            require(ticket in self.tickets and not self.closed and self.error is None,'EVIDENCE_TICKET_OR_WRITER_FAILED')
            self.queue.put_nowait((ticket[1],value)) # reserved capacity, no queue.Full after neural commit
            self.tickets.remove(ticket);self.accepted+=1

    @contextmanager
    def reserved(self,kind,timeout=.1):
        ticket=self.reserve(kind,timeout)
        try:yield ticket
        finally:self.cancel(ticket)

    def put(self,kind,value):
        with self.reserved(kind) as ticket:self.submit(ticket,value)

    def _save(self,kind,value):
        if kind=='source':
            p=self.root/'sources';p.mkdir(exist_ok=True);seq=value['source']['sequence']
            png=base64.b64decode(value['png']);(p/f'{seq:06}.png').write_bytes(png)
            np.save(p/f'{seq:06}_hex.npy',np.asarray(value['values'],dtype=np.float32),allow_pickle=False)
            write(p/f'{seq:06}.json',value['source'])
            paths=[p/f'{seq:06}.png',p/f'{seq:06}_hex.npy',p/f'{seq:06}.json']
        else:
            packet,full=value;p=self.root/'snapshots';p.mkdir(exist_ok=True)
            np.savez(p/f"{packet['serial']:06}.npz",full=full,flow=np.asarray(packet['flow'],dtype=np.float32),
                input=np.asarray(packet['input_hex'],dtype=np.float32),step_id=packet['step_id'])
            metadata={k:v for k,v in packet.items() if k not in ('preview_png','input_hex','flow','recent_activity','spatial')}
            metadata['spatial']={k:v for k,v in packet['spatial'].items() if k!='values'}
            metadata['arrays_file']=f"{packet['serial']:06}.npz";write(p/f"{packet['serial']:06}.json",metadata)
            paths=[p/f"{packet['serial']:06}.npz",p/f"{packet['serial']:06}.json"]
        # Count persisted bytes, not a fixed 200KB surcharge per snapshot.
        # The old estimate could reach 512MiB while actual files were only 376MiB.
        self.bytes+=sum(path.stat().st_size for path in paths)
        require(self.bytes<STORAGE_LIMIT_BYTES,'STREAM_EVIDENCE_STORAGE_LIMIT')

    def loop(self):
        while True:
            item=self.queue.get()
            if item is None:return
            kind,value=item;begin=time.perf_counter()
            try:
                self._save(kind,value)
                with self.lock:self.saved+=1
            except BaseException as error:
                with self.lock:self.error=repr(error)
                return
            finally:
                with self.lock:
                    self.timing.add('asset_'+kind+'_write',time.perf_counter()-begin)
                    self.outstanding-=1;self.available.release()

    def info(self):
        with self.lock:
            return dict(accepted_assets=self.accepted,saved_assets=self.saved,outstanding=self.outstanding,
                reserved=len(self.tickets),capacity=self.capacity,queue_peak=self.peak,error=self.error,
                saved_asset_bytes=self.bytes,storage_limit_bytes=STORAGE_LIMIT_BYTES,stages=self.timing.summary())

    def close(self):
        with self.lock:
            self.closed=True
            for ticket in list(self.tickets):self.cancel(ticket)
        if self.thread.is_alive():
            self.queue.put(None,timeout=5);self.thread.join(10)
        require(not self.thread.is_alive() and self.error is None and self.accepted==self.saved,
                'EVIDENCE_CLOSE_FAILED '+str(self.error))
