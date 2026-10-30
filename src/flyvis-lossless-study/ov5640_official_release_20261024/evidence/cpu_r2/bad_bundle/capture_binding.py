"""CPU-testable capture ownership and durable input-to-step binding.

A hardware integration MUST program only grant() slots, verify VDMA completion,
then invalidate/cache-barrier before complete(). Circular overwrite is forbidden.
No hardware backend or display callback is created here.
"""
import hashlib,json,os,struct,threading
from pathlib import Path

class CapturePool:
    def init__(self, frame_bytes, slots=3):
        if frame_bytes<=0 or slots<2: raise ValueError('invalid capture pool')
        self.size=frame_bytes;self.states=['FREE']*slots;self.generations=[0]*slots
        self.frames={};self.lock=threading.Lock();self.failed=False;self.last_id=-1
    def grant(self):
        with self.lock:
            if self.failed: raise RuntimeError('capture failed')
            # Only unused frames may be dropped. HELD and WRITING never reused.
            choices=[i for i,s in enumerate(self.states) if s=='FREE']
            if not choices: choices=sorted((i for i,s in enumerate(self.states) if s=='READY'),key=lambda i:self.frames[i][0])
            if not choices: return None
            i=choices[0];self.generations[i]+=1;self.states[i]='WRITING';self.frames.pop(i,None)
            return (i,self.generations[i])
    def complete(self,token,source_id,timestamp_ns,raw):
        with self.lock:
            try:
                i,g=token
                if self.failed or self.states[i]!='WRITING' or self.generations[i]!=g: raise RuntimeError('stale capture completion')
                if type(source_id) is not int or source_id<=self.last_id or timestamp_ns<0: raise RuntimeError('invalid source identity')
                data=bytes(raw)
                if len(data)!=self.size: raise RuntimeError('incomplete frame')
                self.frames[i]=(source_id,timestamp_ns,data);self.last_id=source_id;self.states[i]='READY'
            except BaseException: self.failed=True;raise
    def acquire_latest(self):
        with self.lock:
            if self.failed: raise RuntimeError('capture failed')
            ready=[i for i,s in enumerate(self.states) if s=='READY']
            if not ready: return None
            i=max(ready,key=lambda i:self.frames[i][0]);self.states[i]='HELD'
            return (i,self.generations[i]),self.frames[i]
    def release(self,token):
        with self.lock:
            i,g=token
            if self.states[i]!='HELD' or self.generations[i]!=g: raise RuntimeError('invalid frame release')
            self.states[i]='FREE';del self.frames[i]

def save_new(path,data):
    with Path(path).open('xb') as f:
        f.write(data);f.flush();os.fsync(f.fileno())

def save_json(path,value): save_new(path,(json.dumps(value,sort_keys=True,indent=2)+'\n').encode())
def sha(data): return hashlib.sha256(data).hexdigest()

class BoundSteps:
    """One producer, bounded immutable records. Actual PL input checked post-commit.

    advance(bytes) is existing DdrControl.advance. fetch(descriptor) returns a
    decoded immutable record with frame_id, input_bits, state_bits. Oracle checks
    belong to the existing full-state auditor; this layer does NOT claim them.
    """
    def init__(self,path,capacity,first_step=0):
        if capacity<1 or first_step<0: raise ValueError('invalid bounded session')
        self.path=Path(path);self.path.mkdir(exist_ok=False)
        self.capacity,self.first,self.next=capacity,first_step,first_step
        self.failed=False;self.lock=threading.Lock()
    def step(self,source,render,advance,fetch):
        with self.lock:
            if self.failed: raise RuntimeError('uncertain session; no retry')
            if self.next-self.first>=self.capacity: raise RuntimeError('audit capacity reached before STEP')
            sid,stamp,frame=source;frame=bytes(frame)
            step=self.next;directory=self.path/('%06d'%step)
            try:
                directory.mkdir(exist_ok=False)
                inputs=bytes(render(frame))
                if len(inputs)!=2884: raise ValueError('exactly 721 FP32 words required')
                values=struct.unpack('<721f',inputs)
                if any(not 0<=v<=1 for v in values): raise ValueError('finite intensity range required')
                save_new(directory/'source_frame.bin',frame)
                save_new(directory/'input.bin',inputs)
                metadata=dict(step_id=step,source_frame_id=sid,source_timestamp_ns=stamp,
                              frame_sha256=sha(frame),input_sha256=sha(inputs),input_words=721,
                              evidence='PREPARED_INPUT_NOT_COMPLETED_NEURAL_STEP')
                save_json(directory/'PREPARED.json',metadata)
                descriptor=advance(inputs)
                if descriptor.frame_id!=step or descriptor.sequence!=step-self.first+1: raise RuntimeError('neural step identity mismatch')
                record=fetch(descriptor)
                # Preserve raw returned evidence even when mismatch is detected.
                save_new(directory/'actual_input.bin',record.input_bits)
                save_new(directory/'actual_state.bin',record.state_bits)
                if record.frame_id!=step or record.input_bits!=inputs or len(record.state_bits)!=45669*4:
                    raise RuntimeError('published record identity/input/state-length mismatch')
                save_json(directory/'COMMITTED.json',dict(metadata,sequence=descriptor.sequence,
                    state_sha256=sha(record.state_bits),evidence='INPUT_BINDING_ONLY_FULL_STATE_ORACLE_PENDING'))
                self.next+=1
                return descriptor
            except BaseException as exc:
                self.failed=True
                try:
                    save_json(directory/'IN_DOUBT.json',dict(step_id=step,error=type(exc).__name__+': '+str(exc),automatic_retry=False))
                except BaseException:
                    pass  # Disk failure cannot permit another STEP.
                raise

    def process_latest(self,pool,render,advance,fetch):
        # Keep the lease on uncertainty. A successful immutable copy/commit may
        # release it. No display locks, callbacks or ACKs participate.
        if self.failed or self.next-self.first>=self.capacity:
            raise RuntimeError('session stopped before acquiring another frame')
        leased=pool.acquire_latest()
        if leased is None: return None
        token,source=leased
        result=self.step(source,render,advance,fetch)
        pool.release(token)
        return result
