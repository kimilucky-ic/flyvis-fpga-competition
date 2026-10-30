"""Stage immutable inputs/accepted engines for review. Does not import torch/FlyVis."""
from pathlib import Path
import csv, hashlib, json, shutil

HERE=Path(__file__).resolve().parent
P3=HERE.parent/'phase3_ablation_screen_20261010'
OUT=HERE/'pre_run_20261011_r1'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def dump(p,v):
    with p.open('x',encoding='utf-8',newline='\n') as f:
        json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')

def main():
    if (OUT/'input_bundle').exists():raise SystemExit('Existing staging preserved')
    for e in load(HERE/'REVIEW_MANIFEST_v1.json')['files']:
        p=HERE/e['path'];assert p.stat().st_size==e['bytes'] and sha(p)==e['sha256']
    OUT.mkdir(exist_ok=True)
    bundle=OUT/'input_bundle';bundle.mkdir()
    base=P3/'input_bundle_r2';reg=load(HERE/'PRE_REGISTRATION_PROPOSED_v1.json')
    for file in ['initial_state_full.npy','expanded_parameters.npz','identity_manifest.json','nodes_full.csv',
                 'central_node_indices.npy','cell_types.npy','input_node_indices.npy']:
        shutil.copyfile(base/file,bundle/file)
    shutil.copyfile(HERE/'prepared_inputs/stimulus_float32.npy',bundle/'stimulus.npy')
    shutil.copyfile(HERE/'prepared_inputs/time.npy',bundle/'time.npy')
    columns=['bundle_condition','original_sample','polarity','angle','width','intensity','t_stim','speed']
    with (bundle/'conditions.csv').open('x',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=columns);w.writeheader();w.writerows(reg['conditions'])
    for name in reg['candidate_ids']:
        dest=bundle/'candidates'/name;dest.mkdir(parents=True)
        for file in ['candidate_manifest.json','static_boundary_gpu_native.npz','validated_partition_ids.npz','node_map.csv']:
            shutil.copyfile(base/'candidates'/name/file,dest/file)
    dump(bundle/'stimulus_manifest.json',dict(schema='flyvis-fixed-stimulus/v1',shape=[24,485,1,721],
        original_samples=list(range(24)),stimulus_sha256=sha(bundle/'stimulus.npy'),
        conditions_sha256=sha(bundle/'conditions.csv'),time_sha256=sha(bundle/'time.npy'),
        initial_state_sha256=sha(bundle/'initial_state_full.npy'),dt_s=.005,no_rerender=True,
        input_mapping='exact R1-R8 input_node_indices [8,721]',state_semantics='saved[k]=a[k+1] using input[k]; time[k]=k*.005-1'))
    deps=OUT/'dependencies';deps.mkdir()
    copied=[]
    for sub,files in {'b_core':['h_step.py','coordinator.py','gpu_adapter.py','run_closed_loop.py'],
                      'a_snapshot':['r_only.py','full_oracle.py']}.items():
        (deps/sub).mkdir()
        for f in files:
            p=P3/'dependencies'/sub/f;q=deps/sub/f;shutil.copyfile(p,q)
            assert sha(p)==sha(q)
            copied.append(dict(path=q.relative_to(OUT).as_posix(),sha256=sha(q),source=str(p),source_sha256=sha(p),changed=False))
    shutil.copyfile(P3/'gate_service.py',OUT/'gate_service.py')
    copied.append(dict(path='gate_service.py',sha256=sha(OUT/'gate_service.py'),source=str(P3/'gate_service.py'),source_sha256=sha(P3/'gate_service.py'),changed=False))
    for file in ['common.py','bound_adapter.py','run_formal.py']:
        shutil.copyfile(P3/file,OUT/file)
    spec=load(P3/'spec_snapshot/spec_config.json')
    spec['candidates']={n:spec['candidates'][n] for n in reg['candidate_ids']}
    spec['fixture'].update(shape=[24,485,1,721],conditions=[{k:str(v) for k,v in row.items()} for row in reg['conditions']],
        stimulus_sha256=sha(bundle/'stimulus.npy'),time_sha256=sha(bundle/'time.npy'),conditions_sha256=sha(bundle/'conditions.csv'))
    spec['status']='PHASE4_PROPOSED_INPUT_BINDING_NOT_RUN_AUTHORIZATION'
    spec['modes']['Full']['source_reference']=None
    spec['modes']['Full']['reference_policy']='two new shared Full24 references under frozen phase4 campaign; old four-condition reference is overlap regression only'
    (OUT/'spec_snapshot').mkdir()
    dump(OUT/'spec_snapshot/spec_config.json',spec)
    for name in reg['candidate_ids']:
        shutil.copyfile(HERE/'prepared_inputs/operator_ids'/(name+'_HR_edge_ids.npy'),OUT/'spec_snapshot'/(name+'_HR_edge_ids.npy'))
    paths=sorted(p for p in bundle.rglob('*') if p.is_file())
    dump(bundle/'artifact_manifest.json',dict(files=[dict(path=p.relative_to(bundle).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in paths]))
    dump(OUT/'ENGINE_REUSE.json',dict(status='ACCEPTED_ENGINE_BYTES_COPIED_UNCHANGED',sources=copied,
        wrapper_changes='24 conditions, exact new fixture identity, approval/window gate; upstream and old experiments unchanged',
        new_neural_updates=0,GPU_execution=False,FPGA_execution=False))
    print(json.dumps(dict(status='STAGED_REVIEW_INPUTS_AND_ACCEPTED_ENGINES',input_bytes=sum(p.stat().st_size for p in paths),new_neural_updates=0)))

if __name__=='__main__':main()
