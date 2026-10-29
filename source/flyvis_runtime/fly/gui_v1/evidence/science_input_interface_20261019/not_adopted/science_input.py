"""Read-only frozen science input handoff; no rendering, inference or devices.

Explicit descriptor/manifest pins are required. This verifies input identity,
not a scientific conclusion, media decode or hardware execution.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re

import numpy as np

from camera_store import inside, require
from phase3_adapter import VerifiedFiles, array_digest

HERE=Path(__file__).resolve().parent
SCHEMA='flyvis-science-input-handoff/v1'
FAMILIES={'direction','on_off','speed','small_target','looming','background'}
ASSETS={'generator','parameters','preregistration','coordinates','input_node_ids',
        'model_identity','initial_state','numeric_profile','metric_profile'}


def fingerprint(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


class FrozenScienceInput(VerifiedFiles):
    def init__(self,root,*,handoff_sha256,manifest_sha256):
        super().init__()
        self._arrays=[];self._closed=False
        try:self._load(root,handoff_sha256=handoff_sha256,manifest_sha256=manifest_sha256)
        except BaseException:
            self.close()
            raise

    def _load(self,root,*,handoff_sha256,manifest_sha256):
        self.root=Path(root).resolve()
        for value in (handoff_sha256,manifest_sha256):
            require(isinstance(value,str) and re.fullmatch('[0-9a-f]{64}',value),'SCIENCE_EXPLICIT_PINS_REQUIRED')
        self.check(inside(self.root,'DELIVERY_MANIFEST.json'),manifest_sha256)
        self.check(inside(self.root,'GUI_HANDOFF.json'),handoff_sha256)
        self.handoff_sha256=handoff_sha256
        self.desc=self.read('GUI_HANDOFF.json')
        require(self.desc['schema']==SCHEMA and self.desc['status']=='INPUT_FROZEN','SCIENCE_HANDOFF_SCHEMA')
        require(self.desc['source_kind']=='digital_direct' and self.desc['source_is_camera'] is False,'SCIENCE_INPUT_SOURCE')
        require(isinstance(self.desc['experiment_id'],str) and self.desc['experiment_id'],'SCIENCE_EXPERIMENT_ID')
        self.entries={}
        for row in self.read('DELIVERY_MANIFEST.json')['files']:
            key=inside(self.root,row['path'])
            require(key not in self.entries,'SCIENCE_DUPLICATE_MANIFEST_PATH')
            self.entries[key]=row
        self.asset('GUI_HANDOFF.json')
        assets=self.desc['assets']
        require(set(assets)==ASSETS,'SCIENCE_ASSET_ROLES')
        for name in assets.values():self.asset(name)
        self.parameters=self.read(assets['parameters'])
        require(type(self.parameters['seed']) is int and self.parameters['seed']>=0,'SCIENCE_RANDOM_SEED')
        require(self.read(assets['preregistration']) and self.read(assets['metric_profile']),'SCIENCE_PREREGISTRATION')
        self.numeric=self.read(assets['numeric_profile'])
        require(isinstance(self.numeric,dict) and self.numeric,'SCIENCE_NUMERIC_PROFILE')
        # Match the original official model and exact ordered input mapping.
        # The common initial state is supplied by this study, not borrowed from
        # the older G2 or camera run. Q24 and FP32 remain separate comparisons.
        registry=self.read(HERE/'live_registry.json')
        self.model=self.read(assets['model_identity'])
        require(all(self.model[k]==registry['model'][k] for k in
            ('model_id','source_commit','checkpoint_sha256','expanded_parameters_sha256')),'SCIENCE_MODEL_IDENTITY')
        require(self.model['n_nodes']==45669 and self.model['n_edges']==1513231,'SCIENCE_FULL_MODEL_REQUIRED')
        for role,pin in (('coordinates','coordinates'),('input_node_ids','input_map')):
            require(self.checked[inside(self.root,assets[role])]==registry['pins'][pin]['sha256'],'SCIENCE_ORDERED_INPUT_MAP')
        self.coordinates=self.array(assets['coordinates'])
        self.input_node_ids=self.array(assets['input_node_ids'])
        require(self.coordinates.shape==(721,2) and self.input_node_ids.shape==(8,721),'SCIENCE_INPUT_MAP_SHAPE')
        self.initial=self.array(assets['initial_state'])
        require(self.initial.shape in ((45669,),(1,45669)) and self.initial.dtype==np.dtype('<f4')
            and np.isfinite(self.initial).all(),'SCIENCE_INITIAL_STATE')
        self.initial_digest=array_digest(self.initial.reshape(-1))
        self.state_binding=dict(initial_state_file_sha256=self.checked[inside(self.root,assets['initial_state'])],
            initial_state_array_digest=self.initial_digest,
            numeric_profile_sha256=self.checked[inside(self.root,assets['numeric_profile'])])
        self.conditions={}
        rows=self.desc['conditions']
        require(isinstance(rows,list) and 0<len(rows)<=64,'SCIENCE_CONDITION_COUNT')
        for row in rows:
            cid=row['condition_id'];n=row['steps']
            require(isinstance(cid,str) and re.fullmatch('[A-Za-z0-9_-]{1,80}',cid)
                and cid not in self.conditions and row['family'] in FAMILIES,'SCIENCE_CONDITION_ID')
            require(type(n) is int and 0<n<=12000 and row['dt_s']==.005,'SCIENCE_5MS_GRID')
            require(isinstance(row['parameters'],dict) and row['parameters'] and isinstance(row['control_role'],str)
                and row['control_role'],'SCIENCE_CONDITION_PARAMETERS')
            files=row['files']
            require(set(files)=={'stimulus','input_time','activity_time','video','video_pts','frame_index'},'SCIENCE_CONDITION_FILES')
            for name in files.values():self.asset(name)
            x=self.array(files['stimulus']);time=self.array(files['input_time']);after=self.array(files['activity_time'])
            require(x.shape in ((n,721),(1,n,1,721)) and x.dtype==np.dtype('<f4')
                and np.isfinite(x).all() and np.all((x>=0)&(x<=1)),'SCIENCE_INPUT_ARRAY')
            require(time.shape==after.shape==(n,) and time.dtype.kind==after.dtype.kind=='f'
                and np.isfinite(time).all() and np.allclose(time,time[0]+np.arange(n)*.005,rtol=0,atol=1e-12)
                and np.array_equal(after,time+.005),'SCIENCE_INPUT_EULER_TIME')
            video=row['video'];pts=self.array(files['video_pts']);indices=self.array(files['frame_index'])
            require(video['relation'] in ('CONVERSION_SOURCE','GENERATOR_PREVIEW_ONLY')
                and video['resampling']=='CAUSAL_ZOH'
                and type(video['frame_count']) is int and video['frame_count']>0,'SCIENCE_VIDEO_RELATION')
            require(pts.shape==(video['frame_count'],) and pts.dtype.kind=='f' and np.isfinite(pts).all()
                and pts[0]==0 and np.all(np.diff(pts)>0) and np.isfinite(video['duration_s'])
                and video['duration_s']>pts[-1] and time[-1]-time[0]<video['duration_s'],'SCIENCE_VIDEO_PTS')
            elapsed=time-time[0]
            expected=np.searchsorted(pts,elapsed,side='right')-1
            require(indices.shape==(n,) and indices.dtype.kind in 'iu' and np.array_equal(indices,expected),'SCIENCE_VIDEO_STEP_ALIGNMENT')
            binding=dict(experiment_id=self.desc['experiment_id'],condition_id=cid,steps=n,dt_s=.005,
                model={k:self.model[k] for k in ('model_id','source_commit','checkpoint_sha256','expanded_parameters_sha256')},
                file_sha256={k:self.checked[inside(self.root,v)] for k,v in files.items()},
                shared_sha256={k:self.checked[inside(self.root,v)] for k,v in assets.items() if k not in ('initial_state','numeric_profile')})
            self.conditions[cid]=dict(meta=deepcopy(row),input=x.reshape(n,721),time=time,after=after,
                frame_index=indices,binding=binding,input_id=fingerprint(binding))
        self.assert_unchanged()

    def read(self,path):
        path=Path(path)
        if not path.is_absolute():path=inside(self.root,str(path))
        return json.loads(path.read_text(encoding='utf-8-sig'))

    def asset(self,name):
        path=inside(self.root,name)
        require(path in self.entries,'SCIENCE_UNLISTED_FILE')
        row=self.entries[path]
        require(type(row['bytes']) is int and row['bytes']>=0,'SCIENCE_FILE_SIZE')
        self.check(path,row['sha256'],row['bytes'])
        return path

    def array(self,name):
        path=inside(self.root,name)
        require(path in self.checked,'SCIENCE_UNVERIFIED_ARRAY')
        value=np.load(path,allow_pickle=False,mmap_mode='r')
        require(isinstance(value,np.ndarray),'SCIENCE_NPY_REQUIRED')
        self._arrays.append(value)
        return value

    def assert_unchanged(self):
        require(not self._closed,'SCIENCE_INPUT_CLOSED')
        super().assert_unchanged()

    def close(self):
        for value in self._arrays:value._mmap.close()
        self._arrays.clear();self._closed=True

    def __enter__(self):return self

    def __exit__(self,*args):self.close()

    def condition(self,cid):
        self.assert_unchanged()
        require(cid in self.conditions,'SCIENCE_UNKNOWN_CONDITION')
        return self.conditions[cid]

    def binding(self,cid):
        c=self.condition(cid)
        return dict(input_id=c['input_id'],input_binding=deepcopy(c['binding']),
            state_binding=deepcopy(self.state_binding),comparison_id=fingerprint([c['input_id'],self.state_binding]))

    def describe(self):
        self.assert_unchanged()
        return dict(schema=SCHEMA,experiment_id=self.desc['experiment_id'],status='INPUT_FILES_VERIFIED',
            neural_results='NOT_AVAILABLE',FPGA_status='NOT_CONNECTED',execution_kind='FROZEN_INPUT_ONLY',
            media_decode_verified=False,scientific_acceptance='NOT_EVALUATED',
            conditions=[dict(condition_id=cid,steps=c['meta']['steps'],family=c['meta']['family'],
                control_role=c['meta']['control_role'],binding=self.binding(cid)) for cid,c in self.conditions.items()])

    def step(self,cid,k):
        c=self.condition(cid)
        require(type(k) is int and 0<=k<c['meta']['steps'],'SCIENCE_STEP_RANGE')
        return dict(condition_id=cid,step_id=k,input_time_s=float(c['time'][k]),activity_time_s=float(c['after'][k]),
            input_721=c['input'][k],source_frame_index=int(c['frame_index'][k]),
            video_path=str(inside(self.root,c['meta']['files']['video'])),video_relation=c['meta']['video']['relation'],
            **self.binding(cid),execution_kind='FROZEN_INPUT_ONLY',neural_results='NOT_AVAILABLE')

    def check_result_identity(self,cid,result):
        require(result['binding']==self.binding(cid),'SCIENCE_RESULT_BINDING_MISMATCH')
        require(isinstance(result['run_id'],str) and result['run_id'],'SCIENCE_RESULT_RUN_ID')
        return 'IDENTITY_MATCH_ONLY_NOT_NUMERICAL_SCIENTIFIC_OR_BOARD_ACCEPTANCE'
