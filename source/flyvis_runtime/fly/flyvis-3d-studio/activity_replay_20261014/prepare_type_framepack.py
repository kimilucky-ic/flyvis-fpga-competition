"""One bounded, source-verified pack of actual Octarine PNGs; no neural compute."""
from pathlib import Path
from types import SimpleNamespace
from datetime import datetime, timezone
import argparse, base64, hashlib, json, os, shutil, sys, time
from scene import ROOT, research_guard
from bridge import Bridge
from presentation import sha
import numpy as np
import psutil

PACK = ROOT/'framepacks'/'ON60_type_hue_v1_1280x640_cpu'

def save_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')

def request(bridge, frame, request_id, **extra):
    return dict(run_id=bridge.identity['run_id'], activity_sha256=bridge.identity['activity_sha256'],
                activity_time_sha256=bridge.identity['activity_time_sha256'],
                frame_index=frame, activity_time_s=float(bridge.scene.time[frame]),
                request_id=request_id, profile='light', type_filter='all', **extra)

def unpack_checked(bridge, reply, frame):
    meta=reply['metadata']
    payload=base64.b64decode(reply['png_base64'], validate=True)
    assert meta['frame_index']==frame and meta['activity_time_s']==float(bridge.scene.time[frame])
    assert meta['run_id']==bridge.identity['run_id'] and meta['activity_sha256']==bridge.identity['activity_sha256']
    assert hashlib.sha256(payload).hexdigest()==meta['png_sha256']
    assert meta['image_width']==1280 and meta['image_height']==640
    assert meta['type_filter']=='all' and len(meta['visible_types'])==len(bridge.scene.objects)
    assert meta['rois_visible'] and meta['background_style']=='simplified_mesh'
    assert meta['color_encoding']==bridge.scene.color_encoding
    assert meta['camera_framing']['cropped_node_count']==0
    assert meta['evidence_level']=='OFFLINE_SOFTWARE_REPLAY' and meta['PL_execution'] is False
    for i,state in enumerate(meta['type_states']):
        assert state['activity_signed']==float(bridge.scene.activity[frame,i])
        assert state['brightness_factor']>=.38 and state['visible']
    return payload,meta

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--mode', choices=['probe','pack','gpu-probe'], required=True)
    args=ap.parse_args()
    process=psutil.Process()
    process.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    output=PACK if args.mode=='pack' else ROOT/'evidence'/('type_hue_'+args.mode+'_r1')
    output.mkdir(parents=True,exist_ok=True)
    if (output/'manifest.json').exists() or (output/'result.json').exists():
        raise RuntimeError('Evidence already exists; refusing to overwrite completed output: '+str(output))
    if args.mode=='pack' and shutil.disk_usage(output).free<512*1024**2:
        raise RuntimeError('Need at least 512 MiB free for bounded frame package')
    renderer='gpu' if args.mode=='gpu-probe' else 'cpu'
    if renderer=='gpu':
        guard=research_guard()
        if guard['busy'] or guard['markers']:
            result=dict(status='SKIPPED_RESEARCH_BUSY',guard=guard,renderer_created=False,neural_compute=False,
                        PL_execution=False,time_utc=datetime.now(timezone.utc).isoformat())
            save_json(output/'result.json',result)
            print(json.dumps(result),flush=True)
            return
    def offline(event,parameters):
        if event=='socket.connect': raise RuntimeError('Framepack generation is local-file-only')
    sys.addaudithook(offline)
    start=time.perf_counter()
    cpu0=process.cpu_times()
    bridge=None
    try:
        bridge=Bridge(SimpleNamespace(model=ROOT/'model.json',renderer=renderer,profile='light',width=1280,height=640,
                                      tag='type_hue_'+args.mode+'_r1'))
        initialization_s=time.perf_counter()-start
        peak_rss=process.memory_info().rss
        # Startup itself has already made and memoized the actual frame zero.
        repeated=bridge.render(request(bridge,0,'first_repeat_0'))
        payload0,meta0=unpack_checked(bridge,repeated,0)
        assert meta0['cache']['hit'] and not meta0['draw_performed'] and bridge.draw_count==1
        indexes=range(len(bridge.scene.time)) if args.mode=='pack' else [0,213,214]
        frames=[]
        requests=[]
        draw_times=[bridge.startup_frame['render_and_png_ms']]
        sample_metadata={}
        (output/'frames').mkdir(exist_ok=True)
        (output/'receipts').mkdir(exist_ok=True)
        generation_start=time.perf_counter()
        for frame in indexes:
            reply=bridge.render(request(bridge,frame,f'{args.mode}_{frame:04d}'))
            payload,meta=unpack_checked(bridge,reply,frame)
            png_relative=f'frames/frame_{frame:04d}.png'
            receipt_relative=f'receipts/frame_{frame:04d}.json'
            (output/png_relative).write_bytes(payload)
            save_json(output/receipt_relative,meta)
            frames.append(dict(frame_index=frame,activity_time_s=meta['activity_time_s'],
                               png=png_relative,png_sha256=meta['png_sha256'],
                               receipt=receipt_relative,receipt_sha256=sha(output/receipt_relative)))
            requests.append(meta['total_request_ms'])
            if meta['draw_performed']: draw_times.append(meta['render_and_png_ms'])
            peak_rss=max(peak_rss,process.memory_info().rss)
            if frame in (0,213,214,484): sample_metadata[frame]=meta
            if frame%60==0 or frame==len(bridge.scene.time)-1:
                print(json.dumps(dict(progress=len(frames),last_frame=frame,draws=bridge.draw_count,
                                      elapsed_s=round(time.perf_counter()-start,2),rss_mib=round(peak_rss/1024**2,1))),flush=True)
        generation_s=time.perf_counter()-generation_start
        # One duplicate proves that delivery can echo a new request without drawing.
        draws_before=bridge.draw_count
        last=frames[-1]['frame_index']
        duplicate=bridge.render(request(bridge,last,'duplicate_last_no_redraw'))
        _,duplicate_meta=unpack_checked(bridge,duplicate,last)
        assert duplicate_meta['cache']['hit'] and duplicate_meta['png_sha256']==frames[-1]['png_sha256']
        assert bridge.draw_count==draws_before and duplicate_meta['request_id']=='duplicate_last_no_redraw'
        save_json(output/'duplicate_receipt.json',duplicate_meta)
        # Readback every written artifact once before the manifest is admitted.
        for row in frames:
            assert sha(output/row['png'])==row['png_sha256']
            assert sha(output/row['receipt'])==row['receipt_sha256']
        assert len(set(row['png_sha256'] for row in frames))>1
        for name,digest in bridge.source_code_sha256.items():
            assert sha(ROOT/name)==digest, 'Renderer source changed during generation'
        cpu1=process.cpu_times()
        resources=dict(renderer=renderer,adapter=bridge.adapter,pid=os.getpid(),priority='BELOW_NORMAL',
                       initialization_s=initialization_s,generation_s=generation_s,
                       elapsed_s=time.perf_counter()-start,cpu_user_s=cpu1.user-cpu0.user,cpu_system_s=cpu1.system-cpu0.system,
                       peak_sampled_rss_mib=peak_rss/1024**2,actual_draw_count=bridge.draw_count,
                       render_and_png_ms=dict(p50=float(np.median(draw_times)),p95=float(np.percentile(draw_times,95)),
                                              minimum=float(min(draw_times)),maximum=float(max(draw_times))),
                       request_ms_p50=float(np.median(requests)),cache=bridge.health()['cache'],
                       duplicate_total_request_ms=duplicate_meta['total_request_ms'],
                       timing_scope='actual offscreen render plus PNG encoding, not screen refresh or neural inference',
                       neural_compute=False,PL_execution=False)
        common=dict(schema='line10.fixed_camera_framepack.v1',status='COMPLETE',
                    created_utc=datetime.now(timezone.utc).isoformat(),run_id=bridge.identity['run_id'],
                    activity_sha256=bridge.identity['activity_sha256'],activity_time_sha256=bridge.identity['activity_time_sha256'],
                    input_time_sha256=bridge.identity['input_time_sha256'],replay_sha256=bridge.identity['replay_sha256'],
                    mapping_sha256=bridge.identity['mapping_sha256'],identity=bridge.identity,
                    color_encoding=bridge.scene.color_encoding,background_manifest_sha256=bridge.scene.background_manifest_sha256,
                    image_width=1280,image_height=640,frame_count=len(frames),profile='light',type_filter='all',
                    background_style='simplified_mesh',rois_visible=True,renderer='NAVis/Octarine/pygfx',adapter=bridge.adapter,
                    source_code_sha256=bridge.source_code_sha256,producer_sha256=sha(Path(__file__)),
                    model_json_sha256=sha(ROOT/'model.json'),model_dt_s=bridge.identity['dt_s'],
                    presentation_steps_per_s=12,nominal_duration_s=len(frames)/12,
                    interpolation='none; each PNG is one exact saved state',
                    camera_state=meta0['camera_state'],camera_framing=meta0['camera_framing'],
                    resources=resources,frames=frames,evidence_level='OFFLINE_SOFTWARE_REPLAY',PL_execution=False,
                    admission='consumer must explicitly register this exact manifest path and SHA256')
        bridge.scene.v.close()
        bridge.log(dict(event='closed',pid=os.getpid(),reason='bounded_'+args.mode+'_complete'))
        bridge=None
        common['renderer_closed']=True
        if args.mode=='pack':
            assert len(frames)==485 and [x['frame_index'] for x in frames]==list(range(485))
            temporary=output/'manifest.pending.json'
            save_json(temporary,common)
            temporary.replace(output/'manifest.json')
            print(json.dumps(dict(status='COMPLETE',manifest=str(output/'manifest.json'),sha256=sha(output/'manifest.json'),resources=resources)),flush=True)
        else:
            save_json(output/'result.json',common)
            print(json.dumps(dict(status='COMPLETE',result=str(output/'result.json'),resources=resources)),flush=True)
    except Exception as exc:
        save_json(output/'failure.json',dict(error=repr(exc),mode=args.mode,time_utc=datetime.now(timezone.utc).isoformat()))
        raise
    finally:
        if bridge is not None: bridge.scene.v.close()

if __name__=='__main__': main()
