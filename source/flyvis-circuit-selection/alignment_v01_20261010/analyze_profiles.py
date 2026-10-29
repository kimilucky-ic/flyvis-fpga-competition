"""Static v0.1 alignment only. No model stepping, replacement, RTL or board work."""
from pathlib import Path
import csv, hashlib, json, math
import numpy as np

HERE=Path(__file__).resolve().parent
FPGA=HERE.parents[1]
PRIOR=FPGA/'flyvis-circuit-selection/round1_20261010'
CTRL=FPGA/'docs/flyvis_visual_hybrid'
OUT=HERE/'artifacts'
OUT.mkdir(parents=True,exist_ok=True)
if (OUT/'alignment_summary.json').exists():
    raise SystemExit('Existing complete alignment preserved. Use a fresh directory.')

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()
def dump(path,value):
    path.write_text(json.dumps(value,indent=2,ensure_ascii=False),encoding='utf-8')

inputs=[CTRL/'INTERFACE_CONTRACT.md',CTRL/'SYSTEM_ARCHITECTURE.md',
        CTRL/'PROJECT_GOAL.md',CTRL/'evidence/source_audit_20261010.json',
        PRIOR/'artifacts/summary.json',PRIOR/'artifacts/manifest.json']
before={str(p):sha(p) for p in inputs}
source_audit=json.loads(inputs[3].read_text(encoding='utf-8'))
summary=json.loads(inputs[4].read_text(encoding='utf-8'))
N,E=summary['full_network']['nodes'],summary['full_network']['edges']
assert (N,E)==(45669,1513231)

inventory_failures=[]
for item in source_audit['evidence_inventory']:
    p=Path(item['path'])
    if not p.exists() or sha(p)!=item['sha256']:inventory_failures.append(str(p))
manifest_checks=[]
for item in source_audit['manifests']:
    manifest=Path(item['path'])
    entries=json.loads(manifest.read_text(encoding='utf-8'))
    root=manifest.parent.parent if manifest.name=='validation_manifest.json' else manifest.parent
    failures=[]
    for ent in entries:
        p=root/Path(ent['path'].replace('\\','/'))
        if not p.exists() or sha(p)!=ent['sha256']:failures.append(ent['path'])
    manifest_checks.append(dict(path=str(manifest),entries=len(entries),failures=failures,
          manifest_matches_controller_record=sha(manifest)==item['manifest_sha256']))
assert not inventory_failures,inventory_failures
assert all(not c['failures'] and c['manifest_matches_controller_record'] for c in manifest_checks)

original_nodes=list(csv.DictReader((FPGA.parent/'fly/artifacts/golden_reference_v1/structure/nodes.csv').open(encoding='utf-8')))
assert len(original_nodes)==N
assert [int(r['node_index']) for r in original_nodes]==list(range(N))

profiles=[];partitions=[];coverage=[]
for rec in summary['candidates']:
    name=rec['candidate'];folder=OUT/name;folder.mkdir(exist_ok=True)
    static=PRIOR/'artifacts'/name/'static_boundary.npz'
    z=np.load(static,allow_pickle=False)
    h=z['global_node_id'];n=len(h);ei=rec['internal_edges'];erh=rec['incoming_edges'];s=rec['incoming_source_nodes']
    inside=np.zeros(N,dtype=bool);inside[h]=True
    rest=np.flatnonzero(~inside)
    hmap=np.full(N,-1,dtype=np.int32);hmap[h]=np.arange(n)
    rmap=np.full(N,-1,dtype=np.int32);rmap[rest]=np.arange(len(rest))
    classes={label:z[key+'_edge_id'] for label,key in [('HH','internal'),('RH','incoming'),('HR','outgoing')]}
    occupied=np.concatenate(list(classes.values()))
    assert len(np.unique(occupied))==len(occupied)
    rr_mask=np.ones(E,dtype=bool);rr_mask[occupied]=False
    classes['RR']=np.flatnonzero(rr_mask)
    assert sum(len(v) for v in classes.values())==E
    assert np.array_equal(np.sort(np.concatenate(list(classes.values()))),np.arange(E))
    for label,key in [('HH','internal'),('RH','incoming'),('HR','outgoing')]:
        src,dst=z[key+'_source_index'],z[key+'_target_index']
        expected={'HH':inside[src]&inside[dst], 'RH':~inside[src]&inside[dst], 'HR':inside[src]&~inside[dst]}[label]
        assert expected.all()
    np.savez_compressed(folder/'edge_partition_ids.npz',**classes)
    with (folder/'node_map.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=['global_node_index','cell_type','u','v','partition','local_index'])
        writer.writeheader()
        for r in original_nodes:
            g=int(r['node_index'])
            writer.writerow(dict(global_node_index=g,cell_type=r['cell_type'],u=r['u'],v=r['v'],
                partition='H' if inside[g] else 'R',local_index=int(hmap[g] if inside[g] else rmap[g])))
    part=dict(candidate=name,H_nodes=n,R_nodes=N-n,edge_counts={k:len(v) for k,v in classes.items()},
        all_original_edge_ids_present_once=True,incident_edge_endpoints_checked=True,
        RR_scope='Exact ID complement of the previously full-graph-audited HH/RH/HR; RR endpoint/parameter table not newly exported',
        HH_fraction_of_full_edge_count=ei/E,H_fraction_of_full_node_count=n/N,
        HH_plus_RH_fraction_of_full_edge_count=(ei+erh)/E,
        incoming_sources=s,affected_R_targets=rec['outgoing_target_nodes'])
    partitions.append(part)
    for layout in ['CURRENT_AGG','SOURCE_RAW','EDGE_CURRENT']:
        input_scalars={'CURRENT_AGG':n,'SOURCE_RAW':s,'EDGE_CURRENT':erh}[layout]
        request=4*(input_scalars+n);response=4*n
        # Comparable logical storage model, not inferred hardware utilization.
        base=8*ei+20*n
        extra={'CURRENT_AGG':8*n,
               'SOURCE_RAW':8*erh+4*s+4*n,
               'EDGE_CURRENT':8*erh+4*n}[layout]
        host_rh_terms=erh if layout!='SOURCE_RAW' else 0
        pl_terms=ei+(erh if layout=='SOURCE_RAW' else 0)
        row=dict(candidate=name,layout=layout,H_nodes=n,HH_edges=ei,RH_edges=erh,HR_edges=rec['outgoing_edges'],
            incoming_sources=s,boundary_input_scalars=input_scalars,external_x_scalars=n,
            request_bytes=request,response_bytes=response,total_payload_bytes_per_step=request+response,
            payload_bytes_per_second_at_200_steps=(request+response)*200,
            PL_weighted_edge_terms_per_step=pl_terms,
            host_RH_weighted_terms_per_step=host_rh_terms,host_HR_weighted_terms_per_step=rec['outgoing_edges'],
            PL_boundary_contribution_adds_per_step=erh if layout=='EDGE_CURRENT' else (n if layout=='CURRENT_AGG' else 0),
            base_core_logical_bytes=base,profile_extra_logical_bytes=extra,
            profile_core_logical_bytes=base+extra,
            ideal_BRAM36_bit_capacity_floor=math.ceil((base+extra)/4608),
            numeric_scalar_container='FP32 for this analysis; no hardware numeric profile selected',
            header_bytes_included=0,hardware_profile_status='NOT_SELECTED_NOT_FROZEN')
        profiles.append(row)
    runtime_reference=None
    if name in ['A_T4c','B_T5c']:
        typ='T4c' if name=='A_T4c' else 'T5c'
        root=FPGA/'flyvis-visual-experiments/artifacts/boundary_cuda_r1'/typ
        old=list(csv.DictReader((root/'internal_nodes.csv').open(encoding='utf-8')))
        old_g=[int(r['node_index']) for r in old]
        assert np.array_equal(old_g,h)
        old_sources=list(csv.DictReader((root/'incoming_source_nodes.csv').open(encoding='utf-8')))
        assert np.array_equal([int(r['node_index']) for r in old_sources],z['incoming_source_global_node_id'])
        cases=[]
        for sample in [0,1,12,13]:
            sr=root/f'sample_{sample:02d}'
            init=np.load(sr/'initial_internal.npy',allow_pickle=False)
            bnd=np.load(sr/'boundary_incoming_activity_before.npy',mmap_mode='r',allow_pickle=False)
            state=np.load(sr/'internal_activity_after.npy',mmap_mode='r',allow_pickle=False)
            xt=np.load(sr/'external_node_input.npy',mmap_mode='r',allow_pickle=False)
            assert init.shape==(n,) and state.shape==(485,n) and bnd.shape==(485,s) and xt.shape==(485,n)
            assert all(np.isfinite(a).all() for a in [init,bnd,state,xt])
            assert (xt==0).all()  # Confirmed direct injection only, not boundary activity.
            cases.append(dict(condition_sample=sample,initial_internal_sha256=sha(sr/'initial_internal.npy'),
                recorded_steps=485,recorded_x_H_all_zero=True,reference_path=str(sr)))
        runtime_reference=dict(scope='Recorded-boundary local replay only',cases=cases)
    coverage.append(dict(candidate=name,static_npz_sha256=sha(static),full_node_map='EXPORTED',
        all_four_edge_id_partitions='EXPORTED',HH_RH_HR_parameter_tables='EXISTING_ROUND1',
        full_RR_endpoint_parameter_table='NOT_EXPORTED_THIS_LANE',
        canonical_full_initial_state='NOT_AVAILABLE_IN_REFERENCED_BUNDLE',
        actual_H_runtime_reference=runtime_reference,closed_loop='NOT_RUN'))

assert all(sha(Path(p))==digest for p,digest in before.items())
result=dict(date='2026-10-10',protocol_version='0.1',controller_contract_state='DRAFT_NOT_FROZEN',
    analysis_state='STATIC_ALIGNMENT_COMPLETE',input_snapshots_sha256=before,
    controller_documents_unchanged=True,source_audit_evidence_inventory_verified=len(source_audit['evidence_inventory']),
    historical_manifest_verification=manifest_checks,
    historical_manifest_entries=sum(c['entries'] for c in manifest_checks),
    model_identity={k:summary[k] for k in ['source_commit','checkpoint_sha256','connectome_sha256']},
    profiles=profiles,partitions=partitions,bundle_coverage=coverage,
    storage_model=dict(base='8*HH + 20*H: old/new activity, accumulator, bias, inverse_tau',
       CURRENT_AGG_extra='8*H: incoming drive and direct x input',
       SOURCE_RAW_extra='8*RH + 4*unique_sources + 4*H: packed RH table, source buffer, x',
       EDGE_CURRENT_extra='8*RH + 4*H: uint32 target schedule, FP32 per-edge current buffer, x',
       exclusions=['Port/depth/packing loss','HH/RH merge schedule','queues and system shell',
                   'operators, extra state/debug buffers','PS DDR/network staging'],
       scope='Illustrative logical data model, NOT synthesis or capacity proof'),
    no_header_or_physical_interface_selected=True,no_simulation_or_RTL_or_board_operation=True,
    authority='Final choices belong to user / total architecture; all listed design choices remain pending')
dump(OUT/'alignment_summary.json',result)
with (OUT/'boundary_profiles.csv').open('w',newline='',encoding='utf-8') as f:
    keys=['candidate','layout','H_nodes','HH_edges','RH_edges','incoming_sources','request_bytes','response_bytes',
          'total_payload_bytes_per_step','payload_bytes_per_second_at_200_steps','PL_weighted_edge_terms_per_step',
          'host_RH_weighted_terms_per_step','profile_core_logical_bytes','ideal_BRAM36_bit_capacity_floor']
    writer=csv.DictWriter(f,fieldnames=keys);writer.writeheader();writer.writerows({k:r[k] for k in keys} for r in profiles)
dump(OUT/'artifact_manifest.json',[dict(path=str(p.relative_to(OUT)),bytes=p.stat().st_size,sha256=sha(p))
     for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='artifact_manifest.json'])
print(json.dumps(dict(controller_inventory_verified=result['source_audit_evidence_inventory_verified'],
    historical_manifest_entries=result['historical_manifest_entries'],profiles=len(profiles),
    partitions=[p['edge_counts'] for p in partitions]),ensure_ascii=False))
