import hashlib
import importlib.util
import json
import stat
import uuid
import zipfile
from pathlib import Path

base = Path("/home/xilinx/jupyter_notebooks/flyvis_t5c67_v1").resolve()
package = "pynq_v1_single_step_20261011_1620"
archive = base / (package + ".zip")
zip_sha = "e16ddae7e98be753f2d4cb0d07a9204e0932e35a653b3b09f2c90ce030caa4c6"
manifest_sha = "e96537356385fd875fee2c225b5638d4c7deafcbc6669992c6aae7a9837f21ca"

def sha_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

if not archive.is_file() or sha_file(archive) != zip_sha:
    raise RuntimeError("STOP: ZIP missing or SHA256 differs from delivery")

stage = base / ("unpacked_" + uuid.uuid4().hex)
with zipfile.ZipFile(archive) as z:
    members = z.infolist()
    names = [item.filename for item in members]
    if len(names) != 35 or len(set(names)) != 35:
        raise RuntimeError("STOP: unexpected archive member inventory")
    for item in members:
        target = (stage / item.filename).resolve()
        if (not item.filename.startswith(package + "/") or "\\" in item.filename
                or stage not in target.parents
                or stat.S_ISLNK(item.external_attr >> 16)):
            raise RuntimeError("STOP: unsafe archive member")
    stage.mkdir(exist_ok=False)
    z.extractall(stage)

package_dir = stage / package
if sha_file(package_dir / "package_manifest.json") != manifest_sha:
    raise RuntimeError("STOP: package manifest identity differs")

# The reviewed board.py has no PYNQ import or board access at module import.
# Only its file-verification function is called; preflight/review/run-one are not.
spec = importlib.util.spec_from_file_location("_flyvis_v1_filecheck", package_dir / "board.py")
filecheck = importlib.util.module_from_spec(spec)
spec.loader.exec_module(filecheck)
report = filecheck.verify_package()
report.update({"zip_sha256": zip_sha, "package_dir": str(package_dir),
               "board_register_writes": 0, "pl_downloads": 0,
               "hardware_operation_authorized_by_this_cell": False})
record = stage / "unpack_verification.json"
with record.open("x") as stream:
    json.dump(report, stream, indent=2)
print(json.dumps({key: value for key, value in report.items() if key != "files"}, indent=2))
print("PACKAGE_DIR:", package_dir)
print("SAVED:", record)
