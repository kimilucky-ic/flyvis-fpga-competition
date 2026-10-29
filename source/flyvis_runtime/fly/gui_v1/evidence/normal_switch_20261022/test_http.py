import ast,io,json,os,tempfile,sys
from pathlib import Path
from types import SimpleNamespace as NS
from urllib.parse import urlparse,parse_qs
from unittest.mock import patch
sys.path.insert(0,r'C:/Users/hzy72/Documents/ChatGPT/fly/gui_v1')
from operator_selection import Selection
here=Path(sys.path[0]);out=here/'evidence/normal_switch_20261022'
tree=ast.parse((here/'server.py').read_text(encoding='utf-8'));factory=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='handler_factory');handler=next(n for n in factory.body if isinstance(n,ast.ClassDef) and n.name=='Handler');post=next(n for n in handler.body if isinstance(n,ast.FunctionDef) and n.name=='do_POST')
for name,display,ack,expected in [('audit_pending',False,False,409),('board_pending',True,False,409),('normal',True,True,200),('failed',False,False,409)]:
 with tempfile.TemporaryDirectory(dir=out) as d:
  root=Path(d);selection=Selection(root,lambda:NS(metadata_input=lambda:dict(conditions=[dict(condition_id='EDGE_OFF_RIGHT')])));payload=json.dumps(dict(backend='FULL_FPGA',input='scientific28',condition='EDGE_OFF_RIGHT')).encode();replies=[]
  fake=NS(path='/api/operator-selection',client_address=('127.0.0.1',1),headers={'Content-Length':str(len(payload)),'Content-Type':'application/json','Origin':'http://127.0.0.1:8771'},rfile=io.BytesIO(payload),connection=NS(settimeout=lambda _:None),server=NS(server_port=8771),send=lambda v,status=200:replies.append((v,status)))
  stream=NS(claimed=True,camera_live=True,status=lambda:dict(display_complete=display,normal_end_ack=ack,status='FAILED' if name=='failed' else 'FINISHED'))
  env=dict(operator=selection,joint=None,line11_stream=stream,urlparse=urlparse,parse_qs=parse_qs,json=json,Path=Path,os=os)
  exec(compile(ast.Module(body=[post],type_ignores=[]),'ACTUAL_POST_CPU','exec'),env)
  with patch.dict(os.environ,FLYVIS_OPERATOR_STOP=str(root/'STOP.json')):env['do_POST'](fake)
  assert replies[-1][1]==expected,(name,replies)
  assert (root/'NEXT.json').exists()==(expected==200)
  assert (root/'STOP.json').exists()==(expected==200)
print('PASS actual server selection: pending audit/board/failed rejected; normalack allows next')
(out/'HTTP_TEST.json').write_text(json.dumps(dict(evidence='ACTUAL_HANDLER_IN_MEMORY_NO_SOCKETS',cases=4,status='PASS')))
