"""Focused off-board acceptance tests: no real allocator, PYNQ, GPU or sockets."""
import argparse,ast,gc,hashlib,json,shutil,struct,sys,threading,time,unittest,weakref
from pathlib import Path
from unittest.mock import patch
P=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--bundle',default='bundle_r2');ap.add_argument('--tag',default='cpu_tests_r1');args=ap.parse_args()
assert args.bundle.replace('_','').isalnum() and args.tag.replace('_','').isalnum()
B=P/args.bundle;OUT=P/args.tag;OUT.mkdir(exist_ok=False);sys.path.insert(0,str(B))
import cpu_replay as fake
import ddr_acceptance as acceptance
from ddr_control import STRIDE,N
from ddr_memory import OwnedDdr,_PINNED,pynq_allocator_and_barrier
from snapshot_records import rolling
from offline_check import verify,bit_header,plan


class Tests(unittest.TestCase):
    def make(self):return fake.session(B,OUT/self._testMethodName)
    def commit_all(self,s):
        s.start()
        for _ in range(3):s.produce_next()
    def test_complete_async_record_audit_and_explicit_release(self):
        s,m,b=self.make();s.start();s.produce_next();s.audit_next();held=s.display.acquire()
        s.produce_next();s.produce_next()
        self.assertEqual(s.audited,1);self.assertEqual(len(s.descriptors),3)
        s.audit_next();s.audit_next();s.display.release(held.frame_id)
        self.assertEqual(s.display.acquire().frame_id,2)
        r=s.finish();self.assertEqual((r['states_compared'],r['input_words_compared']),(137007,2163))
        self.assertEqual(r['display_frames_skipped'],1);self.assertFalse(r['board_result'])
        self.assertEqual(len(list(s.output.glob('record_*.bin'))),3)
        self.assertEqual(len(list(s.output.glob('receipt_*.json'))),3)
        self.assertEqual(b.events[:4],['allocate','fill','flush','dsb'])
        self.assertEqual(b.events.count('flush'),1)
        for i,event in enumerate(b.events):
            if isinstance(event,tuple) and event[0]=='invalidate':
                self.assertEqual(b.events[i-1],'dsb');self.assertEqual(b.events[i+1],'dsb')
                self.assertEqual(b.events[i+2][0],'copy');self.assertEqual(event[2]-event[1],STRIDE)
        self.assertFalse(b.flags.writeable);self.assertEqual(b.free_calls,0)
        s.release_verified_full();self.assertTrue(s.memory.released);self.assertEqual(b.free_calls,1)
        before=len(m.writes)
        with self.assertRaises(RuntimeError):s.produce_next()
        self.assertEqual(len(m.writes),before)

    def test_slow_cache_and_auditor_do_not_hold_producer(self):
        s,m,b=self.make();s.start();s.produce_next();entered=threading.Event();resume=threading.Event();errors=[]
        original=fake.View.invalidate
        def slow(view):
            entered.set()
            if not resume.wait(3):raise RuntimeError('test cache rendezvous')
            original(view)
        def audit():
            try:s.audit_next()
            except BaseException as ex:errors.append(str(ex))
        with patch.object(fake.View,'invalidate',slow):
            worker=threading.Thread(target=audit);worker.start();self.assertTrue(entered.wait(3))
            try:
                s.produce_next();s.produce_next()
                self.assertEqual(len(s.descriptors),3);self.assertEqual(s.audited,0);self.assertTrue(worker.is_alive())
            finally:resume.set();worker.join(3)
        self.assertFalse(worker.is_alive());self.assertEqual(errors,[])
        s.audit_next();s.audit_next();s.finish();s.release_verified_full()

    def test_allocator_bounds_shape_and_no_fallback(self):
        for change in ('unaligned','low','high','size','noncontiguous','coherent','dtype','ndim'):
            b=fake.Buffer(STRIDE);calls=[]
            if change=='unaligned':b.physical_address+=4
            if change=='low':b.physical_address=0
            if change=='high':b.physical_address=0x40000000
            if change=='size':b.nbytes-=1
            if change=='noncontiguous':b.flags.c_contiguous=False
            if change=='coherent':b.coherent=True
            if change=='dtype':b.dtype.itemsize=4
            if change=='ndim':b.ndim=2
            def allocate(**kw):calls.append(kw);return b
            with self.assertRaises(ValueError):OwnedDdr(allocate,b.barrier,1)
            self.assertEqual(len(calls),1);self.assertEqual(b.free_calls,1)

    def test_allocation_failure_no_neural_writes(self):
        inputs,states=plan(B);b=fake.Buffer(3*STRIDE);m=fake.MMIO(b,(B/'cpu_fixture_ddr.bin').read_bytes());calls=[]
        def allocate(**kw):calls.append(kw);raise MemoryError('CMA unavailable')
        with self.assertRaises(MemoryError):acceptance.AcceptanceSession(m,allocate,b.barrier,inputs,states,OUT/self._testMethodName)
        self.assertEqual(m.writes,[]);self.assertEqual(len(calls),1)

    def test_wrong_abi_or_existing_output_before_allocation(self):
        inputs,states=plan(B);b=fake.Buffer(3*STRIDE);m=fake.MMIO(b,(B/'cpu_fixture_ddr.bin').read_bytes());calls=[]
        def allocate(**kw):calls.append(kw);return b
        m.reg[0x38]^=1
        with self.assertRaises(RuntimeError):acceptance.AcceptanceSession(m,allocate,b.barrier,inputs,states,OUT/self._testMethodName)
        m.reg[0x38]^=1;existing=OUT/self._testMethodName;existing.mkdir()
        with self.assertRaises(FileExistsError):acceptance.AcceptanceSession(m,allocate,b.barrier,inputs,states,existing)
        self.assertEqual(calls,[]);self.assertEqual(m.writes,[])

    def test_already_used_candidate_no_restore_or_allocation(self):
        inputs,states=plan(B);b=fake.Buffer(3*STRIDE);m=fake.MMIO(b,(B/'cpu_fixture_ddr.bin').read_bytes());m.reg[0x14]=1
        def allocate(**kw):raise AssertionError('must not allocate')
        with self.assertRaises(RuntimeError):acceptance.AcceptanceSession(m,allocate,b.barrier,inputs,states,OUT/self._testMethodName)
        self.assertEqual(m.writes,[])

    def test_unknown_step_timeout_retains_allocation_and_forbids_retry(self):
        s,m,b=self.make();s.start();m.hang=True
        with self.assertRaises(TimeoutError):s.produce_next(timeout=0)
        writes=len(m.writes)
        with self.assertRaises(RuntimeError):s.produce_next()
        with self.assertRaises(RuntimeError):s.start()
        with self.assertRaises(RuntimeError):s.release_verified_full()
        self.assertEqual(len(m.writes),writes);self.assertTrue(s.failed)
        self.assertIn(id(s.memory),_PINNED);self.assertEqual(b.free_calls,0)

    def test_cache_failure_stops_without_free(self):
        s,m,b=self.make();self.commit_all(s);b.invalidate_error=True
        with self.assertRaises(OSError):s.audit_next()
        self.assertTrue(s.failed);self.assertEqual(b.free_calls,0);self.assertIn(id(s.memory),_PINNED)
        self.assertTrue((s.output/'STOP.json').exists())

    def test_stale_cache_cannot_be_accepted(self):
        s,m,b=self.make();self.commit_all(s);b.skip_invalidate=True
        with self.assertRaises(ValueError):s.audit_next()
        self.assertEqual(s.audited,0);self.assertEqual(b.free_calls,0)
        self.assertTrue((s.output/'record_000000.bin').exists())

    def test_last_neuron_one_bit_error_even_with_correct_record_checksum(self):
        s,m,b=self.make();s.start();s.produce_next()
        b.ddr[4096+4*(N-1)]^=1
        struct.pack_into('<I',b.ddr,52,rolling(b.ddr[4096:4096+N*4]))
        with self.assertRaises(RuntimeError):s.audit_next()
        check=json.loads((s.output/'compare_000000.json').read_text())
        self.assertEqual(check['words'],45669);self.assertEqual(check['mismatch_words'],1)
        self.assertEqual(check['first_mismatches'][0]['global_id'],45668)
        writes=len(m.writes)
        with self.assertRaises(RuntimeError):s.produce_next()
        self.assertEqual(len(m.writes),writes);self.assertEqual(b.free_calls,0)

    def test_actual_input_mismatch_even_with_updated_record_checksum(self):
        s,m,b=self.make();s.start();s.produce_next();b.ddr[128]^=1
        struct.pack_into('<I',b.ddr,48,rolling(b.ddr[128:128+2884]))
        with self.assertRaises(RuntimeError):s.audit_next()
        check=json.loads((s.output/'compare_000000.json').read_text())
        self.assertFalse(check['input_exact']);self.assertTrue(s.failed)

    def test_descriptor_cycle_binding(self):
        s,m,b=self.make();s.start();m.wrong_cycles=True;s.produce_next()
        with self.assertRaises(RuntimeError):s.audit_next()
        self.assertFalse(json.loads((s.output/'compare_000000.json').read_text())['descriptor_cycles_exact'])

    def test_disk_failure_preserves_ddr_and_original_error(self):
        s,m,b=self.make();s.start();s.produce_next()
        with patch.object(acceptance,'write_new',side_effect=OSError('disk full')):
            with self.assertRaisesRegex(OSError,'disk full'):s.audit_next()
        self.assertTrue(s.failed);self.assertEqual(b.free_calls,0);self.assertEqual(s.audited,0)
        self.assertEqual(bytes(b.ddr[:STRIDE]),(B/'cpu_fixture_ddr.bin').read_bytes()[:STRIDE])

    def test_missing_audit_receipt_prevents_finish_and_free(self):
        s,m,b=self.make();self.commit_all(s);s.audit_next();s.audit_next()
        with self.assertRaises(RuntimeError):s.finish()
        with self.assertRaises(RuntimeError):s.release_verified_full()
        self.assertEqual(b.free_calls,0)

    def test_final_hardware_count_failure_stops(self):
        s,m,b=self.make();self.commit_all(s)
        for _ in range(3):s.audit_next()
        m.reg[0x14]=2
        with self.assertRaises(RuntimeError):s.finish()
        self.assertTrue(s.failed);self.assertEqual(b.free_calls,0)

    def test_armed_owner_survives_lost_caller_reference(self):
        b=fake.Buffer(STRIDE);lease=OwnedDdr(lambda **kw:b,b.barrier,1);lease.pin_before_configure()
        ref=weakref.ref(lease);del lease;gc.collect()
        self.assertIsNotNone(ref());self.assertEqual(b.free_calls,0)

    def test_target_binding_default_denied_and_python38_syntax(self):
        before='pynq' in sys.modules
        with self.assertRaises(RuntimeError):pynq_allocator_and_barrier(OUT/'must_not_be_created')
        self.assertFalse((OUT/'must_not_be_created').exists());self.assertEqual('pynq' in sys.modules,before)
        for f in B.glob('*.py'):ast.parse(f.read_text(encoding='utf-8'),filename=f.name,feature_version=(3,8))

    def test_package_corruption_and_independent_bit_parser(self):
        clone=OUT/'tampered_bundle';shutil.copytree(B,clone)
        f=clone/'flyvis_ddr.bit';raw=f.read_bytes();changed=bytearray(raw);changed[-1]^=1;f.write_bytes(changed)
        with self.assertRaises(ValueError):verify(clone)
        manifest=json.loads((clone/'release_manifest.json').read_text());manifest['flyvis_ddr.bit']['sha256']=hashlib.sha256(changed).hexdigest()
        (clone/'release_manifest.json').write_text(json.dumps(manifest),encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'Wrong release BIT/HWH'):verify(clone)
        with self.assertRaises(ValueError):bit_header(raw[:-1])
        with self.assertRaises(ValueError):bit_header(b'wrong')


if __name__=='__main__':
    start=time.monotonic();result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    value=dict(status='PASS_OFFLINE_RELEASE_CPU_CONTRACT_ONLY' if result.wasSuccessful() else 'FAIL',bundle=args.bundle,tests=result.testsRun,
        failures=len(result.failures),errors=len(result.errors),seconds=time.monotonic()-start,board_operations=0,GPU_operations=0,
        pynq_imported='pynq' in sys.modules,neural_reference='independent serialized binary32 CPU oracle; fake device outputs saved RTL fixture',
        bundle_manifest_sha256=hashlib.sha256((B/'release_manifest.json').read_bytes()).hexdigest(),
        test_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (P/('CPU_RESULT_'+args.tag+'.json')).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(value,indent=2));raise SystemExit(0 if result.wasSuccessful() else 1)
