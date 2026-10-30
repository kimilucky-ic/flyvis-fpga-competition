"""Phase4 read-only experiment evidence; never simulates a device or creates a job."""
import hashlib
import json
from pathlib import Path
import re

import numpy as np

from data_store import read_json, sha256, read_csv, TARGETS
from phase3_adapter import VerifiedFiles

MODES = {'Full_GPU':'Full GPU','Sham_Ablation':'Sham / Ablation','Python_Replacement':'Python Replacement','FPGA_Replacement':'FPGA Replacement'}
HEX = re.compile(r'[0-9a-f]{64}')
IDENTITY_KEYS={'model','expanded','candidate','node_map','edge_partition','stimulus','initial','time','activity_time','numeric','metrics'}
METRIC_KEYS=['pl_cycles','pl_compute_ms','gpu_compute_ms','ps_compute_ms','gpu_ps_ms','ps_pl_ms','pl_ps_ms','end_to_end_ms','resources']


def scientific_handoff_contract():
    """Discovery metadata only: no package registration, execution or acceptance."""
    return {
        'schema': 'flyvis-scientific-handoff-requirements-v1',
        'status': 'REQUIREMENTS_ONLY_QUERY_INPUT_ADMISSION_SEPARATELY',
        'input_preview': {'url': '/api/controlled-stimuli28',
                          'status': 'QUERY_VERIFIED_STIMULUS_ENDPOINT',
                          'result_status': 'NOT_RUN'},
        'priority_groups': ['four_directions', 'on_off', 'small_target'],
        'source_kind': 'controlled_animation', 'source_is_camera': False,
        'display_kind': 'offline_replay', 'dt_s': .005,
        'stimulus_axes': ['condition', 'step', 'channel', 'hex_pixel'],
        'stimulus_shape': ['C', 'N', 1, 721],
        'full_state_nodes': 45669, 'spatial_T4_T5_nodes': 5768,
        'time_binding': 'input[k] -> Euler_after[k] at input_time[k]+0.005 -> flow[k]',
        'control_metadata': ['condition_id', 'control_condition_ids', 'direction_and_convention',
                             'speed_and_units', 'contrast', 'position_or_trajectory',
                             'random_seed_or_explicit_deterministic'],
        'required_source_artifacts': [
            'generator_source_and_parameters', 'preview_mp4', 'frozen_721_input',
            'full_initial_state_and_initialization', 'ordered_hex_and_global_node_maps',
            'input_and_post_Euler_times', 'source_frame_alignment',
            'model_and_numeric_profile', 'manifest_and_independent_acceptance'],
        'run_header': {
            'identity_fingerprint_keys': sorted(IDENTITY_KEYS),
            'required': ['run_id', 'condition_id', 'backend', 'mode',
                         'numeric_family', 'readout_kind', 'readout_sha256',
                         'intervention_sha256', 'identity_fingerprint',
                         'origin_execution_kind', 'evidence_level', 'acceptance_sha256'],
            'modes': list(MODES) + ['Full_FPGA'],
            'numeric_families': ['STRICT_FP32', 'HYBRID_Q24'],
            'readout_kinds': ['official_DecoderGAVP', 'frozen_local_readout'],
        },
        'missing_result': 'NOT_AVAILABLE',
        'admitted_new_result_packages': 0,
        'policy': 'Reuse original producer schemas and pinned consumers; '
                  'metadata compatibility never admits a result or proves PL execution.',
    }


def scientific_pairing_policy(reference, candidate):
    """Same-condition backend pairing, called AFTER existing file/array verification.

    This is not the acceptance gate. Cross-direction plots deliberately use
    different inputs and must retain separate condition/run identities.
    """
    for header in (reference, candidate):
        require(isinstance(header, dict), 'Scientific run header must be an object')
        for key in ('run_id', 'condition_id', 'backend'):
            require(isinstance(header.get(key), str) and header[key].strip(),
                    'Missing actual scientific run identity: ' + key)
        require(header.get('mode') in (*MODES, 'Full_FPGA'), 'Unknown scientific computation mode')
        require(header.get('numeric_family') in ('STRICT_FP32', 'HYBRID_Q24'),
                'Numerical family must be explicit')
        require(header.get('readout_kind') in ('official_DecoderGAVP', 'frozen_local_readout'),
                'Official flow and local readouts must be named separately')
        digest(header.get('readout_sha256')); digest(header.get('intervention_sha256'))
        fingerprint = header.get('identity_fingerprint')
        require(isinstance(fingerprint, dict) and set(fingerprint) == IDENTITY_KEYS,
                'Incomplete scientific fingerprint')
        for value in fingerprint.values(): digest(value)
    left, right = reference['identity_fingerprint'], candidate['identity_fingerprint']
    # Circuit/partition/profile differences can be the experimental treatment.
    common = ('model', 'expanded', 'node_map', 'stimulus', 'initial', 'time', 'activity_time')
    mismatches = [key for key in common if left[key] != right[key]]
    if reference['condition_id'] != candidate['condition_id']:
        mismatches.append('condition_id')
    readout_matches = all(reference[key] == candidate[key]
                          for key in ('readout_kind', 'readout_sha256')) and left['metrics'] == right['metrics']
    profile_matches = reference['numeric_family'] == candidate['numeric_family'] and left['numeric'] == right['numeric']
    treatment_matches = (reference['intervention_sha256'] == candidate['intervention_sha256']
                         and all(left[key] == right[key] for key in ('candidate', 'edge_partition')))
    same_input_context = not mismatches
    return {
        'schema': 'flyvis-scientific-pairing-policy-v1',
        'status': 'IDENTITY_POLICY_ONLY_NOT_ACCEPTANCE',
        'reference_run_id': reference['run_id'], 'candidate_run_id': candidate['run_id'],
        'mismatched_context': mismatches,
        'same_input_context': same_input_context,
        'functional_pairing_compatible': same_input_context and readout_matches,
        'same_numeric_profile': profile_matches, 'same_intervention': treatment_matches,
        'state_equivalence_context_compatible': same_input_context and profile_matches and treatment_matches,
        'state_comparison_rule': ('PREDECLARED_REFERENCE_AND_TOLERANCE_REQUIRED'
                                  if profile_matches else 'SEPARATE_NUMERIC_REFERENCE_REQUIRED'),
        'readout_matches': readout_matches,
        'numeric_pass': None, 'functional_pass': None,
        'hardware_execution_verified': None,
        'display_kind': 'offline_replay',
    }


def require(ok, message):
    if not ok: raise ValueError(message)


def digest(value):
    require(isinstance(value,str) and HEX.fullmatch(value),'Invalid SHA256')
    return value


def inside(root, relative):
    p = (root/relative).resolve()
    require(p.is_relative_to(root.resolve()),'Evidence path escapes package')
    return p


def validate_events(events, run, steps):
    """Candidate returned != accepted != COMMIT. Board success requires all stages."""
    previous_step, phase, request, candidate, commits, previous_after, references = -1,'IDLE',None,None,0,None,0
    for seq,event in enumerate(events):
        require(event['seq']==seq and event['run_id']==run['run_id'] and event['comparison_id']==run['comparison_id'],'Event sequence/run/comparison mismatch')
        k=event['step_id'];require(isinstance(k,int) and 0<=k<steps,'Invalid event step')
        kind=event['type']
        if kind=='REFERENCE_RECORDED':
            require(run['mode'] in ['Full_GPU','Sham_Ablation'] and k==previous_step+1 and phase in ['IDLE','REFERENCE_RECORDED'],'Invalid reference event')
            before=digest(event['before_digest']);digest(event['input_digest'])
            require(previous_after is None or before==previous_after,'Broken reference state chain')
            previous_after=digest(event['after_digest']);previous_step=k;phase=kind;references+=1
        elif kind=='PREPARED':
            require(k==previous_step+1 and phase in ['IDLE','COMMITTED'],'Prepare before previous unified COMMIT')
            previous_step=k;phase='PREPARED';request=digest(event['request_digest']);candidate=None
            digest(event['old_state_digest']);digest(event['input_digest'])
            require(previous_after is None or event['old_state_digest']==previous_after,'Broken committed state chain')
        else:
            require(k==previous_step and event.get('request_digest')==request,'Wrong step or request')
            if kind=='PL_SUBMITTED':
                require(run['mode']=='FPGA_Replacement' and phase=='PREPARED','Invalid PL submission');phase=kind
            elif kind=='PL_STARTED':
                require(phase=='PL_SUBMITTED','PL start without submission');phase=kind
            elif kind=='CANDIDATE_RETURNED':
                require(phase in (['PL_SUBMITTED','PL_STARTED'] if run['mode']=='FPGA_Replacement' else ['PREPARED']),'Unexpected candidate')
                candidate=digest(event['candidate_sha256']);phase=kind
                if run['mode']=='FPGA_Replacement':
                    require(event.get('source')=='actual_board' and event.get('board_id')==run['board']['board_id'],'Candidate has no matching actual board identity')
                    require(isinstance(event.get('pl_cycles'),int) and event['pl_cycles']>0,'PL cycle count absent')
            elif kind=='VALIDATION_ACCEPTED':
                require(phase=='CANDIDATE_RETURNED' and event.get('candidate_sha256')==candidate and event.get('validation_status')=='PASS','Unvalidated/mismatched candidate')
                require(event.get('validation_scope') and event.get('validation_evidence_sha256'),'No validation scope/evidence');digest(event['validation_evidence_sha256']);phase=kind
            elif kind=='UNIFIED_COMMITTED':
                require(phase=='VALIDATION_ACCEPTED' and event.get('candidate_sha256')==candidate and event.get('state_token')==k+1,'Unified COMMIT before validation or token mismatch')
                previous_after=digest(event['full_after_digest']);phase='COMMITTED';commits+=1
            elif kind in ['REJECTED','FAILED','TIMEOUT']:
                require(phase!='COMMITTED','Failure after COMMIT');phase=kind
            else:raise ValueError('Unknown evidence event')
    return {'committed_steps':commits,'reference_steps':references,'last_step':previous_step if previous_step>=0 else None,'transaction_state':phase}


def verify_package_header(desc, acceptance):
    require(desc['schema']=='flyvis-workbench-evidence-v1','Unknown workbench evidence schema')
    digest(desc['comparison_id'])
    require(set(desc['identity_fingerprint'])==IDENTITY_KEYS,'Incomplete comparison fingerprint')
    for value in desc['identity_fingerprint'].values():digest(value)
    require(hashlib.sha256(json.dumps(desc['identity_fingerprint'],sort_keys=True).encode()).hexdigest()==desc['comparison_id'],'Comparison ID does not bind exact input/state/profile')
    require(desc['display_kind']=='offline_replay','A saved package cannot claim live execution')
    require(acceptance['status']=='PASS' and acceptance['comparison_id']==desc['comparison_id'],'Unaccepted or wrong comparison report')
    require(acceptance['evidence_scope']=='actual_computation' and acceptance['production_data_unchanged'] is True,'Simulation or source changes cannot be admitted')
    require(desc['runs'] and len({r['run_id'] for r in desc['runs']})==len(desc['runs']),'Missing/duplicate runs')
    for r in desc['runs']:
        require(r['mode'] in MODES and r['comparison_id']==desc['comparison_id'],'Wrong mode/cohort')
        require(r['identity_fingerprint']==desc['identity_fingerprint'],'Cross-mode input/a0/model/circuit identity mismatch')
        require(r['origin_execution_kind'] in ['actual_computation','reused_verified_actual_computation'],'Invalid origin execution')
        require(r.get('backend_id') and r.get('device') and r.get('model_id'),'Actual backend/device/model identity missing')
        require(r['run_id'] in acceptance['accepted_run_ids'],'Run not covered by acceptance')
        if r['mode']=='Sham_Ablation':
            require(r.get('variant') in ['Sham','Ablation'] and r.get('intervention_spec_sha256') and r.get('functional_report_role'),'Formal intervention/report missing')
            digest(r['intervention_spec_sha256'])
        if r['mode']=='FPGA_Replacement':
            board=r.get('board') or {}
            require(r['evidence_level']=='ACTUAL_BOARD_CLOSED_LOOP' and board.get('board_id') and board.get('device'),'RTL/OOC/non-board evidence rejected')
            for key in ['bit_sha256','hwh_sha256']:digest(board.get(key))
            require(acceptance.get('physical_board_execution') is True and acceptance.get('live_feedback_closed_loop') is True,'No accepted live-feedback physical computation')


class RecordedPackage(VerifiedFiles):
    """Optional GUI-normalized handoff, only after explicit descriptor/manifest/report pins."""
    def init__(self, spec, store):
        super().init__()
        self.root=Path(spec['root']).resolve()
        require(self.root.is_relative_to(store.root.resolve()) or self.root.is_relative_to((store.root.parent/'fpga').resolve()),'Package outside assigned fly/fpga workspaces')
        for name in ['descriptor.json','manifest.json','acceptance.json']:
            self.check(self.root/name,digest(spec['pins'][name]))
        manifest=read_json(self.root/'manifest.json')
        for entry in manifest['files']:self.check(inside(self.root,entry['path']),digest(entry['sha256']),entry['bytes'])
        self.desc=read_json(self.root/'descriptor.json');self.acceptance=read_json(self.root/'acceptance.json')
        verify_package_header(self.desc,self.acceptance)
        require(not any(r['mode']=='FPGA_Replacement' for r in self.desc['runs']),'NOT_AVAILABLE: independent consumer for ⑥ actual board/feedback acceptance has not been delivered; structural declarations alone cannot enable FPGA')
        self.roles={key:inside(self.root,value) for key,value in self.desc['roles'].items()}
        require(all(p in self.checked for p in self.roles.values()),'Role is not covered by manifest')
        def load(role):
            array=np.load(self.roles[role],allow_pickle=False,mmap_mode='r')
            require(isinstance(array,np.ndarray),'Expected NPY array, not an archive')
            return array
        m=self.desc['input'];self.steps=m['steps'];self.comparison_id=self.desc['comparison_id']
        require(isinstance(self.steps,int) and 0<self.steps<=100000 and m['dt_s']>0,'Invalid grid')
        self.preview=store.datasets[m['preview_dataset_id']];self.sample=m['preview_sample_id'];actual=self.preview.sample(self.sample)
        self.input=load(m['stimulus_role']).reshape(self.steps,721)
        self.time=load(m['time_role']);self.after_time=load(m['activity_time_role'])
        require(self.input.dtype==np.dtype('<f4') and np.isfinite(self.input).all(),'Invalid real stimulus')
        source=self.preview.input_array(self.sample) if hasattr(self.preview,'input_array') else self.preview.stimulus[self.sample,:,0]
        require(np.array_equal(self.input,np.asarray(source,dtype='<f4')),'Preview is not this exact input')
        require(self.time.shape==self.after_time.shape==(self.steps,) and np.allclose(np.diff(self.time),m['dt_s'],atol=1e-12,rtol=0) and np.array_equal(self.after_time,self.time+m['dt_s']),'Input/Euler time mismatch')
        self.cells=load(m['cell_types_role']).tolist();self.ids=load(m['node_ids_role'])
        require(self.cells==self.preview.cells and self.ids.shape==(65,) and self.ids.dtype.kind in 'iu' and len(np.unique(self.ids))==65,'Cell/node mapping differs from verified preview')
        actual_ids=[n['original_node_index'] for n in self.preview.neurons]
        require(np.array_equal(self.ids,actual_ids),'Actual global node IDs mismatch')
        for fingerprint,role in [('stimulus',m['stimulus_role']),('time',m['time_role']),('activity_time',m['activity_time_role'])]:
            require(self.desc['identity_fingerprint'][fingerprint]==self.checked[self.roles[role]],'Input fingerprint does not match file')
        require(m['model_id']==self.preview.info()['model'],'Preview model mismatch')
        require(self.desc['identity_fingerprint']['model']==self.preview.info()['checkpoint_sha256'],'Checkpoint identity mismatch')
        for key,value in self.desc['identity_fingerprint'].items():
            digest(value)
            if key=='model':continue
            role=self.desc['fingerprint_roles'][key]
            require(role in self.roles and self.checked[self.roles[role]]==value,'Fingerprint lacks corresponding verified artifact')
        self.arrays={};self.events={};self.progress={};self.errors={}
        for r in self.desc['runs']:
            activity=load(r['activity_role']);require(activity.shape==(self.steps,65) and activity.dtype==np.dtype('<f4') and np.isfinite(activity).all(),'Incomplete/non-finite central activity')
            require(r['model_id']==m['model_id'] and r['source_activity_sha256']==self.checked[self.roles[r['activity_role']]],'Wrong actual activity/model identity')
            rows=[json.loads(s) for s in self.roles[r['events_role']].read_text('utf-8').splitlines() if s.strip()]
            progress=validate_events(rows,r,self.steps)
            reference=r['mode'] in ['Full_GPU','Sham_Ablation'] and progress['reference_steps']==self.steps and progress['transaction_state']=='REFERENCE_RECORDED'
            committed=progress['committed_steps']==self.steps and progress['transaction_state']=='COMMITTED'
            require(reference or committed,'Incomplete recorded execution')
            if reference:progress['committed_steps']=None
            for e in rows:
                for hash_key,role_key in [('candidate_sha256','candidate_evidence_role'),('validation_evidence_sha256','validation_evidence_role')]:
                    if e['type']==('CANDIDATE_RETURNED' if hash_key=='candidate_sha256' else 'VALIDATION_ACCEPTED'):
                        require(e.get(role_key) in self.roles and self.checked[self.roles[e[role_key]]]==e[hash_key],'Event candidate/validation evidence is not manifest-bound')
            if r['mode']=='FPGA_Replacement':
                for key in ['bit','hwh']:
                    require(r['board'].get(key+'_role') in self.roles and self.checked[self.roles[r['board'][key+'_role']]]==r['board'][key+'_sha256'],'Board build identity is not manifest-bound')
            if r['mode']=='Sham_Ablation':
                report=read_json(self.roles[r['functional_report_role']])
                require(report.get('run_id')==r['run_id'] and report.get('comparison_id')==self.comparison_id and report.get('variant')==r['variant'],'Functional report belongs to another run/cohort')
                require(report.get('execution_status')=='COMPLETED_ACTUAL_COMPUTATION' and report.get('functional_conclusion') in ['PASS','FAIL','INCONCLUSIVE'],'Specification is not an actual functional result')
                spec_role=r.get('intervention_spec_role')
                require(spec_role in self.roles and self.checked[self.roles[spec_role]]==r['intervention_spec_sha256'],'Intervention specification is not manifest-bound')
            self.arrays[r['run_id']]=activity;self.events[r['run_id']]=rows;self.progress[r['run_id']]=progress
        full=next((r for r in self.desc['runs'] if r['mode']=='Full_GPU'),None)
        require(full,'Matching actual Full reference required')
        base=self.arrays[full['run_id']].astype(np.float64)
        for r in self.desc['runs']:
            delta=self.arrays[r['run_id']].astype(np.float64)-base
            self.errors[r['run_id']]={'scope':'65_center_readouts','reference_run_id':full['run_id'],'max_abs':np.max(np.abs(delta),axis=1).tolist(),'MAE':np.mean(np.abs(delta),axis=1).tolist(),'RMSE':np.sqrt(np.mean(delta*delta,axis=1)).tolist(),'not_official_DSI':True}


class Workbench:
    def init__(self, store, phase3, config_path=None):
        self.store,self.phase3=store,phase3
        self.imports=[];self.import_errors=[];self.config={}
        try:
            self.config=read_json(config_path or store.root/'gui_v1/workbench.json')
            require(self.config['schema']=='flyvis-workbench-config-v1','Wrong workbench config')
            if self.config.get('execution_backend') or self.config.get('camera_backend'):
                self.import_errors.append('Configured live backend has not passed a formal connector acceptance; NOT_AVAILABLE')
            for spec in self.config['evidence_packages']:
                try:
                    pkg=RecordedPackage(spec,store)
                    require(pkg.comparison_id not in self.p0_ids() and pkg.comparison_id not in [p.comparison_id for p in self.imports],'Duplicate or overwriting accepted comparison')
                    self.imports.append(pkg)
                except (OSError,ValueError,KeyError,TypeError,AssertionError,EOFError,OverflowError) as e:self.import_errors.append(str(e))
        except (OSError,ValueError,KeyError,TypeError,AssertionError,EOFError,OverflowError) as e:self.import_errors.append(str(e))

    def p0_ids(self):
        return list(self.phase3.packages) if self.phase3 else []

    def source(self, comparison_id):
        if comparison_id in self.p0_ids():
            pkg=self.phase3.packages[comparison_id];pkg.assert_unchanged();return pkg
        pkg=next((p for p in self.imports if p.comparison_id==comparison_id),None)
        if not pkg:raise KeyError('No explicitly admitted comparison')
        pkg.assert_unchanged();return pkg

    def comparisons(self):
        rows=[]
        for c in self.p0_ids()+[p.comparison_id for p in self.imports]:
            try:
                pkg=self.source(c)
                rows.append({'comparison_id':c,'title':pkg.desc.get('title',c[:12]) if isinstance(pkg,RecordedPackage) else '01_off_right · 已验收800步软件闭环','steps':pkg.steps if isinstance(pkg,RecordedPackage) else 800,'display_kind':'offline_replay','status':'VERIFIED_RECORDED_EVIDENCE'})
            except (OSError,ValueError) as e:self.import_errors.append(str(e))
        return rows

    def info(self, comparison_id):
        pkg=self.source(comparison_id)
        p0=not isinstance(pkg,RecordedPackage)
        frozen=pkg.frozen if p0 else None
        runs=[]
        for mode,r in (pkg.descriptor['modes'].items() if p0 else [(r['mode'],r) for r in pkg.desc['runs']]):
            progress={'committed_steps':800 if mode=='Python_Replacement' else None,'reference_steps':800 if mode=='Full_GPU' else None,'last_step':799,'execution_state':'COMPLETED_RECORDED'} if p0 else dict(pkg.progress[r['run_id']],execution_state='COMPLETED_RECORDED')
            metrics={k:(r.get('hardware_metrics') or {}).get(k) for k in METRIC_KEYS}
            runs.append(dict(r,mode=mode,variant=r.get('variant'),backend_id=('FlyVis_Full_torch_CUDA' if mode=='Full_GPU' else 'independent_Python_H_plus_GPU_R') if p0 else r['backend_id'],model_id='flow/0000/000' if p0 else r['model_id'],board_used=mode=='FPGA_Replacement',board_connected_now=None,backend_connected_now=False,hardware_metrics=metrics,display_kind='offline_replay',progress=progress,activity_url=f'/api/workbench/runs/{r["run_id"]}/activity.bin',evidence_url=f'/api/workbench/runs/{r["run_id"]}/events'))
        modes={k:{'label':v,'status':'AVAILABLE_RECORDED' if any(r['mode']==k for r in runs) else 'NOT_AVAILABLE','runs':[r['run_id'] for r in runs if r['mode']==k],'reason':None if any(r['mode']==k for r in runs) else 'No explicitly admitted actual computation/report in this comparison'} for k,v in MODES.items()}
        preview=self.store.datasets['controlled6'] if p0 else pkg.preview
        sample=1 if p0 else pkg.sample;d=preview.info();s=preview.sample(sample)
        return {'comparison_id':comparison_id,'display_kind':'offline_replay','steps':800 if p0 else pkg.steps,'dt_s':.005 if p0 else pkg.desc['input']['dt_s'],'input_time_s':frozen.time.tolist() if p0 else pkg.time.tolist(),'activity_time_s':frozen.activity_time.tolist() if p0 else pkg.after_time.tolist(),'identity_fingerprint':frozen.fingerprint if p0 else pkg.desc['identity_fingerprint'],'model_id':'flow/0000/000' if p0 else pkg.desc['input']['model_id'],'modes':modes,'runs':runs,'preview':{'dataset':d,'sample':s,'stimulus_url':s['stimulus']['url']},'cell_types':frozen.cells if p0 else pkg.cells,'central_global_ids':frozen.central_ids.tolist() if p0 else pkg.ids.tolist(),'errors':pkg.errors if p0 else pkg.errors,'error_scope':'full_network_and_registered_groups' if p0 else '65_center_readouts_only','formal_functional_reports':[{'run_id':r['run_id'],'variant':r.get('variant'),'report_url':f'/api/workbench/runs/{r["run_id"]}/functional-report'} for r in runs if r['mode']=='Sham_Ablation'],'official_DSI':{'status':'NOT_AVAILABLE','reason':'This comparison does not adopt a new official direction assay; old edge24 metrics remain in original display'},'current_board_connection':{'status':'NOT_AVAILABLE','board_id':None,'observed_utc':None},'current_backend_connection':{'status':'NOT_AVAILABLE','reason':'No formally accepted live execution adapter'}}

    def status(self):
        comparisons=self.comparisons()
        return {'schema':'flyvis-workbench-status-v1','status':'READY_FOR_EVIDENCE' if comparisons else 'NOT_AVAILABLE','display_kind':'offline_replay' if comparisons else None,'comparisons':comparisons,'mode_ids':MODES,'execution_backend':{'status':'NOT_AVAILABLE','run_id':None,'job_id':None,'connected':False,'reason':'Formal backend service has not been connected; no job has been created'},'camera_input':{'status':'NOT_AVAILABLE','capture_open':False,'contract_owner':'⑤ camera_pipeline','accepted_recorded_input_available':'camera1' in self.store.datasets},'import_errors':list(dict.fromkeys(self.import_errors)),'live_refresh_policy':'manual refresh; no simulated progress or real-time requirement'}

    def find_run(self, run_id):
        for c in self.p0_ids()+[p.comparison_id for p in self.imports]:
            pkg=self.phase3.packages[c] if c in self.p0_ids() else next(p for p in self.imports if p.comparison_id==c)
            raw=pkg.descriptor['modes'].values() if not isinstance(pkg,RecordedPackage) else pkg.desc['runs']
            if any(r['run_id']==run_id for r in raw):
                info=self.info(c)
                return pkg,next(r for r in info['runs'] if r['run_id']==run_id),info
        raise KeyError('No explicitly admitted run')

    def activity(self, run_id):
        pkg,r,info=self.find_run(run_id)
        values=pkg.arrays[r['mode']][:,pkg.frozen.central_ids] if not isinstance(pkg,RecordedPackage) else pkg.arrays[run_id]
        return np.ascontiguousarray(values,dtype='<f4').tobytes(),r['source_activity_sha256'],info['comparison_id']

    def events(self, run_id):
        pkg,r,info=self.find_run(run_id)
        p0=not isinstance(pkg,RecordedPackage)
        path=pkg.roles[r['step_status_role']] if p0 else pkg.roles[r['events_role']]
        rows=[json.loads(line) for line in path.read_text('utf-8').splitlines() if line.strip()]
        return {'run_id':run_id,'comparison_id':info['comparison_id'],'display_kind':'offline_replay','event_schema':'producer_original_P0' if p0 else 'flyvis-workbench-event-v1','source_sha256':pkg.checked[path],'events':rows,'note':'Recorded producer events; missing stages are NOT_RECORDED, never fabricated'}

    def step(self, run_id, k):
        pkg,r,info=self.find_run(run_id);require(0<=k<info['steps'],'Step out of range')
        rows=[e for e in self.events(run_id)['events'] if e['step_id']==k]
        statuses=[e.get('status',e.get('type')) for e in rows]
        p0=not isinstance(pkg,RecordedPackage)
        commit=next((e for e in rows if e.get('status')=='COMMITTED' or e.get('type')=='UNIFIED_COMMITTED'),None)
        candidate=next((e for e in rows if e.get('type')=='CANDIDATE_RETURNED'),None)
        validation=next((e for e in rows if e.get('type')=='VALIDATION_ACCEPTED'),None)
        reference=any(e.get('type')=='REFERENCE_RECORDED' for e in rows) or r['mode']=='Full_GPU' and p0
        return {'run_id':run_id,'comparison_id':info['comparison_id'],'step_id':k,'input_time_s':info['input_time_s'][k],'activity_time_s':info['activity_time_s'][k],'display_kind':'offline_replay','selected_step_is_execution_progress':False,'producer_statuses':statuses,'pl_status':'NOT_APPLICABLE' if r['mode']!='FPGA_Replacement' else 'RECORDED_RESULT_RETURNED' if candidate else 'NOT_RECORDED','candidate':candidate,'candidate_status':'RETURNED_RECORDED' if candidate else 'NOT_RECORDED','unified_commit':commit,'commit_status':'COMMITTED_RECORDED' if commit else 'REFERENCE_RECORDED' if reference else 'NOT_RECORDED','validation':validation or ({'status':'PASS_SOURCE_CHAIN','scope':'GUI independently verified actual saved state chain and registered software comparison; no board validation'} if p0 else None),'validation_status':'PASS_SOURCE_CHAIN' if p0 else 'PASS_RECORDED' if validation else 'NOT_RECORDED','board_connected_now':None}

    def functional_report(self, run_id):
        pkg,r,_=self.find_run(run_id)
        require(isinstance(pkg,RecordedPackage) and r['mode']=='Sham_Ablation','No admitted functional report')
        return pkg.roles[r['functional_report_role']].read_bytes()
