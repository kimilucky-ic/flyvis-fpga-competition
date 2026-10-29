"""No neural steps: resource checks, source freeze and metric unit checks."""
from core import *
import ast

assert not (HERE/'PREREGISTRATION.json').exists()
assert shutil.disk_usage(HERE).free >= 10*1024**3
resources = memory(); assert resources['available_bytes'] >= 2*1024**3
ref.freezecheck(deep=True); base.check_frozen()
assert sha(MODEL) == MODEL_SHA
m = ref.mapping(); roi = np.load(ROI_PATH)
assert len(roi) == 331 and len(m['H']) == 5768 and len(m['R']) == 39901
raw = np.load(RAW, mmap_mode='r'); assert raw.shape == (24, 485, 1, 721)
with SAMPLES.open(encoding='utf-8-sig') as stream: samples = list(csv.DictReader(stream))
cases = candidate_cases()
for case in cases:
    if case['group'] == 'short':
        row = samples[case['sample']]
        assert int(row['sample']) == case['sample'] and int(row['angle']) == case['angle']
        assert int(row['intensity']) == int(case['polarity'] == 'ON')

# Exact agreement with original metric arithmetic for the inherited shape.
spec = importlib.util.spec_from_file_location('original_metrics', METRIC_PATH)
original = importlib.util.module_from_spec(spec); spec.loader.exec_module(original)
rng = np.random.default_rng(2026101617)
fake = rng.normal(0, .001, (485, 2, 721)).astype(np.float32); fake[200:] += .2
other = fake*.97 + rng.normal(0, .001, fake.shape).astype(np.float32)
checks = []
for window in [slice(200, 286), slice(200, 485)]:
    a = original.vector_metrics(fake, other, roi, window=window)
    b = vector_metrics(fake, other, roi, window)
    keys = ['Q', 'magnitude_ratio', 'field_error_E', 'angle_deg', 'reference_response_rms', 'reference_pre_window_rms']
    assert all(a[key] == b[key] for key in keys)
    checks.append(dict(window=[window.start, window.stop], inherited_metrics_bitwise_equal=True))
weak = vector_metrics(np.zeros_like(fake), np.zeros_like(fake), roi, slice(200, 485))
assert not weak['reference_eligible'] and not weak['pass_gate']
for case in cases:
    value = inputs(case, raw, m['grid_uv'])
    assert value.shape == (case['steps'], 721) and value.dtype == np.float32 and np.isfinite(value).all()
    assert value.min() >= 0 and value.max() <= 1
    if case['group'] == 'long':
        assert np.array_equal(value[650], value[750]) and np.array_equal(value[1300], value[1350])
        assert not np.array_equal(value[240], value[300])
    if case['group'] == 'short' and case['variant'] != 'base':
        assert not np.array_equal(value, raw[case['sample'], :, 0])
dump(HERE/'PRECHECK.json', dict(status='PASS_CPU_RESOURCES_AND_ARRAY_TESTS', **resources,
    free_disk_bytes=shutil.disk_usage(HERE).free, source_and_model_SHA_verified=True,
    metric_checks=checks, weak_reference_not_PASS=True, input_range_and_hold_tests=13, neural_steps=0, GPU=0, board=0))
paths = [HERE/name for name in ['core.py', 'prepare.py', 'run.py', 'analyze.py', 'audit.py', 'plots.py']]
paths += [MODEL, REFINE/'MODEL_FREEZE.json', REFINE/'PREREGISTRATION.json', REFINE/'FINAL_AUDIT.json',
          base.HERE/'cnn.py', base.HERE/'common.py', base.HERE/'experiment.py', base.HERE/'decoder_cpu.py',
          base.HERE/'mapping.npz', base.HERE/'R_CANDIDATE.json', ROI_PATH, METRIC_PATH, RAW, SAMPLES,
          BUNDLE/'expanded_parameters.npz', BUNDLE/'initial_state_full.npy', BUNDLE/'identity_manifest.json',
          base.FLY/'gpu_phase2/r_only.py']
for path in HERE.glob('*.py'): ast.parse(path.read_text(encoding='utf-8-sig'))
pins = {str(p):dict(bytes=p.stat().st_size, mtime_ns=p.stat().st_mtime_ns, sha256=sha(p)) for p in paths}
dump(HERE/'PREREGISTRATION.json', dict(schema='frozen-CNN-long-and-new-inputs/v1', cases=cases, pins=pins,
    model_SHA=MODEL_SHA, parameters=31168, training_updates=0, GPU=0, board=0, dt=DT,
    scope='CPU only; inherited official Full/R/decoder/331ROI. All cases fresh for frozen model, no model selection.',
    primary='Every non-gray named window must pass Hresponse relativeL2<=.20 and eligible flow E<=.20,M[.8,1.2],angle<=15. Hreference response RMS>=1e-6; weak reference NOT_EVALUABLE, never PASS.',
    baseline='Full rows160:200 for both paths, old a[k]→new a[k+1], no reset after common a0.',
    long='Two NEW sinusoidal grating families, no saved future states: 0-1s gray; 1-3 forward; 3-4 hold; 4-6 reverse;6-7hold;7-9halfspeed;9-10hold; onset contrast ramp .1s, continuous phase.',
    short='Official new120/300deg ON/OFF; ON1201.5x, OFF120.5x causal floor time; ON/OFF120 stationary aperture radius5 at y+5/-5. No natural video or moving finite object claim.',
    gray='New numeric maintenance gate for both[200:2000] and[1000:2000]: H absoluteRMSE<=.002 (inherited short-gray), R absoluteRMSE<=.002 and raw ROI flow componentRMSE<=.002 (new prereg bounds in model units). No direction-classifier false-positive claim.',
    stability='All states finite and absolute<=100; validate both candidates then commit. Failure stops that run with valid-prefix metadata, no fallback/retry. Remaining cases still run once.',
    evidence='Full newly computed, CNN live39901R/own5768H from same old state; original H guard in CNN path; firstshortSham only; no large re-audit or repeated fault test suite.',
    budget=dict(CPU_threads=1, total_neural_wall_limit_s=600, total_new_disk_limit_GiB=6,
                preflight_free_disk_GiB_min=10, preflight_free_RAM_GiB_min=2, retries=0),
    stop='One bounded batch; no model/threshold changes after results; no training/GPU/board/GUI/new scheduler. All now-seen cases cannot be future independent holdout.'))
dump(HERE/'FREEZE.json', dict(sha256=sha(HERE/'PREREGISTRATION.json'), time_ns=time.time_ns()))
(HERE/'inputs').mkdir()
records = []
for case in cases:
    p = HERE/'inputs'/(case['id']+'.npy'); np.save(p, inputs(case, raw, m['grid_uv']))
    records.append(dict(**case, path=str(p), sha256=sha(p)))
dump(HERE/'INPUTS.json', records)
print(json.dumps(dict(stage='PREPARED', cases=len(cases), max_formal_commits=sum(c['steps']*2 for c in cases)+485,
                     prereg_sha=sha(HERE/'PREREGISTRATION.json'), model_sha=sha(MODEL), GPU=0)), flush=True)
