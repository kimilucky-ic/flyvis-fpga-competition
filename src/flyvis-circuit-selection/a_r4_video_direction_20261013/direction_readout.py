"""Preregistered eight-feature local readout. Not DecoderGAVP or optical flow."""
import numpy as np

TYPES = ['T4a','T4b','T4c','T4d','T5a','T5b','T5c','T5d']


def features(activity, type_index):
    if activity.shape != (400, 56) or not np.isfinite(activity).all():
        raise ValueError('400 by 56 finite local readout required')
    # indices refer to Euler output states. Equal semantics in both models.
    base = activity[60:100].astype(np.float64).mean(axis=0)
    delta = activity[100:400].astype(np.float64) - base
    peaks = np.maximum(delta, 0).max(axis=0)
    f = np.array([peaks[type_index == i].mean() for i in range(8)])
    return f


def fit_readout(motion_features, motion_angles, static_features, identity):
    x = np.asarray(motion_features, np.float64)
    mean = x.mean(axis=0)
    scale = np.maximum(x.std(axis=0), 1e-4)
    z = (x-mean)/scale
    theta = np.deg2rad(motion_angles)
    y = np.column_stack([np.cos(theta), np.sin(theta)])
    # Single declared lambda; no cross-validation search or later retuning.
    w = np.linalg.solve(z.T@z + .1*np.eye(8), z.T@y)
    bias = y.mean(axis=0)
    moving_rms = np.sqrt(np.mean(x*x, axis=1))
    static_rms = np.sqrt(np.mean(np.asarray(static_features)**2, axis=1))
    threshold = max(.001, 1.25*float(static_rms.max()), .1*float(moving_rms.min()))
    return dict(schema='local-linear-direction/v1',identity=identity,types=TYPES,
        mean=mean.tolist(),scale=scale.tolist(),weights=w.tolist(),bias=bias.tolist(),
        ridge_lambda=.1,motion_rms_threshold=threshold,vector_norm_threshold=.25,
        fitting='16 motion design clips and 4 static design clips ONLY; neural parameters unchanged',
        semantics='new local clip direction readout, not official optical flow')


def predict(feature, readout):
    f = np.asarray(feature,np.float64)
    if f.shape != (8,) or not np.isfinite(f).all():
        raise ValueError('eight finite features required')
    vec=((f-np.asarray(readout['mean']))/np.asarray(readout['scale']))@np.asarray(readout['weights'])+np.asarray(readout['bias'])
    norm=float(np.linalg.norm(vec)); rms=float(np.sqrt(np.mean(f*f)))
    accepted=bool(rms >= readout['motion_rms_threshold'] and norm >= readout['vector_norm_threshold'])
    raw_angle=None if norm < 1e-12 else float(np.degrees(np.arctan2(vec[1],vec[0]))%360)
    return dict(status='DIRECTION' if accepted else 'NO_CONFIDENT_MOTION',
        angle_deg=raw_angle if accepted else None,raw_angle_deg=raw_angle,
        motion_feature_rms=rms,vector_norm=norm,vector=vec.tolist(),
        note='norm is not calibrated probability; rejection does not prove static')


def circular_error(predicted, truth):
    return abs((predicted-truth+180)%360-180)


def evaluate(prediction, truth):
    motion=truth['kind']=='motion'; accepted=prediction['status']=='DIRECTION'
    result=dict(is_motion=motion,accepted=accepted)
    if motion:
        error=None if not accepted else circular_error(prediction['angle_deg'],truth['angle_deg'])
        true_class=int(np.floor((truth['angle_deg']+45)%360/90))
        pred_class=None if not accepted else int(np.floor((prediction['angle_deg']+45)%360/90))
        result.update(angle_error_deg=error,penalized_error_deg=180. if error is None else error,
            direction_hit_30=bool(error is not None and error<=30),four_way_correct=bool(accepted and pred_class==true_class),
            true_class=true_class,predicted_class=pred_class)
    else:
        result['false_motion']=accepted
    return result
