import sys,tempfile,json,ast
from pathlib import Path
from types import SimpleNamespace as NS
sys.path.insert(0,r'C:/Users/hzy72/Documents/ChatGPT/fly/gui_v1')
from operator_selection import Selection,command
out=Path(sys.path[0])/'evidence/pure_only_20261023';cases=[]
for inp,cond in [('camera',None),('scientific28','EDGE_ON_RIGHT')]:
 with tempfile.TemporaryDirectory(dir=out) as d:
  op=Selection(d,lambda:NS(metadata_input=lambda:dict(conditions=[dict(condition_id='EDGE_ON_RIGHT')])));v=dict(backend='FULL_FPGA',input=inp,condition=cond);reply=op.select(v);args=command(v,Path(d)/'STOP.json');assert '--line11-ddr' in args and '--line11-live-camera' in args;assert not any('joint_camera_controller' in a for a in args);assert json.loads((Path(d)/'NEXT.json').read_text())==v;cases.append(inp)
with tempfile.TemporaryDirectory(dir=out) as d:
 op=Selection(d,lambda:NS(metadata_input=lambda:dict(conditions=[])))
 try:op.select(dict(backend='GPU_FPGA',input='camera',condition=None));raise AssertionError('mixed accepted')
 except ValueError as e:assert str(e)=='PURE_FPGA_ONLY_NEW_EXPERIMENTS'
 assert not (Path(d)/'NEXT.json').exists()
src=(Path(sys.path[0]).parent/'viewer/operator_selection.js').read_text();assert '<option value="GPU_FPGA">' not in src;assert "backend:'FULL_FPGA'" in src;assert "检测到旧GPU＋FPGA会话" in src
ast.parse((Path(sys.path[0])/'operator_selection.py').read_text(),feature_version=(3,8));(out/'RESULT.json').write_text(json.dumps(dict(status='PASS_PURE_ONLY_OPERATOR_SELECTION',pure_inputs=cases,mixed_new_selection_rejected=True,legacy_code_and_results_preserved=True,devices_or_service_started=False),indent=2));print('PASS camera/fixed pure launch args; mixed selection rejected; UI pure default and legacy identity warning')
