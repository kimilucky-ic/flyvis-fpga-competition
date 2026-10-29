from pathlib import Path
import json,numpy as np,hashlib
B=Path(r'C:/Users/hzy72/Documents/ChatGPT/fly');E=B/'gui_v1/evidence/central_display_timing_20261021';R=B/'gui_v1/runtime/line11_live_camera/4fc03f4a729340598b20eb957875d768';ids=[24399,25120,25841,26562,27283,28004,28725,29446];a=[];inp=[]
for k in range(485):
 f=R/'official_flow'/f'{k:06d}';m=json.loads(f.with_suffix('.json').read_text());bits=f.with_suffix('.state.bin').read_bytes();iv=f.with_suffix('.input.bin').read_bytes();src=json.loads((R/'source_frames'/f'{k:06d}.json').read_text());assert hashlib.sha256(bits).hexdigest()==m['full_state_sha256']==src['full_state_sha256'];assert hashlib.sha256(iv).hexdigest()==m['input_sha256']==src['input_sha256'];assert src['step']==m['frame_id']==k;assert src['model_input_time_s']==k*.005 and src['model_activity_time_s']==(k+1)*.005;assert src['source']['sequence']==k
 a.append(np.frombuffer(bits,dtype='<f4')[ids]);inp.append(float(np.frombuffer(iv,dtype='<f4')[360]))
a=np.array(a);v=np.maximum(a[:,5],0);peak=int(v[200:401].argmax()+200);half=np.flatnonzero((np.arange(485)>=200)&(np.arange(485)<=400)&(v>=v[peak]/2))
out=dict(run=R.name,condition='EDGE_OFF_RIGHT',verified_steps=485,source_step_and_state_bindings=True,T5b=dict(peak_step=peak,peak_raw=float(a[peak,5]),peak_activity_s=(peak+1)*.005,half_peak_steps=[int(half[0]),int(half[-1])],half_peak_model_s=len(half)*.005),motion_window_steps=[200,400],central_values=a.tolist(),central_input=inp)
(E/'TIMING.json').write_text(json.dumps(out,indent=2));print({k:v for k,v in out.items() if k not in ['central_values','central_input']})
