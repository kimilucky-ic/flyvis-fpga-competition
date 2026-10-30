"""Separate streaming graph/record audit and direct official source reconstruction.

Executes only the named pure graph constructor definitions extracted by AST;
does not import/instantiate FlyVis Network or write an upstream data cache.
"""
import ast, collections, csv, dataclasses, json, time
from contextlib import suppress
from pathlib import Path
import numpy as np
import matplotlib.path as mp
import torch
from extract_graph import HERE,ROOT,BUNDLE,TYPES,sha,write_json,first_groups

def groupby(fn,seq):
    d=collections.defaultdict(list)
    for x in seq:d[fn(x)].append(x)
    return dict(d)

def main():
    torch.set_num_threads(1);start=time.perf_counter()
    p=dict(np.load(BUNDLE/'expanded_parameters.npz'));s=p['source_global'];t=p['target_global'];w=p['effective_weight']
    rows=list(csv.DictReader((BUNDLE/'nodes_full.csv').open(encoding='utf-8-sig')))
    nodes=[(r['cell_type'],int(r['u']),int(r['v'])) for r in rows];hs={i for i,r in enumerate(nodes) if r[0] in set(TYPES)}
    ids=dict(np.load(HERE/'data/partition_global_ids.npz'));counts=collections.Counter();nin=collections.Counter();nout=collections.Counter();lasttarget={};gap=None
    positions={k:0 for k in ['HH','RH','HR','RR']};incoming_count=0
    for e,(src,dst) in enumerate(zip(s,t)):
        src=int(src);dst=int(dst);part=('H' if src in hs else 'R')+('H' if dst in hs else 'R')
        assert int(ids[part][positions[part]])==e;positions[part]+=1;counts[part]+=1;nin[dst]+=1;nout[src]+=1
        if dst in hs:
            if dst in lasttarget:gap=min(gap if gap is not None else len(s),incoming_count-lasttarget[dst])
            lasttarget[dst]=incoming_count;incoming_count+=1
    assert np.array_equal(ids['H'],sorted(hs)) and sum(counts.values())==len(s)
    # Independent bit-field decoder; compare each frozen original edge individually.
    records=np.fromfile(HERE/'data/incoming_edges_le64.bin',dtype='<u8')
    dictionary=np.fromfile(HERE/'data/effective_weight_dictionary_f32.bin',dtype='<u4')
    cache=np.r_[ids['H'],ids['R_in_sources']];prev=-1;covered=[]
    for word in records:
        z=int(word);eid=z&((1<<21)-1);si=(z>>21)&32767;ti=(z>>36)&8191;wi=(z>>49)&1023
        assert z>>59==0 and eid>prev and int(cache[si])==int(s[eid]) and int(ids['H'][ti])==int(t[eid]) and int(dictionary[wi])==int(w[eid].view('u4'))
        prev=eid;covered.append(eid)
    assert covered==sorted(ids['HH'].tolist()+ids['RH'].tolist())
    upstream=ROOT.parent/'fly/upstream/flyvis';source=upstream/'flyvis/connectome/connectome.py';specfile=source.with_name('fib25-fib19_v2.2.json')
    spec=json.loads(specfile.read_text());tree=ast.parse(source.read_text(encoding='utf-8'))
    names={'Node','Edge','add_nodes','add_strided_nodes','add_tiled_nodes','add_single_node','add_edges','fill_hull','add_conv_edges'}
    body=[ast.ImportFrom(module='__future__',names=[ast.alias(name='annotations')],level=0)]
    body += [x for x in tree.body if isinstance(x,(ast.FunctionDef,ast.ClassDef)) and x.name in names]
    unit=ast.fix_missing_locations(ast.Module(body=body,type_ignores=[]))
    ns={'__name__':'__main__','dataclass':dataclasses.dataclass,'np':np,'mp':mp,'groupby':groupby,'suppress':suppress}
    exec(compile(unit,str(source),'exec'),ns)
    original_nodes=[];ns['add_nodes'](original_nodes,spec['nodes'],15)
    assert [(x.type,x.u,x.v) for x in original_nodes]==nodes
    class StreamingEdges:
        count=0
        def __len__(self):return self.count
        def append(self,edge):
            k=self.count
            assert edge.id==k and edge.source.id==int(s[k]) and edge.target.id==int(t[k]) and edge.sign==int(p['sign'][k])
            self.count+=1
    streamed=StreamingEdges();ns['add_edges'](streamed,original_nodes,spec['edges'],1)
    assert len(streamed)==len(s)
    # Original parameter group order is first occurrence (pandas sort=False).
    types=list(dict.fromkeys(x[0] for x in nodes));tc=np.array([types.index(x[0]) for x in nodes],dtype='i8')
    uv=np.array([[x[1],x[2]] for x in nodes]);du,dv=(uv[t]-uv[s]).T
    pair=tc[s]*65+tc[t];pf,pi=first_groups(pair)
    keys=(pair*61+du+30)*61+dv+30;kf,ki=first_groups(keys)
    cp=ROOT.parent/'fly/data/results/flow/0000/000/chkpts/chkpt_00000'
    checkpoint=torch.load(cp,map_location='cpu',weights_only=True)['network']
    checks={}
    for name,idx,field in [('nodes_bias',tc,'bias'),('nodes_time_const',tc,'time_const'),('edges_sign',pi,'sign'),('edges_syn_strength',pi,'syn_strength')]:
        q=checkpoint[name].numpy()[idx];checks[name]=bool(np.array_equal(q.view('u4'),p[field].view('u4')));assert checks[name]
    cpu_count=checkpoint['edges_syn_count'].exp().numpy();gpu_count=p['syn_count'][kf]
    cpu_w=(p['sign'][kf]*cpu_count)*p['syn_strength'][kf]
    sourcefiles=[source,specfile,cp,ROOT.parent/'fly/data/results/flow/0000/000/meta.yaml',
        upstream/'flyvis/network/dynamics.py',upstream/'flyvis/network/network.py',upstream/'flyvis/network/initialization.py']
    result=dict(status='PASS',evidence_level='INDEPENDENT_SOFTWARE_AND_SOURCE_RECONSTRUCTION',
      streaming_partition_counts=dict(counts),all_global_ids_exact=True,independent_binary_records_checked=len(records),binary_all_float32_weight_bits_exact=True,
      original_connectome_reconstruction={'nodes_exact':len(original_nodes),'edges_exact_including_global_order':len(streamed),'n_syn_fill':1,'extent':15,'method':'AST extract official pure constructors; transient Edge object per append'},
      maximum_fanin=max(nin[x] for x in hs),maximum_fanout=max(nout[x] for x in hs),minimum_repeat_target_distance_edges=gap,
      checkpoint_parameter_groups={k:list(v.shape) for k,v in checkpoint.items()},checkpoint_expansion_exact=checks,
      cpu_exp_diagnostic={'torch':torch.__version__,'changed_syn_count_dictionary_entries':int(np.count_nonzero(cpu_count.view('u4')!=gpu_count.view('u4'))),
        'max_abs_syn_count_difference':float(np.max(np.abs(cpu_count-gpu_count))),
        'changed_effective_weight_dictionary_entries':int(np.count_nonzero(cpu_w.view('u4')!=w[kf].view('u4'))),
        'max_abs_effective_weight_difference':float(np.max(np.abs(cpu_w-w[kf]))),
        'note':'CPU exp is diagnostic only. Hardware dictionary uses frozen official native GPU expanded float32 bits; no GPU rerun.'},
      source_sha256={str(f):sha(f) for f in sourcefiles},elapsed_seconds=time.perf_counter()-start)
    write_json(HERE/'INDEPENDENT_GRAPH_AUDIT.json',result);print(json.dumps(result,indent=2))

if __name__=='__main__':main()
