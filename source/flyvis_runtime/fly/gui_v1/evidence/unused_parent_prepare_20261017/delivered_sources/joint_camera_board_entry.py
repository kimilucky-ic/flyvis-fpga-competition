"""Runs only in the retained board kernel under the exact new bounded scope.

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


def run(root,source_service,expired_service=None,expired_bundle=None):
    root=Path(root).resolve()
    config=json.loads((root/'PRIVATE_CONFIG.json').read_text(encoding='utf-8'))
    assert config.get('execution_authority')=='APPROVED_BY_HUMAN' and config.get('test_fixture') is not True,'BOARD_ENTRY_REJECTS_CPU_FIXTURE'
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
    if config.get('transfer_from_expired_run') or config.get('completed_parent') or config.get('unused_parent'):
        require(expired_service is not None,'EXPIRED_OWNER_REQUIRED')
        spec=importlib.util.spec_from_file_location(namespace+'_transfer',root/'retained_transfer.py')
        transfer=importlib.util.module_from_spec(spec);spec.loader.exec_module(transfer)
        ancestor=None
        if config.get('completed_parent') or config.get('unused_parent'):
            require(expired_bundle is not None and expired_bundle.driver is expired_service.driver
                and expired_bundle.config==expired_service.config,'COMPLETED_BUNDLE_IDENTITY')
            if config.get('unused_parent'):ancestor=expired_bundle.old_service
        elif config['transfer_from_expired_run']==transfer.NEXT_EXPIRED_RUN:
            require(expired_bundle is not None and expired_bundle.driver is expired_service.driver
                and expired_bundle.config==expired_service.config,'EXPIRED_BUNDLE_IDENTITY')
            ancestor=expired_bundle.old_service
        bundle=transfer.prepare(root/'board_run',expired_service,source_service,config,scope,plan,clock,package,ancestor=ancestor)
    else:
        require(expired_service is None,'UNDECLARED_EXPIRED_OWNER')
        bundle=prepare_module.prepare_retained(root/'board_run',source_service,config,scope,plan,clock)
    adapter=None
    if config.get('ps_durability_policy')=='PS_COMMIT_ACK_DURABLE_TWO_BARRIERS/v1':
        adapter_path=root/'ps_commit_evidence.py'
        require(runtime.get('ps_commit_evidence.py')==config.get('ps_evidence_adapter_sha256'),'PS_ADAPTER_NOT_PINNED_IN_RUNTIME')
        spec=importlib.util.spec_from_file_location(namespace+'_ps_commit_evidence',adapter_path)
        policy_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(policy_module)
        adapter=policy_module.install_before_bind(bundle,scope,importlib.import_module(namespace+'.protocol'),adapter_path)
    service=bundle.bind_service()
    if adapter is not None:
        require(service.evidence is adapter and service.driver.evidence is adapter,'PS_ADAPTER_NOT_ATTACHED_TO_SERVICE')
        adapter.attach_service(service)
    service.start()
    # No STEP, reset or allocation here. This status is from the newly running
    # real service after prepare_retained's exact twenty reads.
    packet=sign(dict(schema='flyvis-camera-retained-prepared/v1',binding=clock.fixed,
        preparation_receipt=bundle.receipt,clock_receipt=clock.receipt(config),status=service.status('00'*16)),config['control_key'])
    ack=verified(request('/prepared',packet),config['control_key'])
    require(ack.get('ok') is True and ack['binding']==clock.fixed,'PC_PREPARATION_RECEIPT_NOT_CONFIRMED')
    print('CAMERA_BOARD_PREPARED requests=0 commits=0; waiting for sole LINE2 controller',flush=True)
    return bundle,service
