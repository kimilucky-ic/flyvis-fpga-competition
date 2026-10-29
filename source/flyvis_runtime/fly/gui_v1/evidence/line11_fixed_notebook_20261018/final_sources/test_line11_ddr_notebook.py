"""Fixed Notebook distribution only: in-memory HTTP, no sockets/devices/inference."""
import ast
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from urllib.parse import urlparse
import zipfile

import line11_ddr_notebook as fixed
from line11_ddr_plan import STARTUP_FILES


class FixedNotebookTests(unittest.TestCase):
    def setUp(self):
        cases = fixed.HERE/'evidence/line11_fixed_notebook_20261018/cpu_cases'
        cases.mkdir(parents=True, exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(prefix='notebook_', dir=cases)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.here = self.root/'pc'; self.here.mkdir()
        self.cwd = self.root/'board_files'; self.cwd.mkdir()
        for name in STARTUP_FILES:
            (self.here/name).write_bytes((fixed.HERE/name).read_bytes())
        path = fixed.export_notebook('http://192.168.2.89:8771', self.here)
        self.notebook = json.loads(path.read_bytes())
        self.entry = self.notebook['metadata']['flyvis_pure_fpga']
        self.scope = 'f'*32
        self.config = dict(schema='flyvis-line2-ddr-preparation/v1', preparation_id=self.scope,
                           url=self.entry['pc_origin'], total_steps=485,
                           release_manifest_sha256=self.entry['release_manifest_sha256'],
                           plan_manifest_sha256=self.entry['plan_manifest_sha256'],
                           startup_sha256=self.entry['startup_sha256'])
        self.path = self.here/'package.zip'
        self.session = SimpleNamespace(total_steps=485, seed=SimpleNamespace(plan_sha=None),
            state='WAITING_FIRST_STEP', preparation_id=self.scope, link_path=self.path,
            authenticate_preparation=lambda _:None)
        self.auth = 'Bearer '+self.entry['pairing_key']
        self.pack()
        self.env = {}
        exec(compile(self.entry['source'], 'NOTEBOOK_CPU_TEST_ONLY', 'exec'), self.env)
        self.calls = []

    def pack(self, additions=None, bad_source=False):
        from line11_ddr_bridge import RELEASE
        with zipfile.ZipFile(self.path, 'w', zipfile.ZIP_DEFLATED) as z:
            z.writestr('PREPARATION.json', json.dumps(self.config))
            z.writestr('release_manifest.json', (RELEASE/'bundle_r2/release_manifest.json').read_bytes())
            z.writestr('RUN_PLAN.json', (fixed.HERE/'evidence/line11_ddr485_on60_20261018/plan/RUN_PLAN.json').read_bytes())
            for i, name in enumerate(STARTUP_FILES):
                raw = (self.here/name).read_bytes()
                z.writestr(name, raw+b'\n# changed' if bad_source and i==0 else raw)
            for name, raw in (additions or {}).items():
                z.writestr(name, raw)

    def transport(self, req, timeout):
        self.assertEqual(req.full_url, self.entry['pc_origin']+fixed.ROUTE)
        body = json.loads(req.data)
        self.calls.append(body['op'])
        reply = fixed.notebook_bundle(self.session, req.get_header('Authorization'), body, self.here)
        return io.BytesIO(reply if isinstance(reply, bytes) else json.dumps(reply).encode())

    def run_entry(self, answer='准备', transport=None, execute=None):
        previous = Path.cwd()
        os.chdir(self.cwd)
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                return self.env['run'](self.entry, self.env, transport or self.transport,
                                       lambda _:answer, execute or (lambda *a, **k:None))
        finally:
            os.chdir(previous)

    def test_fixed_notebook_python38_single_cell_and_original_entry_once(self):
        cells = [c for c in self.notebook['cells'] if c['cell_type']=='code']
        self.assertEqual(len(cells), 1)
        ast.parse(''.join(cells[0]['source']), feature_version=(3,8))
        ast.parse(self.entry['source'], feature_version=(3,8))
        invoked=[]
        self.run_entry(execute=lambda *args, **kwargs:invoked.append((args,kwargs)))
        self.assertEqual(self.calls, ['manifest','package'])
        self.assertEqual(len(invoked), 1)
        self.assertTrue(invoked[0][0][0].endswith('line11_ddr_board.py'))
        self.assertEqual(invoked[0][1], {'run_name':'__main__'})
        with self.assertRaisesRegex(RuntimeError, '本内核已经尝试'):
            self.run_entry()
        self.assertEqual(self.calls, ['manifest','package'])

    def test_wrong_pairing_and_closed_scope_rejected_without_poisoning(self):
        with self.assertRaisesRegex(ValueError, 'UNAUTHORIZED'):
            fixed.notebook_bundle(self.session, 'Bearer wrong', {'op':'manifest'}, self.here)
        for state in ('FINISHED','FAILED','RECEIVING'):
            self.session.state=state
            with self.assertRaisesRegex(ValueError, 'CONSUMED_OR_CLOSED'):
                fixed.notebook_bundle(self.session,self.auth,{'op':'manifest'},self.here)
            self.assertEqual(self.session.state,state)

    def test_GPU_other_steps_camera_or_stale_download_rejected(self):
        with self.assertRaisesRegex(ValueError, 'START_PURE_FPGA'):
            fixed.notebook_bundle(None,self.auth,{'op':'manifest'},self.here)
        self.session.total_steps=32
        with self.assertRaisesRegex(ValueError, 'ONLY_FIXED_ON60'):
            fixed.notebook_bundle(self.session,self.auth,{'op':'manifest'},self.here)
        self.session.total_steps=485;self.session.seed.plan_sha='0'*64
        with self.assertRaisesRegex(ValueError, 'ONLY_FIXED_ON60'):
            fixed.notebook_bundle(self.session,self.auth,{'op':'manifest'},self.here)
        self.session.seed.plan_sha=None
        with self.assertRaisesRegex(ValueError, 'MISMATCH'):
            fixed.notebook_bundle(self.session,self.auth,{'op':'package','preparation_id':'0'*32},self.here)

    def test_cancel_does_not_download_or_attempt_hardware(self):
        with self.assertRaisesRegex(RuntimeError, '已取消'):
            self.run_entry(answer='取消')
        self.assertEqual(self.calls,['manifest'])
        self.assertFalse(list(self.cwd.iterdir()))
        self.assertNotIn('_line2_pure_fpga_attempt',self.env)

    def test_changed_program_and_unsafe_archive_rejected_before_execution(self):
        self.pack(bad_source=True)
        with self.assertRaisesRegex(RuntimeError, '板端程序改变'):
            self.run_entry(execute=lambda *a,**k:self.fail('must not execute'))
        self.assertFalse((self.cwd/('LINE11_DDR_'+self.scope)).exists())
        # Separate simulated board directory; keep corrupt download intact.
        self.cwd=self.root/'board_unsafe';self.cwd.mkdir()
        self.pack({'../escape':'no'})
        with self.assertRaisesRegex(RuntimeError, '不安全'):
            self.run_entry(execute=lambda *a,**k:self.fail('must not execute'))
        self.assertFalse((self.root/'escape').exists())

    def test_truncated_download_rejected_and_failure_attempt_retained(self):
        def truncated(req,timeout):
            body=json.loads(req.data)
            if body['op']=='package':
                return io.BytesIO(self.path.read_bytes()[:-1])
            return self.transport(req,timeout)
        with self.assertRaisesRegex(RuntimeError, '不完整或SHA'):
            self.run_entry(transport=truncated,execute=lambda *a,**k:self.fail('must not execute'))
        self.assertTrue(list(self.cwd.glob('*.zip')))
        self.cwd=self.root/'board_execute_failure';self.cwd.mkdir()
        def fail_execute(*a,**k):raise RuntimeError('original board entry rejected')
        with self.assertRaisesRegex(RuntimeError, 'original board entry'):
            self.run_entry(execute=fail_execute)
        self.assertIn('_line2_pure_fpga_attempt',self.env)
        with self.assertRaisesRegex(RuntimeError, '本内核已经尝试'):
            self.run_entry()

    def test_actual_POST_route_in_memory_with_no_GUI_factory_or_socket(self):
        # Reuse the actual changed method, avoiding GUI constructors and listeners.
        tree=ast.parse((fixed.HERE/'server.py').read_text(encoding='utf-8'))
        node=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='do_POST')
        glob={'urlparse':urlparse,'json':json,'line11_stream':self.session}
        exec(compile(ast.Module(body=[node],type_ignores=[]),'ACTUAL_SERVER_POST_CPU_ONLY','exec'),glob)
        raw=json.dumps({'op':'manifest'}).encode()
        captured=[]
        handler=SimpleNamespace(path=fixed.ROUTE,client_address=('192.0.2.99',123),
            headers={'Content-Length':str(len(raw)),'Content-Type':'application/json','Authorization':self.auth},
            connection=SimpleNamespace(settimeout=lambda _:None),rfile=io.BytesIO(raw),
            send=lambda *a,**k:captured.append((a,k)))
        original=fixed.notebook_bundle
        with patch.object(fixed,'notebook_bundle',side_effect=lambda s,a,b:original(s,a,b,self.here)):
            glob['do_POST'](handler)
            self.assertEqual(captured[0][0][0]['preparation_id'],self.scope)
            handler.headers['Content-Length']='4097'
            glob['do_POST'](handler)
            self.assertEqual(captured[-1][1]['status'],409)
        self.assertEqual(self.session.state,'WAITING_FIRST_STEP')

    def test_original_485_package_consumed_by_fixed_notebook_without_execution(self):
        from line11_ddr_start import DdrGuiSession
        self.session=DdrGuiSession(self.here/'original_preparation',software_test=True,total_steps=485)
        self.session.package(self.entry['pc_origin'])
        self.scope=self.session.preparation_id
        invoked=[]
        self.run_entry(execute=lambda *a,**k:invoked.append(a[0]))
        self.assertEqual(len(invoked),1)
        directory=Path(invoked[0]).parent
        self.assertEqual((directory/'plan_expected_states.bin').stat().st_size,88597860)
        self.assertEqual((directory/'plan_inputs.bin').stat().st_size,1398740)
        self.assertEqual(self.session.state,'WAITING_FIRST_STEP')
        self.assertIsNone(self.session.seed.value)


if __name__=='__main__':
    unittest.main(verbosity=2)
