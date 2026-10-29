"""Read-only frozen CNN/runner bindings and new MP4 case definitions."""
from pathlib import Path
import sys, time, json, hashlib, csv, shutil, ast, importlib.util

HERE = Path(__file__).resolve().parent
PREVIOUS = HERE.parent/'cnn_t4t5_frozen_generalization_20261016'
spec = importlib.util.spec_from_file_location('accepted_frozen_generalization', PREVIOUS/'core.py')
previous = importlib.util.module_from_spec(spec); spec.loader.exec_module(previous)
ref = previous.ref; base = ref.base
np, torch = previous.np, previous.torch
dump, load, sha, digest = previous.dump, previous.load, previous.sha, previous.digest
memory, vector_metrics = previous.memory, previous.vector_metrics
OriginalTargets, ClosedLoop, CNNService = ref.OriginalTargets, ref.ClosedLoop, ref.CNNService
MODEL, MODEL_SHA = previous.MODEL, previous.MODEL_SHA
LANE, BUNDLE, TYPES, ROI_PATH, DT = previous.LANE, previous.BUNDLE, previous.TYPES, previous.ROI_PATH, previous.DT


def check(deep=False):
    registration = load(HERE/'PREREGISTRATION.json')
    assert sha(HERE/'PREREGISTRATION.json') == load(HERE/'FREEZE.json')['sha256']
    assert sha(MODEL) == MODEL_SHA
    for name, record in registration['pins'].items():
        p = Path(name)
        assert p.stat().st_size == record['bytes'] and p.stat().st_mtime_ns == record['mtime_ns'], name
        if deep: assert sha(p) == record['sha256'], name
    return registration


def cases():
    result = []
    for polarity, angle, speed in [('ON',75,12),('OFF',75,6),('ON',255,18),('OFF',255,12)]:
        result.append(dict(id=f'{polarity}{angle}_v{speed}_full', group='motion', kind='motion',
                           polarity=polarity, angle=angle, speed=speed, center=[0,0], local=False, background='gray'))
    for polarity, angle, center in [('ON',75,[0,4]),('OFF',255,[0,-4])]:
        result.append(dict(id=f'{polarity}{angle}_local_static_texture', group='motion', kind='motion',
                           polarity=polarity, angle=angle, speed=12, center=center, local=True, background='static_texture'))
    for polarity, angle, center, bgangle in [('ON',165,[-4,0],345),('OFF',345,[4,0],165)]:
        result.append(dict(id=f'{polarity}{angle}_local_moving_background', group='motion', kind='motion',
                           polarity=polarity, angle=angle, speed=12, center=center, local=True,
                           background='moving_texture', background_angle=bgangle, background_speed=3))
    result += [dict(id='GRAY5s', group='static', kind='gray'),
               dict(id='STATIC_TEXTURE5s', group='static', kind='texture')]
    for c in result:
        c.update(steps=1000, duration_s=5, video_fps=100, texture_seed=2026101621)
        if c['group']=='motion':
            c['windows']=dict(allpost=[200,1000], active=[320,720], stopped=[840,1000])
        else: c['windows']=dict(adapted=[400,1000], late=[800,1000])
    return result


def foreground_roi(case, mapping, common):
    uv=mapping['grid_uv']; x=np.sqrt(3)/2*uv[1]; y=-(uv[0]+uv[1]/2)
    cx,cy=case['center']; ids=np.flatnonzero((x-cx)**2+(y-cy)**2<=3**2)
    assert len(ids)>=10 and np.isin(ids,common).all()
    return ids


def score_motion(case, h_ref, h_value, f_ref, f_value, common, mapping):
    baseline=h_ref[160:200].astype(np.float64).mean(0); scores={}
    for name,(start,stop) in case['windows'].items():
        d=h_value[start:stop].astype(np.float64)-h_ref[start:stop]
        energy=float(np.sum((h_ref[start:stop].astype(np.float64)-baseline)**2))
        response=float(np.sqrt(energy/d.size)); relative=float(np.sqrt(np.sum(d*d)/energy)) if energy>0 else None
        flow=vector_metrics(f_ref,f_value,common,slice(start,stop))
        value=dict(H_response_relative_L2=relative,H_reference_response_rms=response,flow=flow,
                   pass_gate=bool(response>=1e-6 and relative is not None and relative<=.2 and flow['pass_gate']))
        if case.get('local') and name=='active':
            local=foreground_roi(case,mapping,common)
            value['foreground_flow']=vector_metrics(f_ref,f_value,local,slice(start,stop))
            value['foreground_hex_ids']=local.tolist()
            value['pass_gate']=bool(value['pass_gate'] and value['foreground_flow']['pass_gate'])
        scores[name]=value
    return scores


def execute_accepted_function(path,name,namespace):
    """Use the exact frozen function body with an explicit output/path adapter."""
    tree=ast.parse(path.read_text(encoding='utf-8'))
    definitions=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name]
    assert len(definitions)==1
    exec(compile(ast.Module(body=definitions,type_ignores=[]),str(path),'exec'),namespace)


def execute_accepted_audit(namespace):
    tree=ast.parse((PREVIOUS/'audit.py').read_text(encoding='utf-8'))
    body=[n for n in tree.body if not (isinstance(n,ast.ImportFrom) and n.module=='core')]
    exec(compile(ast.Module(body=body,type_ignores=[]),str(PREVIOUS/'audit.py'),'exec'),namespace)
