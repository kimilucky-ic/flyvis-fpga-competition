"""Focused new-profile software checks. Original saved CPU fixture, no hardware."""
import ast
import copy
import importlib.util
import io
import json
from pathlib import Path
import sys
import uuid
import zipfile

HERE=Path(__file__).resolve().parents[2];sys.path.insert(0,str(HERE))
import ov5640_adapter as ov
from ov5640_notebook import export_notebook
ROOT=Path(__file__).resolve().parent/('cpu_conditional_'+uuid.uuid4().hex[:8]);ROOT.mkdir()
tests=[]
def reject(name,fn):
    try:fn()
    except (ValueError,RuntimeError):tests.append(name);return
    raise AssertionError(name)

spec=importlib.util.spec_from_file_location('conditional_checks',ov.BUNDLE/'gui_conditions.py')
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
conditions=json.loads((ov.BUNDLE/'conditions.json').read_text())
conditions.update(baseboard_revision='V3.9',test_profile=c.PROFILE,manufacturer_compatibility='USER_REPORTED_MANUFACTURER_CONFIRMED',
    camera_io_3v3_verified=True,pinmap_and_orientation_verified=True,exclusive_board_ownership=True,
    module_nominal_24MHz_documented=True,PS_nominal_reference_documented=True,unmeasured_timing_accepted=True,
    operator_confirmation='同意单帧测试',physical_clock_measured=False,SCCB_rise_time_measured=False,DVP_external_timing_measured=False)
c.check_conditions(conditions);tests.append('explicit_conditional_scope_accepts_without_claiming_measured_waveforms')
for k,v in [('unmeasured_timing_accepted',False),('exclusive_board_ownership',False),('pinmap_and_orientation_verified',False),
            ('manufacturer_compatibility','UNKNOWN'),('SCCB_rise_time_measured',True),
            ('SCCB_pullups_voltage_and_rise_time_checked',True),('test_profile','old'),('operator_confirmation','准备')]:
    bad=dict(conditions);bad[k]=v
    reject('reject_'+k,lambda:c.check_conditions(bad))
hp=dict(boot_id='test_boot',status='PASS_CURRENT_HP_WIDTH_ONLY',HP0_HP1_64bit_verified=True,register_writes=0,
    raw_registers={'0xf8000240':0,'0xf8008000':0,'0xf8008014':3840,'0xf8009000':0,'0xf8009014':3840})
c.check_hp_evidence(hp,'test_boot');tests.append('matching_HP_evidence')
reject('reject_old_boot',lambda:c.check_hp_evidence(hp,'other'))
for address in ('0xf8008000','0xf8008014','0xf8009000','0xf8009014'):
    bad=copy.deepcopy(hp);bad['raw_registers'][address]|=1
    reject('reject_HP_32bit_'+address,lambda:c.check_hp_evidence(bad,'test_boot'))
ov.verify_package();tests.append('derived_sealed_package_matches')
base=ov.RELEASE/'bundle'
for name in ('flyvis_ov5640.bit','flyvis_ov5640.hwh','reference.exe','edges.bin','initial_state.bin','single_frame.py','ddr_control.py','ddr_memory.py','bounded_io.py','sensor_init.py'):
    assert (ov.BUNDLE/name).read_bytes()==(base/name).read_bytes()
tests.append('images_model_FP32_oracle_control_and_memory_unchanged')
for path in ov.BUNDLE.glob('*.py'):ast.parse(path.read_text(encoding='utf-8'),feature_version=(3,8))
nb=export_notebook('http://192.168.2.89:8771',ROOT)
source=''.join(json.loads(nb.read_text(encoding='utf-8'))['cells'][1]['source'])
ast.parse(source,feature_version=(3,8))
assert source.index('confirmation=input(')<source.index('root.mkdir()')<source.index('board.run(')
assert "SCCB_pullups_voltage_and_rise_time_checked=False" in source
assert source.index("request('capture-intent'")<source.index('board.run(')
tests.append('human_acceptance_before_capture_and_false_measurement_flags')
board=(ov.BUNDLE/'board_capture.py').read_text()
assert board.index('overlay.download()')<board.index('hp=current_hp(')<board.index("phase='SENSOR_INIT'")
tests.append('fresh_HP_check_before_sensor_and_allocation')
fixture=ov.RELEASE/'cpu_tests_999eaf60/42feb0159e'
buf=io.BytesIO()
with zipfile.ZipFile(buf,'w',zipfile.ZIP_DEFLATED) as z:
    for p in fixture.rglob('*'):
        if p.is_file():z.write(p,p.relative_to(fixture).as_posix())
session=ov.OV5640Session(ROOT/'sessions');auth='Bearer '+session.pairing['pairing_key']
receipt=session.ingest(buf.getvalue(),auth,session.session_id)
packet=session.frame()
assert receipt['evidence']=='CPU_MOCK_ONLY' and packet['acceptance']['mismatch_words']==0
assert packet['acceptance']['test_profile']==c.PROFILE and not packet['acceptance']['electrical_timing_acceptance']
assert len(packet['spatial']['values'])==5768 and len(packet['flow'][0])==721
assert packet['flow_binding']['full_state_sha256']==packet['full_state_sha256']
geometry=session.projection()
for n,data in [('DISPLAY.json',packet),('STATUS.json',receipt),('PROJECTION.json',geometry)]:
    (ROOT/n).write_text(json.dumps(data),encoding='utf-8')
tests.append('original_CPU_fixture_full_state_and_official_decoder_display_packet')
assert 'pynq' not in sys.modules
report=dict(status='PASS_CONDITIONAL_SOFTWARE_ONLY',tests=tests,passed=len(tests),board_reads=0,board_writes=0,
            GPU_operations=0,camera_operations=0,physical_test='NOT_RUN',electrical_signoff=False,
            package_sha256=ov.PACKAGE_SHA,result_directory=str(ROOT))
(ROOT/'RESULT.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
