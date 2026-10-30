"""Runs only in the retained board kernel under the exact new three-step scope.

No construction of an overlay or buffer, no init fallback. The sole Line 2 PC
controller supplies time and receives the actual signed preparation evidence.
"""
import hashlib
import json
from pathlib import Path
import sys
import urllib.request
import importlib.util
import importlib


def load_pinned_package(root,config,runtime):
    root=Path(root).resolve()
    for name,digest in runtime.items():
        path=(root/name).resolve();assert path!=root and root in path.parents and hashlib.sha256(path.read_bytes()).hexdigest()==digest,'BOARD_SOFTWARE_CHANGED'
    # Preserve the failed namespace and its pinned owners. Fresh identical
    # helper bytes load under a new name; no replacement in sys.modules.
    namespace='_line2_camera_'+config['run_id']
    assert namespace not in sys.modules,'BOARD_NAMESPACE_CONSUMED'
    spec=importlib.util.spec_from_file_location(namespace,root/'a3ready/init__.py',submodule_search_locations=[str(root/'a3ready')])
    package=importlib.util.module_from_spec(spec);sys.modules[namespace]=package;spec.loader.exec_module(package)
    return package


def run(root,source_service,expired_service=None):
    root=Path(root).resolve()
    config=json.loads((root/'PRIVATE_CONFIG.json').read_text(encoding='utf-8'))
    scope=(root/'scope.json').read_bytes();plan=(root/'PLAN.json').read_bytes()
    assert hashlib.sha256(scope).hexdigest()==config['scope_sha256'],'BOARD_SCOPE_BYTES_CHANGED'
    runtime=json.loads((root/'RUNTIME_SHA256.json').read_text(encoding='utf-8'))
    package=load_pinned_package(root,config,runtime);namespace=package.__name__
    clock_module=importlib.import_module(namespace+'.clock')
    prepare_module=importlib.import_module(namespace+'.prepare')
    control_module=importlib.import_module(namespace+'.control2')
    sign,verified,require=control_module.sign,control_module.verified,control_module.require
    ep=config['pc_authority_endpoint']
    def request(path,packet):
        raw=json.dumps(packet).encode()
        req=urllib.request.Request('http://'+ep['host']+':'+str(ep['port'])+path,data=raw,headers={'Content-Type':'application/json'})
        with urllib.request.urlopen(req,timeout=4) as response:
            data=response.read(65537);require(len(data)<=65536,'CLOCK_RESPONSE_BOUND')
        return json.loads(data)
    handshake=clock_module.BoardClockHandshake(config)
    clock=handshake.accept(request('/clock',handshake.challenge()))
    if config.get('transfer_from_expired_run'):
        require(expired_service is not None,'EXPIRED_OWNER_REQUIRED')
        spec=importlib.util.spec_from_file_location(namespace+'_transfer',root/'retained_transfer.py')
        transfer=importlib.util.module_from_spec(spec);spec.loader.exec_module(transfer)
        bundle=transfer.prepare(root/'board_run',expired_service,source_service,config,scope,plan,clock,package)
    else:
        require(expired_service is None,'UNDECLARED_EXPIRED_OWNER')
        bundle=prepare_module.prepare_retained(root/'board_run',source_service,config,scope,plan,clock)
    service=bundle.bind_service();service.start()
    # No STEP, reset or allocation here. This status is from the newly running
    # real service after prepare_retained's exact twenty reads.
    packet=sign(dict(schema='flyvis-camera-retained-prepared/v1',binding=clock.fixed,
        preparation_receipt=bundle.receipt,clock_receipt=clock.receipt(config),status=service.status('00'*16)),config['control_key'])
    ack=verified(request('/prepared',packet),config['control_key'])
    require(ack.get('ok') is True and ack['binding']==clock.fixed,'PC_PREPARATION_RECEIPT_NOT_CONFIRMED')
    print('CAMERA_BOARD_PREPARED requests=0 commits=0; waiting for sole LINE2 controller',flush=True)
    return bundle,service
