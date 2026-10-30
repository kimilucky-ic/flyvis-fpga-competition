from pathlib import Path
import ast,base64,hashlib,io,json,secrets,uuid,zipfile
P=Path(__file__).resolve().parent;B=P/'bundle'
config_path=P/'pc/session.json'
if config_path.exists():config=json.loads(config_path.read_text())
else:
 config=dict(schema='line11-live-session/v1',session_id=uuid.uuid4().hex,token=secrets.token_hex(32),
  pc_url='http://192.168.2.89:8783',port=8783,max_steps=32,minimum_period_s=0,
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
(P/'LINE11_OFFICIAL_LIVE_R2_OFFLINE.zip').write_bytes(raw)
code='''import base64,hashlib,io,sys,zipfile
from pathlib import Path
if globals().get('_LINE11_LIVE_USED',False):raise RuntimeError('Already attempted; do not rerun. Keep kernel and records.')
_raw=base64.b64decode(%r)
if hashlib.sha256(_raw).hexdigest()!=%r:raise RuntimeError('Payload mismatch')
_hashes=%r
_root=Path('/home/xilinx/jupyter_notebooks/LINE11_OFFICIAL_LIVE_R2')/('package_'+%r)
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
md='''# 官方 OV5640 + 完整 FlyVis：32步与电脑显示

1. 电脑双击本候选的 `.cmd_32295f30.cmd`，保持接收窗口运行。网页显示“等待板端记录”。
2. 确保旧官方相机已正常关闭、领航者7020/OV5640接口未变、板卡独占。此Notebook使用独立新内核，运行下面唯一代码格。
3. 网络预检查通过后，输入 **运行优化版相机32步** 一次。这次授权一次固件加载、官方相机初始化和有限32步计算。
4. 电脑自动显示最新完整帧并保存全部记录；最后自动核查每步全部45669状态。不需要正常流程手动交ZIP。

**原版32步实板记录已通过全状态验收并保留；本优化候选先做CPU等价验证，其ARM速度及连续板端行为待操作者验证。** 完整45669节点/1513231连接、严格FP32和100MHz设计不变。骨架复用原软件T4/T5显示，未接入光流解码箭头。

PC断线只重传已保存文件，不补算或重复STEP。显示暂停/跳帧不影响神经记录。32步结束后正常关闭相机；缓冲区仍保留，不重复运行。若中途异常/阻塞，保留内核及缓冲区，不自行复位、重跑或关闭Python。官方同步驱动可能阻塞，无自动中止承诺。

上传最多等待60秒；若电脑仍未收到全部记录，下载最终打印的RESULT.zip供离线核查，不能重新计算替代丢失传输。本次有限32步避免覆盖；并非无限循环或实时帧率证明。
'''
nb=dict(nbformat=4,nbformat_minor=4,metadata=dict(kernelspec=dict(display_name='Python 3',language='python',name='python3'),language_info=dict(name='python',version='3.8.0')),cells=[dict(cell_type='markdown',metadata={},source=md.splitlines(True)),dict(cell_type='code',metadata={},source=code.splitlines(True),outputs=[],execution_count=None)])
f=P/'LINE11_OFFICIAL_LIVE_R2.ipynb';f.write_text(json.dumps(nb,ensure_ascii=False),encoding='utf-8')
(P/'DELIVERY.json').write_text(json.dumps(dict(notebook=f.name,notebook_bytes=f.stat().st_size,
 notebook_sha256=hashlib.sha256(f.read_bytes()).hexdigest(),zip_sha256=digest,members=len(files),
 pc_url=config['pc_url'],maximum_steps=32,board_operations=0),indent=2)+'\n')
print(f.name,f.stat().st_size,'members',len(files))
