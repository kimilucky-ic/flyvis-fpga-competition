"""FP32 semantic HH/RH tables for C; no rounding/wire/RTL profile decision."""
import csv
import numpy as np
from common import *


def bits(value):return f'{int(np.float32(value).view(np.uint32)):08x}'


def main():
    out=HERE/'c_reference'
    if out.exists():raise SystemExit('Existing C parameter tables preserved')
    out.mkdir()
    with np.load(STATIC,allow_pickle=False) as archive:
        p={name:archive[name] for name in archive.files}
    h=HUpdater(STATIC);initial=np.load(BUNDLE/'initial_state_full.npy',allow_pickle=False).reshape(-1)
    edges=[]
    for route,partition in [('internal','HH'),('incoming','RH')]:
        for j,edge_id in enumerate(p[route+'_edge_id']):
            source=int(p[route+'_source_index'][j]);target=int(p[route+'_target_index'][j])
            weight=p[route+'_weight'][j]
            source_local=int(np.searchsorted(h.h_ids if partition=='HH' else h.source_ids,source))
            edges.append(dict(original_edge_id=int(edge_id),partition=partition,source_global=source,
                source_array='old_H' if partition=='HH' else 'boundary_before',source_local=source_local,
                target_global=target,target_H_local=int(p[route+'_target_local'][j]),
                weight_float32=format(float(weight),'.9g'),weight_ieee754_hex=bits(weight)))
    edges.sort(key=lambda row:row['original_edge_id'])
    assert len(edges)==6537 and len(set(row['original_edge_id'] for row in edges))==6537
    nodes=[]
    for local,global_id in enumerate(h.h_ids):
        row=dict(H_local=local,global_node_id=int(global_id))
        for name,value in [('bias',h.bias[local]),('time_const_s',p['time_const_s'][local]),
            ('inverse_tau',h.inverse_tau[local]),('animation_initial_H',initial[global_id])]:
            row[name]=format(float(value),'.9g');row[name+'_ieee754_hex']=bits(value)
        nodes.append(row)
    for name,rows in [('edges_HH_RH_original_order.csv',edges),('H_parameters.csv',nodes)]:
        with (out/name).open('w',newline='',encoding='utf-8') as stream:
            writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    np.save(out/'H_global_ids.npy',h.h_ids);np.save(out/'boundary_source_global_ids.npy',h.source_ids)
    descriptor=dict(schema='B_SOURCE_RAW_C_REFERENCE/v1',status='PASS_PARAMETER_EXPORT_VECTORS_PENDING_800_RUN',
        condition_id='01_off_right',comparison_id=load(BUNDLE/'video_manifest.json')['comparison_id'],
        input_semantics=dict(old_H=67,x_H=67,boundary_before=1364,new_H_expected=67),
        ordered_HH_RH_edges=6537,HH=970,RH=5567,
        circuit_sha256=h.circuit_digest,expanded_parameters_sha256=file_hash(BUNDLE/'expanded_parameters.npz'),
        initial_state_sha256=file_hash(BUNDLE/'initial_state_full.npy'),stimulus_sha256=file_hash(BUNDLE/'stimulus.npy'),
        row_order='ascending original_edge_id across HH/RH; all zero/recurrent/self edges retained',
        fields='IEEE754 hex preserves exact accepted float32 values; CSV decimals independently roundtrip checked',
        expected_vectors_path=str(HERE/'artifacts/python_source_raw_800_r1/SOURCE_RAW_step_io.npz'),
        physical_protocol_frozen=False,hardware_numeric_profile=None,RTL_execution=False,
        C_needed='Declare numeric profile/bittrue oracle/scientific gate and reviewed backend; provide actual RTL then SoC/board evidence')
    for row in edges:assert bits(np.float32(row['weight_float32']))==row['weight_ieee754_hex']
    dump(out/'C_REFERENCE_HANDOFF.json',descriptor);seal(out)
    print(descriptor['status'],len(edges),flush=True)


if __name__=='__main__':main()
