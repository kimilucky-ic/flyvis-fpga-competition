"""Validate C's CSV mapping/FP32 words independently against full parameters."""
import csv
from common import *

out=HERE/'artifacts/consumer_audit_r2';out.mkdir()
c=HERE/'c_reference';manifest_verify(c);manifest_verify(HERE/'gui_bundle')
_,_,h,_,_,initial,_,_,_=read_input()
rows=list(csv.DictReader((c/'edges_HH_RH_original_order.csv').open(encoding='utf-8')))
with np.load(BUNDLE/'expanded_parameters.npz') as p:
    assert len(rows)==6537
    ids=np.array([int(row['original_edge_id']) for row in rows]);assert (np.diff(ids)>0).all()
    with np.load(STATIC) as z:assert np.array_equal(ids,np.sort(np.r_[z['internal_edge_id'],z['incoming_edge_id']]))
    for row in rows:
        edge=int(row['original_edge_id']);src=int(row['source_global']);dst=int(row['target_global'])
        assert src==p['source_global'][edge] and dst==p['target_global'][edge]
        assert h.h_ids[int(row['target_H_local'])]==dst
        source=h.h_ids if row['partition']=='HH' else h.source_ids
        assert source[int(row['source_local'])]==src
        weight=np.float32(row['weight_float32'])
        assert int(weight.view(np.uint32))==int(row['weight_ieee754_hex'],16)==int(p['effective_weight'][edge].view(np.uint32))
    nodes=list(csv.DictReader((c/'H_parameters.csv').open(encoding='utf-8')));assert len(nodes)==67
    for i,row in enumerate(nodes):
        g=int(row['global_node_id']);assert g==h.h_ids[i] and int(row['H_local'])==i
        for key,value in [('bias',p['bias'][g]),('time_const_s',p['time_const'][g]),('inverse_tau',h.inverse_tau[i]),('animation_initial_H',initial[g])]:
            assert int(np.float32(row[key]).view(np.uint32))==int(row[key+'_ieee754_hex'],16)==int(value.view(np.uint32))
v=np.load(c/'SOURCE_RAW_step_io.npz');words=0
for key in ['old_H','x_H','boundary_before','new_H_expected']:
    data=np.loadtxt(c/(key+'_ieee754.mem'),dtype=np.uint32,converters=lambda text:int(text,16),ndmin=1)
    assert np.array_equal(data,np.ascontiguousarray(v[key]).reshape(-1).view(np.uint32));words+=len(data)
assert load(HERE/'GUI_READER_TEST.json')['status']=='PASS_READONLY_ARRAY_CONSUMER'
dump(out/'result.json',dict(status='PASS_C_AND_GUI_CONSUMER_ARTIFACT_CHECK',source_edges=6537,H_parameters=67,
    exact_FP32_vector_words=words,all_original_edge_maps_and_weight_bits_match=True,GUI_browser_verified=False,
    C_manifest_sha256=file_hash(c/'artifact_manifest.json'),GUI_manifest_sha256=file_hash(HERE/'gui_bundle/artifact_manifest.json'),
    evidence_level='READ_ONLY_FORMAT_AND_IDENTITY_VERIFICATION',RTL_execution=False))
seal(out);print('CONSUMER_AUDIT_PASS',words)
