"""CPU-only selection, frozen inputs and backend protocol preparation.

No sockets, GUI, neural inference, camera, CUDA or board operations.
"""
import ast
import copy
import hashlib
import io
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from urllib.parse import urlparse
import numpy as np
from frozen28_input import Frozen28Input, bind_joint_scope, joint_contract
from controlled_stimuli28 import ControlledStimuli28
from operator_selection import Selection, validate, command
from joint_camera_protocol import frame_check, validate_scope
from live_protocol import HERE


class Operator28Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=ControlledStimuli28(results_config=False)
        cls.ids=list(cls.source.conditions)

    def feed(self,cid=None):
        return Frozen28Input('a'*32,cid or self.ids[0],self.source)

    def test_all_28_conditions_both_backend_argv(self):
        for cid in self.ids:
            for backend in ('GPU_FPGA','FULL_FPGA'):
                v=validate(dict(backend=backend,input='scientific28',condition=cid),self.ids)
                argv=command(v,Path('STOP.json'))
                self.assertEqual(argv[-2:],['--scientific-condition',cid])
                self.assertNotIn('--capture',argv)

    def test_two_camera_backends_use_existing_entries(self):
        for backend in ('GPU_FPGA','FULL_FPGA'):
            v=validate(dict(backend=backend,input='camera',condition=None),self.ids)
            argv=command(v,Path('STOP.json'))
            self.assertNotIn('--scientific-condition',argv)
            self.assertTrue(any(n.endswith(('server.py','joint_camera_controller.py')) for n in argv))

    def test_reject_unknown_extra_fields_and_camera_condition(self):
        for v in [dict(backend='SIMULATED_PL',input='camera',condition=None),
                  dict(backend='FULL_FPGA',input='scientific28',condition='../ON60'),
                  dict(backend='FULL_FPGA',input='camera',condition=self.ids[0]),
                  dict(backend='GPU_FPGA',input='camera',condition=None,execute=True)]:
            with self.assertRaises(ValueError):validate(v,self.ids)

    def test_selection_busy_and_duplicate_fail_closed(self):
        with tempfile.TemporaryDirectory(dir=HERE/'evidence/operator28_20261021') as t:
            s=Selection(t,lambda:self.source);v=dict(backend='GPU_FPGA',input='scientific28',condition=self.ids[0])
            with self.assertRaisesRegex(ValueError,'STOP_AND_FINISH'):s.select(v,busy=True)
            self.assertFalse((Path(t)/'NEXT.json').exists())
            result=s.select(v)
            self.assertFalse(result['actual_execution'])
            with self.assertRaises(FileExistsError):s.select(v)

    def test_unmanaged_gui_cannot_switch_backend(self):
        with self.assertRaisesRegex(ValueError,'OPEN_FIXED'):Selection(None).select({})

    def test_all_real_inputs_and_pixel_identity(self):
        for cid in self.ids:
            f=self.feed(cid)
            for k in (0,200,400,484):
                p=f.for_step(k);s=frame_check(p,f.run,'controlled_animation')
                self.assertEqual(s['sequence'],k)
                self.assertEqual(s['relative_s'],k*.005)
                self.assertEqual(s['timestamp_kind'],'frozen_model_time_not_capture')
                np.testing.assert_array_equal(p['values'],self.source.conditions[cid]['input'][k])
                self.assertIsNone(s['received_utc'])

    def test_fixed_input_no_skip_and_no_implicit_advance(self):
        f=self.feed()
        for k in range(485):
            f.step=k
            self.assertEqual(f.freeze_for_step()['source']['sequence'],k)
        for k in (-1,485,1.5,True):
            with self.assertRaises(ValueError):f.for_step(k)

    def test_wrong_run_source_clock_and_input_rejected(self):
        f=self.feed();p=f.for_step(200)
        with self.assertRaises(ValueError):frame_check(p,'b'*32,'controlled_animation')
        with self.assertRaises(ValueError):frame_check(p,f.run,'real_windows_camera')
        bad=copy.deepcopy(p);bad['values'][0]=.123
        with self.assertRaises(ValueError):frame_check(bad,f.run,'controlled_animation')
        bad=copy.deepcopy(p);bad['source']['timestamp_kind']='Windows_receipt_not_sensor'
        with self.assertRaises(ValueError):frame_check(bad,f.run,'controlled_animation')

    def test_backend_profiles_explicit_and_not_equivalent(self):
        f=self.feed();a=f.binding('GPU_FPGA');b=f.binding('FULL_FPGA')
        self.assertEqual(a['input_raw_sha256'],b['input_raw_sha256'])
        self.assertEqual(a['initial_raw_sha256'],b['initial_raw_sha256'])
        self.assertNotEqual(a['numerical_profile'],b['numerical_profile'])
        self.assertFalse(a['cross_backend_bitwise_equivalence'])

    def test_joint_initial_quantizes_H_once_and_keeps_R(self):
        scope=dict(run_id='a'*32)
        bind_joint_scope(scope,self.ids[0]);c=joint_contract(scope)
        mixed,words,raw=c.initial()
        np.testing.assert_array_equal(mixed[c.r],raw[c.r])
        np.testing.assert_array_equal(mixed[c.h],c.decode(words))
        self.assertEqual(scope['max_steps'],485)
        self.assertIsNone(scope['run_duration_s'])
        self.assertEqual(scope['model']['initial_state_sha256'],
            self.source.pack['initial_state_assets']['original_bias_fp32']['file_sha256'])
        bad=copy.deepcopy(scope);bad['scientific_input']['input_raw_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'BINDING'):joint_contract(bad)

    def test_full_pl_issue_is_strictly_indexed_and_ends_485(self):
        from line11_live_camera import CameraDdrSession
        with tempfile.TemporaryDirectory(dir=HERE/'evidence/operator28_20261021') as t:
            s=CameraDdrSession(t,scientific_condition=self.ids[0],software_test=True)
            self.assertFalse(s.status()['result_valid'])
            self.assertEqual(s.status()['board_connection'],'NOT_CONNECTED')
            s.flow_consumer=SimpleNamespace(error=None);s.started_ns=s.clock()
            old=s.last_state
            for k in range(485):
                p=s.issue(k,old)
                self.assertFalse(p['stop']);self.assertEqual(p['step'],k)
                self.assertEqual(p['input_sha256'],hashlib.sha256(self.source.conditions[self.ids[0]]['input'][k].tobytes()).hexdigest())
            done=s.issue(485,old)
            self.assertTrue(done['stop']);self.assertEqual(done['reason'],'SCIENTIFIC_485_STEPS_COMPLETE')

    def test_full_pl_wrong_order_old_state_and_stop(self):
        from line11_live_camera import CameraDdrSession
        with tempfile.TemporaryDirectory(dir=HERE/'evidence/operator28_20261021') as t:
            s=CameraDdrSession(t,scientific_condition=self.ids[0],software_test=True)
            s.flow_consumer=SimpleNamespace(error=None);s.started_ns=s.clock()
            with self.assertRaises(ValueError):s.issue(1,s.last_state)
            with self.assertRaises(ValueError):s.issue(0,'0'*64)
            s.requested_stop=True
            self.assertEqual(s.issue(0,s.last_state)['reason'],'USER_STOP')

    def test_managed_full_pl_start_requires_prepared_identity_and_is_single_use(self):
        from line11_live_camera import CameraDdrSession
        with tempfile.TemporaryDirectory(dir=HERE/'evidence/operator28_20261021') as t:
            s=CameraDdrSession(t,scientific_condition=self.ids[0],software_test=True,require_gui_start=True)
            body=dict(preparation_id=s.preparation_id)
            with self.assertRaises(ValueError):s.start_compute(body)
            s.prepared_for_compute=True
            with self.assertRaises(ValueError):s.start_compute(dict(preparation_id='other'))
            self.assertTrue(s.status()['ready_to_start'])
            self.assertEqual(s.start_compute(body)['status'],'START_REQUESTED')
            self.assertTrue(s.gui_start.is_set())
            self.assertFalse(s.status()['ready_to_start'])
            with self.assertRaises(ValueError):s.start_compute(body)

    def test_notebook_export_one_cell_source_same_for_condition_changes(self):
        from line11_ddr_notebook import export_notebook
        with tempfile.TemporaryDirectory(dir=HERE/'evidence/operator28_20261021') as t:
            target=Path(t)
            from line11_ddr_plan import STARTUP_FILES
            for n in (*STARTUP_FILES,'line11_live_camera_board.py'):
                (target/n).write_bytes((HERE/n).read_bytes())
            p=export_notebook('http://192.168.2.89:8771',target,selectable_input=True)
            before=p.read_bytes();n=json.loads(before)
            self.assertEqual(len([c for c in n['cells'] if c['cell_type']=='code']),1)
            self.assertTrue(n['metadata']['flyvis_pure_fpga']['selectable_input'])
            ast.parse(n['metadata']['flyvis_pure_fpga']['source'],feature_version=(3,8))
            export_notebook('http://192.168.2.89:8771',target,selectable_input=True)
            self.assertEqual(p.read_bytes(),before)

    def test_actual_http_selection_handler_without_socket_or_gui(self):
        tree=ast.parse((HERE/'server.py').read_text(encoding='utf-8'))
        factory=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='handler_factory')
        handler=next(n for n in factory.body if isinstance(n,ast.ClassDef) and n.name=='Handler')
        post=next(n for n in handler.body if isinstance(n,ast.FunctionDef) and n.name=='do_POST')
        import os
        with tempfile.TemporaryDirectory(dir=HERE/'evidence/operator28_20261021') as t:
            root=Path(t);selection=Selection(root,lambda:self.source)
            replies=[]
            raw=json.dumps(dict(backend='FULL_FPGA',input='scientific28',condition=self.ids[0])).encode()
            fake=SimpleNamespace(path='/api/operator-selection',client_address=('127.0.0.1',1),
                headers={'Content-Length':str(len(raw)),'Content-Type':'application/json','Origin':'http://127.0.0.1:8771'},
                rfile=io.BytesIO(raw),connection=SimpleNamespace(settimeout=lambda n:None),
                server=SimpleNamespace(server_port=8771),send=lambda v,status=200:replies.append((v,status)))
            from joint_camera_bridge import JointCameraBridge
            env=dict(operator=selection,joint=JointCameraBridge(),joint_workspace=None,joint_session_path=None,line11_stream=None,urlparse=urlparse,json=json,Path=Path,os=os)
            exec(compile(ast.Module(body=[post],type_ignores=[]),'ACTUAL_SELECTION_POST','exec'),env)
            with patch.dict(os.environ,FLYVIS_OPERATOR_STOP=str(root/'STOP.json')):
                env['do_POST'](fake)
            self.assertEqual(replies[0][1],200)
            self.assertTrue((root/'STOP.json').exists())
            self.assertEqual(json.loads((root/'NEXT.json').read_text())['condition'],self.ids[0])
            # Cross-origin requests cannot consume a new selection or touch a device.
            fake.headers['Origin']='http://other.invalid';fake.rfile=io.BytesIO(raw)
            env['do_POST'](fake)
            self.assertEqual(replies[-1][1],409)

    def test_scientific_snapshot_never_uses_camera_latency_clock(self):
        import joint_camera_bridge
        source=(HERE/'joint_camera_bridge.py').read_text(encoding='utf-8')
        self.assertIn("if self.scope.get('scientific_input') else latency_sample",source)
        self.assertIn('capture-to-display latency NOT_APPLICABLE',source)

    def test_fixed_source_close_handshake_has_no_duplicate_import_or_camera(self):
        import threading
        from joint_camera_bridge import JointCameraBridge
        with tempfile.TemporaryDirectory(dir=HERE/'evidence/operator28_20261021') as t:
            b=JointCameraBridge();b.root=Path(t)
            b.scope=dict(run_id='a'*32,scientific_input={'fixture':True})
            b.input_client=SimpleNamespace(call=lambda *a:dict(committed_steps=485,capture_close_requested=True))
            with patch('frozen28_input.Frozen28Input',side_effect=AssertionError('Duplicate frozen input import')):
                b.capture()
            end=json.loads((b.root/'camera_capture.json').read_text())
            self.assertTrue(end['closed']);self.assertFalse(end['camera_opened'])
            self.assertEqual(end['frames_delivered'],485)
            self.assertEqual(end['source_kind'],'controlled_animation')

    def test_board_sources_compile_on_pynq_python38(self):
        for name in ('joint_camera_repeat_board.py','joint_camera_clock_wait.py',
                     'line11_live_camera_board.py'):
            ast.parse((HERE/name).read_text(encoding='utf-8'),feature_version=(3,8))

    def test_existing_joint_bundle_freezes_scientific485_scope(self):
        import time,uuid
        from joint_camera_bundle import build
        from joint_camera_fresh import MODE
        fresh=dict(mode=MODE,new_loads=1,new_resets=1,new_allocations=2,
            requests=0,commits=0,neural_listeners_started=0,boot_id=str(uuid.uuid4()),
            kernel_file='CPU_FIXTURE_KERNEL.json',src_address=0x10000000,dst_address=0x10100000)
        family=dict(family_id='b'*32,created_unix=time.time(),expires_unix=time.time()+600,
            max_runs=100,scientific_condition=self.ids[0])
        with tempfile.TemporaryDirectory(dir=HERE/'evidence/operator28_20261021') as t:
            root,archive=build(Path(t),cpu_fixture=True,fresh=fresh,minimal_compute=True,live5=True,repeat_family=family)
            scope=json.loads((root/'scope.json').read_text())
            config=json.loads((root/'PRIVATE_CONFIG.json').read_text())
            self.assertEqual(scope['max_steps'],config['max_steps'])
            self.assertEqual(scope['max_steps'],485)
            self.assertEqual(scope['source_kind'],'controlled_animation')
            self.assertEqual(scope['execution_authority'],'CPU_FIXTURE_ONLY')
            self.assertEqual(scope['initial_H_sha256'],config['initial_H_sha256'])
            approved=dict(scope,status='APPROVED_BY_HUMAN',human_authorization_reference='CPU_FORMAT_TEST_ONLY')
            validate_scope(approved,joint_contract(scope))
            bad=copy.deepcopy(approved);bad['max_steps']=486
            with self.assertRaises(ValueError):validate_scope(bad)


if __name__=='__main__':unittest.main()
