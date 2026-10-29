"""Administrative wait vs compute-time checks; no devices or listeners."""
from datetime import datetime,timedelta,timezone
import unittest
from joint_camera_clock_wait import PROFILE,WAIT_S,scoped_clock,compute_alive
from joint_camera_control import hardware_module
from live_protocol import HERE,load,sha

class WaitProfileTests(unittest.TestCase):
    def setUp(self):
        package=HERE.parent.parent/'fpga/flyvis-fpga/t4t5_neurononly_20261011/soc_a_20261012/camera_joint_ready_20261016'
        self.h=load(package/'templates/HARDWARE_HANDOFF_NOT_PREPARED.json')
        self.original=hardware_module(self.h,'clock')
        now=datetime.now(timezone.utc)
        self.c=dict(clock_wait_profile=PROFILE,clock_wait_s=WAIT_S,max_worker_s=300,max_steps=32,automatic_retry=False,
            run_id='11'*16,server_session='12'*16,boot_id='CPU_BOOT',scope_sha256='13'*32,plan_sha256='14'*32,
            listener_id='15'*16,start_utc=(now-timedelta(seconds=2)).isoformat(),end_utc=(now+timedelta(seconds=1798)).isoformat(),control_key='31'*32)
        self.pc=[100_000_000_000,int(now.timestamp()*1e9)]
        self.ps=[200_000_000_000,int(datetime(2021,11,19,tzinfo=timezone.utc).timestamp()*1e9)]

    def test_wait_over_300s_original_signed_handshake_and_PS_guard_still_valid(self):
        m=scoped_clock(self.original,self.c,self.c)
        authority=m.PCClockAuthority(mono_ns=lambda:self.pc[0],wall_ns=lambda:self.pc[1])
        for i in (0,1):self.pc[i]+=400_000_000_000
        authority.check()
        board=m.BoardClockHandshake(self.c,mono_ns=lambda:self.ps[0],wall_ns=lambda:self.ps[1],boot=lambda:'CPU_BOOT')
        proof=authority.answer(board.challenge(),self.c);guard=board.accept(proof)
        for t in (self.pc,self.ps):
            for i in (0,1):t[i]+=310_000_000_000
        authority.check();receipt=guard.receipt(self.c)
        self.assertEqual(receipt['max_proof_age_ns'],1800_000_000_000)
        self.assertEqual(receipt['pc_clock_id'],authority.id)
        self.assertEqual(m.JUMP_NS,self.original.JUMP_NS)
        self.assertEqual(m.RATE_PPM,self.original.RATE_PPM)

    def test_old_namespace_and_legacy_300s_policy_unchanged(self):
        m=scoped_clock(self.original,self.c,self.c)
        self.assertIsNot(m,self.original);self.assertEqual(self.original.MAX_AGE_NS,300_000_000_000)
        self.assertIs(scoped_clock(self.original,{},{}),self.original)
        original=self.original.PCClockAuthority(mono_ns=lambda:self.pc[0],wall_ns=lambda:self.pc[1])
        for i in (0,1):self.pc[i]+=301_000_000_000
        with self.assertRaisesRegex(ValueError,'AUTHORITY_TOO_OLD'):original.check()

    def test_jump_reverse_and_new_1800_limit_remain_fail_closed(self):
        for kind in ('jump','reverse','age'):
            m=scoped_clock(self.original,self.c,self.c)
            p=[100_000_000_000,self.pc[1]]
            a=m.PCClockAuthority(mono_ns=lambda:p[0],wall_ns=lambda:p[1])
            if kind=='jump':p[1]+=300_000_000
            elif kind=='reverse':p[0]-=1
            else:
                for i in (0,1):p[i]+=1801_000_000_000
            with self.subTest(kind=kind),self.assertRaises(ValueError):a.check()

    def test_bad_profile_or_relaxed_compute_scope_rejected(self):
        for field,value in (('clock_wait_s',3600),('max_worker_s',1800),('max_steps',485),('automatic_retry',True)):
            with self.subTest(field=field),self.assertRaises(ValueError):scoped_clock(self.original,dict(self.c,**{field:value}),self.c)

    def test_compute_limit_starts_on_manual_start_not_human_wait(self):
        self.assertTrue(compute_alive(None,900))
        self.assertTrue(compute_alive(900,1199.999))
        self.assertFalse(compute_alive(900,1200))
        self.assertFalse(compute_alive(900,899))

if __name__=='__main__':unittest.main()
