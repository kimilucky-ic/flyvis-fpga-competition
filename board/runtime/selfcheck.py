"""Public saved-input/full-state CPU self check. No camera pixels or device I/O."""
from pathlib import Path
import hashlib,json,subprocess,sys,tempfile,shutil
def verify(root):
 root=Path(root).resolve();rows=json.loads((root/'manifest.json').read_text('utf8'))['files']
 for n,v in rows.items():
  p=(root/n).resolve()
  if not p.is_relative_to(root) or not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=v['sha256']:raise ValueError('Package mismatch: '+n)
 sys.path.insert(0,str(root/'app/bundle'))
 from offline_check import verify as check
 return check(root/'app/bundle')
def oracle_check(root):
 root=Path(root).resolve();verify(root);bundle=root/'app/bundle'
 with tempfile.TemporaryDirectory(prefix='flyvis_saved_vector_') as temp:
  work=Path(temp)
  for n in ['edges.bin','meta.hex','initial_state.bin']:shutil.copyfile(bundle/n,work/n)
  p=subprocess.run([str(bundle/'reference.exe'),str(work),str(root/'checks/input.bin'),str(work/'state.bin')],capture_output=True,timeout=60)
  if p.returncode:raise RuntimeError('Independent reference failed')
  if (work/'state.bin').read_bytes()!=(root/'checks/state.bin').read_bytes():raise ValueError('Saved full-state mismatch')
 return dict(status='PASS_SAVED_INPUT_FULL_STATE_REFERENCE',input_words=721,state_words=45669,mismatches=0,camera_mapping='NOT_RETESTED_NO_RAW_PIXELS_DISTRIBUTED',GPU=False,board_access=False)
if __name__=='__main__':print(json.dumps(oracle_check(Path(__file__).resolve().parent),indent=2))
