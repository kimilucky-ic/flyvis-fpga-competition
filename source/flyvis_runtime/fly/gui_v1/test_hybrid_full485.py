"""Off-device scope/initial-state checks. No sockets, CUDA or board operations."""
import copy,unittest
from datetime import datetime,timezone,timedelta
from unittest.mock import patch
import numpy as np
from hybrid_full485 import Full485Contract,validate_full_scope
from hybrid_joint_evidence import board_acceptance
from hybrid_joint import connect_live
from live_protocol import canonical

class Full485Profile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.c=Full485Contract();cls.acceptance=board_acceptance(cls.c)
    def setUp(self):
        c=self.c;now=datetime.now(timezone.utc)
        self.s=dict(schema='flyvis-approved-joint-full485/v1',status='APPROVED_BY_HUMAN',human_authorization_reference='CPU_TEST_ONLY',
            condition='ON60',model_steps=list(range(485)),max_requests=485,max_commits=485,automatic_retry=False,
            new_loads=0,new_resets=0,new_allocations=0,board_acceptance_sha256=canonical(self.acceptance),model=c.registry['model'],
            bit_sha256=c.wire.BIT_SHA,hwh_sha256=c.wire.HWH_SHA,mapping_sha256=c.mapping_sha,tolerance=c.tolerance,
            initial_file_sha256=c.reg.data['model']['initial_state_sha256'],initial_kind='FROZEN_GRAY_ADAPTED_A0_QUANTIZE_H_ONCE',
            endpoint={'host':'192.168.2.99','port':5768},expected_boot_id='CPU_TEST',expected_server_session='CPU_TEST_NEW',
            start_utc=(now-timedelta(seconds=1)).isoformat(),end_utc=(now+timedelta(seconds=2699)).isoformat(),
            max_worker_seconds=2700,max_compute_seconds=2400,input_sha256=c.reg.pins['stimulus_ON60']['sha256'],
            gpu_lease_id='CPU_TEST',run_id='CPU_TEST',comparison_id='CPU_TEST')
    def check(self):validate_full_scope(self.s,self.c,self.acceptance)
    def test_valid_scope_without_execution(self):self.check()
    def test_initial_is_frozen_a0_not_output199(self):
        a,words,raw=self.c.initial();np.testing.assert_array_equal(raw,self.c.raw)
        np.testing.assert_array_equal(a[self.c.r],raw[self.c.r]);np.testing.assert_array_equal(a[self.c.h],self.c.decode(words))
        self.assertEqual(words,self.c.wire.encode_activity(raw[self.c.h]))
        from hybrid_v2 import V2Contract
        self.assertFalse(np.array_equal(a,V2Contract().initial()[0]))
    def test_no_scope_cannot_construct_client(self):
        self.s['status']='PENDING'
        with patch.object(self.c.wire,'Client') as client:
            with self.assertRaisesRegex(ValueError,'NOT_AUTHORIZED'):connect_live(self.c,self.s,self.acceptance,None,None,'unused',lambda:None)
            client.assert_not_called()
    def test_short_steps_cannot_expand_implicitly(self):
        self.s['model_steps']=[200,201,202]
        with self.assertRaisesRegex(ValueError,'EXACT_485'):self.check()
    def test_cannot_request_486(self):
        self.s['max_requests']=486
        with self.assertRaisesRegex(ValueError,'EXACT_485'):self.check()
    def test_reset_and_reload_forbidden(self):
        for key in ('new_loads','new_resets','new_allocations'):
            self.s[key]=1
            with self.assertRaisesRegex(ValueError,'NO_LOAD_RESET'):self.check()
            self.s[key]=0
    def test_old_session_forbidden(self):
        self.s['expected_server_session']='f6f0fc75d3304655adc9c9879be0249b'
        with self.assertRaisesRegex(ValueError,'FRESH_FULL485'):self.check()
    def test_no_longer_window(self):
        self.s['end_utc']=(datetime.now(timezone.utc)+timedelta(hours=1)).isoformat()
        with self.assertRaisesRegex(ValueError,'SCOPE_EXPIRED'):self.check()
    def test_numerical_tolerance_frozen(self):
        self.s['tolerance']={**self.c.tolerance,'PL_max_integer_code_error':1}
        with self.assertRaisesRegex(ValueError,'EXACT_FULL485_PROFILE'):self.check()

if __name__=='__main__':unittest.main()
