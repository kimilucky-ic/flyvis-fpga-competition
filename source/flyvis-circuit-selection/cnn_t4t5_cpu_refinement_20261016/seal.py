"""Hash current delivery once; no neural computation or training."""
from pathlib import Path
import ast, hashlib, json

HERE = Path(__file__).resolve().parent

def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()

if __name__ == '__main__':
    target = HERE / 'DELIVERY_MANIFEST.json'
    assert not target.exists(), 'Do not overwrite sealed delivery'
    sources = list(HERE.glob('*.py'))
    for path in sources:
        ast.parse(path.read_text(encoding='utf-8-sig'), filename=str(path))
    rows = []
    for path in sorted(HERE.rglob('*')):
        if not path.is_file() or any(part in ('runtime', '__pycache__') for part in path.relative_to(HERE).parts):
            continue
        rows.append(dict(path=path.relative_to(HERE).as_posix(), bytes=path.stat().st_size, sha256=sha(path)))
    result = dict(schema='delivery-sha256/v1', file_count=len(rows), bytes=sum(r['bytes'] for r in rows),
        scientific_result='PASS_FIXED_HOLDOUT_FUNCTIONAL_GATE', audit='PASS_SAVED_STATES_AND_FROZEN_GATE',
        syntax_checked_sources=len(sources), additional_neural_steps=0, GPU=0, board=0,
        exclusions=['DELIVERY_MANIFEST.json (self)', 'runtime', '__pycache__'], files=rows)
    with target.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
    print(json.dumps(dict(files=len(rows), bytes=result['bytes'], GiB=result['bytes']/2**30,
        manifest_sha256=sha(target), syntax_checked=len(sources), new_neural_steps=0)))
