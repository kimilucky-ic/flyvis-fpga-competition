"""Export actual original full gray-adapted state; reuse installed environments."""
import argparse, hashlib, json, os, platform, shutil, subprocess, sys, time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--device',choices=['cpu','cuda'],default='cpu');p.add_argument('--run',required=True)
args=p.parse_args()
BASE=Path(__file__).resolve().parent
OUT=BASE/'artifacts'/args.run
if OUT.exists():raise SystemExit('Existing run preserved; choose a new --run')
OUT.mkdir(parents=True)
ROOT=Path('/opt/flyvis-phase2-data')
os.environ.update(CUDA_VISIBLE_DEVICES='0' if args.device=='cuda' else '-1',FLYVIS_ROOT_DIR=str(ROOT),MPLBACKEND='Agg',MPLCONFIGDIR=str(ROOT/'matplotlib'),NUMBA_CACHE_DIR=str(ROOT/'numba'),TIMEZONE='Asia/Shanghai',CUBLAS_WORKSPACE_CONFIG=':4096:8')
import numpy as np,pandas as pd,torch
torch.set_num_threads(1);torch.set_num_interop_threads(1);torch.manual_seed(0)
torch.use_deterministic_algorithms(True);torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
import flyvis
from flyvis import NetworkView
from flyvis.utils.nn_utils import simulation
def sha(f):
 h=hashlib.sha256()
 with Path(f).open('rb') as stream:
  for b in iter(lambda:stream.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def dump(f,v):Path(f).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
def tensor_array(t):return np.ascontiguousarray(t.detach().cpu().numpy())
def array_sha(a):return hashlib.sha256(str(a.dtype).encode()+str(a.shape).encode()+a.tobytes()).hexdigest()
def sync():
 if args.device=='cuda':torch.cuda.synchronize()
view=NetworkView('/opt/flyvis-visual-experiments-data/results/flow/0000/000')
checkpoint=Path(view.get_checkpoint('best'))
expected_sha='d0e42857e738d0315897c2d50fde9eb3fb1a3fb1f071d55dfc13d53d72bccc3f'
assert sha(checkpoint)==expected_sha
expected=torch.load(checkpoint,map_location='cpu',weights_only=False)['network']
wrapper=view.network(checkpoint='best',lazy=True);wrapper.recover();net=wrapper.network;net.eval()
def exact():return all(torch.equal(net.state_dict()[k].detach().cpu(),v) for k,v in expected.items())
assert exact() and not net._state_hooks and net.n_nodes==45669 and net.n_edges==1513231
sync();start=time.perf_counter()
with simulation(net):
 states=net.steady_state(1.0,.005,batch_size=1,value=.5,return_last=False)
sync();elapsed=time.perf_counter()-start
assert len(states)==200 and list(states[-1].nodes.keys())==['activity'] and len(states[-1].edges)==0
initial=tensor_array(states[-1].nodes.activity[0])
assert initial.shape==(45669,) and initial.dtype==np.float32 and np.isfinite(initial).all() and exact()
np.save(OUT/'initial_state_full.npy',initial)
np.save(OUT/'warmup_activity_full.npy',np.stack([tensor_array(st.nodes.activity[0]) for st in states]))
params=net._param_api()
arrays={key:tensor_array(t) for key,t in dict(bias=params.nodes.bias,time_const=params.nodes.time_const,
 effective_weight=params.edges.weight,sign=params.edges.sign,syn_count=params.edges.syn_count,syn_strength=params.edges.syn_strength).items()}
arrays['source_global']=net.connectome.edges.source_index[:].astype(np.int64)
arrays['target_global']=net.connectome.edges.target_index[:].astype(np.int64)
arrays['original_edge_index']=np.arange(net.n_edges,dtype=np.int64)
arrays['input_node_index']=net.stimulus.input_index.astype(np.int64)
assert arrays['input_node_index'].shape==(8,721) and len(np.unique(arrays['input_node_index']))==5768
assert np.array_equal(arrays['effective_weight'],arrays['sign']*arrays['syn_count']*arrays['syn_strength'])
np.savez(OUT/'expanded_parameters.npz',**arrays)
nodes=net.connectome.nodes
pd.DataFrame(dict(global_node_index=np.arange(net.n_nodes),cell_type=nodes.type[:].astype(str),u=nodes.u[:],v=nodes.v[:])).to_csv(OUT/'nodes_full.csv',index=False)
np.save(OUT/'central_node_indices.npy',net.connectome.central_cells_index[:])
np.save(OUT/'cell_types.npy',net.connectome.unique_cell_types[:].astype(str))
np.save(OUT/'input_node_indices.npy',arrays['input_node_index'])
src=BASE.parent/'upstream/flyvis'
commit=subprocess.check_output(['git','-C',str(src),'rev-parse','HEAD'],text=True).strip()
dirty=subprocess.check_output(['git','-C',str(src),'status','--porcelain','--untracked-files=no'],text=True)
assert not dirty
info=dict(status='PASS',scope='actual original 1s full-network gray adaptation; not R-only acceptance',run=args.run,device=args.device,
 python=sys.version,torch=torch.__version__,flyvis=flyvis.__version__,os=platform.platform(),command=[sys.executable,*sys.argv],
 model_id='flow/0000/000',source_commit=commit,checkpoint_sha256=expected_sha,n_nodes=net.n_nodes,n_edges=net.n_edges,
 initialization='original Network.steady_state(1.0,0.005,1,value=0.5,return_last=False); starts at actual checkpoint bias and runs 200 Euler steps',
 initial_state_shape=list(initial.shape),initial_state_dtype=str(initial.dtype),initial_state_sha256=sha(OUT/'initial_state_full.npy'),
 initial_state_max_abs_difference_from_bias=float(np.abs(initial-arrays['bias']).max()),initial_state_is_bias=bool(np.array_equal(initial,arrays['bias'])),
 dt_s=.005,warmup_steps=200,gray_value=.5,warmup_s=elapsed,time_semantics='a0 is after warmup step 199; before dataset step0. Dataset 200 preframes remain.',
 weight_state_exact_before=True,weight_state_exact_after=exact(),dynamic_state_keys=['nodes.activity'],dynamic_edge_state_keys=[],
 expanded_parameter_digests={k:array_sha(v) for k,v in arrays.items()},expanded_parameters_sha256=sha(OUT/'expanded_parameters.npz'),
 nodes_full_sha256=sha(OUT/'nodes_full.csv'),upstream_tracked_source_clean=True,environment_reinstalled=False)
dump(OUT/'identity_manifest.json',info)
dump(OUT/'artifact_manifest.json',dict(files=[dict(path=f.name,bytes=f.stat().st_size,sha256=sha(f)) for f in sorted(OUT.iterdir()) if f.is_file()]))
print('INITIAL_STATE_EXPORTED',json.dumps({k:info[k] for k in ['device','initial_state_sha256','warmup_s','initial_state_max_abs_difference_from_bias']}),flush=True)
