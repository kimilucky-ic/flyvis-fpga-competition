"""Read-only before/after hashes of protected 67 sources and sealed package."""
from pathlib import Path
import hashlib,json,argparse
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]
def capture():
    p3=ROOT/'flyvis-fpga/phase3_20261010'; p4=ROOT/'flyvis-fpga/phase4_67_20261010'
    files=[]
    for p in p3.rglob('*'):
        if p.is_file() and 'build' not in p.relative_to(p3).parts and '__pycache__' not in p.parts: files.append(p)
    for p in p4.rglob('*'):
        if p.is_file() and ('build' not in p.relative_to(p4).parts or 'V1_20261010_210347' in p.parts) and '__pycache__' not in p.parts:
            files.append(p)
    # Previously accepted routed resource/timing reports are separately sealed.
    for tag in ('hoc_20261010_190227','rtl_ooc_2026_1_20261010_184604'):
        files.extend((p3/'build'/tag).glob('*.rpt'))
    return {str(p.relative_to(ROOT)).replace('\\','/'):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(set(files))}
ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['before','after']);args=ap.parse_args()
dest=HERE/'artifacts';dest.mkdir(exist_ok=True)
now=capture();(dest/f'protected_{args.mode}.json').write_text(json.dumps(now,indent=2),encoding='utf-8')
if args.mode=='after':
    before=json.loads((dest/'protected_before.json').read_text(encoding='utf-8'))
    changed=[p for p in before.keys()&now.keys() if before[p]!=now[p]]
    deleted=sorted(before.keys()-now.keys()); added=sorted(now.keys()-before.keys())
    sealed=[p for p in before if '/phase3_20261010/' in p or '/build/V1_20261010_210347/' in p or '/pynq/' in p]
    sealed_changed=[p for p in sealed if before[p]!=now.get(p)]
    result={'initial_hashed_files':len(before),'current_hashed_files':len(now),
            'initial_files_unchanged':not changed and not deleted,'changed_initial_files':changed,'deleted_initial_files':deleted,
            'concurrent_new_files_count':len(added),'concurrent_new_files':added,
            'sealed_assets_checked':len(sealed),'sealed_assets_unchanged':not sealed_changed,
            'sealed_assets_differences':sealed_changed,
            'sealed_scope':'phase3 source/ROM/non-build evidence and accepted OOC reports; V1 release including BIT/HWH/XSA; original pynq driver. Active board-preparation gate is separately observed.',
            'scope':'phase3 non-build files, accepted OOC reports, phase4_67 non-build files and V1 sealed release; not all tool caches'}
    (dest/'protected_audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='concurrent_new_files'}))
else: print(json.dumps({'protected_files':len(now),'total_bytes':sum(v['bytes'] for v in now.values())}))
