"""Independent CPU verification of B's saved runs against A's frozen Full.

Read-only in B's tree. This does not run H/R, import torch or make GPU/PL calls.
The detailed SOURCE_RAW/state-chain acceptance remains B's own separate audit.
"""
import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode=True
import numpy as np
from run_camera_full import HERE, FPGA, BUNDLE, load, dump, digest, verify_bundle


def verify_seal(root):
    path=root/"artifact_manifest.json"
    document=load(path)
    entries=document["files"] if isinstance(document,dict) else document
    if isinstance(entries,dict):
        entries=[dict(path=k,sha256=v) for k,v in entries.items()]
    for item in entries:
        p=(root/item["path"]).resolve()
        assert p.is_relative_to(root.resolve()) and digest(p)==item["sha256"],p
    return dict(path=str(path),sha256=digest(path),files=len(entries))


def main(receipt_name):
    if not receipt_name or Path(receipt_name).name!=receipt_name:raise ValueError("Receipt requires a plain directory name")
    out=HERE/receipt_name
    if out.exists():raise RuntimeError("Existing receipt preserved")
    out.mkdir()
    binding=verify_bundle()
    b_root=FPGA/"flyvis-circuit-selection/phase4_camera_replacement_20261011_r1"
    a_root=HERE/"artifacts/full_gpu_609_r1"
    seals=[verify_seal(a_root)]
    full=np.load(a_root/"activities_full.npy",mmap_mode="r",allow_pickle=False)
    h_ids=np.asarray(load(BUNDLE/"candidates/B_T5c/candidate_manifest.json")["h_global_node_indices"],dtype=np.int64)
    groups=dict(H=h_ids,R=np.setdiff1d(np.arange(45669),h_ids),full=np.arange(45669))
    metrics=[];ids=[];traces=[]
    keys=["comparison_id","condition_id","backend_binding_id","checkpoint_sha256","source_commit",
          "expanded_parameters_sha256","initial_state_sha256","stimulus_sha256","time_sha256","activity_time_sha256",
          "candidate_sha256","node_map_sha256","steps","dt_s"]
    a_identity=load(a_root/"run_identity.json")
    for name in ["python_camera_609_r2","python_camera_609_r3"]:
        root=b_root/"artifacts"/name
        seals.append(verify_seal(root))
        ident=load(root/"run_identity.json");result=load(root/"result.json")
        assert all(ident[k]==a_identity[k] for k in keys)
        assert ident["mode"]=="PythonReplacement" and result["status"]=="PASS_CLOSED_LOOP_NUMERICAL"
        assert result["native_H_production_updates"]==result["production_guard"]["forbidden_native_call_count"]==0
        assert result["independent_H_steps"]==result["unified_committed_steps"]==609
        assert result["full_arrays_as_production_boundary"] is False and result["FPGA_execution"] is False
        for relative,sha in ident["code_sha256"].items():assert digest(b_root/relative)==sha,relative
        trace=np.load(root/"activities_full.npy",mmap_mode="r",allow_pickle=False)
        assert trace.shape==full.shape==(1,609,45669) and trace.dtype==np.float32
        rows=[];summed={g:0. for g in groups};maxima={g:0. for g in groups};violations={g:0 for g in groups}
        for k in range(609):
            actual=trace[0,k].astype(np.float64);ref=full[0,k].astype(np.float64)
            assert np.isfinite(actual).all()
            d=actual-ref
            row=dict(step_id=k,run=name)
            for group,indices in groups.items():
                ds=d[indices];sq=float(np.sum(ds*ds))
                mx=float(np.abs(ds).max());bad=int(np.count_nonzero(np.abs(ds)>1e-5+1e-5*np.abs(ref[indices])))
                summed[group]+=sq;maxima[group]=max(maxima[group],mx);violations[group]+=bad
                row.update({group+"_max_abs":mx,group+"_rmse":float(np.sqrt(np.mean(ds*ds))),group+"_violations":bad})
            rows.append(row)
            if k+1 in [1,32,609]:
                metrics.append(dict(run=name,prefix_steps=k+1,groups={g:dict(max_abs=maxima[g],
                    rmse=float(np.sqrt(summed[g]/((k+1)*len(indices)))),violations=violations[g]) for g,indices in groups.items()}))
        assert all(v==0 for v in violations.values())
        assert all(maxima[g]==result["max_abs"][g] for g in groups)
        with (out/(name+"_errors.csv")).open("w",newline="") as f:
            writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
        ids.append(ident["run_id"]);traces.append(trace)
    assert ids[0]!=ids[1]
    replay=max(float(np.abs(traces[0][0,k].astype(np.float64)-traces[1][0,k].astype(np.float64)).max()) for k in range(609))
    replay_bitwise=all(np.array_equal(traces[0][0,k],traces[1][0,k]) for k in range(609))
    probe_root=b_root/"artifacts/camera_live_feedback_r1"
    seals.append(verify_seal(probe_root));probe=load(probe_root/"result.json")
    assert probe["comparison_id"]==binding["comparison_id"]
    assert probe["status"]=="PASS_LIVE_FEEDBACK_AND_GPU_NEGATIVE_TESTS" and probe["actual_GPU_service_tested"] is True
    assert len(probe["negative_tests"])==15 and all(t["status"]=="PASS" for t in probe["negative_tests"])
    assert probe["fault_production_guard"]["forbidden_native_call_count"]==probe["causal_production_guard"]["forbidden_native_call_count"]==0
    assert probe["positive_guard_control"]["forbidden_native_call_count"]==1
    feedback=probe["feedback"]
    assert feedback["H_to_R_next_delta"]!=0 and feedback["R_to_H_next_delta"]!=0 and feedback["returned_R_causal_contribution_to_H_after_second_step"]!=0
    handoff=b_root/"B_CAMERA_609_HANDOFF.json"
    receipt=dict(status="PASS_A_INDEPENDENT_B_REFERENCE_NUMERICS",recorded_utc=datetime.now(timezone.utc).isoformat(),
        scope="A independently verified B saved file seals, shared identities, raw Full comparison and fresh-process repeat; B owns detailed SOURCE_RAW/state-chain audit",
        comparison_id=binding["comparison_id"],backend_binding_id=binding["backend_binding_id"],B_run_ids=ids,
        verified_manifests=seals,prefix_metrics=metrics,independent_B_repeat_max_abs=replay,
        independent_B_repeat_bitwise=replay_bitwise,negative_tests_recorded_pass=15,feedback_record=feedback,
        GPU_calls_in_this_verification=0,PL_calls_in_this_verification=0,FPGAReplacement="NOT_CONNECTED",
        B_final_handoff_present=handoff.exists(),B_final_handoff_sha256=digest(handoff) if handoff.exists() else None,
        B_final_handoff=load(handoff) if handoff.exists() else None,
        verifier_source_sha256=digest(Path(__file__)),command=[sys.executable,*sys.argv])
    dump(out/"receipt.json",receipt)
    dump(out/"artifact_manifest.json",dict(files=[dict(path=p.name,sha256=digest(p)) for p in sorted(out.iterdir()) if p.is_file() and p.name!="artifact_manifest.json"]))
    print(json.dumps(dict(status=receipt["status"],B_repeat_bitwise=replay_bitwise,B_repeat_max_abs=replay,
        final_metrics=[v for v in metrics if v["prefix_steps"]==609],B_handoff_present=handoff.exists(),GPU_calls=0,PL_calls=0)))


if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--receipt",required=True)
    args=parser.parse_args();main(args.receipt)
