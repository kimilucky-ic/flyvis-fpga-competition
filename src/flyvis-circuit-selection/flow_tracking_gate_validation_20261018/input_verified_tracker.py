"""Causal stillness veto; location always comes from the frozen FlyVis-flow tracker.

New API explicitly requires synchronized current input[721] as well as flow[2,721].
Supports original 8bit grayscale, 3x3 mean sampling, common5ms time axis.
This is an input-observation aided postprocessor, not a flow-only improvement.
"""
from collections import deque
from pathlib import Path
import importlib.util
import numpy as np

_path=Path(__file__).resolve().parent.parent/'flow_tracking_refinement_20261018/tracker.py'
_spec=importlib.util.spec_from_file_location('frozen_tracking_algorithm',_path)
_base=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_base)

WINDOW_STEPS=20
INPUT_EPSILON=1/(2*255*9)  # half the smallest3x3-mean8bit input quantum; not fitted to labels

class InputVerifiedTracker:
    def init__(self,xy,roi,calibration):
        self.original=_base.Tracker(xy,roi,calibration)
        self.inputs=deque(maxlen=WINDOW_STEPS+1)

    def step(self,flow,samples,step_id,input_step_id):
        # Validate both modalities before mutating either history.
        if type(step_id) is not int or step_id!=self.original.next_step:raise ValueError('STEP_ORDER')
        if type(input_step_id) is not int or input_step_id!=step_id:raise ValueError('INPUT_FLOW_STEP_MISMATCH')
        f=np.asarray(flow,float);x=np.asarray(samples,float)
        if f.shape!=(2,721) or not np.isfinite(f).all():raise ValueError('FLOW_SHAPE_OR_FINITE')
        if x.shape!=(721,) or not np.isfinite(x).all() or np.any((x<0)|(x>1)):raise ValueError('INPUT_SHAPE_FINITE_RANGE')
        row=self.original.step(f,step_id)
        self.inputs.append(x.copy())
        if row is None:return None
        ready=len(self.inputs)==WINDOW_STEPS+1
        amount=float(np.ptp(np.stack(self.inputs),axis=0).max()) if ready else np.nan
        observed_change=ready and amount>INPUT_EPSILON
        result=list(row)
        if not observed_change:
            result[1]=0;result[2:6]=[np.nan]*4
        return result+[amount,int(observed_change),int(ready)]

def run(flow,inputs,xy,roi,calibration):
    if len(flow)!=len(inputs):raise ValueError('LENGTH_MISMATCH')
    tracker=InputVerifiedTracker(xy,roi,calibration);rows=[]
    for k,(f,x) in enumerate(zip(flow,inputs)):
        row=tracker.step(f,x,k,k)
        if row is not None:rows.append(row)
    return np.asarray(rows,float)
