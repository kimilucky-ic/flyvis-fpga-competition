"""Time-helper integration admission checks; no HTTP listener or devices."""
import copy
from datetime import datetime,timedelta,timezone
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import uuid

from live_protocol import HERE,load,sha,write
from joint_camera_control import hardware_module
from joint_camera_preparation import PreparationAuthority,clock_binding,verify_prepared_handoff
from joint_camera_protocol import validate_scope

PACKAGE=HERE.parent.parent/'fpga/flyvis-fpga/t4t5_neurononly_20261011/soc_a_20261012/camera_joint_ready_20261016'
OUT=HERE/'evidence/camera_joint_start_20261016'


class PreparationTests(unittest.TestCase):
    def setUp(self):
        self.root=OUT/'cpu_preparation'/uuid.uuid4().hex;self.root.mkdir(parents=True)
        self.declaration=load(PACKAGE/'templates/HARDWARE_HANDOFF_NOT_PREPARED.json')
        self.scope=load(HERE/'evidence/camera_joint_service_review_20261016/scope_draft_r2.json')
        now=datetime.now(timezone.utc)
        self.scope.update(status='APPROVED_BY_HUMAN',execution_authority='CPU_FIXTURE_ONLY',
            human_authorization_reference='CPU_FIXTURE_NO_DEVICE_AUTHORITY',boot_id='CPU_BOOT',
            start_utc=(now-timedelta(seconds=2)).isoformat(),end_utc=(now+timedelta(seconds=280)).isoformat())
        self.scope.pop('hardware_handoff_sha256',None)
        self.declaration.update(status='DECLARED_NOT_PREPARED',run_id=self.scope['run_id'],server_session=self.scope['server_session'],
            boot_id='CPU_BOOT',listener_id=uuid.uuid4().hex,plan_sha256='21'*32,
            control_config=dict(run_id=self.scope['run_id'],server_session=self.scope['server_session'],plan_sha256='21'*32,control_key='31'*32),
            pc_authority_endpoint=dict(host='CPU_ONLY',port=18791))
        write(self.root/'HARDWARE_DECLARATION.json',self.declaration)
        self.scope['hardware_declaration_sha256']=sha(self.root/'HARDWARE_DECLARATION.json')
        write(self.root/'scope.json',self.scope)
        self.config=dict(clock_binding(self.declaration,self.scope,sha(self.root/'scope.json')),control_key='31'*32)
        write(self.root/'PRIVATE_CONFIG.json',self.config)
    def test_one_real_signed_time_answer_with_2021_board_clock(self):
        authority=PreparationAuthority(self.root)
        clock=hardware_module(self.declaration,'clock')
        mono=[100_000_000_000];wall=[int(datetime(2021,11,19,tzinfo=timezone.utc).timestamp()*1e9)]
        board=clock.BoardClockHandshake(self.config,mono_ns=lambda:mono[0],wall_ns=lambda:wall[0],boot=lambda:'CPU_BOOT')
        proof=authority.dispatch('/clock',board.challenge());mono[0]+=1_000_000;wall[0]+=1_000_000
        guard=board.accept(proof)
        self.assertEqual(guard.check(self.config)['pc_clock_id'],authority.clock.id)
        with self.assertRaises(ValueError):authority.dispatch('/clock',board.challenge())
    def test_real_clock_receipt_body_can_publish_signed_preparation(self):
        authority=PreparationAuthority(self.root)
        clock=hardware_module(self.declaration,'clock')
        mono=[100_000_000_000];wall=[int(datetime(2021,11,19,tzinfo=timezone.utc).timestamp()*1e9)]
        board=clock.BoardClockHandshake(self.config,mono_ns=lambda:mono[0],wall_ns=lambda:wall[0],boot=lambda:'CPU_BOOT')
        answer=authority.dispatch('/clock',board.challenge())
        mono[0]+=1_000_000;wall[0]+=1_000_000
        guard=board.accept(answer)
        receipt=guard.receipt(self.config)
        self.assertNotIn('mac',receipt['proof'])
        status=dict(authority.binding,state='BOARD_PREPARED',requests=0,commits=0,pending=False,poisoned=False,
            error=None,neural_connections=0,service_alive=True,clock_policy=receipt['policy'],clock_proof_sha256=receipt['proof_sha256'])
        body=dict(schema='flyvis-camera-retained-prepared/v1',binding=authority.binding,
            preparation_receipt={},clock_receipt=receipt,status=status)
        packet=authority.helpers.sign(body,self.config['control_key'])
        # This test focuses on the real clock receipt; read20 validation is
        # independently covered by the delivered prepare tests.
        binding_module=hardware_module(self.declaration,'binding')
        with patch.object(binding_module,'validate_readonly_receipt',return_value={}):
            authority.dispatch('/prepared',packet)
            self.assertTrue(authority.prepared.is_set())
            verify_prepared_handoff(load(self.root/'hardware_handoff.json'),self.scope,self.root)
            altered=copy.deepcopy(packet);altered['body']['clock_receipt']['proof']['pc_clock_id']='00'*16
            from joint_camera_preparation import verify_prepared_packet
            with self.assertRaisesRegex(ValueError,'BAD_HMAC'):
                verify_prepared_packet(altered,self.declaration,self.scope,sha(self.root/'scope.json'))
    def test_guard_authentication_and_nonce_replay(self):
        authority=PreparationAuthority(self.root);helper=authority.helpers
        authority.dispatch('/clock',helper.sign(dict(schema='flyvis-clock-challenge/v1',binding=authority.binding,
            nonce=uuid.uuid4().hex),'31'*32))
        packet=helper.sign(dict(schema='flyvis-pc-clock-check/v1',binding=authority.binding,nonce='42'*16),'31'*32)
        response=helper.verified(authority.dispatch('/guard',packet),'31'*32)
        self.assertTrue(response['ok']);self.assertEqual(response['pc_clock_id'],authority.clock.id)
        with self.assertRaises(ValueError):authority.dispatch('/guard',packet)
    def test_old_run_bad_mac_and_unknown_path_cannot_prepare(self):
        authority=PreparationAuthority(self.root)
        packet=authority.helpers.sign(dict(schema='flyvis-pc-clock-check/v1',binding=dict(authority.binding,run_id='OLD'),nonce='42'*16),'31'*32)
        for path in ('/guard','/anything'):
            with self.assertRaises(ValueError):authority.dispatch(path,packet)
        packet['mac']='00'*32
        with self.assertRaises(ValueError):authority.dispatch('/guard',packet)
        self.assertFalse(authority.prepared.is_set());self.assertFalse((self.root/'hardware_handoff.json').exists())
    def test_declaration_change_is_rejected_before_any_listener(self):
        write(self.root/'HARDWARE_DECLARATION.json',dict(self.declaration,run_id='CHANGED'))
        with self.assertRaisesRegex(ValueError,'DECLARATION_CHANGED'):PreparationAuthority(self.root)
    def test_scope_requires_exactly_one_preparation_identity_pin(self):
        validate_scope(self.scope)
        for update in (dict(hardware_handoff_sha256='51'*32),dict(hardware_declaration_sha256=None)):
            with self.assertRaisesRegex(ValueError,'HANDOFF_PINS'):validate_scope(dict(self.scope,**update))
    def test_helper_namespace_isolated_when_control_client_bytes_identical(self):
        older=load(PACKAGE.parent/'camera_joint_service_20261016/templates/HARDWARE_HANDOFF_NOT_PREPARED.json')
        self.assertEqual(older['software_sha256']['a3camera/control_client.py'],self.declaration['software_sha256']['a3ready/control_client.py'])
        a=hardware_module(older,'control_client');b=hardware_module(self.declaration,'control_client')
        self.assertIsNot(a,b);self.assertNotEqual(a.__package__,b.__package__)
    def test_no_prepared_handoff_exists_from_declaration_alone(self):
        with self.assertRaises(FileNotFoundError):verify_prepared_handoff(self.declaration,self.scope,self.root)
    def test_pc_clock_failure_does_not_answer_or_publish_ready(self):
        authority=PreparationAuthority(self.root,clock=SimpleNamespace(check=lambda:(_ for _ in ()).throw(ValueError('CLOCK_JUMP'))))
        with self.assertRaisesRegex(ValueError,'CLOCK_JUMP'):authority.dispatch('/clock',{})
        self.assertFalse(authority.prepared.is_set());self.assertFalse((self.root/'hardware_handoff.json').exists())


if __name__=='__main__':unittest.main()
