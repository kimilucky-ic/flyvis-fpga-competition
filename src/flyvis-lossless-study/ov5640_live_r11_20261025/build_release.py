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
  zi=zipfile.ZipInfo(n,(2026,10,25,0,0,0));zi.compress_type=zipfile.ZIP_DEFLATED;z.writestr(zi,d)
raw=buf.getvalue();digest=hashlib.sha256(raw).hexdigest();hashes={n:hashlib.sha256(d).hexdigest() for n,d in files.items()}
(P/'LINE11_OFFICIAL_LIVE_R11_OFFLINE.zip').write_bytes(raw)
code='''import base64,hashlib,io,sys,zipfile
from pathlib import Path
if globals().get('_LINE11_LIVE_USED',False):raise RuntimeError('Already attempted; do not rerun. Keep kernel and records.')
_raw=base64.b64decode(%r)
if hashlib.sha256(_raw).hexdigest()!=%r:raise RuntimeError('Payload mismatch')
_hashes=%r
_root=Path('/home/xilinx/jupyter_notebooks/LINE11_OFFICIAL_LIVE_R11')/('package_'+%r)
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
md='''# R11：官方OV5640 + 完整FlyVis，32步

1. 电脑双击 `r11_59c8dcc8.cmd`，保持接收窗口和网页打开。
2. 确认旧相机已正常关闭、板卡独占，领航者7020/正点原子OV5640接口未变。上传本Notebook，用独立新内核运行唯一代码格。
3. 输出方式选1，输入 **运行R11相机32步** 一次。会加载同一已核验BIT一次、初始化相机、恢复初态、有限运行32步。
4. 电脑显示721项灰度输入与神经活动，接收全部45669状态，结束后自动做全状态验收。本次只使用R11接收端。

80x48沿用R9已经通过的采集尺寸，保留灰度，不二值化；直接映射721项，无417x417中间图。完整网络、严格FP32、100MHz设计不变。官方驱动调用可能阻塞，无自动复位/重试；异常时保留内核和输出，不重跑。

本版保留R10通过的相机内存复用和721项批量上传；每8步打印一次进度（8/16/24/32），每一步输入与全部状态仍然保存。映射算法不改；每步测墙钟与本线程CPU时间，并记录映射和后台打包起止时间，仅第7/15/23/31步细分映射、绑定、状态校验及RAM记录。详细计时随最终结果提交，不新增逐步写盘。CPU通过不代表ARM实测提速。

正常路径为精简模式；仅第5和第17次取帧开启内部函数计时，用于定位原来的58ms，分析常规速度时排除两次相机跟踪、四次细分计时及启动帧；完整32步总耗时仍全部计入。实际驱动源码摘要自动随结果送到电脑，完整源码留在板端结果包。

每步实际输入与完整状态先留板端RAM，结束后统一保存；掉电或关闭内核会丢失未保存记录。显示可跳帧，神经步和记录不丢、不重算。正常结束会打印NORMAL_CAMERA_CLOSED；若失败或卡住，提供最后输出，保留内核。
'''
nb=dict(nbformat=4,nbformat_minor=4,metadata=dict(kernelspec=dict(display_name='Python 3',language='python',name='python3'),language_info=dict(name='python',version='3.8.0')),cells=[dict(cell_type='markdown',metadata={},source=md.splitlines(True)),dict(cell_type='code',metadata={},source=code.splitlines(True),outputs=[],execution_count=None)])
f=P/'LINE11_OFFICIAL_LIVE_R11.ipynb';f.write_text(json.dumps(nb,ensure_ascii=False),encoding='utf-8')
(P/'DELIVERY.json').write_text(json.dumps(dict(notebook=f.name,notebook_bytes=f.stat().st_size,
 notebook_sha256=hashlib.sha256(f.read_bytes()).hexdigest(),zip_sha256=digest,members=len(files),
 pc_url=config['pc_url'],maximum_steps=32,board_operations=0),indent=2)+'\n')
print(f.name,f.stat().st_size,'members',len(files))
