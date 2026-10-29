"""Seal completed persistent files after validation log writers finish; verify with --verify."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import argparse
import json
from camera_pipeline.common import ROOT,sha256,utc_now,write_json

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--verify',action='store_true');args=parser.parse_args()
    path=ROOT/'results/validation/manifest.json'
    if args.verify:
        manifest=json.loads(path.read_text(encoding='utf-8'))
        mismatches=[name for name,digest in manifest['files'].items() if not (ROOT/name).is_file() or sha256(ROOT/name)!=digest]
        if mismatches:raise SystemExit('Manifest mismatch: '+', '.join(mismatches))
        print({'status':'PASS','verified_files':len(manifest['files'])})
    else:
        files={str(p.relative_to(ROOT)):sha256(p) for p in ROOT.rglob('*')
               if p.is_file() and p.suffix in ('.py','.ps1','.sh','.md','.npy','.csv','.json','.png','.avi','.log','.txt')
               and not any(part in ('_vendor','runtime','__pycache__') for part in p.relative_to(ROOT).parts)
               and p!=path}
        write_json(path,{'schema':'flyvis-camera-file-manifest-v1','created_utc':utc_now(),'files':files,
                         'excluded':'optional installed dependency, temporary cache/locks, Python bytecode; manifest itself'})
        print({'status':'SEALED','files':len(files)})
