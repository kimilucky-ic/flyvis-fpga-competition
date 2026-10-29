"""Reproduce a self-contained operator Notebook; file-only build."""
import ast,base64,hashlib,io,json,zipfile
from pathlib import Path
P=Path(__file__).resolve().parent
B=P.parent/'ov5640_release_20261023/bundle'
files={n:(B/n).read_bytes() for n in ['flyvis_ov5640.bit','flyvis_ov5640.hwh','upstream_flyvis_license.txt','original_model_provenance.json']}
files.update({n:(P/n).read_bytes() for n in ['id_diag.py','bounded_io.py']})
manifest={n:hashlib.sha256(b).hexdigest() for n,b in files.items()}
raw=io.BytesIO()
with zipfile.ZipFile(raw,'w',zipfile.ZIP_DEFLATED) as z:
 for n,b in files.items():z.writestr(n,b)
payload=raw.getvalue();sha=hashlib.sha256(payload).hexdigest()
header='''# OV5640 重启后只读型号诊断 · ⑪ · 2026-10-24

只运行下面一个代码格，不使用昨天的单帧 Notebook。本文件自带原版 BIT/HWH，不依赖电脑实验台服务。

1. 确认是领航者 ZYNQ-7020 V3.9 + ATK-MC5640，接口未变，板上无其他实验操作硬件。
2. 点代码格，按 Shift+Enter；提示时输入「同意只读型号」。
3. 如果当前固件不匹配，程序会提示替换 PL 配置；只有输入「加载候选并只读型号」才加载一次。不想加载则输入「取消」。
4. 完成后下载 LINE11_OV5640_ID_DIAG/ID_…_RESULT.zip 交回核查。成功只证明读到型号，不证明采图或神经计算通过。

本次会向 IIC 控制器写地址和读命令，但不写摄像头配置，不执行248项初始化、不采图、不分配DDR、不运行神经STEP。失败不自动重试/复位，整个启动周期只允许一次尝试。

250ms是每笔事务的软件截止时间，无法强制中断不返回的硬件MMIO。若持续无输出，保留最后输出，不重复运行或自行复位。时钟和电气波形仍未实测；本次只做条件性功能检查。
'''
code='''import base64, hashlib, io, json, sys, zipfile
from pathlib import Path
if globals().get('_LINE11_ID_ENTRY_USED', False):
    raise RuntimeError('This Notebook entry was already used. Preserve results; do not retry.')
_PAYLOAD_SHA = %r
_FILES = %r
_DATA = base64.b64decode(%r)
if hashlib.sha256(_DATA).hexdigest() != _PAYLOAD_SHA:
    raise RuntimeError('Embedded package corrupted; no hardware access')
_ROOT = Path('/home/xilinx/jupyter_notebooks/LINE11_OV5640_ID_DIAG') / ('package_' + _PAYLOAD_SHA[:12])
_ROOT.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(io.BytesIO(_DATA)) as _z:
    if len(_z.namelist()) != len(_FILES) or set(_z.namelist()) != set(_FILES):
        raise RuntimeError('Unexpected package members')
    for _name, _expected in _FILES.items():
        _bytes = _z.read(_name)
        if hashlib.sha256(_bytes).hexdigest() != _expected:
            raise RuntimeError('Payload member identity mismatch')
        _dest = _ROOT / _name
        if _dest.exists():
            if hashlib.sha256(_dest.read_bytes()).hexdigest() != _expected:
                raise RuntimeError('Existing extracted file differs; not overwritten')
        else:
            with _dest.open('xb') as _f:
                _f.write(_bytes)
for _module in ('id_diag', 'bounded_io'):
    if _module in sys.modules:
        raise RuntimeError('Module already loaded in this kernel; use a fresh diagnostic Notebook before any hardware attempt')
sys.path.insert(0, str(_ROOT))
import id_diag
if Path(id_diag.__file__).resolve() != (_ROOT / 'id_diag.py').resolve():
    raise RuntimeError('Wrong diagnostic module import')
_LINE11_ID_ENTRY_USED = True
id_diag.run(_ROOT)
'''%(sha,manifest,base64.b64encode(payload).decode('ascii'))
ast.parse(code,feature_version=(3,8))
nb=dict(cells=[dict(cell_type='markdown',metadata={},source=header.splitlines(True)),dict(cell_type='code',metadata={},execution_count=None,outputs=[],source=code.splitlines(True))],metadata=dict(kernelspec=dict(display_name='Python 3',language='python',name='python3'),language_info=dict(name='python',version='3.8.0')),nbformat=4,nbformat_minor=4)
out=P/'OV5640_ID_ONLY_20261024.ipynb';out.write_text(json.dumps(nb,ensure_ascii=False),encoding='utf-8')
# Verify every embedded member against the sealed baseline or new diagnostic source.
with zipfile.ZipFile(io.BytesIO(payload)) as z:
 assert all(z.read(n)==b for n,b in files.items())
(P/'DELIVERY.json').write_text(json.dumps(dict(status='PREPARED_OFFLINE_CPU_VERIFIED_NOT_BOARD_TESTED',notebook=str(out.resolve()),notebook_bytes=out.stat().st_size,notebook_sha256=hashlib.sha256(out.read_bytes()).hexdigest(),payload_sha256=sha,members=manifest,board_operations=0,GPU_operations=0,Vivado_operations=0,source_transport_unchanged=files['bounded_io.py']==(B/'bounded_io.py').read_bytes()),indent=2),encoding='utf-8')
print(out.resolve(),out.stat().st_size)
