import json,hashlib,ast,base64,zipfile,io
from pathlib import Path
P=Path(__file__).resolve().parent;B=P/'bundle'
info=dict(revision='LINE11_SINGLE_R2',transport_revision='IIC21_R2',source='copied conditional single-frame release; only isolated candidate files changed',prior_id_acceptance=json.loads((P/'ID_ACCEPTANCE.json').read_text()),board_execution_by_agent=0,full_state_acceptance='PENDING_REAL_CAPTURE')
(B/'SINGLE_R2_INFO.json').write_text(json.dumps(info,indent=2),encoding='utf-8')
files={f.name:f.read_bytes() for f in B.iterdir() if f.is_file() and f.name!='release_manifest.json'}
manifest={n:dict(bytes=len(v),sha256=hashlib.sha256(v).hexdigest()) for n,v in files.items()}
(B/'release_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
files['release_manifest.json']=(B/'release_manifest.json').read_bytes()
for name,data in files.items():
 if name.endswith('.py'):ast.parse(data.decode('utf-8-sig'),feature_version=(3,8))
buf=io.BytesIO()
with zipfile.ZipFile(buf,'w',zipfile.ZIP_DEFLATED) as z:
 for n,v in sorted(files.items()):z.writestr(n,v)
raw=buf.getvalue();sha=hashlib.sha256(raw).hexdigest();hashes={n:hashlib.sha256(v).hexdigest() for n,v in files.items()}
(P/'single_r2_payload.zip').write_bytes(raw)
code='''import base64,hashlib,io,sys,zipfile
from pathlib import Path
if globals().get('_LINE11_SINGLE_R2_USED',False):raise RuntimeError('Already used; preserve results/kernel, no retry')
_raw=base64.b64decode(%r)
if hashlib.sha256(_raw).hexdigest()!=%r:raise RuntimeError('Corrupt payload; no hardware actions')
_hashes=%r
_root=Path('/home/xilinx/jupyter_notebooks/LINE11_OV5640_SINGLE_R2')/('package_'+%r)
_root.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(io.BytesIO(_raw)) as _z:
 if len(_z.namelist())!=len(_hashes) or set(_z.namelist())!=set(_hashes):raise RuntimeError('Unexpected members')
 for _name,_sha in _hashes.items():
  _data=_z.read(_name)
  if hashlib.sha256(_data).hexdigest()!=_sha:raise RuntimeError('Member mismatch')
  _p=_root/_name
  if _p.exists():
   if hashlib.sha256(_p.read_bytes()).hexdigest()!=_sha:raise RuntimeError('Existing file differs; no overwrite')
  else:
   with _p.open('xb') as _f:_f.write(_data)
for _name in _hashes:
 if _name.endswith('.py') and _name[:-3] in sys.modules:raise RuntimeError('Old modules loaded; use this new Notebook in its own fresh kernel')
sys.path.insert(0,str(_root))
import operator_entry
if Path(operator_entry.__file__).resolve()!=(_root/'operator_entry.py').resolve():raise RuntimeError('Wrong entry import')
_LINE11_SINGLE_R2_USED=True
operator_entry.run(_root)
'''%(base64.b64encode(raw).decode(),sha,hashes,sha[:12])
ast.parse(code,feature_version=(3,8))
md='''# OV5640 单帧与完整网络一步 · IIC2.1 修正版

只运行此新文件的唯一代码格，不运行旧单帧Notebook，也不打开电脑实验台。已核查型号0x5640；本次采图和神经状态尚未实板验收。

1. 保留板卡当前状态，确认领航者7020 V3.9/ATK-MC5640连接未变、没有其他程序操作板卡。
2. 点击下方代码格，Shift+Enter，提示时输入 **同意单帧测试**。
3. 此确认授权加载原固件一次、执行相机初始化、分配缓冲区、采一帧、生成721项输入并计算一步。无需先重启整板。
4. 下载打印出的 `LINE11_OV5640_SINGLE_R2/LINE11_OV5640_…_RESULT.zip` 交回。完成消息只表示记录保存，全部45669状态等待电脑独立验收。

原BIT/HWH/完整网络/严格FP32/100MHz设计不变。条件性功能测试：物理时钟与外部电气波形尚未实测，BGR通道顺序尚未色条确认。不承诺实时帧率。

成功或失败均保留此Notebook内核和板上缓冲区；不要重复运行、重启/关闭内核、复位或继续其他实验。错误有ZIP交ZIP，无ZIP交最后完整输出。没有自动重试、自动恢复或自动释放。
'''
nb=dict(nbformat=4,nbformat_minor=4,metadata=dict(kernelspec=dict(display_name='Python 3',language='python',name='python3'),language_info=dict(name='python',version='3.8.0')),cells=[dict(cell_type='markdown',metadata={},source=md.splitlines(True)),dict(cell_type='code',metadata={},source=code.splitlines(True),execution_count=None,outputs=[])])
f=P/'OV5640_SINGLE_FRAME_R2_20261024.ipynb';f.write_text(json.dumps(nb,ensure_ascii=False),encoding='utf-8')
old=json.loads((P/'BASELINE.json').read_text());changed=[n for n,h in old.items() if n not in files or hashlib.sha256(files[n]).hexdigest()!=h]
(P/'DELIVERY.json').write_text(json.dumps(dict(status='OFFLINE_CANDIDATE_BOARD_CAPTURE_PENDING',notebook=str(f.resolve()),bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest(),payload_sha256=sha,members=len(files),changed_baseline_members=changed,bit_sha256=hashes['flyvis_ov5640.bit'],hwh_sha256=hashes['flyvis_ov5640.hwh'],board_operations=0,GPU_operations=0,Vivado_operations=0),indent=2))
print(f.resolve(),f.stat().st_size,'CHANGED',changed)
