"""Read saved runs only. Does not import a model, open a camera, or start a server."""
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

OUT = Path(__file__).resolve().parent
FLY = OUT.parents[2]
GUI = FLY / 'gui_v1'
NEW = GUI / 'runtime/live/f1fe7afff451461fbbc77603a540cc0d'
OLD = GUI / 'runtime/live/457060aac35041eabe99ee8f39a7a95f'


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def rows(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line]


def percentiles(values):
    return dict(zip(('p50', 'p95', 'p99', 'max'), map(float, np.percentile(values, [50, 95, 99, 100]))))


def metrics(root):
    summary = load(root / 'stream/manual_summary.json')
    result = load(root / 'stream/result.json')
    display = load(root / 'stream/display_summary.json')
    receipts = rows(root / 'stream/display_receipts.jsonl')
    frames = rows(root / 'skeleton/frames.jsonl')
    sources = [load(path) for path in sorted((root / 'stream/sources').glob('*.json'))]
    snapshots = [load(path) for path in sorted((root / 'stream/snapshots').glob('*.json'))]
    capture = load(root / 'stream/camera_capture.json')
    lag = percentiles([p['schedule_lag_wall_s'] * 1000 for p in snapshots])
    return dict(
        session_id=summary['session_id'], run_id=summary['run_id'],
        status=summary['status'], computed_steps=summary['computed_steps'],
        durable_steps=summary['durable_steps'], journal_rows=summary['journal_rows'],
        physical_seconds=summary['compute_wall_s'], model_seconds=summary['model_time_s'],
        model_steps_per_second=summary['steps_per_s'], display_FPS=summary['display_FPS'],
        drawn_frames=summary['draw_count'],
        receipt_to_draw_upper_ms=percentiles([p['upper_ms'] for p in receipts]),
        official_input_conversion_ms=percentiles([p['converter_elapsed_s'] * 1000 for p in sources]),
        backend_pixel_audit_ms=percentiles([p['total_render_raw_ms'] for p in frames]),
        browser_cpu_compose_ms=percentiles([p['browser_cpu_compose_ms'] for p in receipts]),
        browser_final_draw_ms=percentiles([p['skeleton_draw_ms'] for p in receipts]),
        raf_wait_ms=percentiles([p['raf_wait_ms'] for p in receipts]),
        latest_slot_age_ms=percentiles([p['packet_slot_age_ms'] for p in receipts]),
        snapshot_schedule_lag_wall_ms=lag,
        latency_above_500ms_frames=sum(p['upper_ms'] > 500 for p in receipts),
        camera_delivery_FPS=capture['capture']['measured_delivery_fps'],
        captured_source_frames=capture['accepted_source_frames'],
        display_transport=display['transport_stages'],
        GPU_and_host_timing=result['stages'], asset_writer=result['asset_writer'],
        commit_journal=result['commit_journal'], browser_environment=summary['browser_environment'],
        clock=summary['clock'], source_queue_final=result['source_queue_length'],
        raw_queue_peak=result['raw_queue_peak'],
        hex_history_peak=result['hex_queue_peak'],
        hex_history_semantics='bounded 96-frame causal history, not a 96-frame unprocessed queue',
        result_sha256=sha(root / 'stream/result.json'),
        journal_sha256=sha(root / 'stream/step_commits.jsonl'),
        manifest_sha256=sha(root / 'stream/manifest.json'),
        FPGA_status='NOT_CONNECTED', PL_execution=False,
        latency_semantics='Windows frame receipt to browser rAF callback, upper bound with paired clock uncertainty; sensor exposure and physical scanout are not measured',
    )


before, after = metrics(OLD), metrics(NEW)
verification = load(OUT / 'verification.json')
assert verification['summary']['run_id'] == after['run_id']
assert verification['summary']['result_sha256'] == after['result_sha256']
assert after['computed_steps'] == after['durable_steps'] == after['journal_rows'] == 6000
comparison = dict(
    schema='flyvis-bounded-headroom-review/v1',
    collected_utc=datetime.now(timezone.utc).isoformat(),
    actual_new_GPU_camera_experiments=1, observation_seconds=60,
    before=before, after=after,
    comparison_limit='Historical WebView2 DPR1.5 vs current visible IAB DPR1, same 1386x883 viewport and 100-step/s pace; different real camera scene. NOT controlled A/B.',
    whole_run_tail_latency_improved=False,
    accepted='BOUNDED_SLOW_CAMERA_TEST / complete evidence; local CPU and normal latency savings',
    not_accepted='overall tail latency improvement, >=15 FPS, p95<200ms, strict realtime or FPGA headroom guarantee',
    transient=dict(
        observation='Around physical seconds 6.5-10.5, committed snapshots already have wall schedule lag up to 594.6ms; it recovers. 32 displayed frames exceed 500ms receipt-to-draw.',
        attribution='Model advancement / host-side scheduling is implicated. Cached one-second cumulative timers cannot isolate the cause of each stall. Pure GPU kernel, power mode or browser cause is NOT established.',
        protection='Original 750ms wall-lag threshold retained; no overload stop in this test.',
    ),
    numerical_checks=dict(official_input=load(OUT / 'input_equality.json')['status'],
                          pixel_reference=load(OUT / 'pixel_audit_cpu.json')['status'],
                          actual_link=verification['status'],
                          saved_files_rehashed=verification['checked_saved_files'],
                          actual_browser_frames=verification['checked_browser_frames'],
                          rendered_type_means=verification['checked_rendered_means']),
)
write(OUT / 'performance.json', comparison)

fields = [
    ('model_steps_per_second', before['model_steps_per_second'], after['model_steps_per_second'], 'steps/s'),
    ('display_FPS', before['display_FPS'], after['display_FPS'], 'FPS'),
    ('receipt_to_draw_p50_upper', before['receipt_to_draw_upper_ms']['p50'], after['receipt_to_draw_upper_ms']['p50'], 'ms'),
    ('receipt_to_draw_p95_upper', before['receipt_to_draw_upper_ms']['p95'], after['receipt_to_draw_upper_ms']['p95'], 'ms'),
    ('official_input_conversion_p50', before['official_input_conversion_ms']['p50'], after['official_input_conversion_ms']['p50'], 'ms'),
    ('backend_pixel_audit_p50', before['backend_pixel_audit_ms']['p50'], after['backend_pixel_audit_ms']['p50'], 'ms'),
    ('browser_cpu_compose_p50', before['browser_cpu_compose_ms']['p50'], after['browser_cpu_compose_ms']['p50'], 'ms'),
    ('latest_slot_age_p50', before['latest_slot_age_ms']['p50'], after['latest_slot_age_ms']['p50'], 'ms'),
    ('camera_delivery_FPS', before['camera_delivery_FPS'], after['camera_delivery_FPS'], 'FPS'),
    ('asset_queue_peak', before['asset_writer']['queue_peak'], after['asset_writer']['queue_peak'], 'items'),
]
with (OUT / 'before_after.csv').open('w', encoding='utf-8-sig', newline='') as stream:
    writer = csv.writer(stream)
    writer.writerow(['metric', 'before', 'after', 'unit', 'change_percent', 'comparison_limit'])
    for name, old, new, unit in fields:
        writer.writerow([name, old, new, unit, (new / old - 1) * 100,
                         'historical different host/DPR/scene; not controlled A/B'])

changed = list(load(OUT / 'before_sources.json')) + [
    'gui_v1/stream_cadence.py', 'gui_v1/prepared_camera_input.py',
    'gui_v1/test_stream_headroom.py', 'gui_v1/verify_prepared_camera.py',
]
write(OUT / 'delivery_sources.json', {name: sha(FLY / name) for name in changed})
old_manifest = load(GUI / 'evidence/cached_canvas_20261015/delivery_sources.json')
protected = ['viewer/index.html', 'viewer/fixed_skeleton.js', 'gui_v1/competition_live.py']
protected += [name for name in old_manifest if name.startswith('flyvis-3d-studio/')]
identity = {name: dict(current=sha(FLY / name), expected=old_manifest[name],
                       matches=sha(FLY / name) == old_manifest[name]) for name in protected}
assert all(row['matches'] for row in identity.values())
write(OUT / 'preserved_sources.json', identity)
print(json.dumps(dict(before_FPS=before['display_FPS'], after_FPS=after['display_FPS'],
    before_latency_ms=before['receipt_to_draw_upper_ms'], after_latency_ms=after['receipt_to_draw_upper_ms'],
    before_input_ms=before['official_input_conversion_ms']['p50'], after_input_ms=after['official_input_conversion_ms']['p50'],
    before_pixel_audit_ms=before['backend_pixel_audit_ms']['p50'], after_pixel_audit_ms=after['backend_pixel_audit_ms']['p50'],
    preserved_sources=len(identity)), indent=2))
