"""Consume explicitly admitted, sealed research B. No model/device/worker imports."""
import csv
from pathlib import Path

import numpy as np

from data_store import ROOT, read_json
from startup_cache import cached_sha256 as sha256
from scientific_pilot import require, signature

COUNTS = [0, 488, 1016, 1736, 2648, 3752, 5768]
CONDITIONS = ['ON60', 'OFF90']
METRICS = ['field_error_E', 'angle_deg', 'magnitude_ratio', 'Q']
TYPES = ['T4a','T4b','T4c','T4d','T5a','T5b','T5c','T5d']


def validate_partition(keep, inactive, nodes, radius):
    """Validate actual global IDs and the preregistered mask, never theoretical counts."""
    for array in (keep, inactive):
        require(array.ndim == 1 and array.dtype == np.int64, 'Node set must be int64 global IDs')
        require(np.all(np.diff(array) > 0), 'Node set must be sorted and unique')
    ids = np.array([int(row['global_node_index']) for row in nodes], dtype=np.int64)
    require(np.array_equal(np.sort(np.concatenate((keep, inactive))), ids), 'Kept/inactive sets must partition actual H')
    u = np.array([int(row['u']) for row in nodes])
    v = np.array([int(row['v']) for row in nodes])
    expected = ids[np.maximum.reduce([np.abs(u),np.abs(v),np.abs(u+v)]) <= radius] if radius is not None else ids[:0]
    require(np.array_equal(keep, expected), 'Kept IDs differ from actual coordinate mask')
    kept=set(keep.tolist())
    return {kind:sum(int(row['global_node_index']) in kept for row in nodes if row['cell_type']==kind) for kind in TYPES}


class ScientificSparse:
    def init__(self, store, pilot, config_path=None):
        require(pilot is not None, 'Verified original Full/Sham reference not available')
        pilot.assert_unchanged()
        self.pilot = pilot
        self.config = read_json(config_path or ROOT/'gui_v1/scientific_sparse.json')
        require(self.config['counts']==COUNTS and self.config['conditions']==CONDITIONS, 'Unadmitted counts/conditions')
        self.root = Path(self.config['directory']).resolve()
        self.files, self.checked, self.stamps = {}, {}, {}
        self.pin(self.root/'DELIVERY_MANIFEST.json', self.config['manifest_sha256'])
        self.manifest = read_json(self.root/'DELIVERY_MANIFEST.json')
        require(self.manifest['status']=='SEALED' and self.manifest['stage']=='B' and self.manifest['run_id']==self.config['run_id'], 'B manifest identity/status mismatch')
        for item in self.manifest['files']:
            path = (self.root/item['path']).resolve()
            require(path.is_relative_to(self.root) and item['path'] not in self.files, 'Manifest path escape/duplicate')
            self.pin(path, item['sha256'])
            require(path.stat().st_size==item['size_bytes'], 'Manifest size mismatch')
            self.files[item['path']] = path
        require(sum(path.stat().st_size for path in self.files.values())==self.manifest['total_bytes'], 'Manifest total mismatch')
        self.spec = self.json('EXPERIMENT_B.json')
        self.handoff = self.json('FINAL_HANDOFF.json')
        self.identity = self.json('artifacts/gpu_r1/run_identity.json')
        self.result = self.json('artifacts/gpu_r1/result.json')
        self.analysis = self.json('artifacts/analysis_r1/result.json')
        require(self.spec['schema']=='B-science-computation/v1', 'Unknown B schema')
        for obj in (self.handoff, self.identity, self.result, self.analysis):
            require(obj['run_id']==self.config['run_id'] and obj['identity_id']==self.config['identity_id'], 'B run/identity mismatch')
        require(self.spec['identity_id']==self.config['identity_id'], 'Spec identity mismatch')
        require(self.handoff['status']==self.analysis['status']=='PASS_SOFTWARE_SPARSE_RETAIN_FIRST_BATCH', 'B not accepted')
        require(self.result['status']=='PASS_ACTUAL_SCIENCE_COMPUTATION' and self.identity['execution_kind']=='ACTUAL_FRESH_ORIGINAL_GPU_NETWORK_AND_DECODER', 'Not actual original GPU science')
        require(self.handoff['PL_execution'] is False and self.identity['PL_execution'] is False and self.result['PL_execution'] is False and self.analysis['FPGA_execution'] is False, 'Software B cannot be PL')
        require(self.spec['FPGA_execution'] is False and self.spec['training'] is False and self.handoff['LIF_or_training'] is False, 'Unexpected experiment backend')
        require(self.spec['model']==self.identity['model']==pilot.identity['model'], 'Full/B model identity mismatch')
        require(self.spec['dt_s']==.005 and self.spec['steps']==485 and self.spec['start_step']==200 and self.spec['n_nodes']==45669, 'B time/node definition mismatch')
        require(self.result['actual_neural_steps']==self.result['actual_decoder_frames']==self.handoff['actual_neural_steps']==6790, 'B execution count mismatch')
        require(self.result['elapsed_s']==self.handoff['elapsed_s'], 'B runtime mismatch')
        # All external dependencies are explicit pins; previously verified references may share hashes.
        for path, digest in self.spec['source_pins'].items():
            path = Path(path).resolve()
            if path in pilot.checked:
                require(pilot.checked[path]==digest and signature(path)==pilot.stamps[path], 'B reference pin mismatch')
                self.checked[path],self.stamps[path] = digest,pilot.stamps[path]
            else:
                self.pin(path,digest)
        self.time = self.array('artifacts/gpu_r1/time.npy')
        self.activity_time = self.array('artifacts/gpu_r1/activity_time.npy')
        require(np.array_equal(self.time,pilot.time) and np.array_equal(self.activity_time,pilot.activity_time), 'B input/Euler time mismatch')
        self.uv, self.roi, self.stimuli = pilot.uv, pilot.roi, pilot.stimuli
        node_path = pilot.files['cpu_preparation_r1/H_node_map.csv']
        with node_path.open(encoding='utf-8',newline='') as stream: self.nodes = list(csv.DictReader(stream))
        require(len(self.nodes)==5768 and {row['cell_type'] for row in self.nodes}==set(TYPES), 'Actual H map mismatch')
        self.sets = {}
        require([s['n_retained'] for s in self.spec['scales']]==COUNTS, 'Scale ordering mismatch')
        previous = set()
        for s in self.spec['scales']:
            count=s['n_retained']; keep=self.array(f'keep_{count}.npy');inactive=self.array(f'inactive_{count}.npy')
            require(Path(s['keep_path']).resolve()==self.files[f'keep_{count}.npy'] and Path(s['inactive_path']).resolve()==self.files[f'inactive_{count}.npy'], 'Node file binding mismatch')
            types=validate_partition(keep,inactive,self.nodes,s['radius'])
            require(len(keep)==count and len(inactive)==s['n_inactive'] and types==s['per_type'], 'Actual node count/type mismatch')
            require(previous.issubset(set(keep.tolist())), 'Retained sets not nested');previous=set(keep.tolist())
            self.sets[count] = {**s,'per_type':types,'global_ids':keep.tolist(),
                'keep_sha256':self.checked[self.files[f'keep_{count}.npy']],
                'inactive_sha256':self.checked[self.files[f'inactive_{count}.npy']],
                'url':f'/api/scientific-sparse/sets/{count}',
                'keep_url':f'/api/scientific-sparse/files/keep_{count}.npy',
                'inactive_url':f'/api/scientific-sparse/files/inactive_{count}.npy'}
        self.flows, self.metrics, self.case_results = {}, {}, {}
        rows=self.csv('sparsity_curve.csv')
        require(len(rows)==14 and len(self.spec['cases'])==14, 'B needs all 14 actual cases')
        for condition in CONDITIONS:
            self.flows[condition]={'Full':pilot.flows[condition]['Full']}
            self.metrics[condition],self.case_results[condition]={},{}
            for count in COUNTS:
                mode=f'KEEP_{count}';base=f'artifacts/gpu_r1/{condition}/{mode}/'
                case=[c for c in self.spec['cases'] if c['condition']==condition and c['mode']==mode]
                require(len(case)==1 and case[0]['n_retained']==count and case[0]['stimulus_sha256']==pilot.conditions[condition]['stimulus_sha256'] and Path(case[0]['stimulus_path']).resolve()==pilot.files['cpu_preparation_r1/'+pilot.conditions[condition]['filename']], 'B input/case binding mismatch')
                flow=self.array(base+'flow.npy')
                require(flow.shape==(1,485,2,721) and flow.dtype==np.float32 and np.isfinite(flow).all(), 'B flow axes/dtype/finite mismatch')
                result=self.json(base+'result.json')
                require(result['condition']==condition and result['mode']==mode and result['neural_steps']==result['decoder_frames']==485 and result['inactive_H']==5768-count and result['old_state_source']=='OWN_LIVE_COMMITTED_STATE' and result['decoder_inactive_inputs_zero'] is True and result['all_finite'] is True, 'B actual case result mismatch')
                self.flows[condition][mode],self.case_results[condition][mode]=flow[0],result
                require(np.array_equal(flow[0,:200],self.flows[condition]['Full'][:200]), 'B pre-clamp flow differs from Full')
                metric=[r for r in rows if r['condition']==condition and r['mode']==mode]
                require(len(metric)==1 and metric[0]['window']=='primary' and int(metric[0]['n_retained'])==count and metric[0]['active_step_range']=='[200, 285]' and metric[0]['pre_step_range']=='[160, 199]' and int(metric[0]['n_hexals'])==331 and metric[0]['reference_eligible']=='True', 'B primary metric window mismatch')
                saved=[r for r in self.handoff['primary_results'] if r['condition']==condition and r['mode']==mode]
                analyzed=[r for r in self.analysis['primary_results'] if r['condition']==condition and r['mode']==mode]
                require(len(saved)==len(analyzed)==1 and saved[0]==analyzed[0], 'B handoff/analysis mismatch')
                values={key:float(metric[0][key]) for key in METRICS}
                require(all(np.isfinite(value) and value==saved[0][key] for key,value in values.items()), 'B numeric identity mismatch')
                self.metrics[condition][mode]={**saved[0],**values}
            require(np.array_equal(self.flows[condition]['KEEP_5768'],self.flows[condition]['Full']), 'B full endpoint differs from original Full')
            clamp=pilot.array(f'artifacts/pilot_gpu_r1/{condition}/CLAMP_T4T5/flow.npy')[0]
            require(np.array_equal(self.flows[condition]['KEEP_0'],clamp), 'B zero endpoint differs from original all-clamp')
        self.allowed = {'DELIVERY_MANIFEST.json','EXPERIMENT_B.json','SPARSE_REPORT.md','FINAL_HANDOFF.json','sparsity_curve.csv',
            'artifacts/gpu_r1/run_identity.json','artifacts/gpu_r1/result.json','artifacts/analysis_r1/result.json',
            'artifacts/gpu_r1/time.npy','artifacts/gpu_r1/activity_time.npy'}
        self.allowed.update(f'{prefix}_{count}.npy' for prefix in ('keep','inactive') for count in COUNTS)
        self.allowed.update(f'artifacts/gpu_r1/{c}/KEEP_{count}/{suffix}' for c in CONDITIONS for count in COUNTS for suffix in ('flow.npy','result.json'))

    def pin(self,path,digest):
        path=Path(path).resolve();before=signature(path)
        require(sha256(path)==digest and before==signature(path),f'Source SHA256 mismatch: {path.name}')
        self.checked[path],self.stamps[path]=digest,before

    def assert_unchanged(self):
        self.pilot.assert_unchanged()
        require(all(signature(p)==stamp for p,stamp in self.stamps.items()), 'B source changed; restart and revalidate')

    def json(self,name):return read_json(self.files[name])
    def array(self,name):return np.load(self.files[name],allow_pickle=False,mmap_mode='r')
    def csv(self,name):
        with self.files[name].open(encoding='utf-8',newline='') as stream:return list(csv.DictReader(stream))

    def status(self):
        self.assert_unchanged()
        return {'status':'VERIFIED','schema':'flyvis-gui-scientific-sparse/v1','evidence_level':'SOFTWARE_SPARSE_RETAIN',
            'display_kind':'OFFLINE_REPLAY','FPGA_status':'NOT_CONNECTED','PL_execution':False,
            'run_id':self.config['run_id'],'identity_id':self.config['identity_id'],'conditions':CONDITIONS,'counts':COUNTS,
            'scales':[{k:v for k,v in self.sets[count].items() if k!='global_ids'} for count in COUNTS],
            'metrics':self.metrics,'model':self.identity['model'],'actual_gpu_result':self.result,
            'started_utc':self.identity['started_utc'],'completed_utc':self.result['completed_utc'],
            'reference_run_id':self.pilot.identity['run_id'],'manifest_sha256':self.config['manifest_sha256'],
            'verified_package_files':len(self.manifest['files']),'clamp_definition':self.spec['clamp_definition'],
            'primary_reference':self.spec['primary_reference'],'limitations':[
                '两条件、七个嵌套空间保留集合；中间规模一次实际 GPU 运行，无逐规模静止对照或独立重复。',
                '3752 节点较接近 Full，E 仍约 0.23；不是数值等价、全条件恢复或板上恢复。',
                '节点数量同时改变空间覆盖与回路；不能由本图推断 FPGA 资源、周期或加速。']}

    def flow_identity(self,condition,mode):
        if mode=='Full':
            path=self.pilot.files[f'artifacts/pilot_gpu_r1/{condition}/Full/flow.npy']
            return {'path':str(path),'sha256':self.pilot.checked[path],'run_id':self.pilot.identity['run_id'],
                'url':f'/api/scientific-pilot/files/artifacts/pilot_gpu_r1/{condition}/Full/flow.npy'}
        path=self.files[f'artifacts/gpu_r1/{condition}/{mode}/flow.npy']
        return {'path':str(path),'sha256':self.checked[path],'run_id':self.config['run_id'],
            'url':f'/api/scientific-sparse/files/artifacts/gpu_r1/{condition}/{mode}/flow.npy'}

    def info(self,condition):
        self.assert_unchanged()
        require(condition in CONDITIONS,'Unadmitted B condition')
        return {'condition':self.pilot.conditions[condition],'run_id':self.config['run_id'],'identity_id':self.config['identity_id'],
            'evidence_level':'SOFTWARE_SPARSE_RETAIN','display_kind':'OFFLINE_REPLAY','PL_execution':False,'FPGA_status':'NOT_CONNECTED',
            'coordinates_uv':self.uv.tolist(),'input_time_s':self.time.tolist(),'activity_time_s':self.activity_time.tolist(),
            'dt_s':.005,'onset_step':200,'primary_window':[200,285],'baseline_window':[160,199], 'roi_indices':self.roi.tolist(),
            'flow_shape':[485,2,721],'input_shape':[485,721],'transport_dtype':'little-endian float32',
            'metrics':self.metrics[condition],'reference_metrics':self.pilot.metrics[condition]['Full'],'case_results':self.case_results[condition],
            'flows':{mode:self.flow_identity(condition,mode) for mode in self.flows[condition]},
            'input':{'path':str(self.pilot.files['cpu_preparation_r1/'+self.pilot.conditions[condition]['filename']]),'sha256':self.pilot.conditions[condition]['stimulus_sha256']},
            'component_convention':self.pilot.contract['component_convention'],'units':self.pilot.contract['units'],
            'source_files':[{'path':str(self.root/name),'sha256':self.checked[(self.root/name).resolve()],
                'url':'/api/scientific-sparse/files/'+name} for name in sorted(self.allowed) if not name.endswith(('/flow.npy','/result.json')) or '/'+condition+'/' in name or name in ('artifacts/gpu_r1/result.json','artifacts/analysis_r1/result.json')]}

    def node_set(self,count):
        self.assert_unchanged()
        value=self.sets[count];ids=set(value['global_ids'])
        return {**value,'nodes':[{'global_id':int(row['global_node_index']),'cell_type':row['cell_type'],'u':int(row['u']),'v':int(row['v'])} for row in self.nodes if int(row['global_node_index']) in ids],
            'node_map_path':str(self.pilot.files['cpu_preparation_r1/H_node_map.csv']),
            'node_map_sha256':self.pilot.checked[self.pilot.files['cpu_preparation_r1/H_node_map.csv']],
            'run_id':self.config['run_id'],'evidence_level':'SOFTWARE_SPARSE_RETAIN','PL_execution':False}

    def binary(self,condition,mode=None):
        self.assert_unchanged()
        array=self.stimuli[condition] if mode is None else self.flows[condition][mode]
        return np.ascontiguousarray(array,dtype='<f4').tobytes()

    def source(self,name):
        self.assert_unchanged()
        if name not in self.allowed:raise KeyError(name)
        return (self.root/name).read_bytes()
