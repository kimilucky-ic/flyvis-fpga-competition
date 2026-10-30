import ast
import json
import hashlib
import uuid
from pathlib import Path
from importlib.metadata import distribution

dist = distribution("pynq")
targets = {
    "pynq/overlay.py": {"Overlay": ("init__", "download")},
    "pynq/bitstream.py": {"Bitstream": ("download",)},
    "pynq/pl_server/embedded_device.py": {
        "EmbeddedDevice": ("download", "set_axi_port_width", "allocate")},
    "pynq/buffer.py": {
        "PynqBuffer": ("flush", "invalidate", "freebuffer"),
        "MODULE": ("allocate",)},
}
sources = {"pynq_version": dist.version, "files": {},
           "scope": "FILE_READS_ONLY_NO_PYNQ_IMPORT_OR_DOWNLOAD"}
for relative, classes in targets.items():
    path = Path(dist.locate_file(relative))
    raw = path.read_bytes()
    text = raw.decode("utf-8")
    sources["files"][relative] = {
        "path": str(path), "sha256": hashlib.sha256(raw).hexdigest(),
        "text": text,
    }
    tree = ast.parse(text)
    for node in tree.body:
        owner = node.name if isinstance(node, ast.ClassDef) else "MODULE"
        members = node.body if isinstance(node, ast.ClassDef) else [node]
        for member in members:
            if isinstance(member, ast.FunctionDef) and member.name in classes.get(owner, ()):
                print("\nSOURCE:", relative, owner + "." + member.name)
                print(ast.get_source_segment(text, member))

record = Path("runtime_sources_" + uuid.uuid4().hex[:8] + ".json")
with record.open("x") as stream:
    json.dump(sources, stream, indent=2)
print("\nSaved:", record)
print("PYNQ:", dist.version, "SOURCE_FILES:", len(sources["files"]))
