"""Read-only identities of protected reference outputs and tracked upstream source."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import argparse
import json
import subprocess
from camera_pipeline.common import ROOT,sha256,write_json

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('output',type=Path);p.add_argument('--compare',type=Path);a=p.parse_args()
    fly=ROOT.parent;fpga=fly.parent/'fpga'
    locations=[fly/'artifacts/golden_reference_v1',fly/'artifacts/moving_edge_minimal_cpu_v1',
               fpga/'flyvis-visual-experiments/artifacts/golden_reference_v2']
    hashes={str(f.resolve()):sha256(f) for location in locations for f in location.rglob('*') if f.is_file()}
    state={'protected_files':hashes,'tracked_upstream_status':subprocess.check_output(['git','-C',str(fly/'upstream/flyvis'),'status','--porcelain','--untracked-files=no'],text=True),
           'source_commit':subprocess.check_output(['git','-C',str(fly/'upstream/flyvis'),'rev-parse','HEAD'],text=True).strip()}
    if a.compare:
        before=json.loads(a.compare.read_text(encoding='utf-8'))
        state['protected_hashes_unchanged']=hashes==before['protected_files']
        assert state['protected_hashes_unchanged'],'Protected reference identity changed'
    write_json(a.output,state)
    print({'protected_file_count':len(hashes),'tracked_upstream_status':state['tracked_upstream_status'],
           'unchanged':state.get('protected_hashes_unchanged')})
