"""Offline extracted R6 run validation; no board/network or source-image claim."""
from pathlib import Path
import sys,json,argparse
P=Path(__file__).resolve().parents[1];sys.path.insert(0,str(P/'bundle'))
from live_protocol import Store,load_packet
from capture_binding import read_capsule
from full_audit import audit

def audit_saved(run,out):
 run=Path(run);out=Path(out);out.mkdir(parents=True,exist_ok=False)
 cfg=json.loads((P/'pc/session.json').read_text());s=Store(out/'records',cfg)
 finish=json.loads((run/'FINISH.json').read_text());count=finish['completed_steps']
 if not 1<=count<=32:raise ValueError('count bound')
 for k in range(count):
  s.accept(load_packet(run,k));m,source,r=s.read(k)
  pre,inputs=read_capsule(run/'capture/bound'/('%06d'%k)/'PREPARED.bin',2884)
  if pre!=m['prepared'] or inputs!=r.input_bits or source is not None:raise ValueError('saved input binding')
 s.finish(finish)
 if (run/'CAMERA_CLOSE.json').exists():s.record_camera_close(json.loads((run/'CAMERA_CLOSE.json').read_text()))
 r=audit(s,P/'bundle',out/'audit');r['source_mapping_audited']=False;r['raw_images_saved']=False
 r['camera_close_status']=s.camera_close['status'] if s.camera_close else 'NOT_CONFIRMED'
 (out/'RESULT.json').write_text(json.dumps(r,indent=2)+'\n');return r
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('run');ap.add_argument('output');a=ap.parse_args()
 r=audit_saved(a.run,a.output);print({k:v for k,v in r.items() if k!='rows'})
