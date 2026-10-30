"""Local-only reception of browser downloads. Never connects to the board."""
import argparse,hashlib,json,re,shutil,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
DOWNLOADS=Path(r'C:\Users\hzy72\Downloads')
DEST=ROOT/'board_results_backup'
def snapshot():
    return {p.name:[p.stat().st_size,p.stat().st_mtime_ns] for p in DOWNLOADS.iterdir() if p.is_file()}
def main():
    p=argparse.ArgumentParser();p.add_argument('op',choices=['before','receive']);p.add_argument('folder');p.add_argument('names',nargs='*');a=p.parse_args()
    rel=Path(a.folder)
    if rel.is_absolute() or '..' in rel.parts:raise ValueError('Unsafe backup path')
    state=ROOT/'download_before.json'
    if a.op=='before':state.write_text(json.dumps({'folder':a.folder,'files':snapshot()}),encoding='utf-8');return
    before=json.loads(state.read_text(encoding='utf-8'));assert before['folder']==a.folder
    for attempt in range(30):
        now=snapshot();changed=[DOWNLOADS/n for n,v in now.items() if before['files'].get(n)!=v and not n.endswith(('.crdownload','.tmp'))];chosen={}
        for name in a.names:
            stem,suffix=Path(name).stem,Path(name).suffix
            match=[f for f in changed if f.name==name or re.fullmatch(re.escape(stem)+r' \(\d+\)'+re.escape(suffix),f.name)]
            if len(match)>1:raise RuntimeError('Ambiguous download '+name)
            if match:chosen[name]=match[0]
        if len(chosen)==len(a.names):break
        time.sleep(.2)
    if len(chosen)!=len(a.names):raise RuntimeError('Missing '+str(set(a.names)-set(chosen)))
    target=DEST/rel;target.mkdir(parents=True,exist_ok=True);records=[]
    for name,src in chosen.items():
        data=src.read_bytes();assert data,'Empty download '+name
        if name.endswith('.json'):json.loads(data.decode('utf-8-sig'))
        digest=hashlib.sha256(data).hexdigest();dst=target/name
        if dst.exists():assert hashlib.sha256(dst.read_bytes()).hexdigest()==digest
        else:shutil.copy2(src,dst)
        assert hashlib.sha256(dst.read_bytes()).hexdigest()==digest
        records.append({'remote_relative_path':str(rel/name).replace('\\','/'),'download':str(src),'backup':str(dst),'bytes':len(data),'sha256':digest})
    manifest=ROOT/'DOWNLOADED_FILES.json';old=json.loads(manifest.read_text(encoding='utf-8')) if manifest.exists() else [];old.extend(records);manifest.write_text(json.dumps(old,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'folder':a.folder,'files':len(records),'bytes':sum(r['bytes'] for r in records)},ensure_ascii=False))
if __name__=='__main__':main()
