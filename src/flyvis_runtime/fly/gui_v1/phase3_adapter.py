"""GUI-owned, read-only fixed-video input and explicitly admitted comparisons.

No model imports, computations of neural activity, directory discovery or device
operation. A missing/bad optional handoff cannot prevent the 55-condition GUI.
The comparison descriptor is a GUI transport contract, not a hardware protocol.
"""
import hashlib
import json
from pathlib import Path

import numpy as np

from camera_store import inside, require
from data_store import ROOT, TARGETS, numeric_row, read_csv, read_json
from startup_cache import cached_sha256 as sha256

PARENT_SHA = "4a55fa37d3a4f1064270b258f314047f059af2880a9ed95689ed438793b654e6"
INITIAL_SHA = "4e09f6eb57dbc84b68294d486fa8684764b2081f1c942ca25ec57228fbd39c0e"
MODEL_SHA = "d0e42857e738d0315897c2d50fde9eb3fb1a3fb1f071d55dfc13d53d72bccc3f"


def array_digest(array):
    a = np.ascontiguousarray(array)
    header = json.dumps({"shape":list(a.shape),"dtype":a.dtype.str},sort_keys=True).encode()
    return hashlib.sha256(header + a.tobytes()).hexdigest()


class VerifiedFiles:
    def init__(self):
        self.checked, self.signatures = {}, {}

    def check(self, path, digest, size=None):
        path = Path(path).resolve()
        before = path.stat()
        require(size is None or before.st_size == size, f"Wrong file size: {path.name}")
        require(sha256(path) == digest, f"SHA256 mismatch: {path.name}")
        after = path.stat()
        require((before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns), "Source changed during verification")
        self.checked[path] = digest
        self.signatures[path] = (after.st_size, after.st_mtime_ns)
        return path

    def assert_unchanged(self):
        for path, signature in self.signatures.items():
            stat = path.stat()
            require((stat.st_size, stat.st_mtime_ns) == signature, "Phase3 verified source changed; restart and revalidate")


class FrozenVideoInput(VerifiedFiles):
    def init__(self, config, root, video):
        super().init__()
        require(video is not None, "Accepted controlled6 source unavailable")
        video.assert_unchanged()
        self.video = video
        self.root = Path(config["input_bundle"]).resolve()
        approved = root.parent / "fpga/flyvis-circuit-selection/phase3_20261010"
        require(self.root.is_relative_to(approved.resolve()), "Input bundle outside assigned phase3 namespace")
        pins = config["input_pins"]
        require(set(pins) == {"video_manifest.json", "artifact_manifest.json"}, "Missing fixed input anchors")
        for name, digest in pins.items():
            self.check(inside(self.root, name), digest)
        entries = read_json(self.root / "artifact_manifest.json")["files"]
        names = set()
        for entry in entries:
            require(entry["path"] not in names, "Duplicate input manifest path")
            names.add(entry["path"])
            self.check(inside(self.root, entry["path"]), entry["sha256"], entry["bytes"])
        load = lambda name: np.load(self.root / name, allow_pickle=False, mmap_mode="r")
        required = {"video_manifest.json", "identity_manifest.json", "stimulus.npy", "initial_state_full.npy",
                    "time.npy", "activity_time.npy", "numeric_profile.json", "metric_profile.json", "cell_types.npy",
                    "central_node_indices.npy", "input_node_indices.npy", "expanded_parameters.npz", "nodes_full.csv",
                    "input_hex_coordinates.csv", "time_alignment.csv", "static_boundary_gpu_native.npz",
                    "candidates/B_T5c/candidate_manifest.json", "candidates/B_T5c/node_map.csv", "candidates/B_T5c/edge_partition_ids.npz"}
        require(required.issubset(names), "Incomplete frozen input inventory")
        self.manifest = m = read_json(self.root / "video_manifest.json")
        self.identity = identity = read_json(self.root / "identity_manifest.json")
        self.metrics = read_json(self.root / "metric_profile.json")
        require(m["schema"] == "flyvis-single-video-frozen-input/v1" and m["status"] == "PASS_FROZEN_SINGLE_VIDEO_INPUT", "Input not frozen")
        require(m["condition_id"] == "01_off_right" and m["original_sample"] == 1 and m["steps"] == 800 and m["dt_s"] == .005 and m["shape"] == [1,800,1,721], "Wrong fixed condition/axes")
        require(m["source_is_camera"] is False and all(m[k] is True for k in ["no_extra_preframes", "no_additional_warmup", "no_rerender"]), "Wrong source/warmup policy")
        self.fingerprint = f = m["identity_fingerprint"]
        roles = {"expanded":"expanded_parameters.npz", "candidate":"candidates/B_T5c/candidate_manifest.json",
                 "node_map":"candidates/B_T5c/node_map.csv", "edge_partition":"candidates/B_T5c/edge_partition_ids.npz",
                 "stimulus":"stimulus.npy", "initial":"initial_state_full.npy", "time":"time.npy",
                 "activity_time":"activity_time.npy", "numeric":"numeric_profile.json", "metrics":"metric_profile.json"}
        require(set(f) == set(roles) | {"model"} and f["model"] == MODEL_SHA, "Wrong comparison identity keys/model")
        for role, name in roles.items():
            require(f[role] == self.checked[(self.root/name).resolve()], f"Fingerprint mismatch: {role}")
        self.comparison_id = hashlib.sha256(json.dumps(f, sort_keys=True).encode()).hexdigest()
        require(self.comparison_id == m["comparison_id"], "Wrong computed comparison_id")
        require(identity["model_id"] == "flow/0000/000" and identity["source_commit"] == video.identity["source_commit"] and identity["n_nodes"] == 45669 and identity["n_edges"] == 1513231 and identity["parameter_profile"] == "OFFICIAL_NATIVE_GPU_EXPANDED", "Wrong model/parameter profile")
        require(identity["checkpoint_sha256"] == f["model"] and identity["expanded_parameters_sha256"] == f["expanded"] and identity["initial_state_sha256"] == f["initial"] == INITIAL_SHA, "Common model/initial identity mismatch")
        # Existing accepted source anchors also bind decoded PNG frames and 721 geometry.
        require(Path(m["source_mp4"]).resolve() == video.paths["source_video_1"] and Path(m["parent_stimulus_path"]).resolve() == video.paths["stimulus"], "Video/parent path differs from accepted source")
        self.check(video.paths["source_video_1"], m["source_mp4_sha256"])
        self.check(video.paths["stimulus"], m["parent_stimulus_sha256"])
        require(m["parent_stimulus_sha256"] == PARENT_SHA, "Wrong parent stimulus identity")
        self.stimulus, self.initial = load("stimulus.npy"), load("initial_state_full.npy")
        require(self.stimulus.shape == (1,800,1,721) and self.stimulus.dtype == np.dtype("<f4") and self.stimulus.tobytes() == np.ascontiguousarray(video.stimulus[1:2]).tobytes(), "Single condition is not the exact float32 slice")
        require(self.initial.shape == (1,45669) and self.initial.dtype == np.dtype("<f4") and np.isfinite(self.initial).all() and identity["initial_state_shape"] == [1,45669], "Wrong initial state axes/values")
        require(array_digest(self.initial.reshape(-1)) == identity["initial_state_flat_digest"], "Wrong explicit flattened initial digest")
        self.time, self.activity_time = load("time.npy"), load("activity_time.npy")
        require(np.array_equal(self.time,np.arange(800)*.005) and np.array_equal(self.activity_time,self.time+.005), "Wrong input/Euler time axes")
        self.central_ids, self.input_ids = load("central_node_indices.npy"), load("input_node_indices.npy")
        self.cells = load("cell_types.npy").tolist()
        require(self.cells == video.cells and np.array_equal(self.central_ids,[n["original_node_index"] for n in video.neurons]), "Wrong center readout mapping")
        require(self.input_ids.shape == (8,721) and self.input_ids.dtype.kind in "iu" and len(np.unique(self.input_ids)) == 5768 and self.input_ids.min() >= 0 and self.input_ids.max() < 45669, "Invalid input mapping")
        candidate = read_json(self.root/"candidates/B_T5c/candidate_manifest.json")
        self.h_ids = np.asarray(candidate["h_global_node_indices"],dtype=np.int64)
        self.r_ids = np.setdiff1d(np.arange(45669),self.h_ids)
        require(len(np.unique(self.h_ids)) == 67 and self.h_ids.min() >= 0 and self.h_ids.max() < 45669 and candidate["partition_counts"] == {"HH":970,"RH":5567,"HR":8159,"RR":1498535}, "Wrong 67-node T5c partition")
        require(candidate["checkpoint_sha256"] == f["model"] and candidate["expanded_parameters_sha256"] == f["expanded"] and candidate["source_node_map_sha256"] == f["node_map"], "Candidate model/order identity differs")
        with np.load(self.root/"static_boundary_gpu_native.npz",allow_pickle=False) as z:
            self.source_ids = np.array(z["incoming_source_global_node_id"],copy=True)
            require(len(self.source_ids) == 1364 and np.array_equal(z["global_node_id"],self.h_ids), "Wrong SOURCE_RAW layout")
        require(self.metrics["registered_before_execution"] is True and self.metrics["post_hoc_tolerance_relaxation"] is False and self.metrics["nonfinite_allowed"] == 0 and self.metrics["atol"] == self.metrics["rtol"] == 1e-5, "Wrong preregistered software metric policy")
        coordinates = [numeric_row(r) for r in read_csv(self.root/"input_hex_coordinates.csv")]
        require([(r["u"],r["v"]) for r in coordinates] == [(r["u"],r["v"]) for r in video.coordinates], "Wrong 721 geometry/order")
        require(np.isfinite(self.stimulus).all() and np.array_equal(self.stimulus[0,:,0],video.source_hex[1,video.source_indices]), "Input is not causal held source hex values")
        self.alignment = [numeric_row(r) for r in read_csv(self.root/"time_alignment.csv")]
        require(len(self.alignment) == 800, "Incomplete time alignment")
        for k,row in enumerate(self.alignment):
            source = int(video.source_indices[k])
            require(row["model_frame"] == k and row["model_time_s"] == self.time[k] and row["source_left_frame"] == row["source_right_frame"] == source and row["source_left_time_s"] == row["source_right_time_s"] == video.source_time[source] and row["right_weight"] == 0 and str(row["uses_future_frame"]).lower() == "false", "Wrong causal source frame/step mapping")
        self.assert_unchanged()

    def assert_unchanged(self):
        super().assert_unchanged()
        self.video.assert_unchanged()

    def info(self):
        self.assert_unchanged()
        return {"status":"verified_frozen_input", "comparison_id":self.comparison_id,
                "condition_id":"01_off_right", "original_sample":1, "steps":800, "dt_s":.005,
                "source_kind":"synthetic_controlled_video", "source_is_camera":False,
                "source_video_sha256":self.manifest["source_mp4_sha256"], "identity_fingerprint":self.fingerprint,
                "initial_state_shape":[1,45669], "initial_shape_rule":"same file bytes; reshape view to [45669]",
                "input_time_s":self.time.tolist(), "activity_time_s":self.activity_time.tolist(),
                "source_time_s":self.video.source_time.tolist(), "input_source_indices":self.video.source_indices.tolist(),
                "stimulus":{"dtype":"<f4","shape":[800,721],"url":"/api/phase3/input/stimulus.bin"},
                "frame_url_template":"/api/phase3/input/frames/{source_frame}.png", "verified_files":len(self.checked),
                "hardware_target":{"candidate":"B_T5c","H_nodes":67,"R_nodes":45602,"boundary":"SOURCE_RAW","boundary_sources":1364},
                "scope":"Input/file/time identity only; no Full/Replacement run accepted by this preflight"}


class ComparisonPackage(VerifiedFiles):
    """Prepared reader. No software mode opens until pinned B acceptance exists."""
    def recompute_errors(self):
        frozen = self.frozen
        full, replacement = self.arrays["Full_GPU"],self.arrays["Python_Replacement"]
        for label,ids in {"H":frozen.h_ids,"R":frozen.r_ids,"full":np.arange(45669),"central65":frozen.central_ids,"T4T5":frozen.central_ids[[frozen.cells.index(c) for c in TARGETS]]}.items():
            self.errors[label] = {key:[] for key in ["max_abs","MAE","RMSE","violations"]}
            for start in range(0,800,16):
                reference = full[start:start+16,ids].astype(np.float64)
                delta = replacement[start:start+16,ids].astype(np.float64)-reference
                limit = frozen.metrics["atol"] + frozen.metrics["rtol"]*np.abs(reference)
                violations = np.count_nonzero(np.abs(delta)>limit,axis=1)
                require(not violations.any(),f"Preregistered numerical threshold failed: {label}")
                values = {"max_abs":np.max(np.abs(delta),axis=1),"MAE":np.mean(np.abs(delta),axis=1),"RMSE":np.sqrt(np.mean(delta*delta,axis=1)),"violations":violations}
                for key,value in values.items():
                    self.errors[label][key].extend(value.tolist())

    def verify_chain(self, mode, run):
        f = self.frozen
        events = [json.loads(line) for line in self.roles[run["step_status_role"]].read_text(encoding="utf-8").splitlines() if line.strip()]
        count = 1 if mode == "Full_GPU" else 2
        require(len(events) == 800*count,"Incomplete/extra transaction events")
        before = f.initial.reshape(-1)
        for k, after in enumerate(self.arrays[mode]):
            row = events[k*count]
            require(row["step_id"] == k,"Non-contiguous step chain")
            if mode == "Full_GPU":
                digest = (lambda a: hashlib.sha256(str(a.dtype).encode()+str(a.shape).encode()+a.tobytes()).hexdigest()) if run.get("digest_profile") == "A_STR_DTYPE_SHAPE_BYTES" else array_digest
                require(row["status"] == "FULL_REFERENCE_ONLY" and row["before_digest"] == digest(before) and row["after_digest"] == digest(after) and row["input_digest"] == digest(f.stimulus[0,k,0]),"Full step digest not bound to input/state")
            else:
                commit = events[k*2+1]
                x = np.zeros(45669,dtype=np.float32)
                x[f.input_ids.reshape(-1)] = np.tile(f.stimulus[0,k,0],8)
                require(row["status"] == "PREPARED" and row["old_full_digest"] == array_digest(before) and row["old_H_digest"] == array_digest(before[f.h_ids]) and row["live_R_source_digest"] == array_digest(before[f.source_ids]) and row["input_digest"] == array_digest(x),"Prepared step is not bound to old H/R/current input")
                require(commit["status"] == "COMMITTED" and commit["step_id"] == k and commit["state_token"] == k+1 and commit["input_digest"] == row["input_digest"] and commit["full_after_digest"] == array_digest(after) and commit["H_after_digest"] == array_digest(after[f.h_ids]) and commit["R_after_digest"] == array_digest(after[f.r_ids]) and commit["native_H_update_count"] == 0 and commit["H_request_digest"] == row["request_digest"] and commit["epoch"] == row["epoch"],"Commit state digest/order differs")
            before = after

    def assert_unchanged(self):
        super().assert_unchanged()
        self.frozen.assert_unchanged()

    def info(self):
        self.assert_unchanged()
        return {"comparison_id":self.frozen.comparison_id,"status":"verified_software_result_replay","display_kind":"offline_replay",
                "identity_fingerprint":self.frozen.fingerprint,"modes":self.descriptor["modes"],"cell_types":self.frozen.cells,"central_global_ids":self.frozen.central_ids.tolist(),
                "errors":self.errors,"error_definition":"replacement - Full; IEEE float64 comparison; preregistered atol/rtol; not DSI",
                "FPGA_Replacement":{"available":False,"status":"unavailable","evidence_level":None,"board_id":None,"bit_sha256":None,"hwh_sha256":None,"pl_cycles":None,"latency":None}}


class Phase3Adapter:
    def init__(self, store, config_path=None):
        self.input, self.packages, self.errors = None,{},[]
        try:
            config = read_json(config_path or store.root/"gui_v1/phase3.json")
            require(config["schema"] == "flyvis-gui-phase3-imports-v1","Unknown phase3 config")
            self.input = FrozenVideoInput(config,store.root,store.datasets.get("controlled6"))
            for spec in config["comparison_packages"]:
                try:
                    if spec.get("schema") == "B_GUI_ANIMATION_RESULTS/v1":
                        from native_comparison import NativeAnimationComparison
                        package = NativeAnimationComparison(spec,self.input)
                    else:
                        raise ValueError("Unknown explicitly admitted comparison schema")
                    require(package.frozen.comparison_id not in self.packages,"Duplicate admitted comparison")
                    self.packages[package.frozen.comparison_id] = package
                except (OSError,ValueError,KeyError,TypeError,AssertionError) as error:
                    self.errors.append(str(error))
        except (OSError,ValueError,KeyError,TypeError,AssertionError,ImportError) as error:
            self.errors.append(str(error))

    def status(self):
        try:
            frozen = self.input.info() if self.input else None
            packages = [p.info() for p in self.packages.values()]
        except (OSError,ValueError) as error:
            return {"status":"unavailable","display_kind":None,"input":None,"comparisons":[],"error":str(error),"FPGA_Replacement":{"available":False,"status":"unavailable"}}
        return {"schema":"flyvis-gui-phase3-status-v1","status":"ready" if packages else "waiting_for_accepted_comparison" if frozen else "input_unavailable",
                "display_kind":"offline_replay" if packages else None,"input":frozen,"comparisons":packages,"errors":self.errors,
                "Full_GPU":{"available":bool(packages),"status":"verified_result_replay" if packages else "waiting_for_B_matching_Full"},
                "Python_Replacement":{"available":bool(packages),"status":"verified_result_replay" if packages else "waiting_for_B_800_SOURCE_RAW"},
                "FPGA_Replacement":{"available":False,"status":"unavailable","reason":"No accepted C board execution handoff","board_id":None,"device":None,"run_id":None,"model_identity":None,"circuit_identity":None,"bit_sha256":None,"hwh_sha256":None,"activity_error":None,"pl_cycles":None,"evidence_level":None,
                                    "latency_s":{k:None for k in ["gpu_compute","ps_compute","pl_compute","gpu_ps_transfer","ps_pl_transfer","step_p50","step_p95","step_p99","total"]}},
                "online_GPU_service":"not_connected"}
