"""Read-only verification of line 2's exported movie against the approved C pack."""
from pathlib import Path
import argparse, hashlib, json
import numpy as np
from PIL import Image
import imageio_ffmpeg
import psutil

HERE=Path(__file__).resolve().parent


def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def load(path):return json.loads(path.read_text(encoding='utf-8'))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('folder');args=parser.parse_args()
    folder=Path(args.folder).resolve()
    proc=psutil.Process();proc.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS);proc.cpu_affinity(proc.cpu_affinity()[:4])
    delivery=load(HERE/'delivery.json');pack_path=Path(delivery['manifest']);pack=load(pack_path)
    contract=load(HERE/'synchronization_contract.json');controls=load(HERE/'selection_and_controls.json')
    assert sha(pack_path)==delivery['manifest_sha256']
    manifest_path=folder/'movie_manifest.json';manifest=load(manifest_path)
    assert manifest['run_id']==contract['run_id']==pack['run_id']
    assert manifest['activity_sha256']==pack['activity_sha256']
    assert manifest['frame_pack_sha256']==delivery['manifest_sha256']
    assert Path(manifest['frame_pack_path']).resolve()==pack_path.resolve()
    assert manifest['color_encoding']==pack['color_encoding']
    assert manifest['PL_execution'] is False and manifest['display_kind']=='OFFLINE_REPLAY'
    assert manifest['model_dt_s']==.005 and manifest['video_fps']==30 and manifest['video_frames']==1200
    assert manifest['duration_s']==40. and manifest['source_for_video_frame']==contract['video']['source_for_video_frame']
    assert not manifest['interpolation'] and len(manifest['frames'])==485
    for k,row in enumerate(manifest['frames']):
        assert row['frame_index']==k and row['run_id']==contract['run_id']
        assert row['activity_time_s']==contract['activity_time_s'][k]
        assert row['input_time_s']==contract['input_time_s'][k]
        assert row['skeleton_sha256']==pack['frames'][k]['png_sha256']
        assert row['source_receipt_sha256']==pack['frames'][k]['receipt_sha256']
        image_path=(folder/row['png']).resolve();assert image_path.is_relative_to(folder)
        assert sha(image_path)==row['png_sha256']
    for row in controls['controls']:assert sha(Path(row['path']))==row['sha256']
    encoded=load(folder/'encoder_receipt.json')
    candidates=[p for p in folder.glob('*.mp4') if sha(p)==encoded['video_sha256']]
    assert len(candidates)==1
    movie=candidates[0]
    dest=HERE/'final_verification';dest.mkdir(exist_ok=True)
    indices=manifest['source_for_video_frame'];keys=(150,205,213,217,360,484)
    take={indices.index(k):k for k in keys};samples=[]
    stream=imageio_ffmpeg.read_frames(str(movie),pix_fmt='rgb24',input_params=['-threads','2'])
    meta=next(stream);assert tuple(meta['size'])==(1920,1080) and meta['fps']==30
    count=0
    for n,raw in enumerate(stream):
        count+=1
        if n in take:
            k=take[n];im=Image.frombytes('RGB',(1920,1080),raw)
            output=dest/f'decoded_step_{k:04d}.png';im.save(output)
            ref=np.asarray(Image.open(folder/manifest['frames'][k]['png']).convert('RGB'),dtype=float)
            mse=float(np.mean((np.asarray(im,dtype=float)-ref)**2))
            psnr=float(10*np.log10(255**2/mse)) if mse else 100.
            assert psnr>30,('encoded frame differs from its declared source',k,psnr)
            samples.append(dict(video_frame=n,source_step=k,png=str(output),sha256=sha(output),psnr_db=psnr))
    assert count==1200 and abs(meta['duration']-40)<.05
    result=dict(status='VERIFIED_LINE2_C_40S_MOVIE',movie=str(movie),video_sha256=sha(movie),
        movie_manifest=str(manifest_path),movie_manifest_sha256=sha(manifest_path),
        frame_pack_sha256=delivery['manifest_sha256'],color_encoding_sha256=delivery['color_encoding_sha256'],
        synchronization_contract_sha256=sha(HERE/'synchronization_contract.json'),
        run_id=contract['run_id'],source_steps=485,decoded_frames=count,fps=30,dimensions=[1920,1080],duration_s=40.,
        every_source_step_present=True,all_485_gui_png_hashes_verified=True,
        all_485_input_activity_times_and_skeleton_receipts_match=True,raw_model_dt_unchanged=True,
        original_A_and_ABC_controls_unchanged=True,decoded_samples=samples,
        visual_review='Decoded key frames saved for manual visual inspection; this JSON verifies identity and timing, not subjective aesthetics.',
        evidence_level='SAVED_SOFTWARE_EXPERIMENT_GUI_MOVIE',neural_compute=False,PL_execution=False)
    (dest/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(dict(status=result['status'],video=str(movie),frames=count,duration_s=40.,samples=len(samples))))


if __name__=='__main__':main()
