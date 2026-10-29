"""Independent Windows camera and original FlyVis input lane."""
from .capture import open_camera, read_frame, record_clip, scan_cameras, CameraError

def video_to_flyvis_stimulus(*args, **kwargs):
    from .adapter import video_to_flyvis_stimulus as convert
    return convert(*args, **kwargs)

def save_stimulus(*args, **kwargs):
    from .adapter import save_stimulus as save
    return save(*args, **kwargs)
