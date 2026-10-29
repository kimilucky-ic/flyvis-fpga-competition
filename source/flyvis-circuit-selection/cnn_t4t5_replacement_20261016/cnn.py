"""Learned hex convolution + recurrent residual; no original H parameters/API."""
import torch
from torch import nn
from torch.nn import functional as F

class HexCNN(nn.Module):
    """C old-state fields -> 8 new activity fields at all721 positions.

    The Markov memory is the module's OWN previous8 outputs. ReLU is a CNN
    activation. All convolution, recurrent weights and offsets are learned.
    No original H weight, tau, bias, HH/RH edge table or teacher enters forward.
    """
    def init__(self,channels,offsets,grid_uv,h_channels):
        super().init__()
        self.kernel=nn.Parameter(torch.zeros(8,channels,len(offsets)))
        self.recurrent=nn.Parameter(torch.zeros(8,8))
        self.offset=nn.Parameter(torch.zeros(8))
        self.register_buffer('input_scale',torch.ones(channels))
        self.register_buffer('h_scale',torch.ones(8))
        self.register_buffer('output_scale',torch.ones(8))
        self.register_buffer('offsets',torch.as_tensor(offsets,dtype=torch.long))
        self.register_buffer('uv',torch.as_tensor(grid_uv,dtype=torch.long)+15)
        self.register_buffer('h_channels',torch.as_tensor(h_channels,dtype=torch.long))

    def patch_delta(self,patch,old_h):
        x=F.relu(patch)/self.input_scale[None,:,None]
        return (F.linear(x.flatten(1),self.kernel.flatten(1))+
            F.linear(old_h/self.h_scale,self.recurrent)+self.offset)*self.output_scale

    def forward(self,fields):
        # fields [B,C,721], same axial storage and true masked hex radius7.
        canvas=fields.new_zeros((len(fields),fields.shape[1],31,31))
        canvas[:,:,self.uv[0],self.uv[1]]=F.relu(fields)/self.input_scale[None,:,None]
        weight=self.kernel.new_zeros((8,fields.shape[1],15,15))
        # Conv2d is cross-correlation: tap+du,+dv reads source at target+offset.
        weight[:,:,self.offsets[:,0]+7,self.offsets[:,1]+7]=self.kernel
        conv=F.conv2d(canvas,weight,padding=7)[:,:,self.uv[0],self.uv[1]]
        old_h=fields[:,self.h_channels,:]
        rec=torch.einsum('oi,bin->bon',self.recurrent,old_h/self.h_scale[None,:,None])
        return old_h+(conv+rec+self.offset[None,:,None])*self.output_scale[None,:,None]

class CNNService:
    def init__(self,model,mapping):
        self.model=model.eval();self.mapping=mapping;self.calls=0
        self.field_ids=torch.as_tensor(mapping['field_ids'],dtype=torch.long)
        self.valid=self.field_ids>=0
        self.h=torch.as_tensor(mapping['H_grid_ids'],dtype=torch.long)

    @torch.no_grad()
    def step(self,old):
        # All R values are from live old state, all H values are own old outputs.
        fields=old[self.field_ids.clamp_min(0)]*self.valid
        result=self.model(fields[None])[0].reshape(-1)
        if result.shape!=(5768,) or not bool(torch.isfinite(result).all()):raise ValueError('CNN invalid candidate')
        self.calls+=1
        return result

def restore(path,mapping):
    model=HexCNN(mapping['field_ids'].shape[0],mapping['offsets'],mapping['grid_uv'],mapping['h_channels'])
    model.load_state_dict(torch.load(path,map_location='cpu',weights_only=True))
    return model.eval()
