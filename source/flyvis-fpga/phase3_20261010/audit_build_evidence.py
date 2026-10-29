"""Read actual vendor reports and seal source/report identities; no hardware I/O."""
import argparse
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def identities(paths):
    return {str(p.resolve()): sha(p) for p in paths if p.is_file()}


def utilization(path):
    text = path.read_text(errors="replace")
    result = {}
    for key, label in {
        "LUT": "Slice LUTs", "FF": "Slice Registers",
        "BRAM36_equivalent": "Block RAM Tile", "DSP": "DSPs",
    }.items():
        match = re.search(r"^\|\s*" + re.escape(label) + r"\s*\*?\s*\|\s*([\d,.]+)\s*\|", text, re.M)
        if not match:
            raise ValueError(f"Missing {label} in {path}")
        number = float(match.group(1).replace(",", ""))
        result[key] = int(number) if number.is_integer() else number
    return result


def ooc_report(directory, prefix="rtl", design="flyvis_source_raw_axil"):
    timing = directory / f"{prefix}_ooc_route_timing.rpt"
    text = timing.read_text(errors="replace")
    # Vivado's summary row has WNS/TNS/failing/total, WHS/THS/failing/total,
    # and optionally pulse-width fields. Header must precede the numeric row.
    summary = text.split("Design Timing Summary", 1)[1]
    row = re.search(r"^\s*(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(\d+)\s+(\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(\d+)\s+(\d+)", summary, re.M)
    if not row:
        raise ValueError("Timing summary row missing")
    wns, tns, setup_failing, setup_total, whs, ths, hold_failing, hold_total = row.groups()
    coverage = {name: int(re.search(r"checking " + name + r" \((\d+)\)", text).group(1))
                for name in ["no_clock", "unconstrained_internal_endpoints", "no_input_delay", "no_output_delay"]}
    meets = (float(wns) >= 0 and float(tns) == 0 and float(whs) >= 0 and float(ths) == 0
             and coverage["no_clock"] == 0 and coverage["unconstrained_internal_endpoints"] == 0)
    return {
        "status": "PASS_OOC_INTERNAL_TIMING" if meets else "FAIL_OOC_INTERNAL_TIMING",
        "scope": f"{design} only; OOC route; external I/O timing is not board timing",
        "tool": "Vivado 2026.1.1 SW build 6605303", "part": "xc7z020clg400-2",
        "clock_target_ns": 10,
        "synthesis_resources": utilization(directory / f"{prefix}_ooc_synthesis_utilization.rpt"),
        "route_resources": utilization(directory / f"{prefix}_ooc_route_utilization.rpt"),
        "timing_ns": {"WNS": float(wns), "TNS": float(tns), "WHS": float(whs), "THS": float(ths)},
        "setup_endpoints": {"failing": int(setup_failing), "total": int(setup_total)},
        "hold_endpoints": {"failing": int(hold_failing), "total": int(hold_total)},
        "constraint_coverage": coverage,
        "report_sha256": identities(sorted(directory.glob("*.rpt")) + sorted(directory.glob("*.dcp")) + [directory / "target_probe.txt"]),
        "source_sha256": identities(sorted((directory / "rtl").glob("*.sv")) + sorted((directory / "rom").glob("*.mem")) + sorted((directory / "hdl").glob("*")) + list(directory.glob("*.tcl"))),
        "full_soc": False, "bitstream": False, "board_execution": False,
    }


def hls_report(directory):
    report_path = directory / "hls/syn/report/flyvis_t5c_source_raw_csynth.xml"
    profile = ET.parse(report_path).getroot()
    if profile.findtext("UserAssignments/Part") != "xc7z020-clg400-2":
        raise ValueError("Unexpected HLS target")
    resources = {node.tag: int(node.text) for node in profile.find("AreaEstimates/Resources")}
    latency = profile.find("PerformanceEstimates/SummaryOfOverallLatency")
    cosim_path = directory / "hls/sim/report/flyvis_t5c_source_raw_cosim.rpt"
    cosim = {"status": "NOT_RUN_OR_NOT_FINISHED", "board_execution": False}
    if cosim_path.exists():
        content = cosim_path.read_text(errors="replace")
        passed = bool(re.search(r"\|\s*Verilog\s*\|\s*Pass\s*\|", content, re.I))
        xsim_log = directory / "hls/sim/verilog/xsim.log"
        if passed and not re.search(r"RTL Simulation\s*:\s*803\s*/\s*803", xsim_log.read_text(errors="replace")):
            raise ValueError("Missing completion evidence for all 803 RTL requests")
        cosim.update(status="PASS_C_RTL_COSIM" if passed else "FAIL_OR_INCOMPLETE_C_RTL_COSIM",
                     report=str(cosim_path.resolve()), report_sha256=sha(cosim_path))
        row = re.search(r"\|\s*Verilog\s*\|\s*Pass\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|", content, re.I)
        if row:
            values = list(map(int, row.groups()))
            cosim["latency_cycles"] = dict(zip(["min", "avg", "max"], values[:3]))
            cosim["interval_cycles"] = dict(zip(["min", "avg", "max"], values[3:6]))
            cosim["total_execution_cycles"] = values[6]
        cosim["xsim_log_sha256"] = sha(xsim_log)
        cosim["requests"] = {"animation": 800, "boundary_perturb": 1, "malformed_or_overflow": 2}
        cosim["scope"] = "803 stateless requests with explicit reference old_H; generated Verilog and AXI memory model; not a GPU-R/PL closed loop"
    return {
        "status": "PASS_HLS_SYNTHESIS", "tool": "Vitis HLS 2026.1.1 launcher build 6595028",
        "part": "xc7z020-clg400-2", "design": "flyvis_t5c_source_raw",
        "clock_target_ns": float(profile.findtext("UserAssignments/TargetClockPeriod")),
        "estimated_period_ns": float(profile.findtext("PerformanceEstimates/SummaryOfTimingAnalysis/EstimatedClockPeriod")),
        "resources_estimate_only": resources,
        "latency_cycles_estimate": {"min": int(latency.findtext("Best-caseLatency")), "max": int(latency.findtext("Worst-caseLatency"))},
        "cosim": cosim,
        "generated_verilog_sha256": identities(sorted((directory / "hls/syn/verilog").glob("*"))),
        "report_sha256": identities([report_path, report_path.with_suffix(".rpt")]),
        "full_soc": False, "board_execution": False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hls-work", type=Path, required=True)
    parser.add_argument("--ooc-dir", type=Path)
    parser.add_argument("--hls-ooc-dir", type=Path)
    args = parser.parse_args()
    fixture = json.loads((ROOT / "testdata_animation_q22/fixture_manifest.json").read_text())
    for name, key in [("requests_i32le.bin", "request_sha256"), ("expected_i32le.bin", "expected_sha256")]:
        if sha(ROOT / "testdata_animation_q22" / name) != fixture[key]:
            raise ValueError(f"Fixture identity changed: {name}")
    result = {
        "evidence_level": "VENDOR_HLS_REPORTS_AND_OPTIONAL_RTL_OOC_REPORTS",
        "comparison_id": fixture["comparison_id"], "condition_id": fixture["condition_id"],
        "hls": hls_report(args.hls_work.resolve()),
        "rtl_ooc": ooc_report(args.ooc_dir.resolve()) if args.ooc_dir else {"status": "NOT_RUN"},
        "hls_rtl_ooc": {"status": "NOT_RUN"},
        "source_sha256": identities([ROOT / p for p in ["hls/flyvis_t5c_source_raw.cpp", "hls/flyvis_t5c_constants_q22.hpp", "hls/testbench.cpp", "hls/testbench_animation.cpp", "hls/hls_config.cfg"]]),
        "fixture_sha256": identities([ROOT / "testdata_animation_q22/fixture_manifest.json"]),
        "scientific_numeric_acceptance": "PENDING_ARCHITECTURE_REVIEW",
        "live_gpu_r_pl_closed_loop": False, "board_io_operations": 0,
    }
    if args.hls_ooc_dir:
        original = args.hls_work / "hls/syn/verilog"
        copied = args.hls_ooc_dir / "hdl"
        copied_files = sorted(p for p in copied.glob("*") if p.suffix in {".v", ".dat"})
        if not copied_files:
            raise ValueError("Missing copied HLS generated RTL")
        for path in copied_files:
            if sha(path) != sha(original / path.name):
                raise ValueError(f"Copied generated HLS RTL changed: {path.name}")
        result["hls_rtl_ooc"] = ooc_report(args.hls_ooc_dir.resolve(), "hls", "flyvis_t5c_source_raw")
        result["hls_rtl_ooc"]["generated_files_matched_to_cosim_build"] = len(copied_files)
    output = ROOT / "artifacts/BUILD_EVIDENCE_REPORT.json"
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"report": str(output), "hls": result["hls"]["status"], "cosim": result["hls"]["cosim"]["status"], "rtl_ooc": result["rtl_ooc"]["status"], "hls_rtl_ooc": result["hls_rtl_ooc"]["status"]}))


if __name__ == "__main__":
    main()
