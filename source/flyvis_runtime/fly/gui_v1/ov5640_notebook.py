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
assert manifest['package_sha256']==entry['package_sha256'], ('电脑后台与Notebook准备包版本不一致：后台 '+manifest['package_sha256'][:12]+'，Notebook '+entry['package_sha256'][:12]+'。请在FlyVis点“关闭实验台”并重新启动电脑入口，再下载对应Notebook。此处尚未下载板端程序、加载固件或采集；不要重启板子或跳过SHA校验。')
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
    conditions=json.loads(conditions_path.read_text(encoding='utf-8-sig'))
    assert manifest.get('test_profile')=='GUI_OV5640_CONDITIONAL_ONE_FRAME_R1' and manifest.get('electrical_timing_acceptance') is False
    assert conditions.get('baseboard_revision') in (None,'V3.9'), '本次只适用已拍照确认的V3.9底板'
    assert conditions.get('board_family')=='Leader ZYNQ-7020' and conditions.get('part')=='xc7z020clg400-2'
    # Imports must not attach to old retained allocations or a different ABI.
    conflicts=[n for n,m in sys.modules.items() if n in ('board_capture','ddr_control','ddr_memory','bounded_io','single_frame')]
    assert not conflicts, '已有板端模块/资源：'+str(conflicts)+'；先按原流程正常收尾，不自动接管'
    assert not globals().get('_line2_ov_attempted',False), '本内核已有尝试；保留DDR，不自动重复加载'
    print('本次：领航者7020 V3.9 + ATK-MC5640 V1.2；厂家兼容性由用户转达确认。')
    print('名义时钟：模块24MHz、PS参考33.333333MHz。波形/实际频率未测量，不作为电气时序验收。')
    print('DVP采用现有条件时序预算及W14非专用时钟布线例外；不声称外部时序测量通过。')
    print('你确认接头无错位、GND/3.3V对应、板卡独占；本次加载OV5640固件一次，采一帧、计算一步。')
    print('加载后自动复核实际时钟配置和HP0/HP1；失败立即停，保留内核/DDR，不重试或回退。')
    confirmation=input('接受未测SCCB/DVP波形的本次条件性功能测试，并授权上述操作，输入 同意单帧测试：')
    assert confirmation=='同意单帧测试', '未授权；无加载/采集/神经计算'
    # Retain original file/flags unchanged. Explicit new scope records the actual
    # evidence basis instead of relabeling unmeasured waveforms as verified.
    conditions=dict(conditions,baseboard_revision='V3.9',test_profile=manifest['test_profile'],
        manufacturer_compatibility='USER_REPORTED_MANUFACTURER_CONFIRMED',
        camera_io_3v3_verified=True,pinmap_and_orientation_verified=True,exclusive_board_ownership=True,
        module_nominal_24MHz_documented=True,PS_nominal_reference_documented=True,
        unmeasured_timing_accepted=True,operator_confirmation=confirmation,
        conditional_DVP_timing_and_nonCCIO_exception_accepted=True,
        physical_clock_measured=False,SCCB_rise_time_measured=False,DVP_external_timing_measured=False,
        SCCB_pullups_voltage_and_rise_time_checked=False,gui_session_id=manifest['session_id'])
    scope={}
    exec(compile(z.read('gui_conditions.py').decode('utf-8'),'sealed_GUI_conditions','exec'),scope)
    scope['check_conditions'](conditions)
    # Validate confirmation structure BEFORE authorizing hardware.
    root.mkdir()
    for n in z.namelist():(root/n).write_bytes(z.read(n))
sys.path.insert(0,str(root))
board=importlib.import_module('board_capture')
try:board.check_conditions(conditions)
except Exception:
    print('实物条件未通过；无硬件操作。请核对条件文件；不要将未知条件直接填true。')
    raise
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
            '本版无需把旧JSON里的false批量改true。由一次明确输入接受条件性单帧功能测试；未测量波形仍记为未测量。\n',
            '运行前确认接头无错位、GND/3.3V对应、板卡独占。输入“同意单帧测试”才授权加载固件和采集。\n',
            '本版本只采一帧、计算一步；不支持60秒连续视频。不得和其他板端实验并行。\n',
            'Notebook含本机配对密钥，请勿公开上传。硬件操作由你手动运行授权。']),
          dict(cell_type='code',metadata={},source=code.splitlines(True),outputs=[],execution_count=None)])
    path=output/'flyvis_ov5640单帧验收.ipynb'
    path.write_text(json.dumps(notebook,ensure_ascii=False,indent=1),encoding='utf-8')
    return path
