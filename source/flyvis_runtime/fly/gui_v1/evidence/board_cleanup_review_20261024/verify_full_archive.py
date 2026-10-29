import hashlib,json,shutil,sys,zipfile
from pathlib import Path
name,digest=sys.argv[1:3]
assert name.startswith('LINE11_DDR_') and len(name)==43
archive='FULL_BACKUP_'+name+'_20261024.zip'
src=Path(r'C:\Users\hzy72\Downloads')/archive
root=Path(r'C:\Users\hzy72\Documents\ChatGPT\fpga\flyvis_runtime\fly\gui_v1\evidence\board_cleanup_review_20261024')
dest=root/'FULL_DDR_ARCHIVES';dest.mkdir(exist_ok=True)
assert hashlib.sha256(src.read_bytes()).hexdigest()==digest,'Source archive SHA mismatch'
with zipfile.ZipFile(src) as z:
 assert z.testzip() is None,'CRC error'
 m=json.loads(z.read('BACKUP_MANIFEST.json'));assert m['directory']==name
 names=z.namelist();assert len(names)==len(set(names))
 assert len(m['files'])==len([n for n in names if n!='BACKUP_MANIFEST.json' and not n.endswith('/')])
 for f in m['files']:
  assert f['path'].startswith(name+'/') or f['path']==name+'.zip'
  data=z.read(f['path']);assert len(data)==f['bytes'] and hashlib.sha256(data).hexdigest()==f['sha256']
 original_bytes=sum(f['bytes'] for f in m['files'])
 target=dest/archive
 if target.exists():assert hashlib.sha256(target.read_bytes()).hexdigest()==digest
 else:shutil.copy2(src,target)
 assert hashlib.sha256(target.read_bytes()).hexdigest()==digest
 receipt=dict(directory=name,backup=str(target),sha256=digest,archive_bytes=src.stat().st_size,files=len(m['files']),original_bytes=original_bytes,status='SOURCE_SHA_AND_ALL_ARCHIVE_MEMBERS_VERIFIED')
 receipts=root/'FULL_ARCHIVE_VERIFICATION.json';rows=json.loads(receipts.read_text(encoding='utf-8')) if receipts.exists() else [];rows=[r for r in rows if r['directory']!=name];rows.append(receipt);receipts.write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(receipt,ensure_ascii=False))
