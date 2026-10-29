"""Lossless float64 per-time/per-global-node differences, streamed on demand.

All H/R are selected by frozen global IDs; no readout clipping or final zeroing.
Creates a NEW file only. The raw full trajectories remain the authority.
"""
import argparse
from common import *

def main():
    p=argparse.ArgumentParser();p.add_argument('--candidate',required=True,choices=['B_T5c','A_T4c','C_T4T5_all_centers']);p.add_argument('--repeat',default='formal_r1',choices=['formal_r1','formal_r2']);p.add_argument('--comparison',default='Ablation-Sham',choices=['Ablation-Sham','Sham-Full']);p.add_argument('--out',required=True);a=p.parse_args()
    path=Path(a.out).resolve()
    if not path.is_relative_to(HERE):raise SystemExit('Output must remain in owned experiment directory')
    if path.exists():raise SystemExit('Preserve existing file')
    root=HERE/'artifacts'/a.repeat/a.candidate
    left=np.load(root/('Ablation' if a.comparison=='Ablation-Sham' else 'Sham')/'activities_full.npy',mmap_mode='r')
    right=np.load(root/'Sham/activities_full.npy',mmap_mode='r') if a.comparison=='Ablation-Sham' else np.load(host_path(load(BUNDLE/'screen_manifest.json')['Full_reference_path'])/'activities_full.npy',mmap_mode='r')
    result=np.lib.format.open_memmap(path,mode='w+',dtype=np.float64,shape=left.shape)
    for c in range(4):
        for k in range(485):result[c,k]=left[c,k].astype(np.float64)-right[c,k].astype(np.float64)
    result.flush();print(json.dumps(dict(path=str(path),shape=list(result.shape),dtype='float64',sha256=file_hash(path),comparison=a.comparison)))

if __name__=='__main__':main()
