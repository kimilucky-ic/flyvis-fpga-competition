"""Actual loopback desktop-backend and on-demand API checks. No window/devices."""
import json
from pathlib import Path
import socket
import sys
import time
from urllib.request import urlopen

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT/'gui_v1'))
from desktop_runtime import DesktopBackend, SessionRecord

backend = DesktopBackend(SessionRecord(HERE/'desktop_backend_test'))
cases = []
start = time.perf_counter()
url = backend.start()
ready = time.perf_counter()-start
port = int(url.rsplit(':',1)[1])
print('DESKTOP_BACKEND_READY', ready, flush=True)


def get(path):
    tick = time.perf_counter()
    with urlopen(url+path,timeout=60) as response:
        raw = response.read()
        print(path, response.status, round(time.perf_counter()-tick, 3), flush=True)
        return json.loads(raw) if 'json' in response.headers['Content-Type'] else raw


try:
    first = get('/api/startup')
    assert not first['dataset_loaded']
    assert all(r['state']=='not_loaded' for r in first['offline_resources'].values())
    assert backend.record.data['conditions'] is None
    cases.append('desktop_shell_does_not_claim_unloaded_data_verified')
    assert get('/api/health')['dataset_state']=='ON_DEMAND'
    assert b'FlyVis' in get('/')
    assert not get('/api/startup')['dataset_loaded']
    cases.append('health_and_static_page_do_not_load_experiments')
    metadata = get('/api/competition')
    assert metadata['run_id']=='2041849d-b1f8-46ad-a059-49b598c19ab2' and metadata['PL_execution'] is False
    pack = get('/api/competition/frames')
    assert pack['frame_count']==485 and pack['brightness_variant']=='C'
    explanation = get('/api/competition/explanation?run='+metadata['run_id'])
    assert len(explanation['frames'])==485
    selected = get('/api/startup')
    assert not selected['dataset_loaded']
    assert selected['offline_resources']['pilot']['state']=='ready'
    assert all(selected['offline_resources'][name]['state']=='not_loaded' for name in ['phase3','workbench','flow','sparse','runner'])
    cases.append('home_loads_only_its_verified_pilot_and_C_frames')
    catalog = get('/api/catalog')
    assert len(catalog['datasets'])==7 and sum(len(d['conditions']) for d in catalog['datasets'])==55
    assert not catalog['unavailable_datasets']
    cases.append('legacy_55_conditions_load_when_requested')
    pilot = get('/api/scientific-pilot')
    assert pilot['status']=='VERIFIED' and pilot['PL_execution'] is False
    sparse = get('/api/scientific-sparse')
    assert sparse['status']=='VERIFIED' and sparse['PL_execution'] is False
    phase3 = get('/api/phase3')
    assert phase3['status']=='ready' and phase3['FPGA_Replacement']['available'] is False
    cases += ['scientific_pilot_unchanged','scientific_B_unchanged','P0_Full_Python_unchanged']
    workbench = get('/api/workbench')
    assert workbench['status']=='READY_FOR_EVIDENCE' and workbench['execution_backend']['connected'] is False
    cases.append('workbench_remains_available_on_demand')
    final = get('/api/startup')
    port = int(url.rsplit(':',1)[1])
finally:
    backend.close()
with socket.socket() as client:
    client.settimeout(1)
    assert client.connect_ex(('127.0.0.1',port))!=0
assert not backend.thread.is_alive()
cases.append('owned_server_and_thread_stop_cleanly')
result = dict(status='PASS_ACTUAL_OFFLINE_HTTP_AND_DESKTOP_BACKEND',cases=cases,backend_ready_s=ready,
              conditions=55,before=first,after_home=selected,after_explicit_requests=final,
              GUI_window_started=False,neural_GPU_runs=0,camera_started=False,board_connections=0)
(HERE/'HTTP_AND_DESKTOP.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({'status':result['status'],'backend_ready_s':ready,'cases':cases}))
