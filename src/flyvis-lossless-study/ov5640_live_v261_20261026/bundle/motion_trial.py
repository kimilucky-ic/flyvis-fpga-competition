"""Planned operator cues, not measurements of edge crossings or sensor exposure."""
import math
CONDITIONS=('demo','white_black','black_white','capture')
LABELS={'capture':'60秒采集','demo':'普通60秒演示','white_black':'白背景 / 黑纸条','black_white':'黑背景 / 白纸条'}
SEGMENTS=((0,10,'baseline',0,'背景静止，纸条放在视野外'),(10,15,'move_right',1,'第1次：纸条从左向右匀速移过中央'),(15,25,'recovery',1,'背景静止；纸条从视野外返回起点'),(25,30,'move_right',2,'第2次：纸条从左向右匀速移过中央'),(30,40,'recovery',2,'背景静止；纸条从视野外返回起点'),(40,45,'move_right',3,'第3次：纸条从左向右匀速移过中央'),(45,60,'recovery',3,'背景静止，等待本轮结束'))
def condition(config):
    name=config.get('motion_condition','demo')
    if name not in CONDITIONS:raise ValueError('unknown motion condition')
    return name

def annotation(name,elapsed_ns):
    if name not in CONDITIONS[1:] or type(elapsed_ns) is not int or elapsed_ns<0:raise ValueError('motion timing/condition')
    if name=='capture':
        return dict(schema='line11-capture-receipt/v1',condition=name,label=LABELS[name],elapsed_ns=elapsed_ns,
            phase='capture',trial=None,cue='',
            time_basis='PS_READFRAME_RETURN_RELATIVE_TO_LOOP_START_NOT_EXPOSURE',
            event_basis='UNANNOTATED_NO_ASSUMED_STIMULUS_OR_DIRECTION',model_dt_s=.005,
            sampled_frame_shape=[48,80,3],channel_order='BGR_ASSUMED_NOT_PHYSICALLY_VERIFIED',
            mapping_crop=dict(x=16,y=0,width=48,height=48))
    t=elapsed_ns/1e9
    # Last admitted capture can return after60s; retain its actual timestamp.
    start,end,phase,trial,cue=next((s for s in SEGMENTS if s[0]<=t<s[1]),SEGMENTS[-1])
    return dict(schema='line11-motion-trial/v1',condition=name,label=LABELS[name],elapsed_ns=elapsed_ns,
        phase=phase,trial=trial,cue=cue,phase_start_s=start,phase_end_s=end,
        time_basis='PS_READFRAME_RETURN_RELATIVE_TO_LOOP_START_NOT_EXPOSURE',
        event_basis='PLANNED_OPERATOR_CUE_NOT_OBSERVED_EDGE',direction='CAMERA_IMAGE_LEFT_TO_RIGHT_REQUESTED_UNCALIBRATED',
        model_dt_s=.005,background_control='EXPOSURE_GAIN_AND_LIGHTING_NOT_MEASURED',
        sampled_frame_shape=[48,80,3],channel_order='BGR_ASSUMED_NOT_PHYSICALLY_VERIFIED',
        mapping_crop=dict(x=16,y=0,width=48,height=48))

def validate(meta,config):
    name=condition(config);a=meta.get('experiment')
    if name=='demo':
        if a is not None:raise ValueError('experiment outside selected session')
        return
    if not isinstance(a,dict) or a!=annotation(name,a.get('elapsed_ns')):raise ValueError('experiment receipt mismatch')
    start=meta.get('experiment_start_ns');stamp=meta['prepared']['source_timestamp_ns']
    if type(start) is not int or start<0 or stamp-start!=a['elapsed_ns'] or meta['committed']['source_timestamp_ns']!=stamp:raise ValueError('experiment frame/time binding')
