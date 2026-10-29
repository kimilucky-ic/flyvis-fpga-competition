from pathlib import Path
import json,statistics,sys
P=Path(__file__).resolve().parent;R=P.parent/'ov5640_live_r3_20261025';B=R/'bundle';A=P/'archive_fcf094ea';raw=A/'raw'
sys.path.insert(0,str(B));from live_protocol import unpack
r2=P.parent/'ov5640_live_r2_20261025';c2=json.loads((r2/'pc/session.json').read_text());f2=json.loads((r2/'pc/records/FINISH.json').read_text())
def stats(v):
 v=list(v);return dict(n=len(v),mean=statistics.mean(v),median=statistics.median(v),min=min(v),max=max(v),sum=sum(v))
rows=[]
for k in range(32):
 d=raw/'capture/bound'/('%06d'%k);t=json.loads((d/'TIMING.json').read_text());p=json.loads((d/'PACKET_TIMING.json').read_text());pr=p['producer_profile']
 _,_,_=unpack((r2/'pc/records'/('%06d.packet'%k)).read_bytes(),c2)
 m,_,_=unpack((r2/'pc/records'/('%06d.packet'%k)).read_bytes(),c2)
 io={n:sum(v['ms'] for key,v in pr.items() if key.startswith(prefix)) for n,prefix in [('write_flush_ms','write:'),('file_fsync_ms','fsync:'),('rename_ms','rename:')]}
 io['directory_fsync_ms']=pr.get('directory_fsync',{}).get('ms',0);io['profiled_disk_total_ms']=sum(io.values())
 rows.append(dict(step=k+1,r3=dict(t,**{key:p[key] for key in ['full_iteration_before_pacing_ms','packet_build_and_persist_ms']},**io,**{key:v['ms'] for key,v in pr.items() if key.startswith('preprocess_')}),r2=dict(m['timing'],**f2['packet_timings']['%06d'%k])))
res={'scope':'Offline saved monotonic duration records; no new board operation. Steady excludes first step. Upload overlaps producer; profile categories overlap camera/bridge/index totals. Profile excludes PACKET_TIMING write itself.', 'rows':rows}
for scope,subset in [('all32',rows),('steady31',rows[1:])]:
 res[scope]={rev:{key:stats(x[rev][key] for x in subset) for key in subset[0][rev] if isinstance(subset[0][rev][key],(int,float)) and not isinstance(subset[0][rev][key],bool)} for rev in ['r2','r3']}
 res[scope]['speedup']=res[scope]['r2']['full_iteration_before_pacing_ms']['mean']/res[scope]['r3']['full_iteration_before_pacing_ms']['mean']
acks=[json.loads(p.read_text()) for p in sorted((raw/'transport').glob('*.ack.json'))]
res['upload_acked31']={key:stats(a[key]*1000 for a in acks) for key in ['rebuild_seconds','round_trip_seconds']}
res['upload_acked31']['note']='Roundtrip includes request, PC validation/durable save and local ACK digest check; excludes ACK file fsync, idle polling and failed requests. No ACK for step32.'
res['upload_acked31']['step_ids']=[a['step_id'] for a in acks]
res['phase_loop_seconds']=(json.loads((raw/'PHASE_CHECK_COMPLETE.json').read_text())['monotonic_ns']-json.loads((raw/'PHASE_BOUNDED_CAPTURE_AND_STEPS.json').read_text())['monotonic_ns'])/1e9
profile={}
for k in range(1,32):
 pr=json.loads((raw/'capture/bound'/('%06d'%k)/'PACKET_TIMING.json').read_text())['producer_profile']
 for key,v in pr.items():
  if 'CAMERA_BUFFER' in key:key=key.split(':')[0]+':CAMERA_BUFFER.json'
  profile.setdefault(key,[]).append(v['ms'])
res['profile_steady31']={key:stats(v) for key,v in profile.items()}
(A/'TIMING_ANALYSIS.json').write_text(json.dumps(res,indent=2)+'\n')
for rev in ['r2','r3']:
 print(rev,{k:round(v['mean'],3) for k,v in res['steady31'][rev].items()})
print('speedup',res['steady31']['speedup'],'loop',res['phase_loop_seconds']);print('upload',res['upload_acked31'])
print('disk top',sorted([(k,round(v['mean'],3)) for k,v in res['profile_steady31'].items() if k.startswith('fsync:')],key=lambda x:-x[1]))
