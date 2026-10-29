"""Read-only bankfix-Q22 identity and host-adapter preparation audit.

Never imports PYNQ, constructs a board driver, loads an overlay, or computes
neural activity. The existing adapter is exercised with driver=None only.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import sys
import zipfile
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET


EXPECTED = {
    "manifest": "54a40c9951388ccb4e6d4cc89da7c0f93f039cdf14b247dfb4278ba3d4def9c6",
    "bitstream": "e45bbe0d7795ee835fb7486444199460733196373ea4f363a8ff1c93431b7383",
    "hwh": "fb40c671c06f41923e4cd41cff055c0b549e2db69bbfcee05810960a95885d82",
    "xsa": "ef475039197de8d98a8af4681b92e92bf92bc507ada537335262e98e457e7248",
    "q22_comparison": "a2f36bb961934225ee16ce5fa75ddf4e6671913fcad3cb557bb47afc4171ac54",
    "q22_initial": "9621c1228cd42bd538be00ff06c6bd3793c82984ce0f8c92b1ef60d2b9f89f21",
}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def records(obj, label="root"):
    if isinstance(obj, dict):
        if "path" in obj and "sha256" in obj:
            yield label, obj
        for key, value in obj.items():
            yield from records(value, label + "." + key)
    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            yield from records(value, label + f"[{i}]")


def write(path, obj):
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, required=True)
    ap.add_argument("--q22-source-root", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args()
    repo = args.repo_root.resolve()
    release = repo / "flyvis-fpga/phase4_67_20261010/build/v1_bankfix_20261011_153525"
    old_release = repo / "flyvis-fpga/phase4_67_20261010/build/V1_20261010_210347"
    q22 = repo / "docs/flyvis_visual_hybrid/architect_phase4_20261010/artifacts/q22_common_initial_state_v2"
    manifest_path = release / "release_manifest.json"
    assert sha(manifest_path) == EXPECTED["manifest"], "new manifest identity differs"
    m = json.loads(manifest_path.read_text(encoding="utf-8"))
    old = json.loads((old_release / "release_manifest.json").read_text(encoding="utf-8"))
    ident_path = q22 / "comparison_identity.json"
    ident = json.loads(ident_path.read_text(encoding="utf-8"))
    canonical = json.dumps({k: v for k, v in ident.items() if k != "comparison_id"},
                           sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    assert hashlib.sha256(canonical).hexdigest() == ident["comparison_id"] == EXPECTED["q22_comparison"]
    assert sha(q22 / "initial_state_full_q22_hybrid.npy") == EXPECTED["q22_initial"]
    assert sha(q22 / "H_global_ids.npy") == ident["h_global_ids_sha256"]

    checked = []
    failures = []
    for label, row in records(m):
        p = Path(row["path"])
        if not p.is_absolute():
            # These two inherited source groups are relative to P3, as
            # explicitly constructed by finalize_v1_release.py. Packaged
            # implementation/vector/software records are release-relative.
            base = repo / "flyvis-fpga/phase3_20261010" if label.startswith(
                ("root.files.hls_sources_and_roms", "root.files.hls_component_xml")) else release
            p = base / p
        exists = p.is_file()
        actual = sha(p) if exists else None
        size_ok = exists and ("bytes" not in row or p.stat().st_size == row["bytes"])
        passed = size_ok and actual == row["sha256"]
        checked.append({"label": label, "path": str(p), "sha256": actual, "pass": passed})
        if not passed:
            failures.append(label)
    assert not failures, f"declared release/source files failed: {failures}"

    for key in ("bitstream", "hwh", "xsa"):
        assert m["files"][key]["sha256"] == EXPECTED[key]
    sources = {Path(r["path"]).name: r["sha256"] for r in m["files"]["hls_sources_and_roms"]}
    old_sources = {Path(r["path"]).name: r["sha256"] for r in old["files"]["hls_sources_and_roms"]}
    assert sources == old_sources, "HLS C or Q22 ROM differs from original release"
    assert sources["flyvis_t5c_source_raw.cpp"] == ident["source_hls_c_sha256"]
    assert sources["flyvis_t5c_constants_q22.hpp"] == ident["source_hls_rom_sha256"]
    assert m["control_register_map"] == old["control_register_map"]
    assert m["interfaces"]["FCLK0_Hz"] == old["interfaces"]["FCLK0_Hz"] == 100000000
    assert m["interfaces"]["PS_M_AXI_GP0"] == old["interfaces"]["PS_M_AXI_GP0"]
    assert m["first_operation_scope"] == {"row": 0, "requests": 1, "commit": False, "true_closed_loop": False}
    ip_rows = []
    for row in m["unchanged_hls_ooc_sources"]:
        for ip in row.get("ip_verilog_files", []):
            assert ip["sha256"] == row["sha256"], "IP Verilog differs from validated OOC source"
            ip_rows.append(ip)

    xsa = release / m["files"]["xsa"]["path"]
    embedded = {}
    with zipfile.ZipFile(xsa) as z:
        for key in ("bitstream", "hwh"):
            suffix = ".bit" if key == "bitstream" else ".hwh"
            entries = [x for x in z.namelist() if Path(x).suffix == suffix]
            assert len(entries) == 1, f"XSA {key} entry missing/ambiguous"
            digest = hashlib.sha256(z.read(entries[0])).hexdigest()
            assert digest == EXPECTED[key]
            embedded[key] = digest
    hwh_root = ET.parse(release / m["files"]["hwh"]["path"]).getroot()
    ps7_modules = [x for x in hwh_root.iter() if x.tag.rsplit("}", 1)[-1] == "MODULE"
                   and x.attrib.get("MODTYPE") == "processing_system7"]
    assert len(ps7_modules) == 1, "HWH PS7 module missing or ambiguous"
    ps7 = ps7_modules[0]
    params = {x.attrib.get("NAME"): x.attrib.get("VALUE") for x in ps7.iter()
              if x.tag.rsplit("}", 1)[-1] == "PARAMETER"}
    bank1 = {k: v for k, v in params.items() if k and "PRESET_BANK1_VOLTAGE" in k}
    assert bank1 and all("1.8" in v for v in bank1.values()), "HWH Bank1 not 1.8 V"
    assert params["C_S_AXI_HP0_DATA_WIDTH"] == params["PCW_S_AXI_HP0_DATA_WIDTH"] == "64"
    assert params["C_USE_S_AXI_HP0"] == params["PCW_USE_S_AXI_HP0"] == "1"

    sys.path.insert(0, str(args.q22_source_root.resolve()))
    from pynq_h_backend_adapter import PynqHBackendAdapter
    from q22_host_coordinator import TransactionError
    driver_source = release / "pynq/flyvis_v1_evidence_driver.py"
    adapter = PynqHBackendAdapter(None, identity=ident,
        h_global_ids_path=q22 / "H_global_ids.npy", soc_manifest_path=manifest_path,
        driver_source_path=driver_source, expected_bit_sha256=EXPECTED["bitstream"],
        expected_hwh_sha256=EXPECTED["hwh"])
    manifest_binding_check = {"status": "PASS_LOCAL_MANIFEST_BINDING_NO_BOARD"}
    try:
        adapter._validate_release_manifest()
    except KeyError as e:
        assert e.args == ("bitstream_sha256",), e.args
        manifest_binding_check = {
            "status": "FAIL_EXISTING_ADAPTER_FIRMWARE_KEY_MAPPING",
            "exception": "KeyError: bitstream_sha256",
            "cause": "expected_firmware stores bit_sha256, but _validate_release_manifest indexes bitstream_sha256 for files.bitstream",
        }
    rejections = []
    for name, call in (("activation_without_driver", adapter.activate_after_overlay_validation),
                       ("step_without_connection", lambda: adapter.step(None))):
        try:
            call()
        except TransactionError as e:
            assert e.code == "NOT_CONNECTED", (name, e.code)
            rejections.append({"check": name, "error_code": e.code, "message": str(e)})
        except KeyError as e:
            assert name == "activation_without_driver" and e.args == ("bitstream_sha256",)
            rejections.append({"check": name, "error_code": "ADAPTER_KEY_MAPPING_BUG",
                               "message": "KeyError: bitstream_sha256 before activation"})
        else:
            raise AssertionError("unconnected adapter unexpectedly passed " + name)
    assert not adapter.connected and adapter.evidence_level == "NOT_CONNECTED"
    from bankfix_q22_manifest_adapter import PreparedBankfixQ22Adapter
    prepared = PreparedBankfixQ22Adapter(None, identity=ident,
        h_global_ids_path=q22 / "H_global_ids.npy", soc_manifest_path=manifest_path,
        driver_source_path=driver_source, expected_bit_sha256=EXPECTED["bitstream"],
        expected_hwh_sha256=EXPECTED["hwh"], hls_source_root=repo / "flyvis-fpga/phase3_20261010")
    prepared._validate_release_manifest()
    prepared_checks = [{"check": "correct_release_and_frozen_Q22_profile", "result": "PASS_LOCAL_FILE_VALIDATION"}]
    for key in ("bit_sha256", "hwh_sha256", "rom_sha256", "numeric_profile_sha256"):
        original_value = prepared.expected_firmware[key]
        prepared.expected_firmware[key] = "0" * 64
        try:
            prepared._validate_release_manifest()
        except TransactionError as e:
            assert e.code == "PL_IDENTITY"
            prepared_checks.append({"check": "reject_mismatched_" + key, "error_code": e.code})
        else:
            raise AssertionError("identity mismatch unexpectedly passed: " + key)
        finally:
            prepared.expected_firmware[key] = original_value
    for name, call in (("activation_without_driver", prepared.activate_after_overlay_validation),
                       ("step_without_connection", lambda: prepared.step(None))):
        try:
            call()
        except TransactionError as e:
            assert e.code == "NOT_CONNECTED"
            prepared_checks.append({"check": name, "error_code": e.code})
        else:
            raise AssertionError("prepared adapter unexpectedly activated or ran")
    assert not prepared.connected and prepared.evidence_level == "NOT_CONNECTED"
    assert "pynq" not in sys.modules and "torch" not in sys.modules

    tree = ast.parse(driver_source.read_text(encoding="utf-8"))
    cls = next(x for x in tree.body if isinstance(x, ast.ClassDef) and x.name == "EvidenceStepDriver")
    identity_stores = [x for x in ast.walk(cls) if isinstance(x, ast.Attribute)
        and isinstance(x.ctx, ast.Store) and isinstance(x.value, ast.Name)
        and x.value.id == "self" and x.attr == "identity"]
    assert not identity_stores, "driver identity API changed; review this audit"
    step = next(x for x in cls.body if isinstance(x, ast.FunctionDef) and x.name == "step")
    return_keys = []
    for x in ast.walk(step):
        if isinstance(x, ast.Return) and isinstance(x.value, ast.Dict):
            return_keys.append([k.value for k in x.value.keys if isinstance(k, ast.Constant)])
    assert ["candidate_h_q22_i32", "report"] in return_keys

    args.out_dir.mkdir(parents=True, exist_ok=False)
    binding = {
        "schema": "flyvis-bankfix-q22-binding-preparation/v1",
        "status": "VERSIONED_MANIFEST_GATE_PREPARED_DRIVER_BRIDGE_PENDING_NOT_CONNECTED",
        "numeric_comparison_id": ident["comparison_id"],
        "source_phase3_vector_comparison_id": ident["source_phase3_comparison_id"],
        "release_path": str(release), "expected_firmware": adapter.expected_firmware,
        "hls_source_records_base": str(repo / "flyvis-fpga/phase3_20261010"),
        "initial_state_sha256": EXPECTED["q22_initial"],
        "first_operation_scope": m["first_operation_scope"],
        "manifest_binding_check": "PASS_VERSIONED_LOCAL_MANIFEST_GATE_NO_BOARD",
        "frozen_adapter_manifest_binding_check": manifest_binding_check,
        "prepared_adapter_source_sha256": sha(Path(__file__).parent / "bankfix_q22_manifest_adapter.py"),
        "evidence_driver_direct_api_compatible": False,
        "required_future_api_work": [
            "The local manifest gate is fixed in a separate prepared adapter. Bind this new source SHA in any future reviewed run/deployment identity; do not replace the frozen source manifest.",
            "Versioned evidence-driver bridge must expose verified firmware identity and validate the nested report fields before translating an H candidate.",
            "Preserve first-step single-attempt/noCOMMIT restrictions; a 1/32/800 live loop requires its own reviewed driver scope and explicit board operation authorization.",
            "New bridge and run identities must not overwrite the frozen Q22 software source manifest or Q24 software comparison.",
        ],
        "Q24_weight_Q30_dt_hardware": "NOT_IMPLEMENTED_BY_THIS_RELEASE",
        "Q22_32_step_scientific_gate": "STILL_FAILS_UNCHANGED_FROZEN_REFERENCE",
        "live_gpu_r_pl": "NOT_CONNECTED", "board_io_operations": 0,
        "gpu_inference_started": 0, "full_or_cpu_H_fallback": False,
    }
    result = {
        "schema": "flyvis-bankfix-q22-readonly-binding-audit/v1",
        "status": "PASS_RELEASE_IDENTITY_AND_VERSIONED_MANIFEST_GATE_NO_BOARD",
        "evidence_level": "FILE_XML_ZIP_AST_AND_CPU_ADAPTER_CHECKS_NO_BOARD",
        "recorded_at": datetime.now().astimezone().isoformat(),
        "manifest_sha256": sha(manifest_path), "declared_file_records_checked": len(checked),
        "actual_ip_verilog_records_checked": len(ip_rows), "checked_files": checked,
        "xsa_embedded_pair": embedded, "bank1_hwh_parameters": bank1,
        "interfaces": m["interfaces"], "actual_hwh_hp0_bits": 64,
        "q22_sources_and_register_abi_unchanged": True,
        "q22_numeric_comparison_identity_verified": True,
        "adapter_source_sha256": sha(args.q22_source_root / "pynq_h_backend_adapter.py"),
        "driver_direct_api_compatible": False, "driver_step_return_keys": return_keys,
        "existing_adapter_manifest_binding_check": manifest_binding_check,
        "prepared_adapter_checks": prepared_checks,
        "prepared_adapter_source_sha256": sha(Path(__file__).parent / "bankfix_q22_manifest_adapter.py"),
        "unconnected_rejections": rejections, "audit_script_sha256": sha(Path(__file__)),
        "board_io_operations": 0, "neural_updates": 0, "live_gpu_r_pl": "NOT_CONNECTED",
    }
    write(args.out_dir / "RELEASE_IDENTITY_AUDIT.json", result)
    write(args.out_dir / "GPU_R_PL_BINDING_PREPARATION.json", binding)
    (args.out_dir / "audit_source_snapshot.py").write_bytes(Path(__file__).read_bytes())
    (args.out_dir / "prepared_adapter_source_snapshot.py").write_bytes(
        (Path(__file__).parent / "bankfix_q22_manifest_adapter.py").read_bytes())
    write(args.out_dir / "artifact_manifest.json", {"schema": "flyvis-binding-preparation-manifest/v1",
        "files": [{"path": p.name, "bytes": p.stat().st_size, "sha256": sha(p)}
                  for p in sorted(args.out_dir.iterdir()) if p.is_file()]})
    print(json.dumps({k: result[k] for k in ("status", "declared_file_records_checked",
        "actual_ip_verilog_records_checked", "driver_direct_api_compatible", "live_gpu_r_pl")}, indent=2))


if __name__ == "__main__":
    main()
