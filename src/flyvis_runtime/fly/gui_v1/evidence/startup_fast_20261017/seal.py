"""Seal bounded startup tests and verify saved protected sources; no devices."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
def digest(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()
def read(name):
    return json.loads((HERE / name).read_text(encoding='utf-8-sig'))
def write(name, value):
    (HERE / name).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')

expected_edits = {
    'gui_v1/server.py', 'gui_v1/data_store.py', 'gui_v1/desktop_runtime.py', 'gui_v1/desktop.py',
    'gui_v1/camera_store.py', 'gui_v1/controlled_store.py', 'gui_v1/phase3_adapter.py',
    'gui_v1/scientific_pilot.py', 'gui_v1/scientific_sparse.py', 'gui_v1/competition_frames.py',
    'gui_v1/competition_explanation.py', 'gui_v1/competition_response.py', 'viewer/index.html',
    'viewer/app.js', 'viewer/scientific_pilot.js', 'viewer/scientific_sparse.js', 'viewer/phase3.js',
    'viewer/workbench.js', 'viewer/unified_flow.js', 'viewer/competition.js', 'start_gui.ps1',
}
protected, edits = [], []
for item in read('before.json'):
    path = Path(item['path'])
    name = path.relative_to(ROOT).as_posix()
    actual = digest(path)
    record = dict(path=name, before=item['sha256'], after=actual, unchanged=actual==item['sha256'])
    if name in expected_edits:
        edits.append(record)
    else:
        protected.append(record)
assert all(p['unchanged'] for p in protected), 'Unexpected protected source changes'
bench = [read(n+'.json') for n in ('baseline', 'cold_cache_final', 'warm_cache_final')]
assert all(b['scientific_identity']==bench[0]['scientific_identity'] for b in bench)
assert all(b['conditions']==55 for b in bench)
assert read('browser_console.json') == []
assert read('HTTP_AND_DESKTOP.json')['status'].startswith('PASS')
assert read('desktop_lifecycle.json')['status']=='PASS'
assert 'Ran 13 tests' in (HERE/'cache_tests_final.log').read_text(encoding='utf-8')
assert 'Ran 22 tests' in (HERE/'offline_regression.log').read_text(encoding='utf-8')
write('VERIFICATION.json', dict(
    status='PASS_BOUNDED_OFFLINE_STARTUP_OPTIMIZATION', source_identity_unchanged=True,
    protected_sources=protected, expected_changed_sources=edits,
    tests=dict(new_python=13, existing_python=22, lazy_panel_JS=6,
               existing_explanation_JS=18, actual_HTTP=9, desktop_lifecycle=6,
               browser='actual original UI navigation, same-run k217, screenshot; no warning/error captured'),
    performance=read('PERFORMANCE.json'), browser=read('browser_regression.json'),
    limits=['No full desktop cold-window timing', 'No fresh inference or real-time/PL performance claim',
            'Daily metadata cache is not independent acceptance evidence'],
    neural_GPU_runs=0, camera_captures=0, board_operations=0, new_video_exports=0))
sources = [ROOT / p for p in sorted(expected_edits)] + [
    ROOT/'gui_v1/startup_cache.py', ROOT/'viewer/startup.js',
    ROOT/'gui_v1/test_startup_fast.py', ROOT/'gui_v1/test_startup_panels.js',
    ROOT.parent/'fpga/docs/workstreams/flyvis-display.md']
assert all(p.is_file() for p in sources)
artifacts = [p for p in HERE.rglob('*') if p.is_file() and
             p.name != 'DELIVERY_MANIFEST.json' and '__pycache__' not in p.parts and
             'test_temp' not in p.parts]
write('DELIVERY_MANIFEST.json', dict(schema='gui-startup-delivery/v1',
    scope='Changed GUI sources and bounded offline verification artifacts; not neural acceptance',
    files=[dict(path=str(p), sha256=digest(p), bytes=p.stat().st_size)
           for p in sorted(set(sources + artifacts))]))
print(json.dumps(dict(status='PASS', protected=len(protected), expected_edits=len(edits),
                      sealed_files=len(set(sources + artifacts)))))
