"""Freeze local V1 BIT/HWH/XSA, timing reports, and the exact reference vectors."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P3 = ROOT.parent / "phase3_20261010"
HLS = P3 / "build" / "vitis_2026_1_q22_animation_enterprise_20261010_1842" / "hls" / "impl" / "ip"
COMPONENT = HLS / "component.xml"
FIXTURE = P3 / "testdata_animation_q22"
AUDIT = ROOT / "artifacts" / "LEADER_BOARD_REFERENCE_AUDIT.json"
PS_PARAMS = ROOT / "artifacts" / "LEADER_PS7_USER_PARAMS.json"
NS = {"s": "http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009"}


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def register_map() -> dict[str, object]:
    root = ET.parse(COMPONENT).getroot()
    block = root.find("s:memoryMaps/s:memoryMap/s:addressBlock", NS)
    if block is None:
        raise ValueError("HLS control memory map is missing")
    registers: dict[str, dict[str, object]] = {}
    for reg in block.findall("s:register", NS):
        name = reg.findtext("s:name", namespaces=NS)
        offset = reg.findtext("s:addressOffset", namespaces=NS)
        size = reg.findtext("s:size", namespaces=NS)
        if not name or offset is None or size is None:
            raise ValueError("Malformed HLS register map entry")
        registers[name] = {"offset": int(offset, 0), "size_bits": int(size, 0)}
    required = {"CTRL", "ap_return", "request_1", "request_2", "result_1", "result_2"}
    if not required.issubset(registers):
        raise ValueError(f"HLS pointer/control registers missing: {sorted(required - registers.keys())}")
    return {
        "source": "validated HLS component.xml",
        "base_address": "0x43C00000",
        "range_bytes": 65536,
        "control_registers": registers,
        "semantics": {
            "CTRL.AP_START": "bit 0; write 1 to launch one stateless request",
            "CTRL.AP_DONE": "bit 1; clear-on-read",
            "CTRL.AP_IDLE": "bit 2",
            "CTRL.AP_READY": "bit 3",
            "ap_return": "unsigned status; zero means HLS request completed without numeric/input faults",
            "request_1_request_2": "64-bit DDR pointer, low word then high word",
            "result_1_result_2": "64-bit DDR pointer, low word then high word",
        },
    }


def timing_extract(path: Path) -> dict[str, object]:
    if not path.is_file():
        return {"path": str(path), "present": False}
    raw = path.read_text(encoding="utf-8", errors="replace")
    lines = raw.splitlines()
    for index, line in enumerate(lines):
        if "WNS(ns)" not in line or "TNS(ns)" not in line or "WHS(ns)" not in line or "THS(ns)" not in line:
            continue
        for row in lines[index + 1:index + 7]:
            columns = re.findall(r"[-+]?\d+(?:\.\d+)?", row)
            if len(columns) < 8:
                continue
            try:
                values = [float(columns[i]) for i in range(8)]
            except ValueError:
                continue
            return {
                "path": str(path), "present": True,
                "wns_ns": values[0], "tns_ns": values[1],
                "setup_failing_endpoints": int(values[2]),
                "setup_total_endpoints": int(values[3]),
                "whs_ns": values[4], "ths_ns": values[5],
                "hold_failing_endpoints": int(values[6]),
                "hold_total_endpoints": int(values[7]),
                "all_setup_and_hold_constraints_met": values[0] >= 0 and values[1] == 0 and values[4] >= 0 and values[5] == 0,
            }
    return {"path": str(path), "present": True, "parsed": False}


def copy_or_verify(source: Path, target: Path) -> dict[str, object]:
    if not source.is_file():
        raise FileNotFoundError(source)
    if target.exists():
        if sha(source) != sha(target):
            raise ValueError(f"Refusing to overwrite conflicting release file: {target}")
    else:
        shutil.copyfile(source, target)
    return {"path": target.name, "bytes": target.stat().st_size, "sha256": sha(target)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--release-dir", required=True, type=Path)
    args = parser.parse_args()
    release = args.release_dir.resolve()
    if not release.name.startswith("V1_"):
        raise ValueError(f"Unexpected V1 release directory name: {release}")
    build_root = ROOT.parent / "p4b" / f"r{release.name.removeprefix('V1_')}"
    if not (build_root / "flyvis67v1.xpr").is_file():
        raise FileNotFoundError(f"Matching isolated Vivado project is missing: {build_root}")
    required = {
        "bitstream": release / "flyvis_t5c_source_raw_v1.bit",
        "hwh": release / "flyvis_t5c_source_raw_v1.hwh",
        "xsa": release / "flyvis_t5c_source_raw_v1.xsa",
        "implementation_timing": release / "implementation_timing_summary.rpt",
        "implementation_utilization": release / "implementation_utilization.rpt",
        "implementation_drc": release / "implementation_drc.rpt",
        "implementation_io": release / "implementation_io.rpt",
    }
    missing = [str(path) for path in required.values() if not path.is_file()]
    if missing:
        raise FileNotFoundError("V1 release files missing: " + ", ".join(missing))

    hwh_root = ET.parse(required["hwh"]).getroot()
    modules = [n for n in hwh_root.iter() if n.tag.rsplit("}", 1)[-1] == "MODULE"]
    flyvis = [n for n in modules if n.attrib.get("INSTANCE") == "flyvis_h"]
    ps7 = [n for n in modules if n.attrib.get("MODTYPE") == "processing_system7"]
    if len(flyvis) != 1 or len(ps7) != 1:
        raise ValueError(f"Unexpected handoff hierarchy: flyvis={len(flyvis)}, PS7={len(ps7)}")
    if flyvis[0].attrib.get("VLNV") != "xilinx.com:hls:flyvis_t5c_source_raw:1.0":
        raise ValueError("HWH does not contain the validated FlyVis HLS IP")
    control_ranges = [n.attrib for n in hwh_root.iter()
                      if n.tag.rsplit("}", 1)[-1] == "MEMRANGE"
                      and n.attrib.get("INSTANCE") == "flyvis_h"
                      and n.attrib.get("ADDRESSBLOCK") == "Reg"]
    if len(control_ranges) != 1 or control_ranges[0].get("BASEVALUE", "").lower() != "0x43c00000" or control_ranges[0].get("HIGHVALUE", "").lower() != "0x43c0ffff":
        raise ValueError(f"HWH control range does not match 0x43C00000/64 KiB: {control_ranges}")
    clock_hz = sorted({int(n.attrib["CLKFREQUENCY"]) for n in hwh_root.iter()
                       if n.tag.rsplit("}", 1)[-1] == "PORT"
                       and n.attrib.get("SIGNAME", "").endswith("FCLK_CLK0")
                       and n.attrib.get("CLKFREQUENCY", "").isdigit()})
    if 100_000_000 not in clock_hz:
        raise ValueError(f"HWH does not describe a 100 MHz FCLK0: {clock_hz}")

    files: dict[str, object] = {}
    for key, path in required.items():
        files[key] = {"path": path.name, "bytes": path.stat().st_size, "sha256": sha(path)}
    files["hls_component_xml"] = {"path": str(COMPONENT.relative_to(P3)), "sha256": sha(COMPONENT)}
    source_paths = [P3 / "hls" / "flyvis_t5c_source_raw.cpp",
                    P3 / "hls" / "flyvis_t5c_constants_q22.hpp",
                    P3 / "rom" / "edges_q22.mem", P3 / "rom" / "neurons_q22.mem",
                    P3 / "rom" / "manifest.json"]
    files["hls_sources_and_roms"] = [{"path": str(p.relative_to(P3)), "bytes": p.stat().st_size,
                                       "sha256": sha(p)} for p in source_paths]

    vectors_dir = release / "vectors"
    vectors_dir.mkdir(exist_ok=True)
    for name in ("requests_i32le.bin", "expected_i32le.bin", "fixture_manifest.json", "request_map.csv"):
        copy_or_verify(FIXTURE / name, vectors_dir / name)
    for name in ("LEADER_BOARD_REFERENCE_AUDIT.json", "LEADER_PS7_USER_PARAMS.json"):
        copy_or_verify(ROOT / "artifacts" / name, release / name)

    log_root = ROOT / "logs"
    build_marker = str(build_root).replace("\\", "/").lower()
    full_soc_logs = [p for p in log_root.glob("v1_soc_*.log")
                     if f"build={build_marker}" in p.read_text(encoding="utf-8", errors="replace").lower()]
    package_marker = str(release).replace("\\", "/").lower()
    package_logs = [p for p in log_root.glob("package_v1_*.log")
                    if "FLYVIS_V1_SOC_IMPL_BIT_HWH_READY" in p.read_text(encoding="utf-8", errors="replace")
                    and package_marker in p.read_text(encoding="utf-8", errors="replace").lower()]
    if len(full_soc_logs) != 1 or len(package_logs) != 1:
        raise ValueError(f"Expected unique full-SoC/package logs; got {len(full_soc_logs)} and {len(package_logs)}")
    log_sources = {
        "vivado_full_soc.log": full_soc_logs[0],
        "synth_1_runme.log": build_root / "flyvis67v1.runs" / "synth_1" / "runme.log",
        "impl_1_runme.log": build_root / "flyvis67v1.runs" / "impl_1" / "runme.log",
        "vivado_bit_hwh_xsa_package.log": package_logs[0],
    }
    copied_logs: dict[str, object] = {}
    logs_dir = release / "logs"
    logs_dir.mkdir(exist_ok=True)
    for name, source in log_sources.items():
        copied_logs[name] = copy_or_verify(source, logs_dir / name)

    fixture = json.loads((vectors_dir / "fixture_manifest.json").read_text(encoding="utf-8"))
    if fixture.get("RTL_execution") or fixture.get("board_execution"):
        raise ValueError("Fixture source identity unexpectedly claims RTL or board execution")
    manifest = {
        "status": "FULL_SOC_BIT_HWH_READY_BOARD_NOT_AUTHORIZED",
        "evidence_level": "VIVADO_FULL_SOC_IMPLEMENTATION_AND_BITSTREAM; NO_LIVE_BOARD_EXECUTION",
        "target": "xc7z020clg400-2",
        "tool": "Vivado 2026.1.1",
        "design": "FlyVis T5c 67 nodes SOURCE_RAW Q22, HLS V1",
        "interfaces": {"PS_M_AXI_GP0": "AXI-Lite control", "PS_S_AXI_HP0": "HLS DDR master path, 64-bit HP0", "FCLK0_Hz": 100_000_000},
        "hwh_instances": {"processing_system7": ps7[0].attrib, "flyvis_h": flyvis[0].attrib},
        "control_register_map": register_map(),
        "files": files,
        "build_project": str(build_root),
        "build_logs": {name: {**item, "path": f"logs/{name}"} for name, item in copied_logs.items()},
        "copied_vectors": {name: {"path": f"vectors/{name}", "bytes": (vectors_dir / name).stat().st_size,
                                  "sha256": sha(vectors_dir / name)}
                           for name in ("requests_i32le.bin", "expected_i32le.bin", "fixture_manifest.json", "request_map.csv")},
        "fixture_identity": {"comparison_id": fixture["comparison_id"], "condition_id": fixture["condition_id"],
                             "request_sha256": fixture["request_sha256"], "expected_sha256": fixture["expected_sha256"],
                             "request_shape": fixture["request_shape"], "expected_shape": fixture["expected_shape"],
                             "scientific_acceptance": fixture["scientific_acceptance"],
                             "replay_semantics": "Each input row includes recorded old_H and x_H; this is not a live feedback loop."},
        "timing": timing_extract(required["implementation_timing"]),
        "board_programming": "NOT_PERFORMED; requires specific user authorization after review of these exact hashes and procedure",
    }
    manifest_path = release / "release_manifest.json"
    if manifest_path.exists():
        existing = json.loads(manifest_path.read_text(encoding="utf-8"))
        for name, entry in existing.get("files", {}).items():
            if manifest.get("files", {}).get(name) != entry:
                raise FileExistsError(f"Refusing to change existing file identity for {name}")
        mutable_evidence = {"timing", "build_logs", "build_project", "files"}
        existing_identity = {k: v for k, v in existing.items() if k not in mutable_evidence}
        new_identity = {k: v for k, v in manifest.items() if k not in mutable_evidence}
        if existing_identity != new_identity:
            raise FileExistsError(f"Refusing to replace a manifest with different artifact identities: {manifest_path}")
        if existing != manifest:
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    else:
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"manifest": str(manifest_path), "status": manifest["status"],
                      "bit_sha256": files["bitstream"]["sha256"], "hwh_sha256": files["hwh"]["sha256"],
                      "timing": manifest["timing"], "board_programming": "NOT_PERFORMED"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
