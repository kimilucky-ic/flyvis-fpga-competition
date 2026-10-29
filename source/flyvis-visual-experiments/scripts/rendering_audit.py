"""Read-only comparison of pre-existing official CPU/GPU rendered offset caches."""
import hashlib,json
from pathlib import Path
import h5py,numpy as np,yaml
work=Path(__file__).resolve().parents[1]
gpu=Path('/opt/flyvis-gpu-data/renderings/RenderedOffsets_0001')
cpu_roots=[Path('/opt/flyvis-minimal-cpu-a/renderings')]
gpu_meta=yaml.safe_load((gpu/'meta.yaml').read_text())['config']
with h5py.File(gpu/'offsets.h5','r') as f:
    keys=list(f.keys());assert len(keys)==1,keys
    rendered_gpu=f[keys[0]][:]
rows=[]
for root in cpu_roots:
    for cpu in sorted(root.glob('RenderedOffsets_*')):
        meta=yaml.safe_load((cpu/'meta.yaml').read_text())
        if meta.get('status')!='done':continue
        config=meta['config'];angle=config['angles'][0]
        if angle not in [0,180]:continue
        with h5py.File(cpu/'offsets.h5','r') as f:
            keys=list(f.keys());assert len(keys)==1,keys
            rendered_cpu=f[keys[0]][:]
        index=gpu_meta['angles'].index(angle)*2+1
        aa=rendered_gpu[index];bb=rendered_cpu[0]
        delta=aa-bb
        # Compare all 21 offsets, not only the three positions used in the earlier benchmark.
        rows.append(dict(angle=angle,cpu_cache=str(cpu),gpu_cache=str(gpu),shape=list(aa.shape),
                         max_abs_error=float(np.abs(delta).max()),rmse=float(np.sqrt(np.mean(delta**2))),
                         different_elements=int(np.count_nonzero(delta)),
                         differing_offset_indices=np.flatnonzero(np.any(delta!=0,axis=1)).tolist(),
                         allclose=bool(np.allclose(aa,bb,atol=1e-5,rtol=1e-5)),
                         config_match_except_condition_list=all(config[k]==gpu_meta[k] for k in config if k not in ['angles','intensities'])))
report=dict(status='PASS' if all(r['allclose'] for r in rows) else 'FAIL',comparisons=rows,
            source_observation='Original HexEye constructor uses float16 coordinates/masks. Numerical cause of device differences has not yet been isolated.',
            scope='Existing native HDF5 rendering caches read without mutation; all 21 positions for ON 0/180; cache geometry and rendering vs time resampling distinguished')
(work/'artifacts/rendering_cache_audit.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report),flush=True)
