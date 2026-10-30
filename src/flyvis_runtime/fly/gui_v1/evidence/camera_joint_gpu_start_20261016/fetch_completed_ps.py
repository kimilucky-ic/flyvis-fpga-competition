"""One authenticated read-only retrieval of an already closed three-step capture."""
import base64, hashlib, json, os, sys
from pathlib import Path

GUI=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(GUI))
from live_protocol import load, require, sha, write
from joint_camera_control import board_client

root=GUI/'runtime/joint/19c681c711c94cbdacb7b953b1091611'
finish=load(root/'PS_FINISH.json')
require(finish['state']=='FINISHED_PENDING_AUDIT' and finish['requests']==finish['commits']==3 and finish['capture_closed'], 'NOT_CLOSED_THREE_STEP_CAPTURE')
out=root/('ps_retrieved_authorized' if '--authorized-network' in sys.argv else 'ps_retrieved')
out.mkdir(exist_ok=False)
client=board_client(load(root/'hardware_handoff.json'))
client.ready_id=finish['ready_id']
try:
    begin=client.request('/evidence_begin', {})
    require(begin['capture_sha256']==finish['PS_capture_sha256'] and 0<begin['capture_bytes']<=512*1024*1024, 'PS_FINAL_CAPTURE_IDENTITY')
    write(out/'begin.json',begin)
    offset=0
    with (out/'evidence.fvej').open('xb') as stream:
        while offset<begin['capture_bytes']:
            packet=client.request('/evidence_chunk',{'offset':offset})
            data=base64.b64decode(packet.pop('data_b64'),validate=True)
            require(packet['offset']==offset and packet['bytes']==len(data) and packet['capture_bytes']==begin['capture_bytes'], 'CHUNK_BOUNDS')
            require(hashlib.sha256(data).hexdigest()==packet['chunk_sha256'], 'CHUNK_SHA')
            stream.write(data);stream.flush();os.fsync(stream.fileno())
            write(out/('chunk_%d.json'%offset),packet)
            offset+=len(data)
    require(sha(out/'evidence.fvej')==finish['PS_capture_sha256'], 'PS_WHOLE_CAPTURE_SHA')
    write(out/'RESULT.json',dict(status='PASS_READ_ONLY_CAPTURE_RETRIEVAL',run_id=finish['run_id'],bytes=offset,sha256=sha(out/'evidence.fvej'),neural_requests=0,automatic_retry=False))
    print('PS_CAPTURE_RETRIEVED',offset,sha(out/'evidence.fvej'),flush=True)
except BaseException as error:
    write(out/'ERROR.json',dict(error=str(error),automatic_retry=False))
    raise
