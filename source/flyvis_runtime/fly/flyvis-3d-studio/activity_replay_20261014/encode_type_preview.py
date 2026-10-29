"""Encode existing actual PNGs only; repeat saved states, never interpolate them."""
from pathlib import Path
import hashlib, json, math, subprocess, time
from PIL import Image
import imageio_ffmpeg
import psutil

ROOT=Path(__file__).resolve().parent
PACK=ROOT/'framepacks'/'ON60_type_hue_v1_1280x640_cpu'

def sha(path):
    with path.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()

def main():
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    manifest_path=PACK/'manifest.json'
    expected='dfddcf69d96f0354ffa01702e2850d8b6c37dd14f78b64851f41892a2451d4fb'
    if sha(manifest_path)!=expected: raise RuntimeError('Only the explicitly admitted CPU pack is allowed')
    manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
    output=PACK/'ON60_八类真实骨架_40秒预览.mp4'
    receipt=PACK/'video_receipt.json'
    if output.exists() or receipt.exists(): raise RuntimeError('Refusing to overwrite completed preview')
    fps=30
    state_rate=12
    count=math.ceil(manifest['frame_count']*fps/state_rate)
    ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
    command=[ffmpeg,'-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24',
             '-s','1280x640','-r',str(fps),'-i','pipe:0','-an','-c:v','libx264','-threads','2',
             '-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(output)]
    start=time.perf_counter()
    cached_frame=None
    sample_map=[]
    with (PACK/'video_encode.log').open('w',encoding='utf-8') as log:
        encoder=subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=log)
        try:
            for n in range(count):
                k=min(n*state_rate//fps,manifest['frame_count']-1)
                if k!=cached_frame:
                    row=manifest['frames'][k]
                    source=PACK/row['png']
                    assert sha(source)==row['png_sha256']
                    with Image.open(source) as im: pixels=im.convert('RGB').tobytes()
                    cached_frame=k
                encoder.stdin.write(pixels)
                sample_map.append(k)
            encoder.stdin.close()
            code=encoder.wait(timeout=60)
            if code: raise RuntimeError('Encoder failed: '+str(code))
        finally:
            if encoder.poll() is None:
                encoder.terminate()
                encoder.wait(timeout=10)
    decoded_count,decoded_duration=imageio_ffmpeg.count_frames_and_secs(str(output))
    assert decoded_count==count and set(sample_map)==set(range(manifest['frame_count']))
    result=dict(schema='line10.repeated_state_video.v1',status='COMPLETE',video=output.name,sha256=sha(output),
                manifest_sha256=expected,run_id=manifest['run_id'],color_encoding=manifest['color_encoding'],
                dimensions=[1280,640],fps=fps,video_frame_count=count,decoded_frame_count=decoded_count,
                nominal_states_duration_s=485/12,video_duration_s=count/fps,decoded_duration_s=decoded_duration,
                saved_state_rate=state_rate,model_dt_s=manifest['model_dt_s'],
                frame_mapping='source_index=min(floor(video_frame_index*12/30),484)',
                video_frame_to_source=sample_map,interpolation=False,encoder='CPU libx264, 2 threads, CRF18',
                encode_and_decode_verify_s=time.perf_counter()-start,neural_compute=False,PL_execution=False,
                scope='3D component preview only; unified 1080p stage and final competition film are owned by line 2')
    receipt.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(dict(video=str(output),frames=count,duration_s=count/fps,elapsed_s=result['encode_and_decode_verify_s'])))

if __name__=='__main__': main()
