from __future__ import annotations
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def utc_now():
    return datetime.now(timezone.utc).isoformat()

def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2, default=str), encoding='utf-8')
    os.replace(temporary, path)

def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def cv2_module():
    # Local optional dependency, without modifying the shared fly .venv.
    vendor = ROOT / '_vendor'
    if vendor.exists() and str(vendor) not in sys.path:
        sys.path.insert(0, str(vendor))
    try:
        import cv2
    except ImportError as error:
        raise RuntimeError('OpenCV missing. Run camera_pipeline/setup_camera.ps1 first.') from error
    return cv2

def new_directory(path):
    path = Path(path).resolve()
    path.mkdir(parents=True, exist_ok=False)
    return path
