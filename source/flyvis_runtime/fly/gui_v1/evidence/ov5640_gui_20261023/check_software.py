"""Focused tests; existing sealed CPU fixture only. Never import PYNQ/OpenCV."""
import ast
import io
import json
from pathlib import Path
import sys
import uuid
import zipfile

HERE=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(HERE))
import ov5640_adapter as ov
from operator_selection import command,validate
from ov5640_notebook import export_notebook,source

ROOT=Path(__file__).resolve().parent/('cpu_'+uuid.uuid4().hex[:8]);ROOT.mkdir()
rows=[]
def ok(name,fn):
    fn();rows.append(dict(test=name,status='PASS'))
def reject(name,fn):
    try:fn()
    except (ValueError,RuntimeError):rows.append(dict(test=name,status='PASS'));return
    raise AssertionError(name+' accepted')

def archive(files):
    b=io.BytesIO()
    with zipfile.ZipFile(b,'w',zipfile.ZIP_DEFLATED) as z:
        for n,v in files.items():z.writestr(n,v)
    return b.getvalue()

ok('sealed_bundle_matches_zip',ov.verify_package)
selection=dict(backend='FULL_FPGA',input='ov5640',condition=None)
ok('selection_and_nondevice_command',lambda:(validate(selection,set()),
    (_ for _ in ()).throw(AssertionError()) if '--line11-live-camera' in command(selection,ROOT/'STOP') else None))
reject('no_mixed_backend',lambda:validate(dict(selection,backend='GPU_FPGA'),set()))
reject('no_frozen_condition_on_camera',lambda:validate(dict(selection,condition='EDGE_ON_RIGHT'),set()))
reject('zip_traversal',lambda:ov.checked_files(archive({'../bad':b'x'})))
reject('zip_oversize',lambda:ov.checked_files(b'x'*(ov.MAX_ZIP+1)))
session=ov.OV5640Session(ROOT/'sessions')
auth='Bearer '+session.pairing['pairing_key']
reject('wrong_auth',lambda:session.ingest(b'x','Bearer wrong',session.session_id))
assert session.claimed is False
reject('wrong_session',lambda:session.ingest(b'x',auth,'other'))
assert session.claimed is False
path=export_notebook('http://192.168.2.89:8771',ROOT)
nb=json.loads(path.read_text(encoding='utf-8'))
source=''.join(nb['cells'][1]['source'])
ast.parse(source,feature_version=(3,8))
assert source.index("scope['check_conditions'](conditions)")<source.index('root.mkdir()')
assert 'board.run(base/' in source and nb['cells'][1]['execution_count'] is None
rows.append(dict(test='notebook_python38_and_confirmation_before_hardware',status='PASS'))
fixture=ov.RELEASE/'cpu_tests_999eaf60/42feb0159e'
files={str(p.relative_to(fixture)).replace('\\','/'):p.read_bytes() for p in fixture.rglob('*') if p.is_file()}
assert json.loads(files['RUN_CONTEXT.json'])['evidence']=='CPU_MOCK_ONLY'
result=session.ingest(archive(files),auth,session.session_id)
assert result['status']=='FINISHED' and result['evidence']=='CPU_MOCK_ONLY'
packet=session.frame()
assert packet['acceptance']['state_words_compared']==45669 and packet['acceptance']['mismatch_words']==0
assert len(packet['spatial']['values'])==5768 and len(packet['flow'])==2 and len(packet['flow'][0])==721
assert packet['flow_binding']['full_state_sha256']==packet['full_state_sha256']
assert packet['board_connection']=='NOT_CONNECTED' and packet['elapsed_seconds'] is None
assert session.latest(-1)['frame'] and session.latest(1)['frame'] is None
assert ov.sha(session.source_frame(0,packet['run_id'],packet['full_state_sha256']))==packet['source']['pixel_png_sha256']
reject('source_mixed_state',lambda:session.source_frame(0,packet['run_id'],'wrong'))
geometry=session.projection()
assert len(geometry['coordinates_uv'])==721 and len(session.cache())>0
(ROOT/'DISPLAY.json').write_text(json.dumps(packet),encoding='utf-8')
(ROOT/'STATUS.json').write_text(json.dumps(session.status()),encoding='utf-8')
(ROOT/'PROJECTION.json').write_text(json.dumps(geometry),encoding='utf-8')
rows.append(dict(test='saved_cpu_fixture_full_state_official_decoder_projection_and_source',status='PASS'))
reject('duplicate_no_retry',lambda:session.ingest(archive(files),auth,session.session_id))
assert session.packet is None and session.phase=='FAILED'
bad=ov.OV5640Session(ROOT/'sessions')
reject('in_doubt_no_display',lambda:bad.ingest(archive(dict(files,**{'IN_DOUBT.json':b'{}'})),auth,bad.session_id))
assert bad.packet is None
# A second corrupted-result case stops before the oracle/decoder.
corrupt=ov.OV5640Session(ROOT/'sessions')
reject('missing_full_state',lambda:corrupt.ingest(archive({'RESULT.json':b'{}'}),auth,corrupt.session_id))
assert corrupt.packet is None
report=dict(status='PASS_CPU_SOFTWARE_ONLY',tests=rows,passed=len(rows),board_operations=0,
            GPU_operations=0,camera_operations=0,gui_service_started=False,
            physical_camera_and_continuous_60s='NOT_VERIFIED',result_directory=str(ROOT),
            packet_sha256=ov.sha((ROOT/'DISPLAY.json').read_bytes()))
(ROOT/'RESULT.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
