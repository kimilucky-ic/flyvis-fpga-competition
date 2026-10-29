"""Read-only consumer of the sealed T4/T5 pilot. No model/device/runner imports."""
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import numpy as np

from data_store import ROOT, read_json, sha256

MODES = ['Full', 'Sham', 'BLOCK_T4_RELEASE', 'BLOCK_T5_RELEASE', 'BLOCK_T4T5_RELEASE']
LABELS = ['Full', 'Sham', 'T4 释放阻断', 'T5 释放阻断', 'T4+T5 联合释放阻断']


def require(condition, message):
    if not condition:
        raise ValueError(message)


def signature(path):
    stat = path.stat()
    return stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns


class ScientificPilot:
    def init__(self, store, config_path=None):
        self.config = read_json(config_path or ROOT/'gui_v1/scientific_pilot.json')
        self.root = Path(self.config['directory']).resolve()
        self.checked, self.stamps, self.files = {}, {}, {}
        manifest_path = self.root/'PILOT_DELIVERY_MANIFEST.json'
        self.pin(manifest_path, self.config['manifest_sha256'])
        self.manifest = read_json(manifest_path)
        require(self.manifest['run_id'] == self.config['run_id'], 'Pilot manifest run mismatch')
        # Verify this explicitly admitted, sealed package; never discover/accept new directories.
        for entry in self.manifest['files']:
            path = (self.root/entry['path']).resolve()
            require(path.is_relative_to(self.root), 'Pilot path escapes package')
            self.pin(path, entry['sha256'])
            require(path.stat().st_size == entry['size_bytes'], 'Pilot file size mismatch')
            self.files[entry['path']] = path
        self.identity = self.json('artifacts/pilot_gpu_r1/run_identity.json')
        self.result = self.json('artifacts/pilot_gpu_r1/result.json')
        self.analysis = self.json('artifacts/pilot_analysis_r1/result.json')
        self.input = self.json('INPUT_IDENTITY.json')
        require(self.analysis['status'] == 'PASS_PILOT_EXECUTION_AND_PREREGISTERED_ANALYSIS', 'Pilot analysis not accepted')
        require(self.result['status'] == 'PASS_ACTUAL_GPU_PILOT_COMPUTATION', 'Actual GPU pilot not accepted')
        for obj in (self.identity, self.result, self.analysis):
            require(obj['run_id'] == self.config['run_id'], 'Run identity mismatch')
            require(obj['preregistration_id'] == self.config['preregistration_id'], 'Preregistration mismatch')
        require(self.identity['model'] == self.input['model'], 'Input/model binding mismatch')
        require(self.identity['PL_execution'] is False and self.result['PL_execution'] is False, 'Software pilot cannot be PL')
        require(self.input['dt_s'] == .005 and self.input['steps'] == 485 and self.input['intervention_start_step'] == 200, 'Unexpected timing')
        contract_path = Path(self.config['decoder_contract'])
        self.pin(contract_path, self.identity['code_sha256'][self.config['decoder_contract_identity_path']])
        self.contract = read_json(contract_path)
        coord = self.contract['coordinates']
        self.pin(Path(coord['path']), coord['sha256'])
        self.uv = np.load(coord['path'], allow_pickle=False)
        require(self.uv.shape == (721, 2), 'Decoder coordinate shape')
        edge = store.datasets['edge24']
        require(np.array_equal(self.uv, [[c['u'],c['v']] for c in edge.coordinates]), 'Decoder/input hex order mismatch')
        require(self.contract['component_convention'] == ['x_right_positive','y_up_positive'], 'Unknown flow component convention')
        self.time = self.array('artifacts/pilot_gpu_r1/time.npy')
        self.activity_time = self.array('artifacts/pilot_gpu_r1/activity_time.npy')
        require(self.time.shape == (485,) and np.array_equal(self.time, edge.time), 'Source input time mismatch')
        require(np.array_equal(self.activity_time, self.time+.005), 'Euler-after time mismatch')
        self.roi = self.array('cpu_preparation_r1/flow_ROI_hex_indices.npy')
        require(len(self.roi) == 331 and len(set(self.roi.tolist())) == 331 and np.all((self.roi>=0)&(self.roi<721)), 'Invalid preregistered ROI')
        self.conditions, self.flows, self.stimuli, self.series, self.metrics = {}, {}, {}, {}, {}
        rows = self.csv('artifacts/pilot_analysis_r1/flow_step_series.csv')
        metric_rows = self.csv('artifacts/pilot_analysis_r1/functional_summary.csv')
        for condition in self.input['conditions']:
            name = condition['condition_id']
            if name not in self.config['conditions']:
                continue
            stimulus = self.array('cpu_preparation_r1/'+condition['filename'])
            require(stimulus.shape == (1,485,1,721) and stimulus.dtype == np.float32 and np.isfinite(stimulus).all(), 'Stimulus axes/dtype/finite mismatch')
            require(np.array_equal(stimulus[0,:,0], np.asarray(edge.stimulus[condition['original_sample'],:,0], dtype=np.float32)), 'Frozen input differs from original edge sample')
            require(hashlib.sha256(stimulus.tobytes()).hexdigest() == condition['FP32_slice_sha256'], 'Frozen FP32 input identity mismatch')
            require(self.checked[self.files['cpu_preparation_r1/'+condition['filename']]] == condition['stimulus_sha256'], 'Stimulus file identity mismatch')
            self.conditions[name], self.stimuli[name] = condition, stimulus[0,:,0]
            self.flows[name], self.series[name], self.metrics[name] = {}, {}, {}
            for mode in MODES:
                base_path = f'artifacts/pilot_gpu_r1/{name}/{mode}/'
                flow = self.array(base_path+'flow.npy')
                require(flow.shape == (1,485,2,721) and flow.dtype == np.float32 and np.isfinite(flow).all(), 'Flow axes/dtype/finite mismatch')
                result = self.json(base_path+'result.json')
                require(result['condition'] == name and result['mode'] == mode and result['neural_steps'] == result['decoder_frames'] == 485 and result['all_finite'] is True, 'Mode result mismatch')
                self.flows[name][mode] = flow[0]
                points = [row for row in rows if row['condition']==name and row['mode']==mode]
                require([int(p['step_id']) for p in points] == list(range(485)), 'Curve step order mismatch')
                require(np.array_equal([float(p['input_time_s']) for p in points], self.time) and np.array_equal([float(p['activity_time_s']) for p in points], self.activity_time), 'Curve time mismatch')
                self.series[name][mode] = {key:[float(p[key]) for p in points] for key in ('stimulus_projection','mean_pixel_vector_magnitude')}
                metric = [p for p in metric_rows if p['condition']==name and p['mode']==mode and p['ROI']=='primary331' and p['window']=='primary']
                require(len(metric)==1 and metric[0]['active_step_range']=='[200, 285]' and metric[0]['pre_step_range']=='[160, 199]', 'Primary window mismatch')
                self.metrics[name][mode] = {key:float(metric[0][key]) for key in ('Q','magnitude_ratio','field_error_E','angle_deg')}
                self.metrics[name][mode]['interpretation'] = metric[0]['interpretation']
            require(np.array_equal(self.flows[name]['Full'],self.flows[name]['Sham']), 'Full/Sham flow mismatch')
            direction = np.array([np.cos(np.deg2rad(condition['angle_deg'])),np.sin(np.deg2rad(condition['angle_deg']))])
            baseline = self.flows[name]['Sham'][160:200].mean(axis=0)
            for mode in MODES:
                require(np.array_equal(self.flows[name][mode][:200],self.flows[name]['Full'][:200]), 'Pre-intervention flow mismatch')
                centered = self.flows[name][mode]-baseline
                projection = np.einsum('tch,c->th',centered[:,:,self.roi],direction).mean(axis=1)
                magnitude = np.sqrt(np.sum(centered[:,:,self.roi].astype(np.float64)**2,axis=1)).mean(axis=1)
                require(np.allclose(projection,self.series[name][mode]['stimulus_projection'],rtol=0,atol=1e-12) and np.allclose(magnitude,self.series[name][mode]['mean_pixel_vector_magnitude'],rtol=0,atol=1e-12), 'Saved curve differs from original field')
        require(set(self.conditions)==set(self.config['conditions']), 'Requested conditions missing')

    def pin(self, path, digest):
        path = Path(path).resolve()
        before = signature(path)
        require(sha256(path)==digest and before==signature(path), f'Source SHA256 mismatch: {path.name}')
        self.checked[path], self.stamps[path] = digest, before

    def assert_unchanged(self):
        require(all(signature(path)==stamp for path,stamp in self.stamps.items()), 'Pilot source changed; restart and revalidate')

    def json(self, name):
        return read_json(self.files[name])

    def array(self, name):
        return np.load(self.files[name],allow_pickle=False,mmap_mode='r')

    def csv(self, name):
        with self.files[name].open(encoding='utf-8',newline='') as stream:
            return list(csv.DictReader(stream))

    def status(self):
        self.assert_unchanged()
        return {'status':'VERIFIED','evidence_level':'SOFTWARE_PILOT','display_kind':'offline replay',
                'FPGA_status':'NOT_CONNECTED','PL_execution':False,'run_id':self.identity['run_id'],
                'conditions':list(self.conditions),'modes':dict(zip(MODES,LABELS)),
                'sparse_recovery':{'status':'NOT_AVAILABLE','reason':'④科研B已验收的逐半径保留节点身份、同条件读出、报告与SHA清单尚未准入；不绘制理论数量或假曲线。'},
                'actual_gpu_result':self.result,'model':self.identity['model'],
                'started_utc':self.identity['started_utc'],'completed_utc':self.result['completed_utc'],
                'manifest_sha256':self.config['manifest_sha256'],'verified_package_files':len(self.manifest['files'])}

    def info(self, condition):
        self.assert_unchanged()
        identity = self.conditions[condition]
        return {'condition':identity,'run_id':self.identity['run_id'],'evidence_level':'SOFTWARE_PILOT',
                'display_kind':'offline replay','PL_execution':False,'FPGA_status':'NOT_CONNECTED',
                'input_time_s':self.time.tolist(),'activity_time_s':self.activity_time.tolist(),
                'dt_s':.005,'onset_step':200,'primary_window':[200,285],'baseline_window':[160,199],
                'coordinates_uv':self.uv.tolist(),'roi_indices':self.roi.tolist(),
                'flow_shape':[485,2,721],'input_shape':[485,721],'transport_dtype':'little-endian float32',
                'series':self.series[condition],'metrics':self.metrics[condition],
                'component_convention':self.contract['component_convention'],'units':self.contract['units'],
                'source_files':[{'path':str(path),'sha256':self.checked[path],'url':'/api/scientific-pilot/files/'+name} for name,path in self.files.items() if name in ('PILOT_REPORT.md','artifacts/pilot_analysis_r1/functional_summary.csv','artifacts/pilot_analysis_r1/flow_step_series.csv','artifacts/pilot_gpu_r1/run_identity.json','artifacts/pilot_gpu_r1/result.json','artifacts/pilot_gpu_r1/time.npy','artifacts/pilot_gpu_r1/activity_time.npy','cpu_preparation_r1/'+identity['filename']) or name.startswith('artifacts/pilot_gpu_r1/'+condition+'/') and name.endswith(('flow.npy','result.json'))]}

    def binary(self, condition, mode=None):
        self.assert_unchanged()
        array = self.stimuli[condition] if mode is None else self.flows[condition][mode]
        return np.ascontiguousarray(array,dtype='<f4').tobytes()

    def source(self, name):
        self.assert_unchanged()
        # Allow only already verified/displayed scientific files, never arbitrary filesystem paths.
        allowed = {item['url'].split('/files/',1)[1] for c in self.conditions for item in self.info(c)['source_files']}
        if name not in allowed:
            raise KeyError(name)
        return self.files[name].read_bytes()


class AutoRunnerRecords:
    """Explicitly registered producer records, not a job executor or result admission path."""
    def init__(self, config_path=None):
        self.config = read_json(config_path or ROOT/'gui_v1/scientific_pilot.json')['autorunner']

    def snapshot(self):
        records = []
        for entry in self.config:
            try:
                directory = Path(entry['directory'])
                seal_path = directory/'seal.json'
                require(sha256(seal_path)==entry['seal_sha256'], 'AutoRunner seal mismatch')
                seal = read_json(seal_path)
                summary_path = directory/'run_summary.json'
                require(sha256(summary_path)==seal['files']['run_summary.json'], 'AutoRunner summary hash mismatch')
                require(sha256(directory/'job.json')==entry['job_sha256'], 'Registered completed job hash mismatch')
                job,summary = read_json(directory/'job.json'), read_json(summary_path)
                require(job['schema']=='flyvis-autorunner/v1/job' and summary['schema']=='flyvis-autorunner/v1/summary','Unknown runner schema')
                require(job['run_id']==summary['run_id']==entry['job_id'] and job['experiment_id']==summary['experiment_id'], 'Runner identities mismatch')
                require(job['stage']==summary['final_stage']=='COMPLETE' and job['step']==job['total_steps']==609,'Completed snapshot inconsistency')
                require(job['PL_execution'] is False and summary['PL_execution'] is False and summary['FPGA_status']=='NOT_CONNECTED','Software record cannot be physical PL')
                timing = Path(entry['timing_path'])
                require(sha256(timing)==entry['timing_sha256'],'External timing identity mismatch')
                command = read_json(timing)
                records.append({'status':'VERIFIED_RECORD','job':job,'summary':summary,'external_timing':command,
                    'display_kind':'offline replay','scope':'camera609 / H67 B_T5c；独立于T4/T5科研先导',
                    'files':[{'path':str(p),'sha256':sha256(p)} for p in (directory/'job.json',summary_path,seal_path,timing)]})
            except (OSError, ValueError, KeyError, TypeError) as error:
                records.append({'status':'NOT_AVAILABLE','job_id':entry.get('job_id'),'error':str(error),'result':None})
        return {'status':'READ_ONLY_REGISTERED_RECORDS','observed_utc':datetime.now(timezone.utc).isoformat(),
                'live_execution_service':'NOT_CONNECTED','PL_execution':False,'FPGA_status':'NOT_CONNECTED','records':records}
