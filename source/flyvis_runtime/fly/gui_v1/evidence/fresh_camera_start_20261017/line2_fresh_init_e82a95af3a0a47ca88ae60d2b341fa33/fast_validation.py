"""Independent NumPy implementation of the pinned scalar Q24 contract.

Every lane and every overflow stage is checked. No clipping, approximation,
float arithmetic or hardware output is used to construct the expected result.
"""
import hashlib,json,types
import numpy as np
DT=83886
def checked(values,bits,label):
    a=np.asarray(values)
    if a.dtype.kind not in 'iu' or (a.dtype.kind=='u' and np.any(a>np.iinfo(np.int64).max)):
        raise ValueError('INTEGER_ARRAY_REQUIRED '+label)
    a=a.astype(np.int64,copy=False)
    if np.any(a<-(1<<(bits-1))) or np.any(a>=(1<<(bits-1))):
        raise OverflowError(label+' signed'+str(bits))
    return a
def rounded(product):
    # Drive33 * parameter31 fits signed63; abs never reaches int64 minimum.
    return np.where(product<0,-(((-product)+(1<<23))>>24),(product+(1<<23))>>24)
def oracle(old,chemical,x,bias,inverse_tau):
    rows=[checked(v,31,k) for k,v in zip(('old','chemical','x','bias','inverse_tau'),(old,chemical,x,bias,inverse_tau))]
    if rows[0].ndim!=1 or any(a.shape!=rows[0].shape for a in rows) or not rows[0].size:raise ValueError('ONE_DIMENSIONAL_EQUAL_NONEMPTY')
    a,c,xi,b,inv=rows
    drive=checked(-a+b+c+xi,33,'drive')
    velocity=checked(rounded(drive*inv),31,'velocity')
    delta=checked(rounded(velocity*DT),31,'delta')
    new=checked(a+delta,31,'new')
    return new,np.stack((a,drive,velocity,delta,new),axis=1)
class BoundReference:
    def init__(self,c):
        self.c=c;p=c.parameters
        kinds=np.asarray(p['type_index'],dtype=np.int64)
        self.bias=np.asarray(p['bias_dictionary_q24'],dtype=np.int64)[kinds].copy()
        self.inverse=np.asarray(p['inverse_tau_dictionary_q24'],dtype=np.int64)[kinds].copy()
        if kinds.shape!=(5768,):raise ValueError('EXACT_5768_PARAMETER_ORDER')
        checked(self.bias,31,'bias');checked(self.inverse,31,'inverse_tau')
        self.bias.flags.writeable=self.inverse.flags.writeable=False
        self.parameter_identity=hashlib.sha256(json.dumps(p,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    def expected_H(self,payload):
        if type(payload) is not bytes or len(payload)!=self.c.wire.INPUT_BYTES:raise ValueError('Q24_REFERENCE_INPUT')
        rows=checked(np.frombuffer(payload,dtype='<i4'),31,'payload').reshape(3,5768)
        result,trace=oracle(*rows,self.bias,self.inverse)
        return result.astype('<i4').tobytes(),trace
def install(c):
    if hasattr(c,'_optimized_reference'):raise ValueError('REFERENCE_ALREADY_INSTALLED')
    ref=BoundReference(c);original=c.validate_H
    c.expected_H=ref.expected_H
    def validate(payload,candidate):
        # Retain original decode, exact comparison and pinned-source receipt.
        record=original(payload,candidate)
        return dict(record,implementation='VECTOR_Q24_ALL_STAGES_V1',parameter_identity=ref.parameter_identity)
    c.validate_H=validate;c._optimized_reference=ref
    return ref
