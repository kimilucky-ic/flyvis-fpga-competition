"""Resume PC admission for the valid, never-started 2050 camera scope."""
import ast,base64,hashlib,json,shutil,sys,time,uuid
from pathlib import Path
P=Path(__file__).resolve().parent;G=P.parent.parent;sys.path.insert(0,str(G))
from live_protocol import load,sha,write
from joint_camera_controller import execute,source_pins
from joint_camera_preparation import prepare_and_execute,verify_prepared_handoff
from launch_recovery import gui_port_available

original=G/'runtime/joint_manual/c7612f01667b89a3ca0293138f77c8af/2050d74ea5eb4948b37c9c687ac2733f'
scope=load(original/'scope.json')
assert scope['run_id']=='2050d74ea5eb4948b37c9c687ac2733f' and scope['source_sha256']==source_pins(),'RECONNECT_FROZEN_SOURCE_CHANGED'
assert not (G/'runtime/joint'/scope['session_id']).exists(),'RECONNECT_PC_ALREADY_EXECUTED'
verify_prepared_handoff(load(original/'hardware_handoff.json'),scope,original)
gui_port_available()  # Before asking the operator to touch anything.
attempt=P/('pc_reconnect_'+uuid.uuid4().hex);attempt.mkdir()
for n in ('scope.json','PRIVATE_CONFIG.json','HARDWARE_DECLARATION.json'):
    shutil.copyfile(original/n,attempt/n)
raw=(P/'reconnect_prestart.py').read_bytes();digest=hashlib.sha256(raw).hexdigest()
cell=('''# LINE2 电脑连接恢复：当前2050会话；0加载/复位/分配/MMIO/DMA/神经计算
import base64,hashlib,importlib.util
from pathlib import Path
assert camera3_service_instance.config['run_id']=='2050d74ea5eb4948b37c9c687ac2733f','Current service changed; stop'
reconnect_bytes=base64.b64decode(%r,validate=True)
assert hashlib.sha256(reconnect_bytes).hexdigest()==%r,'Reconnect source changed'
reconnect_path=Path.cwd()/%r
assert not reconnect_path.exists(),'Reconnect already attempted; stop'
reconnect_path.write_bytes(reconnect_bytes)
reconnect_spec=importlib.util.spec_from_file_location(%r,reconnect_path)
reconnect_module=importlib.util.module_from_spec(reconnect_spec);reconnect_spec.loader.exec_module(reconnect_module)
reconnect_module.reconnect(camera3_bundle,camera3_service_instance,'2050d74ea5eb4948b37c9c687ac2733f')
'''%(base64.b64encode(raw).decode(),digest,'PC_RECONNECT_'+attempt.name+'.py',attempt.name))
ast.parse(cell,feature_version=(3,8));(attempt/'next_board_cell.py').write_text(cell,encoding='utf8')
write(P/'RECONNECT_READY.json',dict(run_id=scope['run_id'],session_id=scope['session_id'],attempt=str(attempt),
    cell=str(attempt/'next_board_cell.py'),source_sha256=digest,status='WAIT_USER_SOFTWARE_RECONNECT_NO_PL_ACTION'))
print('PC_RECONNECT_WAITING '+str(attempt/'next_board_cell.py'),flush=True)
def admitted_execute(*args,**kwargs):
    # A competing offline preview must not kill a valid prepared clock again.
    while True:
        kwargs['pc_clock'].check()
        try:gui_port_available();break
        except ValueError:time.sleep(.5)
    execute(*args,**kwargs)
prepare_and_execute(attempt,admitted_execute)
