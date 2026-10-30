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
(P/'LINE11_OFFICIAL_LIVE_R7_OFFLINE.zip').write_bytes(raw)
code='''import base64,hashlib,io,sys,zipfile
from pathlib import Path
if globals().get('_LINE11_LIVE_USED',False):raise RuntimeError('Already attempted; do not rerun. Keep kernel and records.')
_raw=base64.b64decode(%r)
if hashlib.sha256(_raw).hexdigest()!=%r:raise RuntimeError('Payload mismatch')
_hashes=%r
_root=Path('/home/xilinx/jupyter_notebooks/LINE11_OFFICIAL_LIVE_R7')/('package_'+%r)
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
md='''# 官方 OV5640 + 完整 FlyVis：R7分段计时与小范围优化

1. 电脑双击 `r7_24a91584.cmd`，保持接收窗口运行。仅板端保存模式不需要电脑接收程序。
2. 确认上一轮相机已正常关闭、板卡独占，领航者7020/OV5640接口不变；本Notebook使用独立新内核。若旧会话关闭未确认，先保留已有结果，再由操作者重新上电，不在旧会话继续操作。
3. 运行唯一代码格，选择1=实时721项输入+全部状态（默认）；2=32步结束后上传；3=仅板端保存。然后输入 **运行R7相机32步** 一次。
4. R6直接配置400x240相机输出及采集尺寸，不保存原图。每步721项实际输入和全部45669状态先保留板端内存，32步结束后统一保存。计算期间掉电、退出或杀死内核，会丢失尚未保存的记录；出现异常不要重跑或清理内核。

完整45669节点/1513231连接、严格FP32和100MHz神经设计、原BIT/HWH保持不变。降低相机分辨率会改变视觉输入，不能把结果称为800x480输入的无损复现。400x240实物采集及视场/颜色尚待本次验证；不能用CPU测试替代相机实测。

电脑仅显示721项实际输入和T4/T5活动。模式1/2自动核查实际输入→全部神经状态；没有原图，不能事后验证原图→721项映射。模式3不会自动获得CPU数值PASS。神经步不因显示跳帧或断线而重复。

先完成批量保存、按模式交付并生成不压缩ZIP，再调用官方相机关闭。相机关闭可能阻塞；数值通过不代表相机已关闭。若打印RAM_FLUSH_FAILED，数据仍保留内存，不要关闭内核、重跑或释放缓冲区。本候选限32步，尚无实板速度或实时帧率保证。
'''
nb=dict(nbformat=4,nbformat_minor=4,metadata=dict(kernelspec=dict(display_name='Python 3',language='python',name='python3'),language_info=dict(name='python',version='3.8.0')),cells=[dict(cell_type='markdown',metadata={},source=md.splitlines(True)),dict(cell_type='code',metadata={},source=code.splitlines(True),outputs=[],execution_count=None)])
f=P/'LINE11_OFFICIAL_LIVE_R7.ipynb';f.write_text(json.dumps(nb,ensure_ascii=False),encoding='utf-8')
(P/'DELIVERY.json').write_text(json.dumps(dict(notebook=f.name,notebook_bytes=f.stat().st_size,
 notebook_sha256=hashlib.sha256(f.read_bytes()).hexdigest(),zip_sha256=digest,members=len(files),
 pc_url=config['pc_url'],maximum_steps=32,board_operations=0),indent=2)+'\n')
print(f.name,f.stat().st_size,'members',len(files))
