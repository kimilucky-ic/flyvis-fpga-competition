"""CPU-only job protocol and identity guards, shared by GUI and future WSL worker."""
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import re
import uuid
import time

import numpy as np

HERE=Path(__file__).resolve().parent
MODES=['Full','Sham','BLOCK_T4_RELEASE','BLOCK_T5_RELEASE','BLOCK_T4T5_RELEASE','CLAMP_T4T5','Python_Replacement']
TERMINAL={'COMPLETED','FAILED','CANCELLED','DISCONNECTED'}


def require(ok,message):
    if not ok:raise ValueError(message)

def utc():return datetime.now(timezone.utc).isoformat()
def load(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def host_path(value):
    text=str(value)
    if os.name!='nt' and re.match(r'^[A-Za-z]:[/\\]',text):text='/mnt/'+text[0].lower()+'/'+text[3:].replace('\\','/')
    return Path(text)
def sha(path):
    h=hashlib.sha256()
    with host_path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
    return h.hexdigest()
def canonical(obj):return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def write(path,value,*,compact=False):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);temp=path.with_name(path.name+'.tmp-'+uuid.uuid4().hex)
    temp.write_text(json.dumps(value,indent=None if compact else 2,
        separators=(',',':') if compact else None,ensure_ascii=False,allow_nan=False),encoding='utf-8')
    # Windows readers may briefly deny DELETE sharing. Bounded retry only;
    # failed evidence is retained and the caller must stop its own worker.
    for attempt in range(8):
        try:os.replace(temp,path);return
        except PermissionError:
            if attempt==7:raise
            time.sleep(.01*(attempt+1))
def validate_scope(session,*,protocol_test=False):
    require(session.get('evidence_scope')==('CPU_PROTOCOL_TEST_ONLY' if protocol_test else 'USER_MANUAL_GPU_SESSION'),'SCOPE_NOT_EXECUTABLE')
    require(session['schema']=='flyvis-live-session/v1' and session['gpu_enabled'] is True and session['confirmed_by_user'] is True,'GPU_NOT_AUTHORIZED')
    require(bool(session.get('authorization_reference')) and session['max_jobs']==2 and session['max_steps']==2910,'GPU_SCOPE_BUDGET')
    start=datetime.fromisoformat(session['start_utc']);end=datetime.fromisoformat(session['end_utc'])
    require(start.tzinfo is not None and end.tzinfo is not None and 0<(end-start).total_seconds()<=900,'GPU_SCOPE_TIME')
    require(start<=datetime.now(timezone.utc)<end,'GPU_SCOPE_EXPIRED')
    require(session['board_enabled'] is False,'PL_NOT_AUTHORIZED')


class Registry:
    def init__(self,path=None,verify=True):
        self.path=host_path(path or HERE/'live_registry.json');self.data=load(self.path);self.pins=self.data['pins']
        require(self.data['schema']=='flyvis-live-registry/v1','REGISTRY_SCHEMA')
        require(self.data['steps']==485 and self.data['dt_s']==.005 and self.data['modes']==MODES,'REGISTERED_PROFILE')
        self.stamps={}
        for key,pin in self.pins.items():
            path=host_path(pin['path']);stat=path.stat()
            if verify:require(sha(path)==pin['sha256'],'SOURCE_CHANGED '+key)
            self.stamps[key]=(stat.st_size,stat.st_mtime_ns)
        identity=load(self.path_for('identity'));model=self.data['model']
        for key in ('checkpoint_sha256','initial_state_sha256','expanded_parameters_sha256','source_commit'):require(identity[key]==model[key],'MODEL_BINDING '+key)
        require(self.pins['initial']['sha256']==model['initial_state_sha256'] and self.pins['parameters']['sha256']==model['expanded_parameters_sha256'],'FROZEN_INITIAL_PARAMETERS')
        self.time=np.load(self.path_for('time'),allow_pickle=False);require(self.time.shape==(485,) and np.array_equal(self.time,np.arange(485)*.005-1),'INPUT_TIME')
        self.uv=np.load(self.path_for('coordinates'),allow_pickle=False);require(self.uv.shape==(721,2),'COORDINATE_SCHEMA')
        science=load(self.path_for('science_contract'))
        require(science['model']==model and science['timeline']['N']==485,'SCIENCE_PROFILE')
        for item in science['preferred_inputs']:require(item['stimulus_sha256']==self.pins['stimulus_'+item['condition_id']]['sha256'],'SCIENCE_INPUT')
    def path_for(self,key):return host_path(self.pins[key]['path'])
    def unchanged(self):
        for key,pin in self.pins.items():
            stat=host_path(pin['path']).stat();require((stat.st_size,stat.st_mtime_ns)==self.stamps[key],'SOURCE_CHANGED '+key)
    def input(self,condition):
        require(condition in self.data['inputs'],'UNKNOWN_INPUT');pin=self.pins['stimulus_'+condition]
        require(sha(pin['path'])==pin['sha256'],'INPUT_SHA_CHANGED')
        x=np.load(host_path(pin['path']),allow_pickle=False,mmap_mode='r')
        require(x.shape==(1,485,1,721) and x.dtype==np.float32 and np.isfinite(x).all() and np.all((x>=0)&(x<=1)),'INPUT_SCHEMA')
        return x
    def binding(self,condition):
        self.input(condition)
        return {'condition_id':condition,'input_sha256':self.pins['stimulus_'+condition]['sha256'],
            'time_sha256':self.pins['time']['sha256'],'model':self.data['model'],
            'graph_sha256':self.pins['graph']['sha256'],'node_map_sha256':self.pins['nodes']['sha256'],
            'metric_profile_sha256':self.pins['readout_contract']['sha256'],'numeric_profile':'ORIGINAL_GPU_FP32_DETERMINISTIC',
            'deterministic_algorithms':True,'allow_tf32':False,
            'candidate_sha256':self.pins['candidate']['sha256'],'dt_s':.005,'steps':485,
            'science_contract_sha256':self.pins['science_contract']['sha256'],
            'decoder_sha256':self.pins['decoder_contract']['sha256'],'ROI_sha256':self.pins['roi']['sha256'],
            'input_node_map_sha256':self.pins['input_map']['sha256'],
            'operator_sources':{key:self.pins[key]['sha256'] for key in ('full','intervention','operators','r_only','h_step','coordinator')},
            'Python_replacement_profile':{'H_nodes':67,'layout':'SOURCE_RAW','numeric':'SOFTWARE_FP32','static_sha256':self.pins['h_static']['sha256']},
            'activity_time_formula':'input_time[k]+0.005','intervention_start_step':200,
            'source_kind':self.data['inputs'][condition]['source_kind']}


def check_identity(message,request):
    for key in ('job_id','comparison_id','condition_id','binding'):
        require(message.get(key)==request[key],'RESULT_IDENTITY_MISMATCH '+key)
    require(message.get('mode') in request['run_ids'] and message.get('run_id')==request['run_ids'][message['mode']],'RESULT_RUN_ID_MISMATCH')


def check_chunk(message,request,expected_start,root,*,test_only=False):
    check_identity(message,request);mode=message['mode'];start=message['start_step'];stop=message['stop_step']
    require(type(start) is int and type(stop) is int and start==expected_start and start<stop<=485 and stop-start<=32,'CHUNK_ORDER_OR_SIZE')
    require(message['PL_execution'] is False,'PL_CLAIM_NOT_AVAILABLE')
    if test_only:
        require(message['evidence_level']=='CPU_PROTOCOL_TEST_DOUBLE' and message['execution_kind']=='cpu_protocol_test'
            and message['actual_new_computation'] is False,'CPU_TEST_LABEL_REQUIRED')
    else:
        require(message['execution_kind']=='new_inference' and message['actual_new_computation'] is True,'REPLAY_CANNOT_SATISFY_NEW_JOB')
        require(message['evidence_level']=='ACTUAL_ORIGINAL_GPU_CHUNK' and message['device']['type']=='cuda','ACTUAL_GPU_REQUIRED')
    require(message['input_sha256']==request['binding']['input_sha256'] and message['committed_stop_step']==stop,'INPUT_OR_COMMIT_IDENTITY')
    require(message.get('schema')=='flyvis-live-chunk/v1' and message.get('neural_steps_in_chunk')==stop-start
        and message.get('decoder_frames_in_chunk')==stop-start,'ACTUAL_CHUNK_COUNTS')
    arrays={};root=Path(root).resolve()
    for name,shape in (('activity',[stop-start,8]),('flow',[stop-start,2,721])):
        pin=message['files'][name];path=(root/pin['path']).resolve()
        require(path.is_relative_to(root) and sha(path)==pin['sha256'],'CHUNK_FILE_IDENTITY')
        array=np.load(path,allow_pickle=False,mmap_mode='r')
        require(list(array.shape)==shape and array.dtype==np.float32 and np.isfinite(array).all(),'CHUNK_ARRAY_SCHEMA')
        arrays[name]=array
    if 'spatial' in message['files']:
        from spatial_state import spatial_registry
        spatial=spatial_registry();spatial.unchanged();pin=message['files']['spatial'];path=(root/pin['path']).resolve()
        require(message.get('spatial_map_sha256')==spatial.digest and path.is_relative_to(root) and sha(path)==pin['sha256'],'CHUNK_SPATIAL_IDENTITY')
        values=np.load(path,allow_pickle=False,mmap_mode='r')
        require(values.shape==(stop-start,5768) and values.dtype==np.float32 and np.isfinite(values).all(),'CHUNK_SPATIAL_SHAPE')
        arrays['spatial']=values
    require(message['central_global_ids']==request['central_global_ids'],'CENTRAL_NODE_IDENTITY')
    require(np.array_equal(message['input_time_s'],np.arange(start,stop)*.005-1) and np.array_equal(message['activity_time_s'],np.arange(start,stop)*.005-1+.005),'EULER_TIME_IDENTITY')
    return arrays


def checked_commit(candidate,gate,commit):
    """Protocol boundary only; no neural equations or state generation."""
    gate('before_commit')
    return commit(candidate)
