"""Seal only this stage, retaining the immutable stage-one manifest and package."""
from pathlib import Path
import argparse
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from camera_pipeline.common import ROOT, sha256, utc_now, write_json

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--verify', action='store_true'); a = p.parse_args()
    phase = ROOT/'phase2'
    manifest_path = phase/'results/manifest.json'
    if a.verify:
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        for entry in manifest['files']:
            path = (ROOT/entry['path']).resolve()
            assert path.is_relative_to(phase.resolve())
            assert path.stat().st_size == entry['bytes'] and sha256(path) == entry['sha256'], entry['path']
        assert sha256(ROOT/'results/validation/manifest.json') == manifest['phase1_manifest_sha256']
        print({'status': 'PASS', 'verified_phase2_files': len(manifest['files'])})
    else:
        files = [{'path': file.relative_to(ROOT).as_posix(), 'sha256': sha256(file), 'bytes': file.stat().st_size}
                 for file in sorted(phase.rglob('*')) if file.is_file() and file != manifest_path
                 and '__pycache__' not in file.parts and file.suffix not in ('.pyc', '.tmp')]
        write_json(manifest_path, {'schema': 'flyvis-camera-phase2-manifest-v1', 'created_utc': utc_now(),
                                  'phase1_manifest_sha256': sha256(ROOT/'results/validation/manifest.json'),
                                  'files': files, 'exclusions': 'manifest itself and Python bytecode/temporary files'})
        print({'status': 'SEALED', 'phase2_files': len(files)})
