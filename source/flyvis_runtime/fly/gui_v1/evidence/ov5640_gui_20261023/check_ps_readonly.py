import ast
import hashlib
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(HERE))
import ov5640_ps_readonly as m
tests=[]
def test(values):
    calls=[]
    def read(a):calls.append(a);return values[a]
    return m.inspect(read),calls
r,c=test({0xf8000240:1})
assert len(c)==1 and r['status']=='STOP_RESET_STATE_NOT_PROVEN_RELEASED'
tests.append('nonzero_reset_skips_all_HP_reads')
for address in [None,0xf8008000,0xf8008014,0xf8009000,0xf8009014]:
    values={0xf8000240:0,0xf8008000:0,0xf8008014:0xf00,0xf8009000:0,0xf8009014:0xf00}
    if address:values[address]|=1
    r,c=test(values)
    assert len(c)==5 and r['HP0_HP1_64bit_verified']==(address is None)
    tests.append('64bit_success' if address is None else 'reject_32bit_'+hex(address))
try:m.run()
except RuntimeError:tests.append('no_authority_no_PYNQ_import')
assert 'pynq' not in sys.modules
source=(HERE/'ov5640_ps_readonly.py').read_text(encoding='utf-8')
ast.parse(source,feature_version=(3,8))
pin=hashlib.sha256(source.encode()).hexdigest()
cell='import json, hashlib\nsource = '+repr(source)+'\nassert hashlib.sha256(source.encode()).hexdigest() == '+repr(pin)+'''
namespace={}
exec(compile(source,"OV5640_PS_READ_ONLY","exec"),namespace)
assert input("仅检查当前PS寄存器，不烧录、不复位、不启动摄像头。确认板卡空闲，输入 检查：") == "检查"
print("OV5640_PS_READ_ONLY",json.dumps(namespace["run"](operator_authorized=True),ensure_ascii=False))
'''
ast.parse(cell,feature_version=(3,8))
nb=dict(nbformat=4,nbformat_minor=4,metadata=dict(kernelspec=dict(display_name='Python 3',language='python',name='python3')),
    cells=[dict(cell_type='markdown',metadata={},source=['# OV5640一次性PS只读诊断\n',
        '仅由用户手动运行。不加载固件、写寄存器、复位、分配DDR或启动计算。\n',
        '仅用于确认当前boot的HP宽度；输出不代表摄像头验收。']),
        dict(cell_type='code',metadata={},source=cell.splitlines(True),outputs=[],execution_count=None)])
notebook=HERE/'flyvis_ov5640只读检查.ipynb'
notebook.write_text(json.dumps(nb,ensure_ascii=False,indent=1),encoding='utf-8')
result=dict(status='PASS_CPU_INJECTED_READS_ONLY',tests=tests,source_sha256=pin,
            real_board_reads=0,real_board_writes=0,notebook=str(notebook))
(Path(__file__).resolve().parent/'PS_READONLY_CPU_RESULT.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
