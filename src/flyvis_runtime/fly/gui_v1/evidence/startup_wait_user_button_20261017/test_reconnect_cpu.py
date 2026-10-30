import importlib.util,io,json,socket,sys,time,types,unittest
from datetime import datetime,timezone
from pathlib import Path
from unittest.mock import patch
P=Path(__file__).resolve().parent;G=P.parent.parent;sys.path.insert(0,str(G))
from live_protocol import load
from joint_camera_control import hardware_module
from joint_camera_clock_wait import scoped_clock
import reconnect_prestart as subject

class ReconnectTests(unittest.TestCase):
    def fixture(self,fail_sync=False):
        c=load(G/'runtime/joint_manual/c7612f01667b89a3ca0293138f77c8af/2050d74ea5eb4948b37c9c687ac2733f/PRIVATE_CONFIG.json')
        s=load(G/'runtime/joint_manual/c7612f01667b89a3ca0293138f77c8af/2050d74ea5eb4948b37c9c687ac2733f/scope.json')
        h=load(G/'runtime/joint_manual/c7612f01667b89a3ca0293138f77c8af/2050d74ea5eb4948b37c9c687ac2733f/HARDWARE_DECLARATION.json')
        c['control_key']='31'*32
        m=scoped_clock(hardware_module(h,'clock'),c,s)
        pc=[100_000_000_000,int((datetime.fromisoformat(c['start_utc']).timestamp()+60)*1e9)]
        ps=[200_000_000_000,int(datetime(2021,11,19,tzinfo=timezone.utc).timestamp()*1e9)]
        original=m.BoardClockHandshake
        make=lambda config:original(config,mono_ns=lambda:ps[0],wall_ns=lambda:ps[1],boot=lambda:c['boot_id'])
        authority=lambda:m.PCClockAuthority(mono_ns=lambda:pc[0],wall_ns=lambda:pc[1])
        first=authority();hand=make(c);old=hand.accept(first.answer(hand.challenge(),c))
        entries=[]
        class Journal:
            closed=False
            def add(self,n,raw):entries.append(n)
            def checkpoint(self,n):
                if fail_sync:raise OSError('CPU_FSYNC_FAILURE')
                entries.append(n)
        d=types.SimpleNamespace(requests=0,commits=0,pending=None,poisoned=False,committed={},
            evidence=types.SimpleNamespace(journal=Journal()),clock_guard=old,session_deadline=time.monotonic()+1000)
        import threading
        service=types.SimpleNamespace(config=c,driver=d,state='BOARD_PREPARED',error=None,identity=None,connections=0,
            inflight=False,listener=None,connection=None,neural_thread=None,thread=types.SimpleNamespace(is_alive=lambda:True),
            lock=threading.RLock(),clock_guard=old,clock_receipt=old.receipt(c),idle_deadline=time.monotonic()+1000)
        service.status=lambda nonce:dict(state=service.state,requests=0,commits=0)
        bundle=types.SimpleNamespace(config=c,driver=d,receipt={},clock_guard=old)
        current=authority();packets=[]
        def request(path,packet):
            packets.append(path)
            if path=='/clock':return current.answer(packet,c)
            body=m.verified(packet,c['control_key'])
            self.assertEqual(body['PC_prestart_reconnect']['prior_clock']['pc_clock_id'],first.id)
            self.assertEqual(body['clock_receipt']['pc_clock_id'],current.id)
            return m.sign(dict(ok=True,binding=old.fixed),c['control_key'])
        return bundle,service,m,make,request,entries,packets,old

    def test_current_prestart_reconnect_no_hardware_and_no_scope_extension(self):
        b,s,m,make,req,entries,calls,old=self.fixture();deadline=s.idle_deadline
        with patch.object(m,'BoardClockHandshake',make),patch('builtins.print'):
            subject.reconnect(b,s,s.config['run_id'],req)
        self.assertIsNot(s.clock_guard,old);self.assertIs(s.clock_guard,b.clock_guard)
        self.assertLessEqual(s.idle_deadline,deadline);self.assertEqual(calls,['/clock','/prepared'])
        self.assertEqual(entries,['PC_PRESTART_RECONNECT.json','PC_PRESTART_RECONNECT'])
        self.assertEqual((s.driver.requests,s.driver.commits),(0,0))

    def test_started_session_is_rejected_before_any_request(self):
        b,s,m,make,req,entries,calls,old=self.fixture();s.identity={'STARTED':True}
        with self.assertRaises(AssertionError):subject.reconnect(b,s,s.config['run_id'],req)
        self.assertEqual(calls,[]);self.assertEqual(entries,[]);self.assertIs(s.clock_guard,old)

    def test_failed_persistence_does_not_replace_guard_or_publish_prepared(self):
        b,s,m,make,req,entries,calls,old=self.fixture(True)
        with patch.object(m,'BoardClockHandshake',make),self.assertRaisesRegex(OSError,'CPU_FSYNC'):
            subject.reconnect(b,s,s.config['run_id'],req)
        self.assertIs(s.clock_guard,old);self.assertEqual(calls,['/clock'])

stream=io.StringIO();begin=time.perf_counter()
with patch.object(socket,'socket',side_effect=AssertionError('REAL_SOCKET_FORBIDDEN')):
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ReconnectTests))
record=dict(tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),elapsed_s=time.perf_counter()-begin,
    evidence_level='CPU_PRESTART_ONLY_CLOCK_RECONNECT_NO_HARDWARE',successful=result.wasSuccessful())
(P/'RECONNECT_CPU_RESULT.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf8')
(P/'RECONNECT_CPU_TESTS.log').write_text(stream.getvalue(),encoding='utf8')
print(json.dumps(record))
if not result.wasSuccessful():print(stream.getvalue())
sys.exit(0 if result.wasSuccessful() else 1)
