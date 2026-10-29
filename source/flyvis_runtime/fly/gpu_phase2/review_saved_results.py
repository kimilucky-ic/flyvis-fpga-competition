"""Independent saved-array/hash review. No neural inference/rendering."""
import csv,hashlib,json,os,subprocess
from pathlib import Path
os.environ.update(MPLBACKEND='Agg',MPLCONFIGDIR='/opt/flyvis-phase2-data/matplotlib')
import numpy as np,matplotlib.pyplot as plt
from r_only import file_sha
BASE=Path(__file__).resolve().parent;A=BASE/'artifacts';OUT=A/'final_acceptance_v1'
if OUT.exists():raise SystemExit('Final report exists; preserved')
OUT.mkdir()
def load(path):return json.loads(Path(path).read_text())
def dump(path,x):Path(path).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
def metric(a,b):
 d=np.asarray(a,dtype=np.float64)-np.asarray(b,dtype=np.float64)
 return dict(max_abs=float(np.abs(d).max()),mae=float(np.abs(d).mean()),rmse=float(np.sqrt((d*d).mean())),
 allclose=bool(np.allclose(a,b,atol=1e-5,rtol=1e-5)),bitwise=bool(np.array_equal(a,b)))
def raw_sha(path):
 ar=np.load(path,mmap_mode='r');h=hashlib.sha256()
 for condition in range(ar.shape[0]):
  for begin in range(0,ar.shape[1],32):
   h.update(np.ascontiguousarray(ar[condition,begin:begin+32]).tobytes())
 return h.hexdigest()
cpu=load(A/'r_only_cpu_r3/acceptance.json');gpu=load(A/'r_only_gpu_r2/acceptance.json');repeat=load(A/'r_only_gpu_r3/acceptance.json')
assert all(v['status']=='PASS_R_ONLY_SERVICE_SINGLE_STEP' for v in [cpu,gpu,repeat])
for name in ['r_only.py','full_oracle.py']:
 assert cpu['implementation_sha256'][name]==gpu['implementation_sha256'][name]==repeat['implementation_sha256'][name]==file_sha(BASE/name)
assert file_sha(A/'r_only_cpu_r3/validate_r_only_snapshot.py')==cpu['implementation_sha256']['validate_r_only.py']
assert gpu['implementation_sha256']['validate_r_only.py']==repeat['implementation_sha256']['validate_r_only.py']==file_sha(BASE/'validate_r_only.py')
for key in ['full_activity_raw_stream_sha256','r_activity_raw_stream_sha256','initial_state_sha256','stimulus_sha256','candidate_sha256','expanded_parameters_sha256']:
 assert gpu[key]==repeat[key]
records={}
for run,accept in [('r_only_cpu_r2',cpu),('r_only_gpu_r2',gpu)]:
 for filename,key in [('full_activity.npy','full_activity_raw_stream_sha256'),('r_activity.npy','r_activity_raw_stream_sha256')]:
  path=A/run/filename
  actual=raw_sha(path);assert actual==accept[key]
  records[str(path.relative_to(BASE))]=dict(shape=list(np.load(path,mmap_mode='r').shape),dtype='float32',
    npy_sha256=file_sha(path),raw_stream_sha256=actual,independent_replay_stream_match=True)
dump(OUT/'recorded_timeseries_acceptance.json',dict(status='PASS_SAVED_ALL_NODES_AND_R_VS_INDEPENDENT_REPLAY',files=records))
B=A/'reference_bundle_v1';BG=A/'reference_bundle_gpu_native_v1'
for name in ['initial_state_full.npy','stimulus.npy','time.npy','nodes_full.csv','input_node_indices.npy']:
 assert file_sha(B/name)==file_sha(BG/name)
a0=np.load(B/'initial_state_full.npy');a02=np.load(A/'init_cpu_r2/initial_state_full.npy');a0g=np.load(A/'init_gpu_r1/initial_state_full.npy')
assert np.array_equal(a0,a02)
init=dict(status='PASS_FULL_INITIAL_STATE_REPRODUCIBLE',shape=[45669],dtype='little-endian float32',
 canonical_sha256=file_sha(B/'initial_state_full.npy'),cpu_independent_replay=metric(a0,a02),native_gpu_adaptation_comparison=metric(a0,a0g),
 common_a0_cpu_gpu_input_bytes_identical=True,actual_gray_steps=200,dt_s=.005,gray=.5,
 starts_from_bias_then_adapts=True,is_bias=False,initial_max_abs_difference_from_bias=load(A/'init_cpu_r1/identity_manifest.json')['initial_state_max_abs_difference_from_bias'],
 dynamic_keys=['nodes.activity'],warmup_native_gpu_state_used_as_comparison_input=False)
assert init['native_gpu_adaptation_comparison']['allclose']
dump(OUT/'initial_state_replay_acceptance.json',init)
fullcpu=np.load(A/'r_only_cpu_r2/full_activity.npy',mmap_mode='r');fullgpu=np.load(A/'r_only_gpu_r2/full_activity.npy',mmap_mode='r')
rcpu=np.load(A/'r_only_cpu_r2/r_activity.npy',mmap_mode='r');rgpu=np.load(A/'r_only_gpu_r2/r_activity.npy',mmap_mode='r')
H=np.load(A/'r_only_gpu_r2/h_global_node_indices.npy');central=np.load(B/'central_node_indices.npy').astype(int)
rows=[]
for c in range(4):
 for k in range(485):
  row=dict(condition=c,original_sample=[0,1,12,13][c],step_id=k,time_s=k*.005-1)
  for label,x,y in [('Full',fullcpu[c,k],fullgpu[c,k]),('R',rcpu[c,k],rgpu[c,k]),
                    ('H_ROI_in_Full',fullcpu[c,k,H],fullgpu[c,k,H]),('central65',fullcpu[c,k,central],fullgpu[c,k,central])]:
   m=metric(x,y);assert m['allclose'],(c,k,label,m)
   for name,value in m.items():row[label+'_'+name]=value
  rows.append(row)
with (OUT/'cpu_gpu_step_errors.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
cross={label:dict(max_abs=max(r[label+'_max_abs'] for r in rows),max_step_mae=max(r[label+'_mae'] for r in rows),
 max_step_rmse=max(r[label+'_rmse'] for r in rows),all_steps_allclose=True,all_steps_bitwise=all(r[label+'_bitwise'] for r in rows))
 for label in ['Full','R','H_ROI_in_Full','central65']}
dump(OUT/'cpu_gpu_comparison.json',dict(status='PASS_NATIVE_PROFILE_CPU_GPU_SAME_INPUT_A0',steps=1940,atol=1e-5,rtol=1e-5,
 common_checkpoint_input_a0=True,native_expanded_parameters_bitwise_identical=False,
 expanded_parameter_differences=load(A/'device_expanded_parameter_difference.json'),metrics=cross,
 scope='Original Full trajectories and original-vs-R single-step outputs; not independent-H closed-loop drift'))
# Scientific audit plots, not biological tuning claims.
fig,axes=plt.subplots(2,2,figsize=(11,7),sharex=True)
for c,ax in enumerate(axes.flat):
 selected=[v for v in rows if v['condition']==c]
 ax.plot([v['time_s'] for v in selected],[v['Full_max_abs'] for v in selected],label='Full CPU vs GPU')
 ax.plot([v['time_s'] for v in selected],[v['R_max_abs'] for v in selected],label='R CPU vs GPU',linestyle='--')
 ax.set_title('sample '+str([0,1,12,13][c]));ax.set_ylabel('max absolute activity error');ax.grid(alpha=.3);ax.legend(fontsize=8)
for ax in axes[-1]:ax.set_xlabel('official after-update time label (s)')
fig.suptitle('Same checkpoint, input bytes and a0; native CPU/CUDA expanded parameter profiles');fig.tight_layout()
fig.savefig(OUT/'step_error_audit.png',dpi=180);plt.close(fig)
pert=load(A/'r_only_gpu_r2/h_perturbation_acceptance.json')
fig,ax=plt.subplots(figsize=(8,4))
ax.bar(['positive HR edge','negative HR edge'],[v['selected_target_activity_delta'] for v in pert['cases']],color=['#198a74','#bb5864'])
ax.axhline(0,color='black',linewidth=.8);ax.set_ylabel('R next activity change');ax.set_title('Actual old H +0.5 perturbation through original HR edges');fig.tight_layout()
fig.savefig(OUT/'h_to_r_perturbation.png',dpi=180);plt.close(fig)
fig,ax=plt.subplots(figsize=(9,4))
for case in pert['cases']:
 target=case['r_target_global'];ax.plot(np.load(B/'time.npy'),fullgpu[0,:,target],label='R global '+str(target))
ax.set_xlabel('official after-update time label (s)');ax.set_ylabel('original Full activity');ax.set_title('Selected R targets: frozen OFF 0 degree reference');ax.legend();fig.tight_layout()
fig.savefig(OUT/'r_reference_activity_examples.png',dpi=180);plt.close(fig)
# Recheck source and preserved historical Golden manifests.
src=BASE.parent/'upstream/flyvis'
commit=subprocess.check_output(['git','-C',str(src),'rev-parse','HEAD'],text=True).strip()
dirty=subprocess.check_output(['git','-C',str(src),'status','--porcelain','--untracked-files=no'],text=True).strip()
assert not dirty and commit==cpu['source_commit']
historical=[]
for folder in [BASE.parent/'artifacts/golden_reference_v1',BASE.parent/'artifacts/moving_edge_minimal_cpu_v1',
              BASE.parent.parent/'fpga/flyvis-visual-experiments/artifacts/golden_reference_v2']:
 manifest=load(folder/'manifest.json')
 entries=manifest.get('files',manifest.get('artifacts',[])) if isinstance(manifest,dict) else manifest
 if isinstance(entries,dict):entries=[dict(path=k,sha256=v) if isinstance(v,str) else dict(path=k,**v) for k,v in entries.items()]
 count=0
 for record in entries:
  name=record.get('path',record.get('file'));expected=record.get('sha256')
  if not name or not expected:continue
  path=Path(name.replace("\\","/"))
  if not path.is_absolute():path=folder/path
  assert path.exists(),str(path)
  assert file_sha(path)==expected
  count+=1
 assert count==len(entries)
 historical.append(dict(path=str(folder/'manifest.json'),verified_entries=count))
accept=dict(status='PASS_A_FULL_A0_AND_REAL_R_ONLY_CPU_GPU',date='2026-10-10',
 evidence_level='SOFTWARE_REFERENCE_AND_R_ONLY_SINGLE_STEP',full_initial_state=init,recorded_timeseries_status='PASS',
 cpu_r_only_status=cpu['status'],gpu_r_only_status=gpu['status'],cpu_same_device_max_abs=cpu['max_abs'],
 gpu_same_device_max_abs=gpu['max_abs'],gpu_independent_replay_bitwise=True,steps_per_device=1940,
 production_path_proof='PASS_OFFICIAL_FULL_UPDATE_DISABLED_R_SIZED_SCATTER',
 h_live_old_state_perturbation='PASS_POSITIVE_AND_NEGATIVE_HR',generic_candidates='PASS_T4c_UNION_RECEPTOR',
 error_semantics='PASS_INVALID_INPUT_REJECTED_STATELESS_NO_MUTATION',native_cpu_gpu_cross_comparison=cross,
 CPU_full_and_R_parameter_sha256=cpu['expanded_parameters_sha256'],GPU_full_and_R_parameter_sha256=gpu['expanded_parameters_sha256'],
 common_a0_stimulus_exact=True,original_checkpoint_weights_unchanged=True,upstream_tracked_source_clean=True,
 source_commit=commit,historical_manifests=historical,
 per1940steps_timing_s=dict(cpu_R=cpu['timed_r_only_s'],cpu_Full=cpu['timed_full_s'],gpu_R=gpu['timed_r_only_s'],gpu_Full=gpu['timed_full_s']),
 peak_cuda_allocated_bytes=gpu['peak_cuda_allocated_bytes'],no_H_backend_production_implemented=True,
 closed_loop_status='NOT_TESTED_REQUIRES_B_LIVE_H_AND_ATOMIC_BARRIER',hardware_evidence='NONE',
 H_final_FPGA_selection='NOT_FROZEN',numeric_physical_profiles='NOT_FROZEN',other_workline_files_modified_by_A=False,
 previous_instrumentation_failures_retained=['r_only_cpu_r1','r_only_cpu_r2'],GPU_parameter_identity_rejection_retained='r_only_gpu_r1')
dump(OUT/'acceptance.json',accept)
dump(OUT/'artifact_manifest.json',dict(files=[dict(path=f.name,bytes=f.stat().st_size,sha256=file_sha(f)) for f in sorted(OUT.iterdir()) if f.is_file() and f.name!='artifact_manifest.json']))
print('FINAL_A_ACCEPTANCE',json.dumps(dict(status=accept['status'],cpu_max_abs=cpu['max_abs'],gpu_max_abs=gpu['max_abs'],native_cross=cross,
 init_gpu_max_abs=init['native_gpu_adaptation_comparison']['max_abs'],historical_manifests=historical)),flush=True)
