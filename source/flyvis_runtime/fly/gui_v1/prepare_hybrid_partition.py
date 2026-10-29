"""Static H5768/R39901 manifest only; no neural update or device imports."""
import hashlib
import numpy as np
from hybrid_a3 import A3Contract
from live_protocol import HERE,Registry,load,write,require


def digest(a):
    # Exact original r_only.array_sha convention (metadata + original bytes).
    return hashlib.sha256(str(a.dtype).encode()+str(a.shape).encode()+a.tobytes()).hexdigest()


def prepare(output):
    c=A3Contract();reg=Registry();identity=load(reg.path_for('identity'))
    require(np.all(np.diff(c.h)>0),'R_ONLY_REQUIRES_ASCENDING_H')
    with np.load(reg.path_for('parameters'),allow_pickle=False) as z:
        src=z['source_global'];dst=z['target_global'];order=z['original_edge_index']
    require(src.dtype==dst.dtype==order.dtype==np.int64 and src.shape==dst.shape==order.shape==(identity['n_edges'],),'ORIGINAL_GRAPH_INDEX_SCHEMA')
    require(np.array_equal(order,np.arange(identity['n_edges'])),'ORIGINAL_EDGE_ORDER')
    mask=np.zeros(identity['n_nodes'],dtype=bool);mask[c.h]=True;sh=mask[src];th=mask[dst]
    edges={k:np.flatnonzero(v).astype(np.int64) for k,v in {'HH':sh&th,'RH':~sh&th,'HR':sh&~th,'RR':~sh&~th}.items()}
    require(sum(len(v) for v in edges.values())==1513231,'ALL_EDGES_PRESERVED')
    m={k:identity[k] for k in ('checkpoint_sha256','source_commit','expanded_parameters_sha256','nodes_full_sha256','n_nodes','n_edges','dt_s','dynamics_type','activation_type')}
    m.update(schema='flyvis-r-only-candidate/v1',candidate_id='A3R1_H5768_STATIC_PREPARATION',status='STATIC_PARTITION_ONLY_GPU_NOT_RUN',
        h_global_node_indices=c.h.tolist(),h_indices_digest=digest(c.h),r_indices_digest=digest(c.r),
        r_edge_indices_digest=digest(np.flatnonzero(~th).astype(np.int64)),partition_counts={k:len(v) for k,v in edges.items()},
        partition_ids_digests={k:digest(v) for k,v in edges.items()},A3_mapping_sha256=c.mapping_sha,
        source_A3_fixture=str(c.paths['a3_fixture']),source_A3_fixture_sha256=c.registry['pins']['a3_fixture']['sha256'],
        numeric_profile='original_R_float32; H_A3_Q24_separate_profile',GPU_validation='NOT_RUN',PL_execution=False)
    write(output,m);return {k:m[k] for k in ('status','h_indices_digest','r_indices_digest','partition_counts','GPU_validation')}

if __name__=='__main__':print(prepare(HERE/'evidence/hybrid_prepare_20261012/R5768_candidate_manifest.json'))
