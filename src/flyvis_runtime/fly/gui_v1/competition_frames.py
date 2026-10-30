"""Explicitly admitted ⑩ frame pack; no discovery, inference, or renderer launch."""
import copy
import hashlib
import json
from pathlib import Path
import struct
import threading

import numpy as np
from competition_replay import RUN, ACTIVITY_SHA
from scientific_pilot import require
from startup_cache import cached_sha256
from competition_response import C_ENCODING_SHA,verify_source_contract,validate_c_encoding,validate_c_states

ENCODING_SHA = 'badf1e434eecc9b9c769c536737e3b3aa39ccbf6bd48c7c30c92f9ebfaa986ed'
BACKGROUND_SHA = '99b3c513720b1c087c1c80afc10fa21b0411469dd5a34edd1c091ba89e9c535f'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def validate_encoding(value, means, variant='A'):
    expected=C_ENCODING_SHA if variant=='C' else ENCODING_SHA
    require(value['encoding_sha256'] == expected, 'Unadmitted colour encoding')
    fields = {k: v for k, v in value.items() if k != 'encoding_sha256'}
    require(digest(json.dumps(fields, sort_keys=True, separators=(',', ':')).encode()) == expected,
            'Colour encoding content mismatch')
    if variant=='C':return validate_c_encoding(value,means)
    require(value['mode'] == 'fixed_type_hue_abs_activity_brightness_v1', 'Fixed type hue required')
    require(value['intensity_domain'] == [0., float(np.max(np.abs(means)))] and
            value['brightness_floor'] == .38, 'Fixed whole-run brightness scale required')


class CompetitionFrames:
    def init__(self, replay, config=None):
        self.replay = replay
        self.config_path = Path(config or Path(__file__).with_name('competition_movie_C.json'))
        self.lock = threading.RLock()
        self.manifest = None

    def get(self,variant=None):
        with self.lock:
            if self.manifest is not None:
                self.unchanged()
                return self
            config_bytes = self.config_path.read_bytes()
            config = json.loads(config_bytes)
            self.variant=config.get('variant','A')
            require(variant is None or variant==self.variant,'Frame variant mismatch')
            path = Path(config['manifest']).resolve()
            raw = path.read_bytes()
            require(digest(raw) == config['manifest_sha256'], 'Frame pack not explicitly admitted')
            manifest = json.loads(raw)
            require(manifest['schema'] == 'line10.fixed_camera_framepack.v1', 'Frame pack schema mismatch')
            require(manifest['run_id'] == RUN and manifest['activity_sha256'] == ACTIVITY_SHA,
                    'Frame pack uses another scientific run')
            require(manifest['frame_count'] == 485 and manifest['profile'] == 'light' and
                    manifest['type_filter'] == 'all', 'Complete eight-type pack required')
            require((manifest['image_width'], manifest['image_height']) == (1280, 640), 'Frame dimensions mismatch')
            require(manifest['background_manifest_sha256'] == BACKGROUND_SHA, 'Background source mismatch')
            replay = self.replay.get()
            replay.unchanged()
            validate_encoding(manifest['color_encoding'], replay.means,self.variant)
            self.source_contract=verify_source_contract(config,replay) if self.variant=='C' else None
            require(len(manifest['frames']) == 485, 'Missing saved states')
            checked = {}
            receipts = []
            for k, row in enumerate(manifest['frames']):
                require(row['frame_index'] == k and row['activity_time_s'] == float(replay.pilot.activity_time[k]),
                        'Frame sequence/time mismatch')
                files = {}
                for key in ('png', 'receipt'):
                    item = (path.parent / row[key]).resolve()
                    require(item.is_relative_to(path.parent) and item.is_file(), 'Frame path escapes pack')
                    require(cached_sha256(item) == row[key + '_sha256'], 'Frame hash mismatch: ' + row[key])
                    if key == 'png':
                        with item.open('rb') as stream:
                            data = stream.read(24)
                    else:
                        data = item.read_bytes()
                    checked[item] = (item.stat().st_size, item.stat().st_mtime_ns)
                    files[key] = data
                require(files['png'][:8] == b'\x89PNG\r\n\x1a\n' and
                        struct.unpack('>II', files['png'][16:24]) == (1280, 640), 'Invalid PNG dimensions')
                receipt = json.loads(files['receipt'])
                require(receipt['run_id'] == RUN and receipt['activity_sha256'] == ACTIVITY_SHA and
                        receipt['frame_index'] == k and receipt['activity_time_s'] == row['activity_time_s'],
                        'Receipt identity mismatch')
                require(receipt['png_sha256'] == row['png_sha256'] and receipt['PL_execution'] is False and
                        receipt['evidence_level'] == 'OFFLINE_SOFTWARE_REPLAY', 'Receipt evidence mismatch')
                require(receipt['visible_types'] == replay.spatial.data['types'] and receipt['type_filter'] == 'all',
                        'Eight visible types required')
                require([x['type'] for x in receipt['type_states']] == replay.spatial.data['types'] and
                        [x['value'] for x in receipt['type_states']] == replay.means[k].tolist(),
                        'Receipt differs from original 721-node means')
                require(receipt['color_encoding'] == manifest['color_encoding'], 'Changing frame colour scale')
                if self.variant=='C':validate_c_states(receipt['type_states'],manifest['color_encoding'],replay.means[k])
                require(receipt['background_manifest_sha256'] == BACKGROUND_SHA and receipt['rois_visible'] is True and
                        receipt['background_style'] == 'simplified_mesh', 'Background missing or mismatched')
                receipts.append(receipt)
            self.config_bytes = config_bytes
            self.path = path
            self.manifest_sha = config['manifest_sha256']
            self.raw = raw
            self.checked = checked
            self.receipts = receipts
            self.manifest = manifest
            return self

    def unchanged(self):
        require(self.config_path.read_bytes() == self.config_bytes and self.path.read_bytes() == self.raw,
                'Admitted frame pack changed; restart and revalidate')
        self.replay.get().unchanged()

    def metadata(self):
        self.get()
        return dict(status='VERIFIED', run_id=RUN, activity_sha256=ACTIVITY_SHA, frame_count=485,
                    manifest_path=str(self.path), manifest_sha256=self.manifest_sha,
                    color_encoding=self.manifest['color_encoding'], image_width=1280, image_height=640,
                    display_kind='OFFLINE_REPLAY', PL_execution=False, FPGA_status='NOT_CONNECTED',
                    brightness_variant=self.variant,playback_steps_per_second=12.125 if self.variant=='C' else 12,
                    video_frames=1200 if self.variant=='C' else 1213,video_duration_s=40 if self.variant=='C' else 1213/30,
                    model_dt_s=.005, render_process_required=False)

    def image(self, k, identity):
        self.get()
        require(identity == self.manifest_sha and type(k) is int and 0 <= k < 485, 'Frame URL identity mismatch')
        row = self.manifest['frames'][k]
        path = (self.path.parent / row['png']).resolve()
        data = path.read_bytes()
        require(digest(data) == row['png_sha256'], 'Saved PNG changed')
        return data

    def render(self, body):
        self.get()
        k = body.get('frame_index')
        require(type(k) is int and 0 <= k < 485, 'Frame outside admitted run')
        require(body.get('run_id') == RUN and body.get('activity_sha256') == ACTIVITY_SHA and
                body.get('activity_time_s') == float(self.replay.get().pilot.activity_time[k]), 'Render run/time mismatch')
        require(body.get('type_filter') == 'all' and body.get('presentation_profile') == 'light', 'Fixed all-type light view required')
        require('camera' not in body and 'pick' not in body, 'Interactive view requires actual renderer')
        require(body.get('selected_type') in self.replay.get().spatial.data['types'], 'Unknown type')
        require(isinstance(body.get('request_id'), str) and 0 < len(body['request_id']) <= 64, 'Request identity required')
        r = copy.deepcopy(self.receipts[k])
        r.update(source_request_id=r.get('request_id'), request_id=body['request_id'], selected_type=body['selected_type'],
                 requested_profile='light', frame_source='VERIFIED_PRERENDERED_FRAME', frame_pack_sha256=self.manifest_sha,
                 color_scale=r['scale'], presentation_policy=dict(profile='light', renderer='cached_cpu_frame',
                     max_fps=24, step_stride=1, degraded=False, render_process_required=False,
                     reason='VERIFIED_FIXED_CAMERA_PACK'))
        return dict(status='VERIFIED', receipt=r,
                    image_url=f'/api/competition/frames/{k}.png?identity={self.manifest_sha}')


