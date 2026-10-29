"""CPU only: audit an extracted R5 board run; never contact a board."""
from pathlib import Path
import argparse,json,sys
P=Path(__file__).resolve().parents[1];sys.path.insert(0,str(P/'bundle'))
import numpy as np
from capture_binding import read_capsule
from live_protocol import Store,load_packet,sha
from ps_input import PsInput
from full_audit import audit

def audit_saved(run,output):
 run=Path(run);output=Path(output);output.mkdir(exist_ok=False,parents=True)
 cfg=json.loads((P/'pc/session.json').read_text());store=Store(output/'records',cfg)
 mapper=PsInput(480,800,'BGR');rows=[]
 finish=json.loads((run/'FINISH.json').read_text());count=finish['completed_steps']
 if not 1<=count<=cfg['max_steps']:raise ValueError('step count bound')
 for k in range(count):
  store.accept(load_packet(run,k));m,_,r=store.read(k)
  pre,blob=read_capsule(run/'capture/bound'/('%06d'%k)/'PREPARED.bin',1152000+2884)
  source=blob[:1152000];inputs=blob[1152000:]
  if pre!=m['prepared'] or sha(source)!=m['source_sha256'] or inputs!=r.input_bits:raise ValueError('saved source/input identity')
  mapped=mapper.render(np.frombuffer(source,np.uint8).reshape(480,800,3)).astype('<f4').tobytes()
  if mapped!=inputs:raise ValueError('source mapping bit mismatch')
  rows.append(dict(step_id=k,source_sha256=sha(source),input_words=721,bitwise_equal=True))
 store.finish(finish)
 if (run/'CAMERA_CLOSE.json').exists():store.record_camera_close(json.loads((run/'CAMERA_CLOSE.json').read_text()))
 result=audit(store,P/'bundle',output/'neural_audit')
 summary=dict(status='PASS_SAVED_INPUT_MAPPING_AND_ALL_STATES' if result['mismatch_words']==0 else 'FAIL_NUMERICAL',
  evidence=result['evidence'],steps=count,state_words_compared=count*45669,mismatch_words=result['mismatch_words'],
  source_mapping_bitwise_equal=True,source_input_words=count*721,camera_close=store.camera_close['status'] if store.camera_close else 'NOT_CONFIRMED',board_actions=0,rows=rows)
 (output/'RESULT.json').write_text(json.dumps(summary,indent=2)+'\n');return summary
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('run');ap.add_argument('output');args=ap.parse_args()
 print(json.dumps(audit_saved(args.run,args.output),indent=2))
