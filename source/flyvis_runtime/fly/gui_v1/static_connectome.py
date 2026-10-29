"""Verified official static HDF5 graph copied into a fresh per-session root.

No FlyVis/Torch import, checkpoint object, initial state, or response cache.
The unchanged FullNetworkOracle still verifies all expanded parameters afterward.
"""
import hashlib
import importlib.util
from pathlib import Path,PurePosixPath
import stat
import time
import zipfile
from live_protocol import HERE,host_path,load,require,sha,write

DESCRIPTOR=HERE/'static_connectome_v1/descriptor.json'
DESCRIPTOR_SHA='ad6488544431708015dba6f8c769b6b8cb21df9e451fae0452ddf622f6698d36'
SOURCE_FILES=('init__.py','connectome/connectome.py','connectome/fib25-fib19_v2.2.json',
              'network/network.py','network/network_view.py','network/dynamics.py')


def confirm_static_connectome(oracle,info):
    expected=(Path(info['target'])/'connectomefromavgfilters_0000').resolve()
    actual=Path(oracle.net.connectome.path).resolve()
    require(actual==expected,'STATIC_CONNECTOME_ORIGINAL_LOADER_DID_NOT_REUSE_COPY')
    info.update(original_full_constructor_and_parameter_checks_completed=True,
        official_connectome_path=str(actual),official_loader_used_prepared_directory=True)


def prepare_static_connectome(registry,target,session_id,*,descriptor=DESCRIPTOR,package_root=None):
    started=time.perf_counter();descriptor=Path(descriptor);target=Path(target)
    require(sha(descriptor)==DESCRIPTOR_SHA,'STATIC_CONNECTOME_DESCRIPTOR_CHANGED')
    data=load(descriptor)
    require(data['schema']=='flyvis-static-connectome/v1' and data['model']==registry.data['model'],'STATIC_CONNECTOME_MODEL')
    for name in ('full','identity','parameters','nodes'):
        require(data['reference_pins'][name]==registry.pins[name]['sha256'],'STATIC_CONNECTOME_REFERENCE '+name)
    for pin in data['admission_files']:
        require(sha(host_path(pin['path']))==pin['sha256'],'STATIC_CONNECTOME_ADMISSION_CHANGED')
    if package_root is None:
        spec=importlib.util.find_spec('flyvis');require(spec is not None and spec.origin,'OFFICIAL_FLYVIS_PACKAGE_MISSING')
        package_root=Path(spec.origin).parent
    require(set(data['official_source_sha256'])==set(SOURCE_FILES),'STATIC_CONNECTOME_SOURCE_SCHEMA')
    for name,digest in data['official_source_sha256'].items():
        require(sha(Path(package_root)/name)==digest,'STATIC_CONNECTOME_OFFICIAL_SOURCE '+name)
    payload=descriptor.parent/'connectome.zip'
    require(sha(payload)==data['archive_sha256'],'STATIC_CONNECTOME_ARCHIVE_CHANGED')
    require(not target.exists(),'STATIC_CONNECTOME_TARGET_NOT_FRESH')
    require(0<len(data['files'])<=256 and data['uncompressed_bytes']<=512*1024*1024,'STATIC_CONNECTOME_BOUND')
    with zipfile.ZipFile(payload) as archive:
        members=archive.infolist();names=[m.filename for m in members]
        require(len(names)==len(set(names)) and set(names)==set(data['files']),'STATIC_CONNECTOME_MEMBER_SET')
        require(sum(m.file_size for m in members)==data['uncompressed_bytes'],'STATIC_CONNECTOME_TOTAL_SIZE')
        # Check every name before writing any member. Never use extractall().
        for member in members:
            path=PurePosixPath(member.filename);pin=data['files'][member.filename]
            require(bool(path.parts) and not path.is_absolute() and '..' not in path.parts and '\\' not in member.filename
                    and ':' not in member.filename and path.parts[0]=='connectomefromavgfilters_0000'
                    and not member.is_dir() and not stat.S_ISLNK(member.external_attr>>16),'STATIC_CONNECTOME_MEMBER_SCOPE')
            require(member.file_size==pin['bytes'] and (path.suffix=='.h5' or path.name=='meta.yaml'),'STATIC_CONNECTOME_MEMBER_SCHEMA')
        target.mkdir(parents=True,exist_ok=False)
        for member in members:
            path=target/member.filename;path.parent.mkdir(parents=True,exist_ok=True);digest=hashlib.sha256()
            with archive.open(member) as source,path.open('xb') as output:
                for block in iter(lambda:source.read(1024*1024),b''):output.write(block);digest.update(block)
            require(digest.hexdigest()==data['files'][member.filename]['sha256'],'STATIC_CONNECTOME_MEMBER_SHA')
    return dict(schema='flyvis-static-connectome-use/v1',session_id=session_id,
        mode='VERIFIED_STATIC_GRAPH_COPY',elapsed_s=time.perf_counter()-started,
        descriptor_sha256=DESCRIPTOR_SHA,archive_sha256=data['archive_sha256'],
        source_session_id=data['source_session_id'],files=len(data['files']),
        archive_bytes=payload.stat().st_size,uncompressed_bytes=data['uncompressed_bytes'],
        target=str(target),model_or_checkpoint_object_reused=False,dynamic_state_from_previous_run_used=False,
        neural_activity_reused=False,necessary_full_parameter_validation='STILL_REQUIRED_BY_ORIGINAL_FULLNETWORKORACLE')
