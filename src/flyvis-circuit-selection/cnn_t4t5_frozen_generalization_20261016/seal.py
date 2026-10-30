"""Final file SHA seal. Never run neural inference or repeat an experiment."""
from pathlib import Path
import hashlib, json, ast

HERE = Path(__file__).resolve().parent

def sha(path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(8*1024**2), b''): result.update(block)
    return result.hexdigest()

if __name__ == '__main__':
    target = HERE/'DELIVERY_MANIFEST.json'; assert not target.exists()
    for p in HERE.glob('*.py'): ast.parse(p.read_text(encoding='utf-8-sig'))
    audit = json.loads((HERE/'FINAL_AUDIT.json').read_text(encoding='utf-8'))
    assert audit['status'] == 'PASS_SAVED_VALID_PREFIX_AND_FROZEN_IDENTITY'
    records = []
    for p in sorted(HERE.rglob('*')):
        if p.is_file() and not any(x in ('runtime', '__pycache__') for x in p.relative_to(HERE).parts):
            records.append(dict(path=p.relative_to(HERE).as_posix(), bytes=p.stat().st_size, sha256=sha(p)))
    data = dict(schema='file-SHA256/v1', files=records, file_count=len(records), bytes=sum(r['bytes'] for r in records),
        audit=audit['status'], functional_status=audit['functional_status'], neural_steps_in_seal=0, GPU=0, board=0,
        excludes=['DELIVERY_MANIFEST.json(self)', 'runtime', '__pycache__'])
    with target.open('x', encoding='utf-8') as stream: json.dump(data, stream, ensure_ascii=False, indent=2)
    print(json.dumps(dict(files=data['file_count'], bytes=data['bytes'], GiB=data['bytes']/2**30, manifest_sha=sha(target))))
