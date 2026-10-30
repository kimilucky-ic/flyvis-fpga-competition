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
header='''# OV5640 型号验证 R2 · AXI IIC 2.1 顺序修正

只运行下面一个代码格。本文件自带与上次完全相同的BIT/HWH，不依赖电脑实验台。旧 Notebook 不要重跑。

1. 确认是领航者ZYNQ-7020 V3.9 + ATK-MC5640，接口未变，板上没有其他程序操作硬件。
2. 上传并打开这个新文件，点唯一代码格，按 Shift+Enter。
3. 输入「加载原固件并验证型号」并回车，明确授权加载原固件一次，清除上次未完成IIC事务，再只读型号。
4. 下载 LINE11_OV5640_ID_DIAG/ID_R2_…_RESULT.zip，交回核查；不继续采图。

不需要预先重启板子，不删除旧结果/标记。若仍是已核查的6107d12e…启动，必须找到并验证上次cd4dcb60…失败记录；其他不明旧尝试会停止。新启动也可以使用。本修正版每个启动周期只允许一次尝试，失败不自动重试、复位或重载。

本次向IIC控制器写地址和读取数量命令，但不写摄像头配置，不执行248项初始化、不采图、不分配DDR、不运行神经STEP。0x5640仅证明型号读取成功。

250ms是每笔事务软件限时，不能强制中断不返回的MMIO。若一直无输出，保留最后输出，不重复运行。时钟和电气波形未实测。
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
out=P/'OV5640_ID_FIX_R2_20261024.ipynb';out.write_text(json.dumps(nb,ensure_ascii=False),encoding='utf-8')
# Verify every embedded member against the sealed baseline or new diagnostic source.
with zipfile.ZipFile(io.BytesIO(payload)) as z:
 assert all(z.read(n)==b for n,b in files.items())
(P/'DELIVERY.json').write_text(json.dumps(dict(status='PREPARED_OFFLINE_CPU_VERIFIED_NOT_BOARD_TESTED',notebook=str(out.resolve()),notebook_bytes=out.stat().st_size,notebook_sha256=hashlib.sha256(out.read_bytes()).hexdigest(),payload_sha256=sha,members=manifest,board_operations=0,GPU_operations=0,Vivado_operations=0,revision='IIC21_R2',firmware_unchanged=True,transport_change='queue count before waiting RX; no BB-before-count; RX-aware NACK check'),indent=2),encoding='utf-8')
print(out.resolve(),out.stat().st_size)
