"""Bounded export of the actual GUI canvas. CPU H.264; no neural computation."""
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import threading
import time
import uuid

from competition_replay import RUN, ACTIVITY_SHA
from scientific_pilot import require


def video_source_indices(variant='A'):
    require(variant in ('A','C'),'Unadmitted movie variant')
    if variant=='C':return [i*485//1200 for i in range(1200)]
    # ceil(485 / 12 * 30) = 1213 frames; every saved state survives, no interpolation.
    return [min(484, i * 12 // 30) for i in range(1213)]


class CompetitionMovie:
    def init__(self, frames):
        self.frames = frames
        self.lock = threading.RLock()
        self.state = None
        self.process = None
        self.closed = False

    def start(self, body):
        with self.lock:
            require(not self.closed, 'Exporter is closing')
            require(self.state is None or self.state['status'] in ('COMPLETED', 'FAILED', 'CANCELLED'), 'One export at a time')
            pack = self.frames.get(body.get('brightness_variant'))
            self.pack=pack
            require(body.get('run_id') == RUN and body.get('manifest_sha256') == pack.manifest_sha,
                    'Movie run/frame pack mismatch')
            self.id = uuid.uuid4().hex
            self.folder = Path(__file__).parent / 'exports' / (('ON60_C_40s_' if pack.variant=='C' else 'ON60_40s_') + self.id)
            (self.folder / 'frames').mkdir(parents=True, exist_ok=False)
            self.rows = []
            self.started = time.perf_counter()
            self.state = dict(export_id=self.id, status='CAPTURING_GUI', captured=0, total=485,
                              run_id=RUN, manifest_sha256=pack.manifest_sha, display_kind='OFFLINE_REPLAY',
                              PL_execution=False, output_directory=str(self.folder), error=None)
            self.state.update(brightness_variant=pack.variant,video_duration_s=pack.metadata()['video_duration_s'])
            self._save()
            return dict(self.state)

    def _save(self):
        path = self.folder / 'export_status.json'
        temporary = path.with_suffix('.tmp')
        temporary.write_text(json.dumps(self.state, ensure_ascii=False, indent=2), encoding='utf-8')
        temporary.replace(path)

    def capture(self, identity, k, png, headers):
        with self.lock:
            require(self.state and identity == self.id and self.state['status'] == 'CAPTURING_GUI', 'Inactive export')
            require(type(k) is int and 0 <= k < 485 and k <= len(self.rows), 'Every GUI state required in order')
            pack = self.pack.get()
            source = pack.manifest['frames'][k]
            require(headers.get('X-Run-ID') == RUN and headers.get('X-Frame-Pack') == pack.manifest_sha and
                    headers.get('X-Skeleton-SHA256') == source['png_sha256'] and
                    headers.get('X-Color-Encoding') == pack.manifest['color_encoding']['encoding_sha256'] and
                    float(headers.get('X-Activity-Time', 'nan')) == source['activity_time_s'], 'GUI export frame identity mismatch')
            require(png[:8] == b'\x89PNG\r\n\x1a\n' and struct.unpack('>II', png[16:24]) == (1920, 1080),
                    'Actual 1080p GUI PNG required')
            if k < len(self.rows):
                row=self.rows[k]
                require(hashlib.sha256(png).hexdigest()==row['png_sha256'] and
                        hashlib.sha256((self.folder/row['png']).read_bytes()).hexdigest()==row['png_sha256'],
                        'Retry differs from durable GUI frame')
                return dict(self.state, duplicate_frame_ack=k)
            name = f'frames/frame_{k:04d}.png'
            (self.folder / name).write_bytes(png)
            row = dict(frame_index=k, run_id=RUN, activity_sha256=ACTIVITY_SHA,
                       input_time_s=float(pack.replay.get().pilot.time[k]), activity_time_s=source['activity_time_s'],
                       skeleton_sha256=source['png_sha256'], source_receipt_sha256=source['receipt_sha256'],
                       png=name, png_sha256=hashlib.sha256(png).hexdigest())
            self.rows.append(row)
            with (self.folder / 'gui_frames.jsonl').open('a', encoding='utf-8') as stream:
                stream.write(json.dumps(row, ensure_ascii=False) + '\n')
            self.state['captured'] = len(self.rows)
            self._save()
            return dict(self.state)

    def finish(self, body):
        with self.lock:
            require(self.state and body.get('export_id') == self.id and self.state['status'] == 'CAPTURING_GUI', 'Inactive export')
            require(len(self.rows) == 485, 'Incomplete GUI capture cannot produce success video')
            pack = self.pack.get()
            indices=video_source_indices(pack.variant)
            manifest = dict(schema='flyvis.competition.gui-movie.v1', run_id=RUN, activity_sha256=ACTIVITY_SHA,
                            frame_pack_path=str(pack.path), frame_pack_sha256=pack.manifest_sha,
                            model_dt_s=.005, playback_steps_per_second=pack.metadata()['playback_steps_per_second'], video_fps=30, video_frames=len(indices),
                            brightness_variant=pack.variant,duration_s=len(indices)/30, repeat_saved_states=True, interpolation=False,
                            display_kind='OFFLINE_REPLAY', evidence_level='SOFTWARE_PILOT', PL_execution=False,
                            FPGA_status='NOT_CONNECTED', color_encoding=pack.manifest['color_encoding'],
                            gui_frame_count=485, gui_capture_wall_s=time.perf_counter()-self.started,
                            source_for_video_frame=indices, frames=self.rows)
            (self.folder / 'movie_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
            python = Path(__file__).parent.parent / 'flyvis-3d-studio/anatomy_trial_20261013/.venv/Scripts/python.exe'
            require(python.is_file(), 'Existing CPU encoder environment unavailable')
            self.log = (self.folder / 'encoder.log').open('w', encoding='utf-8')
            self.process = subprocess.Popen([str(python), str(Path(__file__).with_name('encode_competition_movie.py')), str(self.folder)],
                                            stdout=self.log, stderr=subprocess.STDOUT,
                                            creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0) | getattr(subprocess, 'BELOW_NORMAL_PRIORITY_CLASS', 0))
            self.state.update(status='ENCODING_CPU', encoder_pid=self.process.pid)
            self._save()
            threading.Thread(target=self._wait, daemon=True, name='Competition CPU video export').start()
            return dict(self.state)

    def _wait(self):
        try:
            code = self.process.wait(timeout=300)
            with self.lock:
                if self.state['status'] == 'CANCELLED': return
                require(code == 0, 'CPU encoder failed; see encoder.log')
                self.state.update(status='COMPLETED', video_path=str(self.folder/'ON60_40s_1080p.mp4'),
                                  total_wall_s=time.perf_counter()-self.started,
                                  video_url=f'/api/competition/movie/{self.id}.mp4')
                self._save()
        except Exception as error:
            with self.lock:
                if self.process.poll() is None: self.process.terminate(); self.process.wait(timeout=10)
                if self.state['status'] != 'CANCELLED':
                    self.state.update(status='FAILED', error=str(error)); self._save()
        finally:
            self.log.close()

    def status(self):
        with self.lock:
            return dict(self.state) if self.state else dict(status='IDLE')

    def video(self, identity):
        with self.lock:
            require(self.state and identity == self.id and self.state['status'] == 'COMPLETED', 'Complete movie unavailable')
            return (self.folder / 'ON60_40s_1080p.mp4').read_bytes()

    def cancel(self, body):
        with self.lock:
            require(self.state and body.get('export_id') == self.id, 'Export identity mismatch')
            if self.state['status'] not in ('COMPLETED', 'FAILED', 'CANCELLED'):
                self.state.update(status='CANCELLED', error='Export cancelled; partial evidence retained')
                if self.process and self.process.poll() is None: self.process.terminate()
                self._save()
            return dict(self.state)

    def close(self):
        self.closed = True
        if self.state: self.cancel({'export_id': self.id})
        if self.process and self.process.poll() is None: self.process.wait(timeout=10)
