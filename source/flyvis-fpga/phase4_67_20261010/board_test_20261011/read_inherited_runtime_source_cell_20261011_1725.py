import ast
import json
import hashlib
import uuid
from pathlib import Path
from importlib.metadata import distribution

dist = distribution("pynq")
targets = {
    "pynq/pl_server/device.py": "Device",
    "pynq/pl_server/xrt_device.py": "XrtDevice",
    "pynq/pl_server/embedded_device.py": "EmbeddedDevice",
}
record = {"scope": "SOURCE_FILE_READS_ONLY_NO_PYNQ_IMPORT_OR_METHOD_CALL",
          "pynq_version": dist.version,
          "boot_id": Path("/proc/sys/kernel/random/boot_id").read_text().strip(),
          "files": {}}
for relative, owner in targets.items():
    path = Path(dist.locate_file(relative))
    raw = path.read_bytes()
    source = raw.decode("utf-8")
    digest = hashlib.sha256(raw).hexdigest()
    print("\nFILE:", relative, "SHA256:", digest)
    record["files"][relative] = {"path": str(path), "sha256": digest,
                                 "text": source}
    for node in ast.parse(source).body:
        if isinstance(node, ast.ClassDef) and node.name == owner:
            print("CLASS:", owner, "BASES:",
                  [ast.get_source_segment(source, base) for base in node.bases])
            for member in node.body:
                if isinstance(member, ast.FunctionDef) and member.name in (
                        "shutdown", "post_download", "allocate"):
                    print("source:", owner + "." + member.name)
                    print(ast.get_source_segment(source, member))
output = Path("runtime_inherited_" + uuid.uuid4().hex[:8] + ".json")
with output.open("x") as stream:
    json.dump(record, stream, indent=2)
print("\nSaved:", output, "BOOT_ID:", record["boot_id"])
print("SOURCE_FILES:", len(record["files"]), "BOARD_REGISTER_WRITES: 0")
