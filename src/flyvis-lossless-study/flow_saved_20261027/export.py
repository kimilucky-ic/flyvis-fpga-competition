"""Export unchanged official eval decoder, then compare every retained state."""
import os
os.environ.update(CUDA_VISIBLE_DEVICES='-1',FLYVIS_ROOT_DIR='/opt/flyvis-visual-experiments-data',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
from pathlib import Path
import json,hashlib,zipfile,numpy as np,torch
from flyvis import NetworkView
O=Path(__file__).resolve().parent;D=O/'export';D.mkdir(exist_ok=False)
torch.set_num_threads(1);torch.set_num_interop_threads(1)
v=NetworkView('/opt/flyvis-visual-experiments-data/results/flow/0000/000');d=v.init_decoder(checkpoint='best')['flow'];d.eval();expected={k:x.clone() for k,x in d.state_dict().items()}
with torch.no_grad():
 traced=torch.jit.trace(d,torch.zeros(1,1,45669),check_trace=True);traced=torch.jit.freeze(traced.eval());torch.jit.save(traced,str(D/'official_flow_cpu.pt'))
assert all(torch.equal(x,expected[k]) for k,x in d.state_dict().items())
zpath=Path('/mnt/c/Users/hzy72/Documents/xwechat_files/wxid_khlrd7p7q6j422_642a/temp/RWTemp/2026-10/8eaa68ae41247203942b7fc2b28636e7/交付_原始数据_精简版.zip');maximum=0.;count=0
with zipfile.ZipFile(zpath) as z,torch.no_grad():
 for path in sorted(n for n in z.namelist() if n.endswith('/states.bin')):
  folder=path.split('/')[0];a=np.frombuffer(z.read(path),'<f4').reshape(-1,45669);gold=np.load(O/'repeat1'/(folder+'_flow.npy'))
  actual=np.stack([traced(torch.from_numpy(row.copy())[None,None]).numpy()[0,0] for row in a]);err=float(np.max(abs(actual-gold)));maximum=max(maximum,err);count+=len(a)
  assert np.allclose(actual,gold,atol=1e-5,rtol=1e-5);print(folder,err,flush=True)
manifest=dict(schema='line11-official-flow-export/v1',checkpoint_sha256=json.loads((O/'repeat1/RESULT.json').read_text())['checkpoint_sha256'],artifact_sha256=hashlib.sha256((D/'official_flow_cpu.pt').read_bytes()).hexdigest(),input_shape=[1,1,45669],output_shape=[1,1,2,721],axes=['right_positive','up_positive'],export='torch.jit.trace then freeze of unchanged official DecoderGAVP.eval',source_sha256=json.loads((O/'repeat1/RESULT.json').read_text())['decoder_source_sha256'],validation_states=count,max_abs_error=maximum,atol=1e-5,rtol=1e-5,decoder_state_unchanged=True,hardware_actions=0)
(D/'manifest.json').write_text(json.dumps(manifest,indent=2));print('PASS_OFFICIAL_EXPORT',count,maximum)
