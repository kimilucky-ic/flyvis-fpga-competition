from pathlib import Path
import ast,base64,hashlib,io,json,secrets,uuid,zipfile
P=Path(__file__).resolve().parent;B=P/'bundle'
config_path=P/'pc/session.json'
if config_path.exists():config=json.loads(config_path.read_text())
else:
 config=dict(schema='line11-live-session/v1',session_id=uuid.uuid4().hex,token=secrets.token_hex(32),
  pc_url='http://192.168.2.89:8786',port=8786,transfer_mode="live_compact",max_steps=32,minimum_period_s=0,
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
(P/'LINE11_OFFICIAL_LIVE_R5_OFFLINE.zip').write_bytes(raw)
code='''import base64,hashlib,io,sys,zipfile
from pathlib import Path
if globals().get('_LINE11_LIVE_USED',False):raise RuntimeError('Already attempted; do not rerun. Keep kernel and records.')
_raw=base64.b64decode(%r)
if hashlib.sha256(_raw).hexdigest()!=%r:raise RuntimeError('Payload mismatch')
_hashes=%r
_root=Path('/home/xilinx/jupyter_notebooks/LINE11_OFFICIAL_LIVE_R5')/('package_'+%r)
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
md='''# 官方 OV5640 + 完整 FlyVis：R5精简传输与合并记录

1. 实时显示或结束后上传：电脑双击 `r5_42c1ebe8.cmd`，保持窗口运行。仅板端保存模式不需要电脑接收程序。
2. 旧R3关闭未确认：结果已备份后，由操作者重新上电并确认板卡独占、领航者7020/OV5640接口不变。用独立新内核运行唯一代码格。
3. 选择输出方式：**1=实时721项输入+全部状态（默认）；2=运行完再统一上传；3=仅板端保存，不上传、不做电脑CPU验收**。
4. 确认提示后，输入 **运行R5相机32步** 一次。本次只进行有限32步，不能重复运行。

完整45669节点/1513231连接、严格FP32和100MHz设计及原BIT/HWH不变。电脑展示实际721项输入和T4/T5活动，不再传输原始800x480相机图像。每步完整状态仍保存；模式1/2自动执行以实际输入为基础的全状态CPU验收，原图到721项映射的独立验收需稍后导出板端记录。模式3不能宣称数值验收通过。

板端每步两个持久化文件：计算前PREPARED.bin包含原图+721项输入+绑定身份，计算后COMMITTED.bin包含完整DDR记录和提交身份。ready索引另行持久化。耗时/摄像头地址等诊断旁路文件不再逐文件同步；异常断电可能丢失这些诊断文件，不能据其缺失补算或重复STEP。神经输入、结果和提交记录不使用这个放宽。

32步后先保存完成记录、按所选方式处理上传并导出NEURAL_RESULT.zip，再调用相机关闭。官方同步关闭仍可能阻塞，无自动复位或强制中止；数值验收与相机关闭分别显示。上传未确认时保留内核/缓冲区，暂不关闭。若卡在NORMAL_CAMERA_CLOSE，使用已打印的ZIP或查看电脑验收；不要重复运行。

本候选先做CPU验证，尚无R5实板速度或正常关闭证据。模式2/3运行中没有实时电脑更新；本次32步不代表无限运行或实时帧率。
'''
nb=dict(nbformat=4,nbformat_minor=4,metadata=dict(kernelspec=dict(display_name='Python 3',language='python',name='python3'),language_info=dict(name='python',version='3.8.0')),cells=[dict(cell_type='markdown',metadata={},source=md.splitlines(True)),dict(cell_type='code',metadata={},source=code.splitlines(True),outputs=[],execution_count=None)])
f=P/'LINE11_OFFICIAL_LIVE_R5.ipynb';f.write_text(json.dumps(nb,ensure_ascii=False),encoding='utf-8')
(P/'DELIVERY.json').write_text(json.dumps(dict(notebook=f.name,notebook_bytes=f.stat().st_size,
 notebook_sha256=hashlib.sha256(f.read_bytes()).hexdigest(),zip_sha256=digest,members=len(files),
 pc_url=config['pc_url'],maximum_steps=32,board_operations=0),indent=2)+'\n')
print(f.name,f.stat().st_size,'members',len(files))
