"""Supplementary static representability check; no Torch/model inference/training.

This is a structural calculation after the five-condition preregistration.
It changes no acceptance gate and supplies no recovered model.
"""
from pathlib import Path
import hashlib, json, time
import numpy as np

HERE=Path(__file__).resolve().parent
LANE=HERE.parent
began=time.perf_counter()
m=dict(np.load(LANE/'cnn_t4t5_replacement_20261016/mapping.npz'))
p=dict(np.load(LANE/'phase4_direction_extension_20261010/pre_run_20261011_r1/input_bundle/expanded_parameters.npz'))
H=m['H_grid_ids'];F=m['field_ids'];uv=m['grid_uv'];offsets=m['offsets'];neighbors=m['neighbors']
channel=np.full(45669,-1,np.int64);position=channel.copy()
assert len(np.unique(F))==F.size
channel[F.reshape(-1)]=np.repeat(np.arange(23),721)
position[F.reshape(-1)]=np.tile(np.arange(721),23)
ht=np.full(45669,-1,np.int64);hp=ht.copy()
ht[H.reshape(-1)]=np.repeat(np.arange(8),721);hp[H.reshape(-1)]=np.tile(np.arange(721),8)
mask=ht[p['target_global']]>=0
src=p['source_global'][mask];dst=p['target_global'][mask];weights=p['effective_weight'][mask]
assert (channel[src]>=0).all()
du,dv=uv[:,position[src]]-uv[:,hp[dst]]
lookup={tuple(x):i for i,x in enumerate(offsets)}
tap=np.asarray([lookup.get((int(u),int(v)),-1) for u,v in zip(du,dv)])
assert (tap>=0).all()
assert np.array_equal(F[channel[src],neighbors[hp[dst],tap]],src)
inverse_tau=np.float32(1)/np.maximum(p['time_const'],np.float32(.005))
coeff=np.zeros((8,23,169,721),np.float32)
np.add.at(coeff,(ht[dst],channel[src],tap,hp[dst]),weights*inverse_tau[dst]*np.float32(.005))
valid=np.broadcast_to((neighbors.T>=0)[None],(23,169,721))
lo=np.where(valid[None],coeff,np.inf).min(-1)
hi=np.where(valid[None],coeff,-np.inf).max(-1)
span=hi-lo
# Three continuous operator terms: ReLU spatial sources, raw self decay, bias.
self_decay=(-np.float32(.005)*inverse_tau[H]).astype(np.float32)
bias=(np.float32(.005)*inverse_tau[H]*p['bias'][H]).astype(np.float32)
decay_span=np.ptp(self_decay,axis=1);bias_span=np.ptp(bias,axis=1)
external_H_count=int(np.isin(p['input_node_index'],H).sum())
coefficient_shared=bool(float(span.max())<=1e-7)
shared=coefficient_shared and float(decay_span.max())<=1e-7 and float(bias_span.max())<=1e-7 and external_H_count==0
result=dict(status='STATIC_SHARED_OPERATOR_EXPRESSIBLE' if shared else 'STATIC_SHARED_OPERATOR_HAS_UNREPRESENTED_VARIATION',
    H_nodes=5768,H_target_edges=int(mask.sum()),all_edge_sources_in_fields=True,all_offsets_within_radius7=True,
    all_edge_field_neighbor_IDs_match=True,valid_source_features=23*169,
    maximum_valid_position_coefficient_span=float(span.max()),
    coefficient_groups_with_span_over_1e7=int((span>1e-7).sum()),
    maximum_decay_span=float(decay_span.max()),maximum_bias_span=float(bias_span.max()),external_H_injections=external_H_count,
    decay_by_type=self_decay[:,0].tolist(),bias_by_type=bias[:,0].tolist(),
    interpretation='Only an algebraic capacity check. If all spans vanish, this radius7 ReLU-convolution plus signed recurrent self-term and bias can express the original H update in real arithmetic. It does not prove trained weights found it or FP32 operation-order equivalence.',
    model_updates=0,neural_forward_calls=0,production_commits=0,GPU=0,board=0,
    preregistration_role='supplementary static analysis; no new functional test or threshold revision',wall_s=time.perf_counter()-began)
(HERE/'OPERATOR_AUDIT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
