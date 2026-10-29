"""CPU MP4 input and fixed local retina sampling. No neural state inputs."""
import hashlib
from pathlib import Path
import cv2
import numpy as np

cv2.setNumThreads(1)
SIZE = 224
FPS = 100.0
DURATION = 2.0
DT = .005


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(4 * 1024**2), b''):
            h.update(b)
    return h.hexdigest()


def geometry(u, v):
    # Same orientation as upstream hex_utils.hex_to_pixel(mode='default').
    # Nearest-neighbour distance is six image pixels; y positive UP.
    x = 1.5 * np.asarray(v) * (6 / np.sqrt(3))
    y = -6 * (np.asarray(u) + np.asarray(v) / 2)
    return np.rint((SIZE - 1) / 2 + x).astype(np.int64), np.rint((SIZE - 1) / 2 - y).astype(np.int64)


def make_video(path, spec):
    """A true encoded 100 fps movie. Only generator receives ground truth."""
    path = Path(path)
    if path.exists():
        raise FileExistsError(path)
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*'mp4v'), FPS, (SIZE, SIZE))
    if not writer.isOpened():
        raise RuntimeError('MP4 encoder unavailable')
    yy, xx = np.mgrid[:SIZE, :SIZE]
    x = (xx - (SIZE - 1) / 2) / 6
    y = ((SIZE - 1) / 2 - yy) / 6
    theta = np.deg2rad(spec.get('angle_deg', 0))
    projection = x * np.cos(theta) + y * np.sin(theta)
    try:
        for j in range(int(FPS * DURATION)):
            t = j / FPS
            kind = spec['kind']
            if kind == 'gray':
                brightness = np.full((SIZE, SIZE), spec['level'])
            elif kind == 'flash':
                a, b = (.2, .8) if spec['polarity'] == 'ON' else (.8, .2)
                brightness = np.full((SIZE, SIZE), a if t < 1 else b)
            else:
                if kind == 'motion':
                    speed = spec['speed_hex_s']
                    position = -speed * .75 + speed * max(t - .5, 0)
                else:
                    position = spec.get('offset_hex', 0)
                behind = .5 * (1 + np.tanh((position - projection) * 6))
                brightness = .2 + .6 * behind if spec['polarity'] == 'ON' else .8 - .6 * behind
            gray = np.rint(brightness * 255).clip(0, 255).astype(np.uint8)
            writer.write(cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR))
    finally:
        writer.release()


def decode_video(path, sampler):
    """Reads pixels only, never ground truth. First two seconds; fixed ZOH."""
    path = Path(path)
    xs = sampler['x_pixel']; ys = sampler['y_pixel']
    if np.any(xs < 1) or np.any(ys < 1) or np.any(xs >= SIZE - 1) or np.any(ys >= SIZE - 1):
        raise ValueError('retina outside image')
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise ValueError('video cannot be opened')
    fps = float(cap.get(cv2.CAP_PROP_FPS))
    if not np.isfinite(fps) or fps <= 0 or fps > 1000:
        cap.release(); raise ValueError('constant positive FPS required')
    n_needed = int(np.ceil(DURATION * fps))
    values = []; native_sizes = set()
    try:
        for j in range(n_needed):
            ok, frame = cap.read()
            if not ok:
                break
            h, w = frame.shape[:2]; native_sizes.add((h, w))
            if (h, w) != (SIZE, SIZE):
                scale = min(SIZE / w, SIZE / h)
                rw, rh = max(1, round(w * scale)), max(1, round(h * scale))
                resized = cv2.resize(frame, (rw, rh), interpolation=cv2.INTER_AREA)
                canvas = np.full((SIZE, SIZE, 3), 128, np.uint8)
                y0, x0 = (SIZE - rh) // 2, (SIZE - rw) // 2
                canvas[y0:y0+rh, x0:x0+rw] = resized
                frame = canvas
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            samples = np.stack([gray[ys+dy, xs+dx] for dy in [-1,0,1] for dx in [-1,0,1]])
            values.append(samples.mean(axis=0, dtype=np.float64).astype(np.float32) / np.float32(255))
    finally:
        cap.release()
    frame_ids = np.floor(np.arange(400) * DT * fps + 1e-9).astype(np.int64)
    if len(values) <= int(frame_ids.max()):
        raise ValueError('two seconds of decodable video required; no temporal padding')
    values = np.array(values, np.float32)
    return values[frame_ids], dict(video_sha256=sha(path),fps=fps,decoded_frames=len(values),
        used_window_s=[0,2], model_steps=400,dt_s=DT,input_frame_index=frame_ids.tolist(),
        input_time_s=(np.arange(400)*DT).tolist(),activity_time_s=((np.arange(400)+1)*DT).tolist(),
        native_sizes=sorted(native_sizes),retina_points=len(xs),
        temporal_policy='causal zero order hold; no future-frame interpolation',
        spatial_policy='224 square; preserve aspect with gray letterbox; 3x3 local mean',
        angle_convention='0 right; 90 up; 180 left; 270 down, image coordinates')
