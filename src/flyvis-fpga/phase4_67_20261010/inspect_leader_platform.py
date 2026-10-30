"""Read-only audit of the local ATK Leader 7020 PS7 source archive and schematics."""
from __future__ import annotations

import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent
ARTIFACTS = ROOT / "artifacts"
ARTIFACTS.mkdir(parents=True, exist_ok=True)
ARCHIVE = Path(r"D:\BaiduNetdiskDownload\正点原子\4_Source_Code\5_PYNQ_Design\ZYNQ_7020_PYNQ.zip")
MEMBER = "5_pynq_helloworld/vivado/resizer/resizer.srcs/sources_1/bd/resizer/ip/resizer_processing_system7_0_0/resizer_processing_system7_0_0.xci"
DMA_MEMBER = "4_dma_tutorial/vivado/dma_tutorial/dma_tutorial.srcs/sources_1/bd/system/ip/system_processing_system7_0_0/system_processing_system7_0_0.xci"
PYNQ_BASE_XSA_MEMBER = "base/ready_to_test/system.xsa"
PYNQ_IMG = Path(r"D:\BaiduNetdiskDownload\正点原子\4_Source_Code\5_PYNQ_Design\IMG\ZYNQ-7020-2.7.0.zip")
ROOT_DOCS = Path(r"D:\BaiduNetdiskDownload\正点原子\3_开发板原理图和硬件相关文件")
CORE = ROOT_DOCS / "ZYNQ7010_7020核心板原理图_2V5.pdf"
BASE = ROOT_DOCS / "领航者ZYNQ底板原理图_V3.9.pdf"
SPIRIT = "{http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009}referenceId"
XILINX = "{http://www.xilinx.com}"


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def user_params(payload: bytes) -> dict[str, str]:
    root = ET.fromstring(payload)
    values: dict[str, str] = {}
    for node in root.iter():
        ref = node.attrib.get(SPIRIT, "")
        if ref.startswith("PARAM_VALUE.PCW_"):
            values[ref.removeprefix("PARAM_VALUE.")] = node.text or ""
    overrides: dict[str, str] = {}
    for node in root.iter():
        ref = node.attrib.get(XILINX + "referenceId", "")
        source = node.attrib.get(XILINX + "valueSource", "")
        if source == "user" and ref.startswith("PARAM_VALUE.PCW_"):
            key = ref.removeprefix("PARAM_VALUE.")
            if key in values:
                overrides[key] = values[key]
    return overrides


def pdf_pages(path: Path, relevant: tuple[str, ...]) -> dict[str, object]:
    if not path.is_file():
        return {"path": str(path), "present": False}
    reader = PdfReader(path)
    matches = []
    for number, page in enumerate(reader.pages, start=1):
        content = (page.extract_text() or "").replace("\x00", "")
        if any(needle.casefold() in content.casefold() for needle in relevant):
            excerpt = " ".join(content.split())
            matches.append({"page": number, "text": excerpt[:5000]})
    return {"path": str(path), "sha256": sha(path), "pages": len(reader.pages), "matches": matches}


def pynq_hwh_summary(payload: bytes) -> dict[str, object]:
    root = ET.fromstring(payload)
    system_info = next((n for n in root if n.tag.rsplit("}", 1)[-1] == "SYSTEMINFO"), None)
    ps = next((n for n in root.iter() if n.tag.rsplit("}", 1)[-1] == "MODULE"
               and n.attrib.get("MODTYPE") == "processing_system7"), None)
    clocks = sorted({int(n.attrib["CLKFREQUENCY"]) for n in root.iter()
                     if n.tag.rsplit("}", 1)[-1] == "PORT"
                     and n.attrib.get("SIGNAME", "").endswith("FCLK_CLK0")
                     and n.attrib.get("CLKFREQUENCY", "").isdigit()})
    hp0_ranges = [n.attrib for n in root.iter() if n.tag.rsplit("}", 1)[-1] == "MEMRANGE"
                  and n.attrib.get("SLAVEBUSINTERFACE") == "S_AXI_HP0"]
    return {
        "sha256": hashlib.sha256(payload).hexdigest(),
        "system_info": system_info.attrib if system_info is not None else None,
        "processing_system7": ps.attrib if ps is not None else None,
        "fclk0_hz_values": clocks,
        "hp0_ddr_mappings": hp0_ranges,
    }


def main() -> int:
    if not ARCHIVE.is_file():
        print(f"ERROR: board reference archive not found: {ARCHIVE}", file=sys.stderr)
        return 2
    with zipfile.ZipFile(ARCHIVE) as archive:
        xci_payload = archive.read(MEMBER)
        dma_xci_payload = archive.read(DMA_MEMBER)
        xsa_payload = archive.read(PYNQ_BASE_XSA_MEMBER)
    with zipfile.ZipFile(__import__("io").BytesIO(xsa_payload)) as xsa:
        base_hwh_payload = xsa.read("base.hwh")
    image_ok = PYNQ_IMG.is_file()
    parameters = user_params(xci_payload)
    keys = (
        "PCW_CRYSTAL_PERIPHERAL_FREQMHZ", "PCW_UIPARAM_DDR_PARTNO", "PCW_UIPARAM_DDR_BUS_WIDTH",
        "PCW_DDR_RAM_BASEADDR", "PCW_DDR_RAM_HIGHADDR", "PCW_FPGA0_PERIPHERAL_FREQMHZ",
        "PCW_USE_M_AXI_GP0", "PCW_USE_S_AXI_HP0", "PCW_S_AXI_HP0_DATA_WIDTH",
        "PCW_ENET0_PERIPHERAL_ENABLE", "PCW_ENET0_ENET0_IO", "PCW_UART0_PERIPHERAL_ENABLE",
        "PCW_UART0_UART0_IO", "PCW_SD0_SD0_IO", "PCW_QSPI_QSPI_IO", "PCW_USB0_USB0_IO",
    )
    core = pdf_pages(CORE, ("DDR3 SDRAM", "33.333333Mhz", "50Mhz", "XC7Z020", "NT5CC256M16"))
    base = pdf_pages(BASE, ("DDR3", "ENET0", "UART0", "RJ45", "MIO"))
    report = {
        "status": "PASS_LOCAL_VENDOR_REFERENCE_AUDIT_LIVE_BOARD_UNAVAILABLE",
        "scope": "read-only local source audit; not a live physical-board or PYNQ runtime probe",
        "target_from_prior_verified_project": "xc7z020clg400-2",
        "reference_source": {
            "vendor": "正点原子",
            "reference_design": "5_pynq_helloworld/vivado/resizer; PYNQ project PS7 preset",
            "source_archive": str(ARCHIVE),
            "source_archive_sha256": sha(ARCHIVE),
            "xci_member": MEMBER,
            "xci_sha256": hashlib.sha256(xci_payload).hexdigest(),
            "user_config_parameter_count": len(parameters),
            "selected_parameters": {key: parameters.get(key, "NOT_SET_IN_SOURCE") for key in keys},
            "dma_tutorial_secondary_reference": {
                "xci_member": DMA_MEMBER,
                "xci_sha256": hashlib.sha256(dma_xci_payload).hexdigest(),
                "role": "AXI interconnect/HP0 DMA tutorial reference only; not the selected PS7 preset",
            },
            "pynq_base_xsa_reference": {
                "xsa_member": PYNQ_BASE_XSA_MEMBER,
                "xsa_sha256": hashlib.sha256(xsa_payload).hexdigest(),
                "hwh": pynq_hwh_summary(base_hwh_payload),
            },
        },
        "board_schematics": {
            "core_2v5": core,
            "carrier_v3_9": base,
            "physical_revision_observation": "board is away; silkscreen not verified during this task",
        },
        "vendor_pynq_image_reference": {
            "archive": str(PYNQ_IMG),
            "distribution_version": "2.7.0",
            "archive_bytes": PYNQ_IMG.stat().st_size if image_ok else None,
            "archive_sha256": sha(PYNQ_IMG) if image_ok else None,
            "present": image_ok,
            "current_board_version": "UNKNOWN_BOARD_UNAVAILABLE",
        },
        "live_board": {
            "power": "USER_CONFIRMED_AWAY_OFFLINE",
            "pynq_version": None,
            "kernel_or_ssh": "NOT_REACHABLE_BOARD_AWAY",
            "current_overlay": None,
            "board_io_operations": 0,
        },
        "engineering_boundary": "Vendor XCI/HWH and saved schematics are design references. The current board image, installed PYNQ release, exact board revisions, and any network or runtime state require a new live read when the hardware is available.",
    }
    out = ARTIFACTS / "LEADER_BOARD_REFERENCE_AUDIT.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    p_out = ARTIFACTS / "LEADER_PS7_USER_PARAMS.json"
    p_out.write_text(json.dumps(parameters, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tcl_out = ARTIFACTS / "leader_ps7_user_params.tcl"
    safe_pairs = []
    for name, value in sorted(parameters.items()):
        # XCI uses a few multiline Tcl-list values (notably the MIO tree).
        # Braced Tcl words preserve these as a single literal list element.
        safe_value = value.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}")
        safe_pairs.extend(("{" + name + "}", "{" + safe_value + "}"))
    serialized = " \\\n    ".join(safe_pairs)
    tcl_out.write_text(
        "# Generated read-only from the pinned vendor XCI; values are data.\n"
        "set flyvis_vendor_ps7_user_params [list \\\n    " + serialized + "]\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({"report": str(out), "parameters_json": str(p_out), "parameters_tcl": str(tcl_out), "user_parameters": len(parameters), "xci_sha256": report["reference_source"]["xci_sha256"], "core_pages": len(core["matches"]), "base_pages": len(base["matches"]), "live_board": report["live_board"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
