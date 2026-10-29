"""Read-only graph/parameter audit. Does not implement or replace any circuit."""
from pathlib import Path
import os, json, hashlib, subprocess, sys, math

WORK = Path(__file__).resolve().parent
BASE = Path('/mnt/c/Users/hzy72/Documents/ChatGPT/fly')
FPGA = BASE.parent / 'fpga'
os.environ.update(FLYVIS_ROOT_DIR='/opt/flyvis-data', CUDA_VISIBLE_DEVICES='-1',
                  MPLBACKEND='Agg', MPLCONFIGDIR=str(WORK/'runtime/matplotlib'),
                  NUMBA_CACHE_DIR=str(WORK/'runtime/numba'), PYTHONDONTWRITEBYTECODE='1',
                  TIMEZONE='Asia/Shanghai')
sys.dont_write_bytecode = True
import numpy as np
import pandas as pd
import torch
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components
import flyvis
from flyvis import NetworkView

torch.set_num_threads(1)
torch.set_num_interop_threads(1)
torch.use_deterministic_algorithms(True)
OUT = WORK/'artifacts'
if (OUT/'summary.json').exists():
    raise SystemExit('Existing complete results preserved. Use a new round directory.')
OUT.mkdir(exist_ok=True)

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024), b''): h.update(block)
    return h.hexdigest()

def dump(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding='utf-8')

source_rel=['network/dynamics.py','network/network.py','network/initialization.py',
            'network/stimulus.py','utils/tensor_utils.py']
source_root=BASE/'upstream/flyvis/flyvis'
source_before={r:sha(source_root/r) for r in source_rel}
checkpoint=Path('/opt/flyvis-data/results/flow/0000/000/chkpts/chkpt_00000')
checkpoint_before=sha(checkpoint)
assert checkpoint_before=='d0e42857e738d0315897c2d50fde9eb3fb1a3fb1f071d55dfc13d53d72bccc3f'
expected=torch.load(checkpoint,map_location='cpu',weights_only=False)['network']
view=NetworkView(checkpoint.parents[1])
model=view.network(checkpoint='best',lazy=True)
model.recover()
net=model.network
assert all(torch.equal(v.detach().cpu(),expected[k]) for k,v in net.state_dict().items())
net.clamp()
assert all(torch.equal(v.detach().cpu(),expected[k]) for k,v in net.state_dict().items())
params=net._param_api()
conn=net.connectome
N,E=net.n_nodes,net.n_edges
assert (N,E)==(45669,1513231)
src=conn.edges.source_index[:].astype(np.int64)
dst=conn.edges.target_index[:].astype(np.int64)
types=conn.nodes.type[:].astype(str)
u,v=conn.nodes.u[:],conn.nodes.v[:]
bias=params.nodes.bias.detach().cpu().numpy().copy()
tau=params.nodes.time_const.detach().cpu().numpy().copy()
ep={key:params.edges[key].detach().cpu().numpy().copy()
    for key in ['sign','syn_count','syn_strength','weight']}
assert np.array_equal(ep['weight'], (ep['sign']*ep['syn_count'])*ep['syn_strength'])
assert all(np.isfinite(x).all() for x in [bias,tau,*ep.values()])
nodes=pd.DataFrame(dict(global_node_id=np.arange(N),cell_type=types,u=u,v=v,
                        bias=bias,time_const_s=tau))
definitions=[('A_T4c', ['T4c']), ('B_T5c',['T5c']),
             ('C_T4T5_all_centers',[f'T{n}{s}' for n in [4,5] for s in 'abcd'])]
records=[]
for name, output_types in definitions:
    seeds=np.flatnonzero(np.isin(types,output_types)&(u==0)&(v==0))
    assert len(seeds)==len(output_types)
    inside=np.zeros(N,dtype=bool)
    inside[seeds]=True
    inside[np.unique(src[np.isin(dst,seeds)])]=True
    local=np.flatnonzero(inside)
    inv=np.full(N,-1,dtype=np.int64);inv[local]=np.arange(len(local))
    masks={'internal':inside[src]&inside[dst],
           'incoming':~inside[src]&inside[dst],
           'outgoing':inside[src]&~inside[dst]}
    assert not np.any(masks['internal']&masks['incoming'])
    assert sum(int(m.sum()) for m in masks.values())==int((inside[src]|inside[dst]).sum())
    ins=np.unique(src[masks['incoming']]);outs=np.unique(dst[masks['outgoing']])
    in_targets=np.unique(dst[masks['incoming']]);out_sources=np.unique(src[masks['outgoing']])
    si=src[masks['internal']];ti=dst[masks['internal']]
    graph=csr_matrix((np.ones(len(si)),(inv[si],inv[ti])),shape=(len(local),len(local)))
    _,labels=connected_components(graph,directed=True,connection='strong')
    sizes=np.bincount(labels)
    counts={k:int(m.sum()) for k,m in masks.items()}
    n=len(local);ei=counts['internal']
    # Logical storage lower bound, not synthesis: uint16+uint16+fp32 per edge;
    # old/new activity, accumulator, bias, reciprocal tau => five fp32 node arrays.
    storage=8*ei+20*n
    table=nodes.iloc[local].copy();table.insert(0,'local_node_id',np.arange(n))
    table['raw_initial_bias']=bias[local]
    table['inv_max_tau_dt_fp32']=np.float32(1)/np.maximum(tau[local],np.float32(.005))
    folder=OUT/name;folder.mkdir(exist_ok=True)
    table.to_csv(folder/'nodes.csv',index=False)
    nodes.iloc[ins].to_csv(folder/'boundary_source_nodes.csv',index=False)
    nodes.iloc[outs].to_csv(folder/'boundary_target_nodes.csv',index=False)
    arrays={'global_node_id':local,'seed_global_node_id':seeds,
            'seed_local_node_id':inv[seeds], 'bias':bias[local],'time_const_s':tau[local],
            'raw_initial_bias':bias[local],
            'inv_max_tau_dt':table.inv_max_tau_dt_fp32.to_numpy(dtype=np.float32),
            'incoming_source_global_node_id':ins,'outgoing_target_global_node_id':outs,
            'incoming_target_local_node_id':inv[in_targets],
            'outgoing_source_local_node_id':inv[out_sources]}
    for kind,mask in masks.items():
        ids=np.flatnonzero(mask)
        edge=pd.DataFrame(dict(global_edge_id=ids,source_global_node_id=src[mask],
            target_global_node_id=dst[mask],source_local_node_id=inv[src[mask]],
            target_local_node_id=inv[dst[mask]],**{k:x[mask] for k,x in ep.items()}))
        # Edges retain ORIGINAL GLOBAL ORDER. Split reductions can change fp32 rounding.
        edge.to_csv(folder/f'{kind}_edges.csv',index=False)
        for key in ['source_index','target_index','weight','sign','syn_count','syn_strength']:
            val={'source_index':src,'target_index':dst,**ep}[key]
            arrays[f'{kind}_{key}']=val[mask]
        arrays[f'{kind}_edge_id']=ids
        arrays[f'{kind}_source_local']=inv[src[mask]]
        arrays[f'{kind}_target_local']=inv[dst[mask]]
    np.savez(folder/'static_boundary.npz',**arrays)
    for k,mask in masks.items():
        edges=pd.DataFrame(dict(source_type=types[src[mask]],target_type=types[dst[mask]],
            weight=ep['weight'][mask]))
        grouped=edges.groupby(['source_type','target_type']).agg(edges=('weight','size'),
             signed_weight_sum=('weight','sum'),abs_weight_sum=('weight',lambda s:float(np.abs(s).sum())))
        grouped.to_csv(folder/f'{k}_type_connections.csv')
    fanin=np.bincount(inv[dst[inside[dst]]],minlength=n)
    rec=dict(candidate=name,seed_types=output_types,seed_global_ids=seeds.tolist(),
        selection='central output seeds UNION ALL actual one-hop presynaptic nodes; no type filter',
        n_nodes=n,internal_edges=ei,incoming_edges=counts['incoming'],outgoing_edges=counts['outgoing'],
        incoming_source_nodes=len(ins),incoming_target_nodes=len(in_targets),
        outgoing_source_nodes=len(out_sources),outgoing_target_nodes=len(outs),
        internal_self_edges=int((si==ti).sum()),nontrivial_scc_count=int((sizes>1).sum()),
        largest_scc_nodes=int(sizes.max()),max_total_fanin=int(fanin.max()),
        cell_type_counts=table.cell_type.value_counts().to_dict(),
        raw_activity_bytes=4*n,double_buffer_activity_bytes=8*n,node_bias_tau_bytes=8*n,
        packed_internal_edges_bytes=8*ei,logical_core_bytes=storage,
        logical_bram36_lower_bound=math.ceil(storage/4608),
        full_boundary_source_input_bytes_per_step=4*len(ins),
        full_state_output_bytes_per_step=4*n,
        aggregated_input_bytes_per_step=4*n,
        aggregated_input_output_bytes_per_step=8*n,
        aggregated_payload_bytes_per_s_at_200Hz=8*n*200,
        minimal_aggregated_input_bytes_per_step=4*len(in_targets),
        minimal_output_bytes_per_step=4*len(out_sources),
        ps_cross_boundary_edge_terms_per_step=counts['incoming']+counts['outgoing'],
        total_tau_range_s=[float(tau[local].min()),float(tau[local].max())],
        total_bias_range=[float(bias[local].min()),float(bias[local].max())],
        internal_weight_range=[float(ep['weight'][masks['internal']].min()),
                               float(ep['weight'][masks['internal']].max())],
        external_visual_input_nodes=int(np.isin(types[local],['R'+str(i) for i in range(1,9)]).sum()),
        runtime_state_export='Existing official T4c/T5c traces only; C runtime traces NOT_RUN',
        evidence_level='actual source/topology/expanded checkpoint parameter audit; no replacement simulation')
    records.append(rec)
    dump(folder/'metrics.json',rec)
    print('CANDIDATE',json.dumps({k:rec[k] for k in ['candidate','n_nodes','internal_edges',
          'incoming_edges','outgoing_edges','incoming_source_nodes','outgoing_source_nodes',
          'logical_core_bytes','largest_scc_nodes']}),flush=True)

# Independently cross-check existing definitions against newly read full-network data.
assert tuple(records[0][k] for k in ['n_nodes','internal_edges','incoming_edges','outgoing_edges'])==(92,1437,7770,12768)
assert tuple(records[1][k] for k in ['n_nodes','internal_edges','incoming_edges','outgoing_edges'])==(67,970,5567,8159)
assert all(torch.equal(v.detach().cpu(),expected[k]) for k,v in net.state_dict().items())
assert checkpoint_before==sha(checkpoint)
assert source_before=={r:sha(source_root/r) for r in source_rel}
installed_root=Path(flyvis.__file__).parent
source_match={r:sha(installed_root/r)==source_before[r] for r in source_rel}
assert all(source_match.values()), source_match
parameters={name:dict(raw_shape=list(p.raw_values.shape),
                 semantic_shape=list(p.semantic_values.shape),
                 readers={route:list(index.shape) for route,index in p.readers.items()},
                 raw_dtype=str(p.raw_values.dtype))
            for name,p in {**net.node_params,**net.edge_params}.items()}
summary=dict(date='2026-10-10',source_commit=subprocess.check_output(
    ['git','-C',str(BASE/'upstream/flyvis'),'rev-parse','HEAD'],text=True).strip(),
    source_sha256=source_before,installed_sources_match=source_match,
    checkpoint_sha256=checkpoint_before,checkpoint_unchanged=True,in_memory_params_exact=True,
    connectome_sha256=sha(source_root/'connectome/fib25-fib19_v2.2.json'),
    full_network=dict(nodes=N,edges=E),python=sys.version,torch=torch.__version__,flyvis=flyvis.__version__,
    shared_parameters=parameters,candidates=records,dt_s=.005,
    final_hardware_selection='PENDING_USER_DECISION',
    limits=['No circuit updater implemented','No target-disabled/writeback full-network test',
            'No quantization, RTL, synthesis, bitstream or board test',
            'Storage is a logical lower bound; port/packing/operator/interface resources excluded'])
dump(OUT/'summary.json',summary)
files=[p for p in OUT.rglob('*') if p.is_file() and p.name!='manifest.json']
dump(OUT/'manifest.json',[dict(path=str(p.relative_to(OUT)),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(files)])
print('DONE',OUT,flush=True)
