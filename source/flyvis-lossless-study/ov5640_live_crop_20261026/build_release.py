from pathlib import Path
import ast,base64,hashlib,io,json,secrets,uuid,zipfile
P=Path(__file__).resolve().parent;B=P/'bundle'
config_path=P/'pc/session.json'
if config_path.exists():config=json.loads(config_path.read_text())
else:
 info=json.loads((B/'release_info.json').read_text())
 config=dict(schema='line11-live-session/v1',session_id=uuid.uuid4().hex,token=secrets.token_hex(32),
  pc_url='http://192.168.2.89:8797',port=8797,input_mapping='direct-grey-center-square-area/v2',crop_roi=dict(left=16,top=0,width=48,height=48),camera_width=80,camera_height=48,transfer_mode='live_compact',
  max_steps=4096,ring_slots=64,minimum_period_s=0.,duration_s=60.,adaptive_memory=False,
  automatic_archives=False,diagnostics=False,camera_diagnostics=False,
  bit_sha256=info['bit_sha256'],hwh_sha256=info['hwh_sha256'],
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
(P/'LINE11_OFFICIAL_LIVE_CROP_60S_OFFLINE.zip').write_bytes(raw)
code='''import base64,hashlib,io,sys,zipfile
from pathlib import Path
if globals().get('_LINE11_LIVE_USED',False):raise RuntimeError('Already attempted; do not rerun. Keep kernel and records.')
_raw=base64.b64decode(%r)
if hashlib.sha256(_raw).hexdigest()!=%r:raise RuntimeError('Payload mismatch')
_hashes=%r
_root=Path('/home/xilinx/jupyter_notebooks/LINE11_OFFICIAL_LIVE_CROP_60S')/('package_'+%r)
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
md="""# 官方OV5640 + 完整FlyVis：中央正方形铺满 · DDR循环60秒候选

1. 电脑双击本目录 **60_34f67624.cmd**，保持接收窗口打开。网页提供本Notebook下载。
2. 旧相机已正常关闭、板卡独占、接口不变；上传此Notebook并使用独立新内核运行唯一代码格。
3. 默认实时发送每步721项输入和全部45669状态。程序先核对文件、电脑接收端及内存预算，然后只确认一次：输入 **运行铺满版60秒**。
4. 加载与已通过循环版相同的固件一次，采集循环运行60秒，到时完成已开始的当前步。初始化、末批保存、传输及电脑验收另计。
5. 结束后等待 **NORMAL_CAMERA_CLOSED** 和电脑 **PASS_ALL_SAVED_STATES**。异常则保留内核与缓冲区，提供最后输出，不重复运行。

完整45669节点、1513231连接、严格FP32及100MHz设计保持不变。官方仍采集80x48，只取中央48x48（左右各裁16列），保持比例并映射到全部721项，无上下补灰；灰度只处理2304像素。显示沿用现有界面，可以跳过旧帧，神经记录全部保留。

新版使用64个DDR槽（11.5MiB），ARM只在16步批次落盘并完成同步后确认释放。取消为60秒预留全部DDR造成的固定限速；记录队列扩大到32。若写盘持续过慢，计算会等待，绝不覆盖尚未可靠保存的记录。4096步是安全上限，实际速度和完成步数以实板结果为准。

本候选已有CPU/RTL和完整SoC布局布线证据，循环版本已完成实板60秒1070步全状态验收；本次裁剪映射仅完成CPU验证。板上首次运行仍需由操作者执行。官方同步相机调用可能阻塞；异常不自动重试、复位或释放内存。掉电/关内核会丢失尚未落盘的记录。已有通过60秒R3保留作回退。
"""
nb=dict(nbformat=4,nbformat_minor=4,metadata=dict(kernelspec=dict(display_name='Python 3',language='python',name='python3'),language_info=dict(name='python',version='3.8.0')),cells=[dict(cell_type='markdown',metadata={},source=md.splitlines(True)),dict(cell_type='code',metadata={},source=code.splitlines(True),outputs=[],execution_count=None)])
f=P/'LINE11_OFFICIAL_LIVE_CROP_60S.ipynb';f.write_text(json.dumps(nb,ensure_ascii=False),encoding='utf-8')
(P/'DELIVERY.json').write_text(json.dumps(dict(notebook=f.name,notebook_bytes=f.stat().st_size,
 notebook_sha256=hashlib.sha256(f.read_bytes()).hexdigest(),zip_sha256=digest,members=len(files),
 pc_url=config['pc_url'],maximum_steps=config['max_steps'],duration_seconds=60,board_operations=0),indent=2)+'\n')
print(f.name,f.stat().st_size,'members',len(files))
