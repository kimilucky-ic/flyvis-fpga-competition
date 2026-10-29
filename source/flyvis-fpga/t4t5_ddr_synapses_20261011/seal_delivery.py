"""Seal the exact first-milestone source, vectors and accepted raw evidence.

No generated XSim cache/binaries, no external workstream files, no publication.
All hashes are re-read after manifest creation; local Markdown links checked.
"""
from pathlib import Path
import json,hashlib,re
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    report=json.loads((HERE/'RTL_STREAM_SMALL_PASS.json').read_text())
    files=[]
    files.extend(p for p in HERE.iterdir() if p.is_file() and p.suffix in ('.py','.ps1','.md','.json') and p.name not in ('MANIFEST_SHA256.json','DELIVERY_VERIFICATION.json'))
    for folder in ('rtl','fixtures','stage2_format'):
        files.extend(p for p in (HERE/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    for run in report['simulations']:
        files.extend(HERE/run['path']/p for p in run['files'])
    for run in report['excluded_runs']:
        files.extend(p for n in ('RUN_IDENTITY.json','xvlog.log','xelab.log','xsim.log') if (p:=HERE/run['path']/n).is_file())
    entries={p.relative_to(HERE).as_posix():dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(set(files))}
    manifest=dict(algorithm='SHA256',scope='Exact B first-milestone source/fixtures/accepted CSV and logs; failed-run logs retained; no tool cache',files=entries)
    mp=HERE/'MANIFEST_SHA256.json';mp.write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    reloaded=json.loads(mp.read_text());verified=0
    for p,v in reloaded['files'].items():
        f=HERE/p;assert f.stat().st_size==v['bytes'] and sha(f)==v['sha256'];verified+=1
    links=0
    docs=list(HERE.glob('*.md'))+[HERE.parents[1]/'docs/workstreams/flyvis-t4t5-ddr-hardware-b.md']
    for doc in docs:
        for link in re.findall(r'\]\(([^)]+)\)',doc.read_text(encoding='utf-8')):
            if '://' in link or link.startswith('#'):continue
            target=(doc.parent/link.split('#')[0]).resolve()
            assert target.exists(),f'Missing report link: {doc.name}: {link}'
            links+=1
    out=dict(status='PASS_LOCAL_DELIVERY_SEAL',manifest_sha256=sha(mp),verified_files=verified,local_links_verified=links,
        checkpoint_sha256=sha(docs[-1]),published=False,committed=False,board_io=0,
        bytes=sum(v['bytes'] for v in entries.values()))
    (HERE/'DELIVERY_VERIFICATION.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps(out))
if __name__=='__main__':main()
