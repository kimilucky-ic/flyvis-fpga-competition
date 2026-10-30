"""Read-only verification of ⑩'s derived background, no renderer or inference."""
from pathlib import Path
import hashlib
import json
import numpy as np

OUT=Path(__file__).resolve().parent
FOLDER=OUT.parents[2]/'flyvis-3d-studio/activity_replay_20261014'
LOD=FOLDER/'roi_lod_20261015'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
model=json.loads((FOLDER/'model.json').read_text(encoding='utf-8'))
manifest=json.loads((LOD/'manifest.json').read_text(encoding='utf-8'))
sources={r['name']:r for r in model['rois']}
assert len(manifest['rois'])==3
for r in manifest['rois']:
    src=sources[r['name']]
    assert r['source_sha256']==src['sha256']==sha(Path(src['path']))
    derived=LOD/r['derived_file']
    assert r['derived_sha256']==sha(derived)
    with np.load(derived,allow_pickle=False) as z:
        vertices,faces=z['vertices_um'],z['faces']
        assert vertices.shape==(r['derived_vertices'],3) and np.isfinite(vertices).all()
        assert faces.shape==(r['derived_faces'],3) and np.issubdtype(faces.dtype,np.integer)
        assert faces.min()>=0 and faces.max()<len(vertices)
        assert len(faces)<=1200
result=dict(status='PASS_READ_ONLY_GEOMETRY_IDENTITY',background_manifest_sha256=sha(LOD/'manifest.json'),
            source_faces=sum(r['source_faces'] for r in manifest['rois']),
            derived_faces=sum(r['derived_faces'] for r in manifest['rois']),
            derived_vertices=sum(r['derived_vertices'] for r in manifest['rois']),
            background_style='simplified_mesh',rois=manifest['rois'],
            neural_inference_runs=0,board_operations=0)
(OUT/'background_check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='rois'}))
