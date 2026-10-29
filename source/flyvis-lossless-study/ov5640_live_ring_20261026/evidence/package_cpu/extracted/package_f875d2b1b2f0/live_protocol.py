from camera_config import WIDTH,HEIGHT,MAPPING
"""Immutable finite-session wire records. No board imports or control commands."""
import hashlib,json,os,struct,threading
from pathlib import Path
import step_profile as prof
import ram_records
from snapshot_records import decode_record
from cycle_contract import EXPECTED_CYCLES
from capture_binding import read_capsule
N=45669; SOURCE_BYTES=800*480*3; RECORD_BYTES=188416; MAX_PACKET=SOURCE_BYTES+RECORD_BYTES+65540

def sha(data):
    t=prof.tick();result=hashlib.sha256(data).hexdigest();prof.add('sha256',t,len(data));prof.add('hash_protocol_'+str(len(data))+'B',t,len(data));return result
def canonical(obj):
    t=prof.tick();data=json.dumps(obj,sort_keys=True,separators=(',',':'),allow_nan=False).encode();prof.add('json_encode',t,len(data));return data
def atomic(path,data):
    if ram_records.put(path,data,replace=True):return
    path=Path(path);tmp=path.with_suffix(path.suffix+'.pending')
    name='atomic'+path.suffix;t=prof.tick()
    with tmp.open('wb') as f:
        f.write(data);f.flush();prof.add('write:'+name,t,len(data))
        t=prof.tick();os.fsync(f.fileno());prof.add('fsync:'+name,t)
    t=prof.tick();os.replace(str(tmp),str(path));prof.add('rename:'+name,t)
    if os.name=='posix':
        fd=os.open(str(path.parent),os.O_RDONLY)
        try:
            t=prof.tick();os.fsync(fd);prof.add('directory_fsync',t)
        finally:os.close(fd)

def pack(meta,source,record):
    h=canonical(meta)
    if len(h)>65536:raise ValueError('header too large')
    return struct.pack('<I',len(h))+h+(b'' if meta['schema'] in ('line11-live-compact/v2','line11-live-compact/v3') else source)+record

def unpack(raw,config):
    if len(raw)>MAX_PACKET or len(raw)<4:raise ValueError('packet bound')
    n=struct.unpack_from('<I',raw)[0]
    if not 0<n<=65536 or len(raw)<4+n:raise ValueError('header incomplete')
    m=json.loads(raw[4:4+n]);k=m['step_id']
    compact=m['schema'] in ('line11-live-compact/v2','line11-live-compact/v3')
    if len(raw)!=4+n+(0 if compact else SOURCE_BYTES)+RECORD_BYTES:raise ValueError('packet incomplete')
    if type(k) is not int or not 0<=k<config['max_steps']:raise ValueError('step bound')
    if m['session_id']!=config['session_id'] or m['schema'] not in ('line11-live-record/v1','line11-live-compact/v2','line11-live-compact/v3'):raise ValueError('session/schema')
    for key in ('run_id','boot_id'):
        if not isinstance(m[key],str) or not 1<=len(m[key])<=80 or any(c not in '0123456789abcdef_RUN-' for c in m[key]):raise ValueError('identity')
    if m['bit_sha256']!=config['bit_sha256'] or m['hwh_sha256']!=config['hwh_sha256']:raise ValueError('firmware identity')
    if m['evidence'] not in ('CPU_MOCK_ONLY','OPERATOR_PHYSICAL_RUN_UNATTESTED'):raise ValueError('evidence')
    source=None if compact else raw[4+n:4+n+SOURCE_BYTES];record=raw[-RECORD_BYTES:];r=decode_record(record,k,expected_sequence=k+1,expected_cookie=int(m['run_id'][-8:],16))
    if r.cycles!=EXPECTED_CYCLES:raise ValueError('cycles')
    # decode_record already calculated input/state hashes once.
    if m['input_sha256']!=r.input_sha256 or m['state_sha256']!=r.state_sha256:raise ValueError('payload hashes')
    if source is not None and m['source_sha256']!=sha(source):raise ValueError('source_sha256')
    if m['schema']!='line11-live-compact/v3' and m['record_sha256']!=sha(record):raise ValueError('record_sha256')
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
    source=(d/'source_frame.bin').read_bytes();record=(d/'record.bin').read_bytes();r=decode_record(record,k,expected_sequence=k+1,expected_cookie=int(context['run_id'][-8:],16))
    m=dict(schema='line11-live-record/v1',session_id=config['session_id'],run_id=context['run_id'],boot_id=context['boot_id'],
           step_id=k,evidence=context['evidence'],bit_sha256=config['bit_sha256'],hwh_sha256=config['hwh_sha256'],
           previous_state_sha256=previous_sha,source_sha256=sha(source),input_sha256=sha(r.input_bits),state_sha256=sha(r.state_bits),
           record_sha256=sha(record),prepared=p,committed=c,timing=json.loads((d/'TIMING.json').read_text()))
    raw=pack(m,source,record);unpack(raw,config);return raw

def metadata_from_committed(bridge,k,config,context,previous_sha,timing):
    """Internal fast path only; reuse immutable records after durable admission.

    Incoming network/files still pass full unpack(). No checksum work is removed
    from DDR admission or the receiving trust boundary.
    """
    if bridge.failed or bridge.binding.failed or bridge.binding.next!=k+1:
        raise ValueError('no successful current commit')
    source,r,prepared,committed=bridge.binding.last_committed
    record=bridge.last_record_bytes
    p=dict(prepared) if isinstance(prepared,dict) else json.loads(prepared)
    c=dict(committed) if isinstance(committed,dict) else json.loads(committed)
    if (not isinstance(source,bytes) or not isinstance(record,bytes) or len(source)!=WIDTH*HEIGHT*3 or
        len(record)!=RECORD_BYTES or r.frame_id!=k or r.cycles!=EXPECTED_CYCLES or
        record[128:3012]!=r.input_bits or record[4096:186772]!=r.state_bits or
        p['step_id']!=k or c['step_id']!=k or c['sequence']!=k+1 or
        p['frame_sha256']!=c['frame_sha256'] or p['input_sha256']!=r.input_sha256 or
        c['input_sha256']!=r.input_sha256 or c['state_sha256']!=r.state_sha256):
        raise ValueError('committed cache identity mismatch')
    m=dict(schema='line11-live-compact/v3',camera_width=WIDTH,camera_height=HEIGHT,source_pixels_retained=False,producer_storage='BATCH_DURABLE_AFTER_SAVE_UNTIL_THEN_VOLATILE',session_id=config['session_id'],run_id=context['run_id'],boot_id=context['boot_id'],
           step_id=k,evidence=context['evidence'],bit_sha256=config['bit_sha256'],hwh_sha256=config['hwh_sha256'],
           previous_state_sha256=previous_sha,source_sha256=c['frame_sha256'],input_sha256=r.input_sha256,state_sha256=r.state_sha256,
           record_sha256=None,prepared=p,committed=c,timing=timing)
    return m

def packet_from_committed(bridge,k,config,context,previous_sha,timing):
    return pack(metadata_from_committed(bridge,k,config,context,previous_sha,timing),
                bridge.binding.last_committed[0],bridge.last_record_bytes)

def index_from_committed(bridge,k,config,context,previous_sha,timing):
    t=prof.tick();meta=metadata_from_committed(bridge,k,config,context,previous_sha,timing)
    header=canonical(meta);prefix=struct.pack('<I',len(header))+header
    # Same wire digest, without assembling or saving another1.34MB packet.
    wire_t=prof.tick();h=hashlib.sha256();h.update(prefix);h.update(bridge.last_record_bytes)
    wire_digest=h.hexdigest();prof.add('index_wire_sha256',wire_t,len(prefix)+RECORD_BYTES)
    result=dict(schema='line11-durable-packet-index/v1',step_id=k,metadata=meta,
                packet_sha256=wire_digest,packet_bytes=len(prefix)+RECORD_BYTES)
    prof.add('packet_index_build_and_digest',t,RECORD_BYTES);return result

def load_packet(out,k):
    """Read only fixed-name durable files; never accept a path from index metadata."""
    out=Path(out);legacy=out/'transport'/('%06d.packet'%k)
    try:return ram_records.read(legacy)
    except FileNotFoundError:pass # older indexed archives remain readable
    path=out/'transport'/('%06d.ready.json'%k)
    try:blob=ram_records.read(path)
    except FileNotFoundError:return None
    if len(blob)>65536:raise ValueError('index size')
    index=json.loads(blob);m=index['metadata']
    if index['schema']!='line11-durable-packet-index/v1' or index['step_id']!=k or m['step_id']!=k:
        raise ValueError('index identity')
    directory=out/'capture/bound'/('%06d'%k)
    if (directory/'IN_DOUBT.json').exists():raise ValueError('uncertain source record')
    if m['schema'] in ('line11-live-compact/v2','line11-live-compact/v3'):
        prepared,_=read_capsule(directory/'PREPARED.bin',2884,header_only=True)
        committed,record=read_capsule(directory/'COMMITTED.bin',RECORD_BYTES)
        if prepared!=m['prepared'] or committed!=m['committed']:raise ValueError('durable capsule receipt mismatch')
        data=pack(m,None,record)
    else:
        if json.loads((directory/'COMMITTED.json').read_text())!=m['committed'] or json.loads((directory/'PREPARED.json').read_text())!=m['prepared']:
            raise ValueError('durable receipt differs from index')
        source=(directory/'source_frame.bin').read_bytes();record=(directory/'record.bin').read_bytes()
        if len(source)!=WIDTH*HEIGHT*3 or len(record)!=RECORD_BYTES:raise ValueError('incomplete retained source')
        data=pack(m,source,record)
    if len(data)!=index['packet_bytes'] or sha(data)!=index['packet_sha256']:raise ValueError('retained source/index digest mismatch')
    return data

class Store:
    """One durable packet per step; identical resend has no additional effect."""
    def init__(self,path,config):
        self.path=Path(path);self.path.mkdir(parents=True,exist_ok=True);self.config=config;self.lock=threading.RLock();self.meta=[];self.digests=[]
        files=sorted(self.path.glob('*.packet'))
        for k,f in enumerate(files):
            if f.name!='%06d.packet'%k:raise ValueError('noncontiguous saved journal')
            raw=f.read_bytes();m,_,_=unpack(raw,config);self._next(m);self.meta.append(m);self.digests.append(sha(raw))
        self.final=None;self.camera_close=None
        if (self.path/'FINISH.json').exists():
            obj=json.loads((self.path/'FINISH.json').read_text());self._check_finish(obj);self.final=obj
        if (self.path/'CAMERA_CLOSE.json').exists():
            obj=json.loads((self.path/'CAMERA_CLOSE.json').read_text());self._check_camera_close(obj);self.camera_close=obj
    def _next(self,m):
        k=len(self.meta)
        if m['step_id']!=k:raise ValueError('out of order; next=%d'%k)
        previous=self.meta[-1]['state_sha256'] if k else self.config['initial_state_sha256']
        if m['previous_state_sha256']!=previous:raise ValueError('state chain')
        if k and any(m[x]!=self.meta[0][x] for x in ('run_id','boot_id','evidence')):raise ValueError('mixed run')
    def accept(self,raw):
        digest=sha(raw)
        with self.lock:
            if digest in self.digests:
                k=self.digests.index(digest)
                return dict(step_id=k,sha256=digest,durable=True,duplicate=True)
            m,_,_=unpack(raw,self.config);k=m['step_id']
            if k<len(self.meta):raise ValueError('conflicting duplicate')
            if self.final is not None:raise ValueError('session finished')
            self._next(m)
            dest=self.path/('%06d.packet'%k)
            if dest.exists():
                if sha(dest.read_bytes())!=digest:raise ValueError('conflict with persisted record after storage error')
            else:atomic(dest,raw)
            self.meta.append(m);self.digests.append(digest)
            return dict(step_id=k,sha256=digest,durable=True,duplicate=False)
    def _check_finish(self,obj):
        if (obj['session_id']!=self.config['session_id'] or obj['completed_steps']!=len(self.meta) or
            not self.meta or obj['run_id']!=self.meta[0]['run_id'] or obj['boot_id']!=self.meta[0]['boot_id'] or
            obj['packet_sha256']!=self.digests):raise ValueError('finish identity/count')
        if obj['status']=='NORMAL_CAMERA_CLOSED_ALL_STEPS_SAVED_ORACLE_PENDING':
            if len(self.meta)!=self.config['max_steps'] or not obj['camera_closed']:raise ValueError('false completion')
        elif obj['status']=='ALL_STEPS_SAVED_CAMERA_CLOSE_PENDING':
            if self.config.get('duration_s') is not None:
                from duration_run import validate_receipt
                validate_receipt(obj.get('duration',{}),self.config,len(self.meta))
            elif len(self.meta)!=self.config['max_steps']:raise ValueError('false fixed-count completion')
            if (obj['camera_closed'] is not False or obj.get('hardware_completed_steps')!=len(self.meta) or obj.get('error') is not None):
                raise ValueError('false neural completion')
        elif obj['status']!='STOPPED_KEEP_KERNEL_AND_BUFFERS':raise ValueError('finish status')
    def finish(self,obj):
        with self.lock:
            self._check_finish(obj)
            if self.final is not None and canonical(self.final)!=canonical(obj):raise ValueError('conflicting finish')
            if self.final is None:
                dest=self.path/'FINISH.json'
                if dest.exists() and dest.read_bytes()!=canonical(obj):raise ValueError('conflict with saved finish')
                if not dest.exists():atomic(dest,canonical(obj))
                self.final=obj
        return dict(durable=True,completed_steps=len(self.meta))
    def _check_camera_close(self,obj):
        if self.final is None or self.final['status']!='ALL_STEPS_SAVED_CAMERA_CLOSE_PENDING':raise ValueError('no completed neural receipt')
        if obj.get('schema')!='line11-camera-close/v1':raise ValueError('camera receipt schema')
        for key in ('session_id','run_id','boot_id','completed_steps','packet_sha256'):
            if obj.get(key)!=self.final[key]:raise ValueError('camera receipt identity')
        if obj.get('status') not in ('CLOSED','FAILED'):raise ValueError('camera receipt status')
        if obj.get('camera_closed') is not (obj['status']=='CLOSED'):raise ValueError('camera close flag')
        if obj['status']=='CLOSED' and obj.get('error') is not None:raise ValueError('camera close error')
        if obj['status']=='FAILED' and not isinstance(obj.get('error'),str):raise ValueError('missing close error')
    def record_camera_close(self,obj):
        with self.lock:
            self._check_camera_close(obj)
            if self.camera_close is not None and canonical(self.camera_close)!=canonical(obj):raise ValueError('conflicting camera receipt')
            dest=self.path/'CAMERA_CLOSE.json'
            if dest.exists() and dest.read_bytes()!=canonical(obj):raise ValueError('conflicting saved camera receipt')
            if not dest.exists():atomic(dest,canonical(obj))
            self.camera_close=obj
        return dict(durable=True,status=obj['status'])
    def read(self,k):return unpack((self.path/('%06d.packet'%k)).read_bytes(),self.config)
