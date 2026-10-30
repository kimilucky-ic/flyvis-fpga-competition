"""CPU fault injection only. No hardware/network calls or neural recomputation."""
import sys,json,time,threading,tempfile,unittest,os,zipfile
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace
P=Path(__file__).resolve().parents[1];sys.path.insert(0,str(P/'bundle'))
import batch_records,ram_records,record_worker
from batch_records import BatchRecords
from record_worker import RecordWorker
from live_transport import Uploader
from live_protocol import sha
STRIDE=188416
source=P.parent/'ov5640_live_v261_20261026/pc/rounds/cfc66b09bad15b5aab478d8317c618d1/records'
# Actual saved complete payload, byte preservation fixture (not a neural run).
PAYLOAD=(source/'000000.packet').read_bytes()[-STRIDE:]
class Tests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(dir=P/'evidence');self.root=Path(self.tmp.name);self.j=None
 def tearDown(self):
  ram_records.CURRENT=None
  if self.j and self.j.thread:
   self.j.finished.set();self.j.thread.join(2);self.assertFalse(self.j.thread.is_alive())
  self.tmp.cleanup()
 def make(self,**kw):
  self.j=BatchRecords(self.root,**kw);self.j.start();ram_records.CURRENT=self.j;return self.j
 def add(self,k):
  data=k.to_bytes(4,'little')+PAYLOAD
  self.j.put(self.root/('capture/bound/%06d/PREPARED.bin'%k),PAYLOAD[128:3012])
  self.j.put(self.root/('transport/%06d.packet'%k),data);return data
 def wait(self,fn):
  end=time.monotonic()+3
  while not fn():
   self.assertLess(time.monotonic(),end);time.sleep(.005)
 def test_slow_file_sync_does_not_stop_pack_or_upload(self):
  j=self.make(batch_steps=16);gate=threading.Event();entered=threading.Event();real=os.fsync
  def slow(fd):
   if threading.current_thread().name=='line11-batch-save' and not entered.is_set():
    entered.set();assert gate.wait(3)
   real(fd)
  sent=[]
  def send(c,route,data):
   k=int.from_bytes(data[:4],'little');sent.append(k);return dict(step_id=k,sha256=sha(data),durable=True)
  u=Uploader(self.root,{},send=send);packets=[];w=None
  def packed(snapshot,k,*args):return k.to_bytes(4,'little')+snapshot.last_record_bytes
  try:
   with patch('batch_records.os.fsync',slow),patch('record_worker.packet_from_committed',packed):
    w=RecordWorker(self.root,{}, {},packets,uploader=u)
    for k in range(32):
     d=self.root/('capture/bound/%06d'%k)
     j.put(d/'PREPARED.bin',PAYLOAD[128:3012]);j.put(d/'COMMITTED.bin',PAYLOAD)
     b=SimpleNamespace(failed=False,last_record_bytes=PAYLOAD,binding=SimpleNamespace(failed=False,next=k+1,last_committed=(None,None,{},{})))
     w.submit(b,k,'previous',{}, {})
    self.assertTrue(entered.wait(3));self.wait(lambda:w.done==32)
    self.assertEqual(j.durable_prefix(),0);self.assertEqual(len(packets),32)
    for k in range(32):self.assertTrue(u.attempt())
    self.assertEqual(sent,list(range(32)));self.assertTrue(u.wake.is_set())
    with self.assertRaises(RuntimeError):j.put(self.root/'transport/000000.packet',b'changed',True)
    gate.set();w.drain();j.drain();self.assertEqual(j.durable_prefix(),32)
    for k in range(32):self.assertEqual(j.get(self.root/('transport/%06d.packet'%k)),k.to_bytes(4,'little')+PAYLOAD)
  finally:
   gate.set()
   if w:w.finished.set();w.thread.join(3)
 def test_bounded_queue_backpressure_and_no_loss(self):
  j=self.make(batch_steps=1);gate=threading.Event();entered=threading.Event();original=j._persist
  def held(job):entered.set();assert gate.wait(3);original(job)
  result=[]
  with patch.object(j,'_persist',held):
   try:
    self.add(0);j.persist_completed(0);self.assertTrue(entered.wait(2))
    for k in (1,2):self.add(k);j.persist_completed(k)
    self.add(3)
    t=threading.Thread(target=lambda:(j.persist_completed(3),result.append(True)));t.start()
    time.sleep(.08);self.assertEqual(result,[]);self.assertEqual(j.queue.qsize(),2);self.assertEqual(j.durable_prefix(),0)
    gate.set();t.join(3);self.assertEqual(result,[True]);j.drain();self.assertEqual(j.durable_prefix(),4)
   finally:gate.set()
  self.assertLessEqual(j.peak_ram_bytes,j.limit)
 def test_failures_never_publish_or_release_or_retry(self):
  # Includes failure after rename: existing ZIP is evidence, NOT permission to ACK.
  for kind in ('write','fsync','rename','directory'):
   with self.subTest(kind=kind):
    sub=self.root/kind;sub.mkdir();j=BatchRecords(sub,batch_steps=1);self.j=j;ram_records.CURRENT=j;j.start()
    j.put(sub/'capture/bound/000000/PREPARED.bin',b'input');j.put(sub/'transport/000000.packet',PAYLOAD)
    target={'write':'batch_records.zipfile.ZipFile.writestr','fsync':'batch_records.os.fsync','rename':'batch_records.os.replace','directory':'batch_records.BatchRecords._sync_directory'}[kind]
    with patch(target,side_effect=OSError('injected '+kind)):
     j.persist_completed(0);self.wait(lambda:j.error is not None);j.thread.join(2)
    self.assertEqual(j.persisted_steps,0);self.assertEqual(j.get(sub/'transport/000000.packet'),PAYLOAD)
    self.assertIsNotNone(j.failed_job)
    for operation in (j.check,j.durable_prefix,j.flush,lambda:j.persist_completed(0)):
     with self.assertRaises(RuntimeError):operation()
    w=RecordWorker(sub,{}, {},[])
    with self.assertRaises(RuntimeError):w.check()
    w.finished.set();w.thread.join(2)
 def test_directory_barrier_before_watermark(self):
  j=self.make(batch_steps=1);gate=threading.Event();entered=threading.Event()
  def directory(path):entered.set();assert gate.wait(3)
  with patch.object(j,'_sync_directory',directory):
   try:
    self.add(0);j.persist_completed(0);self.assertTrue(entered.wait(2));self.assertEqual(j.durable_prefix(),0)
    self.assertTrue((self.root/'spool/000000_000000.zip').exists());gate.set();j.drain()
   finally:gate.set()
  self.assertEqual(j.durable_prefix(),1)
 def test_partial_tail_and_idempotent_drain(self):
  j=self.make();expected=[self.add(k) for k in range(19)]
  for k in range(19):j.persist_completed(k)
  j.drain();j.drain();self.assertEqual(j.durable_prefix(),19)
  self.assertEqual([(x['first_step'],x['last_step']) for x in j.batches],[(0,15),(16,18)])
  receipt=j.flush();self.assertEqual(receipt['persisted_steps'],19)
  for k,data in enumerate(expected):self.assertEqual(j.get(self.root/('transport/%06d.packet'%k)),data)
 def test_drain_timeout_sticky_even_if_io_later_finishes(self):
  j=self.make(batch_steps=1,wait_timeout=.1);gate=threading.Event();entered=threading.Event();original=j._persist
  def held(job):entered.set();assert gate.wait(3);original(job)
  with patch.object(j,'_persist',held):
   try:
    self.add(0);j.persist_completed(0);self.assertTrue(entered.wait(2))
    with self.assertRaises(TimeoutError):j.drain()
    gate.set();j.thread.join(2);self.assertEqual(j.persisted_steps,0)
    self.assertEqual(j.get(self.root/'transport/000000.packet'),b'\0'*4+PAYLOAD)
    with self.assertRaises(RuntimeError):j.flush()
   finally:gate.set()
 def test_queue_timeout_bounded_and_sticky(self):
  j=self.make(batch_steps=1,wait_timeout=.1);gate=threading.Event();entered=threading.Event();original=j._persist
  def held(job):entered.set();assert gate.wait(3);original(job)
  with patch.object(j,'_persist',held):
   try:
    self.add(0);j.persist_completed(0);self.assertTrue(entered.wait(2))
    for k in (1,2):self.add(k);j.persist_completed(k)
    self.add(3)
    with self.assertRaises(TimeoutError):j.persist_completed(3)
    gate.set();j.thread.join(2);self.assertEqual(j.persisted_steps,0);self.assertEqual(j.queue.qsize(),2)
    self.assertEqual(len(j.pending_keys),8)
   finally:gate.set()
 def test_memory_limit_and_sequence(self):
  j=self.make(limit=10)
  with self.assertRaises(MemoryError):self.add(0)
  self.assertEqual(j.bytes,0)
  with self.assertRaises(RuntimeError):j.persist_completed(2)
 def test_existing_archive_no_overwrite(self):
  j=self.make(batch_steps=1);p=self.root/'spool/000000_000000.zip';p.write_bytes(b'keep')
  self.add(0);j.persist_completed(0);self.wait(lambda:j.error is not None)
  self.assertEqual(p.read_bytes(),b'keep');self.assertEqual(j.persisted_steps,0)

if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
 (P/'evidence/FAULT_RESULT.json').write_text(json.dumps(dict(status='PASS_CPU_ONLY' if result.wasSuccessful() else 'FAIL',tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),board_actions=0,neural_recompute=False),indent=2))
 sys.exit(not result.wasSuccessful())
