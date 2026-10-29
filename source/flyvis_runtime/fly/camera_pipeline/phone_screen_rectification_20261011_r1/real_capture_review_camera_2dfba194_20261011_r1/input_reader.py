"""Read frozen scheme-B input on Windows or its existing WSL /mnt drive mount.

Only translates stored filesystem paths. Never changes arrays, timing, manifests,
or source pixels; imports neither OpenCV nor the neural model.
"""
from pathlib import Path, PureWindowsPath
import csv
import hashlib
import json
import re
import sys
import numpy as np


def saved_path(value):
    text = str(value)
    if sys.platform.startswith('linux') and re.match(r'^[A-Za-z]:[\\/]',text):
        win = PureWindowsPath(text)
        return Path('/mnt')/win.drive[0].lower()/Path(*win.parts[1:])
    return Path(text)


def digest(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as handle:
        for chunk in iter(lambda:handle.read(1024*1024),b''):
            value.update(chunk)
    return value.hexdigest()


def read_doc(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def load_frozen_input(folder):
    folder = saved_path(folder).resolve()
    verified = {}
    def require_digest(path, expected):
        path = Path(path).resolve()
        actual = verified.get(path)
        if actual is None:
            actual = verified[path] = digest(path)
        if actual != expected:
            raise ValueError('Changed frozen evidence: '+str(path))

    def verify_manifest(directory):
        directory = Path(directory).resolve()
        manifest = read_doc(directory/'manifest.json')
        if manifest['schema'] != 'screen-B-seal-v1':
            raise ValueError('Unsupported frozen manifest schema')
        for name, expected in manifest['files'].items():
            relative = PureWindowsPath(name)
            if relative.drive or relative.is_absolute():
                raise ValueError('Internal manifest requires relative paths')
            # Windows seals may store backslashes in nested relative filenames.
            path = (directory/Path(*relative.parts)).resolve()
            if not path.is_relative_to(directory):
                raise ValueError('Manifest path escapes directory')
            require_digest(path,expected)
        for name,expected in manifest['external_files'].items():
            require_digest(saved_path(name),expected)

    verify_manifest(folder)
    identity = read_doc(folder/'INPUT_IDENTITY.json')
    if identity['schema']!='flyvis-screen-rectified-input-v1' or identity['scheme']!='B_fixed_screen_homography_640':
        raise ValueError('Only explicit fixed-screen B inputs supported')
    source_dir = saved_path(identity['source_bundle_path']).resolve()
    require_digest(source_dir/'manifest.json',identity['source_manifest_sha256'])
    verify_manifest(source_dir)
    source = read_doc(source_dir/'source.json')
    require_digest(saved_path(source['frames_path']),source['frames_sha256'])
    require_digest(saved_path(identity['rectified_frames_path']),identity['rectified_frames_sha256'])
    x=np.load(folder/'stimulus.npy',allow_pickle=False)
    t=np.load(folder/'time.npy',allow_pickle=False)
    a=np.load(folder/'activity_time.npy',allow_pickle=False)
    s=np.load(folder/'source_time.npy',allow_pickle=False)
    receptors=np.load(folder/'source_hex.npy',allow_pickle=False)
    if not (x.dtype==np.float32 and x.shape==(1,len(t),1,721) and list(x.shape)==identity['shape']
            and np.isfinite(x).all() and x.min()>=0 and x.max()<=1 and identity['dt_s']==.005
            and identity['temporal_method']=='causal_zoh' and np.array_equal(a,t+.005)):
        raise ValueError('Input shape/range/time semantics mismatch')
    if not (np.isfinite(s).all() and s[0]==0 and (np.diff(s)>0).all()
            and np.array_equal(t,np.arange(int(np.floor(s[-1]/.005))+1,dtype=np.float64)*.005)):
        raise ValueError('Measured source and unpadded 5ms grid mismatch')
    indices=np.searchsorted(s,t,side='right')-1
    if not ((indices>=0).all() and (s[indices]<=t).all() and receptors.shape==(len(s),721)
            and np.array_equal(x[0,:,0],receptors[indices])):
        raise ValueError('Causal input values mismatch')
    with (folder/'input_hex_coordinates.csv').open(encoding='utf-8') as handle:
        if len(list(csv.DictReader(handle)))!=721:
            raise ValueError('Coordinate count mismatch')
    for array in (x,t,a):array.flags.writeable=False
    return identity,x,t,a


if __name__=='__main__':
    folder=sys.argv[1] if len(sys.argv)>1 else Path(__file__).resolve().parent/'frozen_selected_100_190'/'input'
    identity,x,t,a=load_frozen_input(folder)
    print(json.dumps({'status':'PASS','platform':sys.platform,'comparison_id':identity['comparison_id'],
        'shape':list(x.shape),'stimulus_sha256':digest(saved_path(folder)/'stimulus.npy'),
        'input_time_sha256':digest(saved_path(folder)/'time.npy'),
        'activity_time_sha256':digest(saved_path(folder)/'activity_time.npy'),
        'input_read_only':not x.flags.writeable,'source_paths_mapped_only':True,
        'camera_opened':False,'neural_inference':False,'board_used':False},indent=2))
