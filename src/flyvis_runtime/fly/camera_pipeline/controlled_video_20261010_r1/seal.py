"""Seal only the new controlled-file experiment; earlier manifests remain immutable."""
from pathlib import Path
import argparse
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from camera_pipeline.common import sha256, utc_now, write_json
from camera_pipeline.controlled_video_20261010_r1.prepare import TASK

if __name__ == '__main__':
    p=argparse.ArgumentParser(); p.add_argument('--verify', action='store_true'); a=p.parse_args()
    manifest_path=TASK/'manifest.json'
    if a.verify:
        manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
        for entry in manifest['files']:
            path=(TASK/entry['path']).resolve()
            assert path.is_relative_to(TASK.resolve())
            assert path.stat().st_size==entry['bytes'] and sha256(path)==entry['sha256'],entry['path']
        print({'status':'PASS','verified_files':len(manifest['files'])})
    else:
        files=[{'path':p.relative_to(TASK).as_posix(),'bytes':p.stat().st_size,'sha256':sha256(p)}
               for p in sorted(TASK.rglob('*')) if p.is_file() and p!=manifest_path
               and '__pycache__' not in p.parts and p.suffix not in ('.pyc','.tmp')]
        write_json(manifest_path,{'schema':'flyvis-controlled-video-manifest-v1','created_utc':utc_now(),'files':files,
                                 'scope':'this isolated experiment only; sources and earlier packages are read-only',
                                 'excluded':'manifest itself, bytecode and temporary files'})
        print({'status':'SEALED','files':len(files)})
