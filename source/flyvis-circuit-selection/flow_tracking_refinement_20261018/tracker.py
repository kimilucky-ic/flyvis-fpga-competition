"""Small causal postprocessor: separate motion confidence and spatial location.

No input images, ground truth, neuron update, or decoder in this module.
Calibration is frozen old known-white-background flow, not target future states.
"""
from collections import deque
import numpy as np


class Tracker:
    def init__(self,xy,roi,calibration):
        self.xy=np.asarray(xy,float);self.roi=np.asarray(roi,int)
        self.prefix=np.asarray(calibration['background_prefix'],float)
        self.steady=np.asarray(calibration['background_steady'],float)
        self.motion_threshold=float(calibration['motion_threshold'])
        self.location_floor=float(calibration['location_floor'])
        self.history=deque(maxlen=20);self.smooth=np.zeros(721)
        self.p=self.v=None;self.gaps=0;self.next_step=0;self.reacquisitions=0

    def step(self,flow,step_id):
        if type(step_id) is not int or step_id!=self.next_step:raise ValueError('STEP_ORDER')
        f=np.asarray(flow,float)
        if f.shape!=(2,721) or not np.isfinite(f).all():raise ValueError('FLOW_SHAPE_OR_FINITE')
        change=np.linalg.norm(f-self.history[0],axis=0) if len(self.history)==20 else np.zeros(721)
        alpha=.005/(.050+.005)
        self.smooth=(1-alpha)*self.smooth+alpha*change
        self.history.append(f.copy());self.next_step+=1
        if step_id%10!=9:return None
        background=self.prefix[step_id] if step_id<len(self.prefix) else self.steady
        magnitude=np.linalg.norm(f-background,axis=0)
        peak=float(magnitude[self.roi].max());motion=float(self.smooth[self.roi].max())
        selected=self.roi[magnitude[self.roi]>=max(self.location_floor,.5*peak)]
        valid=motion>=self.motion_threshold and peak>=self.location_floor and len(selected)>=3
        prediction=None if self.p is None else self.p+self.v*.05
        if valid:
            weight=magnitude[selected];mass=float(weight.sum())
            measurement=(weight[:,None]*self.xy[selected]).sum(0)/mass
            # Never reject a fresh spatial observation because an old track is wrong.
            if self.p is None or np.linalg.norm(measurement-prediction)>4:
                if self.p is not None:self.reacquisitions+=1
                self.p=measurement.copy();self.v=np.zeros(2)
            else:
                old=self.p.copy();self.p=.8*measurement+.2*prediction
                self.v=.8*self.v+.2*(measurement-old)/.05
            self.gaps=0
            return [step_id,1,*self.p,*measurement,mass,len(selected),motion,peak]
        self.gaps+=1
        if self.p is not None:self.p=prediction
        if self.gaps>=4:self.p=self.v=None
        return [step_id,0,np.nan,np.nan,np.nan,np.nan,0,0,motion,peak]


def run(flow,xy,roi,calibration):
    tracker=Tracker(xy,roi,calibration);rows=[]
    for k,frame in enumerate(flow):
        row=tracker.step(frame,k)
        if row is not None:rows.append(row)
    return np.asarray(rows,float),dict(reacquisitions=tracker.reacquisitions)


def tests(flow,xy,roi,calibration):
    allrows,_=run(flow,xy,roi,calibration)
    prefix,_=run(flow[:500],xy,roi,calibration)
    assert np.allclose(allrows[:50],prefix,atol=0,rtol=0,equal_nan=True)
    t=Tracker(xy,roi,calibration)
    for frame,k in [(np.zeros((2,721)),1),(np.zeros((2,720)),0),(np.full((2,721),np.nan),0)]:
        try:t.step(frame,k)
        except ValueError:continue
        raise AssertionError('NEGATIVE_NOT_REJECTED')
    assert t.next_step==0
    return dict(causal_prefix_exact=True,wrong_step_rejected=True,wrong_shape_rejected=True,
                NaN_rejected=True,failed_input_does_not_advance=True)
