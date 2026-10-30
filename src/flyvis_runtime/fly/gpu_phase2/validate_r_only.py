"""Independent actual Full/R single-step acceptance. NOT a closed-loop H replacement."""
import argparse, contextlib, csv, hashlib, json, os, platform, sys, time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--device',choices=['cpu','cuda'],required=True);p.add_argument('--run',required=True);p.add_argument('--record-full',action='store_true');p.add_argument('--bundle',default='reference_bundle_v1')
args=p.parse_args()
BASE=Path(__file__).resolve().parent;BUNDLE=BASE/'artifacts'/args.bundle;OUT=BASE/'artifacts'/args.run
if OUT.exists():raise SystemExit('Existing run preserved; choose a new --run')
OUT.mkdir(parents=True)
os.environ.update(CUDA_VISIBLE_DEVICES='0' if args.device=='cuda' else '-1',FLYVIS_ROOT_DIR='/opt/flyvis-phase2-data',
 MPLBACKEND='Agg',MPLCONFIGDIR='/opt/flyvis-phase2-data/matplotlib',NUMBA_CACHE_DIR='/opt/flyvis-phase2-data/numba',
 TIMEZONE='Asia/Shanghai',CUBLAS_WORKSPACE_CONFIG=':4096:8')
import numpy as np,torch
torch.set_num_threads(1);torch.set_num_interop_threads(1);torch.manual_seed(0)
torch.use_deterministic_algorithms(True);torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
from r_only import RStepService, InterfaceError, file_sha, array_sha
from full_oracle import FullNetworkOracle
def dump(f,x):Path(f).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
def sync():
 if args.device=='cuda':torch.cuda.synchronize()
def arr(t):return np.ascontiguousarray(t.detach().cpu().numpy())
def tensor(a):return torch.from_numpy(np.array(a,copy=True)).to(service.device)
def metrics(a,b):
 d=np.asarray(a,dtype=np.float64)-np.asarray(b,dtype=np.float64)
 return dict(max_abs=float(np.max(np.abs(d))),mae=float(np.mean(np.abs(d))),rmse=float(np.sqrt(np.mean(d*d))),
   allclose=bool(np.allclose(a,b,atol=1e-5,rtol=1e-5)),bitwise=bool(np.array_equal(a,b)))
def create(name):
 return RStepService(BUNDLE/'expanded_parameters.npz',BUNDLE/'identity_manifest.json',
    BUNDLE/'candidates'/name/'candidate_manifest.json',device=args.device)
service=create('B_T5c')
oracle=FullNetworkOracle(BUNDLE/'identity_manifest.json',device=args.device)
ident=service.identity
for name,key in [('initial_state_full.npy','initial_state_sha256'),('nodes_full.csv','nodes_full_sha256')]:
 assert file_sha(BUNDLE/name)==ident[key]
stim_manifest=json.loads((BUNDLE/'stimulus_manifest.json').read_text())
assert file_sha(BUNDLE/'stimulus.npy')==stim_manifest['stimulus_sha256']
assert file_sha(BUNDLE/'time.npy')==stim_manifest['time_sha256']
stim=np.load(BUNDLE/'stimulus.npy',mmap_mode='r')
initial=np.load(BUNDLE/'initial_state_full.npy')
assert initial.shape==(45669,) and initial.dtype==np.float32
if args.record_full:
 full_out=np.lib.format.open_memmap(OUT/'full_activity.npy',mode='w+',dtype=np.float32,shape=(4,485,45669))
 r_out=np.lib.format.open_memmap(OUT/'r_activity.npy',mode='w+',dtype=np.float32,shape=(4,485,service.n_r))
np.save(OUT/'r_global_node_indices.npy',service.r_indices)
np.save(OUT/'h_global_node_indices.npy',service.h_indices)
central=np.load(BUNDLE/'central_node_indices.npy').astype(np.int64)
central_out=np.zeros((4,485,len(central)),np.float32)
h_out=np.zeros((4,485,len(service.h_indices)),np.float32)
full_sha=hashlib.sha256();r_sha=hashlib.sha256()
errors=[];full_s=0;r_s=0;key_old={}
if args.device=='cuda':torch.cuda.reset_peak_memory_stats()
start=time.perf_counter()
for condition in range(4):
 old=tensor(initial);old_initial_copy=old.clone()
 for k in range(485):
  frame=tensor(stim[condition,k,0])
  before=old.clone() if k in [0,200,240,484] else None
  sync();t0=time.perf_counter();res=service.step(old,frame,step_id=k,run_id=args.run,condition_id=str(stim_manifest['original_samples'][condition]));sync();r_s+=time.perf_counter()-t0
  sync();t0=time.perf_counter();new=oracle.step(old,frame);sync();full_s+=time.perf_counter()-t0
  fa=arr(new);ra=arr(res.activity);expected=fa[service.r_indices]
  m=metrics(ra,expected);assert m['allclose'],(condition,k,m)
  assert np.array_equal(arr(res.global_node_indices),service.r_indices) and res.step_id==k and res.status=='CANDIDATE_NOT_COMMITTED'
  if before is not None:assert torch.equal(old,before)
  if condition==0 and k in [0,200,240,484]:key_old[k]=arr(old)
  if args.record_full:full_out[condition,k]=fa;r_out[condition,k]=ra
  full_sha.update(fa.tobytes());r_sha.update(ra.tobytes())
  errors.append(dict(condition=condition,original_sample=stim_manifest['original_samples'][condition],step_id=k,
    time_s=k*.005-1.0,**m))
  central_out[condition,k]=fa[central];h_out[condition,k]=fa[service.h_indices]
  old=new
 if args.record_full:full_out.flush();r_out.flush()
 print('CONDITION_PASS',json.dumps(dict(condition=condition,steps=485,max_abs=max(x['max_abs'] for x in errors[-485:]),r_s=r_s,full_s=full_s)),flush=True)
elapsed=time.perf_counter()-start
with (OUT/'step_errors.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(errors[0]));w.writeheader();w.writerows(errors)
np.save(OUT/'activity_central.npy',central_out);np.save(OUT/'activity_h_full_reference.npy',h_out)
# Guarded production test: all original Full update entrypoints made unusable.
old=tensor(key_old[240]);frame=tensor(stim[0,240,0])
baseline=service.step(old,frame,step_id=240,run_id=args.run,condition_id='0')
calls=[];saved_scatter=torch.Tensor.scatter_add_
def traced_scatter(self,dim,index,src):
 calls.append(dict(result_shape=list(self.shape),edge_count=int(index.numel()),max_target=int(index.max())))
 return saved_scatter(self,dim,index,src)
def forbidden(*a,**k):raise AssertionError("FORBIDDEN ORIGINAL FULL UPDATE")
with contextlib.ExitStack() as stack:
 def patch(obj,name,value):
  previous=getattr(obj,name);setattr(obj,name,value);stack.callback(setattr,obj,name,previous)
 for obj,name in [(oracle.net,'_next_state'),(oracle.net,'forward'),(oracle.net,'target_sum'),(oracle.net.dynamics,'write_state_velocity')]:
  patch(obj,name,forbidden)
 patch(torch.Tensor,'scatter_add_',traced_scatter)
 # FlyVis's default-device TorchFunction mode redispatches Python wrappers.
 # R-only operations already use explicit devices; disable it only in this spy.
 default_device=torch.get_default_device()
 torch.set_default_device(None);stack.callback(torch.set_default_device,default_device)
 guarded=service.step(old,frame,step_id=240,run_id=args.run,condition_id='0')
assert torch.equal(guarded.activity,baseline.activity)
dump(OUT/'scatter_trace.json',calls)
assert len(calls)==1 and calls[0]['result_shape']==[service.n_r] and calls[0]['edge_count']==service.n_r_edges and 0<=calls[0]['max_target']<service.n_r
production_proof=dict(status='PASS',full_entrypoints_disabled=['Network._next_state','Network.forward','Network.target_sum','dynamics.write_state_velocity'],
 original_full_callable_dependency=False,guarded_result_bitwise=True,scatter_trace=calls,updated_nodes=service.n_r,
 h_next_state_allocated=False,spy_default_device_mode_disabled=True,note='Code path contains only target-R edges and R-sized update vectors; Full oracle is separate')
dump(OUT/'production_path_proof.json',production_proof)
# Controlled positive/negative-weight H source perturbations from real HR edges.
with np.load(BUNDLE/'expanded_parameters.npz') as z:params={k:z[k] for k in z.files}
hm=np.zeros(45669,dtype=bool);hm[service.h_indices]=True
hr=np.flatnonzero(hm[params['source_global']] & ~hm[params['target_global']])
perturbations=[]
delta_rows=[]
np.save(OUT/'perturbation_old_full.npy',arr(old));np.save(OUT/'perturbation_hex_frame.npy',arr(frame))
for sign_label,sign_test in [('positive',params['effective_weight'][hr]>0),('negative',params['effective_weight'][hr]<0)]:
 allowed=hr[sign_test];e=int(allowed[np.argmax(np.abs(params['effective_weight'][allowed]))])
 source=int(params['source_global'][e]);target=int(params['target_global'][e])
 changed=old.clone();before=float(changed[source]);after=max(before,0.0)+.5;changed[source]=after
 actual=service.step(changed,frame,step_id=240,run_id=args.run,condition_id='perturbed-'+sign_label)
 full_changed=oracle.step(changed,frame)
 match=metrics(arr(actual.activity),arr(full_changed)[service.r_indices]);assert match['allclose']
 delta=arr(actual.activity)-arr(baseline.activity)
 changed_targets=service.r_indices[np.abs(delta)>1e-7]
 possible=np.unique(params['target_global'][hr[params['source_global'][hr]==source]])
 assert len(changed_targets)>0 and np.isin(changed_targets,possible).all()
 target_local=int(np.flatnonzero(service.r_indices==target)[0])
 assert abs(float(delta[target_local]))>1e-7
 np.save(OUT/('perturbation_'+sign_label+'_r_delta.npy'),delta)
 for g,d in zip(service.r_indices,delta):
  if abs(float(d))>1e-7:delta_rows.append(dict(case=sign_label,h_source_global=source,r_target_global=int(g),activity_delta=float(d)))
 info=dict(status='PASS',case=sign_label,original_hr_edge=e,h_source_global=source,r_target_global=target,
   actual_edge_weight=float(params['effective_weight'][e]),old_h_value=before,perturbed_old_h_value=after,
   changed_r_targets=int(len(changed_targets)),max_abs_r_change=float(np.max(np.abs(delta))),
   selected_target_activity_delta=float(delta[target_local]),perturbed_full_comparison=match,
   no_recorded_trajectory_read=True,same_step_old_state=True)
 perturbations.append(info)
assert torch.equal(service.step(old,frame,step_id=240,run_id=args.run,condition_id='0').activity,baseline.activity)
dump(OUT/'h_perturbation_acceptance.json',dict(status='PASS',cases=perturbations,base_after_perturbed_calls_bitwise=True))
with (OUT/'h_perturbation_R_delta.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(delta_rows[0]));w.writeheader();w.writerows(delta_rows)
# Validate different H sets and an H containing a receptor (input must exclude it).
generic=[]
for name in ['A_T4c','C_T4T5_all_centers']:
 other=create(name)
 result=other.step(old,frame,step_id=240,run_id=args.run,condition_id='generic')
 m=metrics(arr(result.activity),arr(oracle.step(old,frame))[other.r_indices]);assert m['allclose']
 generic.append(dict(candidate=name,H=len(other.h_indices),R=other.n_r,**m))
manifest=json.loads((BUNDLE/'candidates/B_T5c/candidate_manifest.json').read_text())
receptor=int(params['input_node_index'][0,0])
custom_h=np.array([receptor],dtype=np.int64);custom_mask=np.zeros(45669,dtype=bool);custom_mask[custom_h]=True
sh=custom_mask[params['source_global']];th=custom_mask[params['target_global']]
manifest.update(candidate_id='TEST_ONLY_ONE_RECEPTOR',h_global_node_indices=custom_h.tolist(),h_indices_digest=array_sha(custom_h),
 r_indices_digest=array_sha(np.flatnonzero(~custom_mask).astype(np.int64)),
 r_edge_indices_digest=array_sha(np.flatnonzero(~th).astype(np.int64)),
 partition_counts={k:int(v.sum()) for k,v in dict(HH=sh&th,RH=~sh&th,HR=sh&~th,RR=~sh&~th).items()})
custom=OUT/'test_only_receptor_manifest.json';dump(custom,manifest)
other=RStepService(BUNDLE/'expanded_parameters.npz',BUNDLE/'identity_manifest.json',custom,device=args.device)
asymmetric=tensor(np.linspace(.1,.9,721,dtype=np.float32))
m=metrics(arr(other.step(old,asymmetric,step_id=240,run_id=args.run,condition_id='receptor').activity),arr(oracle.step(old,asymmetric))[other.r_indices])
assert m['allclose']
generic.append(dict(candidate='TEST_ONLY_ONE_RECEPTOR',H=1,R=other.n_r,excluded_receptor=receptor,**m))
dump(OUT/'generic_candidate_acceptance.json',dict(status='PASS',cases=generic))
# Failed validation must never advance or mutate caller state.
bad=[]
def rejected(name,call):
 try:call()
 except InterfaceError as ex:bad.append(dict(case=name,status='PASS_REJECTED',error=str(ex)))
 else:raise AssertionError('Invalid input accepted: '+name)
def step(a=old,x=frame,**kw):return service.step(a,x,step_id=kw.pop('step_id',240),run_id=args.run,condition_id='errors',**kw)
nonfinite=old.clone();nonfinite[0]=float('nan')
rejected('nonfinite_old_state',lambda:step(a=nonfinite))
rejected('float64_old_state',lambda:step(a=old.double()))
rejected('wrong_old_state_shape',lambda:step(a=old[:65]))
rejected('wrong_frame_shape',lambda:step(x=frame[:65]))
rejected('negative_step_id',lambda:step(step_id=-1))
invalid_frame=frame.clone();invalid_frame[0]=1.01
rejected('frame_outside_0_1',lambda:step(x=invalid_frame))
rejected('wrong_device_meta',lambda:step(a=torch.empty(45669,device='meta',dtype=torch.float32)))
for name,h in [('swapped_H_local_order',list(reversed(service.h_indices.tolist()))),('duplicate_H_id',[int(service.h_indices[0])]*2),
               ('out_of_range_H',[45669])]:
 invalid=json.loads((BUNDLE/'candidates/B_T5c/candidate_manifest.json').read_text());invalid['h_global_node_indices']=h
 path=OUT/(name+'.json');dump(path,invalid)
 rejected(name,lambda path=path:RStepService(BUNDLE/'expanded_parameters.npz',BUNDLE/'identity_manifest.json',path,device=args.device))
wrong=json.loads((BUNDLE/'candidates/B_T5c/candidate_manifest.json').read_text());wrong['checkpoint_sha256']='0'*64
path=OUT/'wrong_checkpoint.json';dump(path,wrong)
rejected('wrong_checkpoint_identity',lambda:RStepService(BUNDLE/'expanded_parameters.npz',BUNDLE/'identity_manifest.json',path,device=args.device))
assert torch.equal(old,tensor(key_old[240])) and torch.equal(service.step(old,frame,step_id=240,run_id=args.run,condition_id='0').activity,baseline.activity)
dump(OUT/'error_semantics_acceptance.json',dict(status='PASS_SERVICE_STATELESS_NO_MUTATION',cases=bad,
  error_atomicity_scope='Service returns no candidate on error and holds no committed state; joint H/R barrier is owned by B and NOT TESTED here'))
oracle.assert_weights_unchanged()
kept=service.original_edge_ids
packed=params['source_global'][kept].astype(np.int64)*45669+params['target_global'][kept]
edge_proof=dict(original_R_edge_count=len(kept),partition_counts=service.partition_counts,
 negative_weight_R_edges=int((params['effective_weight'][kept]<0).sum()),
 self_edges_R=int((params['source_global'][kept]==params['target_global'][kept]).sum()),
 repeated_source_target_R_edges=int(len(packed)-len(np.unique(packed))),original_edge_order_maintained=bool(np.all(np.diff(kept)>0)),
 B_export_edge_partition_verified=True,edges_removed_or_merged=0)
dump(OUT/'edge_preservation.json',edge_proof)
summary=dict(implementation_sha256={name:file_sha(BASE/name) for name in ['r_only.py','full_oracle.py','validate_r_only.py']},status='PASS_R_ONLY_SERVICE_SINGLE_STEP',evidence_level='SOFTWARE_ORIGINAL_FULL_VS_INDEPENDENT_R_ONLY',
 scope='4x485 independent R steps using fresh Full old states; NOT H replacement closed loop',device=args.device,
 command=[sys.executable,*sys.argv],python=sys.version,torch=torch.__version__,os=platform.platform(),
 n_h=len(service.h_indices),n_r=service.n_r,n_r_edges=service.n_r_edges,steps=1940,dt_s=.005,
 checkpoint_sha256=ident['checkpoint_sha256'],source_commit=ident['source_commit'],
 expanded_parameters_sha256=ident['expanded_parameters_sha256'],initial_state_sha256=ident['initial_state_sha256'],
 stimulus_sha256=stim_manifest['stimulus_sha256'],candidate_sha256=service.candidate_sha256,
 conditions_original_samples=stim_manifest['original_samples'],reset_each_condition=True,canonical_initial_state_device='cpu',
 max_abs=max(x['max_abs'] for x in errors),max_step_mae=max(x['mae'] for x in errors),max_step_rmse=max(x['rmse'] for x in errors),
 all_steps_allclose=all(x['allclose'] for x in errors),all_steps_bitwise=all(x['bitwise'] for x in errors),
 atol=1e-5,rtol=1e-5,full_activity_raw_stream_sha256=full_sha.hexdigest(),r_activity_raw_stream_sha256=r_sha.hexdigest(),
 timed_full_s=full_s,timed_r_only_s=r_s,total_elapsed_s=elapsed,timing='synchronized update calls including input validation/mapping; no rendering',
 peak_cuda_allocated_bytes=torch.cuda.max_memory_allocated() if args.device=='cuda' else None,
 peak_cuda_reserved_bytes=torch.cuda.max_memory_reserved() if args.device=='cuda' else None,
 weight_state_exact_after=True,production_path_proof=production_proof['status'],
 h_perturbation_status='PASS',generic_candidates_status='PASS',error_semantics_status='PASS',
 closed_loop_status='NOT_TESTED_REQUIRES_INDEPENDENT_H_BARRIER',board_evidence='NONE',
 limitations=['no B H-service integration or fault/atomic-merge tests','H candidate and boundary/numeric/physical profiles not frozen',
 'single-step R replay uses fresh original Full old states solely for comparison, not production input',
 'long-horizon R-only/H-independent cumulative errors are untested'])
dump(OUT/'acceptance.json',summary)
if args.record_full:full_out.flush();r_out.flush()
dump(OUT/'artifact_manifest.json',dict(files=[dict(path=str(f.relative_to(OUT)),bytes=f.stat().st_size,sha256=file_sha(f))
 for f in sorted(OUT.iterdir()) if f.is_file() and f.name!='artifact_manifest.json']))
print('R_ONLY_ACCEPTANCE',json.dumps(summary),flush=True)
