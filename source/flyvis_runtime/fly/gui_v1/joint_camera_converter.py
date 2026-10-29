"""Reuse the existing official BoxEye converter; no camera or neural inference."""
import argparse
import base64
import io
import os
import sys
import time
import numpy as np
from live_protocol import HERE, host_path, load, require
from stream_transport import RPC
from joint_camera_protocol import digest,conversion_receipt


def run(root):
    require(os.environ.get('CUDA_VISIBLE_DEVICES') == '-1', 'JOINT_CONVERTER_MUST_BE_CPU')
    sys.path.insert(0,str(HERE.parent))
    from PIL import Image
    from prepared_camera_input import PreparedCameraInput
    root = host_path(root)
    session = load(root / 'session.json')
    converter = PreparedCameraInput()
    converter.render(np.full((480, 640, 3), 127, dtype=np.uint8))
    client = RPC(load(root / 'joint_endpoint.json'), 'renderer')
    try:
        client.call('ready')
        while not any((root/name).exists() for name in ('STOP_REQUEST.json','CONVERTER_STOP_REQUEST.json')):
            require(time.time() < session['end_unix'], 'JOINT_CONVERTER_SCOPE_EXPIRED')
            frame = client.call('raw')
            if frame is None:
                continue
            image = np.asarray(Image.open(io.BytesIO(base64.b64decode(frame['png']))).convert('RGB'))[:, :, ::-1].copy()
            values, coordinates, transform = converter.render(image)
            frame['values'] = values[0].tolist()
            frame['source']['hex_values_sha256'] = digest(values[0].tobytes())
            frame['conversion'] = dict(backend='ORIGINAL_PREPARED_CAMERA_INPUT_BOXEYE_CPU',
                dependencies_sha256=session['camera_dependencies_sha256'], transform=transform,
                coordinates_sha256=digest(np.asarray(coordinates).tobytes()))
            client.call('converted', conversion_receipt(frame))
    except (OSError,ValueError,ConnectionError):
        if not any((root/name).exists() for name in ('STOP_REQUEST.json','CONVERTER_STOP_REQUEST.json')):
            raise
    finally:
        client.close()


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--root', required=True)
    run(p.parse_args().root)
