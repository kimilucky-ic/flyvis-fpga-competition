"""Startup lifetime regression using the original clock helper and fake time.

No GPU, camera, socket, board service, or register access is needed.
"""
from datetime import datetime,timedelta,timezone
import unittest
from unittest.mock import patch
import uuid

from live_protocol import HERE,load,sha,write
from joint_camera_control import hardware_module
from joint_camera_preparation import PreparationAuthority,clock_binding
from joint_camera_protocol import validate_scope as real_validate_scope
import test_joint_camera_preparation as preparation_tests

OUT=HERE/'evidence/startup_clock_wait_20261017'


class ClockLifecycleTests(unittest.TestCase):
    def setUp(self):
        with patch('test_joint_camera_preparation.OUT',OUT/'fixtures'):
            preparation_tests.PreparationTests.setUp(self)
        self.wall=int(datetime.now(timezone.utc).timestamp()*1e9)
        self.mono=100_000_000_000
        self.scope['end_utc']=(datetime.fromtimestamp(self.wall/1e9,timezone.utc)+timedelta(seconds=900)).isoformat()
        write(self.root/'scope.json',self.scope)
        self.config=dict(clock_binding(self.declaration,self.scope,sha(self.root/'scope.json')),control_key='31'*32)
        write(self.root/'PRIVATE_CONFIG.json',self.config)
        self.clock_module=hardware_module(self.declaration,'clock')
        self.factories=0
        self.validation=patch('joint_camera_preparation.validate_scope',
            side_effect=lambda scope:real_validate_scope(scope,now=datetime.fromtimestamp(self.wall/1e9,timezone.utc)))
        self.validation.start();self.addCleanup(self.validation.stop)
        self.authority=PreparationAuthority(self.root)
        self.authority.clock_factory=self.make_clock

    def make_clock(self):
        self.factories+=1
        return self.clock_module.PCClockAuthority(mono_ns=lambda:self.mono,wall_ns=lambda:self.wall)

    def advance(self,seconds):
        delta=int(seconds*1e9);self.mono+=delta;self.wall+=delta

    def signed(self,schema='flyvis-clock-challenge/v1',**kw):
        body=dict(schema=schema,binding=self.authority.binding,nonce=uuid.uuid4().hex);body.update(kw)
        return self.authority.helpers.sign(body,self.config['control_key'])

    def start_clock(self):
        return self.authority.dispatch('/clock',self.signed())

    def test_old_eager_clock_reproduces_human_wait_expiry(self):
        original=self.make_clock();self.advance(301)
        with self.assertRaisesRegex(ValueError,'AUTHORITY_TOO_OLD'):original.check()
        self.assertIsNone(self.authority.clock)

    def test_wait_does_not_consume_authenticated_lifetime(self):
        self.advance(400)
        for _ in range(3):self.assertIsNone(self.authority.check())
        self.assertEqual(self.factories,0)
        self.assertFalse((self.root/'PC_CLOCK_AUTHORITY_STARTED.json').exists())
        self.start_clock();self.advance(56);self.authority.check()
        self.assertEqual(self.factories,1)
        record=load(self.root/'PC_CLOCK_AUTHORITY_STARTED.json')
        self.assertEqual(record['trigger'],'FIRST_AUTHENTICATED_CLOCK_CHALLENGE')
        self.assertFalse(record['automatic_refresh'])

    def test_actual_original_board_handshake_accepts_late_first_challenge(self):
        self.advance(400)
        ps=[5_000_000_000,int(datetime(2021,11,19,tzinfo=timezone.utc).timestamp()*1e9)]
        board=self.clock_module.BoardClockHandshake(self.config,mono_ns=lambda:ps[0],wall_ns=lambda:ps[1],boot=lambda:'CPU_BOOT')
        proof=self.authority.dispatch('/clock',board.challenge())
        ps[0]+=1_000_000;ps[1]+=1_000_000
        guard=board.accept(proof)
        self.assertEqual(guard.check(self.config)['pc_clock_id'],self.authority.clock.id)
        self.assertEqual(self.factories,1)

    def test_bad_mac_identity_or_nonce_cannot_start_lifetime(self):
        bad_mac=self.signed();bad_mac['mac']='00'*32
        for packet in (bad_mac,self.signed(binding=dict(self.authority.binding,run_id='OTHER')),
                       self.signed(nonce='bad'),self.signed(schema='unknown')):
            with self.subTest(packet=packet),self.assertRaises(ValueError):self.authority.dispatch('/clock',packet)
        self.assertIsNone(self.authority.clock);self.assertEqual(self.factories,0)

    def test_guard_or_preparation_without_clock_rejected(self):
        for path in ('/guard','/prepared'):
            with self.subTest(path=path),self.assertRaisesRegex(ValueError,'NOT_STARTED'):
                self.authority.dispatch(path,self.signed(schema='flyvis-pc-clock-check/v1'))
        self.assertEqual(self.factories,0)

    def test_absolute_scope_still_expires_before_first_challenge(self):
        self.advance(901)
        with self.assertRaisesRegex(ValueError,'SCOPE_EXPIRED'):self.start_clock()
        self.assertEqual(self.factories,0)

    def test_original_300_second_limit_no_refresh_first_error_retained(self):
        self.start_clock();clock_id=self.authority.clock.id;self.advance(301)
        with self.assertRaisesRegex(ValueError,'AUTHORITY_TOO_OLD'):self.authority.check()
        first=(self.root/'PC_CLOCK_FAILURE.json').read_bytes()
        record=load(self.root/'PC_CLOCK_FAILURE.json')
        self.assertEqual(record['pc_clock_id'],clock_id)
        self.assertEqual(record['authority_age_ns'],301_000_000_000)
        self.assertIn('AUTHORITY_TOO_OLD',record['error'])
        with self.assertRaisesRegex(ValueError,'REVOKED'):self.start_clock()
        self.assertEqual((self.root/'PC_CLOCK_FAILURE.json').read_bytes(),first)
        self.assertEqual(self.factories,1)

    def test_original_jump_and_reverse_guards_unchanged(self):
        for kind in ('jump','reverse'):
            with self.subTest(kind=kind):
                self.authority=PreparationAuthority(self.root);self.authority.clock_factory=self.make_clock
                self.start_clock()
                if kind=='jump':self.wall+=300_000_000
                else:self.mono-=1
                with self.assertRaisesRegex(ValueError,'WALL_CLOCK_JUMP' if kind=='jump' else 'REVERSED'):
                    self.authority.check()
                self.assertIsNotNone(self.authority.error)

    def test_guard_reuses_original_id_and_nonce_replay_still_rejected(self):
        self.start_clock();identity=self.authority.clock.id
        packet=self.signed(schema='flyvis-pc-clock-check/v1')
        response=self.authority.helpers.verified(self.authority.dispatch('/guard',packet),self.config['control_key'])
        self.assertEqual(response['pc_clock_id'],identity)
        with self.assertRaisesRegex(ValueError,'NONCE'):self.authority.dispatch('/guard',packet)
        self.assertEqual(self.factories,1)

    def test_diagnostic_write_failure_does_not_mask_clock_failure(self):
        self.start_clock();self.advance(301)
        with patch('joint_camera_preparation.write',side_effect=OSError('CPU_INJECTED_DISK_FAILURE')):
            with self.assertRaisesRegex(ValueError,'AUTHORITY_TOO_OLD'):self.authority.check()
        self.assertIsNotNone(self.authority.error)
        self.assertEqual(self.factories,1)

    def test_injected_clock_keeps_original_check_behavior(self):
        injected=self.make_clock();authority=PreparationAuthority(self.root,clock=injected)
        self.assertIs(authority.clock,injected)
        authority.check();self.advance(301)
        with self.assertRaisesRegex(ValueError,'AUTHORITY_TOO_OLD'):authority.check()
        self.assertEqual(self.factories,1)


if __name__=='__main__':unittest.main()
