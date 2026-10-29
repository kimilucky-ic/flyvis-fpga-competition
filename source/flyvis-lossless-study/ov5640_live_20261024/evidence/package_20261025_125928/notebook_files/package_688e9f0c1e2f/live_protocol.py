"""Immutable finite-session wire records. No board imports or control commands."""
import hashlib,json,os,struct,threading
from pathlib import Path
from snapshot_records import decode_record
from cycle_contract import EXPECTED_CYCLES
N=45669; SOURCE_BYTES=800*480*3; RECORD_BYTES=188416; MAX_PACKET=SOURCE_BYTES+RECORD_BYTES+65540

def sha(data):return hashlib.sha256(data).hexdigest()
def canonical(obj):return json.dumps(obj,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def atomic(path,data):
    path=Path(path);tmp=path.with_suffix(path.suffix+'.pending')
    with tmp.open('wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
    os.replace(str(tmp),str(path))
    if os.name=='posix':
        fd=os.open(str(path.parent),os.O_RDONLY)
        try:os.fsync(fd)
        finally:os.close(fd)

def pack(meta,source,record):
    h=canonical(meta)
    if len(h)>65536:raise ValueError('header too large')
    return struct.pack('<I',len(h))+h+source+record

def unpack(raw,config):
    if len(raw)>MAX_PACKET or len(raw)<4:raise ValueError('packet bound')
    n=struct.unpack_from('<I',raw)[0]
    if not 0<n<=65536 or len(raw)!=4+n+SOURCE_BYTES+RECORD_BYTES:raise ValueError('packet incomplete')
    m=json.loads(raw[4:4+n]);k=m['step_id']
    if type(k) is not int or not 0<=k<config['max_steps']:raise ValueError('step bound')
    if m['session_id']!=config['session_id'] or m['schema']!='line11-live-record/v1':raise ValueError('session/schema')
    for key in ('run_id','boot_id'):
        if not isinstance(m[key],str) or not 1<=len(m[key])<=80 or any(c not in '0123456789abcdef_RUN-' for c in m[key]):raise ValueError('identity')
    if m['bit_sha256']!=config['bit_sha256'] or m['hwh_sha256']!=config['hwh_sha256']:raise ValueError('firmware identity')
    if m['evidence'] not in ('CPU_MOCK_ONLY','OPERATOR_PHYSICAL_RUN_UNATTESTED'):raise ValueError('evidence')
    source=raw[4+n:4+n+SOURCE_BYTES];record=raw[-RECORD_BYTES:];r=decode_record(record,k)
    if r.cycles!=EXPECTED_CYCLES:raise ValueError('cycles')
    for key,data in [('source_sha256',source),('input_sha256',r.input_bits),('state_sha256',r.state_bits),('record_sha256',record)]:
        if m[key]!=sha(data):raise ValueError(key)
    c=m['committed'];p=m['prepared']
    if (c['step_id']!=k or p['step_id']!=k or c['sequence']!=k+1 or
        c['input_sha256']!=m['input_sha256'] or p['input_sha256']!=m['input_sha256'] or
        c['frame_sha256']!=m['source_sha256'] or p['frame_sha256']!=m['source_sha256'] or
        c['state_sha256']!=m['state_sha256'] or c['source_frame_id']!=k or p['source_frame_id']!=k):raise ValueError('binding receipt')
    return m,source,r

def packet_from_step(out,k,config,context,previous_sha):
    d=Path(out)/'capture/bound'/('%06d'%k)
    if (d/'IN_DOUBT.json').exists():raise ValueError('uncertain step')
    p=json.loads((d/'PREPARED.json').read_text());c=json.loads((d/'COMMITTED.json').read_text())
    source=(d/'source_frame.bin').read_bytes();record=(d/'record.bin').read_bytes();r=decode_record(record,k)
    m=dict(schema='line11-live-record/v1',session_id=config['session_id'],run_id=context['run_id'],boot_id=context['boot_id'],
           step_id=k,evidence=context['evidence'],bit_sha256=config['bit_sha256'],hwh_sha256=config['hwh_sha256'],
           previous_state_sha256=previous_sha,source_sha256=sha(source),input_sha256=sha(r.input_bits),state_sha256=sha(r.state_bits),
           record_sha256=sha(record),prepared=p,committed=c,timing=json.loads((d/'TIMING.json').read_text()))
    raw=pack(m,source,record);unpack(raw,config);return raw

class Store:
    """One durable packet per step; identical resend has no additional effect."""
    def init__(self,path,config):
        self.path=Path(path);self.path.mkdir(parents=True,exist_ok=True);self.config=config;self.lock=threading.RLock();self.meta=[];self.digests=[]
        files=sorted(self.path.glob('*.packet'))
        for k,f in enumerate(files):
            if f.name!='%06d.packet'%k:raise ValueError('noncontiguous saved journal')
            raw=f.read_bytes();m,_,_=unpack(raw,config);self._next(m);self.meta.append(m);self.digests.append(sha(raw))
        self.final=None
        if (self.path/'FINISH.json').exists():
            obj=json.loads((self.path/'FINISH.json').read_text());self._check_finish(obj);self.final=obj
    def _next(self,m):
        k=len(self.meta)
        if m['step_id']!=k:raise ValueError('out of order; next=%d'%k)
        previous=self.meta[-1]['state_sha256'] if k else self.config['initial_state_sha256']
        if m['previous_state_sha256']!=previous:raise ValueError('state chain')
        if k and any(m[x]!=self.meta[0][x] for x in ('run_id','boot_id','evidence')):raise ValueError('mixed run')
    def accept(self,raw):
        m,_,_=unpack(raw,self.config);k=m['step_id'];digest=sha(raw)
        with self.lock:
            if k<len(self.meta):
                if self.digests[k]!=digest:raise ValueError('conflicting duplicate')
                return dict(step_id=k,sha256=digest,durable=True,duplicate=True)
            if self.final is not None:raise ValueError('session finished')
            self._next(m)
            atomic(self.path/('%06d.packet'%k),raw)
            self.meta.append(m);self.digests.append(digest)
            return dict(step_id=k,sha256=digest,durable=True,duplicate=False)
    def _check_finish(self,obj):
        if (obj['session_id']!=self.config['session_id'] or obj['completed_steps']!=len(self.meta) or
            not self.meta or obj['run_id']!=self.meta[0]['run_id'] or obj['boot_id']!=self.meta[0]['boot_id'] or
            obj['packet_sha256']!=self.digests):raise ValueError('finish identity/count')
        if obj['status']=='NORMAL_CAMERA_CLOSED_ALL_STEPS_SAVED_ORACLE_PENDING':
            if len(self.meta)!=self.config['max_steps'] or not obj['camera_closed']:raise ValueError('false completion')
        elif obj['status']!='STOPPED_KEEP_KERNEL_AND_BUFFERS':raise ValueError('finish status')
    def finish(self,obj):
        with self.lock:
            self._check_finish(obj)
            if self.final is not None and canonical(self.final)!=canonical(obj):raise ValueError('conflicting finish')
            if self.final is None:atomic(self.path/'FINISH.json',canonical(obj));self.final=obj
        return dict(durable=True,completed_steps=len(self.meta))
    def read(self,k):return unpack((self.path/('%06d.packet'%k)).read_bytes(),self.config)
