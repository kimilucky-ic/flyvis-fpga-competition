"""Isolated continuation: unchanged original FlyVis, existing interpreters only."""
from __future__ import annotations
import argparse, gc, hashlib, json, os, platform, resource, shutil, subprocess, sys, time
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('stage', choices=['cross_cpu','cross_gpu','minimal','flash','bar','bar_replay','decoder','boundary'])
p.add_argument('--device', choices=['cpu','cuda'], default='cuda')
p.add_argument('--repeat', type=int, default=1)
args = p.parse_args()
WORK = Path(__file__).resolve().parents[1]
BASE = Path('/mnt/c/Users/hzy72/Documents/ChatGPT/fly')
PRIOR = WORK.parent / 'flyvis-gpu-validation/artifacts/moving_edge_full_cuda_t1_r1'
ROOT = Path('/opt/flyvis-visual-experiments-data')
DEST = WORK / 'artifacts' / f'{args.stage}_{args.device}_r{args.repeat}'
DEST.mkdir(parents=True, exist_ok=True)
if (DEST/'result.json').exists():
    raise SystemExit(f'Existing result preserved: {DEST}. Choose a new --repeat for a fresh process replay.')
ROOT.mkdir(parents=True, exist_ok=True)
MODEL = ROOT / 'results/flow/0000/000'
if not MODEL.exists():
    shutil.copytree('/opt/flyvis-gpu-data/results/flow/0000/000', MODEL,
                    ignore=shutil.ignore_patterns('__cache__'))
os.environ.update(CUDA_VISIBLE_DEVICES='0' if args.device == 'cuda' else '-1',
                  FLYVIS_ROOT_DIR=str(ROOT), MPLBACKEND='Agg',
                  MPLCONFIGDIR=str(ROOT/'matplotlib'), NUMBA_CACHE_DIR=str(ROOT/'numba'),
                  TIMEZONE='Asia/Shanghai', CUBLAS_WORKSPACE_CONFIG=':4096:8')
import numpy as np
import pandas as pd
import torch
torch.set_num_threads(1)
torch.set_num_interop_threads(1)
torch.manual_seed(0)
np.random.seed(0)
torch.use_deterministic_algorithms(True)
torch.backends.cuda.matmul.allow_tf32 = False
torch.backends.cudnn.allow_tf32 = False
import flyvis
from flyvis import NetworkView
from flyvis.analysis.stimulus_responses import compute_responses
from flyvis.datasets.datasets import StimulusDataset
from flyvis.datasets.moving_bar import MovingBar
from flyvis.utils.nn_utils import simulation

ATOL = RTOL = 1e-5  # Predeclared before this continuation's first simulation.
assert flyvis.device.type == args.device
def dump(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, default=str), encoding='utf-8')
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()
def sync():
    if args.device=='cuda': torch.cuda.synchronize()
def timed(fn):
    sync()
    if args.device=='cuda': torch.cuda.reset_peak_memory_stats()
    start=time.perf_counter(); value=fn(); sync()
    stats={'elapsed_s':time.perf_counter()-start,'process_host_max_rss_MiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024}
    if args.device=='cuda': stats.update(peak_allocated_MiB=torch.cuda.max_memory_allocated()/2**20,
                                      peak_reserved_MiB=torch.cuda.max_memory_reserved()/2**20)
    return value,stats
def compare(a,b):
    assert a.shape==b.shape,(a.shape,b.shape)
    delta=a.astype(np.float64)-b.astype(np.float64)
    denom=np.maximum(np.abs(b.astype(np.float64)),1e-12)
    return dict(shape=list(a.shape), bitwise_equal=bool(np.array_equal(a,b)),
                max_abs_error=float(np.abs(delta).max()),rmse=float(np.sqrt(np.mean(delta**2))),
                max_relative_error_floor_1e12=float((np.abs(delta)/denom).max()),
                relative_l2_error=float(np.linalg.norm(delta.ravel())/max(np.linalg.norm(b.astype(float).ravel()),1e-12)),
                atol=ATOL,rtol=RTOL,allclose=bool(np.allclose(a,b,atol=ATOL,rtol=RTOL)))
record=dict(stage=args.stage,device=args.device,repeat=args.repeat,python=sys.version,
            torch=torch.__version__,cuda=torch.version.cuda,flyvis=flyvis.__version__,
            os=platform.platform(),threads=1,deterministic=True,tf32=False,
            environment_reinstalled=False,command=[sys.executable,*sys.argv],
            root=str(ROOT),response_cache_bypassed=True,acceptance={'atol':ATOL,'rtol':RTOL})
record['source_commit']=subprocess.check_output(['git','-C',str(BASE/'upstream/flyvis'),'rev-parse','HEAD'],text=True).strip()
def fail(kind,value,tb):
    dump(DEST/'failure.json',{**record,'status':'FAIL','error':str(value),'error_type':kind.__name__})
    sys.__excepthook__(kind,value,tb)
sys.excepthook=fail
print('START',json.dumps(record),flush=True)
view=NetworkView(MODEL)
checkpoint=Path(view.get_checkpoint('best'))
checkpoint_data=torch.load(checkpoint,map_location='cpu',weights_only=False)
expected=checkpoint_data['network']
record['checkpoint_sha256']=sha(checkpoint)
assert record['checkpoint_sha256']=='d0e42857e738d0315897c2d50fde9eb3fb1a3fb1f071d55dfc13d53d72bccc3f'
def load():
    m=view.network(checkpoint='best',lazy=True);m.recover();return m
model,record['model_load']=timed(load)
net=model.network
def weights_exact():
    return all(torch.equal(net.state_dict()[k].detach().cpu(),v) for k,v in expected.items())
assert weights_exact()
record.update(neurons=net.n_nodes,edges=net.n_edges,weights_exact_before=True)
ct=net.connectome.unique_cell_types[:].astype(str)
central=net.connectome.central_cells_index[:]
targets=[f'T{n}{s}' for n in [4,5] for s in 'abcd']

class SavedEdge(StimulusDataset):
    def init__(self,dt=.005,t_pre=1.0):
        self.dt,self.t_pre=dt,t_pre
        self.data=np.load(PRIOR/'stimulus.npy')[:,:,0]
        self.arg_df=pd.read_csv(PRIOR/'samples.csv',index_col='sample')
        self.arg_df['width']=80
        self.arg_df['t_stim']=21*2.25/(19*5.8)
    def __len__(self): return len(self.data)
    def __getitem__(self,index):return torch.tensor(self.data[index],dtype=torch.float32,device=flyvis.device)

class SavedCPUReference(StimulusDataset):
    def init__(self,dt=.005,t_pre=1.0):
        self.dt,self.t_pre=dt,t_pre
        self.folder=BASE/('artifacts/moving_edge_minimal_cpu_v1' if args.stage=='minimal' else 'artifacts/golden_reference_v1/flash')
        self.data=np.load(self.folder/'stimulus.npy')[:,:,0]
        self.arg_df=pd.read_csv(self.folder/'samples.csv',index_col='sample')
    def __len__(self):return len(self.data)
    def __getitem__(self,index):return torch.tensor(self.data[index],dtype=torch.float32,device=flyvis.device)

def save_result(folder,result,config):
    folder.mkdir(parents=True,exist_ok=True)
    a=result.responses.values[0];s=result.stimulus.values
    np.save(folder/'activity_central.npy',a);np.save(folder/'stimulus.npy',s)
    np.save(folder/'cell_types.npy',ct)
    t=np.arange(a.shape[1])*config['dt']-config.get('t_pre',1)
    np.save(folder/'time.npy',t)
    columns=[k for k in ['angle','width','intensity','t_stim','speed'] if k in result.coords]
    pd.DataFrame({k:result.coords[k].values for k in columns}).to_csv(folder/'samples.csv',index_label='sample')
    assert np.isfinite(a).all() and np.isfinite(s).all()
    return a,s

if args.stage in ['minimal','flash']:
    result,record['inference']=timed(lambda:compute_responses(model,SavedCPUReference,dict(dt=.005,t_pre=1),batch_size=4,t_pre=1,t_fade_in=0,cell_index='central'))
    a,s=save_result(DEST,result,dict(dt=.005,t_pre=1))
    folder=SavedCPUReference().folder
    record['input_vs_cpu_reference']=compare(s,np.load(folder/'stimulus.npy'))
    record['activity_vs_cpu_reference']=compare(a,np.load(folder/'activity_central.npy'))
    record['status']='PASS' if record['input_vs_cpu_reference']['allclose'] and record['activity_vs_cpu_reference']['allclose'] else 'FAIL'
elif args.stage.startswith('cross_'):
    result,record['inference']=timed(lambda:compute_responses(model,SavedEdge,dict(dt=.005,t_pre=1),
                                                      batch_size=4,t_pre=1,t_fade_in=0,cell_index='central'))
    a,s=save_result(DEST,result,dict(dt=.005,t_pre=1))
    record['activity_vs_prior_gpu']=compare(a,np.load(PRIOR/'activity_central.npy'))
    record['input_vs_prior_gpu']=compare(s,np.load(PRIOR/'stimulus.npy'))
    mini=BASE/'artifacts/moving_edge_minimal_cpu_v1'
    record['minimal_cpu_input']=compare(s[[1,13]],np.load(mini/'stimulus.npy'))
    record['minimal_cpu_activity']=compare(a[[1,13]],np.load(mini/'activity_central.npy'))
    cpu=WORK/'artifacts/cross_cpu_cpu_r1/activity_central.npy'
    if cpu.exists():record['activity_vs_new_cpu']=compare(a,np.load(cpu))
    record['status']='PASS' if all(v['allclose'] for v in record.values() if isinstance(v,dict) and 'allclose' in v) else 'FAIL'
elif args.stage=='bar':
    # Ten explicit conditions, not the full direction/width/speed Cartesian product.
    conditions=[dict(angle=a,intensity=i,width=1,speed=19) for a in [0,180] for i in [0,1]]
    conditions += [dict(angle=0,intensity=i,width=1,speed=4.8) for i in [0,1]]
    conditions += [dict(angle=0,intensity=i,width=4,speed=19) for i in [0,1]]
    conditions += [dict(angle=0,intensity=i,width=1,speed=19) for i in [.25,.75]]
    record['conditions']=[]
    for idx,c in enumerate(conditions):
        folder=DEST/f'condition_{idx:02d}'
        if (folder/'result.json').exists():
            info=json.loads((folder/'result.json').read_text());assert info['status']=='PASS'
            record['conditions'].append(info);continue
        config=dict(widths=[c['width']],angles=[c['angle']],intensities=[c['intensity']],
                    speeds=[c['speed']],height=9,offsets=[-10,11],dt=.005,t_pre=1,t_post=1,
                    post_pad_mode='value')
        gc.collect()
        if args.device=='cuda':torch.cuda.empty_cache()
        dataset,build=timed(lambda:MovingBar(**config))
        gc.collect()
        if args.device=='cuda':torch.cuda.empty_cache()
        result,inference=timed(lambda:compute_responses(model,MovingBar,config,batch_size=1,t_pre=1,t_fade_in=0,cell_index='central'))
        a,s=save_result(folder,result,config)
        info=dict(condition=idx,parameters=c,config=config,stimulus_build=build,inference=inference,
                  activity_shape=list(a.shape),weights_exact=weights_exact(),status='PASS')
        assert info['weights_exact'];dump(folder/'result.json',info)
        record['conditions'].append(info);dump(DEST/'progress.json',record)
        print('BAR_COMPLETE',json.dumps(info),flush=True)
    record['status']='PASS'
elif args.stage=='bar_replay':
    record['conditions']=[]
    for folder in sorted((WORK/'artifacts/bar_cuda_r1').glob('condition_*')):
        class SavedBar(StimulusDataset):
            def init__(self,dt=.005,t_pre=1):
                self.dt,self.t_pre=dt,t_pre
                self.data=np.load(folder/'stimulus.npy')[:,:,0]
                self.arg_df=pd.read_csv(folder/'samples.csv',index_col='sample')
            def __len__(self):return len(self.data)
            def __getitem__(self,index):return torch.tensor(self.data[index],dtype=torch.float32,device=flyvis.device)
        result,stats=timed(lambda:compute_responses(model,SavedBar,dict(dt=.005,t_pre=1),batch_size=1,t_pre=1,t_fade_in=0,cell_index='central'))
        a,s=save_result(DEST/folder.name,result,dict(dt=.005,t_pre=1))
        info=dict(condition=folder.name,inference=stats,activity_vs_gpu=compare(a,np.load(folder/'activity_central.npy')),input_vs_gpu=compare(s,np.load(folder/'stimulus.npy')))
        assert info['activity_vs_gpu']['allclose'] and info['input_vs_gpu']['allclose']
        record['conditions'].append(info);dump(DEST/'progress.json',record)
        print('BAR_REPLAY_COMPLETE',json.dumps(info),flush=True)
    record['status']='PASS'
elif args.stage=='decoder':
    decoder=view.init_decoder(checkpoint='best')['flow']
    # Original simulation() changes only the parent .training flag; eval() is
    # required to recursively disable BatchNorm updates and Dropout for inference.
    decoder.eval()
    record['decoder_module_training_flags']={name:module.training for name,module in decoder.named_modules()}
    record['decoder_class']=type(decoder).__name__
    record['decoder_config']=view.dir.config.task.decoder.flow.to_dict()
    record['output_cell_types']=net.connectome.output_cell_types[:].astype(str).tolist()
    decoder_expected=checkpoint_data['decoder']['flow']
    assert all(torch.equal(decoder.state_dict()[k].detach().cpu(),v) for k,v in decoder_expected.items())
    record['decoder_weights_exact_before']=True
    # Original Conv2dHexSpace.forward calls filter_to_hex(): runtime projection of
    # off-hex kernel taps to zero. Audit this documented operation, without doing it here.
    runtime_expected={k:v.clone() for k,v in decoder_expected.items()}
    projections=[]
    for name,module in decoder.named_modules():
        if getattr(module,'_filter_to_hex',False):
            key=f'{name}.weight'
            runtime_expected[key]=runtime_expected[key]*module.mask.to(dtype=runtime_expected[key].dtype)
            delta=runtime_expected[key]-decoder_expected[key]
            projections.append(dict(parameter=key,changed_taps=int(torch.count_nonzero(delta)),max_abs_change=float(delta.abs().max()),
                                    cause='Original Conv2dHexSpace.forward/filter_to_hex zeroes taps outside hexagonal support'))
    record['official_runtime_projection']=projections
    samples=[0,1,12,13] # Four opposed ON/OFF edges, all frames, original input.
    s=np.load(PRIOR/'stimulus.npy')[samples]
    # Official decoder accepts all original node activities, not just T4/T5 centers.
    a,record['inference']=timed(lambda:net.simulate(torch.tensor(s,device=flyvis.device),dt=.005))
    with simulation(decoder):
        flow,record['decode']=timed(lambda:decoder(a))
    f=flow.detach().cpu().numpy()
    np.save(DEST/'flow.npy',f);np.save(DEST/'stimulus.npy',s)
    np.save(DEST/'activity_central.npy',a[:,:,central].detach().cpu().numpy())
    np.save(DEST/'time.npy',np.arange(s.shape[1])*.005-1)
    pd.read_csv(PRIOR/'samples.csv',index_col='sample').iloc[samples].to_csv(DEST/'samples.csv',index=False)
    np.save(DEST/'cell_types.npy',ct)
    np.save(DEST/'hex_u.npy',net.connectome.nodes.u[:][net.connectome.nodes.type[:].astype(str)=='R1'])
    np.save(DEST/'hex_v.npy',net.connectome.nodes.v[:][net.connectome.nodes.type[:].astype(str)=='R1'])
    record.update(flow_shape=list(f.shape),all_finite=bool(np.isfinite(f).all()),
                  flow_min=float(f.min()),flow_max=float(f.max()),
                  decoder_weights_exact_after=all(torch.equal(decoder.state_dict()[k].detach().cpu(),v) for k,v in decoder_expected.items()),
                  decoder_matches_official_runtime_projection=all(torch.equal(decoder.state_dict()[k].detach().cpu(),v) for k,v in runtime_expected.items()),
                  output_axes=['sample','frame','flow_component','hex_pixel'],
                  limitations=['Synthetic edge inference only; no Sintel endpoint-error evaluation or physical velocity calibration'])
    first=WORK/'artifacts/decoder_cuda_r2/flow.npy'
    # The r1 runs had active child Dropout/BatchNorm and are rejected records.
    # Never use those training-mode outputs as an inference golden reference.
    if args.device=='cuda' and args.repeat>2:record['flow_vs_first_eval_gpu']=compare(f,np.load(first))
    cpu=WORK/'artifacts/decoder_cpu_r2/flow.npy'
    if cpu.exists() and args.device=='cuda':record['flow_vs_cpu']=compare(f,np.load(cpu))
    record['status']='PASS' if record['all_finite'] and record['decoder_matches_official_runtime_projection'] and all(v['allclose'] for v in record.values() if isinstance(v,dict) and 'allclose' in v) else 'FAIL'
elif args.stage=='boundary':
    # Read-only extraction of two candidate circuits from the full-network simulation.
    sources=net.connectome.edges.source_index[:];destinations=net.connectome.edges.target_index[:]
    nodes=net.connectome.nodes
    node_table=pd.DataFrame(dict(node_index=np.arange(net.n_nodes),cell_type=nodes.type[:].astype(str),u=nodes.u[:],v=nodes.v[:]))
    params=net._param_api()
    bias=params.nodes.bias.detach().cpu().numpy();tau=params.nodes.time_const.detach().cpu().numpy()
    weight=params.edges.weight.detach().cpu().numpy()
    node_table['bias']=bias;node_table['time_const_s']=tau
    specs=[]
    for target in ['T4c','T5c']:
        seed=int(node_table.query('cell_type == @target and u == 0 and v == 0').node_index.iloc[0])
        internal=np.union1d([seed],sources[destinations==seed]).astype(int)
        inside=np.zeros(net.n_nodes,dtype=bool);inside[internal]=True
        masks=dict(internal=inside[sources]&inside[destinations],incoming=(~inside[sources])&inside[destinations],outgoing=inside[sources]&(~inside[destinations]))
        incoming=np.unique(sources[masks['incoming']]);outgoing=np.unique(destinations[masks['outgoing']])
        folder=DEST/target;folder.mkdir(parents=True,exist_ok=True)
        node_table.iloc[internal].to_csv(folder/'internal_nodes.csv',index=False)
        node_table.iloc[incoming].to_csv(folder/'incoming_source_nodes.csv',index=False)
        node_table.iloc[outgoing].to_csv(folder/'outgoing_target_nodes.csv',index=False)
        for label,mask in masks.items():
            inds=np.flatnonzero(mask)
            edge_table=pd.DataFrame(dict(edge_index=inds,source_index=sources[mask],target_index=destinations[mask],weight=weight[mask]))
            for key in ['sign','syn_count','syn_strength']:
                edge_table[key]=params.edges[key].detach().cpu().numpy()[mask]
            edge_table.to_csv(folder/f'{label}_edges.csv',index=False)
        specs.append(dict(target=target,seed=seed,internal=internal,incoming=incoming,outgoing=outgoing,folder=folder,masks=masks))
    record['conditions']=[]
    for sample in [0,1,12,13]:
        s=np.load(PRIOR/'stimulus.npy',mmap_mode='r')[sample:sample+1].copy()
        with simulation(net):
            initial=net.steady_state(1,.005,batch_size=1)
            states,stats=timed(lambda:net.simulate(torch.tensor(s,device=flyvis.device),dt=.005,initial_state=initial,as_states=True))
            all_activity=torch.stack([st.nodes.activity[0] for st in states]).detach().cpu().numpy()
            before=np.concatenate([initial.nodes.activity.detach().cpu().numpy(),all_activity[:-1]],axis=0)
            net.stimulus.zero(1,s.shape[1]);net.stimulus.add_input(torch.tensor(s,device=flyvis.device))
            node_input=net.stimulus()[0].detach().cpu().numpy()
        comp=compare(all_activity[:,central],np.load(PRIOR/'activity_central.npy')[sample])
        assert comp['allclose']
        for spec in specs:
            folder=spec['folder']/f'sample_{sample:02d}';folder.mkdir(parents=True,exist_ok=True)
            internal,incoming,outgoing=spec['internal'],spec['incoming'],spec['outgoing']
            np.save(folder/'initial_internal.npy',before[0,internal])
            np.save(folder/'internal_activity_after.npy',all_activity[:,internal])
            np.save(folder/'boundary_incoming_activity_before.npy',before[:,incoming])
            np.save(folder/'boundary_outgoing_target_activity_after.npy',all_activity[:,outgoing])
            np.save(folder/'external_node_input.npy',node_input[:,internal])
            np.save(folder/'stimulus.npy',s)
            np.save(folder/'time.npy',np.arange(s.shape[1])*.005-1)
        record['conditions'].append(dict(sample=sample,inference=stats,central_vs_prior_gpu=comp))
        print('BOUNDARY_COMPLETE',sample,json.dumps(stats),flush=True)
        del states,all_activity,before;gc.collect()
        if args.device=='cuda':torch.cuda.empty_cache()
    record['candidates']=[dict(target=sp['target'],seed=sp['seed'],neurons=len(sp['internal']),incoming_sources=len(sp['incoming']),outgoing_targets=len(sp['outgoing']),
                               edges={k:int(v.sum()) for k,v in sp['masks'].items()}) for sp in specs]
    record['dt_s']=.005
    record['euler_equation']='a_after = a_before + dt/max(tau,dt)*(-a_before+bias+sum(weight*relu(a_source_before))+external_input)'
    record['boundary_semantics']='incoming activity is before the SAME Euler update; internal activity output is after it; edge states are empty in original PPNeuronIGRSynapses'
    record['limitations']=['Extraction from full-network software simulation; candidate does not run independently without incoming boundary data; no FPGA resource or board claim']
    record['status']='PASS'
record['weights_exact_after']=weights_exact();assert record['weights_exact_after']
record['process_host_max_rss_MiB']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024
dump(DEST/'result.json',record)
print('RESULT',json.dumps(record),flush=True)
if record['status']!='PASS':raise SystemExit(2)
