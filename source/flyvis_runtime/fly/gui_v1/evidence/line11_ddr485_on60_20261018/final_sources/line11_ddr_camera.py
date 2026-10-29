"""Explicit bounded camera recording -> official BoxEye/ZOH -> existing DDR plan.

Only a user launch with --capture opens CameraSession. No GPU/PL operation.
--recording consumes a specified saved recording for SOFTWARE testing/replay.
"""
import argparse,csv,hashlib,json,os,sys,time
from pathlib import Path

HERE=Path(__file__).resolve().parent
FLY=HERE.parent;STUDY=FLY.parent/'fpga/flyvis-lossless-study'

def digest(raw):return hashlib.sha256(raw).hexdigest()

def prepare(output,*,recording=None,device=0,capture=False):
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    for k,v in dict(CUDA_VISIBLE_DEVICES='-1',PYTHON_DOTENV_DISABLED='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',NUMBA_NUM_THREADS='1',MPLBACKEND='Agg').items():os.environ[k]=v
    sys.path.insert(0,str(FLY))
    from camera_pipeline import open_camera,record_clip,video_to_flyvis_stimulus,save_stimulus
    from camera_pipeline.adapter import load_stimulus,load_video_source
    if capture:
        if recording is not None:raise ValueError('Choose new capture OR explicit saved recording')
        recording=output/'recording'
        with open_camera(device,backend='dshow',width=640,height=480,fps=30) as camera:
            record_clip(camera,recording,2.5,preview=False)
    if recording is None:raise ValueError('EXPLICIT_CAMERA_INPUT_REQUIRED_NO_FALLBACK')
    recording=Path(recording).resolve()
    frames,times,source=load_video_source(recording)
    if source['source_kind']!='real_windows_camera' or source['timestamp_source']!='measured_host_frame_receipt':raise ValueError('REAL_CAMERA_RECORDING_REQUIRED')
    if digest((recording/'frame_timestamps.csv').read_bytes())!=source['data_sha256']['frame_timestamps.csv']:
        raise ValueError('CAMERA_CAPTURE_TIMESTAMPS_CHANGED')
    converted=video_to_flyvis_stimulus(recording,spatial_policy='native',method='zoh',dt_s=.005)
    bundle=save_stimulus(converted,output/'official_input')
    stimulus,grid,coordinates,metadata=load_stimulus(bundle)
    if stimulus.shape[1]<485:raise ValueError('CAMERA_NEEDS_AT_LEAST_2_42_SECONDS_OF_VALID_CAPTURE')
    import numpy as np
    import torch
    if torch.cuda.is_initialized():raise ValueError('CAMERA_PREPARATION_MUST_BE_CPU')
    torch.set_default_device('cpu');torch.set_flush_denormal(False)
    if metadata['spatial_transform']['official_eye_source_sha256']!='3df1858641031844596c8fb769527cc9c786c1332c0e9b9e81bdee1b6b3a7702':
        raise ValueError('OFFICIAL_BOXEYE_SOURCE_CHANGED')
    sys.path.insert(0,str(STUDY))
    for name,pin in dict(engine='74f88a84563bac1e20b851b7d505db0fab107527f7d57fb44aa8de68d256a29f',codec='e675b4eb7f594467518c9faf725b7706e45237d2b6a9afe0e94a5de6640fef64').items():
        if digest((STUDY/(name+'.py')).read_bytes())!=pin:raise ValueError('FROZEN_CPU_REFERENCE_SOURCE_CHANGED')
    from codec import read_template
    from engine import Engine
    template=STUDY/'runs/acceptance800_20261013/flyvis_template.bin'
    if digest(template.read_bytes())!='1d52e7dea2d244f69398cff81e14c120626f3f9a61694b84ad0259839acfd574':raise ValueError('CPU_REFERENCE_TEMPLATE_CHANGED')
    engine=Engine(read_template(template));initial=digest(engine.activity.tobytes())
    if initial!='d276601573420bf787a81ffa8c81f2da3499a20df2bb858f6082c2e449ff564f':raise ValueError('DDR_CAMERA_INITIAL_STATE')
    x=np.ascontiguousarray(stimulus[0,:485,0],dtype='<f4');a=np.empty((485,45669),dtype='<f4')
    for k,frame in enumerate(x):a[k]=engine.advance(frame)
    plan=output/'plan';plan.mkdir();x.tofile(plan/'plan_inputs.bin');a.tofile(plan/'plan_expected_states.bin')
    selected=[];png_pins={}
    from camera_pipeline.common import cv2_module
    cv2=cv2_module()
    for row in converted.alignment[:485]:
        j=row['source_left_frame'];p=recording/'raw_frames'/('frame_%06d.png'%j)
        if j not in png_pins:
            raw=p.read_bytes();image=cv2.imdecode(np.frombuffer(raw,dtype=np.uint8),cv2.IMREAD_COLOR)
            if not np.array_equal(image,frames[j]):raise ValueError('CAMERA_PREVIEW_DIFFERS_FROM_BOXEYE_SOURCE')
            png_pins[j]=digest(raw)
        selected.append(dict(source_frame=j,capture_relative_s=float(times[j]-times[0]),
            pixel_png_sha256=png_pins[j]))
    with (recording/'frame_timestamps.csv').open(encoding='utf-8') as f:timestamps=list(csv.DictReader(f))
    for row in selected:
        t=timestamps[row['source_frame']];row['capture_received_monotonic_ns']=int(t['received_monotonic_ns']);row['capture_utc']=t['received_utc']
    m=dict(schema='flyvis-line2-ddr-fixed-plan/v1',plan_id='CAMERA_485_'+output.name,
        input_kind='recorded_camera_flyvis',condition_id='真实摄像头短录制',steps=485,dt_s=.005,nodes=45669,edges=1513231,
        input_time_offset_s=0.,model_duration_s=2.425,source_kind='real_windows_camera',
        execution_kind='NEW_RECORDING_FROZEN_INPUT' if capture else 'EXPLICIT_SAVED_CAMERA_RECORDING_SOFTWARE_REPLAY',
        recording_directory=str(recording),recording_sha256=digest((recording/'recording.json').read_bytes()),source_frames=selected,
        initial_state=dict(kind='ORIGINAL_PER_TYPE_BIAS',sha256=initial),
        reference=dict(evidence='CPU_ONLY_EXISTING_STRICT_ENGINE',checkpoint_sha256='d0e42857e738d0315897c2d50fde9eb3fb1a3fb1f071d55dfc13d53d72bccc3f',
            independent_485_ON60_comparison=str(HERE/'evidence/line11_ddr485_on60_20261018/CPU_REFERENCE_RESULT.json')),
        temporal_policy='CAUSAL_ZOH_5MS; first485 native input grid samples; NO_NEURAL_TIME_STEP_CHANGE',
        official_input_directory=str(bundle),official_input_metadata_sha256=digest((bundle/'metadata.json').read_bytes()),
        files={n:dict(bytes=(plan/n).stat().st_size,sha256=digest((plan/n).read_bytes())) for n in ('plan_inputs.bin','plan_expected_states.bin')},
        board_result=False,GPU_execution=False)
    (plan/'RUN_PLAN.json').write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    result=dict(plan_directory=str(plan),plan_manifest_sha256=digest((plan/'RUN_PLAN.json').read_bytes()),
        status='CPU_PREPARED_CAMERA_INPUT_ONLY',new_capture=capture,GPU_execution=False,board_execution=False)
    (output/'PREPARED.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path);p.add_argument('--capture',action='store_true')
    p.add_argument('--recording',type=Path);p.add_argument('--device',type=int,default=0);args=p.parse_args()
    print(json.dumps(prepare(args.output,recording=args.recording,device=args.device,capture=args.capture)),flush=True)
