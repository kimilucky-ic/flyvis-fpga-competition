"""Read-only dependency closure and one final SHA seal; no neural imports."""
from pathlib import Path
import json,hashlib,ast

HERE=Path(__file__).resolve().parent

def sha(path):
    value=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(8*1024**2),b''): value.update(block)
    return value.hexdigest()


if __name__=='__main__':
    target=HERE/'DELIVERY_MANIFEST.json'; assert not target.exists()
    load=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
    audit=load(HERE/'FINAL_AUDIT.json'); video=load(HERE/'VIDEO_INPUT_AUDIT.json')
    assert audit['status']=='PASS_SAVED_VALID_PREFIX_AND_FROZEN_IDENTITY'
    assert video['status']=='PASS_ACTUAL_VIDEO_TO_COMMON_INPUT'
    registrations=[HERE/'PREREGISTRATION.json']; visited=set(); verified={}
    while registrations:
        path=registrations.pop()
        if path in visited: continue
        visited.add(path)
        for name,record in load(path)['pins'].items():
            file=Path(name); expected=record['sha256'] if isinstance(record,dict) else record
            if file not in verified: verified[file]=sha(file)
            assert verified[file]==expected,str(file)
            if isinstance(record,dict):
                assert file.stat().st_size==record['bytes'] and file.stat().st_mtime_ns==record['mtime_ns']
            if file.name=='PREREGISTRATION.json': registrations.append(file)
    with (HERE/'SOURCE_CLOSURE_AUDIT.json').open('x',encoding='utf-8') as stream:
        json.dump(dict(status='PASS_TRANSITIVE_READ_ONLY_DEPENDENCIES',registrations=len(visited),
            unique_files_verified=len(verified),new_neural_steps=0,GPU=0,board=0),stream,indent=2)
    for path in HERE.glob('*.py'): ast.parse(path.read_text(encoding='utf-8-sig'))
    files=[]
    for path in sorted(HERE.rglob('*')):
        if path.is_file() and not any(x in ('runtime','__pycache__') for x in path.relative_to(HERE).parts):
            files.append(dict(path=path.relative_to(HERE).as_posix(),bytes=path.stat().st_size,sha256=sha(path)))
    result=dict(schema='file-SHA256/v1',file_count=len(files),bytes=sum(z['bytes'] for z in files),files=files,
        functional_status=audit['functional_status'],state_audit=audit['status'],video_audit=video['status'],
        source_closure='PASS_TRANSITIVE_READ_ONLY_DEPENDENCIES',neural_steps_in_seal=0,GPU=0,board=0,
        excludes=['DELIVERY_MANIFEST.json(self)','runtime','__pycache__'])
    with target.open('x',encoding='utf-8') as stream: json.dump(result,stream,ensure_ascii=False,indent=2)
    print(json.dumps(dict(files=result['file_count'],bytes=result['bytes'],GiB=result['bytes']/2**30,
        manifest_sha=sha(target),transitive_files=len(verified))))
