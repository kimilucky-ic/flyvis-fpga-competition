"""Actual WSL official conversion startup, synthetic grey pixels ONLY.

No camera, neural updates, board or RPC connection. Calls the real new child
entry with only gui_v1 on sys.path, reproducing its import environment.
"""
from pathlib import Path
import hashlib,json,os,sys,time
import numpy as np
HERE=Path(__file__).resolve().parents[2];sys.path.insert(0,str(HERE))
assert os.environ['CUDA_VISIBLE_DEVICES']=='-1'
import joint_camera_converter as child
import prepared_camera_input
Actual=prepared_camera_input.PreparedCameraInput
captured=[];calls=[]
class Observed(Actual):
    def render(self,image):
        value=super().render(image);captured.append(value);return value
prepared_camera_input.PreparedCameraInput=Observed
class FakeRPC:
    def init__(self,*args):pass
    def call(self,op,*args):calls.append(op);assert op=='ready'
    def close(self):calls.append('closed')
child.RPC=FakeRPC
root=Path(__file__).resolve().parent/'converter_smoke_cpu';root.mkdir(exist_ok=False)
(root/'session.json').write_text(json.dumps(dict(end_unix=time.time()+120)),encoding='utf-8')
(root/'joint_endpoint.json').write_text('{}',encoding='utf-8')
(root/'STOP_REQUEST.json').write_text('{}',encoding='utf-8')
began=time.perf_counter();child.run(root);elapsed=time.perf_counter()-began
from camera_pipeline.adapter import render_bgr_frames
reference,_,_=render_bgr_frames(np.full((1,480,640,3),127,dtype=np.uint8),spatial_policy='full-field',chunk_frames=1)
values=captured[0][0]
assert values.shape==(1,721) and np.isfinite(values).all() and calls==['ready','closed']
assert np.array_equal(values.reshape(-1),np.asarray(reference).reshape(-1))
import torch
assert not torch.cuda.is_initialized()
result=dict(status='PASS_ACTUAL_CPU_CONVERTER_STARTUP',input_kind='SYNTHETIC_GREY_STARTUP_TEST_NOT_CAMERA',
    real_child_entry=True,shape=list(values.shape),values_sha256=hashlib.sha256(values.tobytes()).hexdigest(),
    official_reference_bitwise_equal=True,startup_elapsed_s=elapsed,GPU_operations=0,camera_operations=0,
    neural_updates=0,board_operations=0,RPC_network_operations=0,
    converter_source_sha256=hashlib.sha256((HERE/'joint_camera_converter.py').read_bytes()).hexdigest())
(root.parent/'CPU_CONVERTER_RESULT.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result),flush=True)
