"""Independent CPU file/input checks of line-4's sealed package.

No FlyVis/torch/camera/decoder import, device connection, service or source write.
This verifier does not register results or create a neural reference.
"""
import csv
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import time

import numpy as np
from PIL import Image

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent/'fpga/flyvis-circuit-selection/controlled_stimuli_20261019_v1'
OUT=HERE/'evidence/stimuli28_gpu_fpga_readonly_20261019'
PACK_SHA='7291e37f21a94244b81fb916dca0296d310ce354ac32fc4c8e9077d6aeac3500'
MANIFEST_SHA='a398175a2f9080d5a1aaa49ceb57ee3fe57dcbe282521e55cc373fa0669302c1'


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def inside(name):
    p=(ROOT/name).resolve()
    assert p.is_relative_to(ROOT.resolve()),'PACKAGE_PATH_ESCAPE'
    return p


def load(name):return json.loads(inside(name).read_text(encoding='utf-8'))


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    started=time.perf_counter();assert sha(ROOT/'PACK.json')==PACK_SHA and sha(ROOT/'DELIVERY_MANIFEST.json')==MANIFEST_SHA
    manifest=load('DELIVERY_MANIFEST.json');pack=load('PACK.json');entries={}
    assert manifest['actual_neural_steps']==0 and manifest['GPU'] is manifest['board'] is False
    for row in manifest['files']:
        path=inside(row['path']);assert path not in entries
        assert path.stat().st_size==row['bytes'] and sha(path)==row['sha256'],row['path']
        entries[path]=row
    assert len(entries)==manifest['file_count']==2160
    assert pack['schema']=='flyvis-controlled-stimuli/v1' and pack['steps']==485 and pack['dt_s']==.005
    assert pack['input_time_offset_s']==0 and pack['onset_step']==200 and pack['stop_step']==400
    assert pack['neural_results'] is pack['model_comparison_id'] is None and pack['all_backends_status']=='NOT_RUN'
    validation=load('VALIDATION.json');audit=load('RENDER_AUDIT.json')
    assert validation['status']=='PASS_CPU_STIMULUS_AND_INTERFACE_ONLY' and validation['conditions']==28
    assert audit['neural_steps']==0 and audit['reference_bitwise_equal'] is True and audit['reference_max_abs']==0
    with inside(pack['coordinates']['path']).open(encoding='utf-8',newline='') as f:coords=list(csv.DictReader(f))
    uv=np.asarray([[int(c['u']),int(c['v'])] for c in coords]);assert uv.shape==(721,2)
    registry=json.loads((HERE/'live_registry.json').read_text(encoding='utf-8'))
    assert np.array_equal(uv,np.load(registry['pins']['coordinates']['path'],allow_pickle=False))
    spatial=json.loads((HERE/'spatial_registry.json').read_text(encoding='utf-8'))
    from spatial_state import SpatialRegistry
    ids=np.load(inside(pack['T4T5_global_ids']['path']),allow_pickle=False)
    assert np.array_equal(ids.reshape(-1),SpatialRegistry().ids)
    initials={}
    for name,row in pack['initial_state_assets'].items():
        path=inside(row['path']);a=np.load(path,allow_pickle=False)
        assert a.shape==(45669,) and a.dtype==np.dtype('<f4') and np.isfinite(a).all()
        assert sha(path)==row['file_sha256'] and hashlib.sha256(a.tobytes()).hexdigest()==row['raw_array_sha256']
        initials[name]=dict(file_sha256=row['file_sha256'],raw_array_sha256=row['raw_array_sha256'],selected=False)
    before=set(sys.modules)
    spec=importlib.util.spec_from_file_location('_stimuli28_original_reader',inside('reader.py'))
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    assert not ({'torch','flyvis','cv2'} & (set(sys.modules)-before))
    conditions={c['condition_id']:c for c in pack['conditions']};assert len(conditions)==28
    seen_images={};arrays={};results=[]
    for cid,c in conditions.items():
        assert c['neural_results'] is c['comparison_id'] is None
        assert c['GPU_execution'] is c['FPGA_execution'] is False and c['neural_function_acceptance']=='NOT_RUN'
        for a in c['paths'].values():assert inside(a['path']) in entries and sha(inside(a['path']))==a['sha256']
        x=np.load(inside(c['paths']['input']['path']),allow_pickle=False)
        movie=np.load(inside(c['paths']['stimulus']['path']),allow_pickle=False)
        raw=inside(c['paths']['raw_input']['path']).read_bytes()
        assert x.shape==(485,721) and x.dtype==np.dtype('<f4') and x.flags.c_contiguous and np.isfinite(x).all()
        assert np.all((x>=0)&(x<=1)) and movie.shape==(1,485,1,721)
        assert x.tobytes()==movie.tobytes()==raw and hashlib.sha256(raw).hexdigest()==c['input_raw_sha256']
        t=np.load(inside(c['paths']['input_time']['path']),allow_pickle=False)
        after=np.load(inside(c['paths']['state_time']['path']),allow_pickle=False)
        assert np.array_equal(t,np.arange(485)*.005) and np.array_equal(after,(np.arange(485)+1)*.005)
        with inside(c['paths']['frame_map']['path']).open(encoding='utf-8',newline='') as f:frames=list(csv.DictReader(f))
        assert len(frames)==485
        for k,f in enumerate(frames):
            assert int(f['step_id'])==int(f['video_frame'])==k and float(f['video_pts_s'])==k/50
            assert float(f['input_time_s'])==t[k] and float(f['state_time_s'])==after[k]
            png=inside(f['source_png']);assert png in entries
            if png not in seen_images:
                with Image.open(png) as image:
                    assert image.mode=='L' and image.size==(418,418)
                    seen_images[png]=hashlib.sha256(image.tobytes()).hexdigest()
            assert seen_images[png]==f['pixel_sha256']
        source=module.FrozenInput(ROOT,cid)
        try:
            for k in (0,199,200,399,400,484):
                row=source.frame(k)
                assert np.array_equal(row['input_721'],x[k]) and row['video_frame']==k and row['video_pts_s']==k/50
                assert row['neural_state'] is row['flow'] is None and row['evidence_level']=='STIMULUS_ONLY'
            for bad in (-1,485,True):
                try:source.frame(bad)
                except ValueError:pass
                else:raise AssertionError('INVALID_STEP_ACCEPTED')
        finally:source.input._mmap.close()
        if c['stationary']:assert np.array_equal(x,np.broadcast_to(x[0],x.shape))
        arrays[cid]=x
        results.append(dict(condition_id=cid,stationary=c['stationary'],matched_control=c['matched_control'],
            input_raw_sha256=c['input_raw_sha256'],loaded=True,steps_checked=485,reader_check_steps=[0,199,200,399,400,484],
            preview_fps=50,preview_duration_s=9.7,model_duration_s=2.425,neural_state=None,flow=None))
    paired=0
    for cid,c in conditions.items():
        if c['matched_control']:
            assert c['matched_control'] in arrays and np.array_equal(arrays[cid][:201],arrays[c['matched_control']][:201]);paired+=1
        if c['family'] in ('four_direction_bar','on_off_edge') and not c['stationary']:
            opposite=[r for r in conditions.values() if r['family']==c['family'] and r['polarity']==c['polarity']
                and not r['stationary'] and (r['angle_deg']-c['angle_deg'])%360==180]
            assert len(opposite)==1
    assert len(seen_images)==1847 and paired==14
    assert sha(ROOT/'PACK.json')==PACK_SHA and sha(ROOT/'DELIVERY_MANIFEST.json')==MANIFEST_SHA
    result=dict(status='PASS_READONLY_STIMULUS_FILES_AND_ORIGINAL_READER_ONLY',evidence_level='SOURCE_FILES_ARRAYS_PNG_PIXELS_AND_TIME_IDENTITY',
        package=str(ROOT),PACK_sha256=PACK_SHA,manifest_sha256=MANIFEST_SHA,manifest_files_checked=len(entries),
        conditions=results,condition_count=28,total_input_steps=13580,input_values_compared=28*485*721,
        unique_lossless_frames_checked=len(seen_images),paired_controls_checked=paired,
        official_coordinate_order_matches=True,T4T5_global_ids_match=True,initial_assets=initials,
        all_initial_state_bindings='PENDING_PER_RUN',all_neural_outputs='NOT_RUN',
        source_unchanged=True,elapsed_s=time.perf_counter()-started,
        new_neural_steps=0,decoder_calls=0,GPU_runs=0,camera_runs=0,board_operations=0,
        browser_display='PENDING_SEPARATE_CHECK',REALTIME_STREAM_PASS='NOT_CLAIMED')
    (OUT/'READONLY_VALIDATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(result['status'],len(entries),'files;',len(results),'conditions;',len(seen_images),'lossless frames;',round(result['elapsed_s'],3),'s')


if __name__=='__main__':main()
