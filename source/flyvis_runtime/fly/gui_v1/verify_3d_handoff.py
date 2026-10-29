"""Independent stdlib-only relocated package and HTTP checks; no inference."""
import argparse
from datetime import datetime, timezone
import hashlib
from http.server import ThreadingHTTPServer
import importlib.util
import json
from pathlib import Path
import sys
import threading
from urllib.error import HTTPError
from urllib.request import Request, urlopen
import zipfile


def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(2097152),b''):h.update(b)
    return h.hexdigest()


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--archive',type=Path,required=True)
    p.add_argument('--relocated',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    assert not args.relocated.exists() and not args.output.exists()
    args.relocated.mkdir(parents=True)
    with zipfile.ZipFile(args.archive) as archive:
        for name in archive.namelist():
            assert (args.relocated/name).resolve().is_relative_to(args.relocated.resolve())
            assert not Path(name).is_absolute()
        archive.extractall(args.relocated)
    roots=list(args.relocated.iterdir());assert len(roots)==1
    root=roots[0]
    spec=importlib.util.spec_from_file_location('handoff_backend',root/'backend/frozen_server.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    # This backend imports only Python stdlib and resolves all runtime files under root.
    routes,snapshot,count=module.load_package(root)
    manifest=json.loads((root/'package_manifest.json').read_text('utf-8'))
    for item in manifest['files']:
        assert sha(root/item['path'])==item['sha256']
    origin=json.loads((root/'original_source_inventory.json').read_text('utf-8'))['files']
    for item in origin:assert sha(root/item['packaged_path'])==item['sha256']
    assert snapshot['conditions']==55 and snapshot['steps']==800 and snapshot['dt_s']==.005
    assert snapshot['display_kind']=='offline_replay' and snapshot['online_GPU_service']=='not_connected'
    handler=module.handler_factory(root,routes,snapshot);handler.log_message=lambda *a:None
    server=ThreadingHTTPServer(('127.0.0.1',0),handler)
    worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
    url=f'http://127.0.0.1:{server.server_port}'
    bytes_verified=0
    try:
        for i,(route,item) in enumerate(routes.items()):
            with urlopen(url+route,timeout=20) as r:
                assert r.status==200 and r.headers['X-Package-Mode']=='accepted-result-offline-replay'
                h=hashlib.sha256()
                while True:
                    b=r.read(1048576)
                    if not b:break
                    h.update(b);bytes_verified+=len(b)
                assert h.hexdigest()==item['sha256'],route
                for k,v in item['headers'].items():assert r.headers[k]==v
            if i%500==0:print(f'Relocated HTTP {i+1}/{len(routes)}',flush=True)
        catalog=json.load(urlopen(url+'/api/catalog'))
        assert {d['id']:len(d['conditions']) for d in catalog['datasets']}==snapshot['datasets']
        status=json.load(urlopen(url+'/api/phase3'))
        assert status['status']=='ready' and status['FPGA_Replacement']['available'] is False
        cmp=status['comparisons'][0]
        assert cmp['comparison_id']==snapshot['comparison_id'] and cmp['display_kind']=='offline_replay'
        # Real source digest matches same package origin, not developer's old directory.
        for mode in ['Full_GPU','Python_Replacement']:
            assert cmp['modes'][mode]['source_activity_sha256'] in {o['sha256'] for o in origin}
        negatives=[]
        requests=[('GPU submit',Request(url+'/api/inference',data=b'{}',headers={'Content-Type':'application/json'}),503),('GPU poll',url+'/api/inference/missing_job',503),('FPGA result',url+'/api/phase3/comparisons/'+snapshot['comparison_id']+'/FPGA_Replacement/activity.bin',404),('unknown condition',url+'/api/datasets/controlled6/samples/999',404),('path escape',url+'/../../original_source_inventory.json',404)]
        for name,request,expected in requests:
            try:urlopen(request,timeout=10);raise AssertionError(name)
            except HTTPError as error:
                assert error.code==expected
                body=json.load(error)
                if expected==503:assert body['status']=='not_connected' and body['result'] is None
                negatives.append({'test':name,'http':error.code})
        # Tamper only a copied small replay blob, check fail-closed, restore exact bytes.
        sample_route=next(k for k in routes if k.endswith('/samples/0'))
        tamper=root/routes[sample_route]['file'];saved=tamper.read_bytes()
        try:
            tamper.write_bytes(saved+b' ')
            try:urlopen(url+sample_route);raise AssertionError('tampered payload accepted')
            except HTTPError as error:assert error.code==409
        finally:tamper.write_bytes(saved)
    finally:
        server.shutdown();server.server_close();worker.join()
    report={'schema':'flyvis-3d-handoff-independent-acceptance-v1','status':'PASS','utc':datetime.now(timezone.utc).isoformat(),'archive':str(args.archive.resolve()),'archive_sha256':sha(args.archive),'relocated_root':str(root.resolve()),'runtime_source_scope':'package-relative files only; no original project imports or producer path reads','conditions':55,'steps':800,'comparison_id':snapshot['comparison_id'],'files_exact_after_unzip':len(manifest['files']),'original_source_files_byte_exact':len(origin),'HTTP_routes_exact':len(routes),'HTTP_bytes_verified':bytes_verified,'exporter_original_array_values_exact':snapshot['input_and_activity_values_exactly_verified'],'negative_cases':negatives,'tampered_payload_HTTP_409':True,'GUI_GPU_inference':False,'FPGA_execution':False,'test_backend_stopped':True}
    with args.output.open('x',encoding='utf-8') as f:json.dump(report,f,ensure_ascii=False,indent=2,allow_nan=False)
    print(json.dumps(report,ensure_ascii=False),flush=True)


if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8');main()
