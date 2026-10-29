"""Freeze input/metric/executor identity, without granting permission to run."""
from pathlib import Path
from datetime import datetime,timezone
import ast,hashlib,json,uuid
HERE=Path(__file__).resolve().parent
PROPOSAL=HERE.parent
def load(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def dump(p,v):
    with p.open('x',encoding='utf-8',newline='\n') as f:
        json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def main():
    r=load(PROPOSAL/'PRE_REGISTRATION_PROPOSED_v1.json')
    for e in load(PROPOSAL/'REVIEW_MANIFEST_v1.json')['files']:
        assert sha(PROPOSAL/e['path'])==e['sha256']
    for e in load(HERE/'input_bundle/artifact_manifest.json')['files']:
        assert sha(HERE/'input_bundle'/e['path'])==e['sha256']
    reuse=load(HERE/'ENGINE_REUSE.json')
    for e in reuse['sources']:
        assert sha(HERE/e['path'])==e['sha256']==sha(e['source'])
    codes=sorted(p for p in HERE.rglob('*.py') if '__pycache__' not in p.parts)
    for p in codes:ast.parse(p.read_text(encoding='utf-8'),filename=str(p))
    metric_keys=['readout_priority','windows_zero_based_inclusive','signed_metrics','official_direction_metrics',
                 'temporal_structure','proposed_thresholds','software_acceptance','stimulus_recommendation_rule','readouts']
    metrics={k:r[k] for k in metric_keys}
    dump(HERE/'FROZEN_METRIC_PROFILE.json',dict(schema='flyvis-functional-metric-profile/v1',
        proposal_sha256=sha(PROPOSAL/'PRE_REGISTRATION_PROPOSED_v1.json'),semantics=metrics,
        thresholds_changed=False,ROIs_changed=False,new_neural_results_inspected=False))
    core=dict(schema='flyvis-functional-campaign-core/v1',campaign_name='phase4_24_FP32_G2_native_GPU_20261011_v1',
        proposal_sha256=sha(PROPOSAL/'PRE_REGISTRATION_PROPOSED_v1.json'),proposal_manifest_sha256=sha(PROPOSAL/'REVIEW_MANIFEST_v1.json'),
        metric_profile_sha256=sha(HERE/'FROZEN_METRIC_PROFILE.json'),input_manifest_sha256=sha(HERE/'input_bundle/artifact_manifest.json'),
        runtime_spec_sha256=sha(HERE/'spec_snapshot/spec_config.json'),candidate_ids=r['candidate_ids'],
        model=r['model'],fixture=dict(shape=[24,485,1,721],stimulus_sha256=sha(HERE/'input_bundle/stimulus.npy'),
            time_sha256=sha(HERE/'input_bundle/time.npy'),conditions_sha256=sha(HERE/'input_bundle/conditions.csv'),
            original_samples=list(range(24)),state_after='saved[k]=a[k+1]; input[k]; original t_label[k]'),
        numeric_profile='FP32_G2_NATIVE_GPU_NO_QUANTIZATION',dt_s=.005,operator=r['operator'],
        modes=['Full','Sham','Ablation'],references=2,replacement_process_repeats=2,
        execution_code_sha256={p.relative_to(HERE).as_posix():sha(p) for p in codes},
        GPU_uuid='GPU-3adf67c6-bc3e-00c7-4193-709fc7ca51b1',GPU_batch=1,
        profile_exclusions=['Q22 hardware common start','camera','FPGA execution','result-selected thresholds/ROIs'])
    cid=digest(core)
    comparisons={n:digest(dict(campaign_id=cid,candidate_id=n,
        candidate_manifest_sha256=sha(HERE/'input_bundle/candidates'/n/'candidate_manifest.json'),
        H_static_sha256=sha(HERE/'input_bundle/candidates'/n/'static_boundary_gpu_native.npz'),
        HR_edge_ids_sha256=sha(HERE/'spec_snapshot'/(n+'_HR_edge_ids.npy')))) for n in r['candidate_ids']}
    binding=dict(campaign_id=cid,comparison_ids=comparisons,candidate_ids=r['candidate_ids'],proposal_sha256=core['proposal_sha256'],
        spec_sha256=core['proposal_sha256'],checkpoint_sha256=r['model']['checkpoint_sha256'],
        expanded_parameters_sha256=r['model']['expanded_parameters_sha256'],initial_state_sha256=r['model']['initial_state_sha256'],
        stimulus_sha256=core['fixture']['stimulus_sha256'],time_sha256=core['fixture']['time_sha256'],
        planned_Full_run_ids={name:str(uuid.uuid4()) for name in ['full_r1','full_r2']},
        planned_run_ids={repeat:{n:{mode:str(uuid.uuid4()) for mode in ['Sham','Ablation']} for n in r['candidate_ids']} for repeat in ['formal_r1','formal_r2']},
        execution_order=['full_r1','full_r2','formal_r1','formal_r2'],
        independent_runs='planned UUIDs only; actual fresh PID/steps must be verified after execution',
        run_authorized=False,neural_updates=0,FPGA_execution=False)
    dump(HERE/'EXECUTION_BINDING.json',binding)
    files=[]
    include=[p for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix in ['.py','.npy','.npz','.csv','.json']]
    for p in sorted(include):
        if p.name.startswith('resource_observation') or p.name.startswith('launch_gate_tests'):continue
        files.append(dict(path=p.relative_to(HERE).as_posix(),bytes=p.stat().st_size,sha256=sha(p)))
    identity=dict(schema='flyvis-functional-campaign-identity/v1',status='INPUT_METRIC_EXECUTOR_IDENTITY_FROZEN_RUN_LOCKED',
        created_utc=datetime.now(timezone.utc).isoformat(),campaign_id=cid,comparison_ids=comparisons,
        proposal_sha256=core['proposal_sha256'],GPU_uuid=core['GPU_uuid'],candidate_ids=core['candidate_ids'],
        canonical_core=core,files=files,code_AST_parse_count=len(codes),
        technical_status='PENDING_FINAL_MACHINE_RATIFICATION',GPU_conflict_status='PENDING_A_COORDINATION',
        human_window_authorized=False,new_neural_updates=0,FPGA_execution=False,
        immutable_identity_does_not_grant_launch_permission=True,
        mutable_authority_record_names=['TECHNICAL_RATIFICATION.json','GPU_COORDINATION_CONFIRMED.json','RUN_WINDOW_AUTHORIZATION.json'])
    dump(HERE/'FROZEN_CAMPAIGN_IDENTITY.json',identity)
    print(json.dumps(dict(status=identity['status'],campaign_id=cid,comparison_ids=comparisons,files=len(files),AST_checked=len(codes),neural_updates=0)))
if __name__=='__main__':main()
