"""GUI-owned input selection; no camera, model, board or execution service calls."""
from copy import deepcopy
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import secrets
import sys
import threading
from types import ModuleType, SimpleNamespace
import uuid

from data_store import sha256, read_json
from phase3_adapter import VerifiedFiles
from workbench import MODES, require

SOURCE_KINDS = ('digital_verified_p0', 'interactive_digital', 'phone_camera')
PREPARATION_MANIFEST_SHA = '3732df799028cca136816f1f72b49828d34c04ee6b129635cf967a3baff933b5'


def utc():
    return datetime.now(timezone.utc).isoformat()


class PresentationBridge(VerifiedFiles):
    """Reuse ⑤'s sealed HTML/renderer and logging handler without starting its server."""
    def init__(self, root, runtime):
        super().init__()
        self.root = Path(root)
        self.check(self.root/'manifest.json', PREPARATION_MANIFEST_SHA)
        manifest = read_json(self.root/'manifest.json')
        names = ['acceptance.json', 'config.py', 'serve_phone.py', 'BACKEND_CONTRACT.md',
                 'web\\phone.html', 'web\\player.js', 'web\\style.css']
        for name in names:
            self.check(self.root/name, manifest['files'][name])
        require(read_json(self.root/'acceptance.json')['status'] ==
                'SOFTWARE_PREPARATION_PASS_REAL_CAPTURE_PENDING', 'Unexpected preparation evidence')
        # Import only the sealed standard-library configuration/logging module.
        # No camera_pipeline package import, capture module, torch or model import.
        namespace = '_gui_phone_preparation_' + uuid.uuid4().hex
        package = ModuleType(namespace); package.__path__ = [str(self.root)]
        sys.modules[namespace] = package
        spec = importlib.util.spec_from_file_location(namespace+'.serve_phone', self.root/'serve_phone.py')
        module = importlib.util.module_from_spec(spec); sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        self.handler = module.Handler
        self.state = SimpleNamespace(token=secrets.token_urlsafe(24), logs=Path(runtime)/'presentations',
                                     validation_only=True, sessions={}, guard=threading.Lock())

    def status(self):
        self.assert_unchanged()
        with self.state.guard:
            latest=deepcopy(next(reversed(self.state.sessions.values()),None)) if self.state.sessions else None
        return {'status':'SOFTWARE_PREVIEW_READY', 'owner':'⑤ camera_pipeline',
                'url':'/input-player/phone.html?token='+self.state.token,
                'manifest_sha256':PREPARATION_MANIFEST_SHA,
                'validation_only':True, 'physical_phone_verified':False,
                'camera_capture':False, 'neural_inference':False,
                'settings_are_neural_input':False,
                'latest_software_presentation':latest,
                'latest_presentation_is_bound_to_neural_input':False}

    def asset(self, name):
        require(name in ('phone.html','player.js','style.css'), 'Unknown presentation asset')
        self.assert_unchanged()
        path = self.root/'web'/name
        return path.read_bytes(), self.checked[path.resolve()]

    def post(self, request, respond):
        self.assert_unchanged()
        if request.headers.get('X-Stimulus-Token')==self.state.token:
            self.state.logs.mkdir(parents=True,exist_ok=True)
        # The original producer handler validates every setting/event and writes only
        # under the GUI-owned runtime directory, with validation_only fixed to true.
        proxy = SimpleNamespace(path=request.path, headers=request.headers, rfile=request.rfile,
                                server=self.state, respond=respond)
        return self.handler.do_POST(proxy)


class UnifiedFlow:
    def init__(self, store, workbench, runtime=None, presentation_root=None):
        self.store, self.workbench = store, workbench
        self.runtime = Path(runtime or store.root/'gui_v1/runtime/unified_flow')
        self.sessions = {}; self.guard = threading.RLock()
        self.presenter = None; self.presenter_error = None
        try:
            self.presenter = PresentationBridge(presentation_root or
                store.root/'camera_pipeline/phase4_phone_camera_20261010_r1', self.runtime)
        except (OSError, ValueError, KeyError, TypeError, ImportError) as error:
            self.presenter_error = str(error)

    def capabilities(self):
        presenter = {'status':'NOT_AVAILABLE','error':self.presenter_error,'url':None}
        if self.presenter:
            try: presenter = self.presenter.status()
            except (OSError, ValueError) as error: presenter['error'] = str(error)
        comparisons = [row for row in self.workbench.comparisons() if row['comparison_id'] in self.workbench.p0_ids()] if self.workbench else []
        return {'schema':'flyvis-unified-flow-v1', 'source_kinds':list(SOURCE_KINDS),
                'presentation':presenter, 'verified_p0':comparisons,
                'camera':{'status':'NOT_CONNECTED','capture_open':False,'preview_url':None,
                          'input_id':None,'input_schema':'flyvis-real-screen-input-v1',
                          'accepted_new_phone_input':False,'historical_camera_dataset':'camera1'},
                'execution':{'status':'NOT_CONNECTED','job_id':None,'run_id':None},
                'board':{'status':'NOT_CONNECTED','board_id':None}, 'modes':MODES,
                'direct_interactive_export':{'status':'NOT_AVAILABLE','reason':'⑤ has not delivered an accepted direct 721 input exporter'},
                'state_policy':'CAPTURING/QUEUED/RUNNING/COMPLETED require actual producer observations; no timer advances execution'}

    def create(self):
        with self.guard:
            require(len(self.sessions)<256, 'Too many GUI selection sessions; restart to release them')
            sid = uuid.uuid4().hex
            self.sessions[sid] = {'session_id':sid,'revision':0,'source_kind':'digital_verified_p0',
                'state':'SELECTING_INPUT','input_reference':None,'selected_mode':'Full_GPU',
                'job_id':None,'run_id':None,'result':None,'backend_status':'NOT_CONNECTED',
                'camera_capture':False,'board_connected':None,'error':None}
            return deepcopy(self.sessions[sid])

    def snapshot(self, sid):
        with self.guard:
            require(sid in self.sessions, 'Unknown GUI selection session')
            return deepcopy(self.sessions[sid])

    def action(self, sid, action, data):
        with self.guard:
            require(sid in self.sessions, 'Unknown GUI selection session')
            require(isinstance(data,dict), 'JSON object required')
            session = self.sessions[sid]
            require(type(data.get('revision')) is int and data['revision'] == session['revision'], 'Stale or invalid input selection revision')
            if action == 'select':
                source = data.get('source_kind'); require(source in SOURCE_KINDS, 'Unknown input source')
                session.update(source_kind=source,revision=session['revision']+1,
                    state='SELECTING_INPUT' if source=='digital_verified_p0' else 'PREVIEW_ONLY',
                    input_reference=None,job_id=None,run_id=None,result=None,error=None)
                return 200,deepcopy(session)
            if action == 'freeze':
                if session['source_kind'] != 'digital_verified_p0':
                    return 503,dict(deepcopy(session),status='NOT_AVAILABLE',
                        error='No admitted new phone capture/direct 721 export. Presentation parameters are not frozen neural input.')
                cid = data.get('comparison_id')
                require(self.workbench and cid in self.workbench.p0_ids(), 'Only explicitly verified P0 input can be frozen here')
                package = self.workbench.source(cid); frozen = package.frozen
                frozen.assert_unchanged()
                reference_id = 'gui_reference_'+uuid.uuid4().hex
                reference = {'schema':'flyvis-gui-input-reference-v1','reference_id':reference_id,
                    'created_utc':utc(),'source_kind':'digital_verified_p0',
                    'source_is_camera':False,'presentation_id':None,'comparison_id':cid,
                    'producer_input_identity':frozen.info(), 'identity_fingerprint':deepcopy(frozen.fingerprint),
                    'source_directory':str(frozen.root),'steps':800,'dt_s':.005,
                    'input_shape':[1,800,1,721],'input_time_s':[float(frozen.time[0]),float(frozen.time[-1])],
                    'activity_time_s':[float(frozen.activity_time[0]),float(frozen.activity_time[-1])],
                    'resampling':'accepted causal zero-order hold; no new conversion',
                    'new_capture':False,'new_inference':False,'historical_display_kind':'offline_replay'}
                path = self.runtime/'frozen_references'/f'{reference_id}.json'
                path.parent.mkdir(parents=True,exist_ok=True)
                with path.open('x',encoding='utf-8') as stream:json.dump(reference,stream,ensure_ascii=False,indent=2)
                reference['reference_path'] = str(path); reference['reference_sha256'] = sha256(path)
                session.update(state='INPUT_FROZEN',input_reference=reference,job_id=None,
                               run_id=None,result=None,error=None,revision=session['revision']+1)
                return 200,deepcopy(session)
            if action == 'submit':
                require(session['input_reference'] is not None, 'Freeze a verified input first')
                require(data.get('reference_id')==session['input_reference']['reference_id'], 'Wrong input reference')
                require(data.get('mode') in MODES, 'Unknown compute mode')
                ref = session['input_reference']; self.workbench.source(ref['comparison_id'])
                require(sha256(ref['reference_path'])==ref['reference_sha256'], 'Frozen GUI reference modified')
                session.update(state='WAITING_COMPUTE',selected_mode=data['mode'],job_id=None,run_id=None,
                    result=None,error='NOT_CONNECTED: no accepted execution service; request not queued, no task created.')
                return 503,dict(deepcopy(session),status='NOT_CONNECTED')
            if action in ('capture','preview','stop_capture'):
                return 503,dict(deepcopy(session),status='NOT_CONNECTED',
                    error='Camera owner ⑤ has no accepted GUI capture connector. No camera operation performed.')
            raise ValueError('Unknown flow action')
