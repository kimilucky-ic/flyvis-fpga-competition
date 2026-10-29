"""A3R1 only. Import performs no PYNQ, network or board operations."""
import argparse, dataclasses, hashlib, json, mmap, os, pathlib, socket, struct, sys, threading, time, uuid
from .protocol import *
from .evidence import Evidence, save_bytes, save_json

PINNED_DRIVERS=[]  # Never release uncertain CMA buffers on an exception.

def ps_precheck(evidence):
    # Reuse line 6's PS-only check, freshly bound to this boot. No PS writes.
    values=[]
    for address in (0xf8000240,0xf8008000,0xf8008014,0xf8000240):
        if evidence:evidence.event('PS_READ_INTENT',address=address)
        fd=os.open('/dev/mem',os.O_RDONLY|os.O_SYNC)
        try:
            with mmap.mmap(fd,mmap.PAGESIZE,access=mmap.ACCESS_READ,offset=address&~(mmap.PAGESIZE-1)) as memory:
                value=struct.unpack_from('<I',memory,address&(mmap.PAGESIZE-1))[0]
        finally:os.close(fd)
        values.append(value)
        if evidence:evidence.event('PS_READ_RETURNED',address=address,value=value)
    reset,rd,wr,again=values
    if reset!=again or reset&0x01f33f00 or (rd|wr)&1:raise RuntimeError('PS reset unstable/asserted or HP0 not 64-bit; no image load')
    return dict(register_reads=4,register_writes=0,reset=reset,hp0_read=rd,hp0_write=wr)

def verify_image(bit_path, bit_sha=BIT_SHA, hwh_sha=HWH_SHA):
    # Caller cannot authorize some other firmware by supplying different hashes.
    if (bit_sha.lower(),hwh_sha.lower())!=(BIT_SHA,HWH_SHA):raise ValueError('only sealed A3R1 BIT/HWH allowed')
    bit=pathlib.Path(bit_path);hwh=bit.with_suffix('.hwh')
    for path,expected in [(bit,BIT_SHA),(hwh,HWH_SHA)]:
        if hashlib.sha256(path.read_bytes()).hexdigest()!=expected:raise ValueError('exact BIT/HWH SHA mismatch: '+str(path))
    return bit,hwh

class PLDriver:
    def init__(self,bit_path,expected_bit_sha=BIT_SHA,expected_hwh_sha=HWH_SHA,authorize_load=False,evidence=None):
        self.evidence=evidence;self.pending=None;self.committed={};self.poisoned=False
        self.last_registers={};self.src=None;self.dst=None;self.requests=0;self.commits=0
        self.server_session=uuid.uuid4().hex
        bit,hwh=verify_image(bit_path,expected_bit_sha,expected_hwh_sha)
        if not authorize_load:raise PermissionError('Exact A3R1 load and DMA authorization required')
        self.boot_id=pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()
        self._event('BEFORE_PYNQ_IMPORT',python=sys.executable,xilinx_xrt=os.environ.get('XILINX_XRT'),boot_id=self.boot_id)
        from pynq import Overlay, MMIO, allocate
        import pynq
        import numpy as np
        if pynq.__version__!='2.7.0':raise RuntimeError('different PYNQ version from line 6 verified environment')
        self._event('PS_PRECHECK_COMPLETE',**ps_precheck(self.evidence))
        self._event('BEFORE_METADATA_PARSE',bit_sha256=BIT_SHA,hwh_sha256=HWH_SHA)
        self.overlay=Overlay(str(bit),download=False)
        dma_ip=self.overlay.ip_dict.get('dma',{})
        core_ip=self.overlay.ip_dict.get('neuron_a_core',{})
        if int(dma_ip.get('phys_addr',-1))!=0x40400000 or int(core_ip.get('phys_addr',-1))!=0x43c10000:raise RuntimeError('PYNQ DMA/core metadata address mismatch')
        self._event('LOAD_ATTEMPT_CONSUMED',bit=str(bit),bit_sha256=BIT_SHA,hwh_sha256=HWH_SHA,clock_dict=self.overlay.clock_dict)
        start=time.monotonic_ns()
        self.overlay.download()  # Exactly one download. No retry branch.
        if not self.overlay.is_loaded():raise RuntimeError('PYNQ loaded identity mismatch')
        self._event('LOAD_RETURNED',elapsed_ns=time.monotonic_ns()-start,timestamp=str(self.overlay.timestamp),pynq_version=pynq.__version__)
        self.reg=MMIO(0x43C10000,0x100);self.dma=MMIO(0x40400000,0x100)
        if tuple(self._read('reg',i) for i in (0,4,8))!=(0x33415646,1,N):raise RuntimeError('loaded ABI mismatch')
        fixed=b''.join(self._read('reg',0xe0+i*4).to_bytes(4,'big') for i in range(8))
        if fixed!=CONFIG or self._read('reg',0x14)!=0 or self._read('reg',0x18)!=0:raise RuntimeError('loaded config/initial state mismatch')
        self.src=allocate((3*N,),dtype=np.int32);self.dst=allocate((N,),dtype=np.int32)
        src=int(self.src.device_address);dst=int(self.dst.device_address)
        if src%64 or dst%64 or src<0 or dst<0 or src+INPUT_BYTES>1<<32 or dst+WORD_BYTES>1<<32 or not (src+INPUT_BYTES<=dst or dst+WORD_BYTES<=src):raise RuntimeError('DMA buffers alignment/address/overlap')
        self._event('BUFFERS_ALLOCATED',src=src,dst=dst,input_bytes=INPUT_BYTES,output_bytes=WORD_BYTES,src_coherent=bool(self.src.coherent),dst_coherent=bool(self.dst.coherent))
        self.np=np
        # This initial reset belongs to the newly loaded DMA, not error recovery.
        self._write('dma',0,4);self._wait(lambda:self._read('dma',0)&4==0)
        self._write('dma',0,1);self._write('dma',0x30,1)
        self._event('READY_FOR_ONE_TCP_SESSION',server_session=self.server_session,request_limit=3)

    def _event(self,event,**values):
        if self.evidence:self.evidence.event(event,**values)
    def _read(self,which,offset):
        self._event('MMIO_READ_INTENT',bank=which,offset=offset)
        value=int(getattr(self,which).read(offset));self.last_registers[f'{which}:{offset:02x}']=value
        self._event('MMIO_READ_RETURNED',bank=which,offset=offset,value=value)
        return value
    def _write(self,which,offset,value):
        self._event('MMIO_WRITE_INTENT',bank=which,offset=offset,value=int(value))
        getattr(self,which).write(offset,int(value))
        self._event('MMIO_WRITE_RETURNED',bank=which,offset=offset,value=int(value))
    def _wait(self,predicate,seconds=1):
        deadline=time.monotonic()+seconds
        while True:
            complete=predicate()
            if time.monotonic()>deadline:raise TimeoutError('bounded DMA/PL wait; no retry/reset')
            if complete:return
            time.sleep(0.001)
    def _sha_regs(self,offset,data):
        for i in range(0,len(data),4):self._write('reg',offset+i,int.from_bytes(data[i:i+4],'big'))
    def runtime_check(self):
        if self.poisoned:raise RuntimeError('driver quarantined')
        if pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()!=self.boot_id or not self.overlay.is_loaded():raise RuntimeError('boot/loaded overlay changed')
    def attest(self,h):
        self.runtime_check()
        if h!=Header(HELLO,h.asid,h.txn,0,IMAGE_PAIR,digest(b''),0):raise ValueError('HELLO identity/image binding')
        return dict(bit_sha256=BIT_SHA,hwh_sha256=HWH_SHA,config_sha256=CONFIG.hex(),image_pair_sha256=IMAGE_PAIR.hex(),asid=h.asid.hex(),hello_txn=h.txn.hex(),server_session=self.server_session,boot_id=self.boot_id,pynq_is_loaded=True,bitfile_name=str(self.overlay.bitfile_name),pynq_timestamp=str(self.overlay.timestamp),identity_scope='VERIFIED_FILES_ONE_DOWNLOAD_PYNQ_RUNTIME; NOT_SILICON_ATTESTATION')

    def run(self,h,payload):
        if self.poisoned or self.pending is not None or self.requests>=3:raise RuntimeError('driver quarantined/pending/request limit')
        validate_words(payload)
        if h.op!=STEP or len(payload)!=INPUT_BYTES or digest(payload)!=h.payload_sha:raise ValueError('input integrity')
        prev=self.committed.get(h.asid)
        if prev and (h.step!=prev[0]+1 or h.epoch!=prev[4] or payload[:WORD_BYTES]!=prev[1] or h.parent_commit!=prev[2] or h.previous_txn!=prev[3]):raise ValueError('canonical PL recurrence/COMMIT chain mismatch')
        if not prev and (h.parent_commit!=bytes(32) or h.previous_txn!=bytes(16)):raise ValueError('first COMMIT chain')
        try:
            self.runtime_check()
            if self.evidence:save_bytes(self.evidence.directory/f'request_{self.requests}.bin',h.pack()+payload)
            self._event('REQUEST_ACCEPTED',step=h.step,txn=h.txn.hex(),asid=h.asid.hex(),payload_sha=h.payload_sha.hex())
            if self._read('reg',0x14)!=0 or self._read('reg',0x18)!=0:raise RuntimeError('request requires clean IDLE')
            ps_start=time.monotonic_ns()
            self.src[:]=self.np.frombuffer(payload,dtype='<i4');self.src.flush()
            self.dst.fill(self.np.int32(0x5a5a5a5a));self.dst.flush()
            flush_end=time.monotonic_ns()
            self._write('reg',0x20,PROFILE);self._write('reg',0x24,DT_Q24);self._write('reg',0x28,DT_NS)
            for offset,value in [(0x30,h.step),(0x38,h.epoch)]:
                self._write('reg',offset,value&0xffffffff);self._write('reg',offset+4,value>>32)
            self._sha_regs(0x40,h.asid);self._sha_regs(0x50,h.txn)
            self._sha_regs(0x60,h.config);self._sha_regs(0x80,h.old_sha);self._sha_regs(0xa0,h.payload_sha)
            # Input/candidate buffers stay pinned on every uncertain outcome.
            self._write('dma',0x48,self.dst.device_address);self._write('dma',0x4c,0)
            self._write('dma',0x18,self.src.device_address);self._write('dma',0x1c,0)
            self._event('DMA_LAUNCH_INTENT',commands=[['dma',0x58,WORD_BYTES],['reg',0x10,1],['dma',0x28,INPUT_BYTES]])
            start=time.monotonic_ns()
            # No filesystem waits between ARM and MM2S: PL watchdog is 100ms.
            self.dma.write(0x58,WORD_BYTES);self.reg.write(0x10,1)
            self.requests+=1;self.dma.write(0x28,INPUT_BYTES)
            self._event('DMA_LAUNCH_RETURNED',step=h.step)
            in_complete=None;compute_seen=None;out_complete=None;last=None
            deadline=time.monotonic()+1
            self._event('POLL_BEGIN',timeout_ns=1000000000)
            while True:
                # No fsync between polling reads: timings include only transition logs.
                a=int(self.dma.read(4));b=int(self.dma.read(0x34));state=int(self.reg.read(0x14));error=int(self.reg.read(0x18))
                self.last_registers.update({'dma:04':a,'dma:34':b,'reg:14':state,'reg:18':error})
                now=time.monotonic_ns()
                if a&2 and in_complete is None:in_complete=now
                if state in (5,6) and compute_seen is None:compute_seen=now
                if b&2 and state==6:out_complete=now
                if (a,b,state,error)!=last:
                    self._event('POLL_STATE',mm2s=a,s2mm=b,state=state,error=error);last=(a,b,state,error)
                if error or a&0x770 or b&0x770 or state==7:raise RuntimeError(f'PL/DMA error {error:#x} {a:#x} {b:#x}')
                if time.monotonic()>deadline:raise TimeoutError('DMA request timeout')
                if out_complete is not None:break
                time.sleep(0.001)
            self.dst.invalidate();candidate=self.dst.astype('<i4',copy=False).tobytes()
            invalidate_end=time.monotonic_ns()
            if self.evidence:save_bytes(self.evidence.directory/f'candidate_{self.requests-1}.bin',candidate)
            validate_words(candidate)
            cycles=self._read('reg',0xc8);echo=self._read('reg',0xd0)|(self._read('reg',0xd4)<<32)
            if (cycles,echo,self._read('reg',0xc0),self._read('reg',0xc4))!=(10*N+1,h.step,3*N,N):raise RuntimeError('PL counters/step mismatch')
            if (self._read('reg',0x38)|(self._read('reg',0x3c)<<32))!=h.epoch:raise RuntimeError('PL epoch mismatch')
            for offset,data in [(0x40,h.asid),(0x50,h.txn),(0x60,h.config),(0x80,h.old_sha),(0xa0,h.payload_sha)]:
                if b''.join(self._read('reg',offset+i).to_bytes(4,'big') for i in range(0,len(data),4))!=data:raise RuntimeError('PL identity echo mismatch')
            receipt=dataclasses.replace(h,op=RESULT,payload_bytes=WORD_BYTES,payload_sha=digest(candidate),compute_cycles=cycles,transfer_cycles=self._read('reg',0xcc))
            self.pending=(h,receipt,candidate)
            timing=dict(ps_dma_roundtrip_observed_ns=out_complete-start,input_idle_observed_ns=None if in_complete is None else in_complete-start,compute_done_observed_ns=None if compute_seen is None else compute_seen-start,output_after_compute_observed_ns=None if compute_seen is None else out_complete-compute_seen,input_copy_flush_ns=flush_end-ps_start,output_invalidate_copy_ns=invalidate_end-out_complete,ps_total_until_candidate_ns=time.monotonic_ns()-ps_start,poll_sleep_ns=1000000,core_cycles=cycles,adapter_elapsed_cycles=receipt.transfer_cycles,configured_clock_hz=100000000,timing_scope='PS_OBSERVATIONS_INCLUDE_POLL_LOG_IO; NOT_PRECISE_DMA_PHASE_LATENCIES')
            if self.evidence:save_json(self.evidence.directory/f'timing_{self.requests-1}.json',timing)
            self._event('CANDIDATE_READY',step=h.step,**timing)
            return receipt,candidate,timing
        except Exception:
            self.poisoned=True
            raise

    def finish(self,h,commit):
        if self.poisoned or self.pending is None:raise RuntimeError('quarantined/no pending candidate')
        original,receipt,candidate=self.pending
        if h.op!=(COMMIT if commit else ABORT) or h.payload_bytes or h.payload_sha!=digest(b'') or h.status or h.compute_cycles or h.transfer_cycles:raise ValueError('finish frame')
        if dataclasses.replace(h,parent_commit=original.parent_commit).identity()!=original.identity():raise ValueError('finish identity mismatch')
        if not commit and h.parent_commit!=original.parent_commit:raise ValueError('ABORT parent digest')
        if commit and h.parent_commit==bytes(32):raise ValueError('missing COMMIT digest')
        try:
            self.runtime_check()
            if self._read('reg',0x14)!=6 or self._read('reg',0x18)!=0:raise RuntimeError('candidate not READY/clean')
            self._write('reg',0x10,2 if commit else 4)
            self._wait(lambda:self._read('reg',0x14)==0)
            error=self._read('reg',0x18)
            if error!=(0 if commit else 0x400):raise RuntimeError('RELEASE/ABORT final error mismatch')
            # Publish canonical software state only AFTER hardware IDLE confirmation.
            if commit:
                self.committed[h.asid]=(h.step,candidate,h.parent_commit,h.txn,h.epoch)
                self.commits+=1
            self._event('RELEASE_CONFIRMED' if commit else 'ABORT_CONFIRMED',step=h.step,txn=h.txn.hex(),state=0,error=error,commit_sha=h.parent_commit.hex())
            self.pending=None
            return dataclasses.replace(h,op=ACK)
        except Exception:
            self.poisoned=True
            raise

def serve(driver,bind,port,evidence,ready=None):
    try:
        with socket.socket() as server:
            server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1);server.bind((bind,port));server.listen(1);server.settimeout(60)
            evidence.event('TCP_LISTENING',bind=bind,port=server.getsockname()[1],accept_timeout_s=60)
            if ready:ready(server.getsockname()[1])
            conn,peer=server.accept()
            with conn:
                conn.settimeout(5)
                h,payload=recv_frame(conn,evidence.wire)
                if h.op!=HELLO:raise ValueError('HELLO required before STEP')
                attestation=driver.attest(h)
                raw=json.dumps(attestation,sort_keys=True).encode('utf-8')
                send_frame(conn,dataclasses.replace(h,op=ATTEST,payload_bytes=len(raw),payload_sha=digest(raw)),raw,evidence.wire)
                asid=h.asid
                while driver.commits<3:
                    h,payload=recv_frame(conn,evidence.wire)
                    if h.asid!=asid:raise ValueError('unattested ASID')
                    if h.op==STEP:
                        result,candidate,timing=driver.run(h,payload)
                        send_frame(conn,result,candidate,evidence.wire)
                        evidence.event('CANDIDATE_SENT',step=h.step,txn=h.txn.hex(),peer=peer,**timing)
                    elif h.op in (COMMIT,ABORT):
                        ack=driver.finish(h,h.op==COMMIT)
                        send_frame(conn,ack,observer=evidence.wire)
                        evidence.event('ACK_SENT',step=h.step,txn=h.txn.hex(),op=h.op)
                        if h.op==ABORT:raise RuntimeError('explicit abort; session stops')
                    else:raise ValueError('unexpected request opcode')
                # Three requests and three confirmed releases only; no fourth accept.
                evidence.event('THREE_RELEASES_COMPLETE',requests=driver.requests,commits=driver.commits)
    except BaseException as exc:
        driver.poisoned=True
        save_json(evidence.directory/'BOARD_SERVICE_FAILED_OR_UNKNOWN.json',dict(status='FAILED_OR_UNKNOWN',error=repr(exc),last_event=evidence.last_event,last_known_registers=driver.last_registers,requests=driver.requests,commits=driver.commits,pending=driver.pending is not None,quarantined=True,automatic_retry=False,fault_register_reads=0))
        evidence.event('FAILED_OR_UNKNOWN',error=repr(exc),buffers_retained=True)
        raise

def start(bit,bind,port,directory,authorized=False):
    evidence=Evidence(directory)
    driver=PLDriver.__new__(PLDriver);PINNED_DRIVERS.append(driver)
    try:
        # Reuse line 6's actual successful Notebook environment, never set it blindly.
        if sys.executable!='/usr/local/share/pynq-venv/bin/python3' or os.environ.get('XILINX_XRT')!='/usr' or not pathlib.Path('/usr/lib/libxrt_core.so').is_file():raise RuntimeError('use the verified PYNQ Notebook/XRT environment; no load attempted')
        PLDriver.init__(driver,bit,authorize_load=authorized,evidence=evidence)
    except BaseException as exc:
        driver.poisoned=True
        save_json(evidence.directory/'START_FAILED_OR_UNKNOWN.json',dict(error=repr(exc),last_event=evidence.last_event,automatic_retry=False,buffers_retained=True))
        raise
    return driver,evidence

def start_in_notebook(bit,bind,directory,authorization):
    required='AUTHORIZE_A3R1_ONE_LOAD_INITIAL_DMA_RESET_THREE_5768_REQUESTS'
    if authorization!=required:raise PermissionError('exact operation approval required')
    driver,evidence=start(bit,bind,5768,directory,True)
    def worker():
        try:serve(driver,bind,5768,evidence)
        except BaseException as exc:print('FAILED_OR_UNKNOWN: '+repr(exc)+'; STOP, keep this kernel alive. No recovery.',flush=True)
    thread=threading.Thread(target=worker,daemon=True);thread.start()
    return driver,thread,evidence

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--bit',required=True);p.add_argument('--bind',default='127.0.0.1');p.add_argument('--port',type=int,default=5768);p.add_argument('--evidence',required=True)
    p.add_argument('--authorize-exact-load-and-dma',action='store_true');a=p.parse_args()
    if not a.authorize_exact_load_and_dma:p.error('Exact A3R1 operation approval required')
    try:
        d,e=start(a.bit,a.bind,a.port,a.evidence,True);serve(d,a.bind,a.port,e)
    except BaseException as exc:
        print('FAILED_OR_UNKNOWN: '+repr(exc)+'; networking STOPPED. Keep process alive for pinned CMA buffers.',flush=True)
        # Quarantine: zero further board/network I/O. Only operator may resolve state.
        while True:time.sleep(1)
