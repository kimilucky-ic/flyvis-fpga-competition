"""Export only. Hardware runs solely when the operator executes the Notebook."""
import json
from live_protocol import HERE
from line11_ddr_notebook import installation

source = r'''
# OV5640板端单帧一步。不是电脑USB摄像头，不是60秒连续采集。
import hashlib, io, json, sys, urllib.request, zipfile, importlib
from pathlib import Path
entry = ENTRY
def request(kind, session=None):
    body=dict(kind=kind, installation_id=entry['installation_id'])
    if session:body['session_id']=session
    req=urllib.request.Request(entry['origin']+'/api/full-pl-stream/notebook-bundle',
        data=json.dumps(body).encode(),headers={'Authorization':'Bearer '+entry['pairing_key'],'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=30) as reply:return reply.read(16_000_001)
manifest=json.loads(request('manifest'))
assert manifest['input_kind']=='board_ov5640' and manifest['steps']==1 and not manifest['continuous_60s']
assert manifest['package_sha256']==entry['package_sha256'], '封存包身份不符；停止'
base=Path.cwd()/'flyvis_ov5640'
base.mkdir(exist_ok=True)
root=base/manifest['session_id']
assert not root.exists(), '本次会话已领取；不自动重试，请保留现场'
# Preserve actual operator confirmations outside the sealed package.
conditions_path=base/'OV5640实物条件.json'
blob=request('package',manifest['session_id'])
assert len(blob)==manifest['package_bytes'] and hashlib.sha256(blob).hexdigest()==entry['package_sha256']
with zipfile.ZipFile(io.BytesIO(blob)) as z:
    assert len(z.namelist())==len(set(z.namelist())) and len(z.namelist())<=50
    assert all('/' not in n and '\\' not in n and ':' not in n and n not in ('.','..') for n in z.namelist())
    if not conditions_path.exists():
        conditions_path.write_bytes(z.read('conditions.json'))
        raise RuntimeError('请先按实物核对并填写 '+str(conditions_path)+'；未加载固件、未采集。填写后重新运行本格。')
    conditions=json.loads(conditions_path.read_text(encoding='utf-8-sig'))
    # Execute only the sealed pure condition checker, before creating/importing a
    # package. A missing confirmation can be corrected without consuming a run.
    import ast
    source=z.read('board_capture.py').decode('utf-8')
    tree=ast.parse(source)
    checker=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='check_conditions')
    scope={}
    exec(compile(ast.Module(body=[checker],type_ignores=[]),'sealed_conditions','exec'),scope)
    scope['check_conditions'](conditions)
    # Imports must not attach to old retained allocations or a different ABI.
    conflicts=[n for n,m in sys.modules.items() if n in ('board_capture','ddr_control','ddr_memory','bounded_io','single_frame')]
    assert not conflicts, '已有板端模块/资源：'+str(conflicts)+'；先按原流程正常收尾，不自动接管'
    # Validate confirmation structure BEFORE authorizing hardware.
    root.mkdir()
    for n in z.namelist():(root/n).write_bytes(z.read(n))
sys.path.insert(0,str(root))
board=importlib.import_module('board_capture')
try:board.check_conditions(conditions)
except Exception:
    print('实物条件未通过；无硬件操作。请核对条件文件；不要将未知条件直接填true。')
    raise
assert not globals().get('_line2_ov_attempted',False), '本内核已有尝试；保留DDR，不自动重复加载'
assert input('确认独占该板、接线/电压/24MHz振荡器及条件已核实。加载OV5640固件并采一帧一步，输入 准备：')=='准备'
reservation=json.loads(request('capture-intent',manifest['session_id']))
assert reservation['session_id']==manifest['session_id'] and reservation['status']=='CAPTURE_INTENT_RESERVED'
_line2_ov_attempted=True
result=board.run(base/'results',conditions,authorize_load_and_one_step=True)
archive=Path(str(result)+'_RESULT.zip')
print('板端结果已保存；正在上传，电脑执行独立审核和官方光流解码。')
req=urllib.request.Request(entry['origin']+'/api/ov5640/result',data=archive.read_bytes(),
    headers={'Authorization':'Bearer '+entry['pairing_key'],'Content-Type':'application/zip','X-FlyVis-Session':manifest['session_id']})
with urllib.request.urlopen(req,timeout=240) as reply:receipt=json.loads(reply.read(65536))
print('OV5640_GUI_RECEIPT',json.dumps(receipt,ensure_ascii=False))
print('结果为单帧一步，页面自动显示。请保留内核和分配；不要重跑或自行释放DDR。')
'''


def export_notebook(origin, output):
    from ov5640_adapter import PACKAGE_SHA
    pairing=installation()
    entry=dict(pairing,origin=origin,package_sha256=PACKAGE_SHA)
    code=source.replace('ENTRY',repr(entry),1)
    notebook=dict(nbformat=4,nbformat_minor=4,
        metadata=dict(kernelspec=dict(display_name='Python 3',language='python',name='python3')),
        cells=[dict(cell_type='markdown',metadata={},source=[
            '# FlyVis OV5640板端单帧验收\n',
            '仅适用已核对接口的Leader ZYNQ-7020与自带24MHz晶振的OV5640模块。\n',
            '第一次运行生成实物条件文件，按真实情况填写后再运行。未知条件不能勾选。\n',
            '本版本只采一帧、计算一步；不支持60秒连续视频。不得和其他板端实验并行。\n',
            'Notebook含本机配对密钥，请勿公开上传。硬件操作由你手动运行授权。']),
          dict(cell_type='code',metadata={},source=code.splitlines(True),outputs=[],execution_count=None)])
    path=output/'flyvis_ov5640单帧验收.ipynb'
    path.write_text(json.dumps(notebook,ensure_ascii=False,indent=1),encoding='utf-8')
    return path
