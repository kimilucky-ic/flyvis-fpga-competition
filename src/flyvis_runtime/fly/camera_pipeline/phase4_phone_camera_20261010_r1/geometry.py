"""Preview geometry only. Actual receptor values use the accepted official adapter."""
from __future__ import annotations
import csv
import hashlib
from pathlib import Path
import numpy as np

COORDINATES = Path(__file__).resolve().parents[1]/'controlled_video_20261010_r1/input/input_hex_coordinates.csv'
COORDINATES_SHA = 'a6b889afb932c6efd081c9e287801e6a2abc3144e767a157ebcd5828a3ded743'

def native_geometry(width, height):
    if hashlib.sha256(COORDINATES.read_bytes()).hexdigest()!=COORDINATES_SHA:
        raise ValueError('Accepted coordinate identity changed')
    with COORDINATES.open(encoding='utf-8') as stream: rows=list(csv.DictReader(stream))
    if len(rows)!=721: raise ValueError('Require 721 official coordinates')
    centers=np.array([[13*int(r['v'])+width//2,
                       int(13*(int(r['u'])+int(r['v'])/2))+height//2] for r in rows],dtype=np.int32)
    if (centers[:,0]-6).min()<0 or (centers[:,1]-6).min()<0 or (centers[:,0]+6).max()>=width or (centers[:,1]+6).max()>=height:
        raise ValueError('Formal screen capture requires all 13x13 footprints inside the raw image; no implicit padding/resize')
    mask=np.zeros((height,width),dtype=bool)
    for x,y in centers: mask[y-6:y+7,x-6:x+7]=True
    ys,xs=np.nonzero(mask)
    metadata={'schema':'native-boxeye-overlay-v1','raw_resolution_wh':[width,height],
              'coordinate_source':str(COORDINATES),'coordinate_source_sha256':COORDINATES_SHA,
              'boxeye_extent':15,'boxeye_kernel_size':13,'boxeye_filter':'mean',
              'center_formula':'x=13*v+W//2; y=int(13*(u+v/2))+H//2; cast toward zero',
              'footprint_bounds_xy_inclusive':[int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())],
              'footprint_union_pixels':int(mask.sum()),'mirror':False,'rotation_degrees':0,
              'crop':None,'resize':None,'padding_added':False,'physical_fov_degrees':None,
              'overlay_only':True,'receptor_values_computed_here':False}
    return centers,mask,metadata

def screen_coverage(mask, polygon):
    points=np.asarray(polygon,dtype=float)
    if points.shape!=(4,2) or not np.isfinite(points).all(): raise ValueError('Four finite raw-frame screen corners required')
    h,w=mask.shape
    if (points[:,0]<0).any() or (points[:,0]>=w).any() or (points[:,1]<0).any() or (points[:,1]>=h).any():
        raise ValueError('Screen corners outside actual raw frame')
    edges=np.roll(points,-1,axis=0)-points
    turns=edges[:,0]*np.roll(edges,-1,axis=0)[:,1]-edges[:,1]*np.roll(edges,-1,axis=0)[:,0]
    if not ((turns>0).all() or (turns<0).all()): raise ValueError('Screen polygon must be convex, corners ordered around its perimeter')
    ys,xs=np.nonzero(mask);pixels=np.column_stack([xs,ys])
    cross=edges[:,0,None]*(pixels[None,:,1]-points[:,1,None])-edges[:,1,None]*(pixels[None,:,0]-points[:,0,None])
    inside=(cross>=-1e-8).all(axis=0)|(cross<=1e-8).all(axis=0)
    return {'all_footprints_inside_active_screen':bool(inside.all()),'outside_footprint_pixels':int((~inside).sum()),
            'screen_corners_raw_xy':points.tolist(),'geometry_transform_applied':False,
            'screen_polygon_is_operator_annotation':True,'actual_screen_boundary_independently_verified':False}

def overlay(bgr, cv2, centers, mask, polygon=None):
    view=bgr.copy()
    tint=np.array([0,130,0],dtype=float)
    view[mask]=(view[mask].astype(float)*.78+tint*.22).astype(np.uint8)
    for x,y in centers: cv2.circle(view,(int(x),int(y)),1,(0,255,0),-1)
    if polygon is not None and len(polygon)>=2:
        cv2.polylines(view,[np.asarray(polygon,dtype=np.int32)],len(polygon)==4,(0,200,255),2)
    cv2.putText(view,'721 native centers + 13x13 footprints | raw: x right, y down',(8,20),cv2.FONT_HERSHEY_SIMPLEX,.43,(0,255,255),1)
    return view

def roi_statistics(bgr,mask):
    # Diagnostics only; official stimulus luminance remains Pillow RGB.convert(L).
    from PIL import Image
    values=np.asarray(Image.fromarray(bgr[:,:,::-1]).convert('L'))[mask]
    return {'roi_gray_mean_0_255':float(values.mean()),'roi_gray_std_0_255':float(values.std()),
            'roi_fraction_le_2':float((values<=2).mean()),'roi_fraction_ge_253':float((values>=253).mean()),
            'black_white_clipping_is_not_automatic_exposure_failure':True}
