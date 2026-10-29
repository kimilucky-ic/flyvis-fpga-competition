import json,traceback
from pathlib import Path
import numpy as np, torch
from r_only import RStepService
BASE=Path(__file__).resolve().parent;B=BASE/'artifacts/reference_bundle_v1'
s=RStepService(B/'expanded_parameters.npz',B/'identity_manifest.json',B/'candidates/B_T5c/candidate_manifest.json')
old=torch.from_numpy(np.load(B/'initial_state_full.npy'));frame=torch.from_numpy(np.load(B/'stimulus.npy')[0,0,0].copy())
original=torch.Tensor.scatter_add_
results={}
for mode in ['cpu',None]:
 torch.set_default_device(mode);calls=[]
 def trace(self,dim,index,src):
  calls.append(dict(shape=list(self.shape),frames=[str(v) for v in traceback.extract_stack(limit=6)]))
  return original(self,dim,index,src)
 torch.Tensor.scatter_add_=trace
 try:s.step(old,frame,step_id=0,run_id='trace-diagnosis',condition_id='0')
 finally:torch.Tensor.scatter_add_=original
 results[str(mode)]=calls
(BASE/'artifacts/trace_instrumentation_diagnosis.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results,indent=2))
