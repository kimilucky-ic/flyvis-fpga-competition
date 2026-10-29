"""CPU official decoder on immutable retained FPGA states. No network simulation."""
import os,sys,json,hashlib,time,zipfile,csv,io,resource
from pathlib import Path
os.environ.update(CUDA_VISIBLE_DEVICES='-1',FLYVIS_ROOT_DIR='/opt/flyvis-visual-experiments-data',MPLBACKEND='Agg',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
import numpy as np
import torch
torch.set_num_threads(1);torch.set_num_interop_threads(1);torch.use_deterministic_algorithms(True)
import flyvis
from flyvis import NetworkView
O=Path(__file__).resolve().parent;R=O.parent
repeat=int(sys.argv[1]);D=O/f'repeat{repeat}';D.mkdir(exist_ok=False)
def dump(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf-8')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()
report=dict(evidence='OFFICIAL_CPU_DECODER_ON_RETAINED_BOARD_STATES',device='cpu',repeat=repeat,torch=torch.__version__,flyvis=flyvis.__version__,command=sys.argv,hardware_actions=0,gpu_runs=0,neural_simulations=0,rounds=[])
def failed(kind,value,tb):
 dump(D/'FAILURE.json',dict(report,status='FAIL',error=str(value)));sys.__excepthook__(kind,value,tb)
sys.excepthook=failed
assert flyvis.device.type=='cpu'
view=NetworkView('/opt/flyvis-visual-experiments-data/results/flow/0000/000')
ck=Path(view.get_checkpoint('best'));provenance=json.loads((R/'ov5640_live_v261_20261026/bundle/original_model_provenance.json').read_text())
assert sha(ck)==provenance['checkpoint_sha256'];report['checkpoint_sha256']=sha(ck)
cp=torch.load(ck,map_location='cpu',weights_only=False)
decoder=view.init_decoder(checkpoint='best')['flow'];decoder.eval()
assert all(not m.training for m in decoder.modules())
expected=cp['decoder']['flow'];assert all(torch.equal(v,expected[k]) for k,v in decoder.state_dict().items())
report['training_flags']={k:m.training for k,m in decoder.named_modules()}
report['decoder_config']=view.dir.config.task.decoder.flow.to_dict();report['output_types']=view.connectome.output_cell_types[:].astype(str).tolist()
source=Path(sys.modules[type(decoder).__module__].__file__);report['decoder_source']=str(source);report['decoder_source_sha256']=sha(source)
assert source.read_bytes()==Path('/mnt/c/Users/hzy72/Documents/ChatGPT/fly/upstream/flyvis/flyvis/task/decoder.py').read_bytes()
nodes=list(csv.DictReader(Path('/mnt/c/Users/hzy72/Documents/ChatGPT/fly/artifacts/golden_reference_v1/structure/nodes.csv').open()))
for key in ['type','u','v']:
 actual=view.connectome.nodes[key][:]
 if key=='type':assert actual.astype(str).tolist()==[r['cell_type'] for r in nodes]
 else:assert actual.tolist()==[int(r[key]) for r in nodes]
report['global_node_order_verified']=True
report['sampling']='Every retained state decoded independently; omitted steps not interpolated.';report['batch_size']=16
Z=Path('/mnt/c/Users/hzy72/Documents/xwechat_files/wxid_khlrd7p7q6j422_642a/temp/RWTemp/2026-10/8eaa68ae41247203942b7fc2b28636e7/交付_原始数据_精简版.zip')
report['archive_sha256']=sha(Z)
with zipfile.ZipFile(Z) as z:
 folders=sorted(n[:-10] for n in z.namelist() if n.endswith('/steps.csv'))
 for folder in folders:
  rows=list(csv.DictReader(io.StringIO(z.read(folder+'/steps.csv').decode('utf-8-sig'))));kept=[r for r in rows if int(r['has_full_state'])]
  raw=z.read(folder+'/states.bin');a=np.frombuffer(raw,'<f4').reshape(len(kept),45669)
  for x,row in zip(a,kept):assert hashlib.sha256(x.tobytes()).hexdigest()==row['state_sha256']
  flows=[];durations=[]
  with torch.no_grad():
   for start in range(0,len(a),16):
    activity=torch.from_numpy(a[start:start+16].copy())[None];before=activity.clone();s=time.perf_counter();out=decoder(activity);durations.append(time.perf_counter()-s)
    assert torch.equal(activity,before);flows.append(out[0].numpy().copy())
   one=decoder(torch.from_numpy(a[:1].copy())[None])[0].numpy()
  flow=np.concatenate(flows);assert flow.shape==(len(a),2,721) and np.isfinite(flow).all()
  assert np.allclose(one,flow[:1],atol=1e-5,rtol=1e-5)
  assert all(torch.equal(v,expected[k]) for k,v in decoder.state_dict().items())
  np.save(D/(folder+'_flow.npy'),flow);np.save(D/(folder+'_time.npy'),[float(r['t_s']) for r in kept])
  item=dict(folder=folder,retained_steps=len(a),all_state_hashes_verified=True,decoder_state_unchanged=True,input_unchanged=True,single_vs_batch_max_abs=float(np.max(abs(one-flow[:1]))),decode_s=sum(durations),mean_cpu_ms_per_state=1000*sum(durations)/len(a),flow_sha256=sha(D/(folder+'_flow.npy')))
  if repeat>1:
   other=np.load(O/'repeat1'/(folder+'_flow.npy'));item['independent_repeat_max_abs']=float(np.max(abs(flow-other)));item['independent_repeat_exact']=bool(np.array_equal(flow,other));assert np.allclose(flow,other,atol=1e-5,rtol=1e-5)
  report['rounds'].append(item);dump(D/'PROGRESS.json',report);print(folder,item['retained_steps'],round(item['mean_cpu_ms_per_state'],3),'ms/state',flush=True)
  del raw,a,flow,flows
report['status']='PASS_DECODER_EXECUTION_NOT_DIRECTION_ACCURACY';report['host_max_rss_mib']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024
dump(D/'RESULT.json',report);print(report['status'],flush=True)
