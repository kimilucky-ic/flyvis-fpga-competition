"""Host ABI v2: canonical Q24 and an A3R1 image-bound TCP session.
Hardware ABI is unchanged. PS runtime identity is not silicon attestation.
"""
import dataclasses, hashlib, json, socket, struct, time, uuid
N=5768; WORD_BYTES=N*4; INPUT_BYTES=3*WORD_BYTES; HEADER_BYTES=256
PROFILE=0x41323401; DT_Q24=83886; DT_NS=5000000
CONFIG=bytes.fromhex('a7062049dc9b38047876c264d5a7b7408002819b41c6940cde73b326cc641a2e')
BIT_SHA='b607ea58005046f09f01bc7359c673dbd5e40b4de12b4169fca79ce88e43fd16'
HWH_SHA='54d271dc8aff904a50ca4fb0ff433f1810b0d486cf80f1daed2c204bc88d084c'
STEP,RESULT,COMMIT,ABORT,ACK,ERROR,HELLO,ATTEST=range(1,9)
VERSION=2

def digest(data):return hashlib.sha256(data).digest()
IMAGE_PAIR=digest(b'FLYVIS_A3R1_IMAGE_PAIR\0'+bytes.fromhex(BIT_SHA)+bytes.fromhex(HWH_SHA))

@dataclasses.dataclass(frozen=True)
class Header:
    op:int
    asid:bytes
    txn:bytes
    step:int
    old_sha:bytes
    payload_sha:bytes
    payload_bytes:int
    epoch:int=0
    config:bytes=CONFIG
    parent_commit:bytes=bytes(32)
    previous_txn:bytes=bytes(16)
    status:int=0
    compute_cycles:int=0
    transfer_cycles:int=0
    def pack(self):
        for name,size in [('asid',16),('txn',16),('old_sha',32),('payload_sha',32),('config',32),('parent_commit',32),('previous_txn',16)]:
            if len(getattr(self,name))!=size:raise ValueError(name)
        b=bytearray(256)
        struct.pack_into('<4sHHII',b,0,b'FVA3',VERSION,self.op,256,0)
        b[16:32]=self.asid;b[32:48]=self.txn
        struct.pack_into('<QQIIII',b,48,self.step,self.epoch,N,PROFILE,DT_Q24,DT_NS)
        struct.pack_into('<IIII',b,80,self.payload_bytes,0,WORD_BYTES if self.op==STEP else 0,2*WORD_BYTES if self.op==STEP else 0)
        b[96:128]=self.config;b[128:160]=self.old_sha;b[160:192]=self.payload_sha
        b[192:224]=self.parent_commit;b[224:240]=self.previous_txn
        struct.pack_into('<IIII',b,240,self.status,0,self.compute_cycles,self.transfer_cycles)
        return bytes(b)
    @classmethod
    def unpack(cls,b):
        if len(b)!=256:raise ValueError('header length')
        magic,version,op,length,flags=struct.unpack_from('<4sHHII',b)
        step,epoch,n,profile,dt,dtns=struct.unpack_from('<QQIIII',b,48)
        size,old,chem,x=struct.unpack_from('<IIII',b,80)
        status,reserved,cycles,transfer=struct.unpack_from('<IIII',b,240)
        if (magic,version,length,flags,n,profile,dt,dtns,reserved)!=(b'FVA3',VERSION,256,0,N,PROFILE,DT_Q24,DT_NS,0):raise ValueError('ABI/profile/dt')
        sizes={STEP:INPUT_BYTES,RESULT:WORD_BYTES,COMMIT:0,ABORT:0,ACK:0,ERROR:0,HELLO:0}
        if (op==ATTEST and not 1<=size<=4096) or (op!=ATTEST and (op not in sizes or size!=sizes[op])):raise ValueError('opcode/length')
        if (old,chem,x)!=(0,WORD_BYTES if op==STEP else 0,2*WORD_BYTES if op==STEP else 0):raise ValueError('offsets')
        if b[96:128]!=CONFIG:raise ValueError('configuration')
        if op in (STEP,COMMIT,ABORT,HELLO) and (status or cycles or transfer):raise ValueError('request status')
        return cls(op,b[16:32],b[32:48],step,b[128:160],b[160:192],size,epoch,b[96:128],b[192:224],b[224:240],status,cycles,transfer)
    def identity(self):
        return (self.asid,self.txn,self.step,self.epoch,self.config,self.old_sha,self.parent_commit,self.previous_txn)

class ReceiveFailure(Exception):
    def init__(self,cause,wire):
        super().init__(str(cause));self.cause=cause;self.wire=wire

def recv_exact(sock,n,deadline=None):
    out=bytearray()
    try:
        while len(out)<n:
            if deadline is not None:
                remaining=deadline-time.monotonic()
                if remaining<=0:raise TimeoutError('frame deadline; no retry')
                sock.settimeout(remaining)
            piece=sock.recv(n-len(out))
            if not piece:raise EOFError('truncated frame; no automatic retry')
            out.extend(piece)
        return bytes(out)
    except Exception as exc:raise ReceiveFailure(exc,bytes(out)) from exc

def recv_frame(sock,observer=None,deadline=None):
    raw=b''; recorded=False
    if deadline is None:deadline=time.monotonic()+5
    try:
        raw=recv_exact(sock,256,deadline);h=Header.unpack(raw)
        try:payload=recv_exact(sock,h.payload_bytes,deadline)
        except ReceiveFailure as exc:raise ReceiveFailure(exc.cause,raw+exc.wire) from exc
        raw+=payload
        if observer:observer('rx',raw)
        recorded=True
        if digest(payload)!=h.payload_sha:raise ValueError('payload SHA mismatch')
        return h,payload
    except ReceiveFailure as exc:
        if observer:observer('rx_incomplete',exc.wire)
        raise
    except Exception:
        if not recorded and observer:observer('rx_rejected_header',raw)
        raise

def send_frame(sock,h,payload=b'',observer=None):
    if len(payload)!=h.payload_bytes or digest(payload)!=h.payload_sha:raise ValueError('invalid outgoing frame')
    raw=h.pack()+payload
    if observer:observer('tx_intent',raw)
    sock.sendall(raw)

def validate_words(payload):
    if len(payload)%4:raise ValueError('unaligned words')
    if any(v<-(1<<30) or v>=(1<<30) for (v,) in struct.iter_unpack('<i',payload)):raise ValueError('signed31 Q24 range')

def encode_activity(values):
    import math
    out=bytearray()
    for value in values:
        value=float(value)
        if not math.isfinite(value):raise ValueError('nonfinite activity')
        magnitude=math.floor(abs(value)*(1<<24)+0.5);q=-magnitude if value<0 else magnitude
        if not -(1<<30)<=q<(1<<30):raise ValueError('Q24 overflow')
        out.extend(struct.pack('<i',q))
    if len(out)!=WORD_BYTES:raise ValueError('H length')
    return bytes(out)

class Client:
    def init__(self,host,port=5768,observer=None):
        self.sock=None;self.pending=None;self.poisoned=False;self.observer=observer
        self.asid=uuid.uuid4().bytes
        try:
            self.sock=socket.create_connection((host,port),timeout=5);self.sock.settimeout(5)
            h=Header(HELLO,self.asid,uuid.uuid4().bytes,0,IMAGE_PAIR,digest(b''),0)
            r,payload=self._exchange(h)
            if r.op!=ATTEST or r.status or r.identity()!=h.identity() or r.compute_cycles or r.transfer_cycles:raise RuntimeError('firmware session receipt rejected')
            a=json.loads(payload.decode('utf-8'))
            if (a.get('bit_sha256'),a.get('hwh_sha256'),a.get('config_sha256'),a.get('image_pair_sha256'),a.get('asid'),a.get('hello_txn'),a.get('pynq_is_loaded'))!=(BIT_SHA,HWH_SHA,CONFIG.hex(),IMAGE_PAIR.hex(),self.asid.hex(),h.txn.hex(),True):raise RuntimeError('A3R1 BIT/HWH/session mismatch')
            if not a.get('boot_id') or not a.get('server_session'):raise RuntimeError('missing runtime session identity')
            self.attestation=a
        except Exception:
            self.poisoned=True
            if self.sock is not None:self.sock.close()
            raise
    def _exchange(self,h,payload=b''):
        if self.poisoned:raise RuntimeError('connection quarantined; no retry')
        try:
            deadline=time.monotonic()+5;self.sock.settimeout(5)
            send_frame(self.sock,h,payload,self.observer)
            result=recv_frame(self.sock,self.observer,deadline)
            if time.monotonic()>deadline:raise TimeoutError('PC request deadline; no retry')
            return result
        except Exception:self.poisoned=True;raise
    def step(self,old_H,chemical_H,x_H,identity):
        if self.pending is not None:raise RuntimeError('candidate awaiting COMMIT/ABORT')
        if identity.get('asid')!=self.asid:raise ValueError('unattested ASID')
        if any(len(a)!=WORD_BYTES for a in (old_H,chemical_H,x_H)):raise ValueError('array lengths')
        data=old_H+chemical_H+x_H;validate_words(data)
        h=Header(STEP,payload_bytes=len(data),payload_sha=digest(data),**identity)
        r,candidate=self._exchange(h,data)
        if r.op!=RESULT or r.status or r.identity()!=h.identity() or r.compute_cycles!=10*N+1:
            self.poisoned=True;raise RuntimeError('PL receipt rejected')
        try:validate_words(candidate)
        except Exception:self.poisoned=True;raise
        self.pending=(h,r,candidate)
        return candidate,r
    def _finish(self,h):
        ack,_=self._exchange(h)
        if ack!=dataclasses.replace(h,op=ACK):
            self.poisoned=True;raise RuntimeError('finish ACK status/full identity mismatch; COMMIT UNKNOWN')
        self.pending=None
        return ack
    def commit(self,unified_commit_sha):
        if self.pending is None:raise RuntimeError('no pending candidate')
        if len(unified_commit_sha)!=32 or unified_commit_sha==bytes(32):raise ValueError('COMMIT digest')
        h,_,_=self.pending
        return self._finish(dataclasses.replace(h,op=COMMIT,payload_bytes=0,payload_sha=digest(b''),parent_commit=unified_commit_sha))
    def abort(self):
        # Explicit coordinator command; replay never calls this on failure.
        if self.pending is None:raise RuntimeError('no pending candidate')
        h,_,_=self.pending
        return self._finish(dataclasses.replace(h,op=ABORT,payload_bytes=0,payload_sha=digest(b'')))
    def close(self):
        if self.sock is not None:self.sock.close()
