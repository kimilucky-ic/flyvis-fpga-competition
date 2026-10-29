"""Explicit import of candidate11's saved ONE-step result; no device operations.

Reported board provenance is retained, not inferred from filenames. Every full
initial/state word is independently compared before a display packet is exposed.
The imported result is OFFLINE_REPLAY, never a connected board or a new GPU run.
"""
import hashlib
import io
import json
import math
from pathlib import Path
import re
import threading
from types import SimpleNamespace
import zipfile

import numpy as np
from live_protocol import HERE, host_path, load, require, sha

READINESS = HERE/'evidence/line11_board_readiness_20261018/READINESS.json'
READINESS_SHA = 'fff1e95d1cc9c494b1b52168d03e57f3019a16218021aa8eda80ab892789b564'
BUNDLE_SHA = '672daf29cf4faf2780587c2aeaea4d0f9dc697ca7d3be96b6e3fb1308194c5b2'
DRIVER_SHA = '291345d747d49703478596308274899959e05a226a5dd4690ca0c9dead907096'
STEPPER_SHA = '53da39c0219cd00fb6f54ce687f466f16d57f1ba8625d4267fdb1dc368c636c2'
PASS = 'PASS_BOARD_ONE_STEP_ALL_STATES'
REQUIRED = {'result.json', 'board_before.json', 'bundle_check.json', 'actual_input.bin',
            'actual_initial.bin', 'actual_state1.bin', 'initial_compare.json',
            'state1_compare.json', 'events.jsonl', 'RUN_CONTEXT.json',
            'EVIDENCE_MANIFEST.json', 'SAVED_DISPLAY_FRAME.json'}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def archive_files(blob):
    """No extraction or filename-based discovery; bounded untrusted ZIP input."""
    require(len(blob) <= 8_000_000, 'FULL_PL_ARCHIVE_TOO_LARGE')
    with zipfile.ZipFile(io.BytesIO(blob)) as archive:
        rows = archive.infolist()
        names = [r.filename for r in rows]
        require(len(rows) <= 24 and len(set(names)) == len(names), 'FULL_PL_ZIP_ENTRIES')
        require(REQUIRED <= set(names), 'FULL_PL_MISSING_FILES')
        require(all(re.fullmatch(r'[A-Za-z0-9_.-]+', n) for n in names), 'FULL_PL_UNSAFE_NAME')
        require(sum(r.file_size for r in rows) <= 8_000_000, 'FULL_PL_UNPACKED_BOUND')
        require(all(not (r.flag_bits & 1) and r.file_size <= 2_000_000 for r in rows), 'FULL_PL_FILE_BOUND')
        return {r.filename: archive.read(r) for r in rows}


def validate_files(files, contract):
    """Pure CPU protocol validation; tests use frozen reference bytes, not PL."""
    read = lambda name: json.loads(files[name])
    p, c, r = (read(n) for n in ('SAVED_DISPLAY_FRAME.json', 'RUN_CONTEXT.json', 'result.json'))
    before, manifest = read('board_before.json'), read('EVIDENCE_MANIFEST.json')
    require(r['status'] == PASS and r['board_result'] is True and r['evidence_level'] == 'PHYSICAL_BOARD', 'FULL_PL_NOT_BOARD_PASS')
    require(r['candidate'] == 'hole_pipeline_20261016/soc_r2' and r['automatic_retry'] is False and r['DMA'] is False, 'FULL_PL_BACKEND_SCOPE')
    require(c['status'] == PASS and c['backend'] == 'FULL_NETWORK_FPGA' and c['hardware_operator'] == 'HUMAN_USER', 'FULL_PL_CONTEXT')
    require(p['schema'] == 'flyvis-line11-saved-display-frame/v1' and p['evidence'] == 'PHYSICAL_BOARD_ONE_STEP_ALL_STATES', 'FULL_PL_PACKET')
    run, boot = c['run_id'], c['boot_id']
    require(re.fullmatch(r'LINE11_MANUAL_[0-9a-f]{32}', run) and re.fullmatch(r'[0-9a-f-]{36}', boot), 'FULL_PL_ID_FORMAT')
    require(p['run_id'] == manifest['run_id'] == run and p['boot_id'] == before['boot_id'] == boot and manifest['status'] == PASS, 'FULL_PL_RUN_BOOT')
    require(set(manifest['files']) == set(files)-{'EVIDENCE_MANIFEST.json'}, 'FULL_PL_MANIFEST_FILES')
    for name, info in manifest['files'].items():
        require(info['bytes'] == len(files[name]) and info['sha256'] == digest(files[name]), 'FULL_PL_FILE_SHA '+name)
    for key in ('bit_sha256', 'hwh_sha256'):
        expected = contract[key[:3]]['sha256']
        require(c[key] == r[key] == expected, 'FULL_PL_IMAGE '+key)
    bundle = read('bundle_check.json')
    require(bundle['status'] == 'PASS_OFFLINE_BUNDLE_ONLY' and bundle['bit_sha256'] == r['bit_sha256']
            and bundle['hwh_sha256'] == r['hwh_sha256'], 'FULL_PL_PREPARATION_IDENTITY')
    require(c['source_bundle_sha256'] == BUNDLE_SHA and c['driver_sha256'] == DRIVER_SHA
            and c['frame_stepper_sha256'] == STEPPER_SHA, 'FULL_PL_SOURCE_IDENTITY')
    provenance = c['provenance']
    for key, source in [('source_commit', 'commit'), ('checkpoint_sha256', 'checkpoint_sha256'), ('graph_sha256', 'graph_sha256')]:
        require(provenance[source] == contract['model'][key], 'FULL_PL_MODEL '+key)
    require(provenance['neurons'] == 45669 and provenance['synapses'] == 1513231
            and provenance['dt_seconds'] == c['model_dt_s'] == .005, 'FULL_PL_NUMERIC_SCOPE')
    require(c['node_order'] == 'global_node_id_0_through_45668'
            and c['byte_order'] == 'little_endian_uint32_FP32_bits', 'FULL_PL_NODE_ORDER')
    require(p['input_bits_path'] == 'actual_input.bin' and p['state_bits_path'] == 'actual_state1.bin'
            and p['validation_path'] == 'state1_compare.json' and p['context_path'] == 'RUN_CONTEXT.json', 'FULL_PL_PATH_BINDING')
    require(c['frame_id'] == p['frame_id'] == 0 and p['completed_steps'] == r['completed_steps'] == 1, 'FULL_PL_ONE_STEP_ONLY')
    counter = r['hardware_counters']
    require(counter['completed_steps'] == 1 and counter['nodes'] == r['state_words_checked'] == 45669
            and counter['edges'] == r['full_network_edges'] == 1513231 and r['mismatch_words'] == 0, 'FULL_PL_COUNTERS')
    require(p['faults'] == counter['faults'] == 0 and p['compute_cycles'] == counter['last_cycles'] == 2201418, 'FULL_PL_FAULT_OR_CYCLES')
    require(p['clock_hz'] == r['observed_FCLK0_MHz']*1e6 == 100_000_000, 'FULL_PL_CLOCK')
    for name, reference, size, expected in [
        ('actual_input.bin', host_path(contract['first_step_reference']['input_path']), 2884, contract['first_step_reference']['input_sha256']),
        ('actual_state1.bin', host_path(contract['first_step_reference']['expected_path']), 182676, contract['first_step_reference']['expected_sha256']),
        ('actual_initial.bin', host_path(contract['selected_local_candidate']).parent/'preboard_20261018/bundle_r1/initial_state.bin', 182676, contract['initial']['bits_sha256'])]:
        # Compare ALL bytes, including nodes outside the displayed T4/T5 slice.
        raw, ref = files[name], reference.read_bytes()
        require(len(raw) == len(ref) == size and digest(ref) == expected, 'FULL_PL_REFERENCE '+name)
        require(raw == ref, 'FULL_PL_ALL_WORD_MISMATCH '+name)
        require(np.isfinite(np.frombuffer(raw, dtype='<f4')).all(), 'FULL_PL_NONFINITE')
    require(p['input_bytes'] == 2884 and p['state_bytes'] == 182676
            and p['input_sha256'] == c['input_sha256'] == digest(files['actual_input.bin'])
            and p['state_sha256'] == digest(files['actual_state1.bin'])
            and c['initial_sha256'] == digest(files['actual_initial.bin']), 'FULL_PL_VECTOR_IDENTITY')
    for name, raw, expected in [('initial_compare.json', 'actual_initial.bin', c['initial_sha256']),
                                ('state1_compare.json', 'actual_state1.bin', p['state_sha256'])]:
        comparison = read(name)
        require(comparison['words'] == 45669 and comparison['mismatch_words'] == 0
                and comparison['actual_sha256'] == comparison['expected_sha256'] == expected, 'FULL_PL_COMPARISON '+name)
    timing = r['timing']
    for packet_key, result_key in [('input_upload_ms', 'input_seconds'), ('compute_wait_ms', 'step_call_seconds'), ('full_state_readback_ms', 'readback_seconds')]:
        value = p[packet_key]
        require(type(value) in (int, float) and math.isfinite(value) and value >= 0
                and math.isclose(value, timing[result_key]*1000, rel_tol=1e-12, abs_tol=1e-9), 'FULL_PL_TIMING')
    require(math.isfinite(p['elapsed_seconds']) and math.isclose(p['elapsed_seconds'], sum(timing[k] for k in ('input_seconds', 'step_call_seconds', 'readback_seconds')), rel_tol=1e-12, abs_tol=1e-9), 'FULL_PL_ELAPSED')
    require(c.get('cpu_serial_raw') or c.get('board_id_label'), 'FULL_PL_BOARD_ID_MISSING')
    return dict(packet=p, context=c, result=r)


class FullPLResult:
    """One optional saved package. A bad import never stops the old GUI."""
    def init__(self, path=None):
        self.path = Path(path).resolve() if path else None
        self.lock = threading.RLock()
        self.attempted = False
        self.error = None
        self.value = None
        self.geometry = None

    def _load(self):
        with self.lock:
            if not self.attempted:
                self.attempted = True
                try:
                    require(sha(READINESS) == READINESS_SHA, 'FULL_PL_READINESS_CHANGED')
                    contract = load(READINESS)
                    require(self.path and self.path.is_file() and self.path.stat().st_size <= 8_000_000, 'FULL_PL_RESULT_NOT_CONFIGURED')
                    blob = self.path.read_bytes()
                    files = archive_files(blob)
                    value = validate_files(files, contract)
                    from spatial_state import SpatialRegistry
                    self.spatial = SpatialRegistry()
                    require(self.spatial.digest == contract['consumer']['spatial_mapping_sha256'], 'FULL_PL_SPATIAL_IDENTITY')
                    self.full = np.frombuffer(files['actual_state1.bin'], dtype='<f4')
                    self.input = np.frombuffer(files['actual_input.bin'], dtype='<f4')
                    self.value = value
                    self.archive_sha = digest(blob)
                    self.contract = contract
                except (OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile, RuntimeError) as error:
                    self.value = None
                    self.error = str(error)
            require(self.value is not None, self.error or 'FULL_PL_NOT_AVAILABLE')
            return self.value

    def status(self):
        if self.path is None:
            return dict(status='NOT_CONFIGURED', configured=False, board_connection='NOT_CONNECTED')
        try:
            value = self._load()
            return dict(status='VERIFIED_SAVED_FIRST_STEP', configured=True, run_id=value['context']['run_id'],
                        boot_id=value['context']['boot_id'], backend='FULL_NETWORK_FPGA',
                        display_kind='OFFLINE_REPLAY_FULL_NETWORK_FPGA', board_connection='NOT_CONNECTED',
                        continuous_execution='NOT_AVAILABLE_PENDING_FIRST_STEP_ACCEPTANCE',
                        archive_sha256=self.archive_sha, source_path=str(self.path), flow='NOT_AVAILABLE',
                        full_state_words_checked=45669, mismatch_words=0, timing=value['result']['timing'])
        except ValueError as error:
            return dict(status='NOT_AVAILABLE', configured=True, error=str(error), result_valid=False, board_connection='NOT_CONNECTED')

    def frame(self):
        v = self._load()
        p, c = v['packet'], v['context']
        values = self.spatial.extract(self.full)
        return dict(schema='flyvis-full-pl-first-step-display/v1', run_id=c['run_id'], session_id=c['run_id'],
                    backend='FULL_NETWORK_FPGA', display_kind='OFFLINE_REPLAY_FULL_NETWORK_FPGA',
                    evidence_level='PRODUCER_BOARD_ONE_STEP_PC_ALL_WORDS_VERIFIED', step_id=0, serial=1, state_token=1,
                    input_time_s=0., activity_time_s=.005, source=dict(sequence=0, kind='line11_fixed_frame0'),
                    input_hex=self.input.tolist(), input_sha256=p['input_sha256'], full_state_sha256=p['state_sha256'],
                    spatial=dict(values=values.tolist(), values_sha256=digest(values.tobytes()), map_sha256=self.spatial.digest),
                    signed_means=values.reshape(8,721).mean(axis=1,dtype=np.float64).tolist(),
                    model=self.contract['model'], initial_sha256=c['initial_sha256'], hardware=dict(boot_id=c['boot_id'],
                    bit_sha256=c['bit_sha256'], hwh_sha256=c['hwh_sha256'], compute_cycles=p['compute_cycles'],
                    clock_hz=p['clock_hz'], faults=0, completed_steps=1, board_id=c['board_id_label']),
                    timing=v['result']['timing'], flow=None, flow_status='NOT_AVAILABLE_NOT_DECODED',
                    archive_sha256=self.archive_sha, board_connection='NOT_CONNECTED', continuous_execution='NOT_AVAILABLE')

    def projection(self):
        with self.lock:
            self._load()
            if self.geometry is None:
                from projection_startup import load_static_projection
                registry = load(HERE/'live_registry.json')
                bridge = SimpleNamespace(adapter=SimpleNamespace(registry=SimpleNamespace(data=registry)), spatial=self.spatial)
                self.geometry, self.cached = load_static_projection(bridge)
                self.geometry.update(consumer_kind='FULL_PL_VERIFIED_SAVED_RESULT')
                self.geometry['projection_cache']['url'] = '/api/full-pl/cache'
                pin = registry['pins']['coordinates']
                require(sha(host_path(pin['path'])) == pin['sha256'], 'FULL_PL_INPUT_COORDINATE_SHA')
                uv = np.load(host_path(pin['path']), allow_pickle=False)
                require(uv.shape == (721, 2), 'FULL_PL_INPUT_COORDINATES')
                self.geometry['coordinates_uv'] = uv.tolist()
            return self.geometry

    def cache(self):
        self.projection()
        return self.cached.blob
