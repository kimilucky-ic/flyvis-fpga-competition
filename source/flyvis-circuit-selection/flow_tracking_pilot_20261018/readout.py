"""Causal, flow-only locator/tracker. No images, labels, or model states in API."""
import numpy as np


def saliency(flow):
    f=np.asarray(flow,dtype=np.float64)
    if f.ndim!=3 or f.shape[1:]!=(2,721) or not np.isfinite(f).all():
        raise ValueError('FLOW_SHAPE_OR_FINITE')
    out=np.zeros((len(f),721)); smooth=np.zeros(721)
    alpha=.005/(.050+.005)
    for k in range(len(f)):
        change=np.linalg.norm(f[k]-f[max(0,k-20)],axis=0) if k>=20 else np.zeros(721)
        smooth=(1-alpha)*smooth+alpha*change
        out[k]=smooth
    return out


def components(mask,neighbors):
    remaining=set(np.flatnonzero(mask).tolist()); result=[]
    while remaining:
        seed=min(remaining);remaining.remove(seed);stack=[seed];group=[]
        while stack:
            i=stack.pop();group.append(i)
            for j in neighbors[i]:
                if int(j) in remaining:
                    remaining.remove(int(j));stack.append(int(j))
        if len(group)>=3:result.append(np.array(sorted(group),dtype=np.int64))
    return result


def track(flow,xy,neighbors,roi,threshold):
    """Every50ms: components of temporal flow saliency; causal gated centroid.

    threshold is fixed using the two separate stationary calibration scenes.
    Predicted states during gaps are NOT reported as successful detections.
    """
    scores=saliency(flow); p=v=None; gaps=0; rows=[]
    for k in range(9,len(flow),10):
        s=scores[k]; cut=max(float(threshold),.5*float(s[roi].max()))
        mask=np.zeros(721,bool);mask[roi]=s[roi]>=cut
        groups=components(mask,neighbors); candidates=[]
        for g in groups:
            mass=s[g].sum()
            if mass>0:candidates.append((float(mass),(s[g,None]*xy[g]).sum(0)/mass,len(g)))
        prediction=None if p is None else p+v*.05
        if prediction is not None:
            candidates=[c for c in candidates if np.linalg.norm(c[1]-prediction)<=4]
        if candidates:
            chosen=max(candidates,key=lambda c:c[0]); measurement=chosen[1]
            if p is None:p=measurement.copy();v=np.zeros(2)
            else:
                old=p.copy();p=.8*measurement+.2*prediction
                v=.8*v+.2*(measurement-old)/.05
            gaps=0
            rows.append([k,1,*p,*measurement,chosen[0],chosen[2]])
        else:
            rows.append([k,0,np.nan,np.nan,np.nan,np.nan,0,0])
            gaps+=1
            if p is not None:p=prediction
            if gaps>=4:p=v=None
    return np.asarray(rows,float),scores


def tests(xy,neighbors,roi):
    assert not components(np.zeros(721,bool),neighbors)
    ids=[roi[len(roi)//2]]
    ids.extend([int(j) for j in neighbors[ids[0]][:2]])
    mask=np.zeros(721,bool);mask[ids]=True
    assert len(components(mask,neighbors))==1
    zero=np.zeros((100,2,721),np.float32)
    result,_=track(zero,xy,neighbors,roi,1e-5)
    assert (result[:,1]==0).all()
    for bad in [np.full((100,2,721),np.nan),np.zeros((100,2,720))]:
        try:saliency(bad)
        except ValueError:continue
        raise AssertionError('INVALID_FLOW_NOT_REJECTED')
    return dict(empty_components=True,connected_triplet=True,zero_flow_abstains=True,
                NaN_rejected=True,wrong_order_shape_rejected=True)
