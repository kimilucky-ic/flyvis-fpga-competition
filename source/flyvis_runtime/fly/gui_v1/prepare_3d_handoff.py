"""Build a bounded local frontend/data handoff from accepted sources, not inference."""
import argparse
from datetime import datetime, timezone
import hashlib
from http.server import ThreadingHTTPServer
import json
from pathlib import Path
import shutil
import sys
import threading
from urllib.request import urlopen
from urllib.error import HTTPError

import numpy as np

from data_store import DataStore, ROOT, sha256
from phase3_adapter import Phase3Adapter
from server import handler_factory

SUPPORT = ROOT/'gui_v1/handoff_support'
sys.path.insert(0, str(SUPPORT))
from frozen_server import route_key


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if json.loads(path.read_text('utf-8')) == value:
            return
        raise ValueError(f'Existing artifact differs: {path}')
    with path.open('x', encoding='utf-8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2, allow_nan=False)


def main():
    args = argparse.ArgumentParser()
    args.add_argument('--output', type=Path, required=True)
    args.add_argument('--resume-source-copy', action='store_true')
    args = args.parse_args()
    dest = args.output.resolve()
    resume = args.resume_source_copy and dest.exists() and (dest/'original_source_inventory.json').exists() and not (dest/'package_manifest.json').exists() and not (dest/'data/routes.json').exists()
    if not dest.is_relative_to(ROOT/'deliverables') or dest.exists() and not resume:
        raise ValueError('Use a new directory within fly/deliverables; never overwrite')
    print('Validate current real sources and both accepted modes', flush=True)
    store = DataStore()
    p3 = Phase3Adapter(store)
    assert sum(len(d.conditions) for d in store.datasets.values()) == 55
    assert p3.status()['status'] == 'ready' and len(p3.packages) == 1
    package = next(iter(p3.packages.values()))
    baseline = json.loads((ROOT/'gui_v1/evidence/phase3/baseline.json').read_text('utf-8'))
    sources = dict(baseline['source_sha256'])
    for mapping in [p3.input.checked, package.checked]:
        for path, digest in mapping.items():
            path = str(path)
            assert path not in sources or sources[path] == digest
            sources[path] = digest
    dest.mkdir(parents=True, exist_ok=resume)
    origin_entries, payload_by_sha = [], {}
    for i, (name, digest) in enumerate(sources.items()):
        original = Path(name)
        assert original.is_relative_to(ROOT.parent) and sha256(original) == digest
        relative = 'source_data/' + original.relative_to(ROOT.parent).as_posix()
        target = dest/relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            shutil.copy2(original, target)
        assert sha256(target) == digest
        payload_by_sha.setdefault(digest, relative)
        origin_entries.append({'original_path':name,'packaged_path':relative,'bytes':target.stat().st_size,'sha256':digest})
        if i % 400 == 0: print(f'Copied verified source {i+1}/{len(sources)}', flush=True)
    write_json(dest/'original_source_inventory.json', {'schema':'flyvis-source-copy-v1','original_files_modified':False,'files':origin_entries})
    for name in ['index.html','app.js','styles.css','phase3.js']:
        (dest/'viewer').mkdir(exist_ok=True)
        shutil.copy2(ROOT/'viewer'/name,dest/'viewer'/name)
    # Only the handoff copy receives the optional nonvisual synchronization bridge.
    html = (dest/'viewer/index.html').read_text('utf-8')
    (dest/'viewer/index.html').write_text(html.replace('</head>', '  <script src="/visualization_bridge.js" defer></script>\n</head>'),encoding='utf-8')
    shutil.copy2(SUPPORT/'visualization_bridge.js',dest/'viewer/visualization_bridge.js')
    (dest/'backend').mkdir(exist_ok=True);shutil.copy2(SUPPORT/'frozen_server.py',dest/'backend/frozen_server.py')
    shutil.copy2(SUPPORT/'start.cmd',dest/'start.cmd')
    (dest/'docs').mkdir(exist_ok=True);shutil.copy2(SUPPORT/'3D_DESIGN_BRIEF.md',dest/'docs/3D_DESIGN_BRIEF.md')
    (dest/'licenses').mkdir(exist_ok=True);shutil.copy2(ROOT/'team_distribution/package/vendor/license-FlyVis.txt',dest/'licenses/license-FlyVis.txt')
    for path in (ROOT/'gui_v1').iterdir():
        if path.is_file() and path.suffix in ['.py','.json','.md','.cs','.ps1','.lock','.ico','.js']:
            (dest/'reference_gui').mkdir(exist_ok=True);shutil.copy2(path,dest/'reference_gui'/path.name)
    shutil.copytree(ROOT/'gui_v1/evidence',dest/'evidence/original_GUI_acceptance',dirs_exist_ok=resume)
    routes = {}
    source_download_aliases = []
    handler = handler_factory(store)
    handler.log_message = lambda *args: None
    server = ThreadingHTTPServer(('127.0.0.1',0),handler)
    worker = threading.Thread(target=server.serve_forever,daemon=True);worker.start()
    base = f'http://127.0.0.1:{server.server_port}'
    def capture(url, source_sha=None):
        key = route_key(url)
        if key in routes:
            return (dest/routes[key]['file']).read_bytes()
        try:
            with urlopen(base+url,timeout=20) as response:
                body = response.read();mime = response.headers['Content-Type']
                headers = {k:v for k,v in response.headers.items() if k.lower() in ['x-source-sha256','x-comparison-id','x-run-id','x-display-kind']}
        except HTTPError as error:
            if error.code != 404 or not source_sha or source_sha not in payload_by_sha:
                raise ValueError(f'Cannot export {url}: HTTP {error.code}') from error
            # A declared original file can have a hyphen unsupported by the old server regex.
            body = (dest/payload_by_sha[source_sha]).read_bytes()
            assert hashlib.sha256(body).hexdigest() == source_sha
            mime = 'application/octet-stream';headers={'X-Source-SHA256':source_sha}
            source_download_aliases.append(url)
        digest = hashlib.sha256(body).hexdigest()
        relative = payload_by_sha.get(digest)
        if not relative:
            relative = 'data/blobs/'+digest
            target = dest/relative;target.parent.mkdir(parents=True,exist_ok=True)
            if target.exists():
                assert sha256(target) == digest
            else:
                with target.open('xb') as f:f.write(body)
            payload_by_sha[digest] = relative
        routes[key] = {'file':relative,'sha256':digest,'bytes':len(body),'mime':mime,'headers':headers}
        return body
    actual_values = 0
    try:
        for url in ['/api/health','/api/catalog','/api/adapters','/api/phase3','/api/phase3/input']:
            capture(url)
        frozen_input = capture('/api/phase3/input/stimulus.bin')
        assert np.array_equal(np.frombuffer(frozen_input,dtype='<f4').reshape(800,721),p3.input.stimulus[0,:,0])
        for d in store.datasets.values():
            info = json.loads(capture('/api/datasets/'+d.id))
            for item in info['files']+info['official_metrics'].get('files',[]):capture(item['url'],item['sha256'])
            capture(info['manifest_url'])
            for index, condition in enumerate(d.conditions):
                sample = json.loads(capture(f'/api/datasets/{d.id}/samples/{index}'))
                stim = np.frombuffer(capture(sample['stimulus']['url']),dtype='<f8').reshape(-1,721)
                activity = np.frombuffer(capture(sample['activity']['url']),dtype='<f4').reshape(-1,65)
                original_input = d.input_array(index) if hasattr(d,'input_array') else d.stimulus[index,:,0]
                assert np.array_equal(stim,original_input) and np.array_equal(activity,d.activity[index])
                actual_values += stim.size+activity.size
            media = info.get('camera') or info.get('controlled_video')
            if media:
                count = media.get('source_frame_count',len(media['source_time_s']))
                samples = range(len(d.conditions)) if '{sample}' in media['frame_url_template'] else [0]
                for sample in samples:
                    for k in range(count):capture(media['frame_url_template'].replace('{sample}',str(sample)).replace('{index}',str(k)))
            for cell in ['T4a','T4b','T4c','T4d','T5a','T5b','T5c','T5d']:
                queries = [(c['sample'],c['intensity']) for c in d.conditions] if d.id=='bar10' else [(0,0),(0,1)]
                for sample,intensity in queries:capture(f'/api/datasets/{d.id}/directions?cell={cell}&intensity={intensity}&sample={sample}')
            print(f'Exported real dataset {d.id} / {len(d.conditions)} conditions',flush=True)
        for k in range(240):capture(f'/api/phase3/input/frames/{k}.png')
        comp = '/api/phase3/comparisons/'+p3.input.comparison_id
        capture(comp)
        for mode in ['Full_GPU','Python_Replacement']:
            values = np.frombuffer(capture(f'{comp}/{mode}/activity.bin'),dtype='<f4').reshape(800,65)
            assert np.array_equal(values,package.arrays[mode][:,p3.input.central_ids])
            actual_values += values.size
    finally:
        server.shutdown();server.server_close();worker.join()
    write_json(dest/'data/routes.json',routes)
    snapshot = {'schema':'flyvis-3d-handoff-snapshot-v1','created_utc':datetime.now(timezone.utc).isoformat(),'display_kind':'offline_replay','source_execution':'actual accepted producer runs','conditions':55,'datasets':{d.id:len(d.conditions) for d in store.datasets.values()},'comparison_id':p3.input.comparison_id,'steps':800,'dt_s':.005,'routes_sha256':sha256(dest/'data/routes.json'),'routes':len(routes),'original_source_files':len(sources),'source_bytes':sum(e['bytes'] for e in origin_entries),'input_and_activity_values_exactly_verified':actual_values,'FPGA_available':False,'online_GPU_service':'not_connected','neural_inference_executed_by_exporter':False,'runtime_requires':'Python >=3.10 stdlib only','producer_absolute_paths':'provenance only; runtime uses package-relative verified replay routes'}
    write_json(dest/'data/snapshot.json',snapshot)
    (dest/'README.md').write_text('# FlyVis 3D Handoff\n\n真实数据与已验收GUI的独立视觉改版包。双击start.cmd；需要Python3.10+，无第三方运行依赖。\n\n先读docs/3D_DESIGN_BRIEF.md。只修改viewer；backend/data/source_data/evidence保持原身份。原55条件与固定动画Full/Python800步均可回放，GPU未连接、FPGA不可用。\n\nsource_data为原文件同字节副本；reference_gui只供源逻辑参考，不用原C盘路径启动。data是同数组HTTP序列化快照，非新推理。启动会校验只读包与路由数据，前端允许编辑。正式模型/回路/摄像头/FPGA源码不在运行依赖中。\n\n当前生产FlyVis.exe继续保留在原项目；此包用于视觉开发，改版后再对接桌面封装。所有3D空间图、材质和示意动画须遵守数据/证据边界。\n',encoding='utf-8')
    write_json(dest/'evidence/build_report.json',dict(snapshot,status='PASS_ACTUAL_SOURCE_SNAPSHOT_EXPORT',original_frontend_sha256={n:sha256(ROOT/'viewer'/n) for n in ['index.html','app.js','styles.css','phase3.js']},packaged_index_change='only adds visualization_bridge.js script',declared_verified_source_download_aliases=source_download_aliases))
    files=[]
    for path in sorted(dest.rglob('*')):
        if path.is_file():
            relative=path.relative_to(dest).as_posix()
            files.append({'path':relative,'sha256':sha256(path),'bytes':path.stat().st_size,'role':'editable_frontend' if relative.startswith('viewer/') else 'frozen_data_or_reference'})
    write_json(dest/'package_manifest.json',{'schema':'flyvis-3d-handoff-manifest-v1','files':files})
    print(json.dumps(dict(status='BUILT',directory=str(dest),files=len(files),routes=len(routes),bytes=sum(f['bytes'] for f in files),verified_values=actual_values),ensure_ascii=False),flush=True)


if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
