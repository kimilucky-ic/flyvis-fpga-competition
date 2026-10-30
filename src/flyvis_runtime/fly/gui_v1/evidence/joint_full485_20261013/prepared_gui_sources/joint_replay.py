"""Explicitly admitted actual PC/PS results. Read-only; never a hardware backend."""
import hashlib
from functools import lru_cache
import numpy as np
from live_protocol import HERE,Registry,load,sha,host_path,require,write
from spatial_state import SpatialRegistry

CONFIG=HERE/'joint_replay.json'

class JointReplay:
    def init__(self,config=CONFIG):
        self.config=host_path(config);cfg=load(self.config);self.stamps={}
        self.pin(self.config,sha(self.config))
        self.audit_path=host_path(cfg['acceptance_path']);self.pin(self.audit_path,cfg['acceptance_sha256'])
        self.audit=load(self.audit_path);a=self.audit
        require(a['status']=='PASS_ACTUAL_485_STEP_GPU_FPGA_CLOSED_LOOP' and a['model_steps']==list(range(485)),'FULL485_NOT_ACCEPTED')
        require(a['PL_outputs_checked']==485*5768 and a['PL_feedback_words_checked']==484*5768 and a['native_H_GPU_updates']==0,'PL_FEEDBACK_PROOF')
        self.root=host_path(cfg['run_directory']).resolve();require(self.root.name==a['run_id'],'RUN_DIRECTORY_IDENTITY')
        self.pin(self.root/'manifest.json',a['pc_manifest_sha256'])
        for name,digest in load(self.root/'manifest.json')['files'].items():
            p=(self.root/name).resolve();require(p.is_relative_to(self.root),'MANIFEST_PATH');self.pin(p,digest)
        self.spatial=SpatialRegistry();require(set(a['PL_proven_global_ids'])==set(self.spatial.ids.tolist()),'PL_NODE_SET')
        self.scope=load(self.root/'scope.json');self.result=load(self.root/'result.json')
        require(self.scope['model']==a['model'] and self.scope['input_sha256']==a['input_sha256'],'MODEL_INPUT_IDENTITY')
        pc=self.root/'pc';self.rows=[load(pc/f'committed_step_{k}.json') for k in range(485)]
        for k,r in enumerate(self.rows):
            require(r['run_id']==a['run_id'] and r['model_step']==k and r['state_token']==k+1 and r['unified_commit_sha']==a['rows'][k]['commit_sha'],'ROW_IDENTITY')
            require(r['input_time_s']==k*.005-1 and r['activity_time_s']==k*.005-1+.005,'TIME_IDENTITY')
        self.arrays={name:np.stack([np.load(pc/f'{prefix}_{k}.npy',allow_pickle=False) for k in range(485)]).astype('<f4',copy=False)
            for name,prefix in [('input','input_721'),('spatial','spatial'),('flow','flow')]}
        for name,shape in [('input',(485,721)),('spatial',(485,5768)),('flow',(485,2,721))]:
            require(self.arrays[name].shape==shape and np.isfinite(self.arrays[name]).all(),'REPLAY_ARRAY_SCHEMA')
        self.registry=Registry();self.uv=self.registry.uv.tolist()
        require(np.array_equal(self.arrays['input'],self.registry.input('ON60')[0,:,0]),'ACTUAL_INPUT_ORDER')
        self.acceptance_sha=cfg['acceptance_sha256']
    def pin(self,path,digest):
        path=host_path(path);require(sha(path)==digest,'REPLAY_SHA_CHANGED '+str(path));s=path.stat();self.stamps[path]=(s.st_size,s.st_mtime_ns)
    def unchanged(self):
        for p,stamp in self.stamps.items():
            s=p.stat();require((s.st_size,s.st_mtime_ns)==stamp,'REPLAY_SOURCE_CHANGED '+str(p))
        self.spatial.unchanged()
        self.registry.unchanged()
    def metadata(self):
        self.unchanged();a=self.audit
        return dict(status='VERIFIED_ACTUAL_JOINT_OFFLINE_REPLAY',run_id=a['run_id'],display_mode='OFFLINE_REPLAY',FPGA_status='NOT_CONNECTED',
            historical_backend='ORIGINAL_GPU_R39901_AND_PHYSICAL_PL_H5768',acceptance_sha256=self.acceptance_sha,
            steps=485,dt_s=.005,model=a['model'],input_sha256=a['input_sha256'],mapping_sha256=a['mapping_sha256'],
            bit_sha256=a['BIT_SHA256'],hwh_sha256=a['HWH_SHA256'],boot_id=a['boot_id'],server_session=a['server_session'],
            numerical_profile='H_Q24_R_FP32',integer_error=0,PL_proven_global_ids=a['PL_proven_global_ids'],
            coordinates_uv=self.uv,spatial_metadata=self.spatial.public(),rows=self.rows,
            initial_file_sha256=self.scope['initial_file_sha256'],initial_full_digest=self.scope['initial_full_digest'],
            compute_total_s=self.result['compute_total_s'],total_worker_s=self.result['total_s'],device=self.result['device'],
            independent_reference=self.result['independent_CPU_reference'],REALTIME_STREAM_PASS='NOT_CLAIMED',
            source_directory=str(self.root),acceptance_path=str(self.audit_path),manifest_sha256=a['pc_manifest_sha256'],
            arrays={n:dict(shape=list(v.shape),dtype='float32_le',sha256=hashlib.sha256(v.tobytes()).hexdigest()) for n,v in self.arrays.items()})
    def binary(self,name,run_id):
        self.unchanged();require(run_id==self.audit['run_id'] and name in self.arrays,'REPLAY_RUN_OR_ARRAY')
        return self.arrays[name].tobytes()
    def save_recording(self,body,run_id):
        self.unchanged();require(run_id==self.audit['run_id'] and 0<len(body)<=100_000_000 and body[:4]==bytes.fromhex('1a45dfa3'),'WEBM_RUN_OR_FORMAT')
        out=self.root/'video';out.mkdir(exist_ok=True);p=out/'ON60_actual_GPU_FPGA_offline.webm'
        with p.open('xb') as f:f.write(body)
        receipt=dict(status='SAVED_BROWSER_CANVAS_RECORDING',run_id=run_id,display_mode='OFFLINE_REPLAY',path=str(p),bytes=len(body),sha256=sha(p),acceptance_sha256=self.acceptance_sha)
        write(out/'recording_receipt.json',receipt);return receipt

@lru_cache(maxsize=1)
def admitted_replay():return JointReplay()
