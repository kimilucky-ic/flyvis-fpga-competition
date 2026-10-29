"""Independent saved-output checks, binary rejection tests, budget and portable replay assembly."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil
import struct
import numpy as np
from codec import read_template

ROOT = Path(__file__).resolve().parent


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024), b""): h.update(chunk)
    return h.hexdigest()


def write(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("run", type=Path)
    args = parser.parse_args(); run = args.run.resolve()
    assert ROOT in run.parents
    accepted = json.loads((run / "acceptance.json").read_text())
    assert accepted["status"] == "PASS_CPU_TEMPLATE_STRUCTURE_AND_RECURRENCE"
    manifest = json.loads((run / "manifest.json").read_text())
    for name, entry in manifest.items():
        assert sha(run/name) == entry["sha256"] and (run/name).stat().st_size == entry["bytes"], name
    a = np.load(run/"reference_activity.npy", mmap_mode="r")
    b = np.load(run/"template_activity.npy", mmap_mode="r")
    assert a.shape == b.shape == (accepted["steps"], 45669)
    hashes = []; compared = 0
    for x, y in zip(a, b):
        assert np.array_equal(x.view(np.uint32), y.view(np.uint32)) and np.isfinite(x).all()
        hashes.append(hashlib.sha256(x.tobytes()).hexdigest()); compared += len(x)
    audit = run / "independent_audit"
    audit.mkdir(exist_ok=False)
    blob = (run / "flyvis_template.bin").read_bytes()
    cases = {}
    cases["truncated"] = blob[:-1]
    bad = bytearray(blob); bad[150] ^= 1; cases["payload_corrupt"] = bytes(bad)
    bad = bytearray(blob); bad[-1] ^= 1; cases["checksum_corrupt"] = bytes(bad)
    def signed_patch(offset, value):
        candidate = bytearray(blob[:-32]); candidate[offset:offset+len(value)] = value
        return bytes(candidate) + hashlib.sha256(candidate).digest()
    cases["version_changed"] = signed_patch(8, struct.pack("<H", 2))
    cases["node_count_changed"] = signed_patch(16, struct.pack("<I", 45668))
    cases["dt_changed"] = signed_patch(40, struct.pack("<f", .01))
    cases["node_layout_out_of_range"] = signed_patch(128+6, bytes([255]))
    cases["rule_order_descriptor_changed"] = signed_patch(128+65*16+8, struct.pack("<I", 1))
    rejection = []
    for name, candidate in cases.items():
        p = audit / (name + ".bin"); p.write_bytes(candidate)
        try:
            read_template(p)
        except ValueError as error:
            rejection.append(dict(case=name, rejected=True, reason=str(error)))
        else:
            raise AssertionError(f"Malformed template accepted: {name}")
    write(audit / "binary_rejection_checks.json", rejection)
    n, e, g = 45669, 1513231, 1667894
    lanes = []
    for l in [1,2,4,8]:
        ideal = math.ceil(e/l) + 2*n; scan = math.ceil(g/l)+2*n
        lanes.append(dict(lanes=l, valid_edge_cycles=math.ceil(e/l), ideal_step_cycles=ideal,
                          ideal_step_ms=ideal/100000, ideal_steps_per_second=1e8/ideal,
                          source_candidate_step_cycles=scan, source_candidate_step_ms=scan/100000,
                          onchip_synapse_peak_GB_s=1.2*l, reference_arithmetic_only_LUT=311*l,
                          reference_arithmetic_only_DSP=4*l,
                          arithmetic_plus_separate_1node_per_cycle_update_LUT=311*l+1018,
                          arithmetic_plus_separate_1node_per_cycle_update_DSP=4*l+12,
                          two_vectors_L_banks_BRAM36_capacity_estimate=2*l*math.ceil(n/(1024*l)),
                          actual_total_LUT=None, actual_total_DSP=None, actual_total_BRAM36=None,
                          measured_cycles=None, stall_cycles=None))
    budget = dict(status="ANALYTICAL_ESTIMATE_NOT_SYNTHESIS", frequency_MHz=100, dt_s=.005,
                  binary_bytes=len(blob), vector_bytes_each=4*n, vector_bytes_two=8*n,
                  nominal_BRAM36_blocks=140, BRAM36_blocks_per_unbanked_FP32_vector=math.ceil(n/1024),
                  packed_template_BRAM36_capacity_estimate=math.ceil(len(blob)/4096),
                  synaptic_traffic_bytes_per_step=12*e, full_clear_update_traffic_bytes_per_step=12*e+16*n,
                  total_internal_GB_s_at_200Hz=(12*e+16*n)*200/1e9,
                  full_state_output_MB_s_at_200Hz=4*n*200/1e6,
                  assumptions=["Each lane accepts one valid edge per cycle; clear and node update each process one node per cycle",
                               "Aggregate E/L rounds only once: per-template lane padding and pipeline drain excluded",
                               "Source-candidate model enumerates valid source nodes, not the CPU interpreter's rectangular grid loops",
                               "Weights held per template; no per-edge DDR transaction; scratch in banked BRAM",
                               "No bank conflicts, recurrence hazards, metadata stalls, I/O overhead or routing cost included",
                               "Capacity banking estimate is not a port/conflict feasibility result; no full-vector read replication assumed",
                               "All LUT/DSP arithmetic examples are 2025.1 Floating-point v7.1 OOC xc7k70t fbv676 -1 Full DSP, not this Zynq design"],
                  sources=["https://download.amd.com/docnav/documents/ip_attachments/floating-point.html",
                           "https://www.amd.com/content/dam/xilinx/support/documents/data_sheets/ds190-Zynq-7000-Overview.pdf"],
                  lanes=lanes, real_time_200Hz_verified=False, energy_measured=None)
    write(audit / "hardware_budget.json", budget)
    package = audit / "compact_replay"
    package.mkdir()
    for name in ["codec.py","engine.py","replay.py"]: shutil.copy2(ROOT/name, package/name)
    for name in ["flyvis_template.bin","stimulus.npy"]: shutil.copy2(run/name, package/name)
    write(package / "expected_state_hashes.json", hashes)
    write(package / "payload_manifest.json", {p.name:sha(p) for p in package.iterdir() if p.is_file()})
    write(audit / "saved_evidence_audit.json", dict(status="PASS_SAVED_EVIDENCE_AND_BINARY_REJECTIONS",
              checked_manifest_files=len(manifest), checked_state_values=compared, state_bit_mismatches=0,
              malformed_cases_rejected=len(rejection), package=str(package),
              portable_replay_status="PENDING separate fresh process"))
    print(json.dumps(dict(status="PASS_SAVED_EVIDENCE_AND_BINARY_REJECTIONS", compared=compared,
                          malformed_cases_rejected=len(rejection), package=str(package))), flush=True)


if __name__ == "__main__": main()
