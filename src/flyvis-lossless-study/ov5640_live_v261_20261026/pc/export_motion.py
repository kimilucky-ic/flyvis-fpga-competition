"""Read-only post-run export. No FPGA/GPU or neural recomputation.
Raw80x48 PNGs, signed37-neuron ROI curves, all721inputs CSV, frame-step index.
Not an automatic claim of ON/OFF selectivity or actual hand-motion events.
"""
import argparse,json,csv,sys,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1];sys.path.insert(0,str(P/'bundle'))
import numpy as np
from PIL import Image
from live_protocol import Store,sha
from direct_input import DirectAreaInput
TYPES=['T4a','T4b','T4c','T4d','T5a','T5b','T5c','T5d']
CENTERS=[24399,25120,25841,26562,27283,28004,28725,29446]
OFFSETS=[270,271,272,273,298,299,300,301,302,327,328,329,330,331,332,357,358,359,360,361,362,363,388,389,390,391,392,393,418,419,420,421,422,447,448,449,450]

def export(records,config,output,allow_cpu=False):
 records=Path(records);output=Path(output);store=Store(records,config)
 if config.get('motion_condition') not in ('white_black','black_white','capture'):raise ValueError('not a motion experiment')
 if not store.final or not store.camera_close or store.camera_close['status']!='CLOSED':raise ValueError('normal completion/close required')
 audit=json.loads((records/'audit/RESULT.json').read_text())
 if audit['status']!='PASS_ALL_SAVED_STATES' or audit['steps']!=len(store.meta) or audit['mismatch_words']:raise ValueError('full state acceptance required')
 if any(m['evidence']!='OPERATOR_PHYSICAL_RUN_UNATTESTED' for m in store.meta) and not allow_cpu:raise ValueError('CPU fixtures require explicit test flag')
 output.mkdir(parents=True,exist_ok=False);(output/'frames').mkdir();rows=[];index=[];mapper=DirectAreaInput(48,80,'BGR');max_error=0
 with (output/'inputs721.csv').open('w',newline='',encoding='utf-8') as f:
  writer=csv.writer(f);writer.writerow(['step_id']+['input_'+str(i) for i in range(721)])
  for k in range(len(store.meta)):
   m,source,r=store.read(k);frame=np.frombuffer(source,np.uint8).reshape(48,80,3);input_values=np.frombuffer(r.input_bits,'<f4')
   error=float(np.max(np.abs(mapper.render(frame)-input_values)));max_error=max(max_error,error)
   if error>3e-6:raise ValueError('raw frame to721mapping mismatch')
   Image.fromarray(frame[:,:,::-1],'RGB').save(output/'frames'/('%06d.png'%k))
   states=np.frombuffer(r.state_bits,'<f4');means=[float(np.mean(states[np.array(OFFSETS)+center-360],dtype=np.float64)) for center in CENTERS]
   a=m['experiment'];t=a['elapsed_ns']/1e9
   rows.append(dict(step_id=k,wall_s=t,model_s=(k+1)*.005,planned_phase=a['phase'],planned_trial=a['trial'],**dict(zip(TYPES,means))))
   writer.writerow([k]+input_values.tolist());index.append(dict(step_id=k,wall_s=t,source_timestamp_ns=m['prepared']['source_timestamp_ns'],source_sha256=m['source_sha256'],input_sha256=r.input_sha256,state_sha256=r.state_sha256,packet_sha256=store.digests[k],frame='frames/%06d.png'%k))
 with (output/'signed_T4T5.csv').open('w',newline='',encoding='utf-8') as f:
  writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 fig,axes=plt.subplots(2,4,figsize=(15,6),sharex=True);times=[r['wall_s'] for r in rows]
 for ax,name in zip(axes.flat,TYPES):
  ax.plot(times,[r[name] for r in rows],lw=1);ax.axhline(0,color='gray',lw=.5);ax.set_title(name);ax.set_xlabel('Capture wall time (s)');ax.set_ylabel('Signed state mean, central37')
  if config['motion_condition']!='capture':
   for x,y in [(10,15),(25,30),(40,45)]:ax.axvspan(x,y,color='orange',alpha=.12)
 fig.suptitle(('60s capture | stimulus events not annotated' if config['motion_condition']=='capture' else config['motion_condition']+' | shaded = planned movement, NOT detected edges')+(' | CPU FIXTURE' if allow_cpu else ''))
 fig.tight_layout();fig.savefig(output/'signed_response.png',dpi=140);plt.close(fig)
 manifest=dict(status='CPU_FIXTURE_EXPORT' if allow_cpu else 'EXPORTED_ACCEPTED_OPERATOR_RECORDS',steps=len(rows),source_records=str(records.resolve()),session_id=config['session_id'],condition=config['motion_condition'],raw_frame_shape=[48,80,3],channel_order='BGR_ASSUMED_UNVERIFIED',mapping_max_abs=max_error,dt_s=.005,events='UNANNOTATED_ACTUAL_EDGE_TIMES_REQUIRE_IMAGE_ANALYSIS' if config['motion_condition']=='capture' else 'PLANNED_ONLY_ACTUAL_EDGE_TIMES_REQUIRE_IMAGE_ANALYSIS',signed_values_not_rectified=True,biological_acceptance='NOT_ASSESSED',frame_index=index)
 (output/'INDEX.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8');return manifest
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--records',required=True);p.add_argument('--config',required=True);p.add_argument('--output',required=True);p.add_argument('--allow-cpu-fixture',action='store_true');a=p.parse_args()
 r=export(a.records,json.loads(Path(a.config).read_text()),a.output,a.allow_cpu_fixture);print(r['status'],r['steps'])
