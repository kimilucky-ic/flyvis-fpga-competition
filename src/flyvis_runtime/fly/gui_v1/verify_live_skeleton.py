"""Read-only post-run verification; no CUDA/model import or graphics launch."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image
from live_protocol import HERE,load,require,sha,write
from spatial_state import SpatialRegistry
from stream_manual_summary import manual_summary
from stream_clock import control_clock,model_source_time


def verify(session):
    root=HERE/'runtime/live'/session;stream=root/'stream';graphics=root/'skeleton'
    require(root.resolve().parent==(HERE/'runtime/live').resolve(),'SESSION_SCOPE')
    manifest=load(stream/'manifest.json')
    for name,digest in manifest.items():
        f=(stream/name).resolve();require(f.is_relative_to(stream.resolve()) and sha(f)==digest,'SAVED_ASSET_SHA '+name)
    result=load(stream/'result.json');control=load(stream/'control.json');summary=manual_summary(stream,control)
    clock=control_clock(control)
    if 'clock' in control:
        require(result['clock']==clock,'RESULT_CLOCK_IDENTITY')
        for line in (stream/'step_commits.jsonl').read_text(encoding='utf-8').splitlines():
            c=json.loads(line);k=c['step_id']
            require(c['input_time_s']==k*.005 and c['activity_time_s']==k*.005+.005,'ALL_STEP_MATH_TIME')
            require(c['scheduled_wall_time_s']==k/clock['target_steps_per_s']
                    and c['source_model_time_s']==c['source_wall_time_s']*clock['model_seconds_per_wall_second']
                    and c['source_model_time_s']<=c['input_time_s'],'ALL_STEP_CAUSAL_CLOCK_MAPPING')
    rows=[json.loads(line) for line in (graphics/'frames.jsonl').read_text(encoding='utf-8').splitlines()]
    draws=[json.loads(line) for line in (stream/'display_receipts.jsonl').read_text(encoding='utf-8').splitlines()]
    registry=SpatialRegistry();by_request={r['request_id']:r for r in rows};lags=[];camera_evidence=None
    if control['source_kind']=='real_windows_camera':
        capture=load(stream/'camera_capture.json')
        require(capture['run_id']==result['run_id'] and capture['session_id']==session and capture['closed'] is True,'CAMERA_RELEASE_IDENTITY')
        require(capture['capture']['state']=='closed' and capture['source_kind']=='real_windows_camera','ACTUAL_CAMERA_CLOSED')
        if 'clock' in control:require(capture['clock']==clock,'CAPTURE_CLOCK_IDENTITY')
        sources=[load(f) for f in sorted((stream/'sources').glob('*.json'))]
        for index,s in enumerate(sources):
            prefix=stream/'sources'/f'{s["sequence"]:06d}'
            require(s['source_kind']=='real_windows_camera' and s['run_id']==result['run_id']
                    and s['camera_id']==control['camera_id'] and s['camera_sequence']==s['sequence'],'CAMERA_SOURCE_IDENTITY')
            require(s['timestamp_kind']=='Windows_receipt_not_sensor' and s['camera_received_utc'],'CAPTURE_CLOCK_SEMANTICS')
            model_source_time(s,clock)
            require(sha(prefix.with_suffix('.png'))==s['png_sha256']==s['sha256'],'ACTUAL_CAMERA_PIXELS_SHA')
            with Image.open(prefix.with_suffix('.png')) as im:require(list(im.size)==s['camera_resolution'],'ACTUAL_CAMERA_RESOLUTION')
            x=np.load(prefix.with_name(prefix.name+'_hex.npy'),allow_pickle=False)
            require(x.shape==(721,) and hashlib.sha256(x.tobytes()).hexdigest()==s['hex_values_sha256'],'CAMERA_OFFICIAL_INPUT_SHA')
            if index:require(s['sequence']==sources[index-1]['sequence']+1 and s['received_monotonic_ns']>sources[index-1]['received_monotonic_ns'],'CAMERA_SOURCE_ORDER')
        camera_evidence=dict(capture=capture,capture_sha256=sha(stream/'camera_capture.json'),saved_source_frames=len(sources),
            timestamp_uncertainty='Sensor exposure and driver queue delay are unavailable; latency starts at Windows frame receipt')
    require(len(by_request)==len(rows),'UNIQUE_RENDER_REQUESTS')
    for r in rows:
        prefix=stream/'snapshots'/f'{r["serial"]:06d}'
        p=load(prefix.with_suffix('.json'))
        if 'clock' in control:
            require(p['clock']==clock and model_source_time(p['source'],clock)<=p['input_time_s'],'SNAPSHOT_CLOCK_MAPPING')
        if camera_evidence:
            require(p['execution_kind']=='LIVE_CAMERA_GPU' and p['source_kind']=='real_windows_camera','CAMERA_GPU_NOT_DIGITAL_OR_REPLAY')
        with np.load(prefix.with_suffix('.npz'),allow_pickle=False) as z:
            require(z['full'].shape==(45669,) and z['flow'].shape==(2,721) and z['input'].shape==(721,),'FULL_SNAPSHOT_SHAPES')
            values=z['full'][registry.ids]
            means=values.reshape(8,721).mean(axis=1,dtype=np.float64)
            require(np.array_equal(means,np.asarray(r['means'])),'ACTUAL_FULL_STATE_MEANS')
            require(hashlib.sha256(values.tobytes()).hexdigest()==r['spatial_values_sha256']==p['spatial']['values_sha256'],'ACTIVITY_SLICE_IDENTITY')
            require(hashlib.sha256(z['input'].tobytes()).hexdigest()==p['source']['hex_values_sha256'],'ACTUAL_INPUT_VALUES')
        for key in ('run_id','session_id','step_id','state_token','activity_time_s'):
            require(r[key]==p[key],'RENDER_SNAPSHOT_'+key)
        require(r['source_sequence']==p['source']['sequence'] and r['PL_execution'] is False,'SOURCE_FRAME_AND_NO_PL')
        lags.append(p['model_lag_s']*1000)
        # The producer's manifest already validates every retained original source image.
        b=.25+.75*np.clip(np.abs(means)/r['color_encoding']['intensity_domain'][1],0,1)**.45
        require(np.array_equal(b,np.array([s['brightness_factor'] for s in r['type_states']])),'FIXED_BRIGHTNESS_ONLY')
    for d in draws:
        r=by_request[d['skeleton_request_id']]
        require(d['run_id']==r['run_id'] and d['serial']==r['serial'] and d['step_id']==r['step_id']
                and d['skeleton_raw_sha256']==r['raw_sha256'],'ACTUAL_BROWSER_DRAW_RECEIPT')
        if camera_evidence:
            p=load(stream/'snapshots'/f'{r["serial"]:06d}.json')
            require(d['source_kind']=='real_windows_camera' and d['source_sequence']==p['source']['sequence']
                    and d['source_png_sha256']==p['source']['png_sha256'],'BROWSER_CAMERA_SAME_SOURCE_FRAME')
            if 'clock' in control:require(d['clock']==clock and d['wall_elapsed_s']==p['wall_elapsed_s']
                    and d['activity_time_s']==p['activity_time_s'],'BROWSER_DUAL_CLOCK_IDENTITY')
    require(result['original_weights_unchanged'] and result['decoder_unchanged'],'ORIGINAL_MODEL_DECODER_AUDIT')
    samples=[]
    for file in graphics.glob('*.rgba'):
        r=load(file.with_name(file.stem+'_receipt.json'));raw=file.read_bytes()
        require(hashlib.sha256(raw).hexdigest()==r['raw_sha256'],'ORIGINAL_RAW_PIXEL_SAMPLE')
        # Only a saved-file preview after execution; this codec is never in the live path.
        Image.frombytes('RGBA',(r['image_width'],r['image_height']),raw).save(file.with_suffix('.png'))
        samples.append(dict(file=str(file),step=r['step_id'],raw_sha256=r['raw_sha256'],preview=str(file.with_suffix('.png'))))
    def stats(key,source=rows):
        a=[r[key] for r in source];return dict(p50_ms=float(np.percentile(a,50)),p95_ms=float(np.percentile(a,95)))
    return dict(status='PASS_ACTUAL_BOUNDED_GPU_SKELETON_LINK' if summary['status']=='COMPLETED' else 'INCOMPLETE_LIVE_RUN_PRESERVED',
                summary=summary,checked_saved_files=len(manifest),checked_rendered_means=len(rows)*8,
                checked_full_nodes_per_snapshot=45669,checked_renderer_frames=len(rows),checked_browser_frames=len(draws),
                actual_GPU_operations_this_verifier=0,FPGA_status='NOT_CONNECTED',PL_execution=False,camera_evidence=camera_evidence,
                all_means_exact=True,model_and_decoder_unchanged=True,pixel_samples=samples,
                displayed_model_lag_ms=dict(p50=float(np.percentile(lags,50)),p95=float(np.percentile(lags,95))),
                timings={k:stats(k) for k in ['color_update_ms','draw_and_readback_ms','raw_copy_ms','total_render_raw_ms','windows_render_roundtrip_ms']},
                browser_stages={k:stats(k,draws) for k in ['skeleton_fetch_ms','skeleton_verify_ms','skeleton_put_image_ms','skeleton_draw_ms']},
                source_identity=dict(session=session,run=result['run_id'],manifest_sha256=sha(stream/'manifest.json'),
                                     renderer_frames_sha256=sha(graphics/'frames.jsonl'),draw_receipts_sha256=sha(stream/'display_receipts.jsonl')))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('session');parser.add_argument('--out',required=True);args=parser.parse_args()
    result=verify(args.session);write(Path(args.out),result)
    print(json.dumps({k:result[k] for k in ['status','checked_saved_files','checked_rendered_means','checked_browser_frames','timings','browser_stages']}))
