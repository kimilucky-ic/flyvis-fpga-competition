"""CPU-only stream identity, queue and causal clock rules. No acquisition/inference."""
import hashlib
import re
from pathlib import Path
import numpy as np
from live_protocol import HERE,load,require,sha,utc,write

CAPACITY=32
HEX_CAPACITY=64
DISPLAY_CAPACITY=16
DT=.005
MAX_LAG_S=.75


def relative_asset_path(path,root):
    value=path.relative_to(root).as_posix()
    require(not value.startswith('/') and ':' not in value and '..' not in value.split('/'),'BRIDGE_RELATIVE_PATH')
    return value


def dependencies():
    pin=load(HERE/'camera_stream_dependencies.json')
    for key,item in pin['pins'].items():require(sha(item['path'])==item['sha256'],'CAMERA_DEPENDENCY_CHANGED '+key)
    return pin


def check_control(control,session):
    require(session.get('camera_enabled') is True and session.get('camera_max_steps')==60000
        and session.get('camera_max_duration_s')==300,'CAMERA_SESSION_NOT_ENABLED')
    require(control['schema']=='flyvis-live-camera-control/v1' and control['session_id']==session['session_id'],'CAMERA_SCOPE_IDENTITY')
    require(control['source_kind']=='real_windows_camera' and control['mode']=='Full' and control['spatial_policy']=='full-field','CAMERA_PROFILE')
    require(control['max_duration_s']==300 and control['max_steps']==60000,'CAMERA_BUDGET')
    require(bool(re.fullmatch('[a-f0-9]{32}',control['run_id'])),'CAMERA_RUN_ID')


class CausalSelector:
    def init__(self):self.next_step=0;self.last_sequence=-1
    def choose(self,frames,step_id):
        require(type(step_id) is int and step_id==self.next_step,'MODEL_STEP_ORDER')
        require(frames and all(type(f['sequence']) is int for f in frames),'SOURCE_SEQUENCE_SCHEMA')
        require(all(f['sequence']>=0 and np.isfinite(f['relative_s']) and f['relative_s']>=0 for f in frames),'SOURCE_TIME_SCHEMA')
        require(all(frames[i]['sequence']<frames[i+1]['sequence'] and frames[i]['relative_s']<frames[i+1]['relative_s'] for i in range(len(frames)-1)),'SOURCE_ORDER')
        t=step_id*DT;eligible=[f for f in frames if f['relative_s']<=t]
        require(eligible,'INPUT_HISTORY_NOT_AVAILABLE_NO_FUTURE_FRAME')
        source=eligible[-1];require(source['sequence']>=self.last_sequence,'SOURCE_REVERSED')
        return source
    def commit(self,source,step_id):
        require(step_id==self.next_step,'MODEL_STEP_ORDER');self.last_sequence=source['sequence'];self.next_step+=1


def admitted_packet(packet,control,*,test_only=False):
    require(packet['schema']=='flyvis-live-camera-output/v1' and packet['run_id']==control['run_id'] and packet['session_id']==control['session_id'],'CAMERA_RESULT_IDENTITY')
    require(packet['PL_execution'] is False,'CAMERA_PL_NOT_AVAILABLE')
    if test_only:
        require(packet['execution_kind']=='CPU_PROTOCOL_TEST_ONLY' and packet['actual_new_computation'] is False
            and packet['evidence_level']=='CPU_PROTOCOL_TEST_ONLY' and packet['device']['type']=='cpu','CAMERA_TEST_LABEL_REQUIRED')
    else:
        require(packet['execution_kind']=='LIVE_CAMERA_GPU' and packet['actual_new_computation'] is True
            and packet['evidence_level']=='ACTUAL_FULL_GPU_CAMERA_STATE' and packet['device']['type']=='cuda','CAMERA_ACTUAL_GPU_REQUIRED')
    k=packet['step_id'];require(type(k) is int and k>=0 and packet['state_token']==k+1,'CAMERA_COMMIT_TOKEN')
    require(packet['input_time_s']==k*DT and packet['activity_time_s']==k*DT+DT,'CAMERA_EULER_TIME')
    require(packet['source']['relative_s']<=packet['input_time_s'],'CAMERA_FUTURE_SOURCE')
    activity=np.asarray(packet['activity']);hex_values=np.asarray(packet['input_hex'])
    require(activity.shape==(8,) and hex_values.shape==(721,) and np.isfinite(activity).all() and np.isfinite(hex_values).all(),'CAMERA_VALUE_SCHEMA')
    require(np.all((hex_values>=0)&(hex_values<=1)),'CAMERA_INPUT_RANGE')
    require(packet['source']['hex_values_sha256']==hashlib.sha256(np.asarray(hex_values,dtype=np.float32).tobytes()).hexdigest(),'CAMERA_HEX_IDENTITY')
    require(packet['binding']==control['binding'] and packet['central_global_ids']==control['central_global_ids'],'CAMERA_MODEL_NODE_BINDING')
    if packet['flow'] is not None:
        flow=np.asarray(packet['flow']);require(flow.shape==(2,721) and np.isfinite(flow).all() and packet['decoder_status']=='CONNECTED','CAMERA_FLOW_SCHEMA')
    else:require(packet['decoder_status']=='NOT_CONNECTED','CAMERA_MISSING_FLOW_LABEL')
    if 'spatial_map_sha256' in control:
        require(packet.get('spatial',{}).get('map_sha256')==control['spatial_map_sha256'],'CAMERA_SPATIAL_REQUIRED')
    return packet
