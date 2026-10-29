from pathlib import Path
import shutil
O=Path(__file__).resolve().parent;R=O.parent/'ov5640_live_v261_20261026'
for rel in ['bundle/ram_records.py','bundle/live_board.py','bundle/release_manifest.json','FINAL_MANIFEST_SHA256.json']:
 p=O/'before'/rel;p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists();shutil.copy2(R/rel,p)
p=R/'bundle/ram_records.py';s=p.read_text('utf-8');anchor='    def key(self,path):'
method='''    def prevalidate_generated_steps(self,root,steps):
        # Closed, fixed filename grammar inside a newly-created empty run.
        # Resolve anchors once; do not resolve 13paths *4096steps individually.
        if self.active or self.known_keys:raise RuntimeError('fresh journal required')
        if type(steps) is not int or not 1<=steps<=4096:raise ValueError('step bound')
        root=Path(root)
        if root.resolve()!=self.root:raise ValueError('run root mismatch')
        allowed={'transport','spool'}
        children=list(self.root.iterdir())
        if {p.name for p in children}-allowed:raise ValueError('run namespace is not fresh')
        if 'transport' not in {p.name for p in children}:raise ValueError('transport missing')
        for p in children:
            if p.is_symlink() or p.resolve()!=self.root/p.name or not p.is_dir():raise ValueError('redirected run directory')
            if next(p.iterdir(),None) is not None:raise ValueError('run directory is not empty')
        names=('PREPARED.bin','COMMITTED.bin','CYCLE_CHECK.json','PUBLICATION.json','TIMING.json','PACKET_TIMING.json','WORKER_TIMING.json','RETURNED_UNCOMMITTED.bin','IN_DOUBT.json')
        keys={};prefix=str(root)
        for k in range(steps):
            d=os.path.join('capture','bound','%06d'%k)
            rels=[d]+[os.path.join(d,n) for n in names]
            rels.extend((os.path.join('transport','%06d.packet'%k),os.path.join('transport','%06d.ack.json'%k)))
            rels.append('CAMERA_BUFFER.json' if k==0 else 'CAMERA_BUFFER_%06d.json'%k)
            for rel in rels:keys[os.path.join(prefix,rel)]=rel
        self.known_keys=keys
        return dict(paths=len(keys),steps=steps,method='FRESH_NAMESPACE_FIXED_GRAMMAR_NO_PER_FILE_RESOLVE')
'''
assert s.count(anchor)==1;p.write_text(s.replace(anchor,method+anchor),encoding='utf-8')
p=R/'bundle/live_board.py';s=p.read_text('utf-8')
s=s.replace("    from offline_check import verify\n    identity=verify(root);root=Path(root);base=Path(base)","    startup_begin=time.monotonic();startup={}\n    print('LINE11_STARTUP 校验本轮文件，尚未加载固件',flush=True)\n    from offline_check import verify\n    identity=verify(root);root=Path(root);base=Path(base)\n    startup['package_verify_ms']=(time.monotonic()-startup_begin)*1000\n    storage_begin=time.monotonic()")
a=s.index('    known_paths=[]');b=s.index('    context=dict(',a)
s=s[:a]+"    print('LINE11_STARTUP 准备记录索引，尚未加载固件',flush=True)\n    path_begin=time.monotonic()\n    startup['path_index']=journal.prevalidate_generated_steps(out,config['max_steps'])\n    startup['path_index_ms']=(time.monotonic()-path_begin)*1000\n    startup['storage_and_runtime_prepare_ms']=(time.monotonic()-storage_begin)*1000\n    startup['before_prepare_ms']=(time.monotonic()-startup_begin)*1000\n    print('LINE11_STARTUP_READY %.3fs；即将加载驱动和固件'%(startup['before_prepare_ms']/1000),flush=True)\n"+s[b:]
s=s.replace("context.update(duration_s=config['duration_s']","context.update(startup_timing=startup,duration_s=config['duration_s']")
p.write_text(s,encoding='utf-8')
print('Patched startup path indexing and timings only; backup retained')
