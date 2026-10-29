"""Read-only final package review; never execute notebook or start a process/socket."""
import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
NOTEBOOK = ROOT / "FlyVis摄像头联合实验.ipynb"
MANIFEST = ROOT / "evidence/fixed_camera_one_minute_20261018/VERIFICATION.json"

def sha(data):
    return hashlib.sha256(data).hexdigest()

def main():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    nb = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    cells = [cell for cell in nb["cells"] if cell["cell_type"] == "code"]
    assert len(cells) == 1, "Expected one operator code cell"
    ast.parse("".join(cells[0]["source"]), feature_version=(3, 8))
    entry = nb["metadata"]["flyvis_fixed_entry"]
    ast.parse(entry["source"], feature_version=(3, 8))
    assert sha(entry["source"].encode()) == entry["source_sha256"]
    assert entry["source"] == (ROOT / "joint_camera_fixed_board.py").read_text(encoding="utf-8")
    private = json.loads((ROOT / "runtime/fixed_camera/INSTALLATION_PRIVATE.json").read_text(encoding="utf-8"))
    assert entry["config"] == private, "PC and fixed notebook pairing differ"
    mismatches = []
    for item in manifest["files"]:
        path = Path(item["path"])
        if not path.is_file() or sha(path.read_bytes()) != item["sha256"]:
            mismatches.append(str(path))
    assert not mismatches, "Delivery changed after manifest: " + repr(mismatches)
    desktop = manifest["original_desktop_entry"]
    assert desktop["default"] == "ORIGINAL_JOINT_CONTROLLER_FIXED_NOTEBOOK_60S"
    assert desktop["verification"]["processes_started"] == 0
    assert manifest["unused_notebook_pairing_rotated_before_delivery"] is True
    result = dict(
        status="PASS_READ_ONLY_FINAL_PACKAGE_REVIEW",
        evidence_level="SOURCE_HASH_AND_PYTHON38_SYNTAX_ONLY",
        notebook_sha256=sha(NOTEBOOK.read_bytes()),
        manifest_sha256=sha(MANIFEST.read_bytes()),
        manifest_files_verified=len(manifest["files"]),
        single_code_cell=True,
        installation_matches_PC=True,
        embedded_client_matches_current=True,
        unused_pairing_rotation_recorded=True,
        original_desktop_entry=desktop["path"],
        notebook_executed=False,
        GUI_GPU_camera_board_launches=0,
        actual_60s_camera_GPU_FPGA="NOT_TESTED_THIS_REVIEW",
    )
    (OUT / "NOTEBOOK_REVIEW.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()
