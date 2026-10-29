"""Same FVEJ reader format; compact catalog and time batches, not each MMIO."""
import collections,hashlib,time
from .evidence_journal import JournalWriter as OriginalWriter,PREFIX,MAGIC,MAX_META,encoded,safe_name

def coalesce(pending):
    rows=[];chunks=[];key=None
    for name,kind,data in pending:
        current=(name,kind)
        if current==key and kind=='line':chunks.append(data)
        else:
            if key is not None:rows.append((key[0],key[1],b''.join(chunks)))
            key=current;chunks=[data]
    if key is not None:rows.append((key[0],key[1],b''.join(chunks)))
    return rows

class JournalWriter(OriginalWriter):
    def init__(self,*a,**kw):
        self.phase_ns=collections.Counter();self.barrier_counts=collections.Counter();super().init__(*a,**kw)
    def append_line(self,name,data):
        with self.lock:
            self._ready();safe_name(name)
            if not isinstance(data,bytes):raise TypeError('Evidence bytes')
            if self.pending_bytes+len(data)>self.max_pending or len(self.pending)>=8192:
                self.poisoned=True;raise BufferError('Evidence batch bound')
            self.names.add(name);self.pending.append((name,'line',data));self.pending_bytes+=len(data)
    def snapshot(self):return dict(phase_ns=dict(self.phase_ns),barrier_counts=dict(self.barrier_counts),fsync_calls=self.sync_calls)
    def checkpoint(self,barrier,terminal=None):
        with self.lock:
            self._ready();self.attempted_barrier=barrier;t0=time.perf_counter_ns()
            try:
                records=coalesce(self.pending);catalog=[];offset=0
                for name,kind,data in records:
                    catalog.append(dict(name=name,kind=kind,offset=offset,size=len(data),sha256=hashlib.sha256(data).hexdigest()));offset+=len(data)
                meta=encoded(dict(schema='flyvis-evidence-journal/v1',sequence=self.sequence,previous_sha256=self.previous,
                    context=self.context,barrier=barrier,terminal=terminal,records=catalog))
                if len(meta)>MAX_META:raise BufferError('Evidence metadata bound')
                payload=b''.join(data for _,_,data in records);digest=hashlib.sha256(meta+payload).digest()
                packet=PREFIX.pack(MAGIC,len(meta),len(payload),digest)+meta+payload;t1=time.perf_counter_ns()
                view=memoryview(packet)
                while view:
                    n=self.stream.write(view)
                    if n is None or n<=0:raise OSError('Short evidence write')
                    view=view[n:]
                t2=time.perf_counter_ns();self.stream.flush();t3=time.perf_counter_ns()
                self.sync_calls+=1;self.sync_fn(self.stream.fileno());t4=time.perf_counter_ns()
                self.sync_ns+=t4-t3
                for key,value in (('catalog_pack_and_hash',t1-t0),('journal_write',t2-t1),('stream_flush',t3-t2),('fsync',t4-t3)):
                    self.phase_ns[key]+=value
                self.barrier_counts[barrier]+=1
            except BaseException:self.poisoned=True;raise
            self.previous=digest.hex();self.sequence+=1;self.pending=[];self.pending_bytes=0
