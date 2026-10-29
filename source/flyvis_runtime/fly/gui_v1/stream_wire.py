"""Lossless FP32 stream envelope. No neural computation, truncation or precision change."""
import base64
import hashlib
import numpy as np
from live_protocol import require

SHAPES={'spatial':(5768,), 'input_hex':(721,), 'flow':(2,721)}

def encode_packet(packet):
    output={k:v for k,v in packet.items() if k not in ('spatial','input_hex','flow')}
    output['spatial']={k:v for k,v in packet['spatial'].items() if k!='values'}
    arrays={}
    for key,shape in SHAPES.items():
        values=packet['spatial']['values'] if key=='spatial' else packet[key]
        a=np.asarray(values,dtype='<f4')
        require(a.shape==shape and np.isfinite(a).all(),'WIRE_ARRAY_SCHEMA '+key)
        raw=a.tobytes()
        arrays[key]=dict(dtype='<f4',shape=list(shape),sha256=hashlib.sha256(raw).hexdigest(),base64=base64.b64encode(raw).decode())
    output['wire_arrays']=arrays;output['wire_format']='float32-le-base64/v1'
    return output

def decode_packet(packet):
    require(packet['wire_format']=='float32-le-base64/v1' and set(packet['wire_arrays'])==set(SHAPES),'WIRE_FORMAT')
    output={k:v for k,v in packet.items() if k not in ('wire_arrays','wire_format')}
    output['spatial']=dict(packet['spatial'])
    for key,shape in SHAPES.items():
        item=packet['wire_arrays'][key]
        require(item['dtype']=='<f4' and item['shape']==list(shape),'WIRE_ARRAY_SCHEMA '+key)
        require(len(item['base64'])<=int(np.prod(shape))*6,'WIRE_ARRAY_BOUND')
        raw=base64.b64decode(item['base64'],validate=True)
        require(len(raw)==int(np.prod(shape))*4 and hashlib.sha256(raw).hexdigest()==item['sha256'],'WIRE_ARRAY_HASH '+key)
        a=np.frombuffer(raw,dtype='<f4').reshape(shape)
        require(np.isfinite(a).all(),'WIRE_NONFINITE')
        if key=='spatial':output['spatial']['values']=a.tolist()
        else:output[key]=a.tolist()
    return output
