"""Extract saved real joint values for CPU JS tests; does NOT simulate a camera run."""
import base64
import io
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import numpy as np
from PIL import Image
GUI=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(GUI))
from live_protocol import Registry,load
from spatial_state import SpatialRegistry
from projection_startup import load_static_projection
from live_worker import import_file
from joint_camera_protocol import digest,PROFILE,POLICY,TEST

OUT=Path(__file__).resolve().parent/'display_fixture'
BASE=GUI.parent.parent/'fpga/flyvis-fpga/t4t5_neurononly_20261011/soc_a_20261012/joint_latency485_20261016'
RUN='c708f1c9bac14c07ac8f56d59678b95a'


def main():
    OUT.mkdir(exist_ok=False)
    reg,spatial=Registry(),SpatialRegistry()
    health,cache=load_static_projection(SimpleNamespace(adapter=SimpleNamespace(registry=reg),spatial=spatial))
    health['projection_cache']['url']='/api/joint-camera/cache'
    health['consumer_kind']='JOINT_CAMERA_PENDING_AUDIT'
    reader_module=import_file('camera_display_fixture_reader',BASE/'a3latency485/evidence_journal.py')
    reader=reader_module.JournalReader(BASE/'workers'/RUN/'pc/evidence.fvej')
    report=load(BASE/'runs'/RUN/'FINAL_RESULT.json')
    packets=[];expected=[]
    raw=io.BytesIO();Image.new('RGB',(8,8),(127,127,127)).save(raw,format='PNG');png=raw.getvalue()
    for k in (0,213,284,484):
        def array(prefix):return np.load(io.BytesIO(reader.read(f'{prefix}_{k}.npy')),allow_pickle=False)
        x,values,flow=array('input_721'),array('spatial'),array('flow')
        r=report['rows'][k]
        hardware=dict(ASID='12'*16,boot_id='CPU_PROTOCOL_ONLY',server_session='CPU_PROTOCOL_ONLY',
            bit_sha256=report['BIT_SHA256'],hwh_sha256=report['HWH_SHA256'])
        p=dict(schema='flyvis-camera-joint-output/v1',run_id=RUN,session_id='CPU_TEST_ONLY',
            model=report['model'],mapping_sha256=report['mapping_sha256'],hardware=hardware,
            execution_kind=TEST,source_kind='recorded_protocol_fixture',actual_new_computation=False,
            serial=k+1,step_id=k,state_token=k+1,input_time_s=k*.005,activity_time_s=k*.005+.005,wall_elapsed_s=0,
            evidence_level='CPU_PROTOCOL_REPLAY_ONLY',numerical_profile=PROFILE,
            input_hex=x.tolist(),preview_png=base64.b64encode(png).decode(),
            source=dict(run_id=RUN,source_kind='recorded_protocol_fixture',sequence=k,received_monotonic_ns=1,
                relative_s=0,png_sha256=digest(png),hex_values_sha256=digest(x.tobytes()),timestamp_kind='Windows_receipt_not_sensor'),
            conversion=dict(backend='ORIGINAL_PREPARED_CAMERA_INPUT_BOXEYE_CPU',dependencies_sha256='CPU_TEST_ONLY'),
            temporal_mapping=dict(policy=POLICY),flow=flow.tolist(),flow_sha256=digest(flow.tobytes()),
            spatial=dict(run_id=RUN,step_id=k,state_token=k+1,map_sha256=spatial.digest,values=values.tolist(),values_sha256=digest(values.tobytes())),
            transaction=dict(status='ACK_MATCHED_AND_PUBLISHED',step_id=k,ASID=hardware['ASID'],txn='34'*16,
                unified_commit_sha256=r['commit_sha'],integer_error=0,core_cycles=r['core_cycles'],adapter_cycles=r['adapter_cycles']),
            durable=dict(barrier='STEP_PUBLISHED',sequence=k,end_offset=1,batch_sha256='0'*64),
            PL_participating_global_ids=[],PL_proven_global_ids=[],whole_run_acceptance='PENDING',REALTIME_STREAM_PASS='NOT_CLAIMED')
        means=values.reshape(8,721).mean(axis=1,dtype=np.float64)
        rgba,states=cache.render(means,health)
        expected.append(dict(raw_sha256=digest(rgba.tobytes()),means=means.tolist(),type_states=states))
        packets.append(p)
    for name,data in [('health.json',health),('packets.json',packets),('expected.json',expected),('coordinates.json',reg.uv.tolist())]:
        (OUT/name).write_text(json.dumps(data,allow_nan=False),encoding='utf-8')
    (OUT/'projection.cache').write_bytes(cache.blob)
    (OUT/'readme.txt').write_text('CPU_ONLY: four SAVED actual joint activity/flow arrays. Tiny generated PNG is protocol fixture only. Not a camera run, live service or browser acceptance.\n',encoding='utf-8')
    print(json.dumps(dict(status='SAVED_DATA_DISPLAY_FIXTURES_ONLY',steps=[0,213,284,484],new_neural_updates=0,source_run=RUN)))


if __name__=='__main__':main()
