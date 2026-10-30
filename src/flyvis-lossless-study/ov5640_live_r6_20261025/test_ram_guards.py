from pathlib import Path
import json,sys
from types import SimpleNamespace
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P/'bundle'))
import ram_records
from capture_binding import BoundSteps
from live_protocol import Store
from official_bridge import OfficialBridge
import numpy as np
cfg=json.loads((P/'pc/session.json').read_text());t=Path((P/'evidence/latest_cpu.txt').read_text());s=Store(t/'receiver',cfg);m,_,r=s.read(0);record=(t/'receiver/000000.packet').read_bytes()[-188416:]
out=P/'evidence/negative_ram_verified';out.mkdir();tests=[]
for limit,expected in [(100,0),(8192,1)]:
 root=out/str(limit);root.mkdir();j=ram_records.RamRecords(root,limit=limit);ram_records.CURRENT=j
 binding=BoundSteps(root/'bound',2);j.start();calls=[]
 def adv(ib):calls.append(ib);return SimpleNamespace(frame_id=0,sequence=1)
 try:binding.step((0,0,b'pixel_fixture'),lambda _:r.input_bits,adv,lambda _:(r,record))
 except MemoryError:pass
 else:raise AssertionError('capacity failure ignored')
 assert len(calls)==expected and binding.failed
 try:binding.step((1,1,b'pixel_fixture'),lambda _:r.input_bits,adv,lambda _:(r,record))
 except RuntimeError:pass
 else:raise AssertionError('continued after memory failure')
 assert len(calls)==expected;tests.append(dict(memory_limit=limit,STEP_calls=expected,blocked_next=True))
ram_records.CURRENT=None
video=SimpleNamespace(readframe=lambda:np.zeros((480,800,3),np.uint8))
bridge=OfficialBridge(video,SimpleNamespace(),SimpleNamespace(),out/'wrong_camera',32)
try:bridge.step()
except ValueError:pass
else:raise AssertionError('wrong camera geometry accepted')
assert bridge.failed and bridge.binding.next==0 and bridge.held_frame is not None
tests.append(dict(wrong800x480_frame_rejected_before_STEP=True,held_frame_retained=True))
(out/'RESULT.json').write_text(json.dumps(dict(status='PASS_CPU_RAM_LIMIT_AND_CAMERA_SHAPE_GUARDS',tests=tests,board_actions=0),indent=2))
print('PASS',tests)
