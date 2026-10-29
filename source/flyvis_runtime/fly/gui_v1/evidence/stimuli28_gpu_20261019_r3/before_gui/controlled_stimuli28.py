"""Pinned line-4 stimulus-only consumer. Never imports/runs neural/device code."""
import csv
import hashlib
import json
from pathlib import Path
import re

import numpy as np

from camera_store import inside,require
from phase3_adapter import VerifiedFiles

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent/'fpga/flyvis-circuit-selection/controlled_stimuli_20261019_v1'
PACK_SHA='7291e37f21a94244b81fb916dca0296d310ce354ac32fc4c8e9077d6aeac3500'
MANIFEST_SHA='a398175a2f9080d5a1aaa49ceb57ee3fe57dcbe282521e55cc373fa0669302c1'
PREFIX='/api/controlled-stimuli28'


def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def digest(raw):return hashlib.sha256(raw).hexdigest()


class ControlledStimuli28(VerifiedFiles):
    def init__(self,root=ROOT):
        super().init__();self.root=Path(root).resolve()
        self.check(inside(self.root,'PACK.json'),PACK_SHA)
        self.check(inside(self.root,'DELIVERY_MANIFEST.json'),MANIFEST_SHA)
        self.pack=read(self.root/'PACK.json');manifest=read(self.root/'DELIVERY_MANIFEST.json')
        require(self.pack['schema']=='flyvis-controlled-stimuli/v1' and self.pack['steps']==485
            and self.pack['dt_s']==.005 and self.pack['input_time_offset_s']==0,'STIMULI28_PROFILE')
        require(self.pack['neural_results'] is self.pack['model_comparison_id'] is None
            and self.pack['all_backends_status']=='NOT_RUN','STIMULI28_UNEXPECTED_RESULT')
        require(manifest['PACK_sha256']==PACK_SHA and manifest['actual_neural_steps']==0
            and manifest['GPU'] is manifest['board'] is False,'STIMULI28_EVIDENCE')
        entries={}
        for row in manifest['files']:
            path=inside(self.root,row['path']);require(path not in entries,'STIMULI28_DUPLICATE_FILE')
            self.check(path,row['sha256'],row['bytes']);entries[path]=row
        self.entries=entries
        require(read(self.root/'VALIDATION.json')['status']=='PASS_CPU_STIMULUS_AND_INTERFACE_ONLY'
            and read(self.root/'RENDER_AUDIT.json')['neural_steps']==0,'STIMULI28_NOT_SEALED')
        with (self.root/self.pack['coordinates']['path']).open(encoding='utf-8',newline='') as f:coords=list(csv.DictReader(f))
        self.uv=[[int(row['u']),int(row['v'])] for row in coords]
        registry=read(HERE/'live_registry.json')
        require(np.array_equal(self.uv,np.load(registry['pins']['coordinates']['path'],allow_pickle=False)),'STIMULI28_COORDINATES')
        require(self.pack['model_checkpoint_sha256']==registry['model']['checkpoint_sha256'],'STIMULI28_CHECKPOINT')
        from spatial_state import SpatialRegistry
        ids=np.load(self.root/self.pack['T4T5_global_ids']['path'],allow_pickle=False)
        require(np.array_equal(ids.reshape(-1),SpatialRegistry().ids),'STIMULI28_SPATIAL_IDS')
        self.conditions={}
        for c in self.pack['conditions']:
            cid=c['condition_id'];require(re.fullmatch('[A-Z0-9_]+',cid) and cid not in self.conditions,'STIMULI28_CONDITION')
            paths={role:inside(self.root,asset['path']) for role,asset in c['paths'].items()}
            require(all(path in entries and entries[path]['sha256']==c['paths'][role]['sha256'] for role,path in paths.items()),'STIMULI28_ASSET_BINDING')
            x=np.load(paths['input'],allow_pickle=False)
            require(x.dtype==np.dtype('<f4') and x.shape==(485,721) and np.isfinite(x).all()
                and np.all((x>=0)&(x<=1)),'STIMULI28_INPUT')
            require(digest(x.tobytes())==c['input_raw_sha256']==c['paths']['raw_input']['sha256'],'STIMULI28_INPUT_DIGEST')
            movie=np.load(paths['stimulus'],allow_pickle=False)
            require(movie.shape==(1,485,1,721) and movie.dtype==x.dtype and movie.tobytes()==x.tobytes()==paths['raw_input'].read_bytes(),'STIMULI28_INPUT_AXES')
            t=np.load(paths['input_time'],allow_pickle=False);after=np.load(paths['state_time'],allow_pickle=False)
            require(np.array_equal(t,np.arange(485)*.005) and np.array_equal(after,(np.arange(485)+1)*.005),'STIMULI28_TIME')
            with paths['frame_map'].open(encoding='utf-8',newline='') as f:frames=list(csv.DictReader(f))
            require(len(frames)==485,'STIMULI28_FRAME_COUNT')
            for k,row in enumerate(frames):
                require(int(row['step_id'])==int(row['video_frame'])==k and float(row['video_pts_s'])==k/50
                    and float(row['input_time_s'])==t[k] and float(row['state_time_s'])==after[k]
                    and inside(self.root,row['source_png']) in entries,'STIMULI28_FRAME_TIME_IDENTITY')
            x.flags.writeable=False
            self.conditions[cid]=dict(source=c,paths=paths,input=x,frames=frames,time=t,after=after)
        require(len(self.conditions)==28,'STIMULI28_CONDITION_COUNT')
        for item in self.conditions.values():
            c=item['source'];control=c['matched_control']
            if control:require(control in self.conditions and np.array_equal(item['input'][:201],self.conditions[control]['input'][:201]),'STIMULI28_STATIC_CONTROL')
        self.assert_unchanged()

    def guard(self,cid=None):
        # Initial admission verifies the complete package once. Serving checks
        # anchors and selected files, not all 2160 files on every displayed step.
        paths=[self.root/'PACK.json',self.root/'DELIVERY_MANIFEST.json']
        if cid is not None:
            require(cid in self.conditions,'STIMULI28_UNKNOWN_CONDITION')
            paths+=list(self.conditions[cid]['paths'].values())
        for path in paths:
            stat=path.stat();require((stat.st_size,stat.st_mtime_ns)==self.signatures[path.resolve()],'STIMULI28_SOURCE_CHANGED')

    def metadata(self):
        self.guard()
        return dict(status='VERIFIED_STIMULUS_ONLY',package_id=self.pack['package_id'],PACK_sha256=PACK_SHA,
            manifest_sha256=MANIFEST_SHA,conditions=[dict(condition_id=c['condition_id'],family=c['family'],
                stationary=c['stationary'],kind=c['kind'],polarity=c.get('polarity'),angle_deg=c.get('angle_deg'),
                matched_control=c['matched_control'],input_raw_sha256=c['input_raw_sha256']) for c in self.pack['conditions']],
            coordinates_uv=self.uv,steps=485,dt_s=.005,preview_fps=50,preview_duration_s=9.7,model_duration_s=2.425,
            source_kind='controlled_animation',source_is_camera=False,execution_kind='STIMULUS_ONLY_OFFLINE_PREVIEW',
            neural_state=None,flow=None,direction_prediction=None,all_backends_status='NOT_RUN',
            initial_state_binding='PENDING_PER_RUN',model_comparison_id=None,
            evidence_level='CPU_STIMULUS_PREPARATION_ONLY',FPGA_status='NOT_CONNECTED')

    def frame(self,cid,k):
        self.guard(cid);require(type(k) is int and 0<=k<485,'STIMULI28_STEP_RANGE')
        item=self.conditions[cid];row=item['frames'][k];values=item['input'][k]
        return dict(package_id=self.pack['package_id'],PACK_sha256=PACK_SHA,condition_id=cid,step_id=k,
            input_time_s=float(item['time'][k]),state_time_s=float(item['after'][k]),video_frame=k,video_pts_s=k/50,
            input_721=values.tolist(),input_step_sha256=digest(values.tobytes()),
            input_raw_sha256=item['source']['input_raw_sha256'],source_pixel_sha256=row['pixel_sha256'],
            png_sha256=self.entries[inside(self.root,row['source_png'])]['sha256'],
            source_png_url=f'{PREFIX}/conditions/{cid}/frames/{k}.png',
            execution_kind='STIMULUS_ONLY_OFFLINE_PREVIEW',evidence_level='STIMULUS_ONLY',
            neural_state=None,flow=None,direction_prediction=None,run_id=None,model_comparison_id=None,all_backends_status='NOT_RUN')

    def image(self,cid,k):
        self.frame(cid,k)
        path=inside(self.root,self.conditions[cid]['frames'][k]['source_png']);raw=path.read_bytes()
        require(digest(raw)==self.entries[path]['sha256'],'STIMULI28_PNG_CHANGED')
        return raw

    def route(self,path):
        if path==PREFIX:return self.metadata(),'application/json; charset=utf-8'
        match=re.fullmatch(PREFIX+r'/conditions/([A-Z0-9_]+)/(steps/(\d+)|frames/(\d+)\.png)',path)
        require(match is not None,'STIMULI28_UNKNOWN_ROUTE')
        cid=match[1];k=int(match[3] or match[4])
        return (self.frame(cid,k),'application/json; charset=utf-8') if match[3] else (self.image(cid,k),'image/png')
