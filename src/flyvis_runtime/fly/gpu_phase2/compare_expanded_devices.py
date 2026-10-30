from pathlib import Path
import json,numpy as np
BASE=Path(__file__).resolve().parent/'artifacts'
a=BASE/'init_cpu_r1';b=BASE/'init_gpu_r1'
ia=json.loads((a/'identity_manifest.json').read_text());ib=json.loads((b/'identity_manifest.json').read_text())
out={}
with np.load(a/'expanded_parameters.npz') as ca,np.load(b/'expanded_parameters.npz') as cb:
 for k in ca.files:
  x,y=ca[k],cb[k]
  if not np.array_equal(x,y):
   out[k]=dict(cpu_digest=ia['expanded_parameter_digests'][k],gpu_digest=ib['expanded_parameter_digests'][k],
      dtype=str(x.dtype),shape=list(x.shape),differing_values=int((x!=y).sum()),max_abs=float(np.abs(x.astype(np.float64)-y.astype(np.float64)).max()),
      allclose=bool(np.allclose(x,y,atol=1e-5,rtol=1e-5)))
print(json.dumps(out,indent=2))
(BASE/'device_expanded_parameter_difference.json').write_text(json.dumps(out,indent=2))
