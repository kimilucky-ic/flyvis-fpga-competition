# LINE2 冷启动初始化：你手动执行一次；1次A3R1加载、1次DMA初始化复位、2次CMA分配；0次STEP
# 仅当前boot和内核；失败即停，不重跑；不启动GPU、摄像头或板端监听。
from pathlib import Path
import hashlib,json,zipfile,importlib.util,sys
line2_init_archive=Path.cwd()/'line2_fresh_init_e82a95af3a0a47ca88ae60d2b341fa33.zip'
assert hashlib.sha256(line2_init_archive.read_bytes()).hexdigest()=='68709e8154e4a14b2e02d06b33bb7b027178feee155661489f06ff947f400e23', "Initialization ZIP SHA mismatch"
line2_init_root=Path.cwd()/'line2_fresh_init_e82a95af3a0a47ca88ae60d2b341fa33'
assert not line2_init_root.exists(), "Initialization directory exists; stop, do not retry"
assert not any(n.endswith('_service_instance') and hasattr(v,'driver') for n,v in list(globals().items())), "Existing service owner; stop"
with zipfile.ZipFile(line2_init_archive) as z:
    assert all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in z.namelist())
    line2_init_root.mkdir();z.extractall(line2_init_root)
assert hashlib.sha256((line2_init_root/'INIT_PLAN.json').read_bytes()).hexdigest()=='4ebc66d32dff95616c34dd34b9318afae01e2135fac51b40c0d8ed880283df5a', "Exact initialization plan changed"
line2_init_config=json.loads((line2_init_root/'INIT_CONFIG.json').read_text(encoding='utf8'))
line2_init_runtime=json.loads((line2_init_root/'RUNTIME_SHA256.json').read_text(encoding='utf8'))
line2_loader_spec=importlib.util.spec_from_file_location('line2_fresh_loader_e82a95af3a0a47ca88ae60d2b341fa33',line2_init_root/'prepare_camera.py')
line2_loader=importlib.util.module_from_spec(line2_loader_spec);line2_loader_spec.loader.exec_module(line2_loader)
line2_init_package=line2_loader.load_pinned_package(line2_init_root,line2_init_config,line2_init_runtime)
line2_initializer_spec=importlib.util.spec_from_file_location('line2_initializer_e82a95af3a0a47ca88ae60d2b341fa33',line2_init_root/'fresh_initializer.py')
line2_initializer=importlib.util.module_from_spec(line2_initializer_spec);line2_initializer_spec.loader.exec_module(line2_initializer)
line2_fresh_initialized=line2_initializer.initialize(line2_init_root,line2_init_config,line2_init_package)
print('LINE2_FRESH_INITIALIZED '+json.dumps(line2_fresh_initialized.receipt,sort_keys=True))
