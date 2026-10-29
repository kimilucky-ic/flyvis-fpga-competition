"""CPU-only encoder for exact saved GUI frames; invoked only by explicit export."""
import hashlib
import json
from pathlib import Path
import sys
import time

import imageio_ffmpeg
from PIL import Image
import psutil


def main(folder):
    folder = Path(folder)
    manifest = json.loads((folder/'movie_manifest.json').read_text(encoding='utf-8'))
    output = folder/'ON60_40s_1080p.mp4'
    started = time.perf_counter()
    process = psutil.Process()
    cpu_start = process.cpu_times()
    peak_rss = process.memory_info().rss
    writer = imageio_ffmpeg.write_frames(str(output), (1920,1080), fps=30, codec='libx264', macro_block_size=1,
                                        pix_fmt_in='rgb24', pix_fmt_out='yuv420p',
                                        output_params=['-preset','veryfast','-crf','19','-threads','2','-movflags','+faststart'])
    writer.send(None)
    cached_k = None
    pixels = None
    try:
        for i,k in enumerate(manifest['source_for_video_frame']):
            if k != cached_k:
                row = manifest['frames'][k]
                data = (folder/row['png']).read_bytes()
                if hashlib.sha256(data).hexdigest() != row['png_sha256']: raise ValueError('GUI PNG changed')
                with Image.open(folder/row['png']) as image:
                    if image.size != (1920,1080): raise ValueError('Movie dimensions mismatch')
                    pixels = image.convert('RGB').tobytes()
                cached_k = k
            writer.send(pixels)
            if i%100 == 0:
                peak_rss = max(peak_rss,process.memory_info().rss)
                print(json.dumps(dict(encoded=i+1,total=manifest['video_frames'])),flush=True)
    finally:
        writer.close()
    count, duration = imageio_ffmpeg.count_frames_and_secs(str(output))
    if count != manifest['video_frames'] or abs(duration-manifest['duration_s']) > .02: raise ValueError('Video duration/frame count mismatch')
    reader = imageio_ffmpeg.read_frames(str(output))
    decoded = next(reader)
    reader.close()
    if tuple(decoded['size']) != (1920,1080): raise ValueError('Encoded video is not 1080p')
    cpu_end = process.cpu_times()
    receipt = dict(status='COMPLETED',encoder='CPU libx264',hardware_encoder=False,
                   video_sha256=hashlib.sha256(output.read_bytes()).hexdigest(),video_bytes=output.stat().st_size,
                   frames=count,fps=30,duration_s=duration,width=1920,height=1080,
                   encoded_wall_s=time.perf_counter()-started,python_peak_rss_bytes=peak_rss,
                   python_cpu_s=(cpu_end.user+cpu_end.system)-(cpu_start.user+cpu_start.system),
                   memory_scope='encoder Python only; ffmpeg child and browser not included',
                   subprocess_threads=2,run_id=manifest['run_id'],interpolation=False,
                   evidence_level='SOFTWARE_PILOT / OFFLINE_REPLAY',PL_execution=False)
    (folder/'encoder_receipt.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
    print(json.dumps(receipt),flush=True)


if __name__ == '__main__':main(sys.argv[1])
