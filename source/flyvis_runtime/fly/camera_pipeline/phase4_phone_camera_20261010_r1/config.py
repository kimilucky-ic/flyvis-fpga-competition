from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT = {'family':'edge','polarity':'OFF','direction_deg':0.,'speed_px_s':320.,
           'active_s':2.,'pre_s':1.,'post_s':1.,'dot_radius_px':24.,'flicker_hz':1.,
           'gradient_period_px':640.,'dot_control':'automatic'}

def validate_settings(value):
    if not isinstance(value,dict) or set(value)-set(DEFAULT): raise ValueError('Unknown stimulus fields')
    result={**DEFAULT,**value}
    if result['family'] not in ('edge','dot','flicker','fade','gradient','calibration'): raise ValueError('Unknown family')
    if result['polarity'] not in ('ON','OFF') or result['dot_control'] not in ('automatic','touch'): raise ValueError('Unknown polarity/control')
    bounds={'direction_deg':(0,359.999),'speed_px_s':(1,1200),'active_s':(.5,20),'pre_s':(0,5),
            'post_s':(0,5),'dot_radius_px':(4,96),'flicker_hz':(.25,4),'gradient_period_px':(64,1280)}
    for key,(lower,upper) in bounds.items():
        item=result[key]
        if isinstance(item,bool) or not isinstance(item,(float,int)) or not math.isfinite(item) or not lower<=item<=upper:
            raise ValueError(f'Invalid {key}')
        result[key]=float(item)
    if result['pre_s']+result['active_s']+result['post_s']>30: raise ValueError('Trial exceeds bounded30s recorder')
    return result

def settings_sha(settings):
    return hashlib.sha256(json.dumps(validate_settings(settings),sort_keys=True,separators=(',',':')).encode()).hexdigest()

def write_new(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8',newline='\n') as stream:
        json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n')
