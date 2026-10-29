"""Finalize read-only source identity; never import neural or board launchers."""
import ast
import difflib
import hashlib
import json
from pathlib import Path
import sys

OUT=Path(__file__).resolve().parent
HERE=OUT.parents[1]
ROOT=HERE.parent
sys.path.insert(0,str(HERE))
import line11_ddr_notebook as fixed

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

notebook=HERE/fixed.NAME
nb=json.loads(notebook.read_bytes())
entry=nb['metadata']['flyvis_pure_fpga']
assert entry['source']==fixed.BOARD_SOURCE
assert entry['source_sha256']==hashlib.sha256(entry['source'].encode()).hexdigest()
assert entry['pairing_key']==fixed.installation()['pairing_key']
ast.parse(entry['source'],feature_version=(3,8))
cells=[c for c in nb['cells'] if c['cell_type']=='code']
assert len(cells)==1
ast.parse(''.join(cells[0]['source']),feature_version=(3,8))

preserved={}
previous=HERE/'evidence/line11_ddr485_on60_20261018/final_sources'
for name in ('line11_ddr_board.py','line11_ddr_bridge.py','line11_ddr_plan.py',
             'line11_ddr_start.py','line11_ddr_flow.py','line11_ddr_camera.py','line11_stream.py'):
    if (previous/name).exists():
        assert (HERE/name).read_bytes()==(previous/name).read_bytes(), 'Original changed: '+name
        preserved[name]=sha(HERE/name)
for path,expected in [(ROOT/'FlyVis.exe','30213d96511813f31d559df4b5af9c856eb243cad5d572d7841f5c473132fc7a'),
                      (HERE/'FlyVis摄像头联合实验.ipynb','e94dd363d7c12bcfd77873830425941d923f5dc880913906e24b72f8736d3b4a')]:
    assert sha(path)==expected, 'Other camera entry changed'
    preserved[path.name]=expected

paths=[HERE/'server.py',HERE/'line11_ddr_notebook.py',HERE/'test_line11_ddr_notebook.py',
       HERE/'DESKTOP.md',notebook,ROOT/'flyvisfpga_4b9b8382.cmd']
final=OUT/'final_sources';final.mkdir(exist_ok=True)
for path in paths:
    if path.suffix!='.ipynb':
        # Keep the private Notebook out of source snapshots; only its digest is public evidence.
        (final/path.name).write_bytes(path.read_bytes())
before=(OUT/'before_sources/server.py').read_text(encoding='utf-8')
after=(HERE/'server.py').read_text(encoding='utf-8')
(OUT/'SERVER.diff').write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),
    fromfile='before/server.py',tofile='after/server.py')),encoding='utf-8')
result=dict(status='PASS_SOFTWARE_ONLY_FIXED_PURE_FPGA_NOTEBOOK_BOARD_PENDING',
    evidence_level='CPU_IN_MEMORY_HTTP_AND_SAVED_485_PLAN_PACKAGE_NO_EXECUTION',
    unique_tests_passed=8,logs=['CPU_NOTEBOOK_FINAL.log','CPU_ORIGINAL_485_PACKAGE.log'],
    initial_environment_failure='CPU_NOTEBOOK.log: sandbox Temp ACL denied; fixtures moved to workspace; no production failure',
    original_package_test='Original DdrGuiSession.package(485) read/pack/download/extract; fake board entry; no neural computation',
    notebook=dict(path=str(notebook),sha256=sha(notebook),single_code_cell=True,python38_syntax=True,
                  static_PC_pairing_matches=True,pairing_value_not_in_report=True),
    PC_entry=str(ROOT/'flyvisfpga_4b9b8382.cmd'),board_entry='run fixed Notebook one cell; confirm 准备',
    mode='FULL_NETWORK_FPGA',neural_nodes=45669,steps=485,dt_s=.005,model_duration_s=2.425,
    input_kind='FROZEN_ON60_DIGITAL',official_flow='ORIGINAL_DECODERGAVP_CPU_AFTER_RECEIVED_STATE',
    launches=dict(GUI=0,GPU=0,camera=0,board=0,listeners=0),
    verified_original_sources=preserved,
    files=[dict(path=str(p),sha256=sha(p)) for p in paths],
    pending=['Actual 485-step board/PC delivery, official flow, browser display and timing',
             'Operator must release current board and 8771 workbench before new pure FPGA run',
             'One run per current PC session/kernel; no continuous live camera or 60-second pure FPGA claim'],
    rollback='Restore before_sources/server.py; prior dynamic ZIP + START_DDR.ipynb path unchanged; no firmware/model modifications')
(OUT/'VERIFICATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:result[k] for k in ('status','unique_tests_passed','launches')},ensure_ascii=False))
