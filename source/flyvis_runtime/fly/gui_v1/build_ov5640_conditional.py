"""Create a separately sealed GUI-owned admission revision. Never run hardware.

Only conditions and live HP admission change. Original lane11 bundle is read-only;
neural/RTL/images/reference/memory/transport remain byte-identical.
"""
import ast
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

HERE=Path(__file__).resolve().parent
REPO=next(p for p in HERE.parents if (p/'flyvis-lossless-study').is_dir())
BASE=REPO/'flyvis-lossless-study/ov5640_release_20261023'
BASE_SHA='72b2d1cd31d60c5319307e1be9c2d14aa500f53c72f1cd1d008fc929ee96b79c'
TARGET=HERE/'handoff/ov5640_conditional_r1_20261023'
PROFILE='GUI_OV5640_CONDITIONAL_ONE_FRAME_R1'

CONDITIONS='''"""Explicit conditional functional test, never electrical signoff."""
PROFILE='GUI_OV5640_CONDITIONAL_ONE_FRAME_R1'

def check_conditions(c):
    if c.get('board_family')!='Leader ZYNQ-7020' or c.get('part')!='xc7z020clg400-2' or c.get('baseboard_revision')!='V3.9':
        raise ValueError('Only confirmed Leader7020 V3.9 scope')
    if c.get('test_profile')!=PROFILE:raise ValueError('Explicit conditional profile required; old generic flags not sufficient')
    if c.get('manufacturer_compatibility')!='USER_REPORTED_MANUFACTURER_CONFIRMED':raise ValueError('Manufacturer confirmation absent')
    for k in ('camera_io_3v3_verified','pinmap_and_orientation_verified','exclusive_board_ownership',
              'module_nominal_24MHz_documented','PS_nominal_reference_documented','unmeasured_timing_accepted'):
        if c.get(k) is not True:raise ValueError('Required admission absent: '+k)
    if c.get('operator_confirmation')!='同意单帧测试':raise ValueError('Human conditional-test confirmation absent')
    for k in ('physical_clock_measured','SCCB_rise_time_measured','DVP_external_timing_measured'):
        if c.get(k) is not False:raise ValueError('This profile cannot claim measured external timing: '+k)
    if c.get('SCCB_pullups_voltage_and_rise_time_checked') is not False:
        raise ValueError('Preserve combined SCCB measurement flag as false; circuit pullups documented separately')
    if c.get('channel_order') not in ('RGB','BGR','GBR'):raise ValueError('Explicit channel order required')

def current_hp(mmio,boot_id):
    from gui_ps_readonly import inspect
    pages={}
    def read(address):
        base=address&~0xfff
        if base not in pages:pages[base]=mmio(base,4096)
        return int(pages[base].read(address-base))
    result=inspect(read);result['boot_id']=boot_id
    if not result['HP0_HP1_64bit_verified']:raise RuntimeError('Current HP admission failed: '+str(result))
    return result

def check_hp_evidence(hp,boot_id):
    if hp.get('boot_id')!=boot_id or hp.get('status')!='PASS_CURRENT_HP_WIDTH_ONLY':raise ValueError('HP boot/status mismatch')
    raw=hp['raw_registers']
    if raw.get('0xf8000240')!=0:raise ValueError('HP reset admission absent')
    for a in ('0xf8008000','0xf8008014','0xf8009000','0xf8009014'):
        v=raw.get(a)
        if not isinstance(v,int) or not 0<=v<=0xffffffff or v&1:raise ValueError('HP not64bit: '+a)
    if hp.get('register_writes')!=0 or hp.get('HP0_HP1_64bit_verified') is not True:raise ValueError('Not readonly64bit evidence')
'''

def sha(b):return hashlib.sha256(b).hexdigest()
def replace_once(s,old,new):
    if s.count(old)!=1:raise ValueError('Unexpected source anchor '+old[:60])
    return s.replace(old,new,1)

def build():
    if TARGET.exists():raise RuntimeError('Do not overwrite derived release')
    original=(BASE/'flyvis_line11_ov5640_100mhz_offline_r1.zip').read_bytes()
    if sha(original)!=BASE_SHA:raise ValueError('Original release changed')
    target=TARGET/'bundle';target.mkdir(parents=True)
    with zipfile.ZipFile(BASE/'flyvis_line11_ov5640_100mhz_offline_r1.zip') as z:
        for n in z.namelist():
            if Path(n).name!=n:raise ValueError('Unexpected nonflat source')
            raw=z.read(n)
            if (BASE/'bundle'/n).read_bytes()!=raw:raise ValueError('Original unpacked source changed')
            (target/n).write_bytes(raw)
    board=(target/'board_capture.py').read_text()
    tree=ast.parse(board);f=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='check_conditions')
    lines=board.splitlines(True)
    lines[f.lineno-1:f.end_lineno]=['def check_conditions(c):\n    from gui_conditions import check_conditions as check\n    return check(c)\n']
    board=''.join(lines)
    board=replace_once(board,"        phase='FRESH_ABI'", "        phase='CURRENT_HP_ADMISSION'\n        from gui_conditions import current_hp\n        hp=current_hp(pynq.MMIO,context['boot_id'])\n        save_json(out/'PS_HP_CONFIG.json',hp)\n        phase='FRESH_ABI'")
    (target/'board_capture.py').write_text(board,encoding='utf-8')
    (target/'gui_conditions.py').write_text(CONDITIONS,encoding='utf-8')
    shutil.copyfile(HERE/'ov5640_ps_readonly.py',target/'gui_ps_readonly.py')
    audit=(target/'verify_run.py').read_text()
    audit=replace_once(audit,"            if not ctx['boot_id']:raise ValueError('Boot identity absent')", "            if not ctx['boot_id']:raise ValueError('Boot identity absent')\n            from gui_conditions import check_hp_evidence\n            check_hp_evidence(json.loads((run/'PS_HP_CONFIG.json').read_text()),ctx['boot_id'])")
    audit=replace_once(audit,"        save_json(out/'ACCEPTANCE.json',result);return result", "        result.update(test_profile='GUI_OV5640_CONDITIONAL_ONE_FRAME_R1',electrical_timing_acceptance=False,\n          SCCB_rise_time_measured=False,DVP_external_timing_measured=False,\n          manufacturer_compatibility='NOT_APPLICABLE_CPU_FIXTURE' if ctx['evidence']=='CPU_MOCK_ONLY' else ctx['conditions']['manufacturer_compatibility'])\n        save_json(out/'ACCEPTANCE.json',result);return result")
    (target/'verify_run.py').write_text(audit,encoding='utf-8')
    policy=dict(test_profile=PROFILE,base_package_sha256=BASE_SHA,scope='ONE_FRAME_ONE_FULL_PL_STEP_CONDITIONAL_FUNCTIONAL_TEST',
                board_execution_authority='HUMAN_NOTEBOOK_CONFIRMATION_ONLY',
                manufacturer_confirmation='USER_REPORTED',external_timing_measured=False,
                changes=['explicit conditional admission instead of claiming measured waveforms','fresh readonly post-load HP check','audit checks same policy and HP evidence'],
                unchanged=['BIT/HWH','neural model/FP32/dt','reference oracle','camera initializer','memory/flush/barriers','input/state binding','no-retry/failure preservation'])
    (target/'GUI_CONDITIONAL_PROFILE.json').write_text(json.dumps(policy,indent=2),encoding='utf-8')
    manifest={p.name:dict(bytes=p.stat().st_size,sha256=sha(p.read_bytes())) for p in target.iterdir() if p.name!='release_manifest.json'}
    (target/'release_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    zip_path=TARGET/'GUI_OV5640_CONDITIONAL_R1.zip'
    with zipfile.ZipFile(zip_path,'x',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(target.iterdir()):z.write(p,p.name)
    unchanged=[];changed=[]
    for p in (BASE/'bundle').iterdir():
        (unchanged if p.read_bytes()==(target/p.name).read_bytes() else changed).append(p.name)
    if set(changed)!={'board_capture.py','verify_run.py','release_manifest.json'}:raise ValueError('Unexpected changes '+str(changed))
    result=dict(policy,package_sha256=sha(zip_path.read_bytes()),files=len(list(target.iterdir())),
                unchanged_base_files=unchanged,changed_base_files=changed,package=str(zip_path),bundle=str(target))
    (TARGET/'BUILD.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    return result

if __name__=='__main__':print(json.dumps(build(),indent=2))
