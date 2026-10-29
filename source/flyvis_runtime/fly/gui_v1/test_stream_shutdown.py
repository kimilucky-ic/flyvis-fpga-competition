"""CPU fault injection through the actual orchestration/cleanup, with no processes.

Original saved arrays are read-only test fixtures. The CPU stand-in DOES NOT
perform neural inference; temporary packets cannot pass the GUI CUDA validator.
"""
from contextlib import ExitStack
import copy
import json
import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import numpy as np
import stream_runtime as runtime
from live_protocol import HERE,load,Registry


class Shutdown(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry=Registry()
        source=HERE/'runtime/live/4ea30d875d004bcca1cf81c26da7b377/stream'
        cls.control=load(source/'control.json');cls.meta=load(source/'snapshots/000001.json')
        cls.source=load(source/'sources/000000.json');cls.png=(source/'sources/000000.png').read_bytes()
        cls.values=np.load(source/'sources/000000_hex.npy',allow_pickle=False)
        cls.flow=np.load(source/'snapshots/000001.npz',allow_pickle=False)['flow']
    def execute(self,folder,*,asset_failure=False,fsync_failure=False,full_before_compute=False,pending_selection=False,converter_exit=False,prepared_converter=False,prepared_close_failure=False):
        owner={};calls={'updates':0,'checks':0,'commits':0,'cuda_sync':0,'durable_packets':0}
        class Tensor:
            def init__(self,a):self.a=a
            def clone(self):return Tensor(self.a.copy())
            def detach(self):return self
            def cpu(self):return self
            def numpy(self):return self.a
        class Compute:
            def init__(self,*a,**k):pass
            def step(self,state,frame):calls['updates']+=1;return state
            def candidate_predicate(self,c):return np.isfinite(c.a).all()
            def validate_candidate(self,c):assert self.candidate_predicate(c);calls['checks']+=1
            def commit(self,c):calls['commits']+=1;return c
            def close(self):pass
            def info(self):return dict(actual_original_updates=calls['updates'],candidate_checks=calls['checks'],accepted_commits=calls['commits'],CPU_PROTOCOL_STAND_IN=True)
        class Probes:
            def init__(self,*a):pass
            def wrap(self,*a,**k):pass
            def close(self):pass
            def collect(self):pass
        class Audit:
            calls=0
            def init__(self,*a):pass
            def install(self):return self
            def close(self):pass
        class RPC:
            def init__(self,sid,handler):
                owner['hub']=handler.__self__;self.endpoint={'CPU_PROTOCOL_TEST_ONLY':True}
                c=copy.deepcopy(Shutdown.control);c['session_id']=sid;c['run_id']='c'*32;c['binding']['CPU_PROTOCOL_TEST_ONLY']=True
                if not pending_selection:
                    handler('bridge','start',c);handler('renderer','ready',None)
            def close(self):pass
        class Process:
            def init__(self,*a,**k):
                calls['converter_starts']=calls.get('converter_starts',0)+1
                if pending_selection:return
                import base64
                f=copy.deepcopy(Shutdown.source);f['run_id']='c'*32;f['relative_s']=0
                owner['hub'].dispatch('renderer','converted',dict(source=f,png=base64.b64encode(Shutdown.png).decode(),values=Shutdown.values.tolist(),transform=Shutdown.meta['spatial_transform']))
            def poll(self):return 1 if converter_exit else None
            def wait(self,**kw):calls['converter_waits']=calls.get('converter_waits',0)+1;return 0
        class Writer(runtime.EvidenceWriter):
            def reserve(self,kind,timeout=.1):
                if full_before_compute and kind=='snapshot':raise ValueError('EVIDENCE_BACKPRESSURE_BEFORE_COMPUTE')
                return super().reserve(kind,timeout)
            def close(self):
                super().close()
                if asset_failure:raise OSError('CPU_ASSET_FINALIZATION_FAILURE')
        class Prepared:
            def attach(self):
                calls['prepared_attaches']=calls.get('prepared_attaches',0)+1
                self.process=Process();return self.process,None
            def close(self):
                calls['prepared_closes']=calls.get('prepared_closes',0)+1
                self.process.wait()
                if prepared_close_failure:raise OSError('CPU_PREPARED_CLOSE_FAILED')
        def scope(*a):
            if 'hub' in owner:
                h=owner['hub'];h.bridge_at=h.renderer_at=time.monotonic()
                if pending_selection and not converter_exit:
                    self.assertEqual(calls.get('converter_starts'),1)
                    self.assertIsNone(h.control);self.assertEqual(h.last_source,-1)
                    raise ValueError('STREAM_STOP_REQUESTED')
                if h.computed_steps>=13:raise ValueError('STREAM_STOP_REQUESTED')
        def sync():calls['cuda_sync']+=1
        torch=SimpleNamespace(as_tensor=lambda a,**kw:Tensor(a),float32=np.float32,cuda=SimpleNamespace(synchronize=sync))
        oracle=SimpleNamespace(net=SimpleNamespace(),assert_weights_unchanged=lambda:None)
        decoder=SimpleNamespace(decoder=None,assert_weights_unchanged=lambda:None,decode=lambda *a,**kw:self.flow[None,None])
        original_encode=runtime.encode_packet
        def encode(packet):
            self.assertEqual(packet['durable_commit_steps'],packet['state_token'])
            saved=(folder/'stream/step_commits.jsonl').read_text().splitlines()
            self.assertEqual(len(saved),packet['state_token']);calls['durable_packets']+=1
            return original_encode(packet)
        with ExitStack() as stack:
            for key,value in dict(dependencies=lambda:None,LocalRPC=RPC,CombinedCheckedFull=Compute,CudaProbes=Probes,PackedDecoderAudit=Audit,EvidenceWriter=Writer).items():stack.enter_context(patch.object(runtime,key,value))
            stack.enter_context(patch('stream_runtime.subprocess.Popen',side_effect=AssertionError('must reuse prepared process'))
                if prepared_converter else patch('stream_runtime.subprocess.Popen',Process))
            stack.enter_context(patch.object(runtime,'encode_packet',encode))
            if fsync_failure:stack.enter_context(patch('stream_evidence.os.fsync',side_effect=OSError('CPU_FSYNC_FAILURE')))
            runtime._run_stream(folder,dict(session_id='s'*32,stream_observation_s=10),self.registry,oracle,decoder,torch,dict(type='cpu',CPU_PROTOCOL_TEST_ONLY=True),scope,
                Prepared() if prepared_converter else None)
        result=load(folder/'stream/result.json');rows=(folder/'stream/step_commits.jsonl').read_text().splitlines()
        self.assertTrue(result['CUDA_completed_before_stop_ack']);self.assertGreater(calls['cuda_sync'],0)
        return result,rows,calls
    def test_normal_stop_drains_partial_batch(self):
        with tempfile.TemporaryDirectory(dir=HERE/'runtime') as d:
            r,rows,c=self.execute(Path(d));self.assertTrue(r['success']);self.assertTrue(r['evidence_complete'])
            self.assertEqual((r['committed_steps'],r['computed_steps'],len(rows),c['checks']),(13,13,13,13))
            self.assertGreater(c['durable_packets'],0)
    def test_asset_close_failure_keeps_result_and_all_step_records(self):
        with tempfile.TemporaryDirectory(dir=HERE/'runtime') as d:
            r,rows,c=self.execute(Path(d),asset_failure=True)
            self.assertFalse(r['success']);self.assertFalse(r['evidence_complete']);self.assertIn('assets',r['cleanup_errors'])
            self.assertEqual(len(rows),c['commits']);self.assertEqual(r['committed_steps'],c['commits'])
    def test_fsync_failure_never_publicly_commits_private_candidate(self):
        with tempfile.TemporaryDirectory(dir=HERE/'runtime') as d:
            r,rows,c=self.execute(Path(d),fsync_failure=True)
            self.assertFalse(r['success']);self.assertFalse(r['evidence_complete']);self.assertEqual(r['committed_steps'],0)
            self.assertEqual(c['updates'],1);self.assertEqual(r['computed_steps'],1)
    def test_capacity_failure_occurs_before_any_neural_call(self):
        with tempfile.TemporaryDirectory(dir=HERE/'runtime') as d:
            r,rows,c=self.execute(Path(d),full_before_compute=True)
            self.assertFalse(r['success']);self.assertEqual(c['updates'],0);self.assertEqual(rows,[])

    def test_stop_before_input_selection_closes_prepared_converter_without_neural_steps(self):
        with tempfile.TemporaryDirectory(dir=HERE/'runtime') as d:
            r,rows,c=self.execute(Path(d),pending_selection=True)
            self.assertTrue(r['success']);self.assertIsNone(r['run_id'])
            self.assertEqual((c['updates'],c['commits'],len(rows)),(0,0,0))
            self.assertEqual(c['converter_waits'],1)

    def test_early_converter_exit_is_failure_and_never_starts_neural_steps(self):
        with tempfile.TemporaryDirectory(dir=HERE/'runtime') as d:
            r,rows,c=self.execute(Path(d),pending_selection=True,converter_exit=True)
            self.assertFalse(r['success']);self.assertEqual(r['reason'],'OFFICIAL_RENDERER_EXITED')
            self.assertEqual((c['updates'],c['commits'],len(rows)),(0,0,0))
            self.assertEqual(c['converter_waits'],1)

    def test_parallel_converter_is_adopted_without_a_second_process(self):
        with tempfile.TemporaryDirectory(dir=HERE/'runtime') as d:
            r,rows,c=self.execute(Path(d),prepared_converter=True)
            self.assertTrue(r['success']);self.assertEqual(len(rows),13)
            self.assertEqual((c['converter_starts'],c['prepared_attaches'],c['prepared_closes']),(1,1,1))

    def test_parallel_converter_stop_before_selection_has_no_private_candidate(self):
        with tempfile.TemporaryDirectory(dir=HERE/'runtime') as d:
            r,rows,c=self.execute(Path(d),prepared_converter=True,pending_selection=True)
            self.assertTrue(r['success']);self.assertEqual((c['updates'],len(rows)),(0,0))
            self.assertEqual(c['prepared_closes'],1)

    def test_parallel_converter_cleanup_failure_is_not_hidden_by_complete_steps(self):
        with tempfile.TemporaryDirectory(dir=HERE/'runtime') as d:
            r,rows,c=self.execute(Path(d),prepared_converter=True,prepared_close_failure=True)
            self.assertFalse(r['success']);self.assertIn('prepared_converter',r['cleanup_errors'])
            self.assertEqual(len(rows),13);self.assertEqual(c['prepared_closes'],1)

if __name__=='__main__':unittest.main()
