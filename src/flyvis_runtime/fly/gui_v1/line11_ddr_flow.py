"""Original DecoderGAVP on CPU, isolated from GUI/GPU and the PL STEP thread.

The child decodes ONLY supplied complete states. It never advances neurons,
loads a saved response, connects to a board, or starts a GPU.
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import queue
import struct
import subprocess
import sys
import threading
import time

import numpy as np

HERE = Path(__file__).resolve().parent
SUPPORT = HERE.parent.parent/'fpga/flyvis-gpu-validation/t4t5_decoder_support_20261011'
SERVICE_SHA = 'cfb6e89f1ddc5cbf39d0d670810411b4117a815b09b31c10cb2a9e3943132c30'
CONTRACT_SHA = '60a0987d727f028be4b4928b8b4905bac39c9b0195b5230f8db4825a8ff1d22f'


def digest(raw):return hashlib.sha256(raw).hexdigest()


def archive_frame(output,snapshot,result,flow):
    """Durable writes run in the consumer thread, never in PL reception/STEP."""
    m,inp,bits,received,_=snapshot;base=Path(output)/('%06d'%m['frame_id'])
    record=dict(result,input_sha256=digest(inp),received_pc_ns=received,stream_metadata=dict(m),
                evidence='RECEIVED_STATE_CPU_OFFICIAL_DECODER; NOT_NEW_NEURAL_COMPUTATION')
    files={'.state.bin':bits,'.input.bin':inp,'.flow.bin':flow,
           '.json':(json.dumps(record,indent=2)+'\n').encode()}
    for suffix,data in files.items():
        with base.with_suffix(suffix).open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())


class CPUDecoder:
    def init__(self, scratch):
        scratch=Path(scratch)
        for k,v in dict(CUDA_VISIBLE_DEVICES='-1',PYTHON_DOTENV_DISABLED='1',OMP_NUM_THREADS='1',
                        MKL_NUM_THREADS='1',MPLBACKEND='Agg',TIMEZONE='Asia/Shanghai',
                        FLYVIS_ROOT_DIR=str(scratch/'flyvis'),MPLCONFIGDIR=str(scratch/'mpl')).items():
            os.environ[k]=v
        from types import SimpleNamespace
        from static_connectome import prepare_static_connectome
        data=json.loads((HERE/'live_registry.json').read_text(encoding='utf-8'))
        prepare_static_connectome(SimpleNamespace(data=data,pins=data['pins']),scratch/'flyvis/connectome',
                                  'DDR_ON60_CPU_DECODER',package_root=HERE.parent/'upstream/flyvis/flyvis')
        import torch
        torch.set_num_threads(1);torch.set_num_interop_threads(1)
        torch.set_default_device('cpu');torch.set_flush_denormal(False)
        torch.use_deterministic_algorithms(True)
        if torch.cuda.is_initialized():raise ValueError('CPU_DECODER_CUDA_INITIALIZED')
        if digest((SUPPORT/'service.py').read_bytes())!=SERVICE_SHA or digest((SUPPORT/'FULL_DECODER_CONTRACT.json').read_bytes())!=CONTRACT_SHA:
            raise ValueError('OFFICIAL_DECODER_CONTRACT_CHANGED')
        spec=importlib.util.spec_from_file_location('line2_official_decoder',SUPPORT/'service.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        self.service=module.OfficialDecoderService(HERE.parent/'data_cpu/results/flow/0000/000',
            SUPPORT/'FULL_DECODER_CONTRACT.json',device='cpu',check_scope=lambda operation:None)
        self.torch=torch
        self.identity=dict(decoder='DecoderGAVP',decoder_source_sha256=data['pins']['decoder']['sha256'],
            checkpoint_sha256=self.service.contract['model']['checkpoint_sha256'],recursive_eval=True,
            decoder_state_sha256=self.service.contract['decoder_state_sha256'],device='cpu',
            contract_sha256=CONTRACT_SHA,service_sha256=SERVICE_SHA,
            meaning='ORIGINAL_OFFICIAL_DECODER_ON_COMPLETE_RECEIVED_STATE; NO_NEURAL_UPDATE')

    def decode(self, states):
        a=np.asarray(states)
        if a.dtype!=np.float32 or a.ndim!=2 or a.shape[1]!=45669 or not 1<=len(a)<=32 or not np.isfinite(a).all():
            raise ValueError('DECODER_COMPLETE_FP32_STATE_REQUIRED')
        self.service.assert_weights_unchanged()
        with self.torch.no_grad():
            result=self.service.decoder(self.torch.from_numpy(a.copy()[None])).detach().cpu().numpy()[0].copy()
        self.service.assert_weights_unchanged()
        if result.shape!=(len(a),2,721) or not np.isfinite(result).all() or self.torch.cuda.is_initialized():
            raise ValueError('CPU_DECODER_OUTPUT_OR_DEVICE')
        return result


def send(pipe, meta, raw=b''):
    data=json.dumps(meta,separators=(',',':'),allow_nan=False).encode()
    pipe.write(struct.pack('<I',len(data))+data+raw);pipe.flush()


def read_exact(pipe, n):
    chunks=[]
    while n:
        b=pipe.read(n)
        if not b:raise EOFError('CPU_DECODER_PIPE_CLOSED')
        chunks.append(b);n-=len(b)
    return b''.join(chunks)


def receive(pipe):
    n=struct.unpack('<I',read_exact(pipe,4))[0]
    if not 0<n<=8192:raise ValueError('CPU_DECODER_METADATA_BOUND')
    return json.loads(read_exact(pipe,n))


def worker(root):
    # All upstream console output goes to a log, never into the binary pipe.
    from contextlib import redirect_stdout
    wire=sys.stdout.buffer
    with redirect_stdout(sys.stderr):decoder=CPUDecoder(root/'cache')
    send(wire,dict(status='CPU_DECODER_READY',identity=decoder.identity))
    for k in range(485):
        meta=receive(sys.stdin.buffer)
        if meta.get('stop'):return
        raw=read_exact(sys.stdin.buffer,182676)
        if meta['frame_id']!=k or digest(raw)!=meta['full_state_sha256']:raise ValueError('CPU_DECODER_STATE_BINDING')
        before=time.perf_counter_ns()
        with redirect_stdout(sys.stderr):value=decoder.decode(np.frombuffer(raw,dtype='<f4').reshape(1,45669))[0]
        flow=value.astype('<f4',copy=False).tobytes()
        send(wire,dict(meta,**decoder.identity,flow_sha256=digest(flow),decode_ns=time.perf_counter_ns()-before),flow)


class FlowConsumer:
    """One finite485-state queue; computation/reception never waits for decode/disk."""
    def init__(self, output, callback):
        self.output=Path(output);self.callback=callback
        self.queue=queue.Queue(maxsize=485);self.stop=threading.Event()
        self.accepted=self.completed=0;self.error=None;self.state='NOT_STARTED'
        self.process=None;self.last_binding=None

    def start(self):
        self.output.mkdir(parents=True,exist_ok=False);self.state='LOADING_CPU_DECODER'
        self.thread=threading.Thread(target=self._run,name='line2-official-flow',daemon=True);self.thread.start()

    def submit(self, snapshot):
        if self.error or self.stop.is_set():return
        try:
            if self.accepted>=485:raise ValueError('CPU_DECODER_WINDOW_EXCEEDED')
            self.queue.put_nowait(snapshot);self.accepted+=1
        except (queue.Full,ValueError) as e:self.error=str(e) or 'CPU_DECODER_QUEUE_FULL';self.state='FAILED'

    def status(self):
        return dict(status=self.state,accepted=self.accepted,decoded=self.completed,pending=self.accepted-self.completed,
                    error=self.error,device='cpu',last_binding=self.last_binding,blocks_PL_STEP=False)

    def _run(self):
        try:
            with (self.output/'CPU_DECODER.log').open('xb') as log:
                self.process=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'--worker',str(self.output)],
                    stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=log,
                    cwd=str(HERE.parent),creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
                if self.stop.is_set():raise ValueError('CPU_DECODER_CANCELLED')
                hello=receive(self.process.stdout)
                if hello['status']!='CPU_DECODER_READY':raise ValueError('CPU_DECODER_NOT_READY')
                self.state='READY'
                for k in range(485):
                    while not self.stop.is_set():
                        try:snapshot=self.queue.get(timeout=.1);break
                        except queue.Empty:continue
                    else:return
                    m,inp,bits,received,_=snapshot
                    binding=dict(run_id=m['run_id'],session_id=m['session_id'],frame_id=m['frame_id'],full_state_sha256=m['state_sha256'])
                    if binding['frame_id']!=k:raise ValueError('CPU_DECODER_QUEUE_ORDER')
                    send(self.process.stdin,binding,bits)
                    result=receive(self.process.stdout);flow=read_exact(self.process.stdout,5768)
                    if any(result.get(n)!=v for n,v in binding.items()) or digest(flow)!=result['flow_sha256']:
                        raise ValueError('CPU_DECODER_RETURN_BINDING')
                    values=np.frombuffer(flow,dtype='<f4').reshape(2,721)
                    if not np.isfinite(values).all():raise ValueError('CPU_DECODER_NONFINITE')
                    # This is actual RECEIVED state/flow, never the prepared reference.
                    archive_frame(self.output,snapshot,result,flow)
                    self.last_binding=binding;self.completed+=1
                    self.callback(snapshot,dict(values=values.tolist(),sha256=digest(flow),binding=result))
                if self.process.wait(timeout=10)!=0:raise ValueError('CPU_DECODER_CHILD_FAILED')
                (self.output/'COMPLETE.json').write_text(json.dumps(dict(status='ALL_485_RECEIVED_STATES_DECODED',
                    frames=self.completed,last_binding=self.last_binding,identity=hello['identity']),indent=2)+'\n',encoding='utf-8')
                self.state='COMPLETE'
        except Exception as e:self.error=type(e).__name__+': '+str(e);self.state='FAILED'
        finally:
            if self.process and self.process.poll() is None:
                self.process.terminate()
                try:self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:self.process.kill();self.process.wait()

    def close(self):
        self.stop.set()
        if self.process and self.process.poll() is None:self.process.terminate()
        if hasattr(self,'thread') and self.thread is not threading.current_thread():self.thread.join(5)


if __name__=='__main__':
    if len(sys.argv)!=3 or sys.argv[1]!='--worker':raise SystemExit('Explicit CPU worker only')
    worker(Path(sys.argv[2]))
