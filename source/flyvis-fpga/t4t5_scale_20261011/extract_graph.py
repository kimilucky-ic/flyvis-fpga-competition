"""Read-only complete FlyVis partition / bit-exact dictionary extraction.

Writes only beside this script. No torch inference, CUDA, Vivado or board I/O.
Ordered NPZ edge columns and LE64 records retain every original global edge ID.
"""
from pathlib import Path
import csv, hashlib, json, math, time
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BUNDLE = ROOT/'flyvis-circuit-selection/phase3_ablation_screen_20261010/input_bundle_r2'
TYPES = ['T4a','T4b','T4c','T4d','T5a','T5b','T5c','T5d']

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''): h.update(b)
    return h.hexdigest()

def write_json(path,obj):
    Path(path).write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')

def table(path,header,rows):
    with Path(path).open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow(header);w.writerows(rows)

def summary(a):
    a=np.asarray(a)
    return dict(count=int(a.size),min=float(a.min()),max=float(a.max()),mean=float(a.mean()),
                p50=float(np.percentile(a,50)),p95=float(np.percentile(a,95)),p99=float(np.percentile(a,99)))

def first_groups(keys):
    unique,first,inv=np.unique(keys,return_index=True,return_inverse=True)
    order=np.argsort(first); lookup=np.empty(len(order),dtype=np.int64);lookup[order]=np.arange(len(order))
    return first[order],lookup[inv]

def main():
    start=time.perf_counter(); out=HERE/'data';out.mkdir(exist_ok=True)
    rows=list(csv.DictReader((BUNDLE/'nodes_full.csv').open(encoding='utf-8-sig')))
    typ=np.array([r['cell_type'] for r in rows]);u=np.array([int(r['u']) for r in rows]);v=np.array([int(r['v']) for r in rows])
    n=len(rows); assert [int(r['global_node_index']) for r in rows]==list(range(n))
    types=list(dict.fromkeys(typ.tolist()));tc=np.array([types.index(t) for t in typ],dtype=np.int64)
    p=np.load(BUNDLE/'expanded_parameters.npz');s=p['source_global'];t=p['target_global'];g=p['original_edge_index'];w=p['effective_weight'];m=len(s)
    assert np.array_equal(g,np.arange(m)) and n==45669 and m==1513231
    assert sha(BUNDLE/'expanded_parameters.npz')=='73f397f00c2a27081b16b2a267a58ffa55804c75aebf85277f91218774a725d4'
    assert sha(BUNDLE/'nodes_full.csv')=='c2c367f77083c791c4329d5d3557c0a923ed731d7b47cee35061c49d5b9d79fa'
    assert np.isfinite(w).all() and np.array_equal(((p['sign']*p['syn_count'])*p['syn_strength']).view('u4'),w.view('u4'))
    mask=np.isin(typ,TYPES);h=np.flatnonzero(mask);r=np.flatnonzero(~mask)
    parts={'HH':mask[s]&mask[t],'RH':~mask[s]&mask[t],'HR':mask[s]&~mask[t],'RR':~mask[s]&~mask[t]}
    incoming=np.flatnonzero(mask[t]); rin=np.unique(s[parts['RH']]); rout=np.unique(t[parts['HR']])
    sources=np.concatenate((h,rin)); sl=np.full(n,-1,dtype=np.int64);sl[sources]=np.arange(len(sources));tl=np.full(n,-1,dtype=np.int64);tl[h]=np.arange(len(h))
    np.savez(out/'partition_global_ids.npz',H=h,R=r,R_in_sources=rin,R_out_targets=rout,**{k:g[z] for k,z in parts.items()})
    du=u[t]-u[s];dv=v[t]-v[s]
    assert np.max(np.abs(du))<=30 and np.max(np.abs(dv))<=30
    keys=((tc[s]*65+tc[t])*61+du+30)*61+dv+30
    first,di=first_groups(keys); dw=w[first]
    assert np.array_equal(dw[di].view('u4'),w.view('u4'))
    fi,local_di=first_groups(keys[incoming]);origfirst=incoming[fi];local_w=w[origfirst]
    assert np.array_equal(local_w[local_di].view('u4'),w[incoming].view('u4'))
    assert len(local_w)<=1024 and len(sources)<=32768 and len(h)<=8192 and m<=2097152
    # LE64 [20:0] gid, [35:21] cached source, [48:36] H target,
    # [58:49] dictionary index, [63:59] zero. No edge reordering.
    words=(g[incoming].astype('u8') | (sl[s[incoming]].astype('u8')<<21) |
           (tl[t[incoming]].astype('u8')<<36) | (local_di.astype('u8')<<49))
    words.astype('<u8').tofile(out/'incoming_edges_le64.bin')
    local_w.astype('<f4').tofile(out/'effective_weight_dictionary_f32.bin')
    np.savez(out/'incoming_edges.npz',global_edge_id=g[incoming],source_global=s[incoming],target_global=t[incoming],
             source_cache_index=sl[s[incoming]],target_h_index=tl[t[incoming]],dictionary_index=local_di,
             effective_weight=w[incoming],cache_global_ids=sources,H=h)
    def dictrows(indices):
        for j,e in enumerate(indices):
            yield (j,int(e),typ[s[e]],typ[t[e]],int(du[e]),int(dv[e]),float(w[e]),f'{int(w[e].view("u4")):08x}')
    header=['dictionary_id','first_global_edge_id','source_type','target_type','du','dv','effective_weight_f32','weight_bits_hex']
    table(out/'incoming_weight_dictionary.csv',header,dictrows(origfirst));table(out/'full_weight_dictionary.csv',header,dictrows(first))
    counts={k:int(z.sum()) for k,z in parts.items()}
    indeg=np.bincount(t,minlength=n);outdeg=np.bincount(s,minlength=n)
    in_hh=np.bincount(t[parts['HH']],minlength=n);in_rh=np.bincount(t[parts['RH']],minlength=n)
    out_hr=np.bincount(s[parts['HR']],minlength=n);out_hh=np.bincount(s[parts['HH']],minlength=n)
    bias=p['bias'];tau=p['time_const'];inv=np.float32(1)/np.maximum(tau,np.float32(.005));a0=np.load(BUNDLE/'initial_state_full.npy')
    np.savez(out/'H_parameters.npz',H=h,bias=bias[h],time_const=tau[h],inverse_tau=inv[h],initial_state=a0[h])
    table(out/'H_nodes.csv',['h_index','global_node_id','cell_type','u','v','fanin_HH','fanin_RH','fanin_total','fanout_HH','fanout_HR','fanout_total','bias','inverse_tau','a0'],
          ((j,int(i),typ[i],int(u[i]),int(v[i]),int(in_hh[i]),int(in_rh[i]),int(indeg[i]),int(out_hh[i]),int(out_hr[i]),int(outdeg[i]),float(bias[i]),float(inv[i]),float(a0[i])) for j,i in enumerate(h)))
    table(out/'boundary_nodes.csv',['global_node_id','cell_type','u','v','incoming_boundary','outgoing_boundary','edges_to_H','edges_from_H','fanin_full','fanout_full'],
          ((int(i),typ[i],int(u[i]),int(v[i]),int(i in set_rin),int(i in set_rout),int(to_h[i]),int(from_h[i]),int(indeg[i]),int(outdeg[i]))
           for set_rin,set_rout,to_h,from_h in [(set(rin),set(rout),np.bincount(s[incoming],minlength=n),np.bincount(t[mask[s]],minlength=n))]
           for i in np.union1d(rin,rout)))
    pertype=[]
    for name in TYPES:
        ids=np.flatnonzero(typ==name)
        assert np.unique(bias[ids].view('u4')).size==1 and np.unique(inv[ids].view('u4')).size==1
        pertype.append([name,len(ids),int(ids.min()),int(ids.max()),float(bias[ids[0]]),float(tau[ids[0]]),float(inv[ids[0]])])
    table(out/'H_type_parameters.csv',['cell_type','nodes','first_global_node','last_global_node','bias','tau','inverse_tau'],pertype)
    paircode=tc[s]*65+tc[t];pairs,pairn=np.unique(paircode,return_counts=True)
    table(out/'full_type_pair_counts.csv',['source_type','target_type','partition','edges'],
        ((types[k//65],types[k%65],('H' if types[k//65] in TYPES else 'R')+('H' if types[k%65] in TYPES else 'R'),int(c)) for k,c in zip(pairs,pairn)))
    adj=tl[t[incoming]];change=np.r_[True,adj[1:]!=adj[:-1],True];streak=np.diff(np.flatnonzero(change))
    sums=np.bincount(adj,weights=np.abs(w[incoming].astype('f8')),minlength=len(h))
    pairdup=m-len(np.unique(s*n+t)); incdup=len(incoming)-len(np.unique(s[incoming]*n+t[incoming]))
    minabs=float(np.abs(w[incoming][w[incoming]!=0]).min())
    weightstats={}
    for k,z in parts.items():
        vals=w[z]; weightstats[k]={**summary(vals),'positive':int((vals>0).sum()),'negative':int((vals<0).sum()),'zero':int((vals==0).sum()),'unique_float32_bits':int(np.unique(vals.view('u4')).size)}
    result=dict(evidence_level='SOURCE_DATA_AND_SOFTWARE_EXTRACTION',model='flow/0000/000',parameter_profile='OFFICIAL_NATIVE_GPU_EXPANDED',
       H_definition=TYPES,nodes=n,edges=m,H=len(h),R=len(r),partitions=counts,H_incoming_edges=len(incoming),
       R_in_sources=len(rin),R_out_targets=len(rout),R_boundary_intersection=len(np.intersect1d(rin,rout)),source_cache_nodes=len(sources),
       original_edge_ids_ascending=True,global_pair_duplicates=pairdup,incoming_pair_duplicates=incdup,
       external_input_nodes_in_H=int(np.isin(p['input_node_index'].ravel(),h).sum()),
       weights=weightstats,incoming_weight=summary(w[incoming]),incoming_min_abs_nonzero_weight=minabs,
       incoming_max_abs_to_min_nonzero_ratio=float(np.abs(w[incoming]).max()/minabs),
       H_fanin=summary(indeg[h]),H_fanout=summary(outdeg[h]),R_boundary_source_fanout_to_H=summary(np.bincount(s[incoming],minlength=n)[rin]),
       R_boundary_target_fanin_from_H=summary(np.bincount(t[parts['HR']],minlength=n)[rout]),
       H_bias=summary(bias[h]),H_time_const=summary(tau[h]),H_inverse_tau=summary(inv[h]),H_a0=summary(a0[h]),
       H_per_target_abs_weight_sum=summary(sums),maximum_chemical_bound_if_all_sources_le_64=float(sums.max()*64),
       compression=dict(full_keys=len(first),incoming_keys=len(fi),incoming_unique_weight_bits=int(np.unique(local_w.view('u4')).size),
           key='source_type,target_type,target.u-source.u,target.v-source.v',all_edges_bitwise_reconstruction=True,incoming_bitwise_reconstruction=True,
           incoming_raw_weight_bytes=4*len(incoming),incoming_dictionary_bytes=4*len(fi),dictionary_index_bits=(len(fi)-1).bit_length(),
           incoming_weight_index_and_dictionary_bytes_ceil=math.ceil(len(incoming)*(len(fi)-1).bit_length()/8)+4*len(fi),
           LE64_record_bytes=8,edge_stream_bytes=8*len(incoming)),
       ordering=dict(consecutive_same_target_pairs=int(np.sum(adj[1:]==adj[:-1])),maximum_consecutive_target_run=int(streak.max()),
           note='No reorder by target; same-target hazards measured on original incoming subsequence'),
       input_sha256={str(f.relative_to(ROOT)):sha(f) for f in [BUNDLE/'expanded_parameters.npz',BUNDLE/'nodes_full.csv',BUNDLE/'identity_manifest.json',BUNDLE/'initial_state_full.npy']},
       elapsed_seconds=time.perf_counter()-start)
    write_json(HERE/'T4T5_FULL_GRAPH_STATS.json',result)
    print(json.dumps({k:result[k] for k in ['H','R','partitions','compression','ordering','H_fanin','H_fanout','H_inverse_tau','maximum_chemical_bound_if_all_sources_le_64','elapsed_seconds']},indent=2))

if __name__=='__main__': main()
