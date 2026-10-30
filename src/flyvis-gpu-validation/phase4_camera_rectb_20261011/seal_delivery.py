"""CPU-only final file seal, including immutable nested manifests and report."""
import json
from pathlib import Path
from run_camera_full import HERE, load, dump, digest, verify_bundle

binding=verify_bundle()
assert load(HERE/"DELIVERY_ACCEPTANCE.json")["status"]=="PASS_A_RECORDED_CAMERA_FULL_GPU_REFERENCE"
for run in ["full_gpu_609_r1","full_gpu_609_r2"]:
    root=HERE/"artifacts"/run
    for name, expected in load(root/"artifact_manifest.json")["files"].items():
        assert digest(root/name)==expected,name
entries=[dict(path=p.relative_to(HERE).as_posix(),bytes=p.stat().st_size,sha256=digest(p))
         for p in sorted(HERE.rglob("*")) if p.is_file() and p.name!="DELIVERY_MANIFEST.json"
         and "__pycache__" not in p.parts]
dump(HERE/"DELIVERY_MANIFEST.json",dict(schema="camera-full-delivery-seal/v1",
     comparison_id=binding["comparison_id"],backend_binding_id=binding["backend_binding_id"],
     scope="A original Full GPU + common bundle + independent replay + actual activity plots/report",
     files=entries))
for entry in entries:
    assert digest(HERE/entry["path"])==entry["sha256"],entry["path"]
print(json.dumps(dict(status="PASS_FINAL_DELIVERY_FILE_SEAL",files=len(entries),
     manifest_sha256=digest(HERE/"DELIVERY_MANIFEST.json"),board_used=False)))
