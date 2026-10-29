"""Reuse verified static SWC geometry only; activity always comes from this run.

No Octarine, Torch, camera, socket, or child process imports. Invalid registered
geometry fails closed. A missing registration leaves the existing cold path.
"""
import importlib.util
import os
from pathlib import Path
import time
import uuid
from cached_skeleton import CachedSkeleton
from live_protocol import HERE,load,require,sha

DESCRIPTOR_SHA='e46c23ba84d2bb0406d43ff06a7e4c4017b356bb1f947a556d728b134344e38d'


def load_static_projection(bridge,descriptor=None):
    path=Path(descriptor) if descriptor is not None else HERE/'static_projection.json'
    if not path.exists():return None
    begin=time.perf_counter();require(sha(path)==DESCRIPTOR_SHA,'STATIC_PROJECTION_DESCRIPTOR_CHANGED')
    config=load(path);require(config['schema']=='flyvis-verified-static-projection/v1','STATIC_PROJECTION_SCHEMA')
    for name,digest in config['pins'].items():require(sha(Path(name))==digest,'STATIC_PROJECTION_SOURCE_CHANGED '+Path(name).name)
    admitted=load(config['origin_verification'])
    require(admitted['status']=='PASS_ACTUAL_BOUNDED_GPU_SKELETON_LINK'
        and admitted['source_identity']['session']==config['origin_session']
        and admitted['source_identity']['run']==config['origin_run'],'STATIC_PROJECTION_NOT_ADMITTED')
    base=Path(config['base']);h=load(config['geometry']);model=load(base/'model.json')
    # Retain the original independent full-ID, calibration and time checks.
    spec=importlib.util.spec_from_file_location('flyvis_static_presentation',base/'presentation.py')
    presentation=importlib.util.module_from_spec(spec);spec.loader.exec_module(presentation)
    identity=presentation.verified_identity(base/'model.json')
    e=h['expected_binding'];registry=bridge.adapter.registry.data;spatial=bridge.spatial
    require(identity['mapping_sha256']==e['mapping_sha256'],'STATIC_PROJECTION_MAPPING')
    require(all(e[k]==registry['model'][k] for k in ('model_id','source_commit','checkpoint_sha256','expanded_parameters_sha256')),'STATIC_PROJECTION_MODEL')
    require(e['node_map_sha256']==registry['pins']['nodes']['sha256'] and e['types']==spatial.data['types']
        and e['counts']==[721]*8 and e['aggregation']=='FP64_MEAN_ALL_NODES_PER_TYPE','STATIC_PROJECTION_TYPES')
    require([o['model_node_ids'] for o in model['objects']]==spatial.ids.reshape(8,721).tolist(),'STATIC_PROJECTION_GLOBAL_IDS')
    blob=Path(config['cache']).read_bytes();cached=CachedSkeleton(blob,h)
    h.update(schema='flyvis-static-cpu-projection-health/v1',status='READY_TO_BIND',
        service_id=str(uuid.uuid4()),pid=os.getpid(),adapter=dict(adapter_type='CPU',backend_type='GUI_FIXED_PROJECTION'),
        geometry_rebuilt_per_frame=False,autonomous_playback=False,renderer_computes_neurons=False,PL_execution=False,
        external_renderer_started=False,graphics_backend='VERIFIED_STATIC_GEOMETRY_CURRENT_RUN_CPU_BRIGHTNESS',
        geometry_origin=dict(session_id=config['origin_session'],run_id=config['origin_run'],
            descriptor_sha256=DESCRIPTOR_SHA,execution_kind='VERIFIED_STATIC_GEOMETRY_REUSE',
            neural_activity_reused=False,loader_source_sha256=sha(Path(__file__)),
            pixel_reference_source_sha256=sha(HERE/'cached_skeleton.py')),
        projection_cache=dict(schema='flyvis-fixed-cpu-cache/v1',sha256=cached.sha256,bytes=len(blob),
            url='/api/competition-live/cache',upstream_map_sha256=spatial.digest))
    h['startup_elapsed_s']=time.perf_counter()-begin
    return h,cached
