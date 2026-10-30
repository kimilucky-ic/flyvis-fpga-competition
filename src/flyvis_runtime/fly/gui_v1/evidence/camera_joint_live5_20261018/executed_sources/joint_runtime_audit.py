"""Loaded-session static identity checks; no neural/device calls.

Hash loaded static sources at admission/finalization. Only the three current
session identity files need metadata checks in each background cycle.
"""
from live_protocol import HERE,host_path,sha,require,load
from joint_diagnostics import NONE

class RuntimeFiles:
    def init__(self,*,diagnostics=NONE):
        self.files={};self.diagnostics=diagnostics;self.metadata_passes=0;self.full_hash_passes=0

    @staticmethod
    def stamp(s):
        return (s.st_size,s.st_mtime_ns,s.st_ctime_ns,s.st_ino,s.st_dev)

    def add(self,path,digest,*,prior_stamp=None,already_verified=False,watch=True):
        p=host_path(path).resolve()
        if p in self.files:
            require(self.files[p]['sha256']==digest,'AUDIT_CONFLICTING_FILE_IDENTITY '+str(p))
            self.files[p]['watch'] |= watch
            if prior_stamp is not None:require(self.files[p]['stamp'][:2]==tuple(prior_stamp),'AUDIT_CHANGED_SINCE_LOAD '+str(p))
            return
        s=p.stat()
        if prior_stamp is not None:require((s.st_size,s.st_mtime_ns)==tuple(prior_stamp),'AUDIT_CHANGED_SINCE_LOAD '+str(p))
        if not already_verified:require(sha(p)==digest,'AUDIT_INITIAL_SHA '+str(p))
        self.files[p]=dict(sha256=digest,stamp=self.stamp(s),watch=watch)

    def check(self):
        with self.diagnostics.measure('audit.unique_file_metadata'):
            for p,record in self.files.items():
                if record['watch']:require(self.stamp(p.stat())==record['stamp'],'AUDIT_FILE_CHANGED '+str(p))
        self.metadata_passes+=1

    def final(self):
        self.check()
        with self.diagnostics.measure('audit.final_source_SHA'):
            for p,record in self.files.items():require(sha(p)==record['sha256'],'AUDIT_FINAL_SHA '+str(p))
        self.full_hash_passes+=1
        return self.summary()

    def summary(self):
        return dict(policy='LOADED_STATIC_START_END_HASH/v1',unique_files=len(self.files),
            runtime_identity_files=sum(r['watch'] for r in self.files.values()),
            metadata_passes=self.metadata_passes,final_hash_passes=self.full_hash_passes,
            limitation='Loaded static files are hashed at startup/end, not continuously monitored during computation')

def prepare_runtime_files(root,scope,scope_sha,session,hardware_sha,c,reg,*,diagnostics=NONE):
    guard=RuntimeFiles(diagnostics=diagnostics)
    # These in-memory objects and hashes were already admitted before device use.
    require(load(root/'session.json')==session,'JOINT_SESSION_CHANGED')
    guard.add(root/'scope.json',scope_sha)
    guard.add(root/'session.json',sha(root/'session.json'))
    guard.add(root/'hardware_handoff.json',hardware_sha)
    for name,digest in scope['source_sha256'].items():
        p=(HERE/name).resolve();require(p.is_relative_to(HERE),'JOINT_SOURCE_OUTSIDE_GUI')
        guard.add(p,digest,watch=False)
    # Constructors verified these pins and stored their load-time metadata.
    for key,pin in c.registry['pins'].items():
        same=c.paths.get(key)==host_path(pin['path'])
        guard.add(pin['path'],pin['sha256'],prior_stamp=c.stamps[key] if same else None,already_verified=True,watch=False)
    for key,pin in c.joint['pins'].items():
        guard.add(pin['path'],pin['sha256'],prior_stamp=c.stamps[key],already_verified=True,watch=False)
    for key,pin in c.spatial.data['pins'].items():
        guard.add(pin['path'],pin['sha256'],prior_stamp=c.spatial.stamps[key],already_verified=True,watch=False)
    for key,pin in reg.pins.items():
        guard.add(pin['path'],pin['sha256'],prior_stamp=reg.stamps[key],already_verified=True,watch=False)
    for name in ('hybrid_registry.json','hybrid_joint_registry.json','spatial_registry.json','live_registry.json'):
        guard.add(HERE/name,sha(HERE/name),watch=False)
    guard.check()
    return guard
