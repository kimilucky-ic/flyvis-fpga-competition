"""Descriptive explanation of registered failures; saved arrays ONLY.

These post-run diagnostics do not change any gate, count or pass/fail result.
No torch imports, model calls or extra stimuli.
"""
from pathlib import Path
import json
import numpy as np

HERE=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
mapping=dict(np.load(HERE.parent/'cnn_t4t5_replacement_20261016/mapping.npz'))
roi=np.load(HERE.parent/'t4t5_criticality_20261011/cpu_preparation_r1/flow_ROI_hex_indices.npy')
case='STATIC_TEXTURE5s'; root=HERE/'runs'/case
full=np.load(root/'Full/states_raw.npy',mmap_mode='r')[-200:,mapping['H_grid_ids']].astype(np.float64)
cnn=np.load(root/'CNN/states_raw.npy',mmap_mode='r')[-200:,mapping['H_grid_ids']].astype(np.float64)
d=cnn-full
ff=np.load(root/'Full/flow.npy',mmap_mode='r')[-200:][:,:,roi].astype(np.float64)
cf=np.load(root/'CNN/flow.npy',mmap_mode='r')[-200:][:,:,roi].astype(np.float64)
df=cf-ff
static=dict(H_error_RMSE=float(np.sqrt(np.mean(d*d))),
    H_error_time_mean_field_RMS=float(np.sqrt(np.mean(d.mean(0)**2))),
    H_error_temporal_variation_RMS=float(np.sqrt(np.mean((d-d.mean(0))**2))),
    H_full_activity_RMS=float(np.sqrt(np.mean(full*full))),
    H_state_relative_L2=float(np.linalg.norm(d)/np.linalg.norm(full)),
    subtype_H_error_RMSE=np.sqrt(np.mean(d*d,axis=(0,2))).tolist(),
    flow_error_component_RMSE=float(np.sqrt(np.mean(df*df))),
    flow_error_temporal_variation_RMS=float(np.sqrt(np.mean((df-df.mean(0))**2))),
    full_raw_flow_component_RMS=float(np.sqrt(np.mean(ff*ff))),
    cnn_raw_flow_component_RMS=float(np.sqrt(np.mean(cf*cf))),
    raw_flow_relative_L2=float(np.linalg.norm(df)/np.linalg.norm(ff)),
    decoded_input_late_temporal_RMS=load(HERE/'inputs'/(case+'_time.json'))['late_input_temporal_RMS'])
summary=load(HERE/'SUMMARY.json')
failed=next(r for r in summary['records'] if r['case']=='OFF345_local_moving_background')
local=failed['windows']['active']['foreground_flow']; M=local['magnitude_ratio']; Q=local['Q']; E=local['field_error_E']
amplitude=(M-1)**2; field_angle=2*(M-Q)
assert np.isclose(E**2,amplitude+field_angle,rtol=1e-10,atol=1e-12)
result=dict(status='DESCRIPTIVE_SAVED_DATA_ONLY_NOT_NEW_ACCEPTANCE',static_texture_late=static,
    failed_local=dict(E=E,M=M,Q=Q,field_angle_deg=local['angle_deg'],
        squared_error_amplitude_term=amplitude,squared_error_field_angle_term=field_angle,
        note='field angle is a flattened spatiotemporal field angle; decomposition is not causal attribution'),
    limits='No causal isolation of background/direction/polarity; no single-step teacher-forced new inference; no classifier false-positive definition; existing failures retained.',
    new_neural_steps=0,model_calls=0,GPU=0,board=0)
with (HERE/'FAILURE_DIAGNOSTICS.json').open('x',encoding='utf-8') as stream: json.dump(result,stream,indent=2)
print(json.dumps(result,indent=2))
