import sys,unittest,tempfile,json,copy,types,os,contextlib,io,hashlib,zipfile
from pathlib import Path
sys.path.insert(0,r'C:/Users/hzy72/Documents/ChatGPT/fly/gui_v1')
from line11_ddr_bridge import RELEASE
sys.path.append(str(RELEASE/"bundle_r2"))
from ddr_acceptance import save_new
from line11_live_camera import CameraDdrSession
from line11_live_camera_board import verify_previous_owner,release_previous_after_reload,complete_normal_return
from test_line11_ddr_notebook import FixedNotebookTests
from types import SimpleNamespace as NS
HERE=Path(sys.path[0]);OUT=HERE/'evidence/normal_switch_20261022'
class NormalSwitchTests(unittest.TestCase):
 def session(self,root,n=461):
  s=object.__new__(CameraDdrSession);s.preparation_id='a'*32;s.count=n-1;s.last_state='b'*64;s.audit_chain='c'*64;s.state='FINISHED';s.error=None;s.capture=NS(error=None);s.flow_consumer=NS(error=None,state='COMPLETE',accepted=n,completed=n,last_binding={'full_state_sha256':s.last_state});s.window_stop_reason='WALL_60S';s.output=Path(root);s.closeout_proof=None;s.normal_end_ack=False;s.session_id='d'*32
  body=dict(op='audit',preparation_id=s.preparation_id,completed_steps=n,last_state_sha256=s.last_state,receipt_chain=s.audit_chain)
  return s,body
 def owner(self,n=461):
  mem=NS(base=0x100000,size=485*188416,slots=485,armed=True,released=False);mem.buffer=NS(freebuffer=lambda:self.events.append('free'))
  regs={0x10:4|32,0x14:n,0x18:0,0x24:0,4:mem.base,8:mem.base+mem.size,12:mem.slots,0x2c:int('a'*8,16)}
  control=NS(failed=False,_r=lambda r:regs[r]);pins={id(mem):mem};owner=dict(schema='line2-normal-owned-ddr/v1',run_id='a'*32,boot_id='boot',pid=123,memory=mem,control=control,pins=pins,completed_steps=n,proof=dict(status='NORMAL_RETURN_ACKED',preparation_id='a'*32,completed_steps=n),retired=False)
  return owner,regs
 def setUp(self):self.events=[]
 def test_pc_audit_then_ack_only(self):
  with tempfile.TemporaryDirectory(dir=OUT) as d:
   s,b=self.session(d);s.flow_consumer.state='READY';self.assertEqual(s.closeout(b)['status'],'AUDIT_PENDING');self.assertFalse(s.normal_end_ack)
   with self.assertRaisesRegex(ValueError,'ACK_BEFORE'):s.closeout(dict(b,op='ack'))
   s.flow_consumer.state='COMPLETE';self.assertEqual(s.closeout(b)['status'],'NORMAL_WINDOW_AUDITED');self.assertFalse(s.normal_end_ack)
   self.assertEqual(s.closeout(dict(b,op='ack'))['status'],'NORMAL_RETURN_ACKED');self.assertTrue(s.normal_end_ack)
   self.assertTrue((Path(d)/'NORMAL_CLOSEOUT.json').exists());self.assertTrue((Path(d)/'BOARD_RETURN_ACK.json').exists())
 def test_failed_stopped_wrong_identity_not_rearmed(self):
  for state,reason,error in [('FAILED','WALL_60S',None),('FINISHED','USER_STOP',None),('FINISHED','WALL_60S','disk failed')]:
   with tempfile.TemporaryDirectory(dir=OUT) as d:
    s,b=self.session(d);s.state=state;s.window_stop_reason=reason;s.flow_consumer.error=error
    with self.assertRaisesRegex(ValueError,'REQUIRES_SUCCESS'):s.closeout(b)
    self.assertFalse(s.normal_end_ack)
  with tempfile.TemporaryDirectory(dir=OUT) as d:
   s,b=self.session(d)
   with self.assertRaisesRegex(ValueError,'IDENTITY'):s.closeout(dict(b,preparation_id='x'*32))
 def test_disk_failure_before_ack_cannot_allow_switch(self):
  with tempfile.TemporaryDirectory(dir=OUT) as d:
   s,b=self.session(d);(Path(d)/'NORMAL_CLOSEOUT.json').write_text('existing')
   with self.assertRaises(FileExistsError):s.closeout(b)
   self.assertFalse(s.normal_end_ack)
 def test_full_and_partial_release_only_after_new_image(self):
  for n in (461,485):
   o,r=self.owner(n);verify_previous_owner(o,'boot',123)
   with self.assertRaisesRegex(RuntimeError,'RELOAD_NOT_FRESH'):release_previous_after_reload(o,o['control'])
   self.assertFalse(o['memory'].released)
   release_previous_after_reload(o,NS(_r=lambda a:0));self.assertTrue(o['memory'].released);self.assertTrue(o['retired']);self.assertTrue(o['control'].failed);self.assertEqual(o['pins'],{})
   with self.assertRaisesRegex(RuntimeError,'IDENTITY'):release_previous_after_reload(o,NS(_r=lambda a:0))
  self.assertEqual(self.events,['free','free'])
 def test_busy_fault_cookie_boot_pid_rejected_no_free(self):
  for address,val in [(0x10,1),(0x24,1),(0x14,12),(0x2c,0),(4,0)]:
   o,r=self.owner();r[address]=val
   with self.assertRaises(RuntimeError):verify_previous_owner(o,'boot',123)
  o,r=self.owner()
  with self.assertRaises(RuntimeError):verify_previous_owner(o,'differentboot',123)
  with self.assertRaises(RuntimeError):verify_previous_owner(o,'boot',124)
  self.assertEqual(self.events,[])
 def test_board_audit_pending_then_finish_no_neural_retry(self):
  with tempfile.TemporaryDirectory(dir=OUT) as d:
   s,b=self.session(d);o,r=self.owner();s.flow_consumer.state='READY'
   def post(route,data,mime):
    body=json.loads(data);reply=s.closeout(body)
    if reply['status']=='AUDIT_PENDING':s.flow_consumer.state='COMPLETE'
    return reply
   fakepins={id(o['memory']):o['memory']};module=types.ModuleType('ddr_memory');module._PINNED=fakepins
   from unittest.mock import patch
   result=dict(completed_steps=461,last_state_sha256=s.last_state,receipt_chain=s.audit_chain)
   with patch.dict(sys.modules,{'ddr_memory':module}):
    owner=complete_normal_return(o['control'],o['memory'],NS(post=post),dict(preparation_id=s.preparation_id),dict(boot_id='boot'),d,result,clock=lambda:0,sleep=lambda _:None)
   self.assertEqual(owner['proof']['status'],'NORMAL_RETURN_ACKED');self.assertTrue((Path(d)/'NORMAL_END.json').exists());self.assertFalse(o['memory'].released)
 def test_two_notebook_runs_same_namespace_new_scope_and_failure_stop(self):
  case=FixedNotebookTests('test_fixed_notebook_python38_single_cell_and_original_entry_once');case.setUp()
  try:
   first=case.scope;invoked=[]
   def execute(path,**kwargs):
    scope=case.scope;invoked.append(kwargs)
    if len(invoked)==2:self.assertEqual(kwargs['init_globals']['LINE2_PREVIOUS_COMPLETED_OWNER']['run_id'],first)
    return dict(LINE2_COMPLETED_OWNER=dict(schema='line2-normal-owned-ddr/v1',run_id=scope,proof=dict(status='NORMAL_RETURN_ACKED'),retired=False))
   case.run_entry(execute=execute);self.assertEqual(case.env['_line2_pure_fpga_attempt']['status'],'COMPLETED_AUDITED')
   with self.assertRaisesRegex(RuntimeError,'上一实验'):case.run_entry(execute=execute)
   case.scope='e'*32;case.config['preparation_id']=case.scope;case.session.preparation_id=case.scope;case.pack();case.run_entry(execute=execute)
   self.assertEqual(len(invoked),2);self.assertEqual(case.env['_line2_completed_owner']['run_id'],'e'*32)
   case.scope='d'*32;case.config['preparation_id']=case.scope;case.session.preparation_id=case.scope;case.pack()
   def fail(*a,**k):raise RuntimeError('in doubt simulated')
   with self.assertRaisesRegex(RuntimeError,'in doubt'):case.run_entry(execute=fail)
   with self.assertRaisesRegex(RuntimeError,'未正常收尾'):case.run_entry(execute=execute)
   self.assertEqual(len(invoked),2)
  finally:case.doCleanups()
if __name__=='__main__':
 suite=unittest.defaultTestLoader.loadTestsFromTestCase(NormalSwitchTests)
 for name in ['test_fixed_notebook_python38_single_cell_and_original_entry_once','test_truncated_download_rejected_and_failure_attempt_retained']:
  suite.addTest(FixedNotebookTests(name))
 stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite);text=stream.getvalue();print(text);(OUT/'CPU_TEST.log').write_text(text,encoding='utf-8');(OUT/'RESULT.json').write_text(json.dumps(dict(evidence='CPU_IN_MEMORY_NO_BOARD_CAMERA_GPU_OR_SERVICE',tests=result.testsRun,failures=len(result.failures),errors=len(result.errors)),indent=2));sys.exit(not result.wasSuccessful())
