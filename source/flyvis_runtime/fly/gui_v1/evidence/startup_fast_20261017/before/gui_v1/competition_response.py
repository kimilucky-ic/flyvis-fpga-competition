"""Read-only admission of the selected C baseline display; no model execution."""
import hashlib
import json
from pathlib import Path
import numpy as np
from scientific_pilot import require

C_ENCODING_SHA='92363010e257c9e26178db1b984e2f4656dea7c86a464f6a5e4c51a7386c9a41'

def verify_source_contract(config,replay):
    raw=Path(config['synchronization_contract']).read_bytes()
    require(hashlib.sha256(raw).hexdigest()==config['synchronization_sha256'],'C synchronization contract changed')
    c=json.loads(raw);m=replay.metadata()
    require(c['run_id']==m['run_id'] and c['model']==m['model'] and c['condition']=='ON60' and c['mode']=='Full','C source run/model')
    require(c['sealed_pilot_manifest_sha256']==m['manifest_sha256'] and c['source_dt_s']==.005,'C scientific manifest')
    expected={str(Path(x['path']).resolve()):x['sha256'] for x in m['source_files']}
    for row in c['source_files']:
        p=Path(row['path']);require(hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'],'C source SHA '+str(p))
        if str(p.resolve()) in expected:require(expected[str(p.resolve())]==row['sha256'],'C GUI source disagreement');expected.pop(str(p.resolve()))
    require(not expected,'C missing GUI scientific source')
    require(c['input_time_s']==m['input_time_s'] and c['activity_time_s']==m['activity_time_s'],'C dual timeline')
    require(c['video']['source_for_video_frame']==[n*485//1200 for n in range(1200)] and c['video']['duration_s']==40,'C video mapping')
    return c

def validate_c_encoding(e,means):
    require(e['mode']=='fixed_type_hue_baseline_response_brightness_v1','C display mode')
    baseline=means[100:200].mean(axis=0,dtype=np.float64)
    require(np.array_equal(baseline,np.asarray(e['baseline']['values'])),'C fixed baseline differs from actual saved means')
    require(e['baseline']['step_start_inclusive']==100 and e['baseline']['step_end_exclusive']==200,'C baseline interval')
    delta=means-baseline
    require(e['intensity_domain']==[0.,float(np.max(np.abs(delta)))] and e['raw_activity_domain']==[-float(np.max(np.abs(means))),float(np.max(np.abs(means)))],'C raw and delta scales')
    require(e['display_deadband']==.005 and e['brightness_floor']==.22 and e['gamma']==.45,'C fixed display parameters')

def validate_c_states(states,e,means):
    baseline=np.asarray(e['baseline']['values']);delta=means-baseline
    q=np.clip((np.abs(delta)-.005)/(e['intensity_domain'][1]-.005),0,1)
    for i,s in enumerate(states):
        require(s['activity_signed']==means[i] and s['baseline']==baseline[i] and s['delta_signed']==delta[i],'C actual signed values')
        require(s['delta_polarity']==('positive' if delta[i]>0 else 'negative' if delta[i]<0 else 'zero'),'C delta sign')
        require(abs(s['brightness_factor']-(.22+.78*q[i]**.45))<1e-15 and abs(s['halo_opacity']-.16*np.clip((q[i]-.2)/.8,0,1)**.6)<1e-15,'C fixed brightness/outline')
        require(s['identity_color']==e['palette'][s['type']],'C identity hue')
