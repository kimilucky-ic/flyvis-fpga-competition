"""Read-only v2 handoff and integer-reference checks. Import performs no I/O."""
import numpy as np
from hybrid_a3 import A3Contract, module
from live_protocol import HERE, host_path, load, require, sha


class V2Contract(A3Contract):
    def init__(self):
        super().init__()  # Retain the accepted v1 source/mapping checks.
        self.joint = load(HERE/'hybrid_joint_registry.json')
        require(self.joint['schema']=='flyvis-hybrid-joint-preparation/v1','JOINT_SCHEMA')
        for key,pin in self.joint['pins'].items():
            p=host_path(pin['path']);require(sha(p)==pin['sha256'],'JOINT_SOURCE_CHANGED '+key)
            self.paths[key]=p;self.stamps[key]=(p.stat().st_size,p.stat().st_mtime_ns)
        self.wire=module('gui_A3R1_protocol_v2',self.paths['v2_protocol'])
        self.reference=module('gui_A3R1_integer_reference',self.paths['integer_reference'])
        require(self.wire.VERSION==2 and self.wire.CONFIG.hex()==self.fixture['config_id'],'V2_PROFILE')
        self.parameters=self.fixture['identity_payload']
        self.tolerance=self.joint['tolerance']
        require(self.tolerance=={'PL_max_integer_code_error':0,'R_atol':1e-5,'R_rtol':1e-5,
            'chemical_atol':1e-5,'chemical_rtol':1e-5,'Full_float32_role':'COMPARISON_ONLY_NOT_HARDWARE_ORACLE'},'TOLERANCE_CHANGED')

    def initial(self):
        """Warm start a[200] from accepted ON60 Full a[199] output, not a new prefix."""
        a=np.load(self.paths['ON60_full_prefix'],mmap_mode='r',allow_pickle=False)
        require(a.shape==(1,485,45669) and a.dtype==np.float32,'PREFIX_SHAPE')
        raw=np.array(a[0,199],copy=True);old=self.wire.encode_activity(raw[self.h])
        mixed=raw.copy();mixed[self.h]=self.decode(old)
        return mixed,old,raw

    def expected_H(self,payload):
        require(type(payload) is bytes and len(payload)==self.wire.INPUT_BYTES,'Q24_REFERENCE_INPUT')
        self.wire.validate_words(payload)
        values=np.frombuffer(payload,dtype='<i4').astype(np.int64).reshape(3,5768)
        types=np.array(self.parameters['type_index'],dtype=np.int64)
        bias=np.array(self.parameters['bias_dictionary_q24'],dtype=np.int64)[types]
        inv=np.array(self.parameters['inverse_tau_dictionary_q24'],dtype=np.int64)[types]
        expected,trace=self.reference.oracle(*values,bias,inv)
        return expected.astype('<i4').tobytes(),trace

    def validate_H(self,payload,candidate):
        self.decode(candidate);expected,_=self.expected_H(payload)
        error=np.abs(np.frombuffer(candidate,dtype='<i4').astype(np.int64)-np.frombuffer(expected,dtype='<i4'))
        require(int(error.max())==0,'PL_INTEGER_ORACLE_MISMATCH')
        return {'integer_values_checked':5768,'max_integer_code_error':0,
                'reference':'PINNED_A3_SCALAR_Q24','reference_sha256':self.joint['pins']['integer_reference']['sha256']}

    def readiness(self):
        self.unchanged()
        return dict(status='WAITING_FOR_BOARD_ACCEPTANCE_AND_SHORT_RUN_APPROVAL',protocol=2,
            condition='ON60',proposed_model_steps=[200,201,202],model_duration_s=.015,
            initial_source='ACCEPTED_FULL_ON60_OUTPUT_199_QUANTIZE_H_ONCE',
            GPU_mode='R39901_FP32_PLUS_ORIGINAL_CHEMICAL',H_mode='A3R1_Q24_PL_REQUIRED',
            backend='NOT_CONNECTED',PL_proven_global_ids=[],tolerance=self.tolerance,
            full_485_authorized=False,endpoint=None,board_operations=0)
