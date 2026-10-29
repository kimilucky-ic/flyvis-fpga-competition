"""PC only: bind the user's actual initialization receipt to one new scope."""
import ast,base64,hashlib,json,sys,zipfile
from pathlib import Path
P=Path(__file__).resolve().parent;G=P.parents[1];sys.path.insert(0,str(G))
from joint_camera_bundle import build
from live_protocol import load,sha,write
receipt={"bit_sha256":"b607ea58005046f09f01bc7359c673dbd5e40b4de12b4169fca79ce88e43fd16","boot_id":"35df570f-b50d-4cfc-aafc-0e35baf651df","commits":0,"dst_address":939819008,"dst_bytes":23072,"hwh_sha256":"54d271dc8aff904a50ca4fb0ff433f1810b0d486cf80f1daed2c204bc88d084c","initialization_capture_sha256":"386aab9e73f6fcf749d2acdc4654e3725160a9c38f7925da7528d7fc1db052f8","initialization_plan_sha256":"4ebc66d32dff95616c34dd34b9318afae01e2135fac51b40c0d8ed880283df5a","initialization_run_id":"e82a95af3a0a47ca88ae60d2b341fa33","kernel_file":"kernel-4417274b-c932-4454-9872-47b19244e213.json","mode":"MANUAL_FRESH_INIT_THEN_READ20/v1","neural_listeners_started":0,"new_allocations":2,"new_loads":1,"new_resets":1,"requests":0,"src_address":939917312,"src_bytes":69216}
meta=load(P/'INITIALIZATION_PACKAGE.json')
assert all(receipt[k]==meta[v] for k,v in (('initialization_run_id','run_id'),('initialization_plan_sha256','plan_sha256'),('boot_id','boot_id'),('kernel_file','kernel_file')))
out=P/'actual_camera32';out.mkdir(exist_ok=False)
write(out/'ACTUAL_INITIALIZATION_RECEIPT.json',receipt)
root,archive=build(out/'prepared_bundles',fresh=receipt)
scope=load(root/'scope.json');config=load(root/'PRIVATE_CONFIG.json')
assert scope['max_steps']==32 and scope['recording_required_before_camera'] and scope['capture_duration_s']==30
with zipfile.ZipFile(archive) as z:
    for n,d in load(root/'RUNTIME_SHA256.json').items():assert hashlib.sha256(z.read(n)).hexdigest()==d,n
cell='''# LINE2 最后准备：只读20项；0加载、0复位、0新分配；完成后由你点GUI启动32步
# 必须使用刚才的line2_fresh_initialized对象；不要再运行初始化格。
from pathlib import Path
import base64,hashlib,json,zipfile,importlib.util
assert 'line2_fresh_initialized' in globals(), "Current initialization object missing; stop"
assert line2_fresh_initialized.receipt==%r, "Initialization receipt changed; stop"
line2_camera_archive=Path.cwd()/%r
assert not line2_camera_archive.exists(), "Camera package exists; stop, do not retry"
line2_camera_archive.write_bytes(base64.b64decode(%r,validate=True))
assert hashlib.sha256(line2_camera_archive.read_bytes()).hexdigest()==%r, "Camera ZIP SHA mismatch"
line2_camera_root=Path.cwd()/%r
assert not line2_camera_root.exists(), "Camera run directory exists; stop"
with zipfile.ZipFile(line2_camera_archive) as z:
    assert all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in z.namelist())
    line2_camera_root.mkdir();z.extractall(line2_camera_root)
line2_camera_spec=importlib.util.spec_from_file_location(%r,line2_camera_root/'prepare_camera.py')
line2_camera_entry=importlib.util.module_from_spec(line2_camera_spec);line2_camera_spec.loader.exec_module(line2_camera_entry)
camera3_bundle,camera3_service_instance=line2_camera_entry.run(line2_camera_root,line2_fresh_initialized)
'''%(receipt,archive.name,base64.b64encode(archive.read_bytes()).decode(),sha(archive),'CAMERA3_'+scope['run_id'],'line2_camera_entry_'+scope['run_id'])
ast.parse(cell,feature_version=(3,8));(out/'next_camera_prepare_cell.py').write_text(cell,encoding='utf8')
write(out/'PREPARATION.json',dict(status='PC_PACKAGE_READY_WAITING_USER_READ20_NOT_NEURAL_RUN',run_id=scope['run_id'],session_id=scope['session_id'],
    boot_id=scope['boot_id'],scope_sha256=sha(root/'scope.json'),root=str(root),archive=str(archive),archive_sha256=sha(archive),
    end_utc=scope['end_utc'],max_steps=32,capture_duration_s=30,cell=str(out/'next_camera_prepare_cell.py'),
    initialization_receipt_source='USER_MANUAL_RESULT_PENDING_SIGNED_PREPARATION_VALIDATION',board_actions_by_agent=0,
    user_GUI_start_required=True,recording_required_before_camera=True))
print(json.dumps(load(out/'PREPARATION.json'),indent=2))
