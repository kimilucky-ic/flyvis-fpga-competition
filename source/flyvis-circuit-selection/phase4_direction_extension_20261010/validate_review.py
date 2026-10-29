"""Check the review packet without running neural inference; optionally seal it."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import numpy as np

HERE = Path(__file__).resolve().parent


def sha(p):
    h = hashlib.sha256()
    with Path(p).open("rb") as f:
        for b in iter(lambda:f.read(4*1024*1024), b""):
            h.update(b)
    return h.hexdigest()


def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def dump(p, d):
    with Path(p).open("x",encoding="utf-8",newline="\n") as f:
        json.dump(d,f,ensure_ascii=False,indent=2)
        f.write("\n")


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--seal",action="store_true")
    args=parser.parse_args()
    a=load(HERE/"SOURCE_AUDIT.json")
    r=load(HERE/"PRE_REGISTRATION_PROPOSED_v1.json")
    b=load(HERE/"RESOURCE_BUDGET.json")
    checked=[]
    def check(label, condition):
        assert condition,label
        checked.append(label)
    def filecheck(e):
        p=Path(e["path"])
        check(str(p)+" SHA",sha(p)==e["sha256"])
        check(str(p)+" bytes",p.stat().st_size==e["bytes"])
    for e in a["audited_sources"]:
        filecheck(e)
    for key in ["raw","prepared","time","conditions"]:
        filecheck(a["fixture"][key])
    for key in ["source","snapshot"]:
        filecheck(a["official_metrics"][key])
    for c in a["candidates"].values():
        for key in ["HR_original_edge_identity","H_global_ID_identity","candidate_manifest","static_boundary","validated_partition"]:
            filecheck(c[key])
        check("all edge coverage",sum(c["partition_counts"].values())==1513231)
    for e in a["readouts"].values():
        filecheck(e["prepared"])
    check("audit status",a["status"]=="PASS_PREPARATION_DATA_CHECKS_ONLY")
    check("no new neural or GPU run",a["new_neural_updates"]==0 and a["gpu_execution"] is False)
    check("no FPGA run",not a["FPGA_execution"] and not r["FPGA_execution"])
    check("approval still required",r["approval"]["run_authorized"] is False and b["execution_authorization"] is False)
    check("registration binds budget",r["resource_budget_sha256"]==sha(HERE/"RESOURCE_BUDGET.json"))
    check("registration binds source audit",r["source_audit_sha256"]==sha(HERE/"SOURCE_AUDIT.json"))
    check("67 and298 only",r["candidate_ids"]==["B_T5c","C_T4T5_all_centers"])
    check("complete direction/polarity set",[(c["angle"],c["intensity"]) for c in r["conditions"]]==[(ang,i) for ang in range(0,360,30) for i in [0,1]])
    check("operator unchanged",r["operator"]["name"]=="BLOCK_HR_RELEASE" and r["operator"]["start_step"]==200 and not r["operator"]["neural_output_zeroing"])
    check("primary readout fixed1057",r["readouts"]["primary_visual_readout"]["n"]==1057)
    check("local readouts634/1057",[r["readouts"][c+"_direct_common_visual_R"]["n"] for c in r["candidate_ids"]]==[634,1057])
    stim=np.load(HERE/"prepared_inputs/stimulus_float32.npy",mmap_mode="r")
    check("all24float32",stim.shape==(24,485,1,721) and stim.dtype==np.float32)
    check("all24finite",bool(np.isfinite(stim).all()))
    check("Full is not center replay",r["Full_policy"]["required_shape"]==[24,485,45669] and not r["Full_policy"]["historical_center_only_Full_eligible"])
    check("resource arithmetic states",b["storage"]["all_mode_payload_bytes"]==24*485*45669*4*10)
    check("resource arithmetic H/R",b["replacement_atomic_commits"]==2*24*2*2*485)
    check("resource arithmetic Full",b["Full_state_updates"]==24*2*485)
    check("alltimewindowsunchanged",r["windows_zero_based_inclusive"]==dict(prebaseline=[160,199],intervention=[200,484],primary_response=[200,484],motion=[200,285],post_motion=[286,484]))
    if args.seal:
        result=dict(status="PASS_REVIEW_PACKET_DATA_AND_CONFIG_CHECKS_ONLY",n_assertions=len(checked),
            assertions=checked,created_utc=datetime.now(timezone.utc).isoformat(),
            new_neural_updates=0,GPU_execution=False,FPGA_execution=False,
            execution_authorization=False,scope="fixture/identity/structure/config/budget; not neural numerical acceptance")
        dump(HERE/"PREPARATION_CHECKS.json",result)
        files=[]
        # Draft timing amendment is retained but not part of the submitted v1.
        for p in sorted(HERE.rglob("*")):
            if not p.is_file() or p.name=="REVIEW_MANIFEST_v1.json":
                continue
            if any(x in p.parts for x in ["drafts_before_submission","__pycache__","submission_records","review_responses"]):
                continue
            files.append(dict(path=p.relative_to(HERE).as_posix(),bytes=p.stat().st_size,sha256=sha(p)))
        canonical=json.dumps(files,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")
        manifest=dict(schema="flyvis-phase4-review-manifest/v1",status="SEALED_PROPOSAL_NOT_EXECUTION_APPROVAL",files=files,
            file_count=len(files),total_bytes=sum(e["bytes"] for e in files),
            bundle_digest_sha256=hashlib.sha256(canonical).hexdigest(),
            excluded="earlier unsubmitted timing draft, future submission receipts/review responses and Python caches",
            created_utc=datetime.now(timezone.utc).isoformat())
        dump(HERE/"REVIEW_MANIFEST_v1.json",manifest)
    mf=HERE/"REVIEW_MANIFEST_v1.json"
    if mf.exists():
        m=load(mf)
        for e in m["files"]:
            p=HERE/e["path"]
            assert p.stat().st_size==e["bytes"] and sha(p)==e["sha256"],e["path"]
        print(json.dumps(dict(status="PASS_SEALED_REVIEW_MANIFEST",files=m["file_count"],bytes=m["total_bytes"],manifest_sha256=sha(mf),new_neural_updates=0)))
    else:
        print(json.dumps(dict(status="PASS_UNSEALED_REVIEW_CHECKS",n_assertions=len(checked),new_neural_updates=0)))


if __name__=="__main__":
    main()
