"""Unmodified official DecoderGAVP/LayerActivity class bodies on CPU.

AST loading avoids optional datamate/HDF5/FlyVis package initialization. Only
original definitions are executed; connectome metadata is a read-only adapter.
All parameters/buffers come from the original checkpoint; no decoder training.
"""
import ast
import logging
import weakref
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Dict,List,Optional,Union,Tuple
import numpy as np
from numpy.typing import NDArray
import torch
from torch import nn
from torch.nn import functional as nnf
from common import UPSTREAM,CHECKPOINT,SUPPORT,source,load,sha

def definitions(path,names,env):
    tree=ast.parse(path.read_text(encoding='utf-8'))
    nodes=[n for n in tree.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in names]
    assert len(nodes)==len(names)
    exec(compile(ast.Module(body=nodes,type_ignores=[]),str(path),'exec'),env)

class CPUDecoder:
    def init__(self):
        self.contract=load(SUPPORT/'FULL_DECODER_CONTRACT.json')
        assert sha(CHECKPOINT)==self.contract['model']['checkpoint_sha256']
        for relative,entry in self.contract['source_files'].items():assert sha(UPSTREAM/relative)==entry['sha256']
        env=dict(np=np,torch=torch,nn=nn,nnf=nnf,device=torch.device('cpu'),weakref=weakref,
            NDArray=NDArray,Union=Union,List=List,Optional=Optional,Dict=Dict,Tuple=Tuple,
            ConnectomeFromAvgFilters=SimpleNamespace,Namespace=SimpleNamespace,
            dataclass=dataclass,logging=logging,logging_=logging,logging__=logging)
        env['logging']=logging.getLogger('original_decoder_cpu')
        definitions(UPSTREAM/'utils/hex_utils.py',{'get_hex_coords'},env)
        definitions(UPSTREAM/'utils/nn_utils.py',{'NumberOfParams','n_params'},env)
        definitions(UPSTREAM/'utils/activity_utils.py',{'CellTypeActivity','LayerActivity'},env)
        definitions(UPSTREAM/'task/decoder.py',{'ActivityDecoder','GlobalAvgPool','Conv2dConstWeight','Conv2dHexSpace','DecoderGAVP'},env)
        types,_,_,_=source(); ordered=list(dict.fromkeys(types.tolist()))
        cn=SimpleNamespace(config=SimpleNamespace(extent=15),unique_cell_types=np.array(ordered),
            input_cell_types=np.array(ordered[:8]),output_cell_types=np.array(self.contract['ordered_input_types']),
            nodes=SimpleNamespace(type=types,layer_index={t:np.flatnonzero(types==t) for t in ordered}))
        config=self.contract['decoder_config']
        self.net=env['DecoderGAVP'](cn,shape=config['shape'],kernel_size=config['kernel_size'],
            const_weight=config['const_weight'],p_dropout=config['p_dropout'],n_out_features=config['n_out_features'])
        expected=torch.load(CHECKPOINT,map_location='cpu',weights_only=False)['decoder']['flow']
        self.net.load_state_dict(expected,strict=True);self.net.eval()
        self.before={k:v.clone() for k,v in self.net.state_dict().items()}
        ids=np.load(SUPPORT/'cpu_audit_r1/decoder_input_global_ids.npy')
        assert np.array_equal(self.net.dvs_channels.output_indices,ids)
        self.calls=0
        self.assert_unchanged()

    def assert_unchanged(self):
        assert not any(m.training for m in self.net.modules())
        assert all(torch.equal(v,self.before[k]) for k,v in self.net.state_dict().items())

    @torch.no_grad()
    def decode(self,activity):
        if activity.ndim!=2 or activity.shape[1]!=45669 or not np.isfinite(activity).all():raise ValueError('Full activity required')
        out=np.empty((len(activity),2,721),np.float32)
        for k in range(0,len(activity),32):
            out[k:k+32]=self.net(torch.from_numpy(np.array(activity[k:k+32],copy=True))[None])[0].numpy()
            self.calls+=1
        self.assert_unchanged()
        assert np.isfinite(out).all()
        return out
