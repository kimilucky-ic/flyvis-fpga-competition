"""Independent static-export checks and existing-reference integrity verification."""
from pathlib import Path
import hashlib,json,csv,sys
import numpy as np

HERE=Path(__file__).resolve().parent
FPGA=HERE.parents[1]
FLY=FPGA.parent/'fly'
OUT=HERE/'artifacts'
summary=json.loads((OUT/'summary.json').read_text(encoding='utf-8'))

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x): p.write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf-8')

reference_checks=[]
for root in [FLY/'artifacts/golden_reference_v1',
             FLY/'artifacts/moving_edge_minimal_cpu_v1',
             FPGA/'flyvis-gpu-validation/artifacts',
             FPGA/'flyvis-visual-experiments/artifacts/golden_reference_v2']:
    manifest=root/'manifest.json'
    if not manifest.exists():
        continue
    entries=json.loads(manifest.read_text(encoding='utf-8'))
    assert isinstance(entries,list),manifest
    failures=[]
    for e in entries:
        path=root/Path(e['path'].replace('\\','/'))
        if not path.exists() or sha(path)!=e['sha256']: failures.append(e['path'])
    reference_checks.append(dict(manifest=str(manifest),files=len(entries),failures=failures))
assert not any(e['failures'] for e in reference_checks)

detail=[]
for rec in summary['candidates']:
    root=OUT/rec['candidate']
    z=np.load(root/'static_boundary.npz',allow_pickle=False)
    gids=z['global_node_id']
    assert np.all(np.diff(gids)>0)
    assert np.array_equal(gids[z['seed_local_node_id']],z['seed_global_node_id'])
    for kind in ['internal','incoming','outgoing']:
        src,dst=z[kind+'_source_index'],z[kind+'_target_index']
        sl,tl=z[kind+'_source_local'],z[kind+'_target_local']
        assert np.all(np.diff(z[kind+'_edge_id'])>0)
        assert np.array_equal(z[kind+'_weight'],
            (z[kind+'_sign']*z[kind+'_syn_count'])*z[kind+'_syn_strength'])
        if kind!='incoming': assert np.array_equal(gids[sl],src)
        else: assert (sl==-1).all()
        if kind!='outgoing': assert np.array_equal(gids[tl],dst)
        else: assert (tl==-1).all()
    assert np.array_equal(z['raw_initial_bias'],z['bias'])
    # No simulation occurred: raw bias must not be mislabelled as grey-adapted state.
    assert np.array_equal(z['inv_max_tau_dt'],np.float32(1)/np.maximum(z['time_const_s'],np.float32(.005)))
    seedmask=np.isin(z['internal_target_index'],z['seed_global_node_id'])
    rows=list(csv.DictReader((root/'internal_edges.csv').open(encoding='utf-8')))
    type_by_global={int(r['global_node_id']):r['cell_type'] for r in csv.DictReader((root/'nodes.csv').open(encoding='utf-8'))}
    selected={}
    for row in rows:
        t=int(row['target_global_node_id'])
        if t not in z['seed_global_node_id']: continue
        key=(type_by_global[int(row['source_global_node_id'])],type_by_global[t])
        val=selected.setdefault(key,dict(edges=0,weights=[]))
        val['edges']+=1;val['weights'].append(float(row['weight']))
    direct=[]
    for (s,t),v in sorted(selected.items()):
        direct.append(dict(source_type=s,target_type=t,edges=v['edges'],
                     signed_weight_sum=float(np.sum(v['weights'],dtype=np.float64)),
                     abs_weight_sum=float(np.sum(np.abs(v['weights']),dtype=np.float64))))
    with (root/'seed_input_connections.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(direct[0]));w.writeheader();w.writerows(direct)
    detail.append(dict(candidate=rec['candidate'],all_static_checks_pass=True,
                raw_initial_state='bias only; NOT the grey-adapted runtime state',
                zero_weight_internal_edges=int((z['internal_weight']==0).sum()),
                zero_weight_incoming_edges=int((z['incoming_weight']==0).sum()),
                zero_weight_outgoing_edges=int((z['outgoing_weight']==0).sum()),
                direct_seed_connections=direct,
                all_incident_tables_logical_bytes=8*sum(rec[k] for k in ['internal_edges','incoming_edges','outgoing_edges']),
                serial_edge_scan_illustration=dict(clock_hz=100000000,cycles_per_internal_edge=8,
                    edge_scan_ms=8*rec['internal_edges']/100000,neuron_update_and_io_excluded=True)))

# Copy provenance-bearing summaries, not trajectories or upstream implementations.
directions=list(csv.DictReader((FPGA/'flyvis-visual-experiments/artifacts/analysis/direction_metrics_T4_T5.csv').open(encoding='utf-8')))
dump(OUT/'direction_evidence.json',dict(source=str(FPGA/'flyvis-visual-experiments/artifacts/analysis/direction_metrics_T4_T5.csv'),
     source_sha256=sha(FPGA/'flyvis-visual-experiments/artifacts/analysis/direction_metrics_T4_T5.csv'),
     scope='Existing software measurement, one checkpoint, speed=19; not remeasured this round',rows=directions))
dump(OUT/'verification.json',dict(static_checks=detail,reference_integrity=reference_checks,
     validation_scope='Read-only static graph and parameter audit, no independent dynamics implementation'))
with (OUT/'candidate_comparison.csv').open('w',newline='',encoding='utf-8') as f:
    keys=['candidate','n_nodes','internal_edges','incoming_edges','outgoing_edges','incoming_source_nodes',
          'incoming_target_nodes','outgoing_source_nodes','outgoing_target_nodes','largest_scc_nodes',
          'logical_core_bytes','logical_bram36_lower_bound','aggregated_input_output_bytes_per_step',
          'aggregated_payload_bytes_per_s_at_200Hz']
    w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows({k:r[k] for k in keys} for r in summary['candidates'])
dump(OUT/'manifest.json',[dict(path=str(p.relative_to(OUT)),bytes=p.stat().st_size,sha256=sha(p))
     for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='manifest.json'])
print(json.dumps(dict(static_candidates_pass=len(detail),reference_integrity=reference_checks),ensure_ascii=False))
