"""Explicit original Full oracle, for independent comparison only.

Never imported/called by r_only.py. Requires the existing official FlyVis model
and the selected CPU/GPU environment. Does not silently adapt or reset state.
"""
import json, numpy as np, torch
from pathlib import Path
from r_only import InterfaceError, file_sha, array_sha

class FullNetworkOracle:
    def init__(self,identity_path,*,model_path="/opt/flyvis-visual-experiments-data/results/flow/0000/000",device="cpu"):
        from flyvis import NetworkView
        from flyvis.utils.tensor_utils import AutoDeref
        self.AutoDeref=AutoDeref
        self.device=torch.device(device)
        if self.device.type=="cuda":self.device=torch.device('cuda',self.device.index or 0)
        self.identity=json.loads(Path(identity_path).read_text())
        self.view=NetworkView(model_path)
        ckpt=Path(self.view.get_checkpoint('best'))
        if file_sha(ckpt)!=self.identity['checkpoint_sha256']:raise InterfaceError("Full checkpoint identity mismatch")
        self.expected=torch.load(ckpt,map_location='cpu',weights_only=False)['network']
        wrapper=self.view.network(checkpoint='best',lazy=True);wrapper.recover()
        self.net=wrapper.network;self.net.eval()
        self.dt=float(self.identity['dt_s'])
        if self.net.n_nodes!=self.identity['n_nodes'] or self.net.n_edges!=self.identity['n_edges']:
            raise InterfaceError("Full graph size mismatch")
        if self.net._state_hooks:raise InterfaceError("state hooks are forbidden")
        if type(self.net.dynamics).__name__!='PPNeuronIGRSynapses' or type(self.net.dynamics.activation).__name__!='ReLU':
            raise InterfaceError("unexpected original dynamics")
        self.params=self.net._param_api()
        if self.params.nodes.bias.device!=self.device:raise InterfaceError("Full environment/default device differs from requested device")
        actual=dict(bias=self.params.nodes.bias,time_const=self.params.nodes.time_const,
             effective_weight=self.params.edges.weight,sign=self.params.edges.sign,
             syn_count=self.params.edges.syn_count,syn_strength=self.params.edges.syn_strength)
        arrays={k:np.ascontiguousarray(t.detach().cpu().numpy()) for k,t in actual.items()}
        arrays.update(source_global=self.net.connectome.edges.source_index[:].astype(np.int64),
          target_global=self.net.connectome.edges.target_index[:].astype(np.int64),
          original_edge_index=np.arange(self.net.n_edges,dtype=np.int64),
          input_node_index=self.net.stimulus.input_index.astype(np.int64))
        if {k:array_sha(v) for k,v in arrays.items()}!=self.identity['expanded_parameter_digests']:
            raise InterfaceError("Full parameters differ from reference bundle")
        self.assert_weights_unchanged()
        self.net.stimulus.zero(1,1)

    def assert_weights_unchanged(self):
        if not all(torch.equal(self.net.state_dict()[k].detach().cpu(),v) for k,v in self.expected.items()):
            raise InterfaceError("Full checkpoint weights changed")
        return True

    @torch.no_grad()
    def step(self,old_full,hex_frame):
        """Original Network._next_state with EXPLICIT passed old full state."""
        if old_full.shape!=(self.net.n_nodes,) or old_full.dtype!=torch.float32 or old_full.device!=self.device:
            raise InterfaceError("invalid Full old state")
        if hex_frame.shape!=(721,) or hex_frame.dtype!=torch.float32 or hex_frame.device!=self.device:
            raise InterfaceError("invalid Full input")
        if not bool(torch.isfinite(old_full).all()) or not bool(torch.isfinite(hex_frame).all()):
            raise InterfaceError("nonfinite Full input")
        if bool(((hex_frame<0)|(hex_frame>1)).any()):raise InterfaceError("Full hex input outside [0,1]")
        self.net.stimulus.buffer.zero_()
        self.net.stimulus.add_input(hex_frame.reshape(1,1,1,721))
        state=self.net._state_api(self.AutoDeref(nodes=self.AutoDeref(activity=old_full.reshape(1,-1)),edges=self.AutoDeref()))
        new=self.net._next_state(self.params,state,self.net.stimulus()[:,0],self.dt)
        if list(new.nodes.keys())!=['activity'] or len(new.edges):raise InterfaceError("Full state schema changed")
        return new.nodes.activity[0].detach()
