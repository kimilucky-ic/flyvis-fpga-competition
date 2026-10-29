"""CPU-only, frozen global-node mapping and truthful intervention overlays."""
import csv
import hashlib
from functools import lru_cache
from pathlib import Path
import numpy as np
from live_protocol import HERE,canonical,host_path,load,require,sha,write

TYPES=['T4a','T4b','T4c','T4d','T5a','T5b','T5c','T5d']


def build():
    reg=load(HERE/'live_registry.json');config=load(HERE/'scientific_sparse.json')
    sparse=host_path(config['directory']);manifest=sparse/'DELIVERY_MANIFEST.json'
    require(sha(manifest)==config['manifest_sha256'],'SPARSE_SEAL')
    files={r['path']:r['sha256'] for r in load(manifest)['files']}
    pins={k:reg['pins'][k] for k in ('nodes','candidate')}
    pins['sparse_manifest']={'path':str(manifest),'sha256':config['manifest_sha256']}
    for n in config['counts']:
        name=f'keep_{n}.npy';require(name in files and sha(sparse/name)==files[name],'FROZEN_KEEP_SET')
        pins[f'KEEP_{n}']={'path':str(sparse/name),'sha256':files[name]}
    write(HERE/'spatial_registry.json',dict(schema='flyvis-spatial-map/v1',model=reg['model'],pins=pins,types=TYPES,
        evidence='FROZEN_NODE_COORDINATES_AND_SELECTIONS_ONLY',FPGA_status='NOT_CONNECTED',PL_proven_global_ids=[]))
    m=SpatialRegistry();print({'nodes':len(m.ids),'types':TYPES,'H67_total':len(m.sets['H67']),
        'H67_in_T4T5':len(set(m.sets['H67'])&set(m.ids.tolist())),'map_sha256':m.digest})


class SpatialRegistry:
    def init__(self):
        self.data=load(HERE/'spatial_registry.json');self.stamps={}
        require(self.data['schema']=='flyvis-spatial-map/v1' and self.data['types']==TYPES,'SPATIAL_SCHEMA')
        require(self.data['model']==load(HERE/'live_registry.json')['model'],'SPATIAL_MODEL_BINDING')
        for k,pin in self.data['pins'].items():
            p=host_path(pin['path']);require(sha(p)==pin['sha256'],'SPATIAL_SOURCE_CHANGED '+k)
            self.stamps[k]=(p.stat().st_size,p.stat().st_mtime_ns)
        with host_path(self.data['pins']['nodes']['path']).open(encoding='utf-8-sig') as f:rows=list(csv.DictReader(f))
        self.all_nodes={int(r['global_node_index']):dict(global_id=int(r['global_node_index']),type=r['cell_type'],u=int(r['u']),v=int(r['v'])) for r in rows}
        require(len(self.all_nodes)==45669,'FULL_NODE_MAP')
        self.nodes=[r for typ in TYPES for _,r in sorted(self.all_nodes.items()) if r['type']==typ]
        self.ids=np.array([r['global_id'] for r in self.nodes],dtype=np.int64)
        require(len(set(self.ids))==5768 and all(sum(r['type']==t for r in self.nodes)==721 for t in TYPES),'REAL_8X721_REQUIRED')
        for t in TYPES:require(len({(r['u'],r['v']) for r in self.nodes if r['type']==t})==721,'UNIQUE_COORDINATES')
        self.sets={k:np.load(host_path(p['path']),allow_pickle=False).astype(np.int64).tolist() for k,p in self.data['pins'].items() if k.startswith('KEEP_')}
        self.sets['H5768']=self.ids.tolist()
        candidate=load(host_path(self.data['pins']['candidate']['path']))
        require(candidate['nodes_full_sha256']==self.data['pins']['nodes']['sha256'] and candidate['checkpoint_sha256']==self.data['model']['checkpoint_sha256'],'H67_MODEL_IDENTITY')
        self.sets['H67']=candidate['h_global_node_indices']
        require(len(set(self.sets['H67']))==67 and set(self.sets['H67'])<=self.all_nodes.keys(),'H67_SET')
        for k,ids in self.sets.items():
            require(len(set(ids))==len(ids),'DUPLICATE_ID')
            if k.startswith('KEEP_'):require(len(ids)==int(k[5:]) and set(ids)<=set(self.ids),'KEEP_SET')
        require(set(self.sets['KEEP_5768'])==set(self.ids),'FULL_T4T5_SET_IDENTITY')
        self.digest=canonical(dict(nodes=self.nodes,sets=self.sets,pins=self.data['pins'],model=self.data['model']))
    def unchanged(self):
        for k,pin in self.data['pins'].items():
            s=host_path(pin['path']).stat();require((s.st_size,s.st_mtime_ns)==self.stamps[k],'SPATIAL_SOURCE_CHANGED '+k)
    def public(self):
        self.unchanged()
        return dict(schema='flyvis-spatial-map/v1',map_sha256=self.digest,nodes=self.nodes,types=TYPES,sets=self.sets,
            H67_nodes=[self.all_nodes[k] for k in self.sets['H67']],pins=self.data['pins'],model=self.data['model'],
            FPGA_status='NOT_CONNECTED',PL_proven_global_ids=[],selection_is_execution=False)
    def extract(self,full):
        a=np.asarray(full);require(a.dtype==np.float32 and a.shape[-1]==45669 and np.isfinite(a).all(),'FULL_SPATIAL_STATE_REQUIRED')
        return np.ascontiguousarray(a[...,self.ids])
    def layers(self,mode,step):
        h=self.ids.tolist();disabled=[];blocked=[];replaced=[]
        if mode.startswith('BLOCK_') and step>=200:
            group={'BLOCK_T4_RELEASE':'T4','BLOCK_T5_RELEASE':'T5','BLOCK_T4T5_RELEASE':'T'}[mode]
            blocked=[r['global_id'] for r in self.nodes if r['type'].startswith(group)]
        elif mode=='CLAMP_T4T5' and step>=200:disabled=h
        elif mode.startswith('KEEP_') and step>=200:
            require(mode in self.sets,'UNKNOWN_KEEP_SET');disabled=sorted(set(h)-set(self.sets[mode]))
        elif mode=='Python_Replacement':replaced=self.sets['H67']
        require(mode in ['Full','Sham','BLOCK_T4_RELEASE','BLOCK_T5_RELEASE','BLOCK_T4T5_RELEASE','CLAMP_T4T5','Python_Replacement']+[k for k in self.sets if k.startswith('KEEP_')],'UNSUPPORTED_EXECUTION_MODE')
        return dict(disabled_global_ids=disabled,release_blocked_global_ids=blocked,software_replaced_global_ids=replaced,
            PL_proven_global_ids=[],FPGA_status='NOT_CONNECTED',semantics='actual_mode_at_committed_step; selection overlay is separate')
    def packet(self,full,run_id,step,activity_time,mode='Full'):
        values=self.extract(full);require(values.shape==(5768,),'ONE_COMMITTED_FULL_STATE')
        return dict(schema='flyvis-spatial-state/v1',map_sha256=self.digest,run_id=run_id,step_id=step,state_token=step+1,
            activity_time_s=activity_time,mode=mode,values=values.tolist(),values_sha256=hashlib.sha256(values.tobytes()).hexdigest(),
            layers=self.layers(mode,step),evidence_level='ACTUAL_COMMITTED_FULL_STATE_SLICE')
    def validate(self,p,run_id,step,activity_time,mode):
        require(p['schema']=='flyvis-spatial-state/v1' and p['map_sha256']==self.digest and p['run_id']==run_id
            and p['step_id']==step and p['state_token']==step+1 and p['activity_time_s']==activity_time and p['mode']==mode,'SPATIAL_RUN_STEP_BINDING')
        values=np.asarray(p['values'],dtype=np.float32)
        require(values.shape==(5768,) and np.isfinite(values).all() and hashlib.sha256(values.tobytes()).hexdigest()==p['values_sha256'],'SPATIAL_VALUES')
        require(p['layers']==self.layers(mode,step),'FALSE_SPATIAL_EXECUTION_LAYER')
        return values


@lru_cache(maxsize=1)
def spatial_registry():
    return SpatialRegistry()


if __name__=='__main__':build()
