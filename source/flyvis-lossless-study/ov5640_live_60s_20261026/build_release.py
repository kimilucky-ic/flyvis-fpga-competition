from pathlib import Path
import ast,base64,hashlib,io,json,secrets,uuid,zipfile
P=Path(__file__).resolve().parent;B=P/'bundle'
config_path=P/'pc/session.json'
if config_path.exists():config=json.loads(config_path.read_text())
else:
 config=dict(schema='line11-live-session/v1',session_id=uuid.uuid4().hex,token=secrets.token_hex(32),
  pc_url='http://192.168.2.89:8788',port=8788,camera_width=400,camera_height=240,transfer_mode="live_compact",max_steps=32,minimum_period_s=0,
  bit_sha256='b91abcb6aad7629a9bd85ac306111fa00a9d7ea6467ae5fec70d5af1e29df0a9',
  hwh_sha256='7f60280841ec28570b10cef9ad8a9b9ec5e611cf7036b1b6d198315c45793fff',
  initial_state_sha256=hashlib.sha256((B/'initial_state.bin').read_bytes()).hexdigest())
 config_path.write_text(json.dumps(config,indent=2)+'\n')
files={f.name:f.read_bytes() for f in B.iterdir() if f.is_file() and f.name!='release_manifest.json'}
for n,d in files.items():
 if n.endswith('.py'):ast.parse(d.decode('utf-8-sig'),feature_version=(3,8))
m={n:dict(bytes=len(d),sha256=hashlib.sha256(d).hexdigest()) for n,d in files.items()}
(B/'release_manifest.json').write_text(json.dumps(m,indent=2)+'\n');files['release_manifest.json']=(B/'release_manifest.json').read_bytes()
buf=io.BytesIO()
with zipfile.ZipFile(buf,'w',zipfile.ZIP_DEFLATED) as z:
 for n,d in sorted(files.items()):
  zi=zipfile.ZipInfo(n,(2026,10,26,0,0,0));zi.compress_type=zipfile.ZIP_DEFLATED;z.writestr(zi,d)
raw=buf.getvalue();digest=hashlib.sha256(raw).hexdigest();hashes={n:hashlib.sha256(d).hexdigest() for n,d in files.items()}
(P/'LINE11_OFFICIAL_LIVE_60S_OFFLINE.zip').write_bytes(raw)
code='''import base64,hashlib,io,sys,zipfile
from pathlib import Path
if globals().get('_LINE11_LIVE_USED',False):raise RuntimeError('Already attempted; do not rerun. Keep kernel and records.')
_raw=base64.b64decode(%r)
if hashlib.sha256(_raw).hexdigest()!=%r:raise RuntimeError('Payload mismatch')
_hashes=%r
_root=Path('/home/xilinx/jupyter_notebooks/LINE11_OFFICIAL_LIVE_60S')/('package_'+%r)
_root.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(io.BytesIO(_raw)) as _z:
 if len(_z.namelist())!=len(_hashes) or set(_z.namelist())!=set(_hashes):raise RuntimeError('Unexpected members')
 for _name,_sha in _hashes.items():
  if Path(_name).name!=_name or ':' in _name or '/' in _name or chr(92) in _name:raise RuntimeError('Unsafe member')
  _data=_z.read(_name)
  if hashlib.sha256(_data).hexdigest()!=_sha:raise RuntimeError('Member mismatch')
  _p=_root/_name
  if _p.exists():
   if hashlib.sha256(_p.read_bytes()).hexdigest()!=_sha:raise RuntimeError('Existing file differs')
  else:
   with _p.open('xb') as _f:_f.write(_data)
for _name in _hashes:
 if _name.endswith('.py') and _name[:-3] in sys.modules:raise RuntimeError('Use independent fresh kernel')
sys.path.insert(0,str(_root))
import live_board
if Path(live_board.__file__).resolve()!=(_root/'live_board.py').resolve():raise RuntimeError('Wrong module')
_config=%r
_LINE11_LIVE_USED=True
live_board.run(_root,_config)
'''%(base64.b64encode(raw).decode(),digest,hashes,digest[:12],config)
ast.parse(code,feature_version=(3,8))
md='''# 60秒候选：官方OV5640 + 完整FlyVis

1. 电脑双击 `60_88ae3609.cmd`，保持接收窗口和原显示页打开。
2. 旧相机正常关闭、板卡独占、领航者7020/OV5640接口未变；上传此Notebook，用独立新内核运行唯一代码格。
3. 输出方式选1。程序只读检查空闲内存，打印DDR容量与本次启动速率上限；确认后输入 **运行60秒相机完整网络** 一次。
4. 正式采集循环运行60秒；初始化、最后保存、传输及CPU验收另计。到时完成已经开始的当前帧，不启动下一帧。官方同步驱动仍可能阻塞，因此这不是硬性60秒超时保证。
5. 正常结束看到 `NORMAL_CAMERA_CLOSED`。电脑自动检查每一步721项输入对应的全部45669状态，等待 `PASS_ALL_SAVED_STATES`。计数是实际完成步数，不要求达到1201；1201仅为最高容量。

完整45669节点/1513231连接、严格FP32、100MHz设计和BIT/HWH均沿用通过的R13。80x48灰度直接映射721项、官方相机路径不变；界面暂不改版。最高20步/秒；空闲内存不足时自动限速，确保记录容量覆盖60秒。预检不是连续内存分配保证，分配失败会停止。

每步输入和全部状态都保留，显示可跳旧帧。现有后台记录线程每16步保存一个无压缩批次，不依赖电脑连接、不重复计算；未保存批次掉电或关内核仍会丢失。结束后不再重复生成两个大型ZIP，板端结果目录保留批次与收尾记录，电脑收到逐步完整记录。

异常、断线未收齐或官方调用卡住时保留内核和缓冲区，提供最后输出；不自动复位、重试或释放。不手动重跑同一Notebook。
''' 
nb=dict(nbformat=4,nbformat_minor=4,metadata=dict(kernelspec=dict(display_name='Python 3',language='python',name='python3'),language_info=dict(name='python',version='3.8.0')),cells=[dict(cell_type='markdown',metadata={},source=md.splitlines(True)),dict(cell_type='code',metadata={},source=code.splitlines(True),outputs=[],execution_count=None)])
f=P/'LINE11_OFFICIAL_LIVE_60S.ipynb';f.write_text(json.dumps(nb,ensure_ascii=False),encoding='utf-8')
(P/'DELIVERY.json').write_text(json.dumps(dict(notebook=f.name,notebook_bytes=f.stat().st_size,
 notebook_sha256=hashlib.sha256(f.read_bytes()).hexdigest(),zip_sha256=digest,members=len(files),
 pc_url=config['pc_url'],maximum_steps=config['max_steps'],duration_seconds=60,board_operations=0),indent=2)+'\n')
print(f.name,f.stat().st_size,'members',len(files))
