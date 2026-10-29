"""Independent consumer of B's delivered B_GUI_ANIMATION_RESULTS/v1 contract.

Reads pinned outputs only. Never imports or executes B's reader/common/H code.
"""
from pathlib import Path
import numpy as np

from camera_store import inside, require
from data_store import ROOT, TARGETS, read_json
from phase3_adapter import VerifiedFiles, ComparisonPackage

B_ROOT = ROOT.parent/"fpga/flyvis-circuit-selection/phase3_20261010"
A_ROOT = ROOT/"gpu_phase3_fixed_video_20261010"


class NativeAnimationComparison(ComparisonPackage):
    def init__(self,spec,frozen):
        VerifiedFiles.init__(self)
        self.frozen,self.roles,self.arrays,self.errors = frozen,{},{},{}
        self.root = Path(spec["directory"]).resolve()
        require(self.root == (B_ROOT/"gui_bundle").resolve(),"Unknown B GUI handoff directory")
        self.verify_inventory(self.root,spec["manifest_sha256"])
        desc = read_json(self.check(self.root/"GUI_READONLY_HANDOFF.json",spec["descriptor_sha256"]))
        require(desc["schema"] == "B_GUI_ANIMATION_RESULTS/v1" and desc["status"] == "PASS_SOFTWARE_RESULTS_READY_FOR_GUI_READ_ONLY_INTEGRATION","B GUI software handoff not accepted")
        require(desc["comparison_id"] == frozen.comparison_id and desc["condition_id"] == "01_off_right" and desc["steps"] == 800 and desc["dt_s"] == .005,"Wrong B comparison/condition/time")
        require(Path(desc["video_path"]).resolve() == frozen.video.paths["source_video_1"] and desc["video_sha256"] == frozen.manifest["source_mp4_sha256"],"Wrong video identity")
        require(desc["FPGA_execution"] is False and set(desc["mode_status"]) == {"FullGPU","PythonReplacement","FPGAReplacement"} and desc["mode_status"]["FPGAReplacement"] == {"available":False,"status":"NOT_RUN","reason":"C reviewed actual PL backend/board800 evidence not delivered","fallback":False},"Unaccepted hardware claim")
        load=lambda path:np.load(path,allow_pickle=False,mmap_mode="r")
        for filename,expected in [("stimulus.npy",frozen.stimulus),("time.npy",frozen.time),("activity_time.npy",frozen.activity_time),("central_global_ids.npy",frozen.central_ids),("H_global_ids.npy",frozen.h_ids)]:
            require(np.array_equal(load(self.root/filename),expected),f"B GUI common array mismatch: {filename}")
        require(load(self.root/"central_cell_types.npy").tolist() == frozen.cells,"B cell axis differs")
        t4t5 = frozen.central_ids[[frozen.cells.index(c) for c in TARGETS]]
        require(np.array_equal(load(self.root/"T4T5_global_ids.npy"),t4t5),"B T4/T5 ID mapping differs")
        self.audit = read_json(self.check(B_ROOT/"artifacts/audit_800_r1/result.json",spec["audit_sha256"]))
        self.causal = read_json(self.check(B_ROOT/"artifacts/live_feedback_r1/result.json",spec["causal_sha256"]))
        self.verify_inventory(B_ROOT/"artifacts/audit_800_r1",spec["audit_manifest_sha256"])
        self.verify_inventory(B_ROOT/"artifacts/live_feedback_r1",spec["causal_manifest_sha256"])
        a=self.audit
        require(a["status"] == "PASS_INDEPENDENT_800_STATE_CHAIN_AND_VECTOR_AUDIT" and a["comparison_id"] == frozen.comparison_id and a["prepared"] == a["committed"] == 800 and a["initial_state_exact"] and a["all_state_hashes_match"] and a["live_R_boundary_from_own_old_state"] and a["native_H_production_updates"] == 0,"B independent state chain audit incomplete")
        c=self.causal
        require(c["status"] == "PASS_LIVE_FEEDBACK_AND_GPU_NEGATIVE_TESTS" and c["actual_GPU_service_tested"] and c["actual_GPU_R_calls"] > 0 and c["input_bundle_unchanged"],"B actual causal/fault acceptance missing")
        require(c["comparison_id"] == frozen.comparison_id and c["stimulus_sha256"] == frozen.fingerprint["stimulus"] and c["initial_state_sha256"] == frozen.fingerprint["initial"] and c["expanded_parameters_sha256"] == frozen.fingerprint["expanded"] and c["source_checkpoint"]["sha256"] == desc["mode_status"]["PythonReplacement"]["source_all_nodes_sha256"],"Causal report belongs to different input/state/run")
        require(c["fault_production_guard"]["forbidden_native_call_count"] == c["causal_production_guard"]["forbidden_native_call_count"] == 0 and all(c["feedback"][key] != 0 for key in ["H_to_R_next_delta","R_to_H_next_delta","returned_R_causal_contribution_to_H_after_second_step"]),"Causal/native-H guard incomplete")
        require(c["negative_tests"] and all(t["status"] == "PASS" for t in c["negative_tests"]),"B negative tests not all accepted")
        modes={}
        for own,name,parent in [("Full_GPU","FullGPU",A_ROOT/"artifacts/full_gpu_800_r1"),("Python_Replacement","PythonReplacement",B_ROOT/"artifacts/python_source_raw_800_r2")]:
            source=desc["mode_status"][name]
            require(source["available"] is True and source["execution_kind"] == "actual_new_computation" and source["display_mode"] == "offline_replay_of_actual_computation","Recorded output cannot claim a live execution")
            require(Path(source["source_all_nodes_path"]).resolve() == (parent/"activities_full.npy").resolve(),"Wrong native source path")
            self.verify_inventory(parent,spec["run_manifest_sha256"][own])
            self.check(parent/"activities_full.npy",source["source_all_nodes_sha256"])
            arr=load(parent/"activities_full.npy")
            require(arr.shape == (1,800,45669) and arr.dtype == np.dtype("<f4") and np.isfinite(arr).all(),"Wrong real full trajectory axes/values")
            self.arrays[own]=arr[0]
            identity=read_json(parent/"run_identity.json");result=read_json(parent/"result.json")
            require(read_json(self.root/name/"run_identity.json") == identity and read_json(self.root/name/"result.json") == result,"B GUI identity/result copy differs from actual run")
            require(identity["run_id"] == source["run_id"] and identity["comparison_id"] == frozen.comparison_id and identity["mode"] == name and identity["condition_id"] == "01_off_right" and identity["original_sample"] == 1 and identity["steps"] == 800 and identity["dt_s"] == .005 and identity["layout"] == "SOURCE_RAW" and identity["execution_kind"] == "actual_new_computation" and identity["gpu"] and "+cu" in identity["torch"],"Wrong original computation identity")
            for key,role in {"checkpoint_sha256":"model","expanded_parameters_sha256":"expanded","initial_state_sha256":"initial","stimulus_sha256":"stimulus","time_sha256":"time","activity_time_sha256":"activity_time","candidate_sha256":"candidate","node_map_sha256":"node_map","numeric_profile_sha256":"numeric","metric_profile_sha256":"metrics"}.items():
                require(identity[key] == frozen.fingerprint[role],f"Actual run common identity differs: {key}")
            require(result["status"] == ("PASS_ACTUAL_FULL_800" if own == "Full_GPU" else "PASS_CLOSED_LOOP_NUMERICAL") and result["steps"] == 800 and result["nonfinite"] == 0 and result["input_bundle_unchanged"] and result["wall_s"] > 0,"Actual computation not complete/valid")
            if own == "Python_Replacement":
                require(result["independent_H_steps"] == result["unified_committed_steps"] == 800 and result["native_H_production_updates"] == result["production_guard"]["forbidden_native_call_count"] == 0 and result["full_arrays_as_production_boundary"] is False,"Python source/raw guard incomplete")
            for group,ids in [("central",frozen.central_ids),("H",frozen.h_ids),("T4T5",t4t5)]:
                activity=load(self.root/name/f"activity_{group}.npy")
                require(activity.shape == (800,len(ids)) and activity.dtype == np.dtype("<f4") and np.array_equal(activity,self.arrays[own][:,ids]),"B readout not exact original node activity")
            activity_role,chain_role = own+"_full",own+"_steps"
            self.roles[activity_role],self.roles[chain_role] = parent/"activities_full.npy",parent/"step_status.jsonl"
            run={"run_id":identity["run_id"],"comparison_id":frozen.comparison_id,"origin_execution_kind":identity["execution_kind"],"evidence_level":identity["execution_evidence_level"],"device":identity["gpu"],"wall_s":result["wall_s"],"step_latency_ms":result["step_latency_ms"],"timing_scope":result["timing_scope"],"activity_full_role":activity_role,"step_status_role":chain_role,"source_activity_sha256":source["source_all_nodes_sha256"],"digest_profile":"A_STR_DTYPE_SHAPE_BYTES" if own == "Full_GPU" else "B_JSON_DTYPE_SHAPE_BYTES"}
            self.verify_chain(own,run)
            modes[own]=run
        require(modes["Full_GPU"]["run_id"] != modes["Python_Replacement"]["run_id"] and a["Full_run_id"] == modes["Full_GPU"]["run_id"] and a["Python_run_id"] == modes["Python_Replacement"]["run_id"],"Audit belongs to different run pair")
        self.descriptor={"comparison_id":frozen.comparison_id,"modes":modes,"original_B_descriptor":desc}
        self.recompute_errors()
        for summary in a["summary"]:
            label="central65" if summary["group"] == "central" else summary["group"]
            error=self.errors[label]
            require(max(error["max_abs"]) == summary["max_abs"] and sum(error["violations"]) == summary["violations"] == 0,"GUI independent error differs from B audit")
        self.assert_unchanged()

    def verify_inventory(self,folder,expected_sha):
        self.check(folder/"artifact_manifest.json",expected_sha)
        entries=read_json(folder/"artifact_manifest.json")
        if isinstance(entries,dict):entries=entries["files"]
        names=set()
        for entry in entries:
            require(entry["path"] not in names,"Duplicate B/A manifest entry")
            names.add(entry["path"])
            self.check(inside(folder,entry["path"]),entry["sha256"],entry["bytes"])

    def info(self):
        info=super().info()
        info["verification"]={"files":len(self.checked),"state_chain_steps":800,"source_arrays_exact":True,"GUI_neural_inference_executed":False,"B_causal_report_status":self.causal["status"],"B_independent_audit_status":self.audit["status"]}
        return info
