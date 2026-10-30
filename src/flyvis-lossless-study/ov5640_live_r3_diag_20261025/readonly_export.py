# Only reads this run's saved files and writes a separate evidence ZIP.
# No PYNQ, camera, overlay, MMIO, reset, STEP, or buffer operations.
from pathlib import Path
import hashlib,json,os,shutil,time,uuid,zipfile
run_id='RUN_dcd2298f2d084619be2b202d457f23db'
base=Path('/home/xilinx/jupyter_notebooks/LINE11_OFFICIAL_LIVE_R3')
root=base/run_id
if not root.is_dir():raise RuntimeError('Expected R3 run directory not found; do not choose another run')
context=json.loads((root/'RUN_CONTEXT.json').read_text())
if context.get('run_id')!=run_id:raise RuntimeError('Run identity mismatch')
files=sorted(p for p in root.rglob('*') if p.is_file())
if any(p.is_symlink() or root.resolve() not in p.resolve().parents for p in files):raise RuntimeError('Unexpected linked file')
total=sum(p.stat().st_size for p in files)
if total>160*1024*1024:raise RuntimeError('Unexpected result size; stop export')
if shutil.disk_usage(str(base)).free<total+16*1024*1024:raise RuntimeError('Insufficient free space for read-only export')
output=base/(run_id+'_READONLY_'+uuid.uuid4().hex[:8]+'.zip')
partial=output.with_suffix('.zip.partial')
manifest=[]
with zipfile.ZipFile(str(partial),'x',compression=zipfile.ZIP_STORED) as archive:
    for p in files:
        before=p.stat();data=p.read_bytes();after=p.stat();name=p.relative_to(root).as_posix()
        archive.writestr(name,data)
        manifest.append(dict(name=name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),
            stable_during_read=before.st_size==after.st_size and before.st_mtime_ns==after.st_mtime_ns))
    status=dict(evidence='READ_ONLY_SAVED_FILE_EXPORT_NOT_BOARD_CONTROL_OR_RUN_PASS',run_id=run_id,
        export_unix=time.time(),hardware_operations=0,original_kernel_untouched=True,
        result_file_present=(root/'RESULT.json').exists(),finish_file_present=(root/'FINISH.json').exists(),
        transfer_file_present=(root/'TRANSFER.json').exists(),files=manifest)
    archive.writestr('READ_ONLY_EXPORT.json',json.dumps(status,indent=2))
os.rename(str(partial),str(output))
print('LINE11_R3_READONLY_RESULT',output)
print('RESULT_EXISTS',status['result_file_present'],'FINISH_EXISTS',status['finish_file_present'],'TRANSFER_EXISTS',status['transfer_file_present'])
print('只导出了保存文件，没有相机/MMIO/STEP/复位操作。请下载这个ZIP交回；保留原R3内核，不重跑原实验。')
