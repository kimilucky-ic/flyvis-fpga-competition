"""Preserve exact accepted implementation copies and write portable manifests."""
from pathlib import Path
import argparse, json, shutil
from h_step import file_hash

HERE=Path(__file__).resolve().parent


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('runs',nargs='+')
    args=parser.parse_args()
    for run in args.runs:
        directory=HERE/'artifacts'/run
        assert directory.is_dir()
        identity=directory/'run_identity.json'
        if identity.exists():
            meta=json.loads(identity.read_text())
            source=meta.get('code_sha256',{})
            dependencies=meta.get('A_snapshot_sha256',{})
        else:
            meta=json.loads((directory/'result.json').read_text())
            source={}
            dependencies={}
            if 'code_sha256' in meta:
                if isinstance(meta['code_sha256'],dict):
                    source=meta['code_sha256']
                else:
                    assert run.startswith('live_feedback')
                    source={'verify_live_feedback.py':meta['code_sha256'],**meta.get('dependency_sha256',{})}
                    if 'A_r_only_sha256' in meta:dependencies={'r_only.py':meta['A_r_only_sha256']}
        if source:
            copied=directory/'code_snapshot'
            copied.mkdir(exist_ok=True)
            for name,digest in source.items():
                assert file_hash(HERE/name)==digest
                target=copied/name
                if target.exists():assert file_hash(target)==digest
                else:shutil.copyfile(HERE/name,target)
            for name,digest in dependencies.items():
                target=copied/('A_'+name)
                assert file_hash(HERE/'dependencies/a_snapshot'/name)==digest
                if target.exists():assert file_hash(target)==digest
                else:shutil.copyfile(HERE/'dependencies/a_snapshot'/name,target)
        manifest=[dict(path=p.relative_to(directory).as_posix(),bytes=p.stat().st_size,sha256=file_hash(p))
            for p in sorted(directory.rglob('*')) if p.is_file() and p.name!='artifact_manifest.json']
        (directory/'artifact_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
        print(json.dumps(dict(run=run,files=len(manifest))),flush=True)


if __name__=='__main__':main()
