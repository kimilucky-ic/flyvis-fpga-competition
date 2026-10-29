"""Bounded CPU comparison using unchanged real data and the saved pre-edit code.

Each mode is run in a separate Python process. The baseline loader sets __file__
to the original location so original absolute data roots remain unchanged. No
GUI/socket, worker, camera, decoder or neural inference is launched.
"""
import argparse
import importlib.abc
import importlib.util
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GUI = ROOT/'gui_v1'
sys.path.insert(0, str(GUI))
parser = argparse.ArgumentParser()
parser.add_argument('mode', choices=['baseline','cold_cache','warm_cache','cold_cache_final','warm_cache_final'])
args = parser.parse_args()


if args.mode == 'baseline':
    class BeforeLoader(importlib.abc.Loader):
        def init__(self, path, real):self.path, self.real = path, real
        def create_module(self, spec):return None
        def exec_module(self, module):
            module.__file__ = str(self.real)
            exec(compile(self.path.read_bytes(), str(self.real), 'exec'), module.__dict__)

    class BeforeFinder(importlib.abc.MetaPathFinder):
        def find_spec(self, fullname, path=None, target=None):
            if '.' in fullname:return None
            before = HERE/'before/gui_v1'/f'{fullname}.py'
            if before.is_file():
                return importlib.util.spec_from_loader(fullname, BeforeLoader(before, GUI/f'{fullname}.py'))
    sys.meta_path.insert(0, BeforeFinder())

cache_path = HERE/('benchmark_cache_final.json' if args.mode.endswith('_final') else 'benchmark_cache.json')
if args.mode.startswith('cold_cache'):
    assert not cache_path.exists(), 'Preserve previous cache; no automatic benchmark rerun'
if args.mode.startswith('warm_cache'):
    assert cache_path.is_file(), 'Cold-cache preparation required'
start = time.perf_counter()
import startup_cache
startup_cache.configure(args.mode != 'baseline', cache_path)
import data_store
import server
import competition_replay
import competition_frames
import competition_explanation
captured = {}
for module, name, key in [(competition_replay,'LazyCompetition','replay'),
                          (competition_frames,'CompetitionFrames','frames'),
                          (competition_explanation,'CompetitionExplanation','explanation')]:
    original = getattr(module, name)
    def capture(*a, _original=original, _key=key, **kw):
        value = _original(*a, **kw)
        captured[_key] = value
        return value
    setattr(module, name, capture)
store = data_store.DataStore() if args.mode == 'baseline' else data_store.LazyDataStore()
handler = server.handler_factory(store)
ready = time.perf_counter() - start
replay = captured['replay'].get()
metadata = replay.metadata()
pack = captured['frames']
pack.metadata()
captured['explanation'].binary(competition_replay.RUN)
pack.render(dict(run_id=competition_replay.RUN,activity_sha256=competition_replay.ACTIVITY_SHA,
                 frame_index=0,activity_time_s=metadata['activity_time_s'][0],request_id='startup-benchmark',
                 type_filter='all',selected_type='T4a',presentation_profile='light'))
first_frame = time.perf_counter() - start
legacy_before = store.loaded if hasattr(type(store),'loaded') else True
tick = time.perf_counter()
catalog = store.catalog()
legacy_seconds = time.perf_counter() - tick
assert sum(len(d['conditions']) for d in catalog['datasets']) == 55
handler.close_camera()
result = dict(mode=args.mode,service_initialization_s=ready,first_frame_prepared_s=first_frame,
              selected_data_preparation_s=first_frame-ready,legacy_loaded_before_library_open=legacy_before,
              legacy_library_open_s=legacy_seconds,conditions=55,verification_cache=startup_cache.status(),
              scientific_identity=dict(run_id=metadata['run_id'],activity_sha256=metadata['activity_sha256'],
                  arrays={k:v['sha256'] for k,v in metadata['arrays'].items()},
                  framepack_sha256=pack.manifest_sha,means_k217=metadata['means'][217]),
              source='actual saved results, no inference',GUI_started=False,neural_GPU_runs=0,
              camera_started=False,board_connections=0,
              timing_scope='CPU initialization and selected saved first-frame preparation; excludes WebView/process creation and browser paint; warm OS file cache likely')
with (HERE/(args.mode+'.json')).open('x',encoding='utf-8') as stream:
    json.dump(result,stream,indent=2)
print(json.dumps({k:v for k,v in result.items() if k!='scientific_identity'}))
