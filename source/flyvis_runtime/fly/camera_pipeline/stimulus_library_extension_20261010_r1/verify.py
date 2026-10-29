"""Read-only candidate seal and unchanged prior-input check; never decode/rerender."""
from pathlib import Path
import argparse
import json
from generate import ROOT, prior_identity, sha256, write_json

p=argparse.ArgumentParser(); p.add_argument('--seal',action='store_true'); args=p.parse_args()
manifest_path=ROOT/'manifest.json'
manifest=json.loads(manifest_path.read_text())
for entry in manifest['files']:
    path=(ROOT/entry['path']).resolve()
    assert path.is_relative_to(ROOT.resolve()) and path.stat().st_size==entry['bytes'] and sha256(path)==entry['sha256'],path
current=prior_identity()
validation=json.loads((ROOT/'validation.json').read_text())
assert validation['status']=='PASS' and current==validation['protected_before_after']
if args.seal:
    # Only finalize this new candidate namespace after documentation is added.
    files=[{'path':path.relative_to(ROOT).as_posix(),'bytes':path.stat().st_size,'sha256':sha256(path)}
           for path in sorted(ROOT.rglob('*')) if path.is_file() and path!=manifest_path and '__pycache__' not in path.parts]
    write_json(manifest_path,{'schema':'flyvis-candidate-animation-seal-v1','files':files,
                            'scope':'this new candidate library only; prior P0 inputs remain frozen'})
    manifest={'files':files}
print(json.dumps({'status':'PASS','candidate_files_verified':len(manifest['files']),
                  'prior_files_unchanged':current['historical_sealed_files_checked'],'network_inference':False}))
