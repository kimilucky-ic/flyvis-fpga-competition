"""Prepare versioned input bundle; read but never modify controller/B/Golden files."""
import csv, hashlib, json, shutil
from pathlib import Path
import numpy as np
from r_only import file_sha, array_sha
BASE=Path(__file__).resolve().parent
FLY=BASE.parent
FPGA=FLY.parent/'fpga'
OUT=BASE/'artifacts/reference_bundle_v1'
if OUT.exists():raise SystemExit("Bundle exists; preserve it")
OUT.mkdir(parents=True)
def dump(f,x):Path(f).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
a=BASE/'artifacts/init_cpu_r1';b=BASE/'artifacts/init_cpu_r2'
init=np.load(a/'initial_state_full.npy')
replay=np.load(b/'initial_state_full.npy')
assert np.array_equal(init,replay) and file_sha(a/'initial_state_full.npy')==file_sha(b/'initial_state_full.npy')
for name in ['expanded_parameters.npz','nodes_full.csv','initial_state_full.npy','input_node_indices.npy','central_node_indices.npy','cell_types.npy']:
    shutil.copy2(a/name,OUT/name)
identity=json.loads((a/'identity_manifest.json').read_text())
spec=FLY/'upstream/flyvis/flyvis/connectome/fib25-fib19_v2.2.json'
identity.update(connectome_spec_sha256=file_sha(spec),dynamics_type='PPNeuronIGRSynapses',activation_type='ReLU',
    canonical_initial_state_device='cpu',initialization_replay_status='PASS_BITWISE_CPU_INDEPENDENT_PROCESS',
    initial_state_replay_sha256=file_sha(b/'initial_state_full.npy'),
    initial_state_warmup_activity_sha256=file_sha(a/'warmup_activity_full.npy'))
dump(OUT/'identity_manifest.json',identity)
gold=FPGA/'flyvis-visual-experiments/artifacts/golden_reference_v2'
src=np.load(gold/'stimulus.npy',mmap_mode='r')
time=np.load(gold/'time.npy')
selected=[0,1,12,13]
fixed=np.ascontiguousarray(src[selected],dtype='<f4')
assert fixed.shape==(4,485,1,721) and np.isfinite(fixed).all() and (fixed>=0).all() and (fixed<=1).all()
assert np.array_equal(time,np.arange(485)*.005-1.0)
np.save(OUT/'stimulus.npy',fixed);np.save(OUT/'time.npy',time)
rows=list(csv.DictReader((gold/'samples.csv').open()))
with (OUT/'conditions.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['bundle_condition','original_sample','polarity','angle','width','intensity','t_stim','speed'])
    w.writeheader()
    for i,sample in enumerate(selected):
        v=rows[sample]
        w.writerow(dict(bundle_condition=i,original_sample=sample,polarity='ON' if int(v['intensity']) else 'OFF',
             **{k:v[k] for k in ['angle','width','intensity','t_stim','speed']}))
dump(OUT/'stimulus_manifest.json',dict(schema='flyvis-fixed-stimulus/v1',original_source_path=str(gold/'stimulus.npy'),
  source_sha256=file_sha(gold/'stimulus.npy'),original_samples=selected,shape=list(fixed.shape),dtype='little-endian float32',
  stimulus_sha256=file_sha(OUT/'stimulus.npy'),time_sha256=file_sha(OUT/'time.npy'),conditions_sha256=file_sha(OUT/'conditions.csv'),
  dt_s=.005,pre_stimulus_frames=200,reset_each_condition=True,
  time_semantics='time[k] = k*0.005 - 1.0 labels the saved activity AFTER the update using frame k; step_id k is the synchronization identity',
  no_rerender=True,input_node_map_shape=[8,721],input_mapping='same 721 hex intensities replicated into the exact official R1-R8 global-node map',
  initial_state_sha256=identity['initial_state_sha256']))
with np.load(OUT/'expanded_parameters.npz') as z:p={k:z[k] for k in z.files}
nodes=list(csv.DictReader((OUT/'nodes_full.csv').open()))
align=FPGA/'flyvis-circuit-selection/alignment_v01_20261010/artifacts'
candidate_records=[]
for name in ['B_T5c','A_T4c','C_T4T5_all_centers']:
    folder=align/name
    nm=list(csv.DictReader((folder/'node_map.csv').open()))
    assert len(nm)==len(nodes)
    for i,(actual,other) in enumerate(zip(nodes,nm)):
        assert int(other['global_node_index'])==i
        assert all(str(actual[k])==str(other[k]) for k in ['cell_type','u','v'])
    h=np.array([int(v['global_node_index']) for v in nm if v['partition']=='H'],dtype=np.int64)
    r=np.array([int(v['global_node_index']) for v in nm if v['partition']=='R'],dtype=np.int64)
    assert np.array_equal(np.array([int(v['local_index']) for v in nm if v['partition']=='H']),np.arange(len(h)))
    assert np.array_equal(np.array([int(v['local_index']) for v in nm if v['partition']=='R']),np.arange(len(r)))
    mask=np.zeros(len(nodes),dtype=bool);mask[h]=True
    sh=mask[p['source_global']];th=mask[p['target_global']]
    edges={k:np.flatnonzero(v).astype(np.int64) for k,v in dict(HH=sh&th,RH=~sh&th,HR=sh&~th,RR=~sh&~th).items()}
    with np.load(folder/'edge_partition_ids.npz') as other:
        assert set(other.files)==set(edges)
        assert all(np.array_equal(edges[k],other[k]) for k in edges)
    assert np.array_equal(np.sort(np.concatenate(list(edges.values()))),np.arange(identity['n_edges']))
    manifest={k:identity[k] for k in ['checkpoint_sha256','source_commit','expanded_parameters_sha256','nodes_full_sha256','n_nodes','n_edges','dt_s']}
    manifest.update(schema='flyvis-r-only-candidate/v1',candidate_id=name,status='SOFTWARE_TEST_CANDIDATE_NOT_FINAL_FPGA',
        h_global_node_indices=h.tolist(),h_indices_digest=array_sha(h),r_indices_digest=array_sha(r),
        r_edge_indices_digest=array_sha(np.flatnonzero(~th).astype(np.int64)),
        partition_counts={k:len(v) for k,v in edges.items()},partition_ids_digests={k:array_sha(v) for k,v in edges.items()},
        source_node_map=str(folder/'node_map.csv'),source_node_map_sha256=file_sha(folder/'node_map.csv'),
        source_edge_partition=str(folder/'edge_partition_ids.npz'),source_edge_partition_sha256=file_sha(folder/'edge_partition_ids.npz'),
        boundary_profile='UNSELECTED_NOT_FROZEN',numeric_profile='float32 software only',dynamics_type='PPNeuronIGRSynapses',activation_type='ReLU')
    (OUT/'candidates'/name).mkdir(parents=True)
    dump(OUT/'candidates'/name/'candidate_manifest.json',manifest)
    shutil.copy2(folder/'node_map.csv',OUT/'candidates'/name/'node_map.csv')
    np.savez(OUT/'candidates'/name/'edge_partition_ids.npz',**edges)
    candidate_records.append(dict(candidate=name,n_h=len(h),n_r=len(r),edges={k:len(v) for k,v in edges.items()},B_partition_verified_exact=True))
snap=OUT/'controller_snapshots';snap.mkdir()
controller=FPGA/'docs/flyvis_visual_hybrid'
sources={}
for name in ['PHASE1_REVIEW_20261010.md','INTERFACE_CONTRACT.md','PYTHON_REPLACEMENT_GATE.md','INTEGRATION_STATUS.md']:
    path=controller/name;shutil.copy2(path,snap/name);sources[str(path)]=file_sha(path)
acceptance=dict(status='PASS_INPUT_BUNDLE_STATIC_AND_INITIAL_CPU_REPLAY',candidates=candidate_records,
    initial_cpu_bitwise=True,full_nodes=45669,conditions=selected,dt_s=.005,controller_state='DRAFT_NOT_FROZEN',
    controller_source_sha256=sources,other_lane_files_modified=False,Golden_overwritten=False)
dump(OUT/'bundle_acceptance.json',acceptance)
dump(OUT/'artifact_manifest.json',dict(files=[dict(path=str(f.relative_to(OUT)),bytes=f.stat().st_size,sha256=file_sha(f))
     for f in sorted(OUT.rglob('*')) if f.is_file() and f.name!='artifact_manifest.json']))
print('BUNDLE_PASS',json.dumps(acceptance['candidates']),flush=True)
