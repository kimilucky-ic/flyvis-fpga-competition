"""Read-only, explicitly pinned actual GPU results for the frozen28 inputs."""
import hashlib
import json
from pathlib import Path
import numpy as np
from camera_store import inside,require
from phase3_adapter import VerifiedFiles


def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def raw_sha(a):return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


class Stimuli28Results(VerifiedFiles):
    def init__(self,source,config_path):
        super().init__();self.source=source
        self.config_path=Path(config_path).resolve();config=read(self.config_path)
        require(config['schema']=='flyvis-stimuli28-result-import/v1','STIMULI28_RESULT_CONFIG')
        self.root=Path(config['root']).resolve()
        require(self.root.is_relative_to(Path(__file__).resolve().parent/'evidence'),'STIMULI28_RESULT_ROOT')
        for name in ('RESULT_MANIFEST.json','ACCEPTANCE.json'):
            self.check(self.root/name,config['pins'][name])
        manifest=read(self.root/'RESULT_MANIFEST.json');self.acceptance=read(self.root/'ACCEPTANCE.json')
        for f in manifest['files']:self.check(inside(self.root,f['path']),f['sha256'],f['bytes'])
        require(self.acceptance['status']=='PASS_ACTUAL_GPU_DATA_AND_TARGETED_NUMERICAL_AUDIT'
            and self.acceptance['manifest_sha256']==config['pins']['RESULT_MANIFEST.json']
            and self.acceptance['PACK_sha256']==source.metadata_input()['PACK_sha256'], 'STIMULI28_RESULT_AUDIT')
        result=read(self.root/'RESULT.json');self.result=result
        require(result['status']=='COMPLETED_ACTUAL_GPU_PENDING_AUDIT' and result['total_neural_steps']==13580
            and result['total_decoder_frames']==13580 and result['GPU'] is True and result['PL_execution'] is False
            and result['network_weights_unchanged'] and result['decoder_state_unchanged'],'STIMULI28_RESULT_EXECUTION')
        require(result['PACK_sha256']==source.metadata_input()['PACK_sha256'],'STIMULI28_RESULT_INPUT_PACKAGE')
        self.campaign=result['campaign_id'];self.conditions={}
        self.visual=dict(activity_abs_max=0.,flow_abs_max=0.,mean_min=0.,mean_max=0.)
        self.initial=np.load(self.root/'initial_state.npy',allow_pickle=False)
        initial_hash=raw_sha(self.initial)
        require(initial_hash==source.pack['initial_state_assets']['original_bias_fp32']['raw_array_sha256']
                ==result['common_initial_raw_sha256'],'STIMULI28_RESULT_INITIAL')
        require(np.array_equal(np.load(self.root/'T4T5_global_ids.npy',allow_pickle=False),
            np.load(source.root/source.pack['T4T5_global_ids']['path'],allow_pickle=False)),'STIMULI28_RESULT_MAP')
        self.profile=read(self.root/'NUMERICAL_PROFILE.json')
        require(self.profile['model_dt_s']==.005 and self.profile['TF32'] is False
            and self.profile['name']=='ORIGINAL_FLYVIS_FP32_CUDA','STIMULI28_RESULT_NUMERIC')
        require(len(result['conditions'])==28 and len({x['run_id'] for x in result['conditions']})==28,'STIMULI28_RESULT_RUNS')
        for run in result['conditions']:
            cid=run['condition_id'];require(cid in source.conditions and cid not in self.conditions,'STIMULI28_RESULT_CONDITION')
            folder=self.root/'conditions'/cid
            require(read(folder/'run.json')==run and run['status']=='COMPLETED_ACTUAL_GPU'
                and run['device']=='cuda' and run['backend']=='original_FlyVis_Full_GPU'
                and run['initial_raw_sha256']==initial_hash and run['PACK_sha256']==result['PACK_sha256']
                and run['input_raw_sha256']==source.conditions[cid]['source']['input_raw_sha256']
                and run['model_checkpoint_sha256']==source.pack['model_checkpoint_sha256']
                and run['numeric_profile_sha256']==self.checked[self.root/'NUMERICAL_PROFILE.json']
                and run['recursive_eval'] is True and run['PL_execution'] is False,'STIMULI28_RESULT_BINDING')
            arrays={n:np.load(folder/(n+'.npy'),mmap_mode='r',allow_pickle=False) for n in ('input','states','spatial','means','flow')}
            shapes={'input':(485,721),'states':(485,45669),'spatial':(485,5768),'means':(485,8),'flow':(485,2,721)}
            for n,a in arrays.items():
                require(a.shape==shapes[n] and a.dtype==np.dtype('<f8' if n=='means' else '<f4'),'STIMULI28_RESULT_ARRAY '+n)
            require(raw_sha(arrays['input'])==run['input_raw_sha256'],'STIMULI28_RESULT_INPUT_BITS')
            for n in ('spatial','means','flow'):require(np.isfinite(arrays[n]).all(),'STIMULI28_RESULT_NONFINITE')
            for name,expected in (('input_time',source.conditions[cid]['time']),('activity_time',source.conditions[cid]['after'])):
                require(np.array_equal(np.load(folder/(name+'.npy'),allow_pickle=False),expected),'STIMULI28_RESULT_TIME')
            self.conditions[cid]=dict(run=run,arrays=arrays)
            self.visual['activity_abs_max']=max(self.visual['activity_abs_max'],float(np.max(np.abs(arrays['spatial']))))
            self.visual['flow_abs_max']=max(self.visual['flow_abs_max'],float(np.max(np.abs(arrays['flow']))))
            self.visual['mean_min']=min(self.visual['mean_min'],float(np.min(arrays['means'])))
            self.visual['mean_max']=max(self.visual['mean_max'],float(np.max(arrays['means'])))
        require(set(self.conditions)==set(source.conditions),'STIMULI28_RESULT_INCOMPLETE_CAMPAIGN')
        self.config_stamp=(self.config_path.stat().st_size,self.config_path.stat().st_mtime_ns)

    def guard(self,cid=None):
        s=self.config_path.stat();require((s.st_size,s.st_mtime_ns)==self.config_stamp,'STIMULI28_RESULT_IMPORT_CHANGED')
        paths=[self.root/'ACCEPTANCE.json',self.root/'RESULT_MANIFEST.json']
        if cid:
            require(cid in self.conditions,'STIMULI28_RESULT_UNKNOWN_CONDITION')
            paths += list((self.root/'conditions'/cid).glob('*.npy'))+[self.root/'conditions'/cid/'run.json']
        for p in paths:
            s=p.stat();require((s.st_size,s.st_mtime_ns)==self.signatures[p],'STIMULI28_RESULT_SOURCE_CHANGED')

    def metadata(self):
        self.guard()
        return dict(status='VERIFIED_ACTUAL_GPU_OFFLINE_REPLAY',campaign_id=self.campaign,
            backend='original_FlyVis_Full_GPU',device=self.result['conditions'][0]['device_name'],
            initial_kind='original_bias_fp32',initial_raw_sha256=self.result['common_initial_raw_sha256'],
            numeric_profile=self.profile,model_checkpoint_sha256=self.result['model_checkpoint_sha256'],
            total_neural_steps=13580,total_decoder_frames=13580,PL_execution=False,FPGA_status='NOT_CONNECTED',
            audit_scope=self.acceptance['numerical_audit_scope'],functional_acceptance='NOT_EVALUATED',
            display_kind='OFFLINE_REPLAY',types=self.source.pack['T4T5_global_ids']['types'],
            visual_domains=self.visual,visual_policy='Fixed across all28 conditions and all485 steps; raw values retained')

    def frame(self,cid,k):
        self.guard(cid);require(type(k) is int and 0<=k<485,'STIMULI28_RESULT_STEP')
        item=self.conditions[cid];r=item['run'];a=item['arrays']
        state=a['states'][k];spatial=a['spatial'][k];flow=a['flow'][k]
        return dict(run_id=r['run_id'],campaign_id=self.campaign,condition_id=cid,step_id=k,state_token=k+1,
            input_time_s=k*.005,activity_time_s=(k+1)*.005,backend=r['backend'],device=r['device_name'],
            initial_raw_sha256=r['initial_raw_sha256'],input_raw_sha256=r['input_raw_sha256'],
            full_state_sha256=raw_sha(state),spatial_sha256=raw_sha(spatial),flow_sha256=raw_sha(flow),
            spatial=spatial.tolist(),means=a['means'][k].tolist(),flow=flow.tolist(),
            decoder='official_DecoderGAVP',display_kind='OFFLINE_REPLAY',PL_execution=False,
            evidence_level='ACTUAL_FULL_GPU_OFFLINE',functional_acceptance='NOT_EVALUATED')

    def series(self,cid):
        self.guard(cid);item=self.conditions[cid];a=item['arrays'];r=item['run']
        return dict(run_id=r['run_id'],condition_id=cid,campaign_id=self.campaign,types=self.source.pack['T4T5_global_ids']['types'],
            means=a['means'].tolist(),input_time_s=self.source.conditions[cid]['time'].tolist(),
            activity_time_s=self.source.conditions[cid]['after'].tolist(),
            means_sha256=raw_sha(a['means']),numeric_profile_sha256=r['numeric_profile_sha256'],
            initial_raw_sha256=r['initial_raw_sha256'],input_raw_sha256=r['input_raw_sha256'],
            timing=r['timing'],display_kind='OFFLINE_REPLAY')
