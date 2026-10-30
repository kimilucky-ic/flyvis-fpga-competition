"""Local GUI v1 phase2: verified recordings; no FlyVis import or device operation."""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
from time import perf_counter,time
from urllib.parse import parse_qs, urlparse
import webbrowser
from functools import lru_cache

import numpy as np

from adapters import statuses, DisconnectedGPUAdapter, AdapterUnavailable
from data_store import DataStore, ROOT

STATIC = {"/": "index.html", "/index.html": "index.html", "/app.js": "app.js", "/styles.css": "styles.css", "/phase3.js": "phase3.js", "/workbench.js":"workbench.js", "/workbench.css":"workbench.css", "/unified_flow.js":"unified_flow.js", "/unified_flow.css":"unified_flow.css"}
STATIC.update({"/scientific_pilot.js":"scientific_pilot.js", "/scientific_pilot.css":"scientific_pilot.css"})
STATIC.update({"/scientific_sparse.js":"scientific_sparse.js", "/scientific_sparse.css":"scientific_sparse.css"})
STATIC.update({'/live_experiment.js':'live_experiment.js','/live_experiment.css':'live_experiment.css'})
STATIC.update({'/live_camera.js':'live_camera.js','/live_camera.css':'live_camera.css'})
STATIC.update({'/spatial_view.js':'spatial_view.js','/spatial_view.css':'spatial_view.css'})
STATIC.update({'/joint_replay.js':'joint_replay.js','/joint_replay.css':'joint_replay.css'})
STATIC.update({'/demo_home.js':'demo_home.js','/demo_home.css':'demo_home.css'})
STATIC.update({'/demo_guide.js':'demo_guide.js','/demo_guide.css':'demo_guide.css'})
STATIC.update({'/stream_wire.js':'stream_wire.js'})
STATIC.update({'/stream_display_diagnostics.js':'stream_display_diagnostics.js'})
STATIC.update({'/live_service_status.js':'live_service_status.js'})
STATIC.update({'/competition.js':'competition.js','/competition.css':'competition.css','/competition_stage.js':'competition_stage.js'})
STATIC.update({'/competition_live.js':'competition_live.js','/skeleton_wire.js':'skeleton_wire.js'})
STATIC['/fixed_skeleton.js']='fixed_skeleton.js'
STATIC['/competition_joint.js']='competition_joint.js'
STATIC['/competition_explanation.js']='competition_explanation.js'
MIME = {".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".css": "text/css; charset=utf-8",
        ".json": "application/json; charset=utf-8", ".csv": "text/csv; charset=utf-8", ".png": "image/png"}


@lru_cache(maxsize=1)
def joint_contract():
    from hybrid_v2 import V2Contract
    return V2Contract()


def handler_factory(store, phase3_config_path=None, workbench_config_path=None, pilot_config_path=None, sparse_config_path=None, live_session_path=None, joint_session_path=None):
    gpu = DisconnectedGPUAdapter()
    live=None;live_error=None
    try:
        from live_jobs import LiveGPUAdapter,LiveRoutes
        live=LiveRoutes(LiveGPUAdapter(live_session_path))
    except (OSError,ValueError,KeyError,TypeError,ImportError) as error:live_error=str(error)
    camera=None;camera_error=None
    try:
        from stream_bridge import StreamBridge
        if live:camera=StreamBridge(live.adapter)
    except (OSError,ValueError,KeyError,TypeError,ImportError) as error:camera_error=str(error)
    # Optional read-only handoff is deliberately isolated from legacy DataStore.
    phase3 = None
    phase3_error = None
    try:
        from phase3_adapter import Phase3Adapter
        phase3 = Phase3Adapter(store, config_path=phase3_config_path)
    except (OSError, ValueError, KeyError, TypeError, AssertionError, ImportError) as error:
        phase3_error = str(error)
    workbench = None
    workbench_error = None
    try:
        from workbench import Workbench
        workbench = Workbench(store, phase3, config_path=workbench_config_path)
    except (OSError,ValueError,KeyError,TypeError,AssertionError,ImportError) as error:
        workbench_error=str(error)
    flow, flow_error = None, None
    try:
        from unified_flow import UnifiedFlow
        flow = UnifiedFlow(store, workbench)
    except (OSError,ValueError,KeyError,TypeError,ImportError) as error:
        flow_error = str(error)
    pilot, pilot_error, runner, runner_error = None, None, None, None
    try:
        from scientific_pilot import ScientificPilot
        pilot = ScientificPilot(store, config_path=pilot_config_path)
    except (OSError,ValueError,KeyError,TypeError,AssertionError,ImportError) as error:
        pilot_error = str(error)
    try:
        from scientific_pilot import AutoRunnerRecords
        runner = AutoRunnerRecords(config_path=pilot_config_path)
    except (OSError,ValueError,KeyError,TypeError,ImportError) as error:
        runner_error = str(error)
    sparse, sparse_error = None, None
    try:
        from scientific_sparse import ScientificSparse
        sparse = ScientificSparse(store, pilot, config_path=sparse_config_path)
    except (OSError,ValueError,KeyError,TypeError,AssertionError,ImportError) as error:
        sparse_error = str(error)
    from competition_replay import LazyCompetition
    competition = LazyCompetition(pilot)
    from competition_explanation import CompetitionExplanation, EXPLANATION_SHA
    competition_explanation = CompetitionExplanation(competition)
    from competition_renderer import CompetitionRenderer
    competition_renderer = CompetitionRenderer(competition)
    if joint_session_path is not None:
        competition_renderer.yield_for_compute()  # Joint compute reserves GPU; geometry stays CPU.
    from competition_frames import CompetitionFrames
    from competition_movie import CompetitionMovie
    competition_frames = CompetitionFrames(competition)
    competition_movie = CompetitionMovie(competition_frames)
    skeleton=None;skeleton_error=None
    try:
        from competition_live import LiveSkeleton
        skeleton=LiveSkeleton(camera)
    except (OSError,ValueError,KeyError,TypeError,ImportError) as error:skeleton_error=str(error)
    joint=None;joint_error=None
    try:
        from joint_camera_bridge import JointCameraBridge
        joint=JointCameraBridge(joint_session_path)
    except (OSError,ValueError,KeyError,TypeError,ImportError) as error:joint_error=str(error)
    class Handler(BaseHTTPRequestHandler):
        @staticmethod
        def close_camera():
            if camera and camera.control:camera.stop()
            competition_renderer.close()
            competition_movie.close()
            if skeleton:skeleton.close()
            if joint:joint.close()
        def send(self, data, mime="application/json; charset=utf-8", status=200, extra=None, embedded=False):
            if not isinstance(data, bytes):
                data = json.dumps(data, ensure_ascii=False, allow_nan=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", mime)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", (extra or {}).get('Cache-Control', 'no-store'))
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; frame-ancestors " + ("'self'" if embedded else "'none'"))
            for key, value in (extra or {}).items():
                if key == 'Cache-Control':continue
                self.send_header(key, str(value))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            started = perf_counter()
            parsed = urlparse(self.path)
            if parsed.path.startswith('/api/joint-camera'):
                try:
                    if not joint:raise ValueError(joint_error or 'CAMERA_JOINT_NOT_CONNECTED')
                    if parsed.path=='/api/joint-camera/status':return self.send(joint.status())
                    if parsed.path=='/api/joint-camera/latest':return self.send(joint.latest())
                    if parsed.path=='/api/joint-camera/clock':return self.send(joint.clock())
                    if parsed.path=='/api/joint-camera/cache':return self.send(joint.cache(),'application/octet-stream')
                    return self.send({'status':'NOT_AVAILABLE'},status=404)
                except (OSError,ValueError,KeyError,TypeError,ImportError) as error:
                    return self.send({'status':'NOT_CONNECTED','error':str(error),'result_valid':False,'whole_run_acceptance':'NOT_AVAILABLE'},status=409)
            if parsed.path=='/api/competition-live/cache':
                try:
                    if not skeleton:raise ValueError('SKELETON_NOT_AVAILABLE')
                    return self.send(skeleton.cache(),'application/octet-stream')
                except (OSError,ValueError,KeyError) as error:return self.send({'error':str(error)},status=409)
            if parsed.path.startswith('/api/stream'):
                parsed=parsed._replace(path=parsed.path.replace('/api/stream','/api/live-camera',1))
            try:
                if parsed.path == '/api/competition-live/status':
                    return self.send(skeleton.status() if skeleton else dict(status='NOT_CONNECTED',error=skeleton_error))
                if parsed.path.startswith('/api/competition'):
                    try:
                        replay = competition.get()
                        if parsed.path == '/api/competition':return self.send(replay.metadata())
                        if parsed.path == '/api/competition/explanation':return self.send(competition_explanation.binary(parse_qs(parsed.query).get('run',[None])[0]),extra={'X-Content-SHA256':EXPLANATION_SHA,'X-Run-ID':replay.pilot.identity['run_id'],'X-Display-Kind':'OFFLINE_REPLAY'})
                        if parsed.path == '/api/competition/frames':return self.send(competition_frames.metadata())
                        if parsed.path == '/api/competition/movie/status':return self.send(competition_movie.status())
                        frame_match = re.fullmatch(r'/api/competition/frames/(\d+)\.png', parsed.path)
                        if frame_match:return self.send(competition_frames.image(int(frame_match[1]),parse_qs(parsed.query).get('identity',[None])[0]),'image/png',extra={'Cache-Control':'private, max-age=31536000, immutable'})
                        movie_match = re.fullmatch(r'/api/competition/movie/([a-f0-9]{32})\.mp4', parsed.path)
                        if movie_match:return self.send(competition_movie.video(movie_match[1]),'video/mp4')
                        match = re.fullmatch(r'/api/competition/(input|flow|spatial)\.bin',parsed.path)
                        if match:return self.send(replay.binary(match[1],parse_qs(parsed.query).get('run',[None])[0]),'application/octet-stream',extra={'X-Run-ID':replay.pilot.identity['run_id'],'X-Content-SHA256':replay.binary_sha[match[1]],'X-Display-Kind':'OFFLINE_REPLAY'})
                        return self.send({'status':'NOT_AVAILABLE','error':'Unknown competition route'},status=404)
                    except (OSError,ValueError,KeyError,TypeError,ImportError) as error:
                        return self.send({'status':'NOT_AVAILABLE','error':str(error),'PL_execution':False},status=409)
                if parsed.path.startswith('/api/hybrid/full485'):
                    try:
                        from joint_replay import admitted_replay
                        replay=admitted_replay()
                        if parsed.path=='/api/hybrid/full485':return self.send(replay.metadata())
                        match=re.fullmatch(r'/api/hybrid/full485/(input|spatial|flow)\.bin',parsed.path)
                        if match:return self.send(replay.binary(match[1],parse_qs(parsed.query).get('run',[None])[0]),'application/octet-stream')
                        return self.send({'status':'NOT_AVAILABLE'},status=404)
                    except (OSError,ValueError,KeyError,TypeError,ImportError) as error:
                        return self.send({'status':'NOT_AVAILABLE','FPGA_status':'NOT_CONNECTED','PL_proven_global_ids':[],'error':str(error)},status=409)
                if parsed.path=='/api/hybrid/joint':
                    try:
                        return self.send(joint_contract().readiness())
                    except (OSError,ValueError,KeyError,ImportError) as error:
                        return self.send({'status':'NOT_AVAILABLE','error':str(error),'FPGA_status':'NOT_CONNECTED','PL_proven_global_ids':[]},status=409)
                if parsed.path=='/api/hybrid':
                    try:
                        from hybrid_a3 import contract
                        return self.send(contract().status())
                    except (OSError,ValueError,KeyError) as error:
                        return self.send({'status':'NOT_AVAILABLE','error':str(error),'FPGA_status':'NOT_CONNECTED','PL_proven_global_ids':[]},status=409)
                if parsed.path in STATIC:
                    path = ROOT / "viewer" / STATIC[parsed.path]
                    return self.send(path.read_bytes(), MIME[path.suffix])
                if parsed.path == "/favicon.ico":
                    return self.send(b"", "image/x-icon", 204)
                if parsed.path.startswith('/api/live-camera'):
                    if not camera:return self.send({'status':'NOT_CONNECTED','error':camera_error,'result':None},status=503)
                    camera.touch()
                    if parsed.path=='/api/live-camera/clock':return self.send(camera.clock())
                    if parsed.path=='/api/live-camera/summary':return self.send(camera.summary())
                    if parsed.path=='/api/live-camera':return self.send(camera.status())
                    if parsed.path=='/api/live-camera/latest':
                        try:
                            q=parse_qs(parsed.query);after=int(q['after'][0]) if 'after' in q else None
                            return self.send(camera.latest(wire=q.get('wire',[''])[0]=='f32',after=after,wait_ms=int(q.get('wait_ms',['0'])[0])))
                        except (OSError,ValueError,KeyError) as error:return self.send({'status':'NOT_AVAILABLE','error':str(error),'result':None},status=409)
                    match=re.fullmatch(r'/api/live-camera/frames/(\d+)',parsed.path)
                    if match:return self.send(camera.frame(int(match[1]),parse_qs(parsed.query).get('run',[None])[0]),'image/png',extra={'X-Run-ID':camera.control['run_id']})
                    return self.send({'status':'NOT_AVAILABLE','result':None},status=404)
                if parsed.path=='/api/live' or parsed.path.startswith('/api/live/'):
                    if not live:return self.send({'status':'NOT_CONNECTED','error':live_error,'result':None,'PL_execution':False},status=503)
                    code,value=live.route('GET',self.path)
                    return self.send(value,'application/octet-stream' if isinstance(value,bytes) else 'application/json; charset=utf-8',status=code)
                if parsed.path == "/api/health":
                    return self.send({"status": "ok", "execution_kind": "offline_replay", "datasets": [d["id"] for d in store.catalog()["datasets"]]})
                if parsed.path == "/api/catalog":
                    return self.send(store.catalog())
                if parsed.path == '/api/autorunner':
                    return self.send(runner.snapshot() if runner else {'status':'NOT_AVAILABLE','records':[],'error':runner_error})
                if parsed.path == '/api/scientific-pilot':
                    return self.send(pilot.status() if pilot else {'status':'NOT_AVAILABLE','conditions':[],'error':pilot_error,'result':None,'FPGA_status':'NOT_CONNECTED'})
                if parsed.path == '/api/scientific-sparse':
                    return self.send(sparse.status() if sparse else {'status':'NOT_AVAILABLE','conditions':[],'error':sparse_error,'result':None,'FPGA_status':'NOT_CONNECTED','PL_execution':False})
                if parsed.path.startswith('/api/scientific-sparse/'):
                    if not sparse:return self.send({'status':'NOT_AVAILABLE','error':sparse_error,'result':None},status=503)
                    match=re.fullmatch(r'/api/scientific-sparse/conditions/(ON60|OFF90)(?:/(input\.bin|(?:Full|KEEP_(?:0|488|1016|1736|2648|3752|5768))/flow\.bin))?',parsed.path)
                    if match:
                        condition,tail=match[1],match[2]
                        if not tail:return self.send(sparse.info(condition))
                        mode=None if tail=='input.bin' else tail.split('/')[0]
                        identity=sparse.info(condition)['input'] if mode is None else sparse.flow_identity(condition,mode)
                        return self.send(sparse.binary(condition,mode),'application/octet-stream',extra={'X-Run-ID':sparse.config['run_id'],'X-Source-Run-ID':identity.get('run_id','NOT_APPLICABLE'),'X-Source-SHA256':identity['sha256'],'X-Display-Kind':'OFFLINE_REPLAY','X-Evidence-Level':'SOFTWARE_SPARSE_RETAIN','X-PL-Execution':'false'})
                    match=re.fullmatch(r'/api/scientific-sparse/sets/(0|488|1016|1736|2648|3752|5768)',parsed.path)
                    if match:return self.send(sparse.node_set(int(match[1])))
                    if parsed.path.startswith('/api/scientific-sparse/files/'):
                        name=parsed.path.split('/files/',1)[1]
                        return self.send(sparse.source(name),MIME.get(Path(name).suffix,'application/octet-stream'))
                    return self.send({'status':'NOT_AVAILABLE','error':'Unknown admitted B route','result':None},status=404)
                if parsed.path.startswith('/api/scientific-pilot/'):
                    if not pilot:return self.send({'status':'NOT_AVAILABLE','error':pilot_error,'result':None},status=503)
                    match=re.fullmatch(r'/api/scientific-pilot/conditions/(ON60|OFF90)(?:/(input\.bin|(?:Full|Sham|BLOCK_T4_RELEASE|BLOCK_T5_RELEASE|BLOCK_T4T5_RELEASE)/flow\.bin))?',parsed.path)
                    if match:
                        condition,tail=match[1],match[2]
                        if not tail:return self.send(pilot.info(condition))
                        mode=None if tail=='input.bin' else tail.split('/')[0]
                        return self.send(pilot.binary(condition,mode),'application/octet-stream',extra={'X-Run-ID':pilot.identity['run_id'],'X-Display-Kind':'offline replay','X-Evidence-Level':'SOFTWARE_PILOT','X-PL-Execution':'false'})
                    if parsed.path.startswith('/api/scientific-pilot/files/'):
                        name=parsed.path.split('/files/',1)[1]
                        return self.send(pilot.source(name),MIME.get(Path(name).suffix,'text/plain; charset=utf-8'))
                    return self.send({'status':'NOT_AVAILABLE','error':'Unknown admitted scientific route','result':None},status=404)
                if parsed.path == '/api/flow':
                    return self.send(flow.capabilities() if flow else {'status':'NOT_AVAILABLE','error':flow_error},status=200 if flow else 503)
                flow_session = re.fullmatch(r'/api/flow/sessions/([a-f0-9]{32})', parsed.path)
                if flow_session:
                    if not flow:return self.send({'status':'NOT_AVAILABLE','error':flow_error},status=503)
                    return self.send(flow.snapshot(flow_session[1]))
                player_asset = re.fullmatch(r'/input-player/(phone\.html|player\.js|style\.css)', parsed.path)
                if player_asset:
                    if not flow or not flow.presenter:return self.send({'status':'NOT_AVAILABLE','error':'Verified ⑤ presenter absent'},status=503)
                    body, digest = flow.presenter.asset(player_asset[1])
                    return self.send(body,MIME[Path(player_asset[1]).suffix],extra={'X-Source-SHA256':digest,'X-Preview-Only':'true'},embedded=player_asset[1]=='phone.html')
                if parsed.path == '/api/workbench':
                    return self.send(workbench.status() if workbench else {'status':'NOT_AVAILABLE','comparisons':[],'error':workbench_error})
                if parsed.path.startswith('/api/workbench/'):
                    if not workbench:
                        return self.send({'status':'NOT_AVAILABLE','error':workbench_error,'result':None},status=503)
                    match=re.fullmatch(r'/api/workbench/comparisons/([a-f0-9]{64})',parsed.path)
                    if match:return self.send(workbench.info(match[1]))
                    match=re.fullmatch(r'/api/workbench/runs/([A-Za-z0-9_-]+)/(activity\.bin|events|steps/\d+|functional-report)',parsed.path)
                    if match:
                        run,tail=match[1],match[2]
                        if tail=='activity.bin':
                            body,source_sha,comparison=workbench.activity(run)
                            return self.send(body,'application/octet-stream',extra={'X-Run-ID':run,'X-Comparison-ID':comparison,'X-Source-SHA256':source_sha,'X-Display-Kind':'offline_replay'})
                        if tail=='events':return self.send(workbench.events(run))
                        if tail.startswith('steps/'):return self.send(workbench.step(run,int(tail.split('/')[1])))
                        return self.send(workbench.functional_report(run),'application/json; charset=utf-8')
                    if parsed.path=='/api/workbench/camera':
                        return self.send(workbench.status()['camera_input'])
                    return self.send({'status':'NOT_AVAILABLE','result':None,'error':'Unknown run or evidence route'},status=404)
                if parsed.path == "/api/phase3":
                    return self.send(phase3.status() if phase3 else {"status":"unavailable","input":None,"comparisons":[],"error":phase3_error}, status=200)
                if parsed.path.startswith("/api/phase3/"):
                    if not phase3 or not phase3.input:
                        return self.send({"status":"unavailable","error":phase3_error or "Frozen input not verified","result":None}, status=409)
                    phase3.input.assert_unchanged()
                    if parsed.path == "/api/phase3/input":
                        return self.send(phase3.input.info())
                    if parsed.path == "/api/phase3/input/stimulus.bin":
                        return self.send(phase3.input.stimulus[0,:,0].tobytes(), "application/octet-stream", extra={"X-Source-SHA256":phase3.input.fingerprint["stimulus"],"X-Comparison-ID":phase3.input.comparison_id})
                    source = re.fullmatch(r"/api/phase3/input/frames/(\d+)\.png",parsed.path)
                    if source:
                        path = phase3.input.video.frame_path(int(source[1]),1)
                        return self.send(path.read_bytes(),"image/png",extra={"X-Source-SHA256":phase3.input.video.checked[path]})
                    comparison = re.fullmatch(r"/api/phase3/comparisons/([a-f0-9]{64})(?:/(Full_GPU|Python_Replacement)/activity\.bin)?",parsed.path)
                    if comparison:
                        if comparison[1] not in phase3.packages:
                            return self.send({"status":"unavailable","error":"No explicitly admitted B comparison package","result":None}, status=409)
                        package = phase3.packages[comparison[1]]
                        package.assert_unchanged()
                        if not comparison[2]:
                            return self.send(package.info())
                        run = package.descriptor["modes"][comparison[2]]
                        path = package.roles[run["activity_full_role"]]
                        activity = package.arrays[comparison[2]][:,phase3.input.central_ids]
                        return self.send(np.ascontiguousarray(activity,dtype="<f4").tobytes(),"application/octet-stream",extra={"X-Source-SHA256":package.checked[path],"X-Comparison-ID":comparison[1],"X-Run-ID":run["run_id"],"X-Display-Kind":"offline_replay"})
                    return self.send({"error":"Not found"},status=404)
                if parsed.path == "/api/adapters":
                    verified_ids = {item["id"] for item in store.catalog()["datasets"]}
                    return self.send(statuses("camera1" in verified_ids))
                if re.fullmatch(r"/api/inference/[A-Za-z0-9_-]+", parsed.path):
                    try:
                        return self.send(gpu.poll(parsed.path.rsplit("/", 1)[-1]))
                    except AdapterUnavailable as error:
                        return self.send({"status": "not_connected", "execution_kind": None, "error": str(error), "result": None}, status=503)
                match = re.fullmatch(r"/api/datasets/([a-z0-9]+)(?:/(.*))?", parsed.path)
                if not match:
                    return self.send({"error": "Not found"}, status=404)
                dataset = store.datasets[match[1]]
                if hasattr(dataset, "assert_unchanged"):
                    dataset.assert_unchanged()
                tail = match[2]
                if not tail:
                    return self.send(dataset.info())
                if tail == "directions":
                    query = parse_qs(parsed.query)
                    if hasattr(dataset, "condition_directions"):
                        return self.send(dataset.condition_directions(query.get("cell", ["T4c"])[0], float(query.get("intensity", ["1"])[0]), int(query.get("sample", ["0"])[0])))
                    return self.send(dataset.directions(query.get("cell", ["T4c"])[0], int(query.get("intensity", ["1"])[0])))
                frame_match = re.fullmatch(r"frames/(\d+)\.png", tail)
                if frame_match and hasattr(dataset, "frame_path") and not hasattr(dataset, "descriptor"):
                    path = dataset.frame_path(int(frame_match[1]))
                    return self.send(path.read_bytes(), "image/png", extra={"X-Source-SHA256": dataset.checked[path]})
                video_match = re.fullmatch(r"samples/(\d+)/frames/(\d+)\.png", tail)
                if video_match and hasattr(dataset, "descriptor"):
                    path = dataset.frame_path(int(video_match[2]), int(video_match[1]))
                    return self.send(path.read_bytes(), "image/png", extra={"X-Source-SHA256": dataset.checked[path]})
                sample_match = re.fullmatch(r"samples/(\d+)(?:/(stimulus|activity)\.bin)?", tail)
                if sample_match:
                    index = int(sample_match[1])
                    sample = dataset.sample(index)
                    if not sample_match[2]:
                        return self.send(sample)
                    kind = sample_match[2]
                    array = (dataset.input_array(index) if hasattr(dataset, "input_array") else dataset.stimulus[index, :, 0, :]) if kind == "stimulus" else dataset.activity[index]
                    data = np.asarray(array, dtype="<f8" if kind == "stimulus" else "<f4").tobytes(order="C")
                    return self.send(data, "application/octet-stream", extra={"X-Source-SHA256": sample[f"source_{'input' if kind == 'stimulus' else 'output'}_sha256"],
                                                                          "X-Serve-Ms": (perf_counter() - started) * 1000})
                file_match = re.fullmatch(r"files/([A-Za-z0-9_.]+)", tail)
                if file_match:
                    name = file_match[1]
                    if hasattr(dataset, "file_path") and name != "manifest.json":
                        path = dataset.file_path(name)
                    elif name == "manifest.json":
                        path = dataset.manifest_path
                    elif name in dataset.metric_files:
                        path = dataset.metric_files[name]
                    elif name in dataset.hashes:
                        path = dataset.directory / name
                    else:
                        raise KeyError(name)
                    return self.send(path.read_bytes(), MIME.get(path.suffix, "application/octet-stream"))
                return self.send({"error": "Not found"}, status=404)
            except (KeyError, IndexError):
                self.send({"error": "Unknown dataset, sample or file", **({'status':'NOT_AVAILABLE','result':None} if parsed.path.startswith(('/api/workbench','/api/scientific-sparse')) else {})}, status=404)
            except ValueError as error:
                self.send({"error": str(error), **({'status':'NOT_AVAILABLE','result':None} if parsed.path.startswith(('/api/scientific-pilot','/api/scientific-sparse')) else {})}, status=409 if "restart and revalidate" in str(error) else 400)
            except OSError as error:
                self.send({"error": f"Verified source unavailable: {error}", "status": "NOT_AVAILABLE" if parsed.path.startswith('/api/scientific-sparse') else "unavailable", **({'result':None} if parsed.path.startswith('/api/scientific-sparse') else {})}, status=409)
            except (BrokenPipeError, ConnectionResetError):
                pass

        def do_POST(self):
            if self.path.startswith('/api/joint-camera/'):
                try:
                    expected='http://127.0.0.1:'+str(self.server.server_address[1])
                    if self.headers.get('Host')!=expected.split('://')[1] or self.headers.get('Origin')!=expected or self.headers.get('Sec-Fetch-Site')=='cross-site':raise ValueError('LOCAL_SAME_ORIGIN_REQUIRED')
                    if not joint:raise ValueError(joint_error or 'CAMERA_JOINT_NOT_CONNECTED')
                    size=int(self.headers.get('Content-Length','0'))
                    if self.path=='/api/joint-camera/recording':
                        if not 4<size<=100_000_000 or self.headers.get('Content-Type')!='video/webm':raise ValueError('BOUNDED_WEBM_REQUIRED')
                        return self.send(joint.recording(self.rfile.read(size)))
                    if not 0<size<=16384 or self.headers.get('Content-Type')!='application/json':raise ValueError('BOUNDED_JSON_REQUIRED')
                    body=json.loads(self.rfile.read(size))
                    if self.path=='/api/joint-camera/prepare':return self.send(joint.prepare())
                    if self.path=='/api/joint-camera/start':return self.send(joint.start(body))
                    if self.path=='/api/joint-camera/draw':return self.send(joint.record_draw(body))
                    if self.path=='/api/joint-camera/stop':return self.send(joint.stop(body))
                    raise ValueError('Unknown joint camera action')
                except (OSError,ValueError,KeyError,TypeError,ImportError) as error:
                    return self.send({'status':'NOT_AVAILABLE','error':str(error),'whole_run_acceptance':'NOT_AVAILABLE'},status=409)
            if self.path.startswith('/api/competition-live/'):
                try:
                    expected='http://127.0.0.1:'+str(self.server.server_address[1])
                    if self.headers.get('Host')!=expected.split('://')[1] or self.headers.get('Origin')!=expected or self.headers.get('Sec-Fetch-Site')=='cross-site':raise ValueError('LOCAL_SAME_ORIGIN_REQUIRED')
                    size=int(self.headers.get('Content-Length','0'))
                    if not 0<size<=4096 or self.headers.get('Content-Type')!='application/json':raise ValueError('BOUNDED_JSON_REQUIRED')
                    body=json.loads(self.rfile.read(size))
                    if skeleton is None:raise ValueError(skeleton_error or 'SKELETON_NOT_AVAILABLE')
                    if self.path=='/api/competition-live/prepare':
                        competition_renderer.yield_for_compute()
                        return self.send(skeleton.prepare(body))
                    if self.path=='/api/competition-live/frame':return self.send(skeleton.render(body),'application/octet-stream',extra={'X-Line10-Wire':'json32le+rgba8-v1'})
                    if self.path=='/api/competition-live/stop':
                        skeleton.close();return self.send(skeleton.status())
                    raise ValueError('Unknown skeleton action')
                except (OSError,ValueError,KeyError,TypeError,ImportError) as error:
                    return self.send({'status':'NOT_AVAILABLE','error':str(error),'PL_execution':False},status=409)
            if self.path.startswith('/api/competition/movie/'):
                try:
                    expected='http://127.0.0.1:'+str(self.server.server_address[1])
                    if self.headers.get('Host')!=expected.split('://')[1] or self.headers.get('Origin')!=expected or self.headers.get('Sec-Fetch-Site')=='cross-site':raise ValueError('LOCAL_SAME_ORIGIN_REQUIRED')
                    size=int(self.headers.get('Content-Length','0'))
                    match=re.fullmatch(r'/api/competition/movie/([a-f0-9]{32})/frame/(\d+)',self.path)
                    if match:
                        if not 24<size<=5_000_000 or self.headers.get('Content-Type')!='image/png':raise ValueError('BOUNDED_PNG_REQUIRED')
                        return self.send(competition_movie.capture(match[1],int(match[2]),self.rfile.read(size),self.headers))
                    if not 0<size<=4096 or self.headers.get('Content-Type')!='application/json':raise ValueError('BOUNDED_JSON_REQUIRED')
                    body=json.loads(self.rfile.read(size))
                    action=self.path.rsplit('/',1)[-1]
                    if action not in ('start','finish','cancel'):raise ValueError('Unknown export action')
                    return self.send(getattr(competition_movie,action)(body))
                except (ValueError,KeyError,TypeError,OSError) as error:
                    return self.send({'status':'NOT_AVAILABLE','error':str(error),'PL_execution':False},status=409)
            if self.path == '/api/competition/render':
                try:
                    expected='http://127.0.0.1:'+str(self.server.server_address[1])
                    if self.headers.get('Host')!=expected.split('://')[1] or self.headers.get('Origin')!=expected or self.headers.get('Sec-Fetch-Site')=='cross-site':raise ValueError('LOCAL_SAME_ORIGIN_REQUIRED')
                    size=int(self.headers.get('Content-Length','0'))
                    if not 0<size<=4096 or self.headers.get('Content-Type')!='application/json':raise ValueError('BOUNDED_JSON_REQUIRED')
                    body=json.loads(self.rfile.read(size))
                    if body.get('use_prerendered'):
                        result=competition_frames.render(body)
                        competition_renderer.release()
                        return self.send(result)
                    return self.send(competition_renderer.render(body))
                except (ValueError,KeyError,TypeError,OSError) as error:
                    return self.send({'status':'NOT_AVAILABLE','error':str(error),'result':None,'PL_execution':False},status=409)
            if self.path.startswith('/api/hybrid/full485/recording-trace?'):
                try:
                    expected='http://127.0.0.1:'+str(self.server.server_address[1])
                    if self.headers.get('Host')!=expected.split('://')[1] or self.headers.get('Origin')!=expected or self.headers.get('Sec-Fetch-Site')=='cross-site':raise ValueError('LOCAL_SAME_ORIGIN_REQUIRED')
                    size=int(self.headers.get('Content-Length','0'))
                    if not 0<size<=200000 or self.headers.get('Content-Type')!='application/json':raise ValueError('BOUNDED_TRACE_REQUIRED')
                    from joint_replay import admitted_replay
                    return self.send(admitted_replay().save_recording_trace(json.loads(self.rfile.read(size)),parse_qs(urlparse(self.path).query).get('run',[None])[0]))
                except (OSError,ValueError,KeyError,TypeError) as error:return self.send({'status':'NOT_AVAILABLE','error':str(error)},status=409)
            if self.path.startswith('/api/hybrid/full485/recording?'):
                try:
                    expected='http://127.0.0.1:'+str(self.server.server_address[1]);origin=self.headers.get('Origin')
                    if self.headers.get('Host')!=expected.split('://')[1] or origin!=expected or self.headers.get('Sec-Fetch-Site')=='cross-site':raise ValueError('LOCAL_SAME_ORIGIN_REQUIRED')
                    size=int(self.headers.get('Content-Length','0'))
                    if not 0<size<=100_000_000 or self.headers.get('Content-Type')!='video/webm':raise ValueError('BOUNDED_WEBM_REQUIRED')
                    from joint_replay import admitted_replay
                    return self.send(admitted_replay().save_recording(self.rfile.read(size),parse_qs(urlparse(self.path).query).get('run',[None])[0]))
                except (OSError,ValueError,KeyError,TypeError) as error:return self.send({'status':'NOT_AVAILABLE','error':str(error)},status=409)
            if self.path=='/api/hybrid/jobs':
                return self.send({'status':'NOT_CONNECTED','backend':'NOT_CONNECTED','run_id':None,'result':None,
                    'PL_execution':False,'error':'A3R1 live board, chemical and R5768 acceptance not yet admitted'},status=503)
            if self.path.startswith('/api/stream'):self.path=self.path.replace('/api/stream','/api/live-camera',1)
            if self.path in ('/api/live-camera/start','/api/live-camera/stop','/api/live-camera/draw','/api/live-camera/input'):
                if not camera:return self.send({'status':'NOT_CONNECTED','error':camera_error,'result':None},status=503)
                try:
                    expected='http://127.0.0.1:'+str(self.server.server_address[1]);origin=self.headers.get('Origin')
                    if self.headers.get('Host')!=expected.split('://')[1] or (origin and origin!=expected) or self.headers.get('Sec-Fetch-Site')=='cross-site':raise ValueError('LOCAL_SAME_ORIGIN_REQUIRED')
                    size=int(self.headers.get('Content-Length','0'))
                    if not 0<size<=(2500000 if self.path.endswith('/input') else 8192 if self.path.endswith('/draw') else 2048) or self.headers.get('Content-Type')!='application/json':raise ValueError('BOUNDED_JSON_REQUIRED')
                    body=json.loads(self.rfile.read(size))
                    json.dumps(body,allow_nan=False)
                    if self.path.endswith('/start'):competition_renderer.yield_for_compute()
                    if self.path.endswith('/draw') and skeleton:skeleton.verify_cached_draw(body)
                    value=camera.start(body) if self.path.endswith('/start') else camera.record_draw(body) if self.path.endswith('/draw') else camera.input(body) if self.path.endswith('/input') else camera.stop(body)
                    return self.send(value,status=202)
                except (OSError,ValueError,KeyError,TypeError) as error:return self.send({'status':'NOT_AVAILABLE','error':str(error),'result':None},status=409)
            if self.path.startswith('/api/live/') or (self.path=='/api/inference' and live_session_path):
                if not live:return self.send({'status':'NOT_CONNECTED','error':live_error,'result':None},status=503)
                try:
                    size=int(self.headers.get('Content-Length','0'));origin=self.headers.get('Origin')
                    expected='http://127.0.0.1:'+str(self.server.server_address[1])
                    if self.headers.get('Host')!=expected.split('://')[1] or (origin and origin!=expected) or self.headers.get('Sec-Fetch-Site')=='cross-site':raise ValueError('LOCAL_SAME_ORIGIN_REQUIRED')
                    if not 0<size<=4096 or self.headers.get('Content-Type')!='application/json':raise ValueError('BOUNDED_JSON_REQUIRED')
                    body=json.loads(self.rfile.read(size));json.dumps(body,allow_nan=False)
                    if self.path in ('/api/live/jobs','/api/inference'):competition_renderer.yield_for_compute()
                    code,value=live.route('POST',self.path,body);return self.send(value,status=code)
                except (ValueError,TypeError) as error:return self.send({'status':'NOT_AVAILABLE','error':str(error),'result':None},status=400)
            if self.path.startswith(('/api/scientific-pilot','/api/scientific-sparse','/api/autorunner')):
                return self.send({'status':'NOT_CONNECTED','error':'Read-only research records; no execution service or new job','job_id':None,'run_id':None,'result':None,'PL_execution':False},status=503)
            if self.path in ('/api/arm','/api/events'):
                if not flow or not flow.presenter:return self.send({'status':'NOT_AVAILABLE','error':'Verified ⑤ presenter absent'},status=503)
                try:return flow.presenter.post(self,lambda status,value:self.send(value,status=status))
                except (OSError,ValueError):return self.send({'status':'NOT_AVAILABLE','error':'Presentation source no longer verified'},status=409)
            if self.path.startswith('/api/flow/'):
                if not flow:return self.send({'status':'NOT_AVAILABLE','error':flow_error},status=503)
                try:
                    size=int(self.headers.get('Content-Length','0'))
                    if not 0<size<=4096:raise ValueError('JSON body size outside bounds')
                    if self.headers.get('Content-Type')!='application/json':raise ValueError('application/json required')
                    data=json.loads(self.rfile.read(size));json.dumps(data,allow_nan=False)
                    if not isinstance(data,dict):raise ValueError('JSON object required')
                    if self.path=='/api/flow/sessions':return self.send(flow.create())
                    match=re.fullmatch(r'/api/flow/sessions/([a-f0-9]{32})/(select|freeze|submit|capture|preview|stop_capture)',self.path)
                    if not match:return self.send({'error':'Unknown flow route'},status=404)
                    code,value=flow.action(match[1],match[2],data);return self.send(value,status=code)
                except (ValueError,KeyError,TypeError) as error:return self.send({'status':'NOT_AVAILABLE','error':str(error),'job_id':None,'run_id':None,'result':None},status=409)
                except OSError as error:return self.send({'status':'NOT_AVAILABLE','error':str(error),'job_id':None,'run_id':None,'result':None},status=409)
            if self.path.startswith('/api/workbench/'):
                return self.send({'status':'NOT_AVAILABLE','backend_status':'not_connected','run_id':None,'job_id':None,'execution_kind':None,'result':None,'error':'No formally accepted execution/camera backend. No task created; no replay promoted to computation.'},status=503)
            if self.path == "/api/inference":
                try:
                    gpu.submit()
                except AdapterUnavailable as error:
                    return self.send({"status": "not_connected", "execution_kind": None, "error": str(error), "result": None}, status=503)
            # Reserved endpoints fail explicitly; a replay can never become a new run.
            if self.path in ["/api/inference", "/api/camera/record", "/api/comparison"]:
                return self.send({"status": "not_connected", "execution_kind": None,
                                  "error": "No connected capture/replacement execution adapter", "result": None}, status=503)
            self.send({"error": "Not found"}, status=404)

    return Handler


def main():
    parser = argparse.ArgumentParser(description="FlyVis offline GUI v1")
    parser.add_argument("--port", type=int, default=8771)
    parser.add_argument("--no-open", action="store_true")
    parser.add_argument('--live-session',default=None,help='Fresh GUI-owned bounded session; no automatic GPU startup')
    parser.add_argument('--joint-session',default=None,help='Fresh line2 camera-joint session; never starts a Full worker')
    parser.add_argument('--stop-file',default=None,help='Launcher-owned cooperative shutdown marker')
    parser.add_argument('--controller-file',default=None,help='Optional owned launcher heartbeat; prevents orphan GUI service')
    args = parser.parse_args()
    print("Verifying existing datasets and source manifests...", flush=True)
    store = DataStore()
    handler=handler_factory(store,live_session_path=args.live_session,joint_session_path=args.joint_session)
    server = ThreadingHTTPServer(("127.0.0.1", args.port),handler)
    url = f"http://127.0.0.1:{args.port}"
    print(f"FlyVis offline GUI v1: {url} | {len(store.datasets)} verified datasets | OFFLINE REPLAY", flush=True)
    if store.errors:
        print(json.dumps(store.errors, ensure_ascii=False), flush=True)
    if not args.no_open:
        webbrowser.open(url)
    try:
        if args.stop_file:
            server.timeout=1
            while not Path(args.stop_file).exists():
                if args.controller_file:
                    try:
                        controller=json.loads(Path(args.controller_file).read_text(encoding='utf-8'))
                        if time()-controller['unix_time']>=15:break
                    except (OSError,ValueError,KeyError):break
                server.handle_request()
        else:server.serve_forever()
    except KeyboardInterrupt:
        print("GUI server stopped.", flush=True)
    finally:
        handler.close_camera()
        server.server_close()


if __name__ == "__main__":
    main()
