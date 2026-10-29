"""CPU-only delivery audit and scientific figures for the recorded camera clip."""
import csv
import hashlib
import json
import os
import subprocess
from pathlib import Path, PurePosixPath

os.environ.update(MPLBACKEND="Agg")
import numpy as np
import matplotlib.pyplot as plt
from run_camera_full import HERE, BUNDLE, FLY, INPUT, COMPARISON, load, dump, digest, verify_bundle, manifest


def array_digest(a):
    return hashlib.sha256(str(a.dtype).encode()+str(a.shape).encode()+a.tobytes()).hexdigest()


def windows_path(value):
    p=PurePosixPath(str(value))
    if len(p.parts)>3 and p.parts[1]=="mnt":
        return p.parts[2].upper()+":\\"+"\\".join(p.parts[3:])
    return str(value)


def main():
    binding=verify_bundle()
    root=HERE/"artifacts/full_gpu_609_r1"
    identities=[load(HERE/"artifacts"/r/"run_identity.json") for r in ["full_gpu_609_r1","full_gpu_609_r2"]]
    states=np.load(root/"activities_full.npy",mmap_mode="r",allow_pickle=False)
    x=np.load(BUNDLE/"stimulus.npy",allow_pickle=False)
    t=np.load(BUNDLE/"time.npy",allow_pickle=False)
    after_t=np.load(BUNDLE/"activity_time.npy",allow_pickle=False)
    initial=np.load(BUNDLE/"initial_state_full.npy",allow_pickle=False)[0]
    central=np.load(BUNDLE/"central_node_indices.npy",allow_pickle=False)
    types=np.load(BUNDLE/"cell_types.npy",allow_pickle=False)
    activity=np.load(root/"activity_central.npy",allow_pickle=False)
    checks=[]
    def require(name,ok):
        checks.append(dict(check=name,status="PASS" if ok else "FAIL"))
        assert ok,name
    require("exact609_all_node_float32_trajectory",states.shape==(1,609,45669) and states.dtype==np.float32)
    require("central65_gather_exact",np.array_equal(states[:,:,central],activity))
    require("activity_clock_is_input_plus_dt",np.array_equal(after_t,t+.005))
    require("exact609_unpadded_input_clock",np.array_equal(t,np.arange(609)*.005))
    require("initial_is_full_not65_or_bias",initial.shape==(45669,) and np.isfinite(initial).all())
    with (root/"step_status.jsonl").open() as f:rows=[json.loads(line) for line in f]
    require("609_step_log_rows",len(rows)==609)
    prior=array_digest(initial)
    for k,row in enumerate(rows):
        require("step_%03d_state_input_clock_chain"%k,
            row["step_id"]==k and row["comparison_id"]==COMPARISON and row["before_digest"]==prior
            and row["input_digest"]==array_digest(x[0,k,0])
            and row["after_digest"]==array_digest(states[0,k])
            and row["input_time_s"]==t[k] and row["activity_after_time_s"]==after_t[k])
        prior=row["after_digest"]
    require("final_state_exact",np.array_equal(states[0,-1],np.load(root/"final_state_full.npy")))
    replay=load(HERE/"INDEPENDENT_REPLAY_ACCEPTANCE.json")
    require("fresh_process_run_ids_distinct",identities[0]["run_id"]!=identities[1]["run_id"])
    require("full609_fresh_process_replay_bitwise",replay["all_steps_bitwise"] and replay["max_abs"]==0)
    for ident in identities:
        require("run_"+ident["run_id"]+"_same_backend_binding",ident["backend_binding_id"]==binding["backend_binding_id"])
        for name,sha in ident["code_sha256"].items():
            require("source_unchanged_"+Path(name).name,digest(name)==sha)
    source=FLY/"upstream/flyvis"
    commit=subprocess.check_output(["git","-C",str(source),"rev-parse","HEAD"],text=True).strip()
    dirty=subprocess.check_output(["git","-C",str(source),"status","--porcelain","--untracked-files=no"],text=True).strip()
    require("official_source_commit_and_tracked_clean",commit==binding["source_commit"] and not dirty)
    require("sealed_input_file_unchanged",digest(INPUT/"stimulus.npy")==binding["stimulus_sha256"])
    require("time_files_copied_byte_exact",digest(root/"time.npy")==binding["time_sha256"] and digest(root/"activity_time.npy")==binding["activity_time_sha256"])
    statistics=[]
    for i,(ctype,global_id) in enumerate(zip(types,central)):
        a=activity[0,:,i].astype(np.float64)
        d=a-float(initial[global_id])
        statistics.append(dict(cell_type=str(ctype),global_node_index=int(global_id),initial_activity=float(initial[global_id]),
            min_activity=float(a.min()),max_activity=float(a.max()),peak_to_peak=float(np.ptp(a)),
            max_abs_change_from_bound_a0=float(np.abs(d).max()),rms_change_from_bound_a0=float(np.sqrt(np.mean(d*d))),
            final_activity=float(a[-1])))
    with (HERE/"central65_activity_statistics.csv").open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(statistics[0]));writer.writeheader();writer.writerows(statistics)
    fig,axes=plt.subplots(3,1,figsize=(10,8),sharex=True,constrained_layout=True)
    axes[0].plot(t,x[0,:,0].mean(axis=1),color="black",linewidth=1)
    axes[0].set(ylabel="Mean hex input",title="Recorded phone-screen camera clip: selected frames 100-190")
    for ax,family in zip(axes[1:],["T4","T5"]):
        for suffix in "abcd":
            i=int(np.flatnonzero(types==family+suffix)[0])
            ax.plot(after_t,activity[0,:,i].astype(np.float64)-float(initial[central[i]]),label=family+suffix)
        ax.set(ylabel="Activity change from a0")
        ax.legend(ncol=4)
        ax.grid(alpha=.2)
    axes[-1].set_xlabel("Local model time (s); neural samples are after each 5 ms update")
    fig.savefig(HERE/"recorded_camera_T4_T5.png",dpi=160)
    fig.savefig(HERE/"recorded_camera_T4_T5.pdf")
    plt.close(fig)
    delta=activity[0].astype(np.float64)-initial[central].astype(np.float64)
    limit=float(np.abs(delta).max())
    fig,ax=plt.subplots(figsize=(11,10),constrained_layout=True)
    im=ax.imshow(delta.T,aspect="auto",origin="lower",extent=[float(after_t[0]),float(after_t[-1]),-.5,64.5],
                 cmap="RdBu_r",vmin=-limit,vmax=limit)
    ax.set_yticks(np.arange(65),types,fontsize=7)
    ax.set(xlabel="Local time after update (s)",title="65 central neurons: activity change from the same complete a0")
    fig.colorbar(im,ax=ax,label="Original continuous activity units")
    fig.savefig(HERE/"recorded_camera_central65.png",dpi=160)
    plt.close(fig)
    result=dict(status="PASS_A_RECORDED_CAMERA_FULL_GPU_REFERENCE",comparison_id=COMPARISON,
        backend_binding_id=binding["backend_binding_id"],check_count=len(checks),checks=checks,
        software_execution="two actual original Full GPU fresh-process609 runs",all_steps_nodes_bitwise=True,
        gpu_r_executed_by_A=False,python_replacement="owned by B; not part of A PASS",fpga_replacement="NOT_CONNECTED",
        board_used=False,source_commit=commit,official_tracked_source_clean=True,
        limitations=["Frozen camera input replay, not live camera inference or a realtime guarantee",
                     "Handheld camera and unverified exposure remain; no DSI/speed or biological direction claim",
                     "Original float32 profile; Q22/Q24 hardware comparison needs a separate shared representablea0 and identity"])
    dump(HERE/"DELIVERY_ACCEPTANCE.json",result)
    handoff=load(HERE/"CAMERA_BACKEND_HANDOFF.json")
    handoff["windows_paths"]={k:windows_path(handoff[k]) for k in ["common_bundle","full_gpu_root","replay_root","activities_full",
        "initial_state","identity_manifest","expanded_parameters","native_r_only_source","input_reader","binding"]}
    handoff["condition_id"]="selected_100_190"
    handoff["gpu_coordination_path"]=str(HERE/"GPU_COORDINATION_CAMERA.json")
    handoff["gpu_coordination_sha256"]=digest(HERE/"GPU_COORDINATION_CAMERA.json")
    handoff["full_gpu_reference_sha256"]=digest(root/"activities_full.npy")
    handoff["full_gpu_reference_run_id"]=identities[0]["run_id"]
    dump(HERE/"CAMERA_BACKEND_HANDOFF.json",handoff)
    dump(HERE/"demo_payload.json",dict(schema="camera-full-reference-display/v1",comparison_id=COMPARISON,
        run_id=identities[0]["run_id"],mode="FullGPU",execution_kind="ACTUAL_COMPUTATION_SAVED_FOR_OFFLINE_DISPLAY",
        input_source="recorded_camera",steps=609,dt_s=.005,board_used=False,
        stimulus="common_bundle/stimulus.npy",time="common_bundle/time.npy",activity_time="common_bundle/activity_time.npy",
        cell_types="common_bundle/cell_types.npy",activity_central="artifacts/full_gpu_609_r1/activity_central.npy",
        activity_all_nodes="artifacts/full_gpu_609_r1/activities_full.npy",metadata="common_bundle/camera_backend_identity.json",
        charts=["recorded_camera_T4_T5.png","recorded_camera_central65.png"],GUI_reader_acceptance="NOT_TESTED",
        display_semantics="playing this saved trace is offline replay; the trace itself came from actual original Full GPU inference"))
    dump(HERE/"DELIVERY_MANIFEST.json",dict(schema="camera-full-delivery-seal/v1",files=manifest(HERE)))
    print(json.dumps({k:result[k] for k in ["status","check_count","comparison_id","all_steps_nodes_bitwise","fpga_replacement"]}))
    print(json.dumps([r for r in statistics if r["cell_type"].startswith(("T4","T5"))]))


if __name__=="__main__":main()
