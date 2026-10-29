"""Standalone Windows scan / preview / record / replay commands."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import argparse
import json
import time
from camera_pipeline.capture import CameraError, open_camera, scan_cameras, probe_device, record_clip, preview_camera
from camera_pipeline.common import cv2_module, write_json

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['scan','preview','record','replay','_probe'])
    parser.add_argument('--device', type=int, default=0)
    parser.add_argument('--backend', choices=['dshow','msmf','any'], default='dshow')
    parser.add_argument('--max-devices', type=int, default=4)
    parser.add_argument('--width', type=int, default=640)
    parser.add_argument('--height', type=int, default=480)
    parser.add_argument('--fps', type=float, default=30)
    parser.add_argument('--seconds', type=float, default=6)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--video', type=Path)
    parser.add_argument('--preview', action='store_true')
    parser.add_argument('--headless', action='store_true')
    args = parser.parse_args()
    try:
        if args.mode == '_probe': result = probe_device(args.device,args.backend)
        elif args.mode == 'scan':
            attempts = scan_cameras(args.max_devices)
            result = {'schema':'flyvis-camera-scan-v1','attempts':attempts,
                      'available_devices':[r for r in attempts if r.get('available')]}
            if args.output: write_json(args.output,result)
            if not result['available_devices']:
                print(json.dumps(result)); raise CameraError('NO_CAMERA: no readable device in requested index range')
        elif args.mode in ('preview','record'):
            with open_camera(args.device,backend=args.backend,width=args.width,height=args.height,fps=args.fps) as camera:
                # Driver warmup is excluded from clip timestamps and recording FPS.
                for _ in range(5): camera.read_frame()
                if args.mode == 'record':
                    if args.output is None: parser.error('record requires --output (new directory)')
                    result = record_clip(camera,args.output,args.seconds,preview=args.preview)
                else: result = preview_camera(camera,args.seconds)
            result['resource_released'] = camera.closed and not camera.lock.exists()
        else:
            if args.video is None: parser.error('replay requires --video')
            cv2 = cv2_module(); video = cv2.VideoCapture(str(args.video)); count=0
            if not video.isOpened(): raise CameraError('VIDEO_UNREADABLE')
            fps = video.get(cv2.CAP_PROP_FPS); start=time.perf_counter()
            try:
                while True:
                    ok, frame=video.read()
                    if not ok: break
                    count+=1
                    if not args.headless:
                        cv2.imshow('Camera recorded video replay',frame)
                        if cv2.waitKey(max(1,round(1000/max(fps,1))))&0xff in (ord('q'),27): break
                result={'decoded_frames':count,'video_nominal_fps':fps,'decode_elapsed_s':time.perf_counter()-start,'resource_released':True}
            finally: video.release();cv2.destroyAllWindows()
        print(json.dumps(result,ensure_ascii=False,indent=2))
        return 0
    except (CameraError,RuntimeError,ValueError) as error:
        result={'status':'FAIL','error_type':type(error).__name__,'error':str(error)}
        print(json.dumps(result,ensure_ascii=False),file=sys.stderr)
        return 2

if __name__=='__main__': raise SystemExit(main())
