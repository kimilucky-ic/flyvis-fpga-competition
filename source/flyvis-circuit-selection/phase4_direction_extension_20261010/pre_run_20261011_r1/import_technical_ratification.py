"""Import the architect's exact authority bytes; does not run an experiment."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib, json

HERE = Path(__file__).resolve().parent
TARGET = Path(r"D:\FlyVisCircuitSelection\phase4_direction_extension_20261010\pre_run_20261011_r1")
source = Path(r"C:\Users\hzy72\Documents\ChatGPT\fpga\docs\flyvis_visual_hybrid\architect_phase4_20261011\B_FUNCTIONAL_24_TECHNICAL_RATIFICATION_20261011.json")

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    source_bytes = source.read_bytes()
    technical = json.loads(source_bytes)
    frozen = json.loads((TARGET / "FROZEN_CAMPAIGN_IDENTITY.json").read_text(encoding="utf-8"))
    assert technical["decision"] == "APPROVE_UNCHANGED_v1"
    assert technical["campaign_id"] == frozen["campaign_id"]
    assert technical["proposal_sha256"] == frozen["proposal_sha256"]
    assert technical["comparison_ids"] == frozen["comparison_ids"]
    assert technical["identity_file_sha256"] == sha(TARGET / "FROZEN_CAMPAIGN_IDENTITY.json") == sha(HERE / "FROZEN_CAMPAIGN_IDENTITY.json")
    assert Path(technical["execution_root"]).resolve() == TARGET.resolve()
    assert technical["run_authorized"] is False and technical["human_run_authorized"] is False
    assert technical["GPU_execution"] is False and technical["neural_updates"] == 0
    for key in ["authoritative_record", "audit_record"]:
        assert sha(Path(technical[key])) == technical[key + "_sha256"]
    destinations = [HERE / "TECHNICAL_RATIFICATION.json", TARGET / "TECHNICAL_RATIFICATION.json"]
    if any(p.exists() for p in destinations):
        raise SystemExit("Existing authority records preserved")
    for p in destinations:
        with p.open("xb") as f:
            f.write(source_bytes)
        assert sha(p) == sha(source)
    receipt = dict(status="PASS_EXACT_ARCHITECT_TECHNICAL_RECORD_IMPORTED_NOT_GPU_AUTHORIZATION",
                   imported_utc=datetime.now(timezone.utc).isoformat(),
                   source=str(source), source_sha256=sha(source),
                   destinations=[str(p) for p in destinations],
                   campaign_id=frozen["campaign_id"], proposal_sha256=frozen["proposal_sha256"],
                   authoritative_record=technical["authoritative_record"],
                   authoritative_record_sha256=technical["authoritative_record_sha256"],
                   audit_record=technical["audit_record"], audit_record_sha256=technical["audit_record_sha256"],
                   independent_audit_checks=technical["audit_checks"], technical_decision=technical["decision"],
                   run_authorized=False, human_run_authorized=False, GPU_conflict_free="PENDING_A_CONFIRMATION",
                   neural_updates=0, CUDA_tensor_operations=0, FPGA_execution=False)
    for parent in [HERE, TARGET]:
        with (parent / "TECHNICAL_RATIFICATION_IMPORT_20261011.json").open("x", encoding="utf-8", newline="\n") as f:
            json.dump(receipt, f, ensure_ascii=False, indent=2)
            f.write("\n")
    print(json.dumps(dict(status=receipt["status"], technical=technical["decision"],
                          source_sha256=receipt["source_sha256"], audit_checks=technical["audit_checks"], neural_updates=0)))

if __name__ == "__main__":
    main()
