"""Fixed-camera export using the existing Octarine/rendercanvas renderer.

No geometry, camera, physics or shader implementation. The GUI still owns time.
The current frozen bridge and admitted frame pack do not import this opt-in helper.
"""
import io
import json
import time
import numpy as np
from PIL import Image


def encode_lossless(image):
    """Keep every visible pixel; omit alpha only when every alpha is 255."""
    if image.dtype != np.uint8 or image.ndim != 3 or image.shape[2] != 4:
        raise ValueError('Expected uint8 RGBA from the mature renderer')
    opaque=bool(np.all(image[:,:,3]==255))
    picture=Image.fromarray(image)
    if opaque: picture=picture.convert('RGB')
    buffer=io.BytesIO()
    picture.save(buffer,format='PNG',compress_level=1,optimize=False)
    return buffer.getvalue(),dict(codec='Pillow PNG',compress_level=1,optimize=False,
                                  mode='RGB' if opaque else 'RGBA',lossless=True,
                                  alpha_omitted_only_if_all_255=opaque)


class FixedCameraCapture:
    """An optional data-export adapter for an already configured AnatomyScene."""
    def init__(self,scene):
        from rendercanvas.offscreen import OffscreenRenderCanvas
        if not isinstance(scene.v.canvas,OffscreenRenderCanvas):
            raise ValueError('This adapter only accepts an existing offscreen canvas')
        if scene.type_filter!='all': raise ValueError('Fixed competition view must show all types')
        self.scene=scene
        self.camera_matrix=scene.v.camera.camera_matrix.copy()
        self.camera_state=self._camera_state()
        self.size=tuple(scene.v.size)
        self.profile=scene.profile
        self.color_encoding=scene.color_encoding.copy()
        self.last_key=None
        self.last_result=None
        self.draws=0

    def _camera_state(self):
        return json.dumps(self.scene.v.camera.get_state(),sort_keys=True,
                          default=lambda value:value.tolist())

    def capture(self,frame_index):
        start=time.perf_counter()
        scene=self.scene
        if type(frame_index) is not int or not 0<=frame_index<len(scene.time):
            raise ValueError('An exact in-range saved-state index is required')
        if (scene.type_filter!='all' or scene.profile!=self.profile or tuple(scene.v.size)!=self.size
                or not np.array_equal(scene.v.camera.camera_matrix,self.camera_matrix)
                or self._camera_state()!=self.camera_state
                or scene.color_encoding!=self.color_encoding):
            raise ValueError('Fixed view changed; create an explicitly configured new capture instead')
        # The scene is exclusively owned by its caller; never share it across threads.
        update_start=time.perf_counter()
        scene.set_frame(frame_index)
        update_ms=1000*(time.perf_counter()-update_start)
        if self.last_key==frame_index:
            payload,prior=self.last_result
            receipt=dict(prior,cache_hit=True,draw_performed=False,draw_and_readback_ms=0.,png_encode_ms=0.,
                         color_update_ms=update_ms,total_capture_ms=1000*(time.perf_counter()-start))
            return payload,receipt
        draw_start=time.perf_counter()
        image=np.asarray(scene.v.canvas.draw())
        draw_ms=1000*(time.perf_counter()-draw_start)
        encode_start=time.perf_counter()
        payload,codec=encode_lossless(image)
        encode_ms=1000*(time.perf_counter()-encode_start)
        self.draws+=1
        receipt=dict(frame_index=frame_index,activity_time_s=float(scene.time[frame_index]),
                     image_width=image.shape[1],image_height=image.shape[0],codec=codec,
                     cache_hit=False,draw_performed=True,color_update_ms=update_ms,
                     draw_and_readback_ms=draw_ms,png_encode_ms=encode_ms,
                     total_capture_ms=1000*(time.perf_counter()-start),activity_interpolation=False)
        self.last_key=frame_index
        self.last_result=(payload,receipt)
        return payload,receipt
