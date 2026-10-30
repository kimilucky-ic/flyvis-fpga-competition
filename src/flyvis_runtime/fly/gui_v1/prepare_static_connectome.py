"""One-time CPU-only admission of an accepted run's official static graph."""
import argparse
import csv
import hashlib
from pathlib import Path
import zipfile
import h5py
import numpy as np
from live_protocol import HERE,Registry,host_path,load,require,sha,write
from static_connectome import SOURCE_FILES


def build(source,session_id,out,verification):
    registry=Registry();source=Path(source);out=Path(out);verification=Path(verification)
    require(session_id=='49bdc35ce81e4c2682a134c7c2aaa52a','STATIC_SEED_EXPLICIT_ACCEPTED_SESSION')
    root=HERE/'runtime/live'/session_id;result=load(root/'stream/result.json');checked=load(verification)
    require(checked['status']=='PASS_ACTUAL_BOUNDED_GPU_SKELETON_LINK'
            and checked['source_identity']['session']==session_id and result['success'] is True
            and result['model']==registry.data['model'] and result['original_weights_unchanged'] is True
            and result['decoder_unchanged'] is True,'STATIC_SEED_ACCEPTANCE')
    release=load(root/'worker_shutdown.json');require(release['CUDA_synchronized'] is True and release['shared_lock_closed'] is True,'STATIC_SEED_OWNER_NOT_RELEASED')
    graph=source/'connectomefromavgfilters_0000'
    def array(name):
        # Accepted donor is closed. UNC cannot implement an HDF5 shared lock;
        # this handle is read-only, with full source digests checked around copying.
        with h5py.File(graph/name,'r',locking=False) as handle:return handle['data'][:]
    with registry.path_for('nodes').open(encoding='utf-8-sig',newline='') as f:nodes=list(csv.DictReader(f))
    ids=np.array([int(n['global_node_index']) for n in nodes],dtype=np.int64)
    types=np.array([n['cell_type'].encode() for n in nodes],dtype='S8')
    require(np.array_equal(ids,np.arange(45669)) and np.array_equal(array('nodes/index.h5'),ids),'STATIC_SEED_NODE_IDS')
    require(np.array_equal(array('nodes/type.h5'),types),'STATIC_SEED_NODE_TYPES')
    for axis in ('u','v'):require(np.array_equal(array('nodes/'+axis+'.h5'),np.array([int(n[axis]) for n in nodes],dtype=np.int32)),'STATIC_SEED_HEX_COORDINATES')
    with np.load(registry.path_for('parameters'),allow_pickle=False) as params:
        for name,key in [('source_index','source_global'),('target_index','target_global')]:
            actual=array('edges/'+name+'.h5');require(actual.shape==(1513231,) and np.array_equal(actual,params[key]),'STATIC_SEED_ALL_EDGES '+name)
    for cell in dict.fromkeys(types):
        require(np.array_equal(array('nodes/layer_index/'+cell.decode()+'.h5'),np.flatnonzero(types==cell)),'STATIC_SEED_ALL_SPATIAL_LAYERS')
    paths=sorted(p for p in source.rglob('*') if p.is_file())
    require(0<len(paths)<=256,'STATIC_SEED_FILE_COUNT');files={}
    for path in paths:
        name=path.relative_to(source).as_posix()
        require(not path.is_symlink() and (path.suffix=='.h5' or path.name=='meta.yaml'),'STATIC_SEED_STATIC_FILES_ONLY')
        files[name]=dict(bytes=path.stat().st_size,sha256=sha(path))
    out.mkdir(parents=True,exist_ok=False);archive=out/'connectome.zip'
    with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=3) as bundle:
        for path in paths:bundle.write(path,path.relative_to(source).as_posix())
    for path in paths:require(sha(path)==files[path.relative_to(source).as_posix()]['sha256'],'STATIC_SEED_CHANGED_DURING_COPY')
    package=HERE.parent/'upstream/flyvis/flyvis'
    admission=[root/'session.json',root/'stream/result.json',root/'worker_shutdown.json',verification]
    descriptor=dict(schema='flyvis-static-connectome/v1',model=registry.data['model'],source_session_id=session_id,
        source_directory=str(source),reference_pins={n:registry.pins[n]['sha256'] for n in ('full','identity','parameters','nodes')},
        admission_files=[dict(path=str(p),sha256=sha(p)) for p in admission],
        official_source_sha256={n:sha(package/n) for n in SOURCE_FILES},archive_sha256=sha(archive),
        files=files,uncompressed_bytes=sum(p['bytes'] for p in files.values()),
        independent_checks=dict(all_node_ids=45669,all_edge_pairs=1513231,all_type_spatial_layers=65,
            trained_checkpoint_or_model_object_cached=False,neural_state_or_activity_cached=False))
    write(out/'descriptor.json',descriptor)
    return dict(descriptor_sha256=sha(out/'descriptor.json'),archive_bytes=archive.stat().st_size,
        uncompressed_bytes=descriptor['uncompressed_bytes'],files=len(files),checks=descriptor['independent_checks'])


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--session',required=True)
    p.add_argument('--out',required=True);p.add_argument('--verification',required=True);args=p.parse_args()
    result=build(args.source,args.session,args.out,args.verification);print(result)
