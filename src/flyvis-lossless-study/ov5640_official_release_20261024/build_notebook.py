"""Build an inert offline ZIP and one self-contained operator Notebook."""
from pathlib import Path
import ast,base64,hashlib,io,json,zipfile
P=Path(__file__).resolve().parent;B=P/'bundle'
files={f.name:f.read_bytes() for f in B.iterdir() if f.is_file() and f.name!='release_manifest.json'}
for n,d in files.items():
 if n.endswith('.py'):ast.parse(d.decode('utf-8-sig'),feature_version=(3,8))
m={n:dict(bytes=len(d),sha256=hashlib.sha256(d).hexdigest()) for n,d in files.items()}
(B/'release_manifest.json').write_text(json.dumps(m,indent=2)+'\n')
files['release_manifest.json']=(B/'release_manifest.json').read_bytes()
buf=io.BytesIO()
with zipfile.ZipFile(buf,'w',zipfile.ZIP_DEFLATED) as z:
 for n,d in sorted(files.items()):z.writestr(n,d)
raw=buf.getvalue();sha=hashlib.sha256(raw).hexdigest();hashes={n:hashlib.sha256(d).hexdigest() for n,d in files.items()}
(P/'LINE11_OFFICIAL_FULL_20261024_OFFLINE.zip').write_bytes(raw)
code='''import base64,hashlib,io,sys,zipfile
from pathlib import Path
if globals().get('_LINE11_OFFICIAL_USED',False):raise RuntimeError('Already attempted; keep kernel/results, no repeat')
_raw=base64.b64decode(%r)
if hashlib.sha256(_raw).hexdigest()!=%r:raise RuntimeError('Payload hash mismatch; no hardware actions')
_hashes=%r
_root=Path('/home/xilinx/jupyter_notebooks/LINE11_OFFICIAL_FULL_20261024')/('package_'+%r)
_root.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(io.BytesIO(_raw)) as _z:
 if len(_z.namelist())!=len(_hashes) or set(_z.namelist())!=set(_hashes):raise RuntimeError('Unexpected ZIP members')
 for _name,_sha in _hashes.items():
  if Path(_name).name!=_name or ':' in _name or '/' in _name or chr(92) in _name:raise RuntimeError('Unsafe member')
  _data=_z.read(_name)
  if hashlib.sha256(_data).hexdigest()!=_sha:raise RuntimeError('Member hash mismatch')
  _p=_root/_name
  if _p.exists():
   if hashlib.sha256(_p.read_bytes()).hexdigest()!=_sha:raise RuntimeError('Existing file differs; no overwrite')
  else:
   with _p.open('xb') as _f:_f.write(_data)
for _name in _hashes:
 if _name.endswith('.py') and _name[:-3] in sys.modules:raise RuntimeError('Use this Notebook with its own fresh kernel')
sys.path.insert(0,str(_root))
import operator_entry
if Path(operator_entry.__file__).resolve()!=(_root/'operator_entry.py').resolve():raise RuntimeError('Wrong entry module')
_LINE11_OFFICIAL_USED=True
operator_entry.run(_root)
'''%(base64.b64encode(raw).decode(),sha,hashes,sha[:12])
ast.parse(code,feature_version=(3,8))
md='''# 官方 OV5640 + 完整 FlyVis：单帧、一步、全状态记录

保留45669节点、1513231连接、严格FP32及100MHz设计。此新固件尚未实板验收。

1. 确保此前官方摄像头已正常关闭、板卡独占、同一领航者7020和OV5640接口未变。原电脑摄像头/动画不需启动或更改。
2. 本Notebook使用独立新内核，选中下面唯一代码格，按Shift+Enter。无需先加载固件或运行旧Notebook。
3. 提示时输入 **运行官方完整网络**。这一次确认授权加载新BIT、检查时钟/接口、初始化相机、采一帧、生成721项输入、PL算一步并保存全部45669状态。
4. 显示 `ONE_FRAME_ONE_STEP_SAVED_ORACLE_PENDING` 后，下载打印的 `LINE11_OFFICIAL_FULL_20261024/RUN_…_RESULT.zip` 交回电脑核查。网页图片只是保存帧的预览。

**先保留内核和缓冲区，不重复运行、不复位、不加载其他工程。** 出错也下载结果ZIP；若阻塞/没有ZIP，提供最后完整输出，不自行重试。官方同步驱动可能阻塞，未承诺可自动中止。

数值PASS由电脑侧严格FP32参考程序比较全部状态后给出。物理时钟、颜色顺序、外部时序及本版ARM/DDR路径仍待实板核实。包内Windows参考程序不会在ARM板上执行。只使用本文件即可，不用另传BIT、HWH或ZIP。
'''
nb=dict(nbformat=4,nbformat_minor=4,metadata=dict(kernelspec=dict(display_name='Python 3',language='python',name='python3'),language_info=dict(name='python',version='3.8.0')),cells=[dict(cell_type='markdown',metadata={},source=md.splitlines(True)),dict(cell_type='code',metadata={},source=code.splitlines(True),outputs=[],execution_count=None)])
f=P/'LINE11_OFFICIAL_FULL_20261024.ipynb';f.write_text(json.dumps(nb,ensure_ascii=False),encoding='utf-8')
(P/'DELIVERY.json').write_text(json.dumps(dict(status='OFFLINE_CANDIDATE_CPU_VERIFICATION_PENDING',notebook=f.name,notebook_bytes=f.stat().st_size,notebook_sha256=hashlib.sha256(f.read_bytes()).hexdigest(),zip_sha256=sha,members=len(files),board_operations=0),indent=2)+'\n')
print(f.name,f.stat().st_size,sha)
